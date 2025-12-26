@echo off
chcp 65001 >nul
echo ========================================
echo 明星照片爬虫 - 快速启动
echo ========================================
echo.

REM 检查是否安装了 uv
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 uv，请先安装 uv
    pause
    exit /b 1
)

echo [信息] 使用 uv 运行爬虫...
echo.

REM 使用 uv run 运行爬虫（自动管理环境）
uv run python star_photo_crawler_keyword.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 运行失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo 运行完成！
echo ========================================
pause

