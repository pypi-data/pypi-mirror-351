"""Functions to plot PDFs"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from numpy.typing import ArrayLike, NDArray

from .core.lazy_modules import mpl, plt


def init_matplotlib() -> None:
    """Initialize matplotlib parameters"""
    # Comment out usetex and serif, as these sometimes
    # cause issues on cori with no LaTex installed by
    # default
    # mpl.rcParams['text.usetex'] = True
    # mpl.rcParams['mathtext.rm'] = 'serif'
    mpl.rcParams["font.family"] = "serif"
    mpl.rcParams["font.serif"] = "Times New Roman"
    mpl.rcParams["axes.titlesize"] = 16
    mpl.rcParams["axes.labelsize"] = 16
    mpl.rcParams["savefig.dpi"] = 250
    mpl.rcParams["savefig.format"] = "pdf"
    mpl.rcParams["savefig.bbox"] = "tight"


# init_matplotlib()

COLORS = {}
COLORS["truth"] = "k"
COLORS["mix_mod"] = "k"
COLORS["gridded"] = "k"
COLORS["quantiles"] = "blueviolet"
COLORS["histogram"] = "darkorange"
COLORS["samples"] = "forestgreen"

STYLES = {}
STYLES["truth"] = "-"
STYLES["mix_mod"] = ":"
STYLES["gridded"] = "--"
STYLES["quantiles"] = "--"  # (0,(5,10))
STYLES["histogram"] = ":"  # (0,(3,6))
STYLES["samples"] = "-."  # (0,(1,2))


def make_figure_axes(xlim: tuple[float, float], **kwargs: Any):
    """
    Build a figure and a set of figure axes to plot data on

    Parameters
    ----------
    xlim : tuple[float, float]
        The x-axis limits of the plot
    **kwargs
        Passed directly to the `matplotlib` plot function

    Returns
    -------
    tuple [ Figure, Axes ]
        The figure and axes
    """

    xlabel = kwargs.pop("xlabel", "redshift")
    ylabel = kwargs.pop("ylabel", "p(z)")

    fig = plt.figure()
    axes = fig.add_subplot(111)
    axes.set_xlim(xlim[0], xlim[-1])
    axes.set_xlabel(xlabel, fontsize=16)
    axes.set_ylabel(ylabel, fontsize=16)

    return (fig, axes)


def get_axes_and_xlims(**kwargs: Any):
    """Get and return the axes and xlims from the kwargs

    Returns
    -------
    axes : Axes
        The axes for the figure
    xlim : tuple[float, float]
        The limits for the x axis
    kwargs
        Additional kwargs to be passed on.
    """
    axes = kwargs.pop("axes", None)
    xlim = kwargs.pop("xlim", None)
    if axes is None:
        if xlim is None:  # pragma: no cover
            raise ValueError("Either xlim or axes must be provided")
        _, axes = make_figure_axes(xlim, **kwargs)
    else:
        if xlim is not None:  # pragma: no cover
            raise ValueError("Only one of xlim and axes should be provided")
        xlim = axes.get_xlim()
    return axes, xlim, kwargs


def plot_pdf_on_axes(axes, pdf: "Ensemble", xvals: ArrayLike, **kwargs: Any):
    """
    Plot a PDF on a set of axes, by evaluating it a set of points

    Parameters
    ----------
    axes : Axes
        The axes we want to plot the data on

    pdf : Ensemble
        The distribution we want to plot

    xvals : ArrayLike
        The locations we evaluate the PDF at for plotting
    **kwargs
        Keywords are passed to matplotlib

    Returns
    -------
    Axes
        The axes the data are plotted on
    """
    yvals = pdf.pdf(xvals)
    axes.plot(np.squeeze(xvals), np.squeeze(yvals), **kwargs)
    return axes


def plot_dist_pdf(pdf: "Ensemble", **kwargs: Any):
    """
    Plot a PDF on a set of axes, using the axes limits

    Parameters
    ----------
    pdf :  Ensemble
        The distribution we want to plot

    Other Parameters
    ----------------
    axes : Axes
        The axes to plot on

    xlim : tuple [float, float]
        The x-axis limits

    npts : int
        The number of x-axis points

    **kwargs :
        Passed directly to the `~qp.plotting.plot_pdf_on_axes` plot function

    Returns
    -------
    Axes
        The axes the data are plotted on
    """
    axes, xlim, kw = get_axes_and_xlims(**kwargs)
    npoints = kw.pop("npts", 101)
    xvals = np.linspace(xlim[0], xlim[1], npoints)
    return plot_pdf_on_axes(axes, pdf, xvals, **kw)


def plot_pdf_quantiles_on_axes(
    axes,
    xvals: ArrayLike,
    yvals: ArrayLike,
    quantiles: tuple[np.ndarray, np.ndarray],
    **kwargs: Any,
):
    """
    Plot a PDF on a set of axes, by evaluating at the quantiles provided

    Parameters
    ----------
    axes : Axes
        The axes we want to plot the data on

    xvals : ArrayLike
        Pdf xvalues

    yvals : ArrayLike
        Pdf yvalues

    quantiles : tuple [ np.ndarray, np.ndarray ]
       The quantiles that define the distribution pdf

    **kwargs :
        Passed directly to the `matplotlib` plot function

    Other Parameters
    ----------------
    npoints : int
        Number of points to use in the plotting.  Evenly spaced along the axis provided.

    Returns
    -------
    Axes
        The axes the data are plotted on
    """
    kwargs.setdefault("label", "Quantiles")
    kwargs.setdefault("color", COLORS["quantiles"])
    axes.scatter(
        quantiles[1],
        np.zeros(np.shape(quantiles[1])),
        marker="|",
        s=100,
        alpha=0.75,
        **kwargs,
    )
    kwargs.setdefault("label", "Quantile Interpolated PDF")
    axes.plot(xvals, yvals, lw=2.0, alpha=1.0, linestyle=STYLES["quantiles"], **kwargs)
    return axes


def plot_pdf_histogram_on_axes(axes, hist: ArrayLike, **kwargs: Any):
    """
    Plot a PDF on a set of axes, by plotting the histogrammed data

    Parameters
    ----------
    axes : Axes
        The axes we want to plot the data on
    hist : ArrayLike
        Histogram data
    **kwargs :
        Passed directly to the `matplotlib` plot function

    Other Parameters
    ----------------
    npoints : int
        Number of points to use in the plotting.  Evenly spaced along the axis provided.

    Returns
    -------
    Axes
        The axes the data are plotted on
    """

    kwargs.setdefault("color", COLORS["histogram"])
    axes.scatter(
        hist[0],
        np.zeros(np.shape(hist[0])),
        marker="|",
        s=100,
        label="Histogram Bin Ends",
        alpha=0.75,
    )
    bin_centers = (hist[0][0:-1] + hist[0][1:]) / 2.0
    kwargs.setdefault("label", "Histogram Interpolated PDF")
    axes.hist(
        bin_centers,
        bins=hist[0],
        weights=np.squeeze(hist[1]),
        lw=None,
        alpha=1.0,
        **kwargs,
    )
    return axes


def plot_pdf_samples_on_axes(axes, pdf: "Ensemble", samples: ArrayLike, **kwargs: Any):
    """
    Plot a PDF on a set of axes, by displaying a set of samples from the PDF

    Parameters
    ----------
    axes : Axes
        The axes we want to plot the data on

    pdf :  Ensemble
        The distribution we want to plot

    samples : ArrayLike
        Points sampled from the PDF
    **kwargs :
        Passed directly to the `matplotlib` plot function

    Returns
    -------
    Axes
        The axes the data are plotted on
    """
    kwargs.setdefault("label", "Samples")
    kwargs.setdefault("color", COLORS["samples"])
    axes.scatter(
        samples, np.zeros(np.shape(samples)), marker="|", s=100, alpha=0.75, **kwargs
    )
    npoints = kwargs.pop("npoints", 101)
    xlim = axes.get_xlim()
    xvals = np.linspace(xlim[0], xlim[1], npoints)
    yvals = np.squeeze(pdf.pdf(xvals))
    kwargs.setdefault("label", "Samples Interpolated PDF")
    plt.plot(xvals, yvals, lw=2.0, alpha=1.0, linestyle=STYLES["samples"], **kwargs)
    return axes


def plot_native(pdf, **kwargs):
    """Utility function to plot a pdf in a format that is specific to that type of pdf"""
    if hasattr(pdf, "plot_native"):
        axes = pdf.plot_native(**kwargs)
    else:
        axes = pdf.dist.plot_native(pdf, **kwargs)
    return axes.figure, axes


def plot(pdf, **kwargs):
    """Utility function to plot a pdf in a format that is specific to that type of pdf"""
    if hasattr(pdf, "plot_native"):
        axes = pdf.plot(**kwargs)
    else:
        axes = pdf.dist.plot(pdf, **kwargs)
    return axes.figure, axes
