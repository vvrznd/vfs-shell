"""Tests for the virtual file system."""
import pytest

from src.vfs import (
    DIR_TYPE,
    FILE_TYPE,
    ROOT,
    VfsError,
    VfsFormatError,
    VfsNotFoundError,
    VfsNode,
    VirtualFileSystem,
    create_default_vfs,
    load_from_csv,
)


def _make_vfs() -> VirtualFileSystem:
    """Build a small VFS for tests."""
    vfs = create_default_vfs()
    vfs.add(VfsNode(path="/home", kind=DIR_TYPE, owner="root"))
    vfs.add(VfsNode(path="/home/user", kind=DIR_TYPE, owner="user"))
    vfs.add(VfsNode(
        path="/home/user/readme.txt",
        kind=FILE_TYPE,
        content=b"Hello",
        owner="user",
    ))
    return vfs


def test_create_default_vfs_has_root_only() -> None:
    """A fresh default VFS contains only the root directory."""
    vfs = create_default_vfs()
    assert len(vfs) == 1
    assert ROOT in vfs
    assert vfs.is_dir(ROOT)


def test_resolve_absolute_path() -> None:
    """Absolute paths are returned normalized."""
    vfs = _make_vfs()
    assert vfs.resolve("/", "/home/user") == "/home/user"


def test_resolve_relative_path() -> None:
    """Relative paths are resolved against cwd."""
    vfs = _make_vfs()
    assert vfs.resolve("/home", "user") == "/home/user"


def test_resolve_dotdot() -> None:
    """Parent-directory marker climbs up the tree."""
    vfs = _make_vfs()
    assert vfs.resolve("/home/user", "..") == "/home"


def test_resolve_dot_and_dotdot_combined() -> None:
    """Complex paths are collapsed to a canonical form."""
    vfs = _make_vfs()
    assert vfs.resolve("/home/user", "../user/.") == "/home/user"


def test_list_dir_returns_sorted_children() -> None:
    """Children are listed sorted, no deep descendants."""
    vfs = _make_vfs()
    assert vfs.list_dir("/home/user") == ["readme.txt"]


def test_list_dir_on_file_raises() -> None:
    """Listing a file is an error."""
    vfs = _make_vfs()
    with pytest.raises(VfsError):
        vfs.list_dir("/home/user/readme.txt")


def test_read_file_returns_content() -> None:
    """read_file returns the raw bytes of a file."""
    vfs = _make_vfs()
    assert vfs.read_file("/home/user/readme.txt") == b"Hello"


def test_read_file_on_dir_raises() -> None:
    """Reading a directory is an error."""
    vfs = _make_vfs()
    with pytest.raises(VfsError):
        vfs.read_file("/home")


def test_has_children_on_empty_dir() -> None:
    """An empty dir reports no children."""
    vfs = create_default_vfs()
    vfs.add(VfsNode(path="/empty", kind=DIR_TYPE, owner="root"))
    assert not vfs.has_children("/empty")


def test_has_children_on_non_empty_dir() -> None:
    """A dir with contents reports children."""
    vfs = _make_vfs()
    assert vfs.has_children("/home")


def test_remove_removes_node() -> None:
    """Removing an existing node deletes it."""
    vfs = _make_vfs()
    vfs.remove("/home/user/readme.txt")
    assert "/home/user/readme.txt" not in vfs


def test_remove_missing_raises() -> None:
    """Removing a missing path is an error."""
    vfs = _make_vfs()
    with pytest.raises(VfsError):
        vfs.remove("/no/such/file")


def test_load_from_csv_minimal(tmp_path) -> None:
    """A minimal CSV loads successfully."""
    csv_file = tmp_path / "min.csv"
    csv_file.write_text(
        "path,type,content,owner\n"
        "/,dir,,root\n"
        "/a.txt,file,SGVsbG8=,user\n",
        encoding="utf-8",
    )
    vfs = load_from_csv(str(csv_file))
    assert "/a.txt" in vfs
    assert vfs.read_file("/a.txt") == b"Hello"


def test_load_from_csv_not_found() -> None:
    """A missing file raises VfsNotFoundError."""
    with pytest.raises(VfsNotFoundError):
        load_from_csv("this/does/not/exist.csv")


def test_load_from_csv_bad_base64(tmp_path) -> None:
    """Invalid base64 in content raises VfsFormatError."""
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(
        "path,type,content,owner\n"
        "/,dir,,root\n"
        "/x.txt,file,!!!,user\n",
        encoding="utf-8",
    )
    with pytest.raises(VfsFormatError):
        load_from_csv(str(csv_file))


def test_load_from_csv_relative_path(tmp_path) -> None:
    """A path that does not start with / is rejected."""
    csv_file = tmp_path / "rel.csv"
    csv_file.write_text(
        "path,type,content,owner\n"
        "/,dir,,root\n"
        "nope,dir,,root\n",
        encoding="utf-8",
    )
    with pytest.raises(VfsFormatError):
        load_from_csv(str(csv_file))