import argparse
import enum
import logging
import sys
from dataclasses import _MISSING_TYPE, MISSING, Field, dataclass
import functools
from typing import (
    Any,
    BinaryIO,
    Iterable,
    List,
    Optional,
    Sequence,
    TextIO,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
)

if sys.version_info >= (3, 10):
    from types import NoneType
else:
    NoneType = type(None)

T = TypeVar("T")

logger = logging.getLogger(__name__)


def arg(
    default: Union[T, _MISSING_TYPE] = MISSING,
    short="",
    help="",
    positional=False,
):
    """
    short只填字母不填"-"
    """
    if isinstance(default, list):
        # hack: pass list to factory
        factory: Any = default
        default = MISSING
    else:
        factory = MISSING

    kw_only = {"kw_only": False} if sys.version_info >= (3, 10) else {}

    field = Field(
        default=default,
        default_factory=factory,
        metadata={"positional": positional, "short": short, "help": help},
        init=True,
        repr=True,
        hash=None,
        compare=True,
        **kw_only,
    )
    return cast(T, field)


def build_positional(name: str, positional: bool, short: str):
    args: list[str] = []

    text = name.replace("_", "-")
    if positional:
        args.append(text)
    else:
        if short:
            args.append(f"-{short}")
        args.append(f"--{text}")

    return args


def is_primary(kind: type):
    return kind is bool or kind is int or kind is float or kind is str


def is_union(kind: type):
    """判断是否为Union[T]"""
    origin = get_origin(kind)
    return origin is Union


def extract_union(kind: type) -> tuple[type, ...]:
    assert is_union(kind)
    return get_args(kind)


def extract_union_anyway(kind: type) -> tuple[type, ...]:
    return extract_union(kind) if is_union(kind) else (kind,)


def is_optional(kind: type):
    """判断是否为Optional[T]"""
    if is_union(kind):
        args = extract_union(kind)
        return NoneType in args
    return False


def extract_optional(kind: type) -> list[type]:
    """提取Optional[T]中的T"""
    assert is_optional(kind)
    args = extract_union(kind)
    return list(t for t in args if t is not NoneType)


def is_list(kind: type):
    """判断是否为list[T]或List[T]"""
    origin = get_origin(kind)
    return origin is list or origin is List


def extract_list(kind: type) -> type:
    """提取list[T]中的T"""
    assert is_list(kind)
    args = get_args(kind)
    return args[0] if args else type


def extract_list_anyway(kind: type):
    return extract_list(kind) if is_list(kind) else kind


def build_argument(
    name: str,
    kind: type,
    default,
    short: str,
    is_positional: bool,
    help: str,
):
    positional = build_positional(name, is_positional, short)
    named: dict[str, Any] = {"help": help}

    if default is not None:
        named["default"] = default

    if is_optional(kind):
        just_kind = extract_optional(kind)
        assert just_kind is not bool, (
            f"{name} ({kind}): use bool instead of Optional[bool]"
        )

        named["default"] = None
    else:
        just_kind = extract_union_anyway(kind)

    if len(just_kind) > 1:
        assert not any(is_list(x) for x in just_kind), (
            f"{name} ({kind}): list[T] is exclusive with other types"
        )
    else:
        assert len(just_kind) == 1, f"{name} ({kind}): use a type except Never"
        inner_kind = just_kind[0]

        nargs = "*" if "default" in named else "+"
        if is_list(inner_kind):
            inner_kind = extract_list(inner_kind)
            named["nargs"] = nargs
        elif issubclass(inner_kind, enum.Flag):
            named["nargs"] = nargs

        variants = extract_union_anyway(inner_kind)
        if len(variants) > 1:
            assert not any(x is NoneType for x in variants), (
                f"{name} ({kind}) ({variants}): can't parse list[None]"
            )
        else:
            assert len(variants) == 1, (
                f"{name} ({kind}) ({variants}): use a type except Never"
            )

            variant = variants[0]

            if variant is bool:
                named["action"] = "store_true"
                named["default"] = False
            else:
                logger.debug(f"{build_argument.__name__}: variant of {kind}: {variant}")
                if issubclass(variant, enum.IntEnum):
                    named["choices"] = [
                        choice for x in variant for choice in (x.name, str(x.value))
                    ]
                    variant = str
                elif issubclass(variant, enum.Enum):
                    named["choices"] = [x.name for x in variant]
                    variant = str
                elif issubclass(variant, TextIO):
                    variant = argparse.FileType("r+")
                elif issubclass(variant, BinaryIO):
                    variant = argparse.FileType("rb+")
                elif not is_primary(variant):
                    logger.warning(f"unknown kind {variant}, name is {name}")

                named["type"] = variant

    """
        constraint of argparse.ArgumentParser: `TypeError: 'required' is an invalid argument for positionals`

        required/nargs:
                  positional
                    x    o
                x   o/   x/
        default o   x/   x/?
    """
    if "default" in named:
        if not positional[0].startswith("-"):
            named["nargs"] = "?"
    elif positional[0].startswith("-"):
        named["required"] = True
    return positional, named


def create_parser(members: Iterable[Field], exit_on_error: bool):
    parser = argparse.ArgumentParser(exit_on_error=exit_on_error)

    for member in members:
        meta = member.metadata

        if member.default is not MISSING:
            default = member.default
        elif member.default_factory is not MISSING:
            # hack: don't call factory, as it's a list actually
            default = member.default_factory
        else:
            default = None

        positional, named = build_argument(
            member.name,
            cast(type, member.type),
            default,
            meta.get("short", ""),
            meta.get("positional", False),
            meta.get("help", ""),
        )
        logger.debug(f"{create_parser.__name__}: {positional}, {named}")
        parser.add_argument(*positional, **named)
    return parser


def parse(cls: type[T], args: Optional[Sequence[str]] = None, strict=True):
    """strict: 若传入未声明的参数则报错"""

    clz = cast(Any, cls)
    if strict:
        raw = clz.parser.parse_args(args)
    else:
        raw, _ = clz.parser.parse_known_args(args)

    arg_map = vars(raw)

    for member in clz.__dataclass_fields__.values():
        name = member.name
        kinds = normalize_kind(member.type)

        value = arg_map[name]
        if isinstance(value, list):
            parsed = [parse_in_order(kinds, x) for x in value]
            if parsed and isinstance(parsed[0], enum.Flag):
                parsed = functools.reduce(lambda a, b: a | b, parsed, kinds[0][0](0))
        else:
            parsed = parse_in_order(kinds, value)

        arg_map[name] = parsed

    return cls(**arg_map)


def cli(exit_on_error=True):
    """
    arg名称中的"_"会转成CLI参数的"-"
    bool类型arg默认Falsy
    禁用Optional[bool]类型
    其他Optional类型arg默认值为None
    数组默认值禁用`list_arg: list[int] = []`，正确写法为`list_arg: list[int] = arg(default=[])`
    其他类型arg无默认值则必需
    枚举类型arg根据枚举变体的名称解析CLI参数
    """

    def decorator(cls: type[T]):
        clz = cast(Any, cls)
        clz.parser = create_parser(clz.__dataclass_fields__.values(), exit_on_error)
        clz.parse = classmethod(parse)

        return cls

    return decorator


class AutoCli(type):
    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, Any]):
        new_class = super().__new__(cls, name, bases, attrs)
        if bases:
            new_class = cli()(dataclass(new_class))
        return new_class


def parse_in_order(kinds: Iterable[Sequence[type]], value):
    ret = value
    for kind in (x for union in kinds for x in union):
        logger.debug(f"{parse_in_order.__name__}: {kind}, {value}")

        if kind is NoneType:
            assert value is None
            break

        if kind is str:
            break

        if issubclass(kind, enum.Enum):
            if isinstance(value, str):
                if value[0].isdecimal():
                    try:
                        ret = int(value)
                    except ValueError:
                        continue
                else:
                    try:
                        ret = kind.__members__[value]
                    except KeyError:
                        continue
            break

        try:
            ret = kind(value)
        except (TypeError, ValueError):
            pass
        else:
            break
    return ret


def normalize_kind(kind: type):
    """resolve enum and union from value"""

    kinds = extract_union_anyway(kind)

    # handles Optional[list[T]]
    unions = (extract_list_anyway(kind) for kind in kinds)

    # handles list[Union[T, U]]
    return [extract_union_anyway(kind) for kind in unions]


class Parser(metaclass=AutoCli):
    __dataclass_fields__: dict[str, Field]
    parser: argparse.ArgumentParser

    def __init__(self, *_, **__): ...

    @classmethod
    def parse(cls: type[T], args: Optional[Sequence[str]] = None, strict=True) -> T: ...
