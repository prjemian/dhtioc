"""
Analyze signal for its recent trend.

.. autosummary::
    ~Trend

"""

__all__ = "SMOOTHING_FACTOR Trend TREND_SMOOTHING_FACTOR".split()

from .StatsReg import StatsRegClass
from .utils import smooth

SMOOTHING_FACTOR = 0.72         # factor between 0 and 1, higher is smoother
TREND_SMOOTHING_FACTOR = 0.95   # applied to the reported trend
# pick smoothing factors: https://github.com/prjemian/dhtioc/issues/20#issuecomment-672074382


class Trend:
    """
    Compute the current trend in signal values

    Apply smoothing with various factors, and take the slope
    of the smoothed signal v. the smoothing factor.

    .. autosummary::
        ~compute
        ~slope
    """

    def __init__(self):
        """Constructor."""
        self.cache = {k: None for k in [0.2, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]}
        self.stats = StatsRegClass()
        self.trend = None
        self._computed = False

    def compute(self, reading):
        """
        (Re)compute the trend.

        Actually, reset the stats registers and load new values
        """
        self.stats.Clear()
        self._computed = False
        for factor in self.cache.keys():
            self.cache[factor] = smooth(reading, factor, self.cache[factor])
            self.stats.Add(1-factor, self.cache[factor])

    @property
    def slope(self):
        """Set the trend as the slope of smoothed v. (1-smoothing factor)."""
        if not self._computed and self.stats.count > 1:
            raw = self.stats.LinearRegression()[-1]
            self.trend = smooth(raw, TREND_SMOOTHING_FACTOR, self.trend)
            self._computed = True
        return self.trend

    def __str__(self):
        """Default string."""
        if self.slope is None:
            return "no trend yet"
        else:
            return "trend: {self.slope:.3f}"
