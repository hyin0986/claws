from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class LeafNode:
    name: str = ""
    path: str = ""
    description: str = ""
    type: str = ""
    mode: str = ""
    units: str | None = None
    precision: int | None = None


@dataclass(slots=True, frozen=True)
class ArrayLeafNode(LeafNode):
    size: int = 0


@dataclass(slots=True, frozen=True)
class EnumLeafNode(LeafNode):
    enum_labels: list[str] = field(default_factory=list)
