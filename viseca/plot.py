from typing import Optional, cast

import click
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import mixbox
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from scipy.interpolate import PchipInterpolator


def _setup_theme():
    color = "#1f1f1f"
    font_size = 9
    sns.set_style("dark")
    sns.set_theme(
        style="darkgrid",
        rc={
            "font.family": "DejaVu Sans",
            "font.size": font_size,
            "xtick.labelsize": font_size,
            "ytick.labelsize": font_size,
            "axes.facecolor": color,
            "figure.facecolor": color,
            "grid.color": "#2e2e2e",
            "xtick.color": "white",
            "ytick.color": "white",
            "text.color": "white",
            "axes.labelcolor": "white",
            "axes.edgecolor": color,
        },
    )
    sns.despine()


def resample(df: pd.DataFrame, rule: str):
    return (
        df.resample(rule, on="Date")
        .agg(
            {
                "Amount": "sum",
                "Merchant": "list",
                "PFMCategoryID": "list",
                "PFMCategoryName": "list",
            }
        )
        .reset_index()
    )


def add_shadow(
    x: np.ndarray,
    y: np.ndarray,
    color: tuple[int, int, int],
    ax: "Axes",
    pad: float = 2.0,
    nb_alpha: int = 50,
):
    alphas = np.linspace(0.2, 0, nb_alpha)
    to_rgb = (31, 31, 31)

    # y_lin = scipy.interpolate.interp1d(num_x, y, kind=1)(x_smooth_num)

    for i, alpha in enumerate(alphas):
        top_offset = i * pad
        bot_offset = top_offset + pad

        r, g, b = cast(
            tuple[int, int, int], mixbox.lerp(color, to_rgb, (i + 1) / len(alphas))
        )
        c = (r / 255, g / 255, b / 255)

        ax.fill_between(
            x=x,
            y1=y - bot_offset,
            y2=y - top_offset,
            color=c,
            alpha=alpha,
            zorder=1,
        )


def plot_with_shadow(
    x: pd.Series,
    y: pd.Series,
    color: tuple[int, int, int] = (0, 255, 255),
    ax: Optional["Axes"] = None,
):
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 7))
    ax.scatter(x, y, color="pink", s=7, zorder=999)

    num_x = pd.to_numeric(x)
    x_smooth_num = np.linspace(num_x.min(), num_x.max(), 300)
    pchip = PchipInterpolator(num_x, y)
    y_smooth = pchip(x_smooth_num)
    x_smooth = pd.to_datetime(x_smooth_num)

    y_mean = np.ones(len(x_smooth)) * y.mean()
    ax.plot(x_smooth, y_mean, color=(0.9, 0, 0.9), linewidth=1, zorder=1)
    add_shadow(x_smooth, y_mean, color=(200, 0, 200), ax=ax, pad=0.3)

    ax.plot(x_smooth, y_smooth, color=(0, 1, 1), linewidth=1)
    add_shadow(x_smooth, y_smooth, color=color, ax=ax)

    ax.tick_params(axis="x", rotation=30)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda tick, _: f"${int(tick)}"))
    ax.set_xlim(left=x_smooth.min(), right=x_smooth.max())
    ax.set_ylim(bottom=max(y.min() - 100, 0))


@click.command()
@click.option("--filename", help="File to plot")
@click.option(
    "--date-from",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="From which date on transactions should be fetched (format: YYYY-MM-DD, included)",
)
@click.option(
    "--date-to",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="To which date transactions should be fetched (format: YYYY-MM-DD, included)",
)
def plot(filename: str, date_from: str, date_to: str):
    df = pd.read_csv(filename)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    df = df[df["Date"] >= pd.to_datetime(date_from)]
    df = df[df["Date"] <= pd.to_datetime(date_to)]

    # Viseca sends a recap of your monthly transactions
    # These transactions are (to my knowledge) the only ones that can be negative
    transfer_mask = (df["Amount"] < 0) & pd.isna(df["Merchant"])
    _, expenses = df[transfer_mask], df[~transfer_mask]

    week_expenses = resample(expenses, rule="W-Mon")
    month_expenses = resample(expenses, rule="ME")

    _setup_theme()
    _, axs = plt.subplots(figsize=(24, 7), ncols=2)
    plot_with_shadow(x=week_expenses["Date"], y=week_expenses["Amount"], ax=axs[0])
    plot_with_shadow(x=month_expenses["Date"], y=month_expenses["Amount"], ax=axs[1])
    plt.show()


if __name__ == "__main__":
    plot()
