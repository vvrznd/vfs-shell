@echo off
chcp 65001 >nul

echo === Stage 5: rm and rmdir (vfs_multi) ===
python -m src.main --vfs-path examples/vfs_multi.csv --script-path scripts/startup_stage5.txt
echo.

echo === Stage 5: rmdir non-empty should fail ===
python -m src.main --vfs-path examples/vfs_multi.csv --script-path scripts/startup_stage5_fail.txt
echo.

echo === All stage 5 tests done ===