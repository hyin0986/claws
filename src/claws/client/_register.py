import pickle
from dataclasses import dataclass
from enum import IntFlag, StrEnum, unique

from ._unpacker import UnpackProtocol


@unique
class Access(IntFlag):
    RO = 1
    WO = 2
    RW = RO | WO


@unique
class Attr(StrEnum):
    GET = "get"
    SET = "set"


@dataclass(slots=True, frozen=True)
class Register[ValueType]:
    access: Access
    path: str
    unpacker: UnpackProtocol[ValueType]
    """Converts the value"""

    def generate_get_request(self, attr: Attr = Attr.GET) -> bytes:
        assert Access.RO in self.access, (
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
        assert Access.WO in self.access, "Register does not write permission!"

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
