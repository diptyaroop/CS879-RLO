from pathlib import Path

import ipywidgets as widgets
from IPython.display import display, clear_output

from .cdma_ref import run_build_command
from .cdma_runner import make_run_python, make_run_cpp, make_build_ref


BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"

PY_TEMPLATE_PATH = TEMPLATE_DIR / "cdma_template.py"
CPP_TEMPLATE_PATH = TEMPLATE_DIR / "cdma_template.cpp"
HARNESS_CPP_PATH = TEMPLATE_DIR / "harness.cpp"


def load_text(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    return path.read_text(encoding="utf-8")


def make_ui():
    py_editor = widgets.Textarea(
        value=load_text(PY_TEMPLATE_PATH),
        layout=widgets.Layout(width="100%", height="360px")
    )
    cpp_editor = widgets.Textarea(
        value=load_text(CPP_TEMPLATE_PATH),
        layout=widgets.Layout(width="100%", height="360px")
    )
    harness_cpp = load_text(HARNESS_CPP_PATH)

    out = widgets.Output(layout=widgets.Layout(width="100%"))

    run_py_btn = widgets.Button(description="Run Python Template ▶")
    run_cpp_btn = widgets.Button(description="Run C++ Template ▶")
    reset_py_btn = widgets.Button(description="Reset")
    reset_cpp_btn = widgets.Button(description="Reset")
    build_ref_btn = widgets.Button(description="Build Ref Library (Instructor)")

    def reset_py(_):
        try:
            py_editor.value = load_text(PY_TEMPLATE_PATH)
        except Exception as e:
            with out:
                clear_output()
                print("Failed to reload Python template:")
                print(e)

    def reset_cpp(_):
        try:
            cpp_editor.value = load_text(CPP_TEMPLATE_PATH)
        except Exception as e:
            with out:
                clear_output()
                print("Failed to reload C++ template:")
                print(e)

    run_py_btn.on_click(make_run_python(py_editor, out))
    run_cpp_btn.on_click(make_run_cpp(cpp_editor, harness_cpp, out))
    build_ref_btn.on_click(make_build_ref(out, run_build_command))
    reset_py_btn.on_click(reset_py)
    reset_cpp_btn.on_click(reset_cpp)

    tabs = widgets.Tab(children=[
        widgets.VBox([widgets.HBox([reset_cpp_btn, run_cpp_btn]), cpp_editor]),
        widgets.VBox([widgets.HBox([reset_py_btn, run_py_btn]), py_editor]),
    ])
    tabs.set_title(0, "C++")
    tabs.set_title(1, "Python")

    display(widgets.VBox([build_ref_btn, tabs]), out)