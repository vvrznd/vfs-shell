"""Virtual file system backed by a CSV file.

All operations are performed in memory. The CSV source is read
only once at load time; after that the file is never touched.
"""
import base64
import binascii
import csv
import os
from dataclasses import dataclass

DIR_TYPE = "dir"
FILE_TYPE = "file"
ROOT = "/"
REQUIRED_FIELDS = ("path", "type", "content", "owner")


class VfsError(Exception):
    """Base error for VFS problems."""


class VfsNotFound(VfsError):
    """Raised when the CSV file cannot be found."""


class VfsFormatError(VfsError):
    """Raised when the CSV content is malformed."""


@dataclass
class VfsNode:
    """A single file or directory in the VFS.

    Attributes:
        path: Absolute path inside the VFS.
        kind: Either 'dir' or 'file'.
        content: Raw bytes for files, empty for directories.
        owner: Owner name.
    """
    path: str
    kind: str
    content: bytes = b""
    owner: str = ""


class VirtualFileSystem:
    """In-memory virtual file system.

    Attributes:
        name: Human-readable name of this VFS instance.
        nodes: Mapping from absolute path to VfsNode.
    """

    def __init__(self, name: str = "vfs-default") -> None:
        self.name = name
        self.nodes: dict[str, VfsNode] = {}

    def __len__(self) -> int:
        return len(self.nodes)

    def __contains__(self, path: str) -> bool:
        return path in self.nodes

    def add(self, node: VfsNode) -> None:
        """Insert or replace a node."""
        self.nodes[node.path] = node

    def get(self, path: str) -> VfsNode:
        """Return the node at path, raising VfsError if absent."""
        node = self.nodes.get(path)
        if node is None:
            raise VfsError(f"no such path: {path}")
        return node

    def is_dir(self, path: str) -> bool:
        """Return True if path points to a directory."""
        node = self.nodes.get(path)
        return node is not None and node.kind == DIR_TYPE

    def is_file(self, path: str) -> bool:
        """Return True if path points to a file."""
        node = self.nodes.get(path)
        return node is not None and node.kind == FILE_TYPE

    def list_dir(self, path: str) -> list[str]:
        """Return sorted names of the direct children of a dir."""
        if not self.is_dir(path):
            raise VfsError(f"not a directory: {path}")
        prefix = path.rstrip("/") + "/"
        result: list[str] = []
        for node_path in self.nodes:
            if not node_path.startswith(prefix):
                continue
            rest = node_path[len(prefix):]
            if not rest or "/" in rest:
                continue
            result.append(rest)
        return sorted(result)

    def resolve(self, cwd: str, target: str) -> str:
        """Resolve a possibly-relative path against cwd.

        Handles '.', '..', and absolute paths.
        """
        if not target:
            target = "."
        if target.startswith("/"):
            base = target
        else:
            base = cwd.rstrip("/") + "/" + target
        parts: list[str] = []
        for chunk in base.split("/"):
            if chunk in ("", "."):
                continue
            if chunk == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(chunk)
        return "/" + "/".join(parts)

    def read_file(self, path: str) -> bytes:
        """Return raw content of a file node."""
        node = self.get(path)
        if node.kind != FILE_TYPE:
            raise VfsError(f"not a file: {path}")
        return node.content


def create_default_vfs(name: str = "vfs-default") -> VirtualFileSystem:
    """Create an empty VFS containing only the root directory."""
    vfs = VirtualFileSystem(name=name)
    vfs.add(VfsNode(path=ROOT, kind=DIR_TYPE, owner="root"))
    return vfs


def load_from_csv(path: str, name: str | None = None) -> VirtualFileSystem:
    """Load a VFS from a CSV file into memory.

    Args:
        path: Path to the CSV source file.
        name: Optional VFS name. If None, derived from file name.

    Returns:
        A fully loaded VirtualFileSystem.

    Raises:
        VfsNotFound: If the file does not exist.
        VfsFormatError: If the CSV structure or content is bad.
    """
    if not os.path.isfile(path):
        raise VfsNotFound(f"file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, csv.Error) as exc:
        raise VfsFormatError(f"cannot read CSV: {exc}") from exc

    if name is None:
        name = _guess_name(path)
    vfs = create_default_vfs(name=name)
    for index, row in enumerate(rows, start=2):
        _add_row(vfs, row, index)
    return vfs


def _guess_name(path: str) -> str:
    """Derive a VFS name from a CSV file path."""
    base = os.path.basename(path)
    stem, _ = os.path.splitext(base)
    return stem or "vfs"


def _add_row(
    vfs: VirtualFileSystem, row: dict[str, str], index: int
) -> None:
    """Validate a CSV row and add it to the VFS."""
    for field_name in REQUIRED_FIELDS:
        if field_name not in row:
            raise VfsFormatError(
                f"row {index}: missing field '{field_name}'"
            )
    path = (row["path"] or "").strip()
    if not path.startswith("/"):
        raise VfsFormatError(
            f"row {index}: path must start with '/': {path!r}"
        )
    kind = (row["type"] or "").strip()
    if kind not in (DIR_TYPE, FILE_TYPE):
        raise VfsFormatError(f"row {index}: bad type: {kind!r}")
    owner = (row["owner"] or "").strip()
    if kind == DIR_TYPE:
        content = b""
    else:
        content = _decode_content(row["content"], index)
    vfs.add(VfsNode(path=path, kind=kind, content=content, owner=owner))


def _decode_content(raw: str | None, index: int) -> bytes:
    """Decode a base64 cell into bytes."""
    if raw is None:
        raw = ""
    raw = raw.strip()
    if not raw:
        return b""
    try:
        return base64.b64decode(raw, validate=True)
    except binascii.Error as exc:
        raise VfsFormatError(
            f"row {index}: invalid base64: {exc}"
        ) from exc