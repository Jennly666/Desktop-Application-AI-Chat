import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_windows():
    print("Building Windows executable...")
    
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    bin_dir = Path("bin")
    bin_dir.mkdir(exist_ok=True)
    
    # --onefile: создать один исполняемый файл
    # --windowed: запускать без консольного окна
    # --name: задать имя выходного файла
    # --clean: очистить кэш PyInstaller перед сборкой
    # --noupx: не использовать UPX для сжатия
    # --uac-admin: запрашивать права администратора при запуске
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=AI Chat",
        "--clean",
        "--noupx",
        "--uac-admin",
        "src/main.py"
    ])
    
    try:
        shutil.move("dist/AI Chat.exe", "bin/AIChat.exe")
        print("Windows build completed! Executable location: bin/AIChat.exe")
    except:
        print("Windows build completed! Executable location: dist/AI Chat.exe")

def build_linux():
    print("Building Linux executable...")
    
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    bin_dir = Path("bin")
    bin_dir.mkdir(exist_ok=True)
    
    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--icon=assets/icon.ico",
        "--name=aichat",
        "src/main.py"
    ])
    
    try:
        shutil.move("dist/aichat", "bin/aichat")
        print("Linux build completed! Executable location: bin/aichat")
    except:
        print("Linux build completed! Executable location: dist/aichat")

def main():
    if sys.platform.startswith('win'):
        build_windows()
    elif sys.platform.startswith('linux'):
        build_linux()
    else:
        print("Unsupported platform")


if __name__ == "__main__":
    main()
