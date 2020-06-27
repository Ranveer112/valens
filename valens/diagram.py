import io
from datetime import date

import matplotlib
import matplotlib.style
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

from valens import storage

matplotlib.style.use("seaborn-whitegrid")

matplotlib.rc("font", family="Roboto", size=12)
matplotlib.rc("legend", handletextpad=0.5, columnspacing=0.5, handlelength=1)


def plot_png(fig: Figure) -> bytes:
    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return output.getvalue()


def plot_svg(fig: Figure) -> bytes:
    fig.set_size_inches(5, 4)
    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    return output.getvalue()


def workouts(first: date = None, last: date = None) -> Figure:
    df = storage.read_workouts()
    df["reps+rir"] = df["reps"] + df["rir"]
    df = df.drop("rir", 1)
    r = df.groupby(["date"]).mean()

    plot = r.plot(style=".-", xlim=(first, last), ylim=(0, None), legend=False)

    ax2 = (
        df.groupby(["date"])
        .sum()["reps"]
        .plot(secondary_y=True, style=".-", label="volume (right)")
    )
    ax2.set(ylim=(0, None))
    ax2.grid(None)

    plot.set(xlabel=None)
    plot.grid()

    fig = plot.get_figure()
    _common_layout(fig)
    return fig


def exercise(name: str, first: date = None, last: date = None) -> Figure:
    df = storage.read_workouts()
    df["reps+rir"] = df["reps"] + df["rir"]
    df_ex = df.loc[lambda x: x["exercise"] == name]
    r = df_ex.loc[:, ["date", "reps", "reps+rir", "weight", "time"]].groupby(["date"]).mean()

    plot = r.plot(style=".-", xlim=(first, last), ylim=(0, None), legend=False)
    plot.set(xlabel=None)

    fig = plot.get_figure()
    _common_layout(fig)
    return fig


def bodyweight(first: date = None, last: date = None) -> Figure:
    bw = storage.read_bodyweight()
    df = pd.DataFrame({"weight": list(bw.values())}, index=list(bw.keys()))

    plot = df.plot(style=".-", xlim=(first, last), legend=False)
    df.rolling(window=9, center=True).mean()["weight"].plot(style="-")

    fig = plot.get_figure()
    _common_layout(fig)
    return fig


def _common_layout(fig: Figure) -> None:
    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 0.97), ncol=6)
    fig.autofmt_xdate()