import sys
import time
import argparse
import os
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import logging
from typing import Optional, List, Dict, Any, Tuple
import asyncio
import shutil # For terminal size

try:
    import questionary
    from questionary import Style, Separator, Choice
except ImportError:
    print("The 'questionary' library is required. 'pip install questionary'")
    sys.exit(1)

# Import the PURELY SYNCHRONOUS functions directly
from .prompts import (
    plan,
    specify_file_paths,
    generate_project_slug
)
# Import the ASYNC versions of functions that have sync wrappers in prompts.py
from .prompts import (
    generate_code as prompts_generate_code_async,
    handle_conversation as prompts_handle_conversation_async,
    generate_modification as prompts_generate_modification_async,
    answer_question as prompts_answer_question_async
)
from .utils import generate_folder, write_file, load_codebase, save_codebase, get_file_tree

MODEL_NAME = "gemini-1.5-pro-latest"
# Configure logging for main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() /"Desktop"
HISTORY_FILE = CONFIG_DIR / "vg_dev_history.json"

# --- Custom Style for Questionary ---
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#03a9f4'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#858585'),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])

# --- UI Helper Functions ---
def print_header(text: str):
    # import shutil # Already imported globally
    import pyfiglet
    terminal_width = shutil.get_terminal_size().columns
    main_font = "big"
    main_art = pyfiglet.figlet_format(text, font=main_font)
    tag_art = pyfiglet.figlet_format("< / >", font=main_font)
    main_lines = main_art.splitlines()
    tag_lines = tag_art.splitlines()
    combined_lines = []
    max_lines = max(len(main_lines), len(tag_lines))
    main_lines += [""] * (max_lines - len(main_lines))
    tag_lines += [""] * (max_lines - len(tag_lines))
    spacer = "    "
    for m_line, t_line in zip(main_lines, tag_lines):
        combined_line = m_line + spacer + t_line
        combined_lines.append(combined_line.center(terminal_width))
    colors = ["\033[38;5;99m", "\033[38;5;105m", "\033[38;5;111m", "\033[38;5;117m", "\033[38;5;123m"]
    for i, line in enumerate(combined_lines):
        color = colors[i % len(colors)]
        print(f"{color}{line}\033[0m")

def print_success(text: str): print(f"✅ \033[92m{text}\033[0m")
def print_warning(text: str): print(f"⚠️ \033[93m{text}\033[0m")
def print_info(text: str): print(f"ℹ️ \033[94m{text}\033[0m")
def print_error_msg(text: str): print(f"❌ \033[91m{text}\033[0m")

def _run_in_thread_with_new_loop(async_func, *args, **kwargs):
    return asyncio.run(async_func(*args, **kwargs))

# --- Terminal Folder Selector ---
def _is_vigi_dev_project(path: Path) -> bool:
    """Checks if the given path is a Vigi_Dev project directory."""
    return (path.resolve() / ".vigi_dev_meta" / "project_context.json").is_file()

async def _ask_for_project_directory_terminal_async() -> Optional[str]:
    """
    Asynchronously presents a terminal-based folder selector.
    Allows navigation and selection of an *existing* Vigi_Dev project folder.
    Returns the absolute path string of the selected Vigi_Dev project, or None if cancelled.
    """
    current_path = Path.home().resolve() # Start at home directory

    try:
        terminal_width = shutil.get_terminal_size().columns
    except Exception:
        terminal_width = 80 # Default

    while True:
        try:
            entries = await asyncio.to_thread(os.listdir, current_path)
            choices_meta = []
            for entry_name in entries:
                entry_path = current_path / entry_name
                try:
                    is_dir = await asyncio.to_thread(entry_path.is_dir)
                    # For "load existing", we are primarily interested in directories
                    if is_dir:
                         choices_meta.append({"name": entry_name, "path": entry_path, "is_dir": True})
                except (PermissionError, FileNotFoundError):
                    # Skip entries we can't access or that vanished
                    continue
        except PermissionError:
            await asyncio.to_thread(questionary.print, f"Permission denied for '{current_path}'", style="fg:ansired")
            if current_path.parent != current_path:
                current_path = current_path.parent
                continue
            else:
                await asyncio.to_thread(questionary.print, "Cannot navigate further. Please check permissions.", style="fg:ansired")
                return None
        except FileNotFoundError:
            await asyncio.to_thread(questionary.print, f"Path not found: '{current_path}'. Resetting to Home.", style="fg:ansired")
            current_path = Path.home().resolve()
            continue
        except Exception as e:
            logger.error(f"Error listing directory {current_path}: {e}", exc_info=True)
            await asyncio.to_thread(questionary.print, f"Error accessing '{current_path}'.", style="fg:ansired")
            if current_path.parent != current_path:
                current_path = current_path.parent
                continue
            else:
                return None

        q_choices = []

        # Option to select the current directory
        q_choices.append(Choice(
            title=f"[➡️ Attempt to Select Current Folder: {current_path.name}]",
            value={"action": "attempt_select_current", "path": current_path}
        ))

        # Parent directory option
        if current_path.parent != current_path:
             q_choices.append(Choice(title="[⬆️ Go to Parent Directory (..)]", value={"action": "go_up", "path": current_path.parent}))

        q_choices.append(Separator())

        # Sort directories alphabetically
        sorted_entries = sorted([item for item in choices_meta if item["is_dir"]], key=lambda x: x["name"].lower())

        for item in sorted_entries:
            is_sub_project = await asyncio.to_thread(_is_vigi_dev_project, item['path'])
            title = f"📁 {item['name']}/"
            if is_sub_project:
                title += " ✨ (Vigi_Dev Project)"
            q_choices.append(Choice(title=title, value={"action": "navigate", "path": item['path']}))

        q_choices.append(Separator())
        q_choices.append(Choice(title="[✏️ Enter Path Manually]", value={"action": "manual_path"}))
        q_choices.append(Choice(title="[❌ Cancel Selection]", value={"action": "cancel"}))

        path_str_for_prompt = str(current_path)
        max_len_for_message = terminal_width - 25 # Accommodate "Current folder: " and qmark
        if len(path_str_for_prompt) > max_len_for_message and max_len_for_message > 20: # Ensure space for truncation
            show_chars = (max_len_for_message - 3) // 2 # 3 for "..."
            truncated_path_for_message = f"{path_str_for_prompt[:show_chars]}...{path_str_for_prompt[-show_chars:]}"
        else:
            truncated_path_for_message = path_str_for_prompt
        
        select_message = f"Current folder: {truncated_path_for_message}"

        chosen_item = await questionary.select(
            message=select_message,
            choices=q_choices,
            style=custom_style,
            qmark="🗂️"
        ).ask_async()

        if chosen_item is None: return None # User pressed Ctrl+C

        action = chosen_item["action"]

        if action == "navigate" or action == "go_up":
            current_path = chosen_item["path"].resolve()
        elif action == "attempt_select_current":
            target_path = chosen_item["path"].resolve()
            if await asyncio.to_thread(_is_vigi_dev_project, target_path):
                return str(target_path)
            else:
                await asyncio.to_thread(
                    questionary.print,
                    f"Folder '{target_path.name}' is not a Vigi_Dev project. Cannot load this folder.",
                    style="fg:ansiyellow"
                )
                continue
        elif action == "manual_path":
            manual_path_str = await questionary.text(
                "Enter the full path to the project folder:",
                default=str(current_path),
                style=custom_style
            ).ask_async()
            if manual_path_str:
                manual_path = Path(manual_path_str.strip()).resolve()
                if await asyncio.to_thread(manual_path.is_dir):
                    current_path = manual_path
                    # After manual entry, immediately check if it's a project and select if so.
                    if await asyncio.to_thread(_is_vigi_dev_project, current_path):
                         await asyncio.to_thread(
                            questionary.print,
                            f"Path '{current_path.name}' is a Vigi_Dev project.",
                            style="fg:ansigreen"
                        )
                         # Offer to select it directly if they confirm
                         confirm_select = await questionary.confirm(
                             f"Select Vigi_Dev project '{current_path.name}'?",
                             default=True, style=custom_style
                         ).ask_async()
                         if confirm_select:
                             return str(current_path)
                    # else, just loop to show contents of new current_path
                else:
                    await asyncio.to_thread(questionary.print, f"Path '{manual_path_str}' is not a valid directory.", style="fg:ansired")
            continue
        elif action == "cancel":
            return None

# --- Project History and Basic Utils ---
def _ensure_config_dir(): CONFIG_DIR.mkdir(parents=True, exist_ok=True)
def load_project_history() -> List[Dict[str, str]]:
    _ensure_config_dir()
    if not HISTORY_FILE.exists(): return []
    try:
        with open(HISTORY_FILE, 'r') as f: history = json.load(f)
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return history
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading project history: {e}. Starting empty.") 
        return []
def save_project_history(history: List[Dict[str, str]]):
    _ensure_config_dir(); seen_paths = {}; unique_history = []
    for entry in sorted(history, key=lambda x: x.get("created_at", ""), reverse=True):
        path = entry.get("path")
        if path and path not in seen_paths: seen_paths[path] = entry; unique_history.append(entry)
    unique_history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    try:
        with open(HISTORY_FILE, 'w') as f: json.dump(unique_history, f, indent=2)
    except IOError as e: logger.error(f"Error saving project history: {e}")
def add_project_to_history(project_name: str, project_path: str, original_prompt: Optional[str] = None):
    history = load_project_history()
    history = [entry for entry in history if entry.get("path") != project_path]
    new_entry = {"name": project_name, "path": project_path, "created_at": datetime.now(timezone.utc).isoformat(), "original_prompt": original_prompt or ""}
    history.append(new_entry); save_project_history(history)

async def _initialize_project(original_prompt: str, project_root_abs: str, project_name_for_meta: str, debug: bool, model: str) -> Optional[dict]:
    if not original_prompt: print_error_msg("Cannot initialize project without an initial prompt."); return None
    
    print_info(f"Initializing project '{project_name_for_meta}' at: {project_root_abs}")
    if debug: logger.info(f"Debug: Initializing project '{project_name_for_meta}' at: {project_root_abs}")
    
    generate_folder(project_root_abs)
    meta_dir = os.path.join(project_root_abs, ".vigi_dev_meta"); generate_folder(meta_dir)

    if debug: logger.debug("--------Generating shared_deps (plan)---------")
    print_info("Step 1/3: Planning project structure...")
    shared_deps_content = plan(original_prompt, None, model=model) 
    write_file(os.path.join(meta_dir, "shared_deps.md"), shared_deps_content)
    write_file(os.path.join(meta_dir, "original_prompt.txt"), original_prompt)
    if debug: logger.debug(f"Shared Deps:\n{shared_deps_content[:200]}...\n--------Finished shared_deps---------")

    if debug: logger.debug("--------Generating file paths---------")
    print_info("Step 2/3: Determining file paths...")
    file_paths_from_llm = specify_file_paths(original_prompt, shared_deps_content, model=model) 
    if debug: logger.debug(f"--------Raw file_paths from LLM---------\n{file_paths_from_llm}")

    codebase = {}; sanitized_project_files = []
    if file_paths_from_llm:
        print_info(f"Step 3/3: Generating code for {len(file_paths_from_llm)} file(s)...")
        for i, gen_path_orig in enumerate(file_paths_from_llm):
            norm_path = os.path.normpath(gen_path_orig); _, path_no_drive = os.path.splitdrive(norm_path)
            rel_path_comp = path_no_drive.lstrip(os.sep).lstrip('/')
            if not rel_path_comp or rel_path_comp == '.':
                if debug: logger.warning(f"Skipping invalid path from LLM: '{gen_path_orig}'"); continue
            abs_final_path = os.path.abspath(os.path.join(project_root_abs, rel_path_comp))
            if not abs_final_path.startswith(os.path.abspath(project_root_abs)):
                if debug: logger.warning(f"Path '{gen_path_orig}' escapes output dir. Skipping."); continue
            final_clean_rel_path = os.path.relpath(abs_final_path, project_root_abs)
            if final_clean_rel_path == '..' or final_clean_rel_path.startswith('..' + os.sep) or final_clean_rel_path == '.':
                if debug: logger.warning(f"Path '{gen_path_orig}' invalid after relpath. Skipping."); continue
            sanitized_project_files.append(final_clean_rel_path)
            if debug: logger.debug(f"Sanitized relative path: '{final_clean_rel_path}' -> Writing to: {abs_final_path}")
            
            print_info(f"  Generating ({i+1}/{len(file_paths_from_llm)}): {final_clean_rel_path}...")
            code = await asyncio.to_thread(
                _run_in_thread_with_new_loop, 
                prompts_generate_code_async,
                original_prompt, shared_deps_content, final_clean_rel_path, 
                None, 
                model 
            )
            write_file(abs_final_path, code) 
            codebase[final_clean_rel_path] = code
            if debug: logger.debug(f"Finished generating code for: {abs_final_path}")
    else:
        print_warning("No file paths were determined. Project will be empty initially.")
    
    project_context = {
        "original_prompt": original_prompt, "project_slug": project_name_for_meta,
        "shared_deps": shared_deps_content, "file_paths": sanitized_project_files, 
        "output_dir": project_root_abs, "conversation_history": [], "codebase": codebase
    }
    context_to_save = {k: v for k, v in project_context.items() if k != "codebase"}
    try:
        with open(os.path.join(meta_dir, "project_context.json"), 'w') as f: json.dump(context_to_save, f, indent=2)
        if debug: logger.debug(f"Initial project context saved.")
        add_project_to_history(project_name_for_meta, project_root_abs, original_prompt)
        print_success(f"Project '{project_name_for_meta}' initialized successfully!")
    except Exception as e: 
        print_error_msg(f"Could not save initial project context or history: {e}")
        logger.error(f"Could not save initial project context or history: {e}", exc_info=True)
    return project_context

def _load_project_context(project_root_abs: str, debug: bool) -> Optional[dict]:
    meta_context_file = os.path.join(project_root_abs, ".vigi_dev_meta", "project_context.json")
    if os.path.exists(meta_context_file):
        try:
            with open(meta_context_file, 'r') as f: context_data = json.load(f)
            if context_data.get("output_dir") != project_root_abs:
                print_warning(f"Context output_dir '{context_data.get('output_dir')}' does not match loaded path '{project_root_abs}'. Not loading.")
                return None
            context_data["codebase"] = load_codebase(project_root_abs)
            context_data.setdefault("conversation_history", [])
            if debug: logger.info(f"Loaded existing project context from {meta_context_file}")
            project_name = context_data.get("project_slug", Path(project_root_abs).name)
            add_project_to_history(project_name, project_root_abs, context_data.get("original_prompt"))
            print_success(f"Successfully loaded project: {project_name}")
            return context_data
        except Exception as e: 
            print_error_msg(f"Could not load project context from {meta_context_file}: {e}")
            logger.error(f"Could not load project context: {e}", exc_info=True)
    else: 
        print_warning(f"No project context file found at {meta_context_file}")
        logger.warning(f"No project context file found at {meta_context_file}")
    return None

async def _start_conversation_mode(project_context: Dict[str, Any], initial_user_message: Optional[str], debug: bool, model: str):
    if not project_context: print_error_msg("Cannot start conversation without project context."); return
    project_slug = project_context.get("project_slug", Path(project_context.get("output_dir", "Unknown")).name)

    print_info(f"Project Location: {project_context.get('output_dir')}")
    if not project_context.get("conversation_history") and project_context.get("original_prompt"):
        print_success(f"Project '{project_slug}' loaded/initialized. Starting conversation.")
    else:
        print_success(f"Resuming conversation for project '{project_slug}'.")
    print_info("Select an action, then provide your input. Press Ctrl+C to cancel an input or action selection.")

    current_message_to_process = initial_user_message
    exit_flag = False # Flag to break the main loop

    while not exit_flag:
        actual_intent = None
        final_user_input = None

        if current_message_to_process:
            print_info(f"You provided: \"{current_message_to_process[:70].strip()}...\"")
            action_for_current_message = await questionary.select(
                "What would you like to do with this message?",
                choices=[
                    Choice("📝 Modify existing code", value="modify"),
                    Choice("❓ Ask a question about the code/project", value="ask"),
                    Choice("💬 General conversation / other request", value="chat"),
                    Separator(),
                    Choice("🗑️ Discard this message and select a new action", value="discard_and_new_action"),
                    Choice("🚪 Save and Exit Conversation", value="exit_conversation"),
                ],
                style=custom_style,
                qmark="💡"
            ).ask_async()

            if action_for_current_message is None: # Ctrl+C
                print_info("\nAction selection cancelled. Exiting conversation.")
                exit_flag = True
                continue
            if action_for_current_message == "exit_conversation":
                exit_flag = True
                continue
            if action_for_current_message == "discard_and_new_action":
                current_message_to_process = None
                continue

            actual_intent = action_for_current_message
            final_user_input = current_message_to_process
            current_message_to_process = None # Message is now being handled

        else: # No pre-existing message, standard action selection flow
            chosen_action = await questionary.select(
                "Choose an action:",
                choices=[
                    Choice("📝 Request Code Modification", value="modify"),
                    Choice("❓ Ask a Question", value="ask"),
                    Choice("💬 General Chat/Request", value="chat"),
                    Separator(),
                    Choice("🚪 Save and Exit Conversation", value="exit_conversation"),
                ],
                style=custom_style,
                qmark="🎯"
            ).ask_async()

            if chosen_action is None: # Ctrl+C
                print_info("\nAction selection cancelled. Exiting conversation.")
                exit_flag = True
                continue
            if chosen_action == "exit_conversation":
                exit_flag = True
                continue
            
            actual_intent = chosen_action
            
            prompt_message_for_input = "Your request/question/message:"
            qmark_for_input = "👤" # Default
            if actual_intent == "modify":
                prompt_message_for_input = f"Describe the code modifications for '{project_slug}':"
                qmark_for_input = "✍️"
            elif actual_intent == "ask":
                prompt_message_for_input = f"What is your question about '{project_slug}'?:"
                qmark_for_input = "❓"
            elif actual_intent == "chat":
                prompt_message_for_input = f"What's on your mind for '{project_slug}'? (General chat):"
                qmark_for_input = "💬"

            user_provided_input_text = await questionary.text(
                prompt_message_for_input,
                style=custom_style,
                qmark=qmark_for_input
            ).ask_async()

            if user_provided_input_text is None: # User pressed Ctrl+C during text input
                print_info("\nInput cancelled. Returning to action selection.")
                continue # Go back to "Choose an action"
            
            final_user_input = user_provided_input_text.strip()
            if not final_user_input:
                print_info("Empty input. Returning to action selection.")
                continue
        
        # ---- Process the input ----
        project_context["conversation_history"].append({"role": "user", "content": final_user_input})
        print_info("🤖 AI is thinking...")
        response = ""

        if actual_intent == "modify":
            if debug: logger.info(f"Handling modification request: {final_user_input[:50]}...")
            modified_files_dict = await asyncio.to_thread(
                _run_in_thread_with_new_loop, prompts_generate_modification_async,
                project_context, final_user_input, model
            )

            response_parts = [] # To build the final response message
            if modified_files_dict and not modified_files_dict.get("error"): # Successfully got a dict of potential modifications
                modified_keys = []
                skipped_file_details: List[str] = [] # Store details of skipped files

                for file_p, new_code_val in modified_files_dict.items():
                    if isinstance(new_code_val, str):
                        write_file(os.path.join(project_context["output_dir"], file_p), new_code_val)
                        project_context["codebase"][file_p] = new_code_val
                        modified_keys.append(file_p)
                    else:
                        # Handle the case where new_code_val is not a string
                        error_detail = f"File '{file_p}': Expected string content, got {type(new_code_val).__name__}."
                        skipped_file_details.append(error_detail) 
                        if debug: logger.warning(f"LLM returned non-string content for file '{file_p}'. Type: {type(new_code_val)}. Content: {str(new_code_val)[:100]}")
                
                if modified_keys:
                    response_parts.append(f"Modified {len(modified_keys)} files: {', '.join(modified_keys)}.")
                    print_success(f"Applied modifications to: {', '.join(modified_keys)}")
                
                if skipped_file_details:
                    response_parts.append(f"Could not apply modifications to {len(skipped_file_details)} file(s) due to unexpected content format: {'; '.join(skipped_file_details)}")
                    # print_warning(f"Skipped modifications for some files due to unexpected content format: {'; '.join(skipped_file_details)}") # This might be too noisy for UI, response is enough

                if not modified_keys and not skipped_file_details: # Empty dict from LLM (e.g. {}), no errors during generation
                    response_parts.append("LLM indicated no specific file modifications were made.")
                    print_info("No specific file modifications were made by the AI.")

            elif modified_files_dict and modified_files_dict.get("error"): 
                err_msg = modified_files_dict['error']
                response_parts.append(f"Modification request failed: {err_msg}") 
                # print_warning(f"Modification error: {err_msg}") # UI noise
            else: # modified_files_dict is None or some other unexpected empty value
                response_parts.append("No modifications were processed or an unexpected issue occurred.")
                # print_warning("Modification attempt resulted in no changes; the LLM might not have provided valid modifications.") # UI noise
            
            response = " ".join(response_parts).strip()
        elif actual_intent == "ask":
            if debug: logger.info(f"Handling code question: {final_user_input[:50]}...")
            response = await asyncio.to_thread(
                _run_in_thread_with_new_loop, prompts_answer_question_async,
                project_context, final_user_input, model 
            )
        elif actual_intent == "chat": 
            if debug: logger.info(f"Handling general conversation: {final_user_input[:50]}...")
            project_context["file_tree"] = get_file_tree(project_context["output_dir"])
            response = await asyncio.to_thread(
                _run_in_thread_with_new_loop, prompts_handle_conversation_async,
                project_context, final_user_input, model
            )
        
        project_context["conversation_history"].append({"role": "assistant", "content": response})
        print("🤖 AI: ", end="") 
        print(response)
        # Loop continues unless exit_flag was set

    # ---- Common exit logic: Save context ----
    meta_dir = os.path.join(project_context["output_dir"], ".vigi_dev_meta")
    # Ensure meta_dir exists, especially if project initialization was minimal or errored.
    generate_folder(meta_dir) # generate_folder is idempotent
    
    context_to_save = {k:v for k,v in project_context.items() if k != "codebase"}
    try:
        with open(os.path.join(meta_dir, "project_context.json"), 'w') as f: json.dump(context_to_save, f, indent=2)
        print_success(f"Project context for '{project_slug}' saved.")
    except Exception as e: 
        print_error_msg(f"Failed to save project context: {e}")
        logger.error(f"Failed to save project context: {e}", exc_info=True)
    print_info("Exiting conversation.")


async def _run_single_pass(initial_prompt: str, project_context: Dict[str, Any], debug: bool, model: str):
    if not project_context: print_error_msg("Cannot run single-pass without project context."); return
    project_slug = project_context.get("project_slug", "Unknown")
    project_root_abs = project_context.get("output_dir")
    if not initial_prompt: print_error_msg("Prompt required for single-pass."); sys.exit(1)
    
    print_info(f"Project Location: {project_root_abs}")
    print_info(f"Using Prompt: \"{initial_prompt[:70]}...\"")
    print_success(f"Done setting up '{project_slug}' complete. Files are located in {project_root_abs}")
    
    print_info("Generated File Tree:")
    file_tree_str = get_file_tree(project_root_abs)
    if file_tree_str:
        for line in file_tree_str.splitlines():
            print(f"  {line}")
    else:
        print_warning("  No files found or an error occurred generating the file tree.")

async def get_user_project_setup(args_output_dir: Optional[str], args_prompt: Optional[str], debug: bool, model: str) -> Tuple[Optional[str], Optional[str]]:
    project_root_abs: Optional[str] = None
    effective_initial_prompt_for_creation: Optional[str] = None
    print_header("VIGI DEV ASSIST")

    if args_output_dir:
        candidate_path = Path(args_output_dir).resolve()
        if (candidate_path / ".vigi_dev_meta" / "project_context.json").exists():
            print_info(f"Found existing project at --output_dir: {candidate_path}. Loading.")
            return str(candidate_path), None
        else:
            print_warning(f"--output_dir '{args_output_dir}' is not a recognized Vigi_Dev project. Proceeding to interactive setup.")

    while not project_root_abs:
        action = await questionary.select( # use ask_async
                "What would you like to do?",
                choices=[
                    Choice("🚀 Load Existing Project", value="Load Existing Project"),
                    Choice("✨ Create New Project", value="Create New Project"),
                    Separator(),
                    Choice("🚪 Exit", value="Exit")
                ],
                style=custom_style,
                qmark="👋"
            ).ask_async()
        if action == "Exit" or action is None:
            print_info("Exiting Vigi_Dev. Goodbye!")
            sys.exit(0)

        if action == "Load Existing Project":
            load_method_action = await questionary.select( # use ask_async
                    "How would you like to load the project?",
                    choices=[
                        Choice("📂 Load from History", value="history"),
                        Choice("📁 Other (Select Folder)", value="other"),
                        Separator(),
                        Choice("[Back to Main Menu]", value="--back-main--")
                    ],
                    style=custom_style,
                    qmark="🔎"
                ).ask_async()

            if load_method_action == "--back-main--" or load_method_action is None:
                continue

            if load_method_action == "history":
                history = load_project_history()
                if not history:
                    await asyncio.to_thread(
                        questionary.print,
                        "No project history found. Try creating a new project or loading from 'Other'.",
                        style="fg:ansiyellow"
                    )
                    continue 

                project_choices = [
                    Choice(
                        title=f"{e['name']}  (📄 {Path(e['path']).name})",
                        value=e['path'],
                    ) for e in history
                ]
                project_choices.extend([Separator(), Choice(title="[Back]", value="--back-load-menu--")])

                selected_path_history = await questionary.select( # use ask_async
                        "Select a project from history:",
                        choices=project_choices,
                        style=custom_style,
                        qmark="📜",
                        pointer="❯"
                    ).ask_async()
                if selected_path_history == "--back-load-menu--" or selected_path_history is None:
                    continue
                if selected_path_history:
                    print_info(f"Loading project from history: {Path(selected_path_history).name}")
                    return selected_path_history, None

            elif load_method_action == "other":
                selected_folder_path_str = await _ask_for_project_directory_terminal_async()
                if selected_folder_path_str:
                    selected_folder_path = Path(selected_folder_path_str).resolve()
                    # _ask_for_project_directory_terminal_async should only return valid project paths
                    if _is_vigi_dev_project(selected_folder_path): # Redundant check, but safe
                        print_info(f"Loading project from selected folder: {selected_folder_path.name}")
                        return str(selected_folder_path), None
                    else:
                        # This case should ideally not be reached if terminal selector works as designed
                        await asyncio.to_thread(
                            questionary.print,
                            f"The selected folder '{selected_folder_path.name}' is not a Vigi_Dev project (internal error or unexpected selection).",
                            style="fg:ansired"
                        )
                else:
                     await asyncio.to_thread(questionary.print, "No folder selected or selection cancelled.", style="fg:ansiyellow")
                continue # Back to "Load Existing Project" sub-menu (history/other)

        elif action == "Create New Project":
            print_info("Let's create a new project!")
            bases_choices = [
                Choice("🖥️ Desktop", value="Desktop"),
                Choice("📥 Downloads", value="Downloads"),
                Choice("📄 Documents", value="Documents"),
                Choice("📍 Current Directory", value="Current Dir (.)"),
                Choice("📁 Custom Path", value="Custom"),
                Separator(),
                Choice("[Back to Main Menu]", value="--back--")
            ]
            base_key = await questionary.select( # use ask_async
                    "Where should we create the project folder?",
                    choices=bases_choices,
                    style=custom_style,
                    qmark="🗺️",
                    pointer="❯"
                ).ask_async()
            if base_key == "--back--" or base_key is None:
                continue

            base_path: Optional[Path] = None
            base_dirs_map = {
                "Desktop": Path.home() / "Desktop",
                "Downloads": Path.home() / "Downloads",
                "Documents": Path.home() / "Documents",
                "Current Dir (.)": Path.cwd()
            }
            if base_key == "Custom":
                custom_str = await questionary.text( # use ask_async
                        "Enter the custom base path:",
                        validate=lambda t: True if t.strip() and Path(t.strip()).resolve().is_dir() else "Path must be an existing directory.",
                        style=custom_style,
                        qmark="✍️"
                    ).ask_async()
                if custom_str and custom_str.strip():
                    base_path = Path(custom_str.strip()).resolve()
                else:
                    continue
            else:
                base_path = base_dirs_map[base_key].resolve()

            name_str = await questionary.text( # use ask_async
                    "Project Name (this will be the folder name):",
                    validate=lambda t: True if t.strip() else "Project name cannot be empty.",
                    style=custom_style,
                    qmark="🏷️"
                ).ask_async()
            if not name_str or not name_str.strip():
                continue

            s_name = re.sub(r'\s+', '_', re.sub(r'[^\w\-_ \.]', '_', name_str.strip()))
            candidate_root = base_path / s_name

            if candidate_root.exists():
                if (candidate_root / ".vigi_dev_meta" / "project_context.json").exists():
                    if await questionary.confirm(f"Project '{s_name}' already exists at {candidate_root}. Load it instead?", default=True, style=custom_style, qmark="❓").ask_async():
                        print_info(f"Loading existing project: {candidate_root}")
                        return str(candidate_root), None
                    else:
                        continue
                else:
                    choice = await questionary.select( # use ask_async
                            f"Directory '{candidate_root}' already exists but is not a Vigi_Dev project. What to do?",
                            choices=[
                                Choice("Initialize Vigi_Dev here (will create .vigi_dev_meta)", value="init"),
                                Choice("Choose a different name/location", value="back"),
                                Choice("Exit", value="exit")
                            ],
                            style=custom_style,
                            qmark="🤔"
                        ).ask_async()
                    if choice == "exit" or choice is None:
                        print_info("Exiting."); sys.exit(0)
                    if choice == "back":
                        continue
            
            project_root_abs = str(candidate_root)
            print_info(f"New project will be created at: {project_root_abs} (Name: {s_name})")

            effective_initial_prompt_for_creation = args_prompt
            if not effective_initial_prompt_for_creation:
                effective_initial_prompt_for_creation = await questionary.text( # use ask_async
                        "Describe your new project (e.g., 'a snake game in python'):",
                        style=custom_style,
                        qmark="💬",
                        validate=lambda t: True if t.strip() else "Prompt cannot be empty for a new project."
                    ).ask_async()
            
            if not effective_initial_prompt_for_creation or not effective_initial_prompt_for_creation.strip():
                print_warning("Initial prompt is required for new project. Starting over.")
                project_root_abs = None
                continue
            
            return project_root_abs, effective_initial_prompt_for_creation

    return None, None

async def main_async(args):
    project_root_abs_str: Optional[str] = None
    project_creation_prompt: Optional[str] = None
    
    if args.output_dir and Path(args.output_dir).resolve().joinpath(".vigi_dev_meta", "project_context.json").exists():
        project_root_abs_str = str(Path(args.output_dir).resolve())
        print_info(f"Directly loading project from --output_dir: {project_root_abs_str}")
    elif args.output_dir and args.prompt and (not Path(args.output_dir).is_file()):
        output_path = Path(args.output_dir).resolve()
        if output_path.exists() and not output_path.joinpath(".vigi_dev_meta").exists():
             print_warning(f"Directory '{output_path}' exists but is not a Vigi_Dev project. Will initialize here non-interactively.")
        
        project_root_abs_str = str(output_path)
        project_creation_prompt = args.prompt
        print_info(f"Attempting non-interactive new project at: {project_root_abs_str} with prompt: \"{args.prompt[:50]}...\"")
        if not output_path.exists() and not output_path.parent.exists():
            print_error_msg(f"Parent directory for new project '{output_path.parent}' does not exist.")
            sys.exit(1)
    else: 
        project_root_abs_str, project_creation_prompt = await get_user_project_setup(args.output_dir, args.prompt, args.debug, args.model)

    if not project_root_abs_str:
        print_info("No project selected or created. Exiting.")
        sys.exit(0)
    
    project_root_path = Path(project_root_abs_str).resolve()
    project_context: Optional[Dict[str, Any]] = None

    if project_creation_prompt:
        project_name = project_root_path.name
        project_context = await _initialize_project(project_creation_prompt, str(project_root_path), project_name, args.debug, args.model)
    else:
        project_context = _load_project_context(str(project_root_path), args.debug)
        if not project_context:
            if not (project_root_path / ".vigi_dev_meta" / "project_context.json").exists():
                print_warning(f"No .vigi_dev_meta configuration found at {project_root_path}.")
                if args.prompt:
                    should_init = False
                    if sys.stdin.isatty():
                         should_init = await questionary.confirm( # use ask_async
                                f"Initialize a new Vigi_Dev project at '{project_root_path}' using the provided command-line prompt?",
                                default=True, style=custom_style, qmark="❓"
                            ).ask_async()
                    else:
                        should_init = True
                    
                    if should_init:
                        project_context = await _initialize_project(args.prompt, str(project_root_path), project_root_path.name, args.debug, args.model)
                        project_creation_prompt = args.prompt
                    else:
                        print_error_msg(f"Cannot proceed: '{project_root_path}' is not a project and initialization was declined. Exiting."); sys.exit(1)
                else:
                    print_error_msg(f"Project at {project_root_path} is not a valid Vigi_Dev project and no --prompt was given to initialize it. Exiting."); sys.exit(1)
            else:
                print_error_msg(f"Failed to load project context from {project_root_path}, file might be corrupted or inconsistent. Exiting."); sys.exit(1)
    
    if not project_context:
        print_error_msg("Fatal: Failed to obtain or create a valid project context. Exiting.")
        sys.exit(1)

    current_session_prompt = args.prompt if not project_creation_prompt else None

    if args.conversation:
        initial_message_for_conv_mode = None # Default to no initial message
        if current_session_prompt:
            # current_session_prompt contains args.prompt IF it wasn't used for project creation
            initial_message_for_conv_mode = current_session_prompt
            # The initial print_info about this message is now handled inside _start_conversation_mode
        
        await _start_conversation_mode(project_context, initial_message_for_conv_mode, args.debug, args.model)
    else: 
        prompt_for_single_pass = current_session_prompt or project_creation_prompt or project_context.get("original_prompt")
        if not prompt_for_single_pass:
            print_error_msg("No prompt available for single-pass mode. Use --prompt or ensure the project has an original prompt."); sys.exit(1)
        await _run_single_pass(prompt_for_single_pass, project_context, args.debug, args.model)

def main():
    print("UIPDTED")
    parser = argparse.ArgumentParser(
        description="Vigi_Dev - Your AI-Powered Coding Assistant",
        formatter_class=argparse.RawTextHelpFormatter 
    )
    parser.add_argument("--prompt", type=str, help="Initial prompt for new projects or session prompt for existing ones.\nIf creating new and not provided, you'll be asked interactively.")
    parser.add_argument("--output_dir", type=str, help="Optional: Path to an existing project to load directly, or path for a new project if --prompt is also given (non-interactive creation).")
    parser.add_argument("--debug", action="store_true", help="Enable detailed debug logging (mostly for developers).")
    parser.add_argument("--conversation", action="store_true", help="Start an interactive conversation mode after project setup.")
    parser.add_argument("--model", type=str, default=MODEL_NAME, help=f"Specify the AI model to use (default: {MODEL_NAME}).")
    
    if len(sys.argv) == 1 and sys.stdin.isatty():
        print_header("Welcome to Vigi_Dev!")
    
    args = parser.parse_args()

    if args.debug: 
        logger.setLevel(logging.DEBUG)
        logging.getLogger('prompts').setLevel(logging.DEBUG) 
        print_info("Debug mode enabled. Expect verbose logging.")
    else: 
        logging.getLogger().handlers[0].setLevel(logging.WARNING)
        logger.setLevel(logging.INFO)

    asyncio.run(main_async(args))

if __name__ == "__main__":
    utils_logger = logging.getLogger('utils') 
    if not utils_logger.hasHandlers():
        utils_logger.addHandler(logging.StreamHandler(sys.stdout))
        utils_logger.propagate = False
    main()