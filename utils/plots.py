import matplotlib.pyplot as plt
from io import BytesIO

def plot_matplotlib_timeseries(dates, values, title="", color="blue", figsize=(10,4)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(dates, values, marker="o", linestyle="-", color=color)
    ax.set_title(title)
    ax.set_xlabel("Année")
    ax.set_ylabel("Production")
    ax.grid(alpha=0.3)
    return fig

def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return buf
