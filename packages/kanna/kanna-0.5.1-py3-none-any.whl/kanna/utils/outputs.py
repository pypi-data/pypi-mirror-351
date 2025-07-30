import re

from kanna.utils.project import KannaProject


class OutputParser:
    """
    A simple argument parser that can parse command line arguments.
    """

    def __init__(self, project: KannaProject):
        self._project = project
        self._arg_regex = r'{{kanna:output:([\w-]+)}}'

    def _get_command_custom_args(self, command: str) -> set[str]:
        return set(re.findall(self._arg_regex, command) or [])

    def _replace_output_placeholder_with_value(
        self, command: str, arg_mapping: dict[str, str | int | float | bool]
    ) -> str:
        for arg, value in arg_mapping.items():
            placeholder = f'{{{{kanna:output:{arg}}}}}'
            command = command.replace(placeholder, str(value))
        return command

    def handle_task_outputs_replacing(
        self, task_outputs: dict[str, str], command: str
    ) -> str:
        for task_request in self._get_command_custom_args(command):
            if task_request in task_outputs:
                command = self._replace_output_placeholder_with_value(
                    command=command,
                    arg_mapping={task_request: task_outputs[task_request]},
                )

        return command
