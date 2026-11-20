import base64
import copy
import lzma
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from io import BytesIO
from pathlib import Path
from types import TracebackType
from typing import Any, Final, Self

import numpy as np
import numpy.typing as npt
import yaml

from claws.errors import YAMLError

from ._pr_node import LeafNode, ArrayLeafNode, EnumLeafNode

LZMA_FORMAT: Final[int] = lzma.FORMAT_XZ
_CRC_CHECK: Final[int] = lzma.CHECK_CRC64
_PRESET: Final[int] = 2
_TYPE_TAG_PREFIX: Final[str] = "!claws"


def _type_tag_generator(cls: type):
    """Generates a custom type tag in the yaml file.

    The type tag consist of:

    .. code::

        "!diamond.[type name of cls]"

    Parameters
    ----------
    cls : Type
        type to be dumped

    Returns
    -------
    str
        diamond specific type tag.
    """
    return f"{_TYPE_TAG_PREFIX}.{cls.__name__}"


def _represent_numpy_array(
    dumper: "CLAWSCSafeDumper", data: npt.NDArray
) -> yaml.MappingNode:
    """Represents numpy NDArray as yaml entry.

    - shape: matrix dimension
    - dtype: how to binary format, ie small endian, primitive type and word size
    - data: data in base64

    Parameters
    ----------
    dumper : Dumper
        yaml dumper interface/handle
    data : npt.NDArray
        data to be dumped.

    Returns
    -------
    yaml.MappingNode
        the representation in abstract yaml DOM.
    """
    binary_data = base64.b64encode(data.tobytes()).decode("ascii")
    metadata = {
        "shape": ",".join(map(str, data.shape)),
        "dtype": data.dtype.str,
        "data": binary_data,
    }
    return dumper.represent_mapping(_type_tag_generator(type(data)), metadata)


def _construct_numpy_array(
    loader: "CLAWSCSafeLoader", node: yaml.MappingNode
) -> npt.NDArray:
    """Defines how the numpy array is constructed from a yaml entry.

    Parameters
    ----------
    loader : Loader
        yaml loader interface/handle
    node : yaml.MappingNode
        the representation in abstract yaml DOM, containing numpy array.

    Returns
    -------
    npt.NDArray
        reconstructed numpy array
    """
    metadata = loader.construct_mapping(node)
    shape = [int(elem) for elem in metadata["shape"].split(",")]
    dtype = np.dtype(metadata["dtype"])
    binary_data: bytes = base64.b64decode(metadata["data"])
    return np.frombuffer(binary_data, dtype=dtype).reshape(shape)


def _represent_dataclass(
    dumper: "CLAWSCSafeDumper", data: Any
) -> yaml.MappingNode:
    """Defines how to dump a dataclass object.

    Parameters
    ----------
    dumper : Dumper
        yaml dumper interface/handle
    data : Any
        Must be an instance of dataclass!

    Returns
    -------
    yaml.MappingNode
        the representation in abstract yaml DOM.
    """
    assert is_dataclass(data)
    field_dict = {
        field.name: getattr(data, field.name) for field in fields(data)
    }
    return dumper.represent_mapping(
        _type_tag_generator(type(data)), field_dict
    )


def _construct_dataclass(
    cls: type,
) -> Callable[["CLAWSCSafeLoader", yaml.MappingNode], Any]:
    """Returns a function that dumps reconstructs the dataclass from yaml.

    Parameters
    ----------
    cls : Type
        Type to be reconstructed.

    Returns
    -------
    Callable[[Loader, yaml.MappingNode], Any]
        function constructing the given cls based on the yaml entry.
    """
    assert is_dataclass(cls)

    def constructor(loader: "CLAWSCSafeLoader", node: yaml.MappingNode) -> Any:
        data = loader.construct_mapping(node)
        for field in fields(cls):
            data[field.name] = data.get(field.name)
        return cls(**data)  # type: ignore

    return constructor


REPRESENTER_MAP: Final[
    dict[type, Callable[["CLAWSCSafeDumper", Any], yaml.MappingNode]]
] = {
    np.ndarray: _represent_numpy_array,
    LeafNode: _represent_dataclass,
    ArrayLeafNode: _represent_dataclass,
    EnumLeafNode: _represent_dataclass,
}
"""Mapping custom yaml representation based on the type."""

CONSTRUCTOR_MAP: Final[
    dict[type, Callable[["CLAWSCSafeLoader", yaml.MappingNode], Any]]
] = {
    np.ndarray: _construct_numpy_array,
    LeafNode: _construct_dataclass(LeafNode),
    ArrayLeafNode: _construct_dataclass(ArrayLeafNode),
    EnumLeafNode: _construct_dataclass(EnumLeafNode),
}
"""Mapping custom yaml construction based on the given type."""


def _register_representer(dumper: type["CLAWSCSafeDumper"]):
    """helper function to register the dumpers"""
    for data_type, rep in REPRESENTER_MAP.items():
        dumper.add_representer(data_type, rep)


def _register_constructor(loader: type["CLAWSCSafeLoader"]):
    """helper function to construct diamond types from yaml"""
    for data_type, constructor in CONSTRUCTOR_MAP.items():
        loader.add_constructor(_type_tag_generator(data_type), constructor)


class CLAWSCSafeLoader(yaml.CSafeLoader):
    yaml_constructors = copy.deepcopy(yaml.CSafeLoader.yaml_constructors)


_register_constructor(CLAWSCSafeLoader)


class CLAWSCSafeDumper(yaml.CSafeDumper):
    yaml_representers = copy.deepcopy(yaml.CSafeDumper.yaml_representers)


_register_representer(CLAWSCSafeDumper)


# def _is_writeable_file(file: Path) -> bool:
#     """Checks if a given file path is writeable."""
#     open(file, "wb")
#     assert file.is_file()

#     tmp_file = Path(file.parent.absolute()) / ".diamond_framework_temp_file"
#     try:
#         with open(tmp_file, "wb") as _:
#             pass
#         tmp_file.unlink()  # delete created test tmp file
#         return True
#     except OSError:
#         return False


class YAMLFile:
    """Dumps the ``BeamDump`` and ``Results`` in a compressed yaml file.

    .. note::
        The compress argument should alway be set to True. Only during
        debugging it set to False to provide a human readable file.

    Parameters
    ----------
    file : Path
        output file path
    compress : bool, optional
        if the output should be compressed, by default True.

    Raises
    ------
    OutputError
        If the given file path can not be written to.
    """

    _compress: bool = True
    """If the output should be compressed, default True."""

    _io: BytesIO | None = None
    """Internal buffer"""

    _output_stream: Path
    """output file path"""

    def __init__(self, stream: BytesIO, compress: bool = True):
        self._compress = compress
        self._output_stream = stream

        # register the data class etc here but in a helper function

    def __enter__(self) -> Self:
        self.open()
        return self

    def __exit__(
        self,
        _type: type[BaseException] | None,
        _instance: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()

    def open(self) -> None:
        """Only opens the internal buffer.

        The actual file operation is done at close().
        """
        self._io = BytesIO()

    def close(self) -> None:
        """Dumpes the internal buffer to file.

        Raises
        ------
        OutputError
            If the dump generates a file error.
        """
        if self._io is None:
            return

        try:
            self._output_stream.write(self._io.getvalue())
        except OSError as err:
            raise YAMLError("Failed to save data to YAML file!") from err
        finally:
            self._io.close()

    def write(self, nodes: list[LeafNode]) -> None:
        """Dumps the given result and beam dump as yam into a internal buffer.

        Raises
        ------
        OutputError
            If there is a compression error.
        """
        assert self._io is not None, (
            "Using YAMLFile.write() before YAMLFile.open()!"
        )

        try:
            payload = yaml.dump(
                nodes,
                Dumper=CLAWSCSafeDumper,
            ).encode("utf-8")
        except yaml.YAMLError as err:
            raise YAMLError(
                "Failed to convert the given data to yaml!"
            ) from err

        if self._compress:
            try:
                payload = lzma.compress(
                    payload,
                    format=LZMA_FORMAT,
                    check=_CRC_CHECK,
                    preset=_PRESET,
                )
            except lzma.LZMAError as err:
                raise YAMLError("Failed to compress yaml content!") from err
        self._io.write(payload)
