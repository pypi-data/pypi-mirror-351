"""
finalisers.py

Simple convenience functions to finalise and produce plots.
- bar_plot_finalise()
- line_plot_finalise()
- postcovid_plot_finalise()
- raw_growth_plot_finalise()
- revision_plot_finalise()
- run_plot_finalise()
- seastrend_plot_finalise()
- series_growth_plot_finalise()
- summary_plot_finalise()

Note: we keep these functions in a separate module to
stop circular imports

We also do most of the indicative code testing from this
module.
"""

# --- imports
from pandas import DataFrame, period_range, Period, PeriodIndex, read_csv, Index
from numpy import random

from mgplot.test import prepare_for_test
from mgplot.settings import DataT
from mgplot.multi_plot import plot_then_finalise, multi_column, multi_start
from mgplot.line_plot import line_plot
from mgplot.bar_plot import bar_plot
from mgplot.seastrend_plot import seastrend_plot
from mgplot.postcovid_plot import postcovid_plot
from mgplot.revision_plot import revision_plot
from mgplot.run_plot import run_plot
from mgplot.growth_plot import series_growth_plot, raw_growth_plot
from mgplot.summary_plot import summary_plot, ZSCORES, ZSCALED


# --- public functions
def line_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call plot_then_finalise(), which
    wraps calls to line_plot() and finalise_plot().
    """

    if isinstance(data, DataFrame):
        if len(data.columns) > 1:
            # default to displaying a legend
            kwargs["legend"] = kwargs.get("legend", True)
        if len(data.columns) > 4:
            # default to using a style for the lines
            kwargs["style"] = kwargs.get(
                "style", ["solid", "dashed", "dashdot", "dotted"]
            )
    plot_then_finalise(
        data,
        function=line_plot,
        **kwargs,
    )


def bar_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call plot_then_finalise(), which
    wraps calls to bar_plot() and finalise_plot().
    """

    plot_then_finalise(
        data,
        function=bar_plot,
        **kwargs,
    )


def seastrend_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call seas_trend_plot() and finalise_plot().
    """

    plot_then_finalise(
        data,
        function=seastrend_plot,
        **kwargs,
    )


def postcovid_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call postcovid_plot() and finalise_plot().
    """

    plot_then_finalise(
        data,
        function=postcovid_plot,
        **kwargs,
    )


def revision_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call revision_plot() and finalise_plot().
    """

    kwargs["legend"] = kwargs.get(
        "legend", {"loc": "best", "fontsize": "x-small", "ncol": 2}
    )
    kwargs["style"] = kwargs.get("style", ["solid", "dashed", "dashdot", "dotted"])
    plot_then_finalise(
        data,
        function=revision_plot,
        **kwargs,
    )


def run_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call run_plot() and finalise_plot().
    """

    plot_then_finalise(
        data=data,
        function=run_plot,
        **kwargs,
    )


def series_growth_plot_finalise(data: DataT, **kwargs) -> None:
    """
    A convenience function to call series_growth_plot() and finalise_plot().
    Use this when you are providing the series data, for mgplot to calculate
    the growth series.
    """

    kwargs["ylabel"] = kwargs.get("ylabel", "Per cent Growth")
    kwargs["xlabel"] = kwargs.get("xlabel", None)
    plot_then_finalise(
        data=data,
        function=series_growth_plot,
        **kwargs,
    )


def raw_growth_plot_finalise(data: DataT, **kwargs) -> None:
    """
    A convenience function to call series_growth_plot() and finalise_plot().
    Use this when you are providing the raw growth data. Don't forget to
    set the ylabel in kwargs.
    """

    kwargs["ylabel"] = kwargs.get("ylabel", "Growth Units unspecified")
    kwargs["xlabel"] = kwargs.get("xlabel", None)
    plot_then_finalise(
        data=data,
        function=raw_growth_plot,
        **kwargs,
    )


def summary_plot_finalise(
    data: DataT,
    **kwargs,
) -> None:
    """
    A convenience function to call summary_plot() and finalise_plot().
    This is more complex than most convienience methods.

    Arguments
    - data: DataFrame containing the summary data. The index must be a PeriodIndex.
    - kwargs: additional arguments for the plot, including:
        - plot_from: int | Period | None  (None means plot from 1995-01-01)
        - verbose: if True, print the summary data.
        - middle: proportion of data to highlight (default is 0.8).
        - plot_type: list of plot types to generate (either "zscores" or "zscaled")
          defaults to "zscores".
    """

    # --- sanity checks
    if not isinstance(data.index, PeriodIndex):
        raise ValueError("data must have a PeriodIndex")

    # --- standard arguments
    kwargs["legend"] = kwargs.get(
        "legend",
        {
            # put the legend below the x-axis label
            "loc": "upper center",
            "fontsize": "xx-small",
            "bbox_to_anchor": (0.5, -0.125),
            "ncol": 4,
        },
    )
    start = kwargs.get("plot_from", None)

    for plot_type in (ZSCORES, ZSCALED):
        # some sorting of kwargs for plot production
        kwargs["plot_type"] = plot_type
        kwargs["title"] = kwargs.get("title", f"Summary at {data.index[-1]}")
        kwargs["pre_tag"] = plot_type  # necessary because the title is same
        kwargs["preserve_lims"] = kwargs.get(
            "preserve_lims", True
        )  # preserve the x-axis limits

        # get the start date for the plot
        set_default = start is None
        if isinstance(start, int):
            start = data.index[start]
        if set_default:
            freq = data.index.freqstr[0]
            if freq not in ("D", "M", "Q"):
                raise ValueError(f"Unknown frequency {freq} for data index")
            start = Period("1995-01-01", freq=data.index.freqstr)
        kwargs["plot_from"] = start

        if plot_type not in (ZSCORES, ZSCALED):
            print(f"Unknown plot type {plot_type}, defaulting to {ZSCORES}")
            plot_type = ZSCORES
        if plot_type == "zscores":
            kwargs["xlabel"] = f"Z-scores for prints since {start}"
            kwargs["x0"] = True
        else:
            kwargs["xlabel"] = f"-1 to 1 scaled z-scores since {start}"
            kwargs.pop("x0", None)

        plot_then_finalise(
            data,
            function=summary_plot,
            **kwargs,
        )


# --- test code
if __name__ == "__main__":
    # --- Preparation
    TEST_DATA_DIR = "./zz-test-data/"
    prepare_for_test("finalisers")

    # - fake data
    index = period_range(start="2010Q1", periods=60, freq="Q")
    test_frame = DataFrame(
        {
            "Series 1": [0.1] * len(index),
            "Series 2": [0.1] * len(index),
            "Series 3": [1.1] * len(index),
        },
        index=index,
    )
    test_frame["Series 1"] = test_frame["Series 1"].cumsum() + random.normal(
        0, 0.1, len(index)
    )
    test_frame["Series 2"] = test_frame["Series 2"].cumsum()
    test_frame["Series 3"] = test_frame["Series 3"].cumprod()

    SKIP = False
    if not SKIP:

        line_plot_finalise(
            data=test_frame,
            title="Test Line Plot",
            ylabel="Value",
            xlabel=None,
        )

        multi_column(
            data=test_frame,
            function=line_plot_finalise,
            title="Test Multi Column Line Plot: ",
            ylabel="Value",
            xlabel=None,
        )

        multi_start(
            data=test_frame,
            function=line_plot_finalise,
            starts=[20, -10, Period("2018Q1")],
            title="Test Multi Start Line Plot: ",
            ylabel="Value",
            xlabel=None,
        )

        postcovid_plot_finalise(
            data=test_frame["Series 3"],
            title="Test Post-COVID Plot",
            ylabel="Value",
            xlabel=None,
        )

        st = test_frame[["Series 1", "Series 2"]].copy()
        st.columns = Index(["Seasonally Adjusted", "Trend"])
        multi_start(
            st,
            function=seastrend_plot_finalise,
            starts=[0, Period("2018Q1")],
            title="Test Multi Start Seas-Trend Plot",
            ylabel="Value",
            xlabel=None,
        )

        # - summary plot test
        summary_data = read_csv(
            f"{TEST_DATA_DIR}summary.csv",
            index_col=0,
            parse_dates=True,
        )
        summary_data.index = PeriodIndex(summary_data.index, freq="M")
        summary_plot_finalise(
            data=summary_data,
            title=f"Summary Plot at {summary_data.index[-1]}",
            ylabel="Value",
            xlabel=None,
        )

        multi_start(
            data=test_frame["Series 1"],
            function=series_growth_plot_finalise,
            starts=[0, -19],
            title="Test Multi Start Series Growth Plot: ",
            ylabel="Per cent Growth",
            xlabel=None,
        )

        # -- run plot test
        ocr_data = read_csv(
            f"{TEST_DATA_DIR}ocr_rba.csv",
            index_col=0,
            parse_dates=True,
        )
        ocr_data.index = PeriodIndex(ocr_data.index, freq="M")
        ocr_series = ocr_data[ocr_data.columns[0]]
        multi_start(
            data=ocr_series,
            function=[plot_then_finalise, run_plot],
            starts=[Period("2020-11", freq="M"), Period("2000-11", freq="M"), 1],
            title=f"Test Multi Start Run Plot at {ocr_series.index[-1]}",
            ylabel="Annual Per cent Growth",
            xlabel=None,
        )

    data_ = read_csv("./zz-test-data/revisions.csv", index_col=0, parse_dates=True)
    data_.index = PeriodIndex(data_.index, freq="M")
    revision_plot_finalise(
        data=data_,
        title="Test Revision Plot",
        ylabel="Units",
        xlabel=None,
        rounding=2,
    )
