import base64
import logging
import threading
from dataclasses import asdict
from io import BytesIO
from typing import Self, TypedDict

import zmq
from pyrogue import BaseVariable as RogueVariable
from pyrogue import Node as RogueNode

from claws.data._pr_node import ArrayLeafNode, EnumLeafNode, LeafNode
from claws.data._yaml_serialization import YAMLFile
from claws.errors import CLAWSBaseError, DiscoveryServerError, YAMLError

_LOG = logging.getLogger(__name__)


def _parse_array_size_from_type(type_str: str) -> int:
    try:
        return int(type_str.split("(")[-1].strip(")").strip(","))
    except (ValueError, TypeError) as err:
        raise CLAWSBaseError(
            f"Failed to extract size from array variable, got: {type_str}"
        ) from err


def _construct_node(
    var: RogueVariable,
) -> LeafNode | ArrayLeafNode | EnumLeafNode:
    node = LeafNode(
        name=var.name,
        path=var.path,
        description=var.description,
        type=var.typeStr,
        mode=var.mode,
    )
    if var.enum is not None:
        return EnumLeafNode(
            **asdict(node),
            enum_labels=[
                value
                for value in var.enum.values()
                if value not in ["ParentFalse", "ExtDepFalse"]
            ],
        )
    if var.ndType is not None:
        return ArrayLeafNode(
            **asdict(node), size=_parse_array_size_from_type(var.typeStr)
        )
    return node


class Nodes(TypedDict):
    variables: list[LeafNode]
    enums: list[EnumLeafNode]
    arrays: list[ArrayLeafNode]


def discover_device_tree(
    root: RogueNode,
) -> Nodes:
    """Serialize a PyRogue node into a JSON-compatible dictionary."""
    variables = root.variableList
    vars = (
        var for var in variables if var.enum is None and var.ndType is None
    )
    enum_vars = (var for var in variables if var.enum is not None)
    array_vars = (var for var in variables if var.ndType is not None)
    return Nodes(
        variables=[_construct_node(item) for item in vars],
        enums=[_construct_node(item) for item in enum_vars],
        arrays=[_construct_node(item) for item in array_vars],
    )


class DiscoveryServer:
    """ZeroMQ JSON request/reply device discovery server."""

    def __init__(self, root: RogueNode, host: str, port: int):
        self._nodes = discover_device_tree(root)
        self._host = host
        self._port = port

    def run(
        self,
        context: zmq.Context,
        stop_event: threading.Event,
    ) -> None:
        """Run the discovery server."""

        socket = context.socket(zmq.REP)
        socket.setsockopt(zmq.LINGER, 0)
        socket.setsockopt(zmq.RCVTIMEO, 250)
        socket.bind(f"tcp://{self._host}:{self._port}")

        try:
            while not stop_event.is_set():
                try:
                    request = socket.recv_json()
                except zmq.Again:
                    continue

                response = self.handle_request(request)
                socket.send_json(response)

        finally:
            socket.close()

    def _serialize_nodes(self) -> bytes:
        byte_io = BytesIO()

        with YAMLFile(byte_io) as stream:
            stream.write(self._nodes)

        return base64.b64encode(byte_io.getvalue())

    def handle_request(self, request: dict) -> dict:
        command = request.get("cmd")

        if command == "get_device_tree":
            try:
                return {
                    "status": "ok",
                    "nodes": self._serialize_nodes().decode("ascii"),
                }
            except YAMLError:
                _LOG.exception("Failed to serialize nodes to YAML.")
                return {
                    "status": "error",
                    "message": "Failed to serialize nodes to YAML.",
                }

        return {
            "status": "error",
            "message": f"Unknown command: {command}",
        }


class DiscoveryServerContext:
    """Context manager running DiscoveryServer in a background thread."""

    def __init__(
        self,
        server: DiscoveryServer,
        name: str = "discovery-server",
        daemon: bool = True,
    ):
        self._server = server
        self._name = name
        self._daemon = daemon

        self._context: zmq.Context | None = None
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        self._exception: BaseException | None = None

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback_obj):
        self.stop()

    def start(self) -> None:
        """Create the context and start the server thread."""

        if self._thread is not None and self._thread.is_alive():
            raise DiscoveryServerError("Discovery server is already running")

        self._stop_event.clear()
        self._exception = None

        self._context = zmq.Context()

        self._thread = threading.Thread(
            target=self._run,
            name=self._name,
            daemon=self._daemon,
        )

        self._thread.start()

    def _run(self) -> None:
        """Thread entry point."""

        try:
            self._server.run(
                self._context,
                self._stop_event,
            )
        except zmq.ZMQError as exc:
            raise DiscoveryServerError("Run Breaking Error.") from exc

    def stop(self) -> None:
        """Stop the server and release resources."""

        self._stop_event.set()

        if self._thread is not None:
            self._thread.join()

        if self._context is not None:
            self._context.term()
            self._context = None

        self._thread = None

        if self._exception is not None:
            exc = self._exception
            self._exception = None
            raise RuntimeError(
                "Discovery server terminated unexpectedly"
            ) from exc

    @property
    def is_running(self) -> bool:
        """Return whether the server thread is running."""
        return self._thread is not None and self._thread.is_alive()
