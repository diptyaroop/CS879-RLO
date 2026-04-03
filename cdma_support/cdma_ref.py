import os
import sys
import ctypes
import subprocess
from pathlib import Path

import numpy as np


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
REF_DIR = PROJECT_DIR / "ref"
INSTR_DIR = PROJECT_DIR / "instructor_ref"

_ref_fn = None


def build_hint():
    if sys.platform.startswith("win"):
        return r"powershell -ExecutionPolicy Bypass -File .\instructor_ref\build_ref_lib.ps1"
    return "bash ./instructor_ref/build_ref_lib.sh"


def run_build_command():
    if sys.platform.startswith("win"):
        script = INSTR_DIR / "build_ref_lib.ps1"
        if not script.exists():
            raise FileNotFoundError(f"Build script not found: {script}")
        return subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            capture_output=True,
            text=True,
        )

    script = INSTR_DIR / "build_ref_lib.sh"
    if not script.exists():
        raise FileNotFoundError(f"Build script not found: {script}")
    return subprocess.run(["bash", str(script)], capture_output=True, text=True)


def ref_lib_path():
    if sys.platform.startswith("win"):
        return REF_DIR / "cdma_ref.dll"
    if sys.platform == "darwin":
        return REF_DIR / "libcdma_ref.dylib"
    return REF_DIR / "libcdma_ref.so"


def load_ref_fn():
    global _ref_fn
    if _ref_fn is not None:
        return _ref_fn

    lib_path = ref_lib_path()
    if not lib_path.exists():
        return None

    lib = ctypes.CDLL(str(lib_path))
    fn = lib.cdma_reference_decode
    fn.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int),
        ctypes.c_double,
        ctypes.c_uint,
        ctypes.POINTER(ctypes.c_int),
    ]
    fn.restype = ctypes.c_int
    _ref_fn = fn
    return fn


def reference_decode(bits, codes, noise_std=0.0, seed=7):
    fn = load_ref_fn()
    if fn is None:
        raise FileNotFoundError(
            "Reference library not found. Build it with: "
            f"{build_hint()}"
        )

    bits = np.asarray(bits, dtype=np.int32)
    codes = np.asarray(codes, dtype=np.int32)
    users, chip_len = codes.shape

    if bits.shape != (users,):
        raise ValueError(f"bits shape {bits.shape} does not match users={users}")

    flat_codes = np.ascontiguousarray(codes.reshape(-1), dtype=np.int32)
    out = np.zeros(users, dtype=np.int32)

    rc = fn(
        int(users),
        int(chip_len),
        bits.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        flat_codes.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
        float(noise_std),
        int(seed),
        out.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    )
    if rc != 0:
        raise RuntimeError(f"Reference library returned error code: {rc}")
    return out