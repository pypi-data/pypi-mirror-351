from contextlib import suppress
from io import StringIO
from textwrap import dedent

from clypi import Command, Positional, arg, get_config
from tests.prompt_test import replace_stdout


def _assert_stdout_matches(stdout: StringIO, expected: str):
    __tracebackhide__ = True
    stdout_str = stdout.getvalue()
    assert stdout_str.strip() == expected.strip()


def _get_help(cmd: type[Command], err: Exception | None = None) -> StringIO:
    with replace_stdout() as stdout:
        with suppress(SystemExit):
            cmd.print_help(err)

        return stdout


class TestCase:
    def setup_method(self):
        conf = get_config()
        conf.disable_colors = True
        conf.fallback_term_width = 50

    def test_basic_example(self):
        class Main(Command):
            pass

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main
                """
            ),
        )

    def test_basic_example_with_error(self):
        class Main(Command):
            pass

        stdout = _get_help(Main, RuntimeError())
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main

                ┏━ Error ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ RuntimeError                                   ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_with_all_args(self):
        class Subcmd(Command):
            pass

        class Main(Command):
            subcommand: Subcmd
            positional: Positional[str]
            flag: bool = False
            option: int = 5

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [POSITIONAL] [OPTIONS] COMMAND
                
                ┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ subcmd                                         ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ [POSITIONAL]                                   ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --flag                                         ┃
                ┃ --option <OPTION>                              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_with_all_args_and_help(self):
        class Subcmd(Command):
            pass

        class Main(Command):
            subcommand: Subcmd
            positional: Positional[str] = arg(help="Some positional arg")
            flag: bool = arg(False, help="Some flag")
            option: int = arg(5, help="Some option")

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [POSITIONAL] [OPTIONS] COMMAND
                
                ┏━ Subcommands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ subcmd                                         ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Arguments ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ [POSITIONAL]  Some positional arg              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --flag             Some flag                   ┃
                ┃ --option <OPTION>  Some option                 ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_group_option(self):
        class Main(Command):
            option: int = arg(5)
            option2: int = arg(5, group="foo")

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [OPTIONS]
               
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --option <OPTION>                              ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
               
                ┏━ Foo options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ --option2 <OPTION2>                            ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_flag_extras(self):
        class Main(Command):
            option: bool = arg(False, short="o", negative="no_option")

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [OPTIONS]
               
                ┏━ Options ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
                ┃ -o, --option/--no-option                       ┃
                ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                """
            ),
        )

    def test_basic_example_hidden_option(self):
        class Main(Command):
            option: int = arg(5, hidden=True)

        stdout = _get_help(Main)
        _assert_stdout_matches(
            stdout,
            dedent(
                """
                Usage: main [OPTIONS]
                """
            ),
        )
