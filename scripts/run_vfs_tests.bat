@echo off
chcp 65001 >nul

echo === VFS minimal ===
python -m src.main --vfs-path examples/vfs_minimal.csv --script-path scripts/startup_ok.txt
echo.

echo === VFS multi ===
python -m src.main --vfs-path examples/vfs_multi.csv --script-path scripts/startup_ok.txt
echo.

echo === VFS deep ===
python -m src.main --vfs-path examples/vfs_deep.csv --script-path scripts/startup_ok.txt
echo.

echo === VFS not found ===
python -m src.main --vfs-path examples/nonexistent.csv --script-path scripts/startup_ok.txt
echo.

echo === VFS broken base64 ===
python -m src.main --vfs-path examples/broken.csv --script-path scripts/startup_ok.txt
echo.

echo === All VFS tests done ===