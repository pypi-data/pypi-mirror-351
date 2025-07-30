from pathlib import Path
import ctypes


def load_library():
    [path] = Path(__file__).resolve().parent.glob("lib_stoken_bfasst.*")
    return ctypes.cdll.LoadLibrary(str(path))
