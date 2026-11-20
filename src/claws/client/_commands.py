import pickle
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntFlag, StrEnum, unique


@unique
class Access(IntFlag):
    READ = 1
    WRITE = 2
    READ_WRITE = READ | WRITE


@unique
class Attr(StrEnum):
    GET = "get"
    SET = "set"


@dataclass(slots=True, frozen=True)
class Register[ValueType]:
    access: Access
    path: str
    to_value: Callable[[str | bytes | ValueType], ValueType]
    """Converts the value"""

    def generate_get_request(self, attr: Attr = Attr.GET) -> bytes:
        assert Access.READ in self.permission, (
            "Register does not have read permission!"
        )

        return pickle.dumps(
            {
                "path": self.path,
                "attr": attr.value,
                "args": (),
                "kwargs": {},
            }
        )

    def generate_set_request(
        self, value: ValueType, attr: Attr = Attr.SET
    ) -> bytes:
        assert Access.WRITE in self.permission, (
            "Register does not write permission!"
        )

        return pickle.dumps(
            {
                "path": self.path,
                "attr": attr.value,
                "args": (value,),
                "kwargs": {},
            }
        )

    # def unpack_get_request(raw: bytes) -> ValueType:
    #     python.
