@echo off
rem ---------------------------------------------------------------------------
rem  Build the Halo 2 debug XBE with the hk21x fork of XboxXBERecomp.
rem
rem  The toolchain is the standalone LLVM 20.1.5 at C:\Program Files\LLVM
rem  (the Visual Studio LLVM workload is not installed), plus MSVC's rc.exe and
rem  link.exe for the resource compiler and the import libraries -- CMake
rem  needs those even when the C++ compiler is clang.
rem ---------------------------------------------------------------------------
setlocal
set "GAME_TITLE=Halo 2 (debug XBE)"
set "GAME_XBE=halo2debug.xbe"
set "GAME_EXE=Halo2"

set "VSCMAKE=G:\Program Files\VisualStudio\Common7\IDE\CommonExtensions\Microsoft\CMake"
set "NINJA=%VSCMAKE%\Ninja"
set "MSVC=G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x86"
set "SDKBIN=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x86"
set "SDKVER=10.0.26100.0"
set "SDKINC=C:\Program Files (x86)\Windows Kits\10\Include\%SDKVER%"
rem wrl/client.h (runtime/app/splash.cpp) lives under winrt\, not the usual ucrt\um\shared
set "INCLUDE=%SDKINC%\ucrt;%SDKINC%\um;%SDKINC%\shared;%SDKINC%\winrt;G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\include"
set "LIB=C:\Program Files (x86)\Windows Kits\10\Lib\%SDKVER%\um\x64;C:\Program Files (x86)\Windows Kits\10\Lib\%SDKVER%\ucrt\x64;G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\lib\x64"

set "PATH=C:\Program Files\LLVM20\bin;%MSVC%;%SDKBIN%;%VSCMAKE%\CMake\bin;%NINJA%;%PATH%"

rem the MSVC environment the SDK and the import libraries live in
call "G:\Program Files\VisualStudio\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1
set "PATH=C:\Program Files\LLVM20\bin;%MSVC%;%SDKBIN%;%VSCMAKE%\CMake\bin;%NINJA%;%PATH%"
set "INCLUDE=%SDKINC%\ucrt;%SDKINC%\um;%SDKINC%\shared;%SDKINC%\winrt;G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\include"
set "LIB=C:\Program Files (x86)\Windows Kits\10\Lib\%SDKVER%\um\x64;C:\Program Files (x86)\Windows Kits\10\Lib\%SDKVER%\ucrt\x64;G:\Program Files\VisualStudio\VC\Tools\MSVC\14.44.35207\lib\x64"

cd /d "%~dp0"
set "OUT=%CD%\out\build\release"

echo.
echo   %GAME_TITLE% - build
echo   ================================================
echo.

if not exist assets\%GAME_XBE% (
  echo   assets\%GAME_XBE% is missing.
  exit /b 1
)

rem A stale cache is the usual failure here: the compiler, the SDK path or a
rem dependency changed under it and CMake keeps the old one.
if "%~1"=="clean" (
  echo [0/3] clean cache
  if exist out\build\release rmdir /s /q out\build\release
)

echo [1/3] configure
cmake --preset release || exit /b 1

echo [2/3] XDK symbols
cmake --build out\build\release --target xbe_symbols || exit /b 1
if not exist out\build\release\sdk_dir.txt (
  echo       out\build\release\sdk_dir.txt was not written.
  exit /b 1
)
set /p SDK=<out\build\release\sdk_dir.txt
rem the scan output: config\game.toml is rewritten here and never edited, the
rem hand kept entries live in config\game_hand.toml, which includes it
"%OUT%\xbe_symbols.exe" assets\%GAME_XBE% "%SDK%\xdk" --out config\game.toml || exit /b 1

echo [3/3] build
cmake --build out\build\release || exit /b 1

echo.
echo   built: %OUT%\%GAME_EXE%.exe
echo   the recompiled code: %CD%\generated\game
endlocal
