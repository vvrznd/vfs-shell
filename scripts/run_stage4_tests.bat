@echo off
chcp 65001 >nul

echo === Stage 4 commands on vfs_multi ===
python -m src.main --vfs-path examples/vfs_multi.csv --script-path scripts/startup_stage4.txt
echo.

echo === Stage 4 commands on vfs_deep ===
python -m src.main --vfs-path examples/vfs_deep.csv --script-path scripts/startup_stage4.txt
echo.

echo === All stage 4 tests done ===