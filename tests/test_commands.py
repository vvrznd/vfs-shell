"""Tests for shell commands."""
import pytest

from src.commands import (
    CommandError,
    ExitShellError,
    cmd_cal,
    cmd_cd,
    cmd_ls,
    cmd_rev,
    cmd_rm,
    cmd_rmdir,
    cmd_tac,
    dispatch,
)
from src.context import ShellContext
from src.vfs import DIR_TYPE, FILE_TYPE, VfsNode, create_default_vfs


def _ctx() -> ShellContext:
    """Build a context with a small VFS for tests."""
    vfs = create_default_vfs()
    vfs.add(VfsNode(path="/home", kind=DIR_TYPE, owner="root"))
    vfs.add(VfsNode(path="/home/user", kind=DIR_TYPE, owner="user"))
    vfs.add(VfsNode(
        path="/home/user/readme.txt",
        kind=FILE_TYPE,
        content=b"Hello\nWorld",
        owner="user",
    ))
    vfs.add(VfsNode(path="/empty", kind=DIR_TYPE, owner="root"))
    return ShellContext(vfs=vfs, cwd="/")


def test_ls_lists_root(capsys) -> None:
    """Ls on the root prints its direct children."""
    cmd_ls(_ctx(), [])
    out = capsys.readouterr().out
    assert "home" in out
    assert "empty" in out


def test_ls_long_format_shows_owner(capsys) -> None:
    """Ls -l includes owner info."""
    ctx = _ctx()
    ctx.cwd = "/home/user"
    cmd_ls(ctx, ["-l"])
    out = capsys.readouterr().out
    assert "user" in out
    assert "readme.txt" in out


def test_ls_on_file_raises() -> None:
    """Ls on a file is an error."""
    ctx = _ctx()
    with pytest.raises(CommandError):
        cmd_ls(ctx, ["/home/user/readme.txt"])


def test_cd_changes_cwd() -> None:
    """Cd updates the current working directory."""
    ctx = _ctx()
    cmd_cd(ctx, ["/home/user"])
    assert ctx.cwd == "/home/user"


def test_cd_too_many_args_raises() -> None:
    """Cd with two args is an error."""
    with pytest.raises(CommandError):
        cmd_cd(_ctx(), ["a", "b"])


def test_cd_into_file_raises() -> None:
    """Cd into a file is an error."""
    with pytest.raises(CommandError):
        cmd_cd(_ctx(), ["/home/user/readme.txt"])


def test_cd_without_args_goes_home() -> None:
    """Cd with no argument goes to /home/user when present."""
    ctx = _ctx()
    cmd_cd(ctx, [])
    assert ctx.cwd == "/home/user"


def test_tac_reverses_lines(capsys) -> None:
    """Tac prints file content with lines reversed."""
    ctx = _ctx()
    cmd_tac(ctx, ["/home/user/readme.txt"])
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["World", "Hello"]


def test_tac_missing_file_raises() -> None:
    """Tac on a missing file is an error."""
    with pytest.raises(CommandError):
        cmd_tac(_ctx(), ["/nope.txt"])


def test_rev_reverses_each_line(capsys) -> None:
    """Rev reverses characters of each line."""
    ctx = _ctx()
    cmd_rev(ctx, ["/home/user/readme.txt"])
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["olleH", "dlroW"]


def test_rev_without_args_uses_last_input(capsys) -> None:
    """Rev with no args reverses the last input line."""
    ctx = _ctx()
    ctx.last_input = "abc"
    cmd_rev(ctx, [])
    out = capsys.readouterr().out
    assert out.strip() == "cba"


def test_cal_prints_month(capsys) -> None:
    """Cal prints a calendar with at least the current year."""
    cmd_cal(_ctx(), [])
    out = capsys.readouterr().out
    assert "Mo Tu We Th Fr Sa Su" in out


def test_cal_with_args_raises() -> None:
    """Cal with arguments is an error."""
    with pytest.raises(CommandError):
        cmd_cal(_ctx(), ["x"])


def test_rm_removes_file() -> None:
    """Rm deletes a file from the VFS."""
    ctx = _ctx()
    cmd_rm(ctx, ["/home/user/readme.txt"])
    assert "/home/user/readme.txt" not in ctx.vfs


def test_rm_on_dir_raises() -> None:
    """Rm on a directory is an error."""
    with pytest.raises(CommandError):
        cmd_rm(_ctx(), ["/home"])


def test_rmdir_removes_empty_dir() -> None:
    """Rmdir deletes an empty directory."""
    ctx = _ctx()
    cmd_rmdir(ctx, ["/empty"])
    assert "/empty" not in ctx.vfs


def test_rmdir_on_non_empty_raises() -> None:
    """Rmdir on a non-empty directory is an error."""
    with pytest.raises(CommandError):
        cmd_rmdir(_ctx(), ["/home"])


def test_rmdir_on_root_raises() -> None:
    """Rmdir on the root path is not allowed."""
    with pytest.raises(CommandError):
        cmd_rmdir(_ctx(), ["/"])


def test_dispatch_exit_raises_exit_shell() -> None:
    """The exit command signals shell termination."""
    with pytest.raises(ExitShellError):
        dispatch(_ctx(), ["exit"])


def test_dispatch_unknown_command_raises() -> None:
    """An unknown command raises CommandError."""
    with pytest.raises(CommandError):
        dispatch(_ctx(), ["blabla"])