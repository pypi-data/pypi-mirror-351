import argparse
import enum
import sys
from typing import Optional, TextIO, Union
import pytest
import typecli


def test_positional():
    class Args(typecli.Parser):
        foo: str = typecli.arg(positional=True)

    args = Args.parse(["bar"])

    assert args.foo == "bar"


def test_required_positional():
    @typecli.cli(exit_on_error=False)
    class Args(typecli.Parser):
        foo: str = typecli.arg(positional=True)

    with pytest.raises(argparse.ArgumentError):
        Args.parse([])

    args = Args.parse(["bar"])
    assert args.foo == "bar"


def test_default_positional():
    class Args(typecli.Parser):
        foo: str = typecli.arg(default="bar", positional=True)

    args = Args.parse([])

    assert args.foo == "bar"


def test_list_positional():
    class Args(typecli.Parser):
        s: list[str] = typecli.arg(positional=True)

    args = Args.parse(["a", "b"])

    assert args.s == ["a", "b"]


def test_required():
    @typecli.cli(exit_on_error=False)
    class Args(typecli.Parser):
        foo: str

    with pytest.raises(argparse.ArgumentError):
        Args.parse([])

    args = Args.parse(["--foo", "bar"])
    assert args.foo == "bar"


def test1():
    class Args(typecli.Parser):
        vip: bool
        coins: int
        name: str = typecli.arg(short="n", help="person name")
        male: bool
        age: Optional[int]
        is_ok: bool
        height: int = 190

    args = Args.parse(["--name", "iw", "--hei", "3", "--co", "3"])

    assert args.name == "iw"
    assert not args.male
    assert args.age is None
    assert not args.vip
    assert args.coins == 3
    assert not args.is_ok
    assert args.height == 3


def test2():
    class Args(typecli.Parser):
        verbose: bool = typecli.arg(help="Enable verbose output")
        output_file: Optional[str] = typecli.arg(help="Path to the output file")
        targets: list[str] = typecli.arg(short="t")
        numbers: list[int] = typecli.arg(short="n", help="List of numbers to process")
        input_file: str = typecli.arg(
            default="input.txt", help="Path to the input file"
        )

    args = Args.parse(["-t", "a", "-n", "1", "2"])
    assert isinstance(args, Args)
    assert not args.verbose
    assert args.targets == ["a"]
    assert args.output_file is None
    assert args.input_file == "input.txt"
    assert args.numbers == [1, 2]


def test_construct():
    class Args(typecli.Parser):
        verbose: bool = typecli.arg(help="Enable verbose output")
        output_file: Optional[str] = typecli.arg(help="Path to the output file")
        targets: list[str] = typecli.arg(short="t")
        numbers: list[int] = typecli.arg(short="n", help="List of numbers to process")
        input_file: str = typecli.arg(
            default="input.txt", help="Path to the input file"
        )

    args = Args(verbose=False, output_file=None, targets=["a"], numbers=[1, 2])
    assert isinstance(args, Args)
    assert not args.verbose
    assert args.targets == ["a"]
    assert args.output_file is None
    assert args.input_file == "input.txt"
    assert args.numbers == [1, 2]


def test_default_list():
    class Args(typecli.Parser):
        a: list[int] = typecli.arg(default=[])
        b: list[str] = typecli.arg(default=[])

    args = Args.parse([])
    assert isinstance(args, Args)
    assert args.a == []
    assert args.b == []
    assert id(args.a) != id(args.b)


def test_optional_list():
    class Args(typecli.Parser):
        a: Optional[list[int]]
        b: list[str] = typecli.arg(default=[])

    args = Args.parse([])
    assert isinstance(args, Args)
    assert args.a is None
    assert args.b == []


def test_union():
    class Args(typecli.Parser):
        e: Union[int, str, None]

    none = Args.parse([]).e
    assert none is None, f"{none!r}"

    num = Args.parse(["--e", "1"]).e
    assert num == 1, f"{num!r}"

    s = Args.parse(["--e", "1a"]).e
    assert s == "1a", f"{s!r}"


def test_union_with_default_str():
    class Args(typecli.Parser):
        host: Union[int, str] = typecli.arg(default="127.0.0.1")

    default = Args.parse([]).host
    assert default == "127.0.0.1", f"{default!r}"

    num = Args.parse(["--host", "42"]).host
    assert num == 42, f"{num!r}"

    localhost = Args.parse(["--host", "localhost"]).host
    assert localhost == "localhost", f"{localhost!r}"


def test_union_with_default_int():
    class Args(typecli.Parser):
        host: Union[int, str] = typecli.arg(default=68)

    default = Args.parse([]).host
    assert default == 68, f"{default!r}"

    num = Args.parse(["--host", "42"]).host
    assert num == 42, f"{num!r}"

    localhost = Args.parse(["--host", "localhost"]).host
    assert localhost == "localhost", f"{localhost!r}"


def test_optional_union():
    class Args(typecli.Parser):
        host: Optional[Union[int, str]]

    default = Args.parse([]).host
    assert default is None, f"{default!r}"

    num = Args.parse(["--host", "42"]).host
    assert num == 42, f"{num!r}"

    localhost = Args.parse(["--host", "127.0.0.1"]).host
    assert localhost == "127.0.0.1", f"{localhost!r}"


def test_enum():
    class E(enum.Enum):
        a = enum.auto()
        b = enum.auto()

    class Args(typecli.Parser):
        e: E
        s: str = "s"

    args = Args.parse(["--e", "a"])
    assert isinstance(args, Args)
    assert args.e == E.a, args.e
    assert args.s == "s", args.s


def test_default_enum():
    class E(enum.Enum):
        a = enum.auto()
        b = enum.auto()

    class Args(typecli.Parser):
        e: E = E.b
        s: str = "s"

    args = Args.parse([])
    assert isinstance(args, Args)
    assert args.e == E.b, args.e
    assert args.s == "s", args.s


def test_optional_enum():
    class E(enum.Enum):
        a = enum.auto()
        b = enum.auto()

    class Args(typecli.Parser):
        e: Optional[E]

    none = Args.parse([]).e
    assert none is None, none

    just = Args.parse(["--e", "a"]).e
    assert just == E.a, just


def test_int_enum():
    class E(enum.IntEnum):
        a = 1
        b = 2

    class Args(typecli.Parser):
        e: E

    value_args = Args.parse(["--e", "1"])
    assert isinstance(value_args, Args)
    assert value_args.e == E.a, value_args.e

    name_args = Args.parse(["--e", "b"])
    assert isinstance(name_args, Args)
    assert name_args.e == E.b, name_args.e


def test_flag():
    class Color(enum.Flag):
        RED = enum.auto()
        GREEN = enum.auto()
        BLUE = enum.auto()

    class Args(typecli.Parser):
        color: Color

    args = Args.parse(["--color", "RED", "BLUE"])
    assert isinstance(args, Args)
    assert args.color == Color.RED | Color.BLUE


def test_enum_list():
    class SubApp(enum.Enum):
        radio = enum.auto()
        sound = enum.auto()
        wifi = enum.auto()

    class Args(typecli.Parser):
        run: list[SubApp] = typecli.arg(
            default=[SubApp.radio, SubApp.sound, SubApp.wifi]
        )

    assert (x := Args.parse([]).run) == [SubApp.radio, SubApp.sound, SubApp.wifi], x
    assert Args.parse(["--run"]).run == []
    assert (x := Args.parse(["--run", "radio"]).run) == [SubApp.radio], x
    assert (x := Args.parse(["--run", "radio", "wifi"]).run) == [
        SubApp.radio,
        SubApp.wifi,
    ], x


def test_io():
    class Args(typecli.Parser):
        input: TextIO = typecli.arg(positional=True)
        output: TextIO = typecli.arg(default=sys.stdout, short="o")

    args = Args.parse(["-"])
    assert isinstance(args, Args)
    assert args.input == sys.stdin
    assert args.output == sys.stdout


def test_complicated():
    class Choice(enum.IntEnum):
        foo = 42
        bar = 24

    class Args(typecli.Parser):
        a: Optional[list[Union[Choice, int, str]]]

    none = Args.parse([]).a
    assert none is None

    empty = Args.parse(["--a"]).a
    assert empty == []

    # `Choice` is declared before `str` in `Union[Choice, int, str]`, so "bar" will be treated as Choice.bar instead of "bar"
    array = Args.parse(["--a", "42", "68", "1a", "bar"]).a
    assert array == [Choice.foo, 68, "1a", Choice.bar]
