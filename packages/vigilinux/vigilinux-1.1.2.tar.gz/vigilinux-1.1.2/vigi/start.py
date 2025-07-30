import os
import sys
if sys.platform == "win32":
    import pyreadline3 as readline  # noqa: F401
else:
    import readline  # noqa: F401
import typer
from click import BadArgumentUsage
# Import click.Context and click.HelpFormatter for type hinting in custom Typer class
import click
from click.types import Choice
from typing_extensions import Annotated
from typing import Optional, List # Added List

# Import questionary for interactive prompts
import questionary

from .config import cfg
from .tools_and_personas import (
    collect_schemas,
    DefaultPersonas,
    DigitalPersona,
    _display_persona_details_impl as display_persona_details_callback,
    _display_personas_impl as display_personas_callback_internal,
)
from .chat_handler import ChatHandler
from .default_handler import DefaultHandler
from .repl_handler import ReplHandler
from .corefunctions import get_edited_prompt, run_command
from .developerch.main import main as developerch_main
from .docker_part.docker_main import docker_main
from .shell_smart.shell_main import vigi_shell_entry_point as smart_vigi_shell_entry_point

def display_personas_entry_point(value: bool):
    if value:
        return display_personas_callback_internal(value)

# Updated epilog_text using styled titles and separator lines
epilog_text = """
[b]Examples:[/b]

  [i]The application provides powerful assistance through several specialized modules.
  Below are examples of how to use features from these key modules:[/i]

[bold bright_blue]Vigi Shell Module[/bold bright_blue]
[bright_blue]───────────────────────────────────────────────────────────────────────────────[/bright_blue]
  For interactive AI-powered shell experiences.

  [b]• Start an interactive Vigi Shell session:[/b]
    $ vg .shell

  [b]• Start an interactive Vigi Shell with session memory (retains context):[/b]
    $ vg .memshell

  [b]• Get AI help for a specific shell command/query via Vigi Shell:[/b]
    $ vg .shell "how to find all text files modified last week"

[bold green]Docker Module[/bold green]
[green]───────────────────────────────────────────────────────────────────────────────[/green]
  For specialized assistance with Docker commands and concepts.

  [b]• Enter Docker assistance mode:[/b]
    $ vg --docker
    (This will typically start an interactive session or tool focused on Docker)

[bold yellow]Code Development Module[/bold yellow]
[yellow]───────────────────────────────────────────────────────────────────────────────[/yellow]
  For generating code and engaging in development-focused conversations.

  [b]• Generate a Python function for a specific task:[/b]
    $ vg .c "write a python function that calculates factorial"

  [b]• Start an interactive coding session/conversation:[/b]
    $ vg .c .talk "Let's design a simple API endpoint using Flask."

[bold magenta]Persona and Chat Module[/bold magenta]
[magenta]───────────────────────────────────────────────────────────────────────────────[/magenta]
  For general conversations, using AI personas, and managing chat history.

  [b]• Start a general interactive chat session:[/b]
    $ vg .talk
    You can then type your messages, e.g., "Tell me about Large Language Models."

  [b]• Send a single query for a quick answer:[/b]
    $ vg "What is the weather like in London today?"

  [b]• Interactively select or create an AI persona for your chat:[/b]
    $ vg .prs
    (This will start a chat session with the chosen persona)

  [b]• List all available personas:[/b]
    $ vg .shpersonas

  [b]• View details of a specific persona:[/b]
    $ vg --show-role "MyCustomCoderPersona"
"""

class InteractiveHelpTyper(typer.Typer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """
        Custom epilog formatting to conditionally display examples based on user prompt.
        This method is called by Click/Typer when formatting help for a command.
        This override specifically affects the main application 'app' instance.
        Subcommands will use their default epilog formatting.
        """
        current_command_epilog = self.epilog # Epilog text for the current command (our main app)

        # Proceed with custom logic only if:
        # 1. We are formatting help for the main application (ctx.parent is None).
        #    (This is implicitly true because this method is overridden on the main app object,
        #     but the check is an explicit safeguard.)
        # 2. The main application actually has an epilog defined.
        if not (ctx.parent is None and current_command_epilog):
            # Not the main app's help screen, or the main app has no epilog.
            # Fall back to standard epilog rendering behavior.
            if current_command_epilog:
                formatter.write_paragraph()
                formatter.write_text(current_command_epilog)
            return

        # If we reach here, we are formatting the main app's help, and it has an epilog.
        epilog_to_render = current_command_epilog  # Default to showing the epilog

        if sys.stdin.isatty():
            # Terminal is interactive, so we can prompt the user.
            try:
                # Use a unique attribute name on the context to store the decision.
                # This prevents re-prompting if format_epilog is (hypothetically) called multiple times
                # during a single help generation.
                decision_attr_name = '_show_examples_main_app_help_decision'

                if hasattr(ctx, decision_attr_name):
                    # Decision already made for this help invocation
                    show_examples = getattr(ctx, decision_attr_name)
                else:
                    # Ask the user
                    show_examples = questionary.confirm(
                        "Show command examples in help?",
                        default=True,  # Default to 'Yes' if user presses Enter
                        auto_enter=False,  # Require explicit Y/N selection then Enter
                        kbi_msg="Example display choice cancelled. Defaulting to show examples."
                    ).ask()

                    if show_examples is None:  # User pressed Ctrl+C at the prompt
                        show_examples = True  # Default to showing examples as per kbi_msg
                    
                    # Store the decision on the context
                    setattr(ctx, decision_attr_name, show_examples)

                if not show_examples:
                    epilog_to_render = None  # User chose not to display examples

            except Exception:
                # If questionary fails for any reason (e.g., unusual terminal environment),
                # fall back to the default behavior of showing the epilog.
                # `epilog_to_render` remains `current_command_epilog`.
                # For a CLI help screen, failing silently and showing default is often best.
                # Optionally, one could log this to stderr if a debug environment variable is set.
                pass
        else:
            # Not an interactive TTY (e.g., output is piped).
            # Default to showing the epilog. `epilog_to_render` remains `current_command_epilog`.
            pass

        if epilog_to_render:
            formatter.write_paragraph()  # Adds a standard separation
            formatter.write_text(epilog_to_render)


# Use the custom InteractiveHelpTyper class for the application
app = InteractiveHelpTyper(epilog=epilog_text, rich_markup_mode="rich")

@app.callback(invoke_without_command=True)
def default_handler_main(
    ctx: typer.Context,
    prompt_args: Annotated[Optional[List[str]], typer.Argument(
        show_default=False,
        help="The prompt text. Can be entered as a single string or multiple words. Options like .c, .talk should precede this.",
        metavar="[PROMPT_TEXT...]"
    )] = None,
    model: Annotated[str, typer.Option(
        help="LLM to use. Passed to developer/ch if .c is used.",
        hidden=True,
    )] = cfg.get("DEFAULT_MODEL"),
    temperature: Annotated[float, typer.Option(
        min=0.0, max=2.0, help="Randomness of output.",
        hidden=True,
    )] = 0.0,
    top_p: Annotated[float, typer.Option(
        min=0.0, max=1.0, help="Limits highest probable tokens.",
        hidden=True,
    )] = 1.0,
    md: Annotated[bool, typer.Option(
        help="Prettify markdown output.",
        hidden=True,
    )] = (cfg.get("PRETTIFY_MARKDOWN") == "true"),
    shell: Annotated[bool, typer.Option(
        "--assist-shell",
        help="Generate/execute shell commands (Assistance Options). If a prompt is provided with this, it's for general AI assistance.",
        rich_help_panel="Assistance Options",
        hidden=True
    )] = False,
    interaction: Annotated[bool, typer.Option(
        help="Interactive mode for shell assistance (Assistance Options).",
        rich_help_panel="Assistance Options",
        hidden=True
    )] = (cfg.get("SHELL_INTERACTION") == "true"),
    describe_shell: Annotated[bool, typer.Option(
        "--describe-shell", "-d", help="Describe a shell command.", rich_help_panel="Assistance Options"
    )] = False,
    code: Annotated[bool, typer.Option(
        ".c",
        help="Generate code using developer/ch. Use with .talk (or --conversation) for its chat mode.",
        rich_help_panel="Code Development Module",
    )] = False,
    shell_mode: Annotated[bool, typer.Option(
        ".shell",
        help="Invoke Vigi Shell: Interactive AI Shell if no prompt, single query processing if prompt is given.",
        rich_help_panel="Vigi Shell Module",
    )] = False,
    memshell_flag: Annotated[bool, typer.Option(
        ".memshell",
        help="Invoke Vigi Shell with session memory: an interactive AI Shell session that retains context across commands.",
        rich_help_panel="Vigi Shell Module",
    )] = False,
    devch_output_dir: Annotated[Optional[str], typer.Option(
        "--devch-output-dir",
        help="Base output directory for developer/ch (with .c).",
        rich_help_panel="Code Development Module",
        hidden=True,
    )] = None,
    devch_debug: Annotated[bool, typer.Option(
        "--devch-debug",
        help="Enable debug logging for developer/ch (with .c).",
        rich_help_panel="Code Development Module",
        hidden=True,
    )] = False,
    conversation: Annotated[bool, typer.Option(
        ".talk", "--conversation",
        help="Enable conversation mode. If .c is used, enables developer/ch conversation. Otherwise, starts a vigi REPL/chat session.",
        rich_help_panel="Persona and Chat Module",
    )] = False,
    docker: Annotated[bool, typer.Option(
        "--docker", help="Used to help with docker commands.", rich_help_panel="Docker Module",
    )] = False,
    functions: Annotated[bool, typer.Option(
        help="Allow function calls.", rich_help_panel="Assistance Options",
    )] = (cfg.get("VIGI_USE_FUNCTIONS") == "true"),
    editor: Annotated[bool, typer.Option(
        help="Open $EDITOR to provide a prompt.",
        hidden=True,
        )] = False,
    cache: Annotated[bool, typer.Option(
        help="Cache completion results.",
        hidden=True,
        )] = True,
    repl: Annotated[bool, typer.Option(
        ".convo", help="Start a REPL session (DEPRECATED, use .talk or --conversation).", rich_help_panel="Persona and Chat Module", hidden=True,
    )] = False,
    repl_id: Annotated[Optional[str], typer.Option(
        "--repl-id", help="Session ID for REPL/conversation session (optional, cached if provided).", rich_help_panel="Persona and Chat Module",
        hidden=True,
    )] = None,
    show_chat_id: Annotated[Optional[str], typer.Option(
        "--show-chat", help="Show messages from a specific chat ID.", rich_help_panel="Persona and Chat Module",
        hidden=True,
    )] = None,
    list_chats_flag: Annotated[bool, typer.Option(
        "--list-chats", "-lc",
        help="List existing chat ids.",
        callback=ChatHandler.list_ids,
        rich_help_panel="Persona and Chat Module",
        is_eager=True,
        hidden=True,
    )] = False,
    select_persona_flag: Annotated[bool, typer.Option(
        ".prs", ".persona",
        help="Interactively select or create a persona. If present, triggers selection/creation and starts a REPL session.",
        rich_help_panel="Persona and Chat Module",
        is_flag=True
    )] = False,
    show_role_trigger: Annotated[Optional[str], typer.Option(
        "--show-role",
        help="Show details of a specific persona: --show-role MyRole",
        callback=display_persona_details_callback,
        rich_help_panel="Persona and Chat Module",
        is_eager=True,
    )] = None,
    display_personas_trigger: Annotated[bool, typer.Option(
        ".shpersonas", ".shprs",
        help="List all available personas.",
        callback=display_personas_entry_point,
        rich_help_panel="Persona and Chat Module",
        is_eager=True
    )] = False
) -> None:


    if ctx.invoked_subcommand is not None:
        return

    stdin_content_str: Optional[str] = None
    if not sys.stdin.isatty():
        stdin_data_lines = []
        for line in sys.stdin:
            if "__sgpt__eof__" in line:
                break
            stdin_data_lines.append(line)

        if stdin_data_lines:
            stdin_content_str = "".join(stdin_data_lines).strip()

        try:
            if os.name == "posix":
                sys.stdin = open("/dev/tty", "r")
            elif os.name == "nt":
                sys.stdin = open("CONIN$", "r")
        except OSError:
            pass

    cli_arg_prompt_str: Optional[str] = None
    if prompt_args:
        cli_arg_prompt_str = " ".join(prompt_args).strip()
        if not cli_arg_prompt_str:
            cli_arg_prompt_str = None

    effective_prompt: Optional[str] = None
    if stdin_content_str and cli_arg_prompt_str:
        effective_prompt = f"{stdin_content_str}\n\n{cli_arg_prompt_str}"
    elif stdin_content_str:
        effective_prompt = stdin_content_str
    elif cli_arg_prompt_str:
        effective_prompt = cli_arg_prompt_str

    if editor and not effective_prompt:
        effective_prompt = get_edited_prompt()

    role_class: Optional[DigitalPersona] = None
    general_shell_assistance_flag = shell
    vigi_shell_mode_flag = shell_mode

    vigi_main_conversation_mode = (conversation and not code) or \
                                  (repl and not code)

    if select_persona_flag:
        try:
            role_class = DigitalPersona.retrieve_persona()
        except InterruptedError:
            typer.secho("Persona selection/creation was cancelled. Exiting.", fg=typer.colors.YELLOW)
            raise typer.Exit(code=0)
        except BadArgumentUsage as e:
            typer.secho(f"Error during persona selection/creation: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        except RuntimeError as e:
            typer.secho(f"Runtime error during persona selection/creation: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        if role_class:
            vigi_main_conversation_mode = True
    else:
        role_class = DefaultPersonas.determine_persona(general_shell_assistance_flag, describe_shell, code)

    if not role_class:
        typer.secho("CRITICAL: Persona could not be determined or selected/created.", fg=typer.colors.RED)
        raise typer.Exit(1)

    if docker:
        docker_main()
        raise typer.Exit()

    if memshell_flag:
        from .shell_part.main import ai_shell_interactive
        if effective_prompt:
            typer.secho(
                "Warning: .memshell is for interactive sessions; the provided prompt will be ignored as .memshell always starts an interactive session.",
                fg=typer.colors.YELLOW,
            )
        typer.echo("Starting Vigi Shell with session memory (.memshell)...")
        ai_shell_interactive()
        raise typer.Exit()

    if vigi_shell_mode_flag:
        if effective_prompt:
            smart_vigi_shell_entry_point(initial_query=effective_prompt)
        else:
            smart_vigi_shell_entry_point()
        raise typer.Exit()

    if code:
        dev_ch_conversation_mode = conversation

        if repl and not dev_ch_conversation_mode:
            raise BadArgumentUsage(
                "Cannot use .convo (deprecated Vigi REPL) with .c. "
                "For developer/ch conversation mode, use '.c .talk' or '.c --conversation'."
            )

        original_argv = sys.argv[:]
        developerch_args = ['developerch_invoker']
        if effective_prompt:
             developerch_args.extend(['--prompt', effective_prompt])
        if model != cfg.get("DEFAULT_MODEL"):
            developerch_args.extend(['--model', model])
        if devch_output_dir:
            developerch_args.extend(['--output_dir', devch_output_dir])
        if devch_debug:
            developerch_args.append('--devch-debug')
        if dev_ch_conversation_mode:
            developerch_args.append('--conversation')

        sys.argv = developerch_args
        exit_code = 0
        try:
            developerch_main()
        except SystemExit as e_sys:
            exit_code = e_sys.code if isinstance(e_sys.code, int) else (0 if e_sys.code is None else 1)
        except Exception as e_exc:
            typer.secho(f"Error running developer/ch: {e_exc}", file=sys.stderr, fg=typer.colors.RED)
            exit_code = 1
        finally:
            sys.argv = original_argv
        raise typer.Exit(code=exit_code)

    if show_chat_id:
        ChatHandler.show_messages(show_chat_id, md)
        raise typer.Exit()

    if vigi_main_conversation_mode:
        if not effective_prompt and not repl_id and select_persona_flag :
             typer.echo(f"Starting Vigi conversation with selected/created persona: {role_class.identifier}")

        function_schemas_repl = (collect_schemas() or None) if functions else None
        ReplHandler(repl_id, role_class, md).handle(
            init_prompt=effective_prompt if effective_prompt else "",
            model=model,
            temperature=temperature,
            top_p=top_p,
            caching=cache,
            functions=function_schemas_repl,
        )
        raise typer.Exit()

    if not effective_prompt:
        typer.secho("No prompt provided and no specific mode selected (e.g., .shell, .talk, .c).", fg=typer.colors.YELLOW)
        typer.echo(ctx.get_help())
        raise typer.Exit(code=1)

    if sum((bool(general_shell_assistance_flag), bool(describe_shell))) > 1 :
        raise BadArgumentUsage(
            "Only one of general shell assistance (e.g., --assist-shell, hidden) or --describe-shell can be used at a time "
            "in single-shot general assistance mode."
        )

    if repl_id == ".c":
        raise BadArgumentUsage(
            "Session ID for --repl-id cannot be '.c'. "
            "Use '.c .talk' or '.c --conversation' for developer/ch conversation mode."
        )

    function_schemas_single = (collect_schemas() or None) if functions else None

    full_completion = DefaultHandler(role_class, md).handle(
        prompt=effective_prompt,
        model=model,
        temperature=temperature,
        top_p=top_p,
        caching=cache,
        functions=function_schemas_single
    )

    active_shell_interaction_loop = general_shell_assistance_flag and interaction and full_completion

    while active_shell_interaction_loop:
        typer.echo("")
        option_choice = typer.prompt(
            text="Choose action: [E]xecute, [A]bort",
            type=Choice(("e", "a"), case_sensitive=False),
            default="e" if cfg.get("DEFAULT_EXECUTE_SHELL_CMD") == "true" else "a",
            show_choices=True,
            show_default=True,
        )
        if option_choice == "e":
            run_command(full_completion)
            break
        elif option_choice == "a":
            typer.secho("Aborted.", fg=typer.colors.YELLOW)
            break

if __name__ == "__main__":
    app()