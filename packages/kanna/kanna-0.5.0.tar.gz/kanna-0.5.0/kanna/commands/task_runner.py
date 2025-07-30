import os
import subprocess
import sys
import time

from kanna.renderers import ExecutionRecorder
from kanna.utils import get_command
from kanna.utils.arguments import ArgumentParser
from kanna.utils.colors import Colors
from kanna.utils.outputs import OutputParser
from kanna.utils.project import KannaProject


class TaskRunner:
    def __init__(
        self,
        project: KannaProject,
        argument_parser: ArgumentParser,
        output_parser: OutputParser,
        dry_run: bool = False,
        recorder: ExecutionRecorder | None = None,
    ):
        self.project = project
        self.dry_run = dry_run
        self.recorder = recorder
        self._visited: set[str] = set()
        self._argument_parser = argument_parser
        self._output_parser = output_parser
        self._task_outputs: dict[str, str] = {}

    def run(self, task: str) -> set[str]:
        current_command = get_command(identifier=task, project=self.project)

        if current_command is None:
            sys.exit(f"Error: Task '{task}' was not defined.")

        first_run = task not in self._visited
        self._visited.add(task)

        if isinstance(current_command, str):
            self._execute(task, current_command)
            return self._visited

        # 1) Pre-tasks
        self._run_phase(task, current_command.pre, first_run, phase='pre')

        # 2) Main command
        self._execute(task, current_command.command, current_command.env)

        # 3) Post-tasks
        self._run_phase(task, current_command.post, first_run, phase='post')

        return self._visited

    def _run_phase(
        self, parent: str, tasks: list[str], first_run: bool, phase: str
    ) -> None:
        if not tasks:
            return

        if first_run:
            for child in tasks:
                if self.recorder:
                    self.recorder.record_effect(parent, child)
                self.run(child)
        else:
            print(
                f"{Colors.OKBLUE}Info: Skipping {phase}-tasks for '{parent}' "
                f'({", ".join(tasks)}) because it has already been executed.{Colors.ENDC}'
            )

    def _output_sdout_to_shell(self, process: subprocess.Popen[bytes]) -> str:
        output = ''

        if process.stdout is None:
            print('Error: process.stdout is None')
            return output

        while line := process.stdout.readline():
            if line == b'' and process.poll() is not None:
                break

            line = line.strip().decode('utf-8')
            print(line)
            output += line + '\n'

        return output

    def _output_stderr_to_shell(
        self, result: int | None, process: subprocess.Popen[bytes]
    ) -> None:
        if result is not None and result != 0:
            if process.stderr is None:
                return

            sys.exit(b''.join(process.stderr.readlines()).decode('utf-8'))

    def _dispatch_shell(
        self, task: str, command: str, env: str | None = None
    ) -> None:
        # Use BOLD and UNDERLINE for the task header
        print(f'\n{Colors.BOLD}📓 Executing Task: {task}{Colors.ENDC}')
        print(f'{Colors.OKBLUE}✍️ Command: {command}{Colors.ENDC}\n')

        start_time = time.perf_counter()
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
        )

        output = self._output_sdout_to_shell(process)

        result = process.poll()

        self._output_stderr_to_shell(result, process)

        end_time = time.perf_counter()
        print(
            f'\n✨ Finished executing task: {task} and it took: {end_time - start_time:.2f}s \n'
        )

        self._task_outputs[task] = output

    def _dispatch_dry_run(self, task: str, command: str) -> None:
        print(
            f'{Colors.OKBLUE}[DRY-RUN]{Colors.ENDC} Would Execute Task {Colors.BOLD}{task}{Colors.ENDC}: {command}'
        )

    def _execute(self, task: str, command: str, env: str | None = None) -> None:
        if not command:
            return

        if env:
            self.project.load_env(env)

        if not self.dry_run:
            command = self._argument_parser.handle_command_custom_args(
                command=command
            )
            command = self._output_parser.handle_task_outputs_replacing(
                task_outputs=self._task_outputs, command=command
            )

        if self.recorder:
            self.recorder.record_start(task)

        if self.dry_run:
            self._dispatch_dry_run(task, command)
        else:
            self._dispatch_shell(task, command)
