# src/pricepy/__init__.py

from .pricepy import (
    # config
    ALLOW_INFINITY,
    WARN_INFINITY,
    DATA_PATH,
    # warnings & errors
    _WARN_INFINITY,
    _ERROR_INFINITY,
    # data structures
    Candle,
    OHLC,
    # data manipulation
    dropsd,
    dropif,
    downsample,
    setLen,
    # algebra
    inter,
    # statistics
    pdf,
    sd,
    mean,
    corr,
    sma,
    # price trend analysis
    logReturns,
    ariReturns,
    logReturn,
    ariReturn,
    cumReturns,
    totReturn,
    # groups
    grBounds,
    grGet,
    grCount,
    grFreq,
    grProb,
    # tools
    rolWin,
    # visualisation
    Aesthetics,
    line,
    scat,
    hist,
    histline,
    bar,
    distr,
    multiplot,
)

__all__ = [
    # config
    "ALLOW_INFINITY",
    "WARN_INFINITY",
    "DATA_PATH",
    # warnings & errors
    "_WARN_INFINITY",
    "_ERROR_INFINITY",
    # data structures
    "Candle",
    "OHLC",
    # data manipulation
    "dropsd",
    "dropif",
    "downsample",
    "setLen",
    # algebra
    "inter",
    # statistics
    "pdf",
    "sd",
    "mean",
    "corr",
    "sma",
    # price trend analysis
    "logReturns",
    "ariReturns",
    "logReturn",
    "ariReturn",
    "cumReturns",
    "totReturn",
    # groups
    "grBounds",
    "grGet",
    "grCount",
    "grFreq",
    "grProb",
    # tools
    "rolWin",
    # visualisation
    "Aesthetics",
    "line",
    "scat",
    "hist",
    "histline",
    "bar",
    "distr",
    "multiplot",
]
