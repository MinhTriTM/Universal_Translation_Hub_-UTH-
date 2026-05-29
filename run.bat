@echo off
chcp 65001 >nul 2>&1
title Universal Translation Hub (UTH) v0.2.0
cd /d "%~dp0"
set "PROVIDER=local"

:MENU
cls
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║         Universal Translation Hub (UTH) v0.2.0         ║
echo  ║         Powered by MiMo V2.5 + Local AI                ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo   --- WEB GUI ---
echo.
echo   [0] 🌐  Mở Web GUI (localhost:8000)
echo.
echo   --- CHỌN PIPELINE ---
echo.
echo   [1] 🎮  Dịch Game (AG-Translator backend)
echo   [2] 📖  Dịch Manga/Comic (OCR + Translate + Render)
echo   [3] 🎬  Dịch Film + Thuyết Minh (Subtitle + TTS)
echo   [4] 🔍  Auto-detect (tự nhận diện loại nội dung)
echo.
echo   --- KHÁC ---
echo.
echo   [5] 🎪  Demo mode (không cần backend)
echo   [6] ⚙️   Chọn Provider (Local / MiMo / Auto)
echo   [7] 📊  Kiểm tra trạng thái Backend
echo   [8] 📖  Mở tài liệu (docs)
echo   [9] ❌  Thoát
echo.
echo  ══════════════════════════════════════════════════════════

set "CHOICE="
set /p "CHOICE=  Nhập chọn [1-9]: "

if "%CHOICE%"=="0" goto WEBGUI
if "%CHOICE%"=="1" goto GAME
if "%CHOICE%"=="2" goto MANGA
if "%CHOICE%"=="3" goto FILM
if "%CHOICE%"=="4" goto AUTO
if "%CHOICE%"=="5" goto DEMO
if "%CHOICE%"=="6" goto PROVIDER
if "%CHOICE%"=="7" goto STATUS
if "%CHOICE%"=="8" goto DOCS
if "%CHOICE%"=="9" goto EXIT

echo   ⚠️  Lựa chọn không hợp lệ!
timeout /t 2 >nul
goto MENU

:: ==========================================
:: WEB GUI
:: ==========================================
:WEBGUI
cls
echo.
echo  ═══ WEB GUI ═══
echo.
echo   Server đang khởi động tại http://localhost:8000
echo   Trình duyệt sẽ tự động mở...
echo.
start http://localhost:8000
python server.py
pause
goto MENU

:: ==========================================
:: GAME PIPELINE
:: ==========================================
:GAME
cls
echo.
echo  ═══ GAME PIPELINE ═══
echo.
echo   Nhập đường dẫn thư mục game:
echo   (Ví dụ: E:\Games\MyGame)
echo.
set "GAME_PATH="
set /p "GAME_PATH=  Path: "

if "%GAME_PATH%"=="" (
    echo   ⚠️  Chưa nhập đường dẫn!
    timeout /t 2 >nul
    goto GAME
)

echo.
echo   Chọn engine (Enter = auto-detect):
echo   [1] Auto    [2] rpgmz    [3] kirikiri    [4] renpy
echo   [5] unity   [6] catsys2  [7] nscripter   [8] tyrano
echo.
set "ENGINE_CHOICE="
set /p "ENGINE_CHOICE=  Engine [1-8, Enter=auto]: "

set "ENGINE_ARG="
if "%ENGINE_CHOICE%"=="2" set "ENGINE_ARG=--engine rpgmz"
if "%ENGINE_CHOICE%"=="3" set "ENGINE_ARG=--engine kirikiri"
if "%ENGINE_CHOICE%"=="4" set "ENGINE_ARG=--engine renpy"
if "%ENGINE_CHOICE%"=="5" set "ENGINE_ARG=--engine unity"
if "%ENGINE_CHOICE%"=="6" set "ENGINE_ARG=--engine catsys2"
if "%ENGINE_CHOICE%"=="7" set "ENGINE_ARG=--engine nscripter"
if "%ENGINE_CHOICE%"=="8" set "ENGINE_ARG=--engine tyrano"

echo.
echo   🚀 Đang chạy Game Pipeline...
echo.
python main.py --mode game --input "%GAME_PATH%" --provider %PROVIDER% %ENGINE_ARG%
echo.
pause
goto MENU

:: ==========================================
:: MANGA PIPELINE
:: ==========================================
:MANGA
cls
echo.
echo  ═══ MANGA PIPELINE ═══
echo.
echo   Nhập đường dẫn thư mục ảnh manga:
echo   (Ví dụ: E:\Manga\Chapter01)
echo.
set "MANGA_PATH="
set /p "MANGA_PATH=  Path: "

if "%MANGA_PATH%"=="" (
    echo   ⚠️  Chưa nhập đường dẫn!
    timeout /t 2 >nul
    goto MANGA
)

echo.
echo   Ngôn ngữ nguồn:
echo   [1] Japanese (ja)    [2] Chinese (zh)    [3] Korean (ko)    [4] English (en)
echo.
set "LANG_CHOICE="
set /p "LANG_CHOICE=  Ngôn ngữ [1-4, Enter=ja]: "

set "SRC_LANG=ja"
if "%LANG_CHOICE%"=="2" set "SRC_LANG=zh"
if "%LANG_CHOICE%"=="3" set "SRC_LANG=ko"
if "%LANG_CHOICE%"=="4" set "SRC_LANG=en"

echo.
echo   🚀 Đang chạy Manga Pipeline...
echo.
python main.py --mode manga --input "%MANGA_PATH%" --provider %PROVIDER% --source-lang %SRC_LANG%
echo.
pause
goto MENU

:: ==========================================
:: FILM PIPELINE
:: ==========================================
:FILM
cls
echo.
echo  ═══ FILM PIPELINE ═══
echo.
echo   Nhập đường dẫn file video:
echo   (Ví dụ: E:\Movies\anime.mkv)
echo.
set "FILM_PATH="
set /p "FILM_PATH=  Video path: "

if "%FILM_PATH%"=="" (
    echo   ⚠️  Chưa nhập đường dẫn!
    timeout /t 2 >nul
    goto FILM
)

echo.
echo   Nhập đường dẫn file subtitle (Enter = tự tìm):
set "SUB_PATH="
set /p "SUB_PATH=  Subtitle path: "

echo.
echo   Giọng đọc TTS:
echo   [1] Nữ - HoaiMyNeural    [2] Nam - NamMinhNeural
echo.
set "VOICE_CHOICE="
set /p "VOICE_CHOICE=  Giọng [1-2, Enter=nữ]: "

set "VOICE=vi-VN-HoaiMyNeural"
if "%VOICE_CHOICE%"=="2" set "VOICE=vi-VN-NamMinhNeural"

set "SUB_ARG="
if not "%SUB_PATH%"=="" set "SUB_ARG=--subtitle "%SUB_PATH%""

echo.
echo   🚀 Đang chạy Film Pipeline...
echo.
python main.py --mode film --input "%FILM_PATH%" %SUB_ARG% --provider %PROVIDER% --voice %VOICE%
echo.
pause
goto MENU

:: ==========================================
:: AUTO-DETECT
:: ==========================================
:AUTO
cls
echo.
echo  ═══ AUTO-DETECT PIPELINE ═══
echo.
echo   Nhập đường dẫn (thư mục game / ảnh manga / video):
echo.
set "AUTO_PATH="
set /p "AUTO_PATH=  Path: "

if "%AUTO_PATH%"=="" (
    echo   ⚠️  Chưa nhập đường dẫn!
    timeout /t 2 >nul
    goto AUTO
)

echo.
echo   🔍 Đang tự nhận diện và chạy...
echo.
python main.py --mode auto --input "%AUTO_PATH%" --provider %PROVIDER%
echo.
pause
goto MENU

:: ==========================================
:: DEMO
:: ==========================================
:DEMO
cls
echo.
echo  ═══ DEMO MODE ═══
echo.
python main.py --demo
echo.
pause
goto MENU

:: ==========================================
:: PROVIDER SELECTION
:: ==========================================
:PROVIDER
cls
echo.
echo  ═══ CHỌN PROVIDER ═══
echo.
echo   Hiện tại: %PROVIDER%
echo.
echo   [1] local  — AG-Translator backend (Dolphin/HyMT trên GPU)
echo   [2] mimo   — Xiaomi MiMo V2.5 API (cần MIMO_API_KEY)
echo   [3] auto   — Tự động chọn (MiMo trước, fallback local)
echo.
set "P_CHOICE="
set /p "P_CHOICE=  Chọn [1-3]: "

if "%P_CHOICE%"=="1" set "PROVIDER=local"
if "%P_CHOICE%"=="2" set "PROVIDER=mimo"
if "%P_CHOICE%"=="3" set "PROVIDER=auto"

echo.
echo   ✅ Đã chọn provider: %PROVIDER%
timeout /t 1 >nul
goto MENU

:: ==========================================
:: CHECK BACKEND STATUS
:: ==========================================
:STATUS
cls
echo.
echo  ═══ KIỂM TRA BACKEND ═══
echo.
echo   Đang kiểm tra AG-Translator backend...
echo.

curl -s http://localhost:5000/api/translate/status >nul 2>&1
if %errorlevel%==0 (
    echo   [Dolphin GGUF]
    curl -s http://localhost:5000/api/translate/status
    echo.
    echo.
    echo   [Tencent HY-MT]
    curl -s http://localhost:5000/api/translate/hymt/status
    echo.
) else (
    echo   ❌ Backend không chạy!
    echo.
    echo   Để khởi động:
    echo   cd E:\DichGame\Backend
    echo   python server.py
)

echo.
pause
goto MENU

:: ==========================================
:: DOCS
:: ==========================================
:DOCS
cls
echo.
echo  ═══ TÀI LIỆU ═══
echo.
echo   [1] README (mở trong notepad)
echo   [2] SRS - Requirements Analysis
echo   [3] SAD - System Architecture
echo   [4] SDP - Project Plan
echo   [5] Quay lại
echo.
set "DOC_CHOICE="
set /p "DOC_CHOICE=  Chọn [1-5]: "

if "%DOC_CHOICE%"=="1" (start notepad README.md)
if "%DOC_CHOICE%"=="2" (start notepad docs\vi\01-requirements-analysis-SRS.md)
if "%DOC_CHOICE%"=="3" (start notepad docs\vi\02-system-architecture-SAD.md)
if "%DOC_CHOICE%"=="4" (start notepad docs\vi\03-project-plan-SDP.md)
goto MENU

:: ==========================================
:: EXIT
:: ==========================================
:EXIT
echo.
echo   Tạm biệt! 👋
echo.
exit /b 0
