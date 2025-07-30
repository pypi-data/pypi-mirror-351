import re
from dataclasses import dataclass, field
from typing import List, Tuple, Callable, TypeVar, Any, Union
import pandas as pd
import warnings
import matplotlib.pyplot as plt
import numpy as np
import csv
import math
import statistics
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.ticker as mtick
from dateutil import parser as date_parser
from matplotlib.ticker import MaxNLocator

T = TypeVar('T')
R = TypeVar('R')

_VOID_STRING = "_NA"

##########
# Config #
##########

ALLOW_INFINITY = False
WARN_INFINITY = True
DATA_PATH = './data'

#######################
# Warnings and Errors #
#######################

def _WARN_INFINITY(override: bool = False) -> None:
    """
    Internal helper to issue a warning when an infinite value is produced.

    Parameters:
        override (bool): If True, force the warning even if WARN_INFINITY is False.
    """
    if WARN_INFINITY:
        warnings.warn(
            'An infinite value was produced'
            '\nTo disable this warning, use \'WARN_INFINITY = False\'',
            UserWarning
        )
    elif override:
        warnings.warn(
            'An infinite value was produced'
            '\n(This is a forced warning and cannot be disabled)',
            UserWarning
        )


def _ERROR_INFINITY(override: bool = False) -> None:
    """
    Internal helper to raise an error when an infinite value is produced.

    Parameters:
        override (bool): If True, force an error even if ALLOW_INFINITY is True.

    Raises:
        ValueError: When infinite values are not allowed.
    """
    if not ALLOW_INFINITY:
        raise ValueError(
            'An infinite value was produced'
            '\nTo allow infinities and disable this error message, use \'ALLOW_INFINITY = True\''
        )
    elif override:
        warnings.warn(
            'An infinite value was produced'
            '\n(This is a forced error message and cannot be disabled)',
            UserWarning
        )

##################
# Data Structure #
##################

@dataclass
class Candle:
    """
    Represents a single OHLC (Open-High-Low-Close) data point.

    Attributes:
        date (str): Date of the candle in DD-MM-YYYY format.
        time (str): Time of the candle in HH:MM:SS format.
        open (float): Opening price.
        high (float): Highest price.
        low (float): Lowest price.
        close (float): Closing price.
        volume (float): Volume traded.
    """
    date:   str  # DD-MM-YYYY
    time:   str  # HH:MM:SS
    open:   float
    high:   float
    low:    float
    close:  float
    volume: float


class OHLC:
    """
    Loads OHLC data from a CSV file or a pandas DataFrame and stores it in lists.

    Attributes:
        source (Union[str, pd.DataFrame]): Either the ticker symbol (CSV file) or a DataFrame.
        candles (List[Candle]): List of Candle objects.
        dates, times, opens, highs, lows, closes, volumes (List): Separate lists of each candle attribute.
    """
    def __init__(self, source: Union[str, pd.DataFrame], yf_format: bool = True) -> None:
        """
        Initialize the OHLC dataset from either a CSV file ('<ticker>.csv') or a pandas DataFrame.

        Parameters:
            source (str or pd.DataFrame): If str, expects a CSV named '<source>.csv'; if DataFrame, uses it directly.
            timescale (str, optional): Resolution of data.
        """
        self.source = source
        self.candles: List[Candle] = []
        self.dates:   List[str] = []
        self.times:   List[str] = []
        self.opens:   List[float] = []
        self.highs:   List[float] = []
        self.lows:    List[float] = []
        self.closes:  List[float] = []
        self.volumes: List[float] = []

        # Load into a DataFrame
        if isinstance(source, str):
            filename = f'{DATA_PATH}/{source}'
            df = pd.read_csv(filename)
        elif isinstance(source, pd.DataFrame):
            df = source.copy()
        else:
            raise TypeError("source must be a ticker string or a pandas DataFrame")

        timezone_string = re.compile(r'([+-]\d{2}:\d{2})$')

        df = df.reset_index()

        df.columns = [col.lower() for col in df.columns]

        date_col = next((col for col in df.columns if 'date' in col), None)
        time_col = next((col for col in df.columns if 'time' in col), None)

        required_fields = ['open', 'high', 'low', 'close', 'volume']
        for field in required_fields:
            if field not in df.columns:
                raise KeyError(f"Missing '{field}' column in data source")

        for _, row in df.iterrows():
            date_value = str(row[date_col]) if date_col else _VOID_STRING
            time_value = str(row[time_col]) if time_col else _VOID_STRING

            if yf_format:
                date_value = timezone_string.sub("", date_value)
                datetime = date_value.split(" ")
                date_val = datetime[0]
                time_val = datetime[1]

            try:
                open_val   = float(row['open'])
                high_val   = float(row['high'])
                low_val    = float(row['low'])
                close_val  = float(row['close'])
                volume_val = float(row['volume'])
            except ValueError as e:
                raise ValueError(f"Invalid numeric value in row: {e}")

            candle = Candle(
                date=date_val,
                time=time_val,
                open=open_val,
                high=high_val,
                low=low_val,
                close=close_val,
                volume=volume_val
            )

            self.candles.append(candle)
            self.dates.append(candle.date)
            self.times.append(candle.time)
            self.opens.append(candle.open)
            self.highs.append(candle.high)
            self.lows.append(candle.low)
            self.closes.append(candle.close)
            self.volumes.append(candle.volume)


#####################
# Data Manipulation #
#####################


def dropsd(values: List[float], n: float = 1.5) -> List[float]:
    """
    Remove values outside n standard deviations from the mean.

    Parameters:
        values (List[float]): Input list of numbers.
        n (float): Number of standard deviations for filtering (must be >=0).

    Returns:
        List[float]: Filtered list of values within the specified range.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError('Cannot have negative n value')

    mu = mean(values)
    bound = n * sd(values)
    keep = []
    for value in values:
        if value <= mu + bound and value >= mu - bound:
            keep.append(value)
    return keep


def dropif(values: List[T], condition: Callable[[T, int], bool]) -> List[T]:
    """
    Remove items from a list based on a condition.

    Parameters:
        values (List[T]): Input list.
        condition (Callable[[T, int], bool]): Function returning True to keep an item.

    Returns:
        List[T]: Filtered list of values that satisfy the condition.
    """
    keep = []
    for i in range(len(values)):
        if condition(values[i], i):
            keep.append(values[i])
    return keep


def downsample(values: List[T], old: str, new: str) -> List[T]:
    """
    Convert data to lower resolution (downsampling).

    Parameters:
        values (List[T]): Input data points.
        old (str): Original timescale (e.g., '1m', '2h').
        new (str): Desired lower resolution (e.g., '1h', '1d').

    Returns:
        List[T]: Downsampled list of values.

    Raises:
        ValueError: If conversion between scales is not supported.
    """
    oldscale = old[-1]
    oldfactor = int(old[:-1]) if len(old) > 1 else 1
    newscale = new[-1]
    newfactor = int(new[:-1]) if len(new) > 1 else 1

    if oldscale == 'm' and newscale == 'h':
        step = 60 * newfactor / oldfactor
    elif oldscale == 'h' and newscale == 'd':
        step = 24 * newfactor / oldfactor
    elif oldscale == 'm' and newscale == 'd':
        step = 60 * 24 * newfactor / oldfactor
    elif oldscale == newscale and (oldscale == 'm' or oldscale == 'h' or oldscale == 'd'):
        step = newfactor / oldfactor
        if step < 1:
            raise ValueError(f'Cannot convert from timescale \'{old}\' to \'{new}\'')
    else:
        raise ValueError(f'Cannot convert from timescale \'{old}\' to \'{new}\'')

    return [values[i] for i in range(0, len(values), int(step))]


def setLen(base: List[T], newsize: int) -> List[T]:
    """
    Resize a list using linear interpolation and repetition.

    Parameters:
        base (List[T]): Original list.
        newsize (int): Desired length (must be non-negative).

    Returns:
        List[T]: Resized list of length newsize.

    Raises:
        ValueError: If base is empty or newsize is negative.
        NotImplementedError: If downscaling is requested.
    """
    if len(base) == 0:
        raise ValueError('Cannot change length of an empty list')
    if newsize < 0:
        raise ValueError('List lengths cannot be negative')

    scale = newsize / len(base)

    if scale < 1:
        # TODO: handle when len(base) > newsize
        raise NotImplementedError

    stretched = []
    whole = int(scale)

    for i in range(len(base) - 1):
        stretched.append(base[i])
        stretched[len(stretched):len(stretched)] = inter(base[i], base[i + 1], whole - 1)
    stretched.append(base[-1])

    remaining = newsize - len(stretched)
    if remaining == 0:
        return stretched

    incr = int(len(stretched) / remaining)

    j = 0
    while len(stretched) < newsize:
        stretched.insert(j + 1, inter(stretched[j], stretched[j + 1], 1)[0])
        j += incr + 1

    return stretched

###########
# Algebra #
###########


def inter(a: float, b: float, points: int = 1) -> List[float]:
    """
    Generate points between a and b via linear interpolation.

    Parameters:
        a (float): Start value.
        b (float): End value.
        points (int): Number of points to generate between a and b.

    Returns:
        List[float]: List of interpolated values.

    Raises:
        ValueError: If points is negative.
    """
    if points < 0:
        raise ValueError('Number of internal points cannot be less than 0')

    points += 1
    return [a + ((b - a) / points) * i for i in range(1, points)]

##############
# Statistics #
##############


def pdf(values: List[float]) -> List[float]:
    """
    Compute the probability density function (Gaussian) normalized over the data.

    Parameters:
        values (List[float]): Data points.

    Returns:
        List[float]: Normalized PDF values summing to 1.

    Raises:
        ValueError: If values list is empty.
    """
    if len(values) == 0:
        raise ValueError('List must be non-empty')

    x = np.array(values, dtype=float)
    z = (x - x.mean()) / x.std(ddof=0)
    pdf_vals = np.exp(-0.5 * z**2) / np.sqrt(2 * np.pi)
    probs = pdf_vals / pdf_vals.sum()
    return probs.tolist()


def sd(values: List[float]) -> float:
    """
    Compute the sample standard deviation.

    Parameters:
        values (List[float]): Data points.

    Returns:
        float: Sample standard deviation.

    Raises:
        ValueError: If values list is empty.
    """
    if len(values) == 0:
        raise ValueError('List must be non-empty')

    return statistics.stdev(values)


def mean(values: List[float]) -> float:
    """
    Compute the arithmetic mean.

    Parameters:
        values (List[float]): Data points.

    Returns:
        float: Mean of the values.

    Raises:
        ValueError: If values list is empty.
    """
    if len(values) == 0:
        raise ValueError('List must be non-empty')

    return sum(values) / len(values)


def corr(x: List[float], y: List[float]) -> float:
    """
    Compute Pearson correlation coefficient between two lists.

    Parameters:
        x (List[float]): First data series.
        y (List[float]): Second data series (same length as x).

    Returns:
        float: Correlation coefficient.

    Raises:
        ValueError: If lists differ in length or are empty.
    """
    if len(x) != len(y):
        raise ValueError('Lists must be of the same length')
    if len(x) == 0:
        raise ValueError('Lists must be non-empty')

    return float(np.corrcoef(x, y)[0, 1])


def sma(values: List[float], period: int) -> List[float]:
    """
    Get the rolling simple moving average.

    Parameters:
        values (List[float]): Data points.
        period (int): Size of rolling window to compute SMA.

    Returns:
        List[float]: Rolling SMA values.

    Raises:
        ValueError: If period < 1 or values is empty
    """
    if len(values) == 0:
        raise ValueError('List must be non-empty')
    if period < 1:
        raise ValueError('Period must be greater than 0')

    return rolWin(values, period, lambda v, i: mean(v))


########################
# Price Trend Analysis #
########################


def logReturns(prices: List[float]) -> List[float]:
    """
    Compute log returns for a series of prices.

    Parameters:
        prices (List[float]): List of price data.

    Returns:
        List[float]: Log returns between consecutive prices.

    Raises:
        ValueError: If fewer than 2 prices or a zero price encountered when infinities not allowed.
    """
    if len(prices) < 2:
        raise ValueError('List must contain at least 2 elements')

    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] == 0:
            if ALLOW_INFINITY:
                returns.append(math.inf * prices[i] / abs(prices[i]))
                _WARN_INFINITY()
            else:
                _ERROR_INFINITY()
        else:
            returns.append(math.log(prices[i] / prices[i - 1]))

    return returns


def ariReturns(prices: List[float]) -> List[float]:
    """
    Compute arithmetic returns for a series of prices.

    Parameters:
        prices (List[float]): List of price data.

    Returns:
        List[float]: Arithmetic returns between consecutive prices.

    Raises:
        ValueError: If fewer than 2 prices or a zero price encountered when infinities not allowed.
    """
    if len(prices) < 2:
        raise ValueError('List must contain at least 2 elements')

    returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] == 0:
            if ALLOW_INFINITY:
                returns.append(math.inf * prices[i] / abs(prices[i]))
                _WARN_INFINITY()
            else:
                _ERROR_INFINITY()
        else:
            returns.append((prices[i] - prices[i - 1]) / prices[i - 1])

    return returns


def logReturn(old: float, new: float) -> float:
    """
    Compute single-period log return.

    Parameters:
        old (float): Previous price.
        new (float): Current price.

    Returns:
        float: Logarithmic return.

    Raises:
        ValueError: If old price is zero when infinities not allowed.
    """
    if old == 0:
        if ALLOW_INFINITY:
            _WARN_INFINITY()
            return math.inf * new / abs(new)
        else:
            _ERROR_INFINITY()

    return math.log(new / old)


def ariReturn(old: float, new: float) -> float:
    """
    Compute single-period arithmetic return.

    Parameters:
        old (float): Previous price.
        new (float): Current price.

    Returns:
        float: Arithmetic return.

    Raises:
        ValueError: If old price is zero when infinities not allowed.
    """
    if old == 0:
        if ALLOW_INFINITY:
            _WARN_INFINITY()
            return math.inf * new / abs(new)
        else:
            _ERROR_INFINITY()

    return (new - old) / old


def cumReturns(prices: List[float]) -> List[float]:
    """
    Compute cumulative returns relative to the first price.

    Parameters:
        prices (List[float]): List of price data.

    Returns:
        List[float]: Cumulative return at each time step.

    Raises:
        ValueError: If fewer than 2 prices or first price is zero when infinities not allowed.
    """
    if len(prices) < 2:
        raise ValueError('List must contain at least 2 elements')
    if prices[0] == 0:
        if ALLOW_INFINITY:
            _WARN_INFINITY()
            return [math.inf * prices[i] / abs(prices[i]) for i in range(len(prices))]
        else:
            _ERROR_INFINITY()

    return [(prices[i] - prices[0]) / prices[0] for i in range(len(prices))]


def totReturn(prices: List[float]) -> float:
    """
    Compute total return from first to last price.

    Parameters:
        prices (List[float]): List of price data.

    Returns:
        float: Total return.

    Raises:
        ValueError: If fewer than 2 prices or first price is zero when infinities not allowed.
    """
    if len(prices) < 2:
        raise ValueError('List must contain at least 2 elements')
    if prices[0] == 0:
        if ALLOW_INFINITY:
            _WARN_INFINITY()
            return math.inf * prices[-1] / abs(prices[-1])
        else:
            _ERROR_INFINITY()

    return (prices[-1] - prices[0]) / prices[0]

##########
# Groups #
##########


def grBounds(values: List[float], n: int) -> List[Tuple[float, float]]:
    """
    Calculate n equally spaced bounds for grouping values.

    Parameters:
        values (List[float]): Data points.
        n (int): Number of groups (bins).

    Returns:
        List[Tuple[float, float]]: List of (lower, upper) bounds per group.

    Raises:
        ValueError: If n <= 0.
    """
    if n <= 0:
        raise ValueError('Cannot have less than 1 bound')

    inorder = sorted(values)
    width = (inorder[-1] - inorder[0]) / n

    return [(inorder[0] + i * width, inorder[0] + (i + 1) * width) for i in range(n)]


def grGet(values: List[float], bounds: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Assign values to groups based on provided bounds.

    Parameters:
        values (List[float]): Data points.
        bounds (List[Tuple[float, float]]): List of (low, high) bounds.

    Returns:
        List[List[float]]: Groups of values per bound.
    """
    groups = []
    for bound in bounds:
        groups.append([])
        for value in values:
            if value <= bound[1] and value > bound[0]:
                groups[-1].append(value)
            elif len(groups) == 1 and value == bound[0]:
                groups[0].append(value)

    return groups


def grCount(values: List[float], bounds: List[Tuple[float, float]]) -> List[float]:
    """
    Count number of values in each group defined by bounds.

    Parameters:
        values (List[float]): Data points.
        bounds (List[Tuple[float, float]]): List of (low, high) bounds.

    Returns:
        List[float]: Count per group.
    """
    counts = []
    for bound in bounds:
        counts.append(0)
        for value in values:
            if (value <= bound[1] and value > bound[0]) or (len(counts) == 1 and value == bound[0]):
                counts[-1] += 1

    return counts


def grFreq(values: List[float], bounds: List[Tuple[float, float]], event: Callable[[List[float], int], bool]) -> List[float]:
    """
    Count occurrences of an event per group.

    Parameters:
        values (List[float]): Data points.
        bounds (List[Tuple[float, float]]): List of (low, high) bounds.
        event (Callable[[List[float], int], bool]): Event function taking (values, index).

    Returns:
        List[float]: Number of events per group.
    """
    counts = []
    for bound in bounds:
        counts.append(0)
        for i in range(len(values)):
            if (values[i] <= bound[1] and values[i] > bound[0]) or (len(counts) == 1 and values[i] == bound[0]):
                if event(values, i):
                    counts[-1] += 1

    return counts


def grProb(values: List[float], bounds: List[Tuple[float, float]], event: Callable[[List[float], int], bool]) -> List[float]:
    """
    Compute probability of an event within each group.

    Parameters:
        values (List[float]): Data points.
        bounds (List[Tuple[float, float]]): List of (low, high) bounds.
        event (Callable[[List[float], int], bool]): Event function taking (values, index).

    Returns:
        List[float]: Probability per group (positive/total).
    """
    positive = []
    total = []
    for bound in bounds:
        positive.append(0)
        total.append(0)
        for i in range(len(values)):
            if (values[i] <= bound[1] and values[i] > bound[0]) or (len(positive) == 1 and values[i] == bound[0]):
                total[-1] += 1
                if event(values, i):
                    positive[-1] += 1

    return [positive[i] / (total[i] if total[i] > 0 else 1) for i in range(len(total))]

#########
# Tools #
#########

def rolWin(values: List[T], window: int, method: Callable[[List[T], int], R]) -> List[R]:
    """
    Iterate over a list with a rolling window and a custom method.

    Parameters:
        values (List[T]): Data points.
        window (int: Number of elements in the window.
        method (Callable[[List[T], int], R]): Custom method executed on each window.

    Returns:
        List[R]: List of outcomes from custom method over each window.

    Raises:
        ValueError: If window < 1 or window > len(values).
    """
    if window < 1 or window > len(values):
        raise ValueError(f'Window must be less than the length of your values list and at least 1'
                         f'\nwindow = {window}, len(values) = {len(values)}')

    outcomes = []
    for i in range(len(values) - window):
        outcomes.append(method(values[i : i + window], i))

    return outcomes

#################
# Visualisation #
#################

@dataclass
class Display:
    """
    Aesthetic settings for plotting functions.

    Attributes:
        xlabel (str): Label for the x-axis.
        ylabel (str): Label for the y-axis.
        title  (str): Title of the plot.
    """
    xlabel: str = 'x'
    ylabel: str = 'y'
    title: str  = 'Plot'


def line(y: List[float], x: List[float] = None, aes: Display = None) -> None:
    """
    Create a line plot of y vs x.

    Parameters:
        y (List[float]): Y-values.
        x (List[float], optional): X-values (defaults to index sequence).
        aes (Display, optional): Plot styling options.
    """
    aes = aes or Display(title='Line Plot')
    x = list(range(len(y))) if x is None else x
    x, y = zip(*sorted(zip(x, y), key=lambda pair: pair[0]))

    plt.figure()
    plt.plot(x, y)
    plt.xlabel(aes.xlabel)
    plt.ylabel(aes.ylabel)
    plt.title(aes.title)
    plt.show()


def scat(y: List[float], x: List[float], aes: Display = None) -> None:
    """
    Create a scatter plot of y vs x.

    Parameters:
        y (List[float]): Y-values.
        x (List[float]): X-values.
        aes (Display, optional): Plot styling options.
    """
    aes = aes or Display(title='Scatter Plot')

    plt.figure()
    plt.scatter(x, y)
    plt.xlabel(aes.xlabel)
    plt.ylabel(aes.ylabel)
    plt.title(aes.title)
    plt.show()


def hist(values: List[float], bins: int = 10, density: bool = False, aes: Display = None) -> None:
    """
    Create a histogram of data values.

    Parameters:
        values (List[float]): Data to histogram.
        bins (int): Number of histogram bins.
        density (bool): If True, show probability density.
        aes (Display, optional): Plot styling options.
    """
    aes = aes or Display(title='Histogram', xlabel='Value', ylabel='Density' if density else 'Frequency')

    plt.figure()
    plt.hist(values, bins=bins, density=density)
    plt.xlabel(aes.xlabel)
    plt.ylabel(aes.ylabel)
    plt.title(aes.title)
    plt.show()


def histline(values: List[float], y: List[float], density: bool = False, aes: Display = None) -> None:
    """
    Create a histogram with an overlaid line plot.

    Parameters:
        values (List[float]): Data to histogram.
        y (List[float]): Line values to overlay.
        density (bool): If True, normalize histogram.
        aes (Display, optional): Plot styling options.
    """
    aes = aes or Display(title='Histogram + Line', xlabel='Value', ylabel='Density' if density else 'Frequency')

    bins = len(y)
    groups = grBounds(values, bins)
    x = [(low + high) / 2 for low, high in groups]

    fig, ax1 = plt.subplots()
    ax1.hist(values, bins=bins, density=density)
    ax1.set_xlabel(aes.xlabel)
    ax1.set_ylabel(aes.ylabel)
    ax1.set_title(aes.title)

    ax2 = ax1.twinx()
    ax2.plot(x, y)
    ax2.set_ylabel('Line Value')
    fig.tight_layout()
    plt.show()


def bar(x: List[T], heights: List[float], aes: Display = None) -> None:
    """
    Create a bar chart.

    Parameters:
        x (List[T]): Categories for bars.
        heights (List[float]): Heights of bars.
        aes (Display, optional): Plot styling options.
    """
    aes = aes or Display(title='Bar Chart', xlabel='Category', ylabel='Value')

    plt.figure()
    plt.bar(x, heights)
    plt.xlabel(aes.xlabel)
    plt.ylabel(aes.ylabel)
    plt.title(aes.title)
    plt.show()


def distr(values: List[float], aes: Display = None) -> None:
    """
    Plot the distribution (PDF) of values.

    Parameters:
        values (List[float]): Data points.
        aes (Display, optional): Plot styling options.
    """
    aes = aes or Display(title='Distribution', xlabel='Value', ylabel='Probability')
    line(y=pdf(values), x=values, aes=aes)


def lines(ys: List[List[float]], x: List[float] = None, autofit: bool = True, aes: Display = None) -> None:
    """
    Plot multiple lines on the same axes.

    Parameters:
        ys (List[List[float]]): List of sets of y-coordinates.
        x (List[float], optional): Shared x-values (defaults to index).
        autofit (Bool, optional): Automatically adjust lengths of y-coordinate sets to match x-coordinate set
        aes (Display, optional): Plot styling options.

    Raises:
        ValueError: If plot type is invalid or data lengths mismatch x.
    """
    aes = aes or Display(title='Lines')
    x = list(range(len(plots[0][1]))) if x is None else x

    if any(len(y) != len(x) for y in ys) and not autofit:
        raise ValueError(f'At least one of your y-coordinates sets is not the same size as your set of x-coordinates'
                         f'\nConsider using \'y = setLen(y, len(x))\' or \'autofit=True\' to resolve the issue')

    fig, ax = plt.subplots()

    for y in ys:
        if autofit:
            plt.plot(x, setLen(y, len(x)))
        else:
            plt.plot(x, y)

    # TODO: Ticks count hardcoded to 10
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10, prune=None))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    ax.set_xlabel(aes.xlabel)
    ax.set_ylabel(aes.ylabel)
    ax.set_title(aes.title)
    fig.tight_layout()
    plt.show()


def multiplot(plots: List[Tuple[str, List[float]]], x: List[float] = None, aes: Display = None) -> None:
    """
    Plot multiple series on the same axes.

    Parameters:
        plots (List[Tuple[str, List[float]]]): List of (plot_type, data) tuples.
        x (List[float], optional): Shared x-values (defaults to index).
        aes (Display, optional): Plot styling options.

    Raises:
        ValueError: If plot type is invalid or data lengths mismatch x.
    """
    aes = aes or Display(title='Multiplot')
    x = list(range(len(plots[0][1]))) if x is None else x

    if any(len(y) != len(x) for _, y in plots):
        raise ValueError(f'At least one of your y-coordinates sets is not the same size as your set of x-coordinates'
                         f'\nConsider using \'y = setLen(y, len(x))\' to resolve the issue')

    plt.figure()

    for plot_type, data in plots:
        if plot_type == 'line':
            plt.plot(x, data)
        elif plot_type == 'scatter':
            plt.scatter(x, data)
        else:
            raise ValueError(f"'{plot_type}' is not a valid plot type for multiplot")

    plt.xlabel(aes.xlabel)
    plt.ylabel(aes.ylabel)
    plt.title(aes.title)
    plt.show()


def candlestick(ohlc: OHLC, width: float = 0.8, xticks: str = 'date', overlays: List[List[float]] = [], labels: List[str] = []) -> None:
    """
    Plot candlestick chart from OHLC object.

    Parameters:
        ohlc (OHLC): Object containing candlestick data.
        width (float, optional): Display width of each candlestick.
        xticks (str, optional): 'date', 'time' or 'datetime' to display corresponding tick.
        overlays (List[List[float]], optional): Collection of y-coordinates to overlay the candlesticks as line plots.
        labels (List[str], optional): Labels for the overlays, matched by index.
    """
    fig, ax = plt.subplots()
    xs, lbls = [], []

    timezone_string = re.compile(r'([+-]\d{2}:\d{2})$')

    for c in ohlc.candles:
        # Skip if no date
        if c.date == _VOID_STRING:
            continue

        # Build display label pieces
        date_str = str(c.date)
        time_str = "" if c.time == _VOID_STRING else str(c.time)

        _date = "date"
        _time = "time"
        _empty = ""

        label = f"{date_str if _date in xticks else _empty} {time_str if _time in xticks else _empty}"
        lbls.append(label)

        xs.append(len(xs))

    for x, o, h, l, c in zip(xs, ohlc.opens, ohlc.highs, ohlc.lows, ohlc.closes):
        ax.plot([x, x], [l, h], color='black', linewidth=1, zorder=1)
        bullish = c >= o
        bottom = o if bullish else c
        height = max(abs(c - o), 0.01)
        rect = Rectangle(
            (x - width/2, bottom),
            width,
            height,
            facecolor=('green' if bullish else 'red'),
            edgecolor='black',
            linewidth=0.5,
            zorder=2
        )
        ax.add_patch(rect)


    m = len(xs)
    for i in range(len(overlays)):
        overlay = overlays[i]
        k = len(overlay)
        diff = m - k
        if diff > 0:
            x_vals = xs[diff:]
            y_vals = overlay
        elif diff < 0:
            # x_vals = xs
            # y_vals = overlay[-m:]
            raise ValueError('Overlay cannot have more datapoints than candles')
        else:
            x_vals = xs
            y_vals = overlay

        ax.plot(x_vals, y_vals, linewidth=1.5, zorder=3, label=labels[i] if i < len(labels) else None)

    # for overlay in overlays:
    #     ax.plot(xs, setLen(overlay, len(xs)), linewidth=1.5, zorder=3)

    # TODO: Ticks count hardcoded to 10
    n = len(xs)
    if n:
        idxs = np.linspace(0, n - 1, min(10, n), dtype=int)
        tick_pos = [xs[i] for i in idxs]
        tick_lbl = [lbls[i] for i in idxs]
        ax.set_xticks(tick_pos)
        ax.set_xticklabels(tick_lbl, rotation=45, ha='right')

    ax.set_ylabel('Price')
    ax.set_title('Candlestick Chart')
    if len(labels) > 0:
        ax.legend(loc='best')
    plt.tight_layout()
    plt.show()
