# coding:utf-8

from errno import EPERM
import os
import shutil
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Union

from tabulate import tabulate
from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandExecutor

from xargcomplete.attribute import __description__
from xargcomplete.attribute import __project__
from xargcomplete.attribute import __urlhome__
from xargcomplete.attribute import __version__
from xargcomplete.complete import Bash
from xargcomplete.complete import Collections


@CommandArgument("enable", help="Enable completion.")
def add_cmd_enable(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_enable)
def run_cmd_enable(cmds: Command) -> int:
    which = shutil.which("activate-global-python-argcomplete")
    command = f"{which} --user --yes"
    cmds.logger.info(command)
    retcode = os.system(command)
    if retcode != 0:
        return retcode
    Bash.enable()
    return 0


@CommandArgument("update", help="Update completion config.")
def add_cmd_update(_arg: ArgParser):
    group_script = _arg.argument_group("Specify update command or script")
    group_script.add_argument("--script", type=str, nargs=1, metavar="PATH",
                              dest="_commands_", action="extend",
                              help="Specify script path.")
    group_script.add_argument(type=str, nargs="*", metavar="command",
                              dest="_commands_", action="extend",
                              help="Specify command.")


@CommandExecutor(add_cmd_update)
def run_cmd_update(cmds: Command) -> int:
    iter_commands = getattr(cmds.args, "_commands_")
    if len(iter_commands) == 0:
        iter_commands = Collections().cmds
    for cmd in set(iter_commands):
        if shutil.which(cmd) is None:
            cmds.stderr_red(f"Non existent command or script: {cmd}")
            continue
        cmds.stdout(f"Update command or script: {cmd}")
        Bash.update(cmd)
    cmds.stdout_green("Please restart your shell or source the file to activate it.")  # noqa: E501
    cmds.stdout_green(f"Bash: source {os.path.expanduser(Bash.USER_COMPLETION_CFG)}")  # noqa: E501
    return 0


@CommandArgument("remove", help="Remove completion config.")
def add_cmd_remove(_arg: ArgParser):
    allowed = list(Bash.list())
    group_script = _arg.argument_group("Specify remove command or script")
    mgroup_script = group_script.add_mutually_exclusive_group()
    mgroup_script.add_argument("--auto-clean", dest="_clean_",
                               action="store_true",
                               help="Clean invalid Command or scripts.")
    mgroup_script.add_argument("--all", const=allowed,
                               dest="_commands_", action="store_const",
                               help="Remove all Command or scripts.")
    group_script.add_argument(type=str, nargs="*", metavar="command",
                              dest="_commands_", action="extend",
                              help="Specify command or script.",
                              choices=allowed + [[]])


@CommandExecutor(add_cmd_remove)
def run_cmd_remove(cmds: Command) -> int:
    list_commands: List[str] = getattr(cmds.args, "_commands_")
    if getattr(cmds.args, "_clean_"):
        assert isinstance(list_commands, list)
        for cmd in Bash.list():
            if cmd in list_commands:
                continue  # pragma: no cover
            if shutil.which(cmd) is None:
                list_commands.append(cmd)
    for cmd in set(list_commands):
        cmds.stdout(f"Remove command or script: {cmd}")
        assert Bash.remove(cmd)
    return 0


@CommandArgument("list", help="List all completion.")
def add_cmd_list(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd_list)
def run_cmd_list(cmds: Command) -> int:
    table: Dict[str, Dict[str, Union[None, str, Set[str]]]] = {}

    def update_table(cmd: str, shell: str):
        if cmd not in table:
            table[cmd] = {"which": shutil.which(cmd), "shell": set()}
        shell_set = table[cmd]["shell"]
        assert isinstance(shell_set, set)
        shell_set.add(shell)

    def output_table() -> List[Tuple[str, str, str]]:
        datas: List[Tuple[str, str, str]] = []
        for k, v in table.items():
            which = v["which"] if v["which"] is not None else "None"
            shell = v["shell"]
            assert isinstance(which, str)
            assert isinstance(shell, set)
            datas.append((k, which, ", ".join(shell)))
        datas.sort(key=lambda line: line[0])
        datas.insert(0, ("command", "which", "shell"))
        return datas

    for cmd in Bash.list():
        update_table(cmd, "bash")
    cmds.stdout(tabulate(output_table(), headers="firstrow"))
    return 0


@CommandArgument(__project__, description=__description__)
def add_cmd(_arg: ArgParser):
    pass


@CommandExecutor(add_cmd, add_cmd_enable, add_cmd_update, add_cmd_remove,
                 add_cmd_list)
def run_cmd(cmds: Command) -> int:
    if sys.version_info < (3, 8):
        cmds.logger.error("Require Python>=3.8")  # pragma: no cover
        return EPERM  # pragma: no cover
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {__urlhome__}.")  # noqa:E501
