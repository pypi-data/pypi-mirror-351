import re

from kanna.utils.colors import Colors
from kanna.utils.project import KannaProject


class ArgumentParser:
    """
    A simple argument parser that can parse command line arguments.
    """

    def __init__(self, project: KannaProject):
        self._project = project
        self._arg_regex = r'{{kanna:arg:([\w-]+)}}'

    def _get_command_custom_args(self, command: str) -> set[str]:
        return set(re.findall(self._arg_regex, command) or [])

    def _handle_custom_args_propagation(self, arg: str, value: str) -> None:
        if self._project.args[arg].propagate:
            self._project.args[arg].propagated = value

    def _ask_user_for_custom_arg(
        self, arg: str
    ) -> dict[str, str | int | float | bool]:
        # Check if the argument is defined in project.args
        if arg not in self._project.args:
            value = input(
                f'{Colors.OKGREEN}[ARGUMENT] {Colors.BOLD}{arg.capitalize()}{Colors.ENDC}: '
            )
            return {arg: value}

        arg_definition = self._project.args[arg]

        # Use default value if available
        if arg_definition.default:
            # Pretty print default argument
            print(
                f'{Colors.OKGREEN}[ARGUMENT] {Colors.BOLD}{arg}{Colors.ENDC}: '
                f'{Colors.OKCYAN}{arg_definition.default}{Colors.ENDC} (Default)'
            )
            return {arg: arg_definition.default}

        if arg_definition.propagate and arg_definition.propagated:
            # If the argument is propagated, use the propagated value
            print(
                f'{Colors.OKGREEN}[ARGUMENT] {Colors.BOLD}{arg}{Colors.ENDC}: '
                f'{Colors.OKCYAN}{arg_definition.propagated}{Colors.ENDC} (Propagated)'
            )
            return {arg: arg_definition.propagated}

        # If no default, ask user for input
        prompt = f'{Colors.OKGREEN}[ARGUMENT] {Colors.BOLD}{arg.capitalize()}{Colors.ENDC}'

        if arg_definition.help:
            prompt += f' ({arg_definition.help})'

        prompt += f'{Colors.OKGREEN}: {Colors.ENDC}'

        value = input(prompt)

        self._handle_custom_args_propagation(arg, value)

        return {arg: value}

    def _replace_custom_arg_placeholder_with_provided_value(
        self, command: str, arg_mapping: dict[str, str | int | float | bool]
    ) -> str:
        for arg, value in arg_mapping.items():
            placeholder = f'{{{{kanna:arg:{arg}}}}}'
            command = command.replace(placeholder, str(value))
        return command

    def handle_command_custom_args(self, command: str) -> str:
        args_to_ask = self._get_command_custom_args(command)
        for arg in args_to_ask:
            mapping = self._ask_user_for_custom_arg(arg=arg)
            command = self._replace_custom_arg_placeholder_with_provided_value(
                command=command, arg_mapping=mapping
            )

        return command
