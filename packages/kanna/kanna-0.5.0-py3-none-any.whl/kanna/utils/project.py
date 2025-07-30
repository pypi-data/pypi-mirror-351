import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypedDict

import tomli
from dotenv import load_dotenv

type Command = str | CommandConfig
type ICommand = str | ICommandConfig
type IKannaTasks = dict[str, ICommand]
type IKannaArgs = dict[str, IKannaArg]
type IKannaEnvs = dict[str, IKannaEnv]


class ICommandConfig(TypedDict):
    command: str
    help: str
    pre: list[str]
    post: list[str]
    env: str


class IKannaArg(TypedDict):
    default: str | int | float | bool
    help: str


class IKannaEnv(TypedDict):
    path: str


class IKannaTools(TypedDict):
    tasks: IKannaTasks
    args: IKannaArgs


@dataclass
class CommandConfig:
    command: str
    help: str | None = field(default=None)
    pre: list[str] = field(default_factory=list[str])
    post: list[str] = field(default_factory=list[str])
    env: str | None = field(default=None)


@dataclass
class Argument:
    default: str | int | float | bool
    help: str
    propagated: str = field(default='')
    propagate: bool = field(default=False)


@dataclass
class Environment:
    path: str


type KannaTasks = dict[str, Command]
type KannaArgs = dict[str, Argument]
type KannaEnvs = dict[str, Environment]


@dataclass
class KannaProject:
    tasks: KannaTasks
    args: KannaArgs
    envs: KannaEnvs

    @staticmethod
    def _get_commands_from_pyproject(tasks: IKannaTasks) -> KannaTasks:
        normalized_tasks: KannaTasks = {}

        for task, command in tasks.items():
            if isinstance(command, str):
                normalized_tasks[task] = command
                continue

            normalized_tasks[task] = CommandConfig(
                command=command.get('command'),
                help=command.get('help', None),
                pre=command.get('pre', []),
                post=command.get('post', []),
                env=command.get('env', None),
            )

        return normalized_tasks

    @staticmethod
    def _get_args_from_pyproject(args: IKannaArgs) -> KannaArgs:
        normalized_args: KannaArgs = {}

        for arg, value in args.items():
            normalized_args[arg] = Argument(
                default=value.get('default', ''),
                help=value.get('help', ''),
                propagate=value.get('propagate', False),
            )

        return normalized_args

    @staticmethod
    def _get_envs_from_pyproject(envs: IKannaEnvs) -> KannaEnvs:
        normalized_envs: KannaEnvs = {}

        for env, value in envs.items():
            normalized_envs[env] = Environment(path=value.get('path', ''))

        return normalized_envs

    @staticmethod
    def from_pyproject() -> 'KannaProject':
        pyproject = Path('pyproject.toml')

        if not pyproject.exists():
            sys.exit(
                'Initialize a pyproject before calling Kanna'
            )  # TODO: add better error raising

        kanna_tools: IKannaTools | None = None

        with pyproject.open('rb') as config:
            kanna_tools = tomli.load(config).get('tool', {}).get('kanna')

        if kanna_tools is None:
            raise Exception(
                'Kanna tools not found in pyproject.toml. '
                'Please add a [tool.kanna] section.'
            )

        tasks = KannaProject._get_commands_from_pyproject(
            tasks=kanna_tools.get('tasks', {})
        )
        args = KannaProject._get_args_from_pyproject(
            args=kanna_tools.get('args', {})
        )
        envs = KannaProject._get_envs_from_pyproject(
            envs=kanna_tools.get('envs', {})
        )

        return KannaProject(tasks=tasks, args=args, envs=envs)

    def load_env(self, env: str) -> None:
        if env not in self.envs:
            raise Exception(f"Environment '{env}' not found in project.")

        env_path = self.envs[env].path
        if not Path(env_path).exists():
            raise Exception(f"Environment path '{env_path}' does not exist.")

        load_dotenv(dotenv_path=env_path, override=True)
