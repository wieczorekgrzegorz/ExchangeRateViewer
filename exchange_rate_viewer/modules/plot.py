"""Module to generate a chart with currency exchange rates and save it as a file."""
import logging

import matplotlib.ticker
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from modules import config

log = logging.getLogger(name="app_logger")


def generate_chart(currency_table: list[tuple], selected_currency: str) -> None:
    """Generate a chart with currency exchange rates and save it as a file. The chart is saved in the 'static' folder.

    Parameters:
        currency_table (list[tuple]): list of tuples with date and exchange rates.
        selected_currency (str): currency code as per NBP API.
    """
    log.debug(msg="Generating chart with currency exchange rates.")
    axes_color = "#1f77b4"
    grid_color = "#e7f6f8"
    bg_color = "#fcfcfc"

    dates = [row[0] for row in currency_table]
    rates = [row[1] for row in currency_table]

    fig, ax = plt.subplots()
    fig.set_facecolor(color=bg_color)
    ax.patch.set_facecolor(bg_color)

    ax.plot(dates, rates, linewidth=2, marker=".", markersize=7)

    ax.set_ylabel("Exchange rates", fontdict={"weight": "bold"})
    ax.yaxis.label.set_color(axes_color)

    major_locator_x = mdates.AutoDateLocator(interval_multiples=True)
    ax.xaxis.set_major_locator(major_locator_x)
    minor_locator_x = matplotlib.ticker.MultipleLocator(base=1)
    ax.xaxis.set_minor_locator(minor_locator_x)
    ax.xaxis.label.set_color(axes_color)

    ax.tick_params(axis="x", colors=axes_color)
    ax.tick_params(axis="y", colors=axes_color)
    plt.xticks(rotation=45, ha="right")

    ax.set_title(f"{selected_currency}/PLN Exchange Rates", fontdict={"weight": "bold"})
    ax.title.set_color(axes_color)

    ax.grid(visible=True, axis="y", color=grid_color, linestyle=":")
    ax.grid(visible=True, axis="x", color=grid_color, linestyle=":")

    ax.spines["bottom"].set_color(axes_color)
    ax.spines["top"].set_color(axes_color)
    ax.spines["right"].set_color(axes_color)
    ax.spines["left"].set_color(axes_color)

    plt.tight_layout()
    plt.savefig(config.CHART_FILEPATH, transparent=True)
    plt.close()

    log.info(msg="Currency exchange rate chart generated successfully.")
