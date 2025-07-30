import subprocess
import sys
import ctypes
import psutil
from datetime import date, datetime

class fonction:
    #CMD
    @staticmethod
    def clear():
        if sys.platform=='win32':
            subprocess.run('cls', shell=True)
        elif sys.platform=='linux':
            subprocess.run('clear', shell=True)

    @staticmethod
    def title(title):
        if sys.platform=='win32':
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        if sys.platform=='linux':
            subprocess.run(f'echo -ne "\033]0;{title}\007"', shell=True)
    
    #SYSTEM
    @staticmethod
    def iswin32():
        if sys.platform == 'win32':
            return True
        else:
            return False
    
    @staticmethod
    def islinux():
        if sys.platform == 'linux':
            return True
        else:
            return False
    
    @staticmethod
    def isdarwin():
        if sys.platform == 'darwin':
            return True
        else:
            return False
    
    @staticmethod
    def cpu_usage():
        return f'{psutil.cpu_percent()}%'
    
    @staticmethod
    def ram_usage():
        return f'{psutil.virtual_memory().percent}%'
    