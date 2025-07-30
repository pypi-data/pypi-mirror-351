######################################################################
#                                                                    #
#               Engineered for GitHub: naumanAhmed3                  #
#                                                                    #
#     <<<<< AI System Instruction & Example Formulator >>>>>         #
#                                                                    #
######################################################################
"""
Responsible for constructing the structured prompts and example dialogues
fed to the Generative AI for shell instruction generation tasks.
It defines the expected JSON output formats and provides few-shot learning examples.
"""

from datetime import datetime

class SystemInstructionBuilder:
    """
    Constructs and manages templates for AI system instructions and few-shot examples,
    specifically for generating shell instructions based on user requests.
    It defines the JSON schemas for valid responses and error indications from the AI.
    """
    DETAILED_RESPONSE_JSON_SCHEMA = """
{
"input": "<user input>",
"error": 0,
"commands": [
{
"seq": <Order of Command>,
"cmd_to_execute": "<commands and arguments to execute>",
"cmd_explanations": ["<explanation of command 1>", "<explanation of command 2>", ...],
"arg_explanations": {"<arg1>": "<explanation of arg1>", "<arg2>": "<explanation of argument 2>", ...}
},
{
"seq": <Order of Command>,
"cmd_to_execute": "<commands and arguments to execute>",
"cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
"arg_explanations": {"<arg1>": "<explanation of arg1>", "<arg2>": "<explanation of argument 2>", ...}
}
]
}
"""

    CONDENSED_RESPONSE_JSON_SCHEMA = """
{
"commands": ["<commands and arguments to execute>", "<commands and arguments to execute>", ...]
}
"""
    INVALID_REQUEST_JSON_RESPONSE = """{"input": "<user input>", "error": 1}"""
    INVALID_REQUEST_CONDENSED_JSON_RESPONSE = """{"error": 1}"""

    SAMPLE_TARGET_OS_FOR_EXAMPLES = "macOS-13.3.1-x86-64bit"
    EXAMPLE_REQUEST_CONDA_INSTALL = "install conda"
    EXAMPLE_OUTPUT_CONDA_DETAILED = """
{
"input": "install conda",
"error": 0,
"commands": [
{
"seq": 1,
"cmd_to_execute": "curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh",
"cmd_explanations": ["The curl command is used to issue web requests, e.g. download web pages."],
"arg_explanations": {
"-O": "specifies that we want to save the response to a file.",
"https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh": "is the URL of the file we want to download."
}
},
{
"seq": 2,
"cmd_to_execute": "bash Miniconda3-latest-MacOSX-x86_64.sh",
"cmd_explanations": ["The bash command is used to execute shell scripts."],
"arg_explanations": {"Miniconda3-latest-MacOSX-x86_64.sh": "is the name of the file we want to execute."}
}
]
}
"""
    EXAMPLE_OUTPUT_CONDA_CONDENSED = """
{
"commands": ["curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh", "bash Miniconda3-latest-MacOSX-x86_64.sh"]
}
"""
    EXAMPLE_REQUEST_FILE_SEARCH = "search ~/Documents directory for any python file that begins with 'test'"
    EXAMPLE_OUTPUT_SEARCH_DETAILED = """
{
"input": "search the ~/Documents/ directory for any python file that begins with 'test'",
"error" : 0,
"commands": [
{
"seq": 1,
"cmd_to_execute": "find /Documents/ -name 'test*.py'",
"cmd_explanations": ["find is used to list files."],
"arg_explanations": {
"/Documents": "specifies the folder to search in.",
"-name 'test*.py'": "specifies that we want to search for files starting with test that are python files."
}
}
]
}
"""
    EXAMPLE_OUTPUT_SEARCH_CONDENSED = """
{
"commands": ["find ~/Documents/ -name 'test*.py'"]
}
"""
    EXAMPLE_REQUEST_PROCESS_LIST = "list all processes using more than 50 MB of memory"
    EXAMPLE_OUTPUT_PROCESS_CONDENSED = """
{
"commands": ["ps -axm -o %mem,rss,comm | awk '$1 > 0.5 { printf(\\"%.0fMB\\t%s\\n\\", $2/1024, $3); }'"]
}
"""
    EXAMPLE_AMBIGUOUS_REQUEST = "the quick brown fox jumped over"
    EXAMPLE_OUTPUT_AMBIGUOUS_DETAILED = """{"input": "the quick brown fox jumped over", "error": 1}"""
    EXAMPLE_OUTPUT_AMBIGUOUS_CONDENSED = """{"error": 1}"""

    def __init__(self):
        pass

    def _determine_instruction_json_schema(self, use_condensed_format: bool) -> str:
        return self.CONDENSED_RESPONSE_JSON_SCHEMA if use_condensed_format else self.DETAILED_RESPONSE_JSON_SCHEMA

    def _determine_error_json_response(self, use_condensed_format: bool) -> str:
        return self.INVALID_REQUEST_CONDENSED_JSON_RESPONSE if use_condensed_format else self.INVALID_REQUEST_JSON_RESPONSE

    def generate_initial_ai_directive(self, use_condensed_format: bool) -> str:
        json_response_template = self._determine_instruction_json_schema(use_condensed_format)
        json_error_template = self._determine_error_json_response(use_condensed_format)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""
Provide the appropriate command-line commands that can be executed for a user request (keep in mind the platform of the user).
Today's date/time is {current_timestamp}.
If the request is possible, please provide commands that can be executed in the command line and do not require a GUI.
Do not include commands that require a yes/no response.
For each command, explain the command and any arguments used.
Try to find the simplest command(s) that can be used to execute the request.

If the request is valid, format each command output in the following JSON format: {json_response_template}

            If the request is invalid, please return the following JSON format: {json_error_template}
            """

    def _construct_ai_interaction_message(self, role_type: str, message_content: str) -> dict:
        return {"role": role_type, "parts": [message_content]}

    def _create_user_request_message_for_instruction_gen(self, end_user_query: str, target_os_descriptor: str) -> dict:
        formatted_query_content = (
            f"""Provide the appropriate command-line commands that can be executed on a {target_os_descriptor} machine for the user request: "{end_user_query}"."""
        )
        return self._construct_ai_interaction_message("user", formatted_query_content)

    def _create_ai_response_message_for_instruction_gen(self, ai_generated_json_output: str) -> dict:
        return self._construct_ai_interaction_message("model", ai_generated_json_output)

    def assemble_instruction_generation_training_examples(self, use_condensed_format: bool) -> list:
        initial_directive_message = self.generate_initial_ai_directive(use_condensed_format)
        dialogue_sequence = [
            self._construct_ai_interaction_message("user", initial_directive_message),
            self._construct_ai_interaction_message("model", "Understood!"), 
        ]
        conda_user_request = self._create_user_request_message_for_instruction_gen(
            self.EXAMPLE_REQUEST_CONDA_INSTALL, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
        )
        conda_ai_response_content = self.EXAMPLE_OUTPUT_CONDA_CONDENSED if use_condensed_format else self.EXAMPLE_OUTPUT_CONDA_DETAILED
        conda_ai_response = self._create_ai_response_message_for_instruction_gen(conda_ai_response_content)
        dialogue_sequence.extend([conda_user_request, conda_ai_response])

        search_user_request = self._create_user_request_message_for_instruction_gen(
            self.EXAMPLE_REQUEST_FILE_SEARCH, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
        )
        search_ai_response_content = self.EXAMPLE_OUTPUT_SEARCH_CONDENSED if use_condensed_format else self.EXAMPLE_OUTPUT_SEARCH_DETAILED
        search_ai_response = self._create_ai_response_message_for_instruction_gen(search_ai_response_content)
        dialogue_sequence.extend([search_user_request, search_ai_response])

        if use_condensed_format:
            process_user_request = self._create_user_request_message_for_instruction_gen(
                self.EXAMPLE_REQUEST_PROCESS_LIST, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
            )
            process_ai_response = self._create_ai_response_message_for_instruction_gen(self.EXAMPLE_OUTPUT_PROCESS_CONDENSED)
            dialogue_sequence.extend([process_user_request, process_ai_response])

        ambiguous_user_request = self._create_user_request_message_for_instruction_gen(
            self.EXAMPLE_AMBIGUOUS_REQUEST, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
        )
        ambiguous_ai_response_content = self.EXAMPLE_OUTPUT_AMBIGUOUS_CONDENSED if use_condensed_format else self.EXAMPLE_OUTPUT_AMBIGUOUS_DETAILED
        ambiguous_ai_response = self._create_ai_response_message_for_instruction_gen(ambiguous_ai_response_content)
        dialogue_sequence.extend([ambiguous_user_request, ambiguous_ai_response])
        
        return dialogue_sequence

    def format_actual_user_request_for_instruction_gen(self, end_user_query: str, current_target_os_descriptor: str) -> dict:
        return self._create_user_request_message_for_instruction_gen(end_user_query, current_target_os_descriptor)

    def format_actual_ai_response_for_instruction_gen(self, ai_generated_json_output: str) -> dict:
        return self._create_ai_response_message_for_instruction_gen(ai_generated_json_output)######################################################################
#                                                                    #
#               Engineered for GitHub: naumanAhmed3                  #
#                                                                    #
#     <<<<< AI System Instruction & Example Formulator >>>>>         #
#                                                                    #
######################################################################
"""
Responsible for constructing the structured prompts and example dialogues
fed to the Generative AI for shell instruction generation tasks.
It defines the expected JSON output formats and provides few-shot learning examples.
"""

from datetime import datetime

class SystemInstructionBuilder:
    """
    Constructs and manages templates for AI system instructions and few-shot examples,
    specifically for generating shell instructions based on user requests.
    It defines the JSON schemas for valid responses and error indications from the AI.
    """
    DETAILED_RESPONSE_JSON_SCHEMA = """
{
"input": "<user input>",
"error": 0,
"commands": [
{
"seq": <Order of Command>,
"cmd_to_execute": "<commands and arguments to execute>",
"cmd_explanations": ["<explanation of command 1>", "<explanation of command 2>", ...],
"arg_explanations": {"<arg1>": "<explanation of arg1>", "<arg2>": "<explanation of argument 2>", ...}
},
{
"seq": <Order of Command>,
"cmd_to_execute": "<commands and arguments to execute>",
"cmd_explanations": ["<explanation of command 1>", "<explantion of command 2>", ...],
"arg_explanations": {"<arg1>": "<explanation of arg1>", "<arg2>": "<explanation of argument 2>", ...}
}
]
}
"""

    CONDENSED_RESPONSE_JSON_SCHEMA = """
{
"commands": ["<commands and arguments to execute>", "<commands and arguments to execute>", ...]
}
"""
    INVALID_REQUEST_JSON_RESPONSE = """{"input": "<user input>", "error": 1}"""
    INVALID_REQUEST_CONDENSED_JSON_RESPONSE = """{"error": 1}"""

    SAMPLE_TARGET_OS_FOR_EXAMPLES = "macOS-13.3.1-x86-64bit"
    EXAMPLE_REQUEST_CONDA_INSTALL = "install conda"
    EXAMPLE_OUTPUT_CONDA_DETAILED = """
{
"input": "install conda",
"error": 0,
"commands": [
{
"seq": 1,
"cmd_to_execute": "curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh",
"cmd_explanations": ["The curl command is used to issue web requests, e.g. download web pages."],
"arg_explanations": {
"-O": "specifies that we want to save the response to a file.",
"https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh": "is the URL of the file we want to download."
}
},
{
"seq": 2,
"cmd_to_execute": "bash Miniconda3-latest-MacOSX-x86_64.sh",
"cmd_explanations": ["The bash command is used to execute shell scripts."],
"arg_explanations": {"Miniconda3-latest-MacOSX-x86_64.sh": "is the name of the file we want to execute."}
}
]
}
"""
    EXAMPLE_OUTPUT_CONDA_CONDENSED = """
{
"commands": ["curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh", "bash Miniconda3-latest-MacOSX-x86_64.sh"]
}
"""
    EXAMPLE_REQUEST_FILE_SEARCH = "search ~/Documents directory for any python file that begins with 'test'"
    EXAMPLE_OUTPUT_SEARCH_DETAILED = """
{
"input": "search the ~/Documents/ directory for any python file that begins with 'test'",
"error" : 0,
"commands": [
{
"seq": 1,
"cmd_to_execute": "find /Documents/ -name 'test*.py'",
"cmd_explanations": ["find is used to list files."],
"arg_explanations": {
"/Documents": "specifies the folder to search in.",
"-name 'test*.py'": "specifies that we want to search for files starting with test that are python files."
}
}
]
}
"""
    EXAMPLE_OUTPUT_SEARCH_CONDENSED = """
{
"commands": ["find ~/Documents/ -name 'test*.py'"]
}
"""
    EXAMPLE_REQUEST_PROCESS_LIST = "list all processes using more than 50 MB of memory"
    EXAMPLE_OUTPUT_PROCESS_CONDENSED = """
{
"commands": ["ps -axm -o %mem,rss,comm | awk '$1 > 0.5 { printf(\\"%.0fMB\\t%s\\n\\", $2/1024, $3); }'"]
}
"""
    EXAMPLE_AMBIGUOUS_REQUEST = "the quick brown fox jumped over"
    EXAMPLE_OUTPUT_AMBIGUOUS_DETAILED = """{"input": "the quick brown fox jumped over", "error": 1}"""
    EXAMPLE_OUTPUT_AMBIGUOUS_CONDENSED = """{"error": 1}"""

    def __init__(self):
        pass

    def _determine_instruction_json_schema(self, use_condensed_format: bool) -> str:
        return self.CONDENSED_RESPONSE_JSON_SCHEMA if use_condensed_format else self.DETAILED_RESPONSE_JSON_SCHEMA

    def _determine_error_json_response(self, use_condensed_format: bool) -> str:
        return self.INVALID_REQUEST_CONDENSED_JSON_RESPONSE if use_condensed_format else self.INVALID_REQUEST_JSON_RESPONSE

    def generate_initial_ai_directive(self, use_condensed_format: bool) -> str:
        json_response_template = self._determine_instruction_json_schema(use_condensed_format)
        json_error_template = self._determine_error_json_response(use_condensed_format)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""
Provide the appropriate command-line commands that can be executed for a user request (keep in mind the platform of the user).
Today's date/time is {current_timestamp}.
If the request is possible, please provide commands that can be executed in the command line and do not require a GUI.
Do not include commands that require a yes/no response.
For each command, explain the command and any arguments used.
Try to find the simplest command(s) that can be used to execute the request.

If the request is valid, format each command output in the following JSON format: {json_response_template}

            If the request is invalid, please return the following JSON format: {json_error_template}
            """

    def _construct_ai_interaction_message(self, role_type: str, message_content: str) -> dict:
        return {"role": role_type, "parts": [message_content]}

    def _create_user_request_message_for_instruction_gen(self, end_user_query: str, target_os_descriptor: str) -> dict:
        formatted_query_content = (
            f"""Provide the appropriate command-line commands that can be executed on a {target_os_descriptor} machine for the user request: "{end_user_query}"."""
        )
        return self._construct_ai_interaction_message("user", formatted_query_content)

    def _create_ai_response_message_for_instruction_gen(self, ai_generated_json_output: str) -> dict:
        return self._construct_ai_interaction_message("model", ai_generated_json_output)

    def assemble_instruction_generation_training_examples(self, use_condensed_format: bool) -> list:
        initial_directive_message = self.generate_initial_ai_directive(use_condensed_format)
        dialogue_sequence = [
            self._construct_ai_interaction_message("user", initial_directive_message),
            self._construct_ai_interaction_message("model", "Understood!"), 
        ]
        conda_user_request = self._create_user_request_message_for_instruction_gen(
            self.EXAMPLE_REQUEST_CONDA_INSTALL, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
        )
        conda_ai_response_content = self.EXAMPLE_OUTPUT_CONDA_CONDENSED if use_condensed_format else self.EXAMPLE_OUTPUT_CONDA_DETAILED
        conda_ai_response = self._create_ai_response_message_for_instruction_gen(conda_ai_response_content)
        dialogue_sequence.extend([conda_user_request, conda_ai_response])

        search_user_request = self._create_user_request_message_for_instruction_gen(
            self.EXAMPLE_REQUEST_FILE_SEARCH, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
        )
        search_ai_response_content = self.EXAMPLE_OUTPUT_SEARCH_CONDENSED if use_condensed_format else self.EXAMPLE_OUTPUT_SEARCH_DETAILED
        search_ai_response = self._create_ai_response_message_for_instruction_gen(search_ai_response_content)
        dialogue_sequence.extend([search_user_request, search_ai_response])

        if use_condensed_format:
            process_user_request = self._create_user_request_message_for_instruction_gen(
                self.EXAMPLE_REQUEST_PROCESS_LIST, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
            )
            process_ai_response = self._create_ai_response_message_for_instruction_gen(self.EXAMPLE_OUTPUT_PROCESS_CONDENSED)
            dialogue_sequence.extend([process_user_request, process_ai_response])

        ambiguous_user_request = self._create_user_request_message_for_instruction_gen(
            self.EXAMPLE_AMBIGUOUS_REQUEST, target_os_descriptor=self.SAMPLE_TARGET_OS_FOR_EXAMPLES
        )
        ambiguous_ai_response_content = self.EXAMPLE_OUTPUT_AMBIGUOUS_CONDENSED if use_condensed_format else self.EXAMPLE_OUTPUT_AMBIGUOUS_DETAILED
        ambiguous_ai_response = self._create_ai_response_message_for_instruction_gen(ambiguous_ai_response_content)
        dialogue_sequence.extend([ambiguous_user_request, ambiguous_ai_response])
        
        return dialogue_sequence

    def format_actual_user_request_for_instruction_gen(self, end_user_query: str, current_target_os_descriptor: str) -> dict:
        return self._create_user_request_message_for_instruction_gen(end_user_query, current_target_os_descriptor)

    def format_actual_ai_response_for_instruction_gen(self, ai_generated_json_output: str) -> dict:
        return self._create_ai_response_message_for_instruction_gen(ai_generated_json_output)