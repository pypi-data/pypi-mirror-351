# coding:utf-8

from argparse import Namespace
from errno import ECANCELED
from errno import EINVAL
from errno import ENOENT
from errno import ENOTRECOVERABLE
import logging
from logging import Logger
from os import getenv
import sys
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple

from xkits_logger.logger import Logger as Log

from xkits_command.attribute import __project__
from xkits_command.parser import ArgParser


class CommandArgument:
    """Define a new command-line node.

    For example:

    >>> from xkits_command import ArgParser\n
    >>> from xkits_command import CommandArgument\n

    >>> @CommandArgument("example")\n
    >>> def cmd(_arg: ArgParser):\n
    >>>     _arg.add_opt_on("-t", "--test")\n
    """

    def __init__(self, name: str, **kwargs):
        """Initialize the node.

        @param name: Node name
        @type name: str

        @param description: Text to display before the argument help
        @type description: str (by default, no text)

        @param epilog: Text to display after the argument help
        @type epilog: str (by default, no text)

        @param help: Help message as a subcommand
        @type help: str

        @param add_help: Add a -h/--help option to the node
        @type add_help: bool (default: True)
        """
        if "help" in kwargs and "description" not in kwargs:
            kwargs["description"] = kwargs["help"]
        if "description" in kwargs and "help" not in kwargs:
            kwargs["help"] = kwargs["description"]
        self.__name: str = name
        self.__prev: CommandArgument = self
        self.__cmds: Command = Command()
        self.__options: Dict[str, Any] = kwargs
        self.__bind: Optional[CommandExecutor] = None
        self.__subs: Optional[Tuple[CommandArgument, ...]] = None
        self.__func: Optional[Callable[[ArgParser], None]] = None

    def __call__(self, cmd_func: Callable[[ArgParser], None]):
        self.__func = cmd_func
        return self

    @property
    def func(self) -> Callable[[ArgParser], None]:
        if self.__func is None:
            raise ValueError("No function")  # pragma: no cover
        return self.__func

    @property
    def name(self) -> str:
        return self.__name

    @property
    def root(self) -> "CommandArgument":
        root = self.__prev
        while root.prev != root:
            root = root.prev
        return root

    @property
    def prev(self) -> "CommandArgument":
        return self.__prev

    @prev.setter
    def prev(self, value: "CommandArgument"):
        assert isinstance(value, CommandArgument)
        self.__prev = value

    @property
    def cmds(self) -> "Command":
        return self.__cmds

    @property
    def options(self) -> Dict[str, Any]:
        return self.__options

    @property
    def bind(self) -> Optional["CommandExecutor"]:
        return self.__bind

    @bind.setter
    def bind(self, value: "CommandExecutor"):
        assert isinstance(value, CommandExecutor)
        self.__bind = value

    @property
    def subs(self) -> Optional[Tuple["CommandArgument", ...]]:
        return self.__subs

    @subs.setter
    def subs(self, value: Tuple["CommandArgument", ...]):
        assert isinstance(value, Tuple)
        for sub in value:
            assert isinstance(sub, CommandArgument)
        self.__subs = value

    @property
    def sub_dest(self) -> str:
        node: CommandArgument = self
        subs: List[str] = [self.name]
        while node.prev is not node:
            node = node.prev
            subs.insert(0, node.name)
        name = "_".join(subs)
        return f"__sub_dest_{name}__"


class CommandExecutor:
    """Define the main callback function, and bind it to a node and
    all subcommands.

    For example:

    >>> from xkits_command import Command\n
    >>> from xkits_command import CommandExecutor\n

    >>> @CommandExecutor(cmd, cmd_get, cmd_set)\n
    >>> def run(cmds: Command) -> int:\n
    >>>     return 0\n
    """

    def __init__(self, cmd_bind: CommandArgument, *sub_cmds: CommandArgument,
                 skip: bool = False):
        """Initialize the node.

        @param cmd_bind: Bind to a root command node
        @type name: CommandArgument

        @param *sub_cmds: All required subcommands
        @type *sub_cmds: CommandArgument

        @param skip: This node (CommandExecutor, CommandCreation and
        CommandDeletion) does not run when a subcommand is specified,
        run this node without any subcommands
        @type skip: bool (default: False)
        """
        assert isinstance(cmd_bind, CommandArgument)
        assert isinstance(skip, bool)
        cmd_bind.bind = self
        cmd_bind.subs = sub_cmds
        for sub in sub_cmds:
            sub.prev = cmd_bind
        cmd_bind.cmds.root = cmd_bind.root
        self.__skip: bool = skip
        self.__bind: CommandArgument = cmd_bind
        self.__prep: Optional["CommandCreation"] = None
        self.__done: Optional["CommandDeletion"] = None
        self.__func: Optional[Callable[["Command"], int]] = None

    def __call__(self, run_func: Callable[["Command"], int]):
        self.__func = run_func
        return self

    @property
    def func(self) -> Callable[["Command"], int]:
        if self.__func is None:
            raise ValueError("No function")  # pragma: no cover
        return self.__func

    @property
    def bind(self) -> CommandArgument:
        return self.__bind

    @property
    def prep(self) -> Optional["CommandCreation"]:
        return self.__prep

    @prep.setter
    def prep(self, value: "CommandCreation"):
        assert isinstance(value, CommandCreation)
        self.__prep = value

    @property
    def done(self) -> Optional["CommandDeletion"]:
        return self.__done

    @done.setter
    def done(self, value: "CommandDeletion"):
        assert isinstance(value, CommandDeletion)
        self.__done = value

    @property
    def skip(self) -> bool:
        return self.__skip


class CommandCreation:
    """Define prepare callback function, and bind it with main callback.

    For example:

    >>> from xkits_command import Command\n
    >>> from xkits_command import CommandCreation\n
    >>> from xkits_command import CommandExecutor\n

    >>> @CommandExecutor(cmd, cmd_get, cmd_set)\n
    >>> def run(cmds: Command) -> int:\n
    >>>     return 0\n

    >>> @CommandCreation(run)\n
    >>> def pre(cmds: Command) -> int:\n
    >>>     return 0\n
    """

    def __init__(self, run_bind: CommandExecutor):
        """Initialize the node.

        @param cmd_bind: Bind to a root command node
        @type name: CommandArgument
        """
        assert isinstance(run_bind, CommandExecutor)
        run_bind.prep = self
        self.__main: CommandExecutor = run_bind
        self.__func: Optional[Callable[["Command"], int]] = None

    def __call__(self, run_func: Callable[["Command"], int]):
        self.__func = run_func
        return self

    @property
    def func(self) -> Callable[["Command"], int]:
        if self.__func is None:
            raise ValueError("No function")  # pragma: no cover
        return self.__func

    @property
    def main(self) -> CommandExecutor:
        return self.__main


class CommandDeletion:
    """Define purge callback function, and bind it with main callback.

    For example:

    >>> from xkits_command import Command\n
    >>> from xkits_command import CommandDeletion\n
    >>> from xkits_command import CommandExecutor\n

    >>> @CommandExecutor(cmd, cmd_get, cmd_set)\n
    >>> def run(cmds: Command) -> int:\n
    >>>     return 0\n

    >>> @CommandDeletion(run)\n
    >>> def end(cmds: Command) -> int:\n
    >>>     return 0\n
    """

    def __init__(self, run_bind: CommandExecutor):
        """Initialize the node.

        @param cmd_bind: Bind to a root command node
        @type name: CommandArgument
        """
        assert isinstance(run_bind, CommandExecutor)
        run_bind.done = self
        self.__main: CommandExecutor = run_bind
        self.__func: Optional[Callable[["Command"], int]] = None

    def __call__(self, run_func: Callable[["Command"], int]):
        self.__func = run_func
        return self

    @property
    def func(self) -> Callable[["Command"], int]:
        if self.__func is None:
            raise ValueError("No function")  # pragma: no cover
        return self.__func

    @property
    def main(self) -> CommandExecutor:
        return self.__main


class Command(Log):
    """Singleton command-line tool based on argparse.

    Define and bind all callback functions before calling run() or parse().

    For example:

    >>> from typing import Optional\n
    >>> from typing import Sequence\n

    >>> from xkits_command import ArgParser\n
    >>> from xkits_command import Command\n
    >>> from xkits_command import CommandArgument\n
    >>> from xkits_command import CommandCreation\n
    >>> from xkits_command import CommandDeletion\n
    >>> from xkits_command import CommandExecutor\n

    >>> @CommandArgument("example")\n
    >>> def cmd(_arg: ArgParser):\n
    >>>     _arg.add_opt_on("-t", "--test")\n

    >>> @CommandExecutor(cmd, cmd_get, cmd_set)\n
    >>> def run(cmds: Command) -> int:\n
    >>>     return 0\n

    >>> @CommandCreation(run)\n
    >>> def pre(cmds: Command) -> int:\n
    >>>     return 0\n

    >>> @CommandDeletion(run)\n
    >>> def end(cmds: Command) -> int:\n
    >>>     return 0\n

    >>> def main(argv: Optional[Sequence[str]] = None) -> int:\n
    >>>     return Command().run(\n
    >>>         root=cmd,\n
    >>>         argv=argv,\n
    >>>         prog="xkits-command-example",\n
    >>>         description="Simple command-line tool based on argparse.")\n
    """

    LOGGER_ARGUMENT_GROUP = "logger options"

    __INSTANCE: Optional["Command"] = None
    __INITIALIZED: bool = False

    def __init__(self):
        if not self.__INITIALIZED:
            self.__prog: str = __project__
            self.__root: Optional[CommandArgument] = None
            self.__args: Namespace = Namespace()
            self.__version: Optional[str] = None
            self.__enabled_logger: bool = True
            self.__INITIALIZED = True
            super().__init__()

    def __new__(cls):
        if not cls.__INSTANCE:
            cls.__INSTANCE = super(Command, cls).__new__(cls)
        return cls.__INSTANCE

    @property
    def prog(self) -> str:
        return self.__prog

    @property
    def root(self) -> Optional[CommandArgument]:
        """Root Command."""
        return self.__root

    @root.setter
    def root(self, value: CommandArgument):
        assert isinstance(value, CommandArgument)
        self.__root = value

    @property
    def args(self) -> Namespace:
        """Namespace after parse arguments."""
        assert isinstance(self.__args, Namespace)
        return self.__args

    @args.setter
    def args(self, value: Namespace):
        assert isinstance(value, Namespace)
        self.__args = value

    @property
    def version(self) -> Optional[str]:
        """Custom version for "-v" or "--version" output."""
        return self.__version

    @version.setter
    def version(self, value: str):
        assert isinstance(value, str)
        _version = value.strip()
        self.__version = _version

    @property
    def enabled_logger(self) -> bool:
        return self.__enabled_logger

    @enabled_logger.setter
    def enabled_logger(self, value: bool):
        assert isinstance(value, bool)
        self.__enabled_logger = value

    @property
    def logger(self) -> Logger:
        """Logger."""
        return self.get_logger(self.prog)

    def __add_optional_version(self, _arg: ArgParser):
        version = self.version
        if not isinstance(version, str):
            return  # pragma: no cover

        options = _arg.filter_optional_name("-v", "--version")
        if len(options) > 0:
            _arg.add_argument(*options, action="version",
                              version=f"%(prog)s {version.strip()}")

    def __add_inner_parser_tail(self, _arg: ArgParser):

        def filter_optional_name(*name: str) -> Optional[str]:
            options = _arg.filter_optional_name(*name)
            if len(options) > 0:
                for i in name:
                    if i in options:
                        return i
            return None

        def add_optional_level():
            group = _arg.argument_group(self.LOGGER_ARGUMENT_GROUP)
            group_level = group.add_mutually_exclusive_group()

            option_level = filter_optional_name("--level", "--log-level")
            if isinstance(option_level, str):
                DEF_LOG_LEVEL: str = getenv("LOG_LEVEL", self.LOG_LEVELS.INFO.value).lower()  # noqa:E501
                group_level.add_argument(
                    option_level,
                    type=str,
                    nargs="?",
                    const=DEF_LOG_LEVEL,
                    default=DEF_LOG_LEVEL,
                    choices=self.ALLOWED_LOG_LEVELS,
                    dest="_log_level_str_",
                    help=f"Logger output level, default is {DEF_LOG_LEVEL}.")

            for level in self.ALLOWED_LOG_LEVELS:
                options = []
                if isinstance(filter_optional_name(f"-{level[0]}"), str):
                    options.append(f"-{level[0]}")
                if isinstance(filter_optional_name(f"--{level}"), str):
                    options.append(f"--{level}")
                elif isinstance(filter_optional_name(f"--{level}-level"), str):
                    options.append(f"--{level}-level")

                if not options:
                    continue
                group_level.add_argument(*options,
                                         action="store_const",
                                         const=level,
                                         dest="_log_level_str_",
                                         help=f"Logger level set to {level}.")

        def add_optional_stream():
            option = filter_optional_name("--log", "--log-file")
            if not isinstance(option, str):
                return

            group = _arg.argument_group(self.LOGGER_ARGUMENT_GROUP)
            group.add_argument(option,
                               type=str,
                               nargs=1,
                               default=[],
                               metavar="FILE",
                               action="extend",
                               dest="_log_files_",
                               help="Logger output to file.")

        def add_optional_format():
            option = filter_optional_name("--format", "--log-format")
            if not isinstance(option, str):
                return

            DEFAULT_LOG_FMT = "%(log_color)s%(asctime)s"\
                " %(process)d %(threadName)s %(levelname)s"\
                " %(funcName)s %(filename)s:%(lineno)s"\
                " %(message)s"

            group = _arg.argument_group(self.LOGGER_ARGUMENT_GROUP)
            group.add_argument(option,
                               type=str,
                               nargs="?",
                               const=DEFAULT_LOG_FMT,
                               default=self.DEFAULT_LOG_FORMAT,
                               metavar="STRING",
                               dest="_log_format_",
                               help="Logger output format.")

        def add_optional_console():
            group = _arg.argument_group(self.LOGGER_ARGUMENT_GROUP)
            group_std = group.add_mutually_exclusive_group()

            option = filter_optional_name("--stdout", "--log-stdout")
            if isinstance(option, str):
                group_std.add_argument(option,
                                       const=sys.stdout,
                                       action="store_const",
                                       dest="_log_console_",
                                       help="Logger output to stdout.")

            option = filter_optional_name("--stderr", "--log-stderr")
            if isinstance(option, str):
                group_std.add_argument(option,
                                       const=sys.stderr,
                                       action="store_const",
                                       dest="_log_console_",
                                       help="Logger output to stderr.")

        if self.enabled_logger:
            add_optional_level()
            add_optional_stream()
            add_optional_format()
            add_optional_console()

    def __parse_logger(self, args: Namespace):
        if not self.enabled_logger:
            return

        def parse_format() -> Optional[str]:
            if hasattr(args, "_log_format_"):
                fmt = getattr(args, "_log_format_")
                if isinstance(fmt, str):
                    return fmt
            return None

        def parse_level() -> Optional[str]:
            if hasattr(args, "_log_level_str_"):
                level = getattr(args, "_log_level_str_")
                if isinstance(level, str):
                    return level.upper()
            return None

        def parse_console() -> Optional[Any]:
            return getattr(args, "_log_console_", None)

        def parse_files() -> List[str]:
            return getattr(args, "_log_files_", [])

        fmt: Optional[str] = parse_format()
        level_name: Optional[str] = parse_level()
        console: Optional[Any] = parse_console()

        handlers: List[logging.Handler] = []
        if console is not None:
            handlers.append(Log.new_stream_handler(stream=console, fmt=fmt))
        for filename in parse_files():
            handlers.append(Log.new_file_handler(filename=filename, fmt=fmt))
        self.initiate_logger(self.logger, level=level_name, handlers=handlers)

    def __add_parser(self, _map: Dict[CommandArgument, ArgParser],
                     arg_root: ArgParser, cmd_root: CommandArgument, **kwargs):
        assert isinstance(cmd_root, CommandArgument)
        assert cmd_root not in _map
        _map[cmd_root] = arg_root

        if not cmd_root.subs or len(cmd_root.subs) <= 0:
            return

        _sub = arg_root.add_subparsers(dest=cmd_root.sub_dest)
        for sub in cmd_root.subs:
            assert isinstance(sub, CommandArgument)
            options = sub.options.copy()
            for key, value in kwargs.items():
                options.setdefault(key, value)
            options.setdefault("epilog", arg_root.epilog)
            options.setdefault("prev_parser", arg_root)
            _arg: ArgParser = _sub.add_parser(sub.name, **options)
            self.__add_parser(_map, _arg, sub)

    def __add_option(self, _map: Dict[CommandArgument, ArgParser]):
        for _cmd, _arg in _map.items():
            _cmd.func(_arg)
            self.__add_inner_parser_tail(_arg)

    @classmethod
    def check_error(cls, value: Any) -> int:
        """Check value is an error.

        Return True if value is an error, otherwise False.
        """
        return value if isinstance(value, int) else 0 if value in (None, True) else EINVAL  # noqa:E501

    def parse(self, root: Optional[CommandArgument] = None,
              argv: Optional[Sequence[str]] = None, **kwargs) -> Namespace:
        """Parse the command line."""
        if root is None:
            root = self.root
        assert isinstance(root, CommandArgument)

        _map: Dict[CommandArgument, ArgParser] = {}
        _arg = ArgParser(argv=argv, **kwargs)
        self.__prog = _arg.prog
        self.__add_optional_version(_arg)
        # To support preparse_from_sys_argv(), all subparsers must be added
        # first. Otherwise, an error will occur during the help action.
        self.__add_parser(_map, _arg, root, **kwargs)
        self.__add_option(_map)

        args = _arg.parse_args(args=argv)
        assert isinstance(args, Namespace)
        self.__parse_logger(args)
        self.args = args
        return self.args

    def has_sub(self, root: CommandArgument,
                args: Optional[Namespace] = None) -> bool:
        """If the root command node has any subcommand nodes, return true.

        @param root: Command node
        @type root: CommandArgument

        @param args: Command arguments
        @type args: Namespace or None (default self.args if None is specified)

        @return: bool
        """
        if args is None:
            args = self.args
        assert isinstance(root, CommandArgument)
        assert isinstance(args, Namespace)
        return isinstance(getattr(args, root.sub_dest), str)\
            if hasattr(args, root.sub_dest) else False

    def __run(self, args: Namespace, root: CommandArgument) -> int:
        assert isinstance(root, CommandArgument)
        assert isinstance(root.bind, CommandExecutor)

        if not root.bind.skip or not self.has_sub(root, args):
            ret = root.bind.func(self)
            if self.check_error(ret):
                return ret

        if hasattr(args, root.sub_dest):
            sub_dest = getattr(args, root.sub_dest)
            if isinstance(sub_dest, str):
                assert isinstance(root.subs, (list, tuple))
                for sub in root.subs:
                    assert isinstance(sub, CommandArgument)
                    if sub.name == sub_dest:
                        ret = self.__run(args, sub)
                        if self.check_error(ret):
                            return ret

        done = root.bind.done
        if done is not None:
            assert isinstance(done, CommandDeletion)
            if not root.bind.skip or not self.has_sub(root, args):
                ret = done.func(self)  # purge
                if self.check_error(ret):
                    return ret
        return 0

    def __pre(self, args: Namespace, root: CommandArgument) -> int:
        assert isinstance(root, CommandArgument)
        assert isinstance(root.bind, CommandExecutor)

        prep = root.bind.prep
        if prep is not None:
            assert isinstance(prep, CommandCreation)
            if not root.bind.skip or not self.has_sub(root, args):
                ret = prep.func(self)
                if self.check_error(ret):
                    return ret

        if hasattr(args, root.sub_dest):
            sub_dest = getattr(args, root.sub_dest)
            if isinstance(sub_dest, str):
                assert isinstance(root.subs, (list, tuple))
                for sub in root.subs:
                    assert isinstance(sub, CommandArgument)
                    if sub.name == sub_dest:
                        return self.__pre(args, sub)
        return 0

    def run(self,
            root: Optional[CommandArgument] = None,
            argv: Optional[Sequence[str]] = None,
            **kwargs) -> int:
        """Parse and run the command line."""
        if root is None:
            root = self.root

        if not isinstance(root, CommandArgument):
            self.logger.debug("cannot find root")
            return ENOENT

        kwargs.pop("prog", None)  # Please do not specify prog
        if "description" in root.options:  # Default use root's description
            kwargs["description"] = root.options["description"]
        args = self.parse(root, argv, **kwargs)
        self.logger.debug("%s", args)

        try:
            version = self.version
            if isinstance(version, str):
                # Output version for the debug level. Internal log
                # items are debug level only, except for errors.
                self.logger.debug("version: %s", version)

            ret = self.__pre(args, root)
            if self.check_error(ret):
                return ret
            return self.__run(args, root)
        except KeyboardInterrupt:
            return ECANCELED
        except BaseException:  # pylint: disable=broad-except
            self.logger.exception("Something went wrong:")
            return ENOTRECOVERABLE
