from itertools import permutations
from typing import Set, Iterable, Tuple, Type

from .base import BaseType


class StringSerializable(BaseType):
    @classmethod
    def to_internal_value(cls, value: str) -> 'StringSerializable':
        raise NotImplementedError()

    def to_representation(self) -> str:
        raise NotImplementedError()

T_StringSerializable = Type[StringSerializable]

class StringSerializableRegistry:
    @classmethod
    def default(cls):
        pass

    def __init__(self, *types: T_StringSerializable):
        self.types: Set[T_StringSerializable] = set(types)
        self.replaces: Set[Tuple[T_StringSerializable, T_StringSerializable]] = set()

    def add(self, replace_types: Iterable[T_StringSerializable] = (), cls: type = None):
        def decorator(cls):
            self.types.add(cls)
            for t in replace_types:
                self.replaces.add((t, cls))
            return cls

        if cls:
            decorator(cls)
            return

        return decorator

    def resolve(self, *types: T_StringSerializable) -> Iterable[T_StringSerializable]:
        types = set(types)
        flag = True
        while flag:
            flag = False
            filtered: Set[T_StringSerializable] = set()
            for t1, t2 in permutations(types, 2):
                if (t1, t2) in self.replaces:
                    filtered.add(t2)
                    flag = True
            if flag:
                types = filtered
        # noinspection PyUnboundLocalVariable
        return types


registry = StringSerializableRegistry()


@registry.add()
class IntString(StringSerializable, int):
    @classmethod
    def to_internal_value(cls, value: str) -> 'IntString':
        return cls(value)

    def to_representation(self) -> str:
        raise str(self)


@registry.add(replace_types=(IntString,))
class FloatString(StringSerializable, float):
    @classmethod
    def to_internal_value(cls, value: str) -> 'FloatString':
        return cls(value)

    def to_representation(self) -> str:
        raise str(self)


@registry.add()
class BooleanString(StringSerializable, int):
    # We can't extend bool class, but we can extend int with same result excepting isinstance and issubclass check

    @classmethod
    def to_internal_value(cls, value: str) -> 'BooleanString':
        b = {"true": True, "false": False}.get(value.lower(), None)
        if b is None:
            raise ValueError(f"invalid literal for bool: '{value}'")
        return cls(b)

    def to_representation(self) -> str:
        raise str(bool(self)).lower()