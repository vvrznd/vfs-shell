@echo off
chcp 65001 >nul

echo === Test 1: no arguments ===
echo exit|python -m src.main
echo.

echo === Test 2: only --vfs-path ===
python -m src.main --vfs-path examples/vfs_minimal.csv --script-path scripts/startup_ok.txt
echo.

echo === Test 3: only --script-path ===
python -m src.main --script-path scripts/startup_ok.txt
echo.

echo === Test 4: both arguments ===
python -m src.main --vfs-path examples/vfs_minimal.csv --script-path scripts/startup_ok.txt
echo.

echo === Test 5: script with error ===
python -m src.main --script-path scripts/startup_error.txt
echo.

echo === All tests done ===