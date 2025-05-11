@echo off
:: FastAPI サーバーの停止
echo 停止中... FastAPI サーバーを探して停止します。

:: uvicorn プロセスを探して強制終了
tasklist | findstr uvicorn > nul
if %errorlevel% equ 0 (
    echo uvicorn プロセスが見つかりました。停止します...
    taskkill /F /IM python.exe
) else (
    echo uvicorn プロセスは見つかりませんでした。
)

:: FastAPI サーバーの起動
echo FastAPI サーバーを起動します...
start cmd /k "uvicorn backend.main:app --reload"

pause
