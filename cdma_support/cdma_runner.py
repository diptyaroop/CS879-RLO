import os
import re
import sys
import tempfile
import subprocess

import numpy as np
from IPython.display import clear_output

from .cdma_ref import reference_decode, build_hint


TEST_CODES = np.array([
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, -1, 1, -1, 1, -1, 1, -1],
    [1, 1, -1, -1, 1, 1, -1, -1],
], dtype=np.int32)

PUBLIC_BITS = np.array([1, -1, 1], dtype=np.int32)


def print_vec(name, v):
    print(f"{name}: [{', '.join(str(int(x)) for x in v)}]")


def normalize_sign(arr):
    arr = np.asarray(arr)
    return np.where(arr >= 0, 1, -1).astype(np.int32)


def make_run_python(py_editor, out):
    def run_python(_):
        with out:
            clear_output()
            namespace = {}

            try:
                exec(py_editor.value, namespace)
            except Exception as e:
                print("Python syntax/runtime error while loading template:")
                print(e)
                return

            required = ["encode", "modulate", "demodulate", "decode", "run_cdma_pipeline"]
            missing = [name for name in required if name not in namespace]
            if missing:
                print("Missing required functions:", ", ".join(missing))
                return

            try:
                pred = namespace["run_cdma_pipeline"](
                    PUBLIC_BITS.copy(), TEST_CODES.copy(), noise_std=0.0, seed=7
                )
                pred = normalize_sign(pred)
            except Exception as e:
                print("Error while running run_cdma_pipeline:")
                print(e)
                return

            print_vec("Student output", pred)

            try:
                ref = reference_decode(PUBLIC_BITS, TEST_CODES, noise_std=0.0, seed=7)
                print_vec("Reference output", ref)
                print("Public check:", "PASS" if np.array_equal(pred, ref) else "FAIL")
            except Exception as e:
                print("Reference check unavailable:")
                print(e)
                print(f"Tip: build the shared library with: {build_hint()}")
                return

            rng = np.random.default_rng(12345)
            for t in range(1, 6):
                bits_t = rng.choice([-1, 1], size=3).astype(np.int32)
                try:
                    pred_t = namespace["run_cdma_pipeline"](
                        bits_t.copy(), TEST_CODES.copy(), noise_std=0.0, seed=t
                    )
                    pred_t = normalize_sign(pred_t)
                    ref_t = reference_decode(bits_t, TEST_CODES, noise_std=0.0, seed=t)
                except Exception as e:
                    print(f"Hidden check {t}: ERROR ({e})")
                    return

                if not np.array_equal(pred_t, ref_t):
                    print(f"Hidden check {t}: FAIL")
                    print_vec("  bits", bits_t)
                    print_vec("  student", pred_t)
                    print_vec("  reference", ref_t)
                    return

            print("Hidden checks: PASS (5/5)")

    return run_python


def make_run_cpp(cpp_editor, harness_cpp, out):
    def run_cpp(_):
        with out:
            clear_output()

            try:
                ref = reference_decode(PUBLIC_BITS, TEST_CODES, noise_std=0.0, seed=7)
            except Exception as e:
                print("Reference check unavailable:")
                print(e)
                print(f"Tip: build the shared library with: {build_hint()}")
                return

            with tempfile.TemporaryDirectory() as d:
                user_cpp = os.path.join(d, "student.cpp")
                harness_cpp_path = os.path.join(d, "harness.cpp")
                exe = os.path.join(
                    d, "student_runner.exe" if sys.platform.startswith("win") else "student_runner"
                )

                with open(user_cpp, "w", encoding="utf-8") as f:
                    f.write(cpp_editor.value)
                with open(harness_cpp_path, "w", encoding="utf-8") as f:
                    f.write(harness_cpp)

                try:
                    comp = subprocess.run(
                        ["g++", "-std=c++17", "-O2", user_cpp, harness_cpp_path, "-o", exe],
                        capture_output=True,
                        text=True,
                    )
                except FileNotFoundError:
                    print("g++ not found. Install g++, then try again.")
                    return

                if comp.stdout.strip():
                    print("--- compile stdout ---")
                    print(comp.stdout)
                if comp.stderr.strip():
                    print("--- compile stderr ---")
                    print(comp.stderr)

                if comp.returncode != 0:
                    print("Compilation failed.")
                    return

                run = subprocess.run([exe], capture_output=True, text=True)
                if run.returncode != 0:
                    print("Program exited with code", run.returncode)
                if run.stdout.strip():
                    print("--- program stdout ---")
                    print(run.stdout.strip())
                if run.stderr.strip():
                    print("--- program stderr ---")
                    print(run.stderr.strip())

                vals = re.findall(r"-?\d+", run.stdout)
                if len(vals) < 3:
                    print("Could not parse 3 decoded bits from program output.")
                    return

                pred = normalize_sign(np.array([int(vals[0]), int(vals[1]), int(vals[2])], dtype=np.int32))
                print_vec("Parsed student output", pred)
                print_vec("Reference output", ref)
                print("Public check:", "PASS" if np.array_equal(pred, ref) else "FAIL")

    return run_cpp


def make_build_ref(out, run_build_command):
    def build_ref(_):
        with out:
            clear_output()
            try:
                proc = run_build_command()
            except Exception as e:
                print("Failed to start build:")
                print(e)
                return

            if proc.stdout.strip():
                print(proc.stdout.strip())
            if proc.stderr.strip():
                print(proc.stderr.strip())
            print("Build status:", "SUCCESS" if proc.returncode == 0 else f"FAILED ({proc.returncode})")

    return build_ref