import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

from . import cdma_interactive


def make_interactive_ui():
    num_users = widgets.Dropdown(options=[2, 3, 4], value=2, description="Users:")
    chip_len = widgets.Dropdown(options=[8, 16, 32], value=8, description="Chip L:")
    noise = widgets.FloatSlider(value=0, min=0, max=1.0, step=0.01, description="Noise:")
    new_codes_btn = widgets.Button(description="New codes")
    random_bits_btn = widgets.Button(description="Random bits")

    bits_box = widgets.HBox([])
    codes_out = widgets.Textarea(
        value="", description="Codes:",
        layout=widgets.Layout(width="100%", height="120px")
    )
    recv_out = widgets.Textarea(
        value="", description="Recovered:",
        layout=widgets.Layout(width="100%", height="120px")
    )
    plot_out = widgets.Output(layout=widgets.Layout(width="100%"))

    state = {"codes": None, "bits": None}

    def rebuild_bits_ui(U):
        ds = []
        for i in range(U):
            dd = widgets.Dropdown(options=[-1, 1], value=1, description=f"U{i+1}")
            dd.observe(refresh, "value")
            ds.append(dd)
        bits_box.children = ds

    def get_bits_from_ui():
        return np.array([c.value for c in bits_box.children], dtype=int)

    def set_bits_to_ui(bits):
        for i, b in enumerate(bits):
            bits_box.children[i].value = int(b)

    def refresh(*_):
        U = int(num_users.value)
        L = int(chip_len.value)
        sig = float(noise.value)

        if state["codes"] is None or state["codes"].shape != (U, L):
            state["codes"] = cdma_interactive.make_codes(U, L)

        if len(bits_box.children) != U:
            rebuild_bits_ui(U)

        if state["bits"] is None or state["bits"].shape != (U,):
            state["bits"] = cdma_interactive.rand_pm1(U)
            set_bits_to_ui(state["bits"])

        bits = get_bits_from_ui()
        state["bits"] = bits

        codes, bits, rx, corrs, rec_bits = cdma_interactive.cdma_once(
            U=U, L=L, noise=sig, bits=bits, codes=state["codes"]
        )

        codes_out.value = "\n".join(
            [f"U{i+1}: [{' '.join(map(str, codes[i].tolist()))}]" for i in range(U)]
        )
        recv_out.value = "\n".join(
            [f"U{i+1}: corr={corrs[i]:.2f}  -> bit={rec_bits[i]}" for i in range(U)]
        )

        with plot_out:
            clear_output(wait=True)

            fig, ax = plt.subplots(figsize=(10, 2.5))
            ax.set_title("Received chips (sum + noise)")
            ax.axhline(0, lw=1)
            bars = ax.bar(range(L), rx)
            ax.bar_label(bars, fmt="%.1f", label_type="center", fontsize=8, color="white", fontweight="bold")
            ax.set_xlabel("chip index")
            ax.set_ylabel("value")
            plt.show()

            fig, ax = plt.subplots(figsize=(10, 2.5))
            ax.set_title("Correlation values (per user)")
            ax.axhline(0, lw=1)
            ax.bar([f"U{i+1}" for i in range(U)], corrs)
            ax.set_ylabel("corr")
            plt.show()

    def new_codes(_):
        U = int(num_users.value)
        L = int(chip_len.value)
        state["codes"] = cdma_interactive.make_codes(U, L)
        refresh()

    def random_bits(_):
        U = int(num_users.value)
        state["bits"] = cdma_interactive.rand_pm1(U)
        set_bits_to_ui(state["bits"])
        refresh()

    num_users.observe(refresh, "value")
    chip_len.observe(refresh, "value")
    noise.observe(refresh, "value")
    new_codes_btn.on_click(new_codes)
    random_bits_btn.on_click(random_bits)

    ui = widgets.VBox([
        widgets.HBox([num_users, chip_len, noise, new_codes_btn, random_bits_btn]),
        widgets.HTML("<b>User bits</b> (set each to -1 or +1):"),
        bits_box,
        widgets.HBox([codes_out, recv_out]),
        plot_out
    ])

    display(ui)
    refresh()