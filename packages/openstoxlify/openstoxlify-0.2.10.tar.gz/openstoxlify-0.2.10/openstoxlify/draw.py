import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime
from .models import PlotType, ActionType
from .plotter import PLOT_DATA
from .fetch import MARKET_DATA
from .strategy import STRATEGY_DATA

COLOR_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

ASSIGNED_COLORS = {}


def _get_color(label):
    """Assign a consistent random color for each label."""
    if label not in ASSIGNED_COLORS:
        ASSIGNED_COLORS[label] = random.choice(COLOR_PALETTE)
    return ASSIGNED_COLORS[label]


def _has_plotting_data() -> bool:
    """Check if there's any data available to plot.

    Returns:
        bool: True if there's data to plot, False otherwise
    """
    for plot_type in PlotType:
        if PLOT_DATA.get(plot_type):
            return True

    if hasattr(MARKET_DATA, "quotes") and MARKET_DATA.quotes:
        return True

    if STRATEGY_DATA.get("strategy"):
        for strategy in STRATEGY_DATA["strategy"]:
            if strategy.get("data"):
                return True

    return False


def draw(
    show_legend: bool = True,
    figsize: tuple = (12, 6),
    offset_multiplier: float = 0.05,
    rotation: int = 30,
    ha: str = "right",
    title: str = "Market Data Visualizations",
    xlabel: str = "Date",
    ylabel: str = "Price",
    candle_linewidth: float = 1,
    candle_body_width: float = 4,
    marker_size: int = 8,
    annotation_fontsize: int = 9,
    histogram_alpha: float = 0.6,
    area_alpha: float = 0.3,
    line_width: float = 2,
):
    """Draw all charts from the PLOT_DATA and MARKET_DATA with customizable options.

    Args:
        show_legend (bool): Whether to show the legend. Default True.
        figsize (tuple): Figure size as (width, height). Default (12, 6).
        offset_multiplier (float): Multiplier for trade annotation offset. Default 0.05.
        rotation (int): Rotation angle for x-axis labels. Default 30.
        ha (str): Horizontal alignment for x-axis labels. Default 'right'.
        title (str): Chart title. Default 'Market Data Visualizations'.
        xlabel (str): X-axis label. Default 'Date'.
        ylabel (str): Y-axis label. Default 'Price'.
        candle_linewidth (float): Width of candle wick lines. Default 1.
        candle_body_width (float): Width of candle body lines. Default 4.
        marker_size (int): Size of trade markers. Default 8.
        annotation_fontsize (int): Font size for trade annotations. Default 9.
        histogram_alpha (float): Transparency for histogram bars. Default 0.6.
        area_alpha (float): Transparency for area plots. Default 0.3.
        line_width (float): Width of line plots. Default 2.
    """
    if not _has_plotting_data():
        print("No data available to plot")
        return

    fig, ax = plt.subplots(figsize=figsize)

    def convert_timestamp(timestamp):
        if isinstance(timestamp, str):
            return mdates.date2num(datetime.fromisoformat(timestamp))
        return mdates.date2num(timestamp)

    plotted_histograms = set()
    for plot in PLOT_DATA.get(PlotType.HISTOGRAM, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]

        bar_width = (
            (max(timestamps) - min(timestamps)) / len(timestamps) * 0.8
            if len(timestamps) > 1
            else 0.5
        )
        label = (
            plot["label"] if plot["label"] not in plotted_histograms else "_nolegend_"
        )
        plotted_histograms.add(plot["label"])

        ax.bar(
            timestamps,
            values,
            label=label,
            color=_get_color(plot["label"]),
            width=bar_width,
            alpha=histogram_alpha,
        )

    for plot in PLOT_DATA.get(PlotType.LINE, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]
        ax.plot(
            timestamps,
            values,
            label=plot["label"],
            color=_get_color(plot["label"]),
            lw=line_width,
        )

    for plot in PLOT_DATA.get(PlotType.AREA, []):
        timestamps = [convert_timestamp(item["timestamp"]) for item in plot["data"]]
        values = [item["value"] for item in plot["data"]]
        ax.fill_between(
            timestamps,
            values,
            label=plot["label"],
            color=_get_color(plot["label"]),
            alpha=area_alpha,
        )

    candle_lut = {}
    for item in MARKET_DATA.quotes:
        timestamp = item.timestamp
        ts_str = timestamp if isinstance(timestamp, str) else timestamp.isoformat()
        ts_num = convert_timestamp(timestamp)
        price = item.close

        color = "green" if item.close > item.open else "red"
        ax.vlines(ts_num, item.low, item.high, color=color, lw=candle_linewidth)
        ax.vlines(ts_num, item.open, item.close, color=color, lw=candle_body_width)

        candle_lut[ts_str] = (ts_num, price)

    for strategy in STRATEGY_DATA.get("strategy", []):
        for trade in strategy.get("data", []):
            if "timestamp" not in trade:
                continue

            ts_key = (
                trade["timestamp"]
                if isinstance(trade["timestamp"], str)
                else trade["timestamp"].isoformat()
            )

            if ts_key not in candle_lut:
                continue

            ts_num, price = candle_lut[ts_key]
            offset = price * offset_multiplier
            direction = trade.get("action") or trade.get("value")
            amount = trade.get("amount", 0.0)

            if direction == ActionType.LONG.value:
                y = price - offset
                ax.plot(ts_num, y, marker="^", color="blue", markersize=marker_size)
                ax.annotate(
                    f"LONG {amount}",
                    xy=(ts_num, y),
                    xytext=(0, -15),
                    textcoords="offset points",
                    ha="center",
                    fontsize=annotation_fontsize,
                    color="blue",
                )
            elif direction == ActionType.SHORT.value:
                y = price + offset
                ax.plot(ts_num, y, marker="v", color="purple", markersize=marker_size)
                ax.annotate(
                    f"SHORT {amount}",
                    xy=(ts_num, y),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha="center",
                    fontsize=annotation_fontsize,
                    color="purple",
                )

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if show_legend and ax.get_legend_handles_labels()[0]:
        ax.legend()

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=rotation, ha=ha)
    plt.tight_layout()
    plt.show()
