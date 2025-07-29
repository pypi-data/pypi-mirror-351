"""Utilitly package for working with Pandas dataframes."""
__docformat__ = "google"
from collections import OrderedDict
import datetime
import functools
import re

from typing import (
    Any, Optional, Dict
)
import isodate
import pandas as pd
import pandas.tseries.frequencies as pd_freq

KEY_DEFAULT = ''


@pd.api.extensions.register_index_accessor("tsa")
class TsaIndexMetaAccessor:
    """Accessor added under the 'tsa' namespace to Indexes.

    Attaches additional timeseries functionality.
    A 'freq' property is added which will be taken from the index if available
    """

    def __init__(self, index):
        """Create the accessor."""
        self._index = index
        self._iso_freqstr = to_iso_freq(index.freq) if isinstance(index, pd.DatetimeIndex) else None
        self._table_attributes = {}

    @property
    def iso_freqstr(self) -> Optional[str]:
        """Get the ISO-8601 frequency string for the DataFrame's index.

        None if there is no frequency.
        """
        return self._iso_freqstr

    @property
    def pandas_freqstr(self) -> Optional[str]:
        """Get the pandas frequency string for the DataFrame's index.

        None if there is no frequency.
        """
        iso_freqstr = self.iso_freqstr
        if iso_freqstr is not None:
            return to_pandas_freqstr(iso_freqstr)
        return None

    @property
    def pandas_freq(self) -> Optional[pd_freq.DateOffset]:
        """Get the pandas frequency object for the DataFrame's index.

        None if there is no frequency.
        """
        iso_freqstr = self.iso_freqstr
        if iso_freqstr is not None:
            return to_pandas_freq(iso_freqstr)
        return None

    @property
    def window_length(self) -> Optional[pd.Timedelta]:
        """Get window length of this data series.

        If a frequency is present, this is the
        length of the half-open interval that extends
        1 freq unit after the last datapoint.
        """
        idx = self._index
        if isinstance(idx, pd.DatetimeIndex):
            if idx.size == 0:
                return None
            freq = self.pandas_freq
            if idx.size == 1 and freq is None:
                return None
            if freq is None:
                return idx[-1] - idx[0]
            else:
                return idx[-1] + freq - idx[0]
        return None

    @property
    def _from(self) -> Optional[pd.Timestamp]:
        """Get the `from` specification of this index."""
        idx = self._index
        if isinstance(idx, pd.DatetimeIndex) and idx.size > 0:
            return idx[0]
        return None

    @property
    def until(self) -> Optional[pd.Timestamp]:
        """Get the `until` specification of this index."""
        idx = self._index
        if isinstance(idx, pd.DatetimeIndex) and idx.size > 0:
            freq = self.pandas_freq
            if freq is not None:
                return idx[-1] + freq
            else:
                return idx[-1]
        return None

    @property
    def window_spec(self) -> Optional[Dict]:
        """Create the window specification that can be inferred."""
        idx = self._index
        if isinstance(idx, pd.DatetimeIndex) and idx.size > 0:
            spec = {
                "from": self._from,
                "until": self.until
            }
            window = self.window_length
            if window:
                spec["window"] = window
            freq = self.iso_freqstr
            if freq:
                spec["freq"] = freq
            return spec
        else:
            return None


@pd.api.extensions.register_series_accessor("tsa")
class TsaSeriesMetaAccessor:
    """Accessor added under the 'tsa' namespace to Series.

    Attaches additional timeseries functionality.
    """

    def __init__(self, series: pd.Series):
        """Create a TsaSeriesMetaAccessor."""
        self._series = series
        self._series_attributes: Dict[str, Any] = {}

    @property
    def table_attributes(self) -> Dict:
        """Get additional attributes on table level.

        E.g. column metadata that is the same for each column.
        """
        return self._series_attributes

    @property
    def iso_freqstr(self) -> Optional[str]:
        """Get the ISO-8601 frequency string for the DataFrame's index.

        None if there is no frequency.
        """
        return self._series.index.tsa.iso_freqstr

    @property
    def pandas_freqstr(self) -> Optional[str]:
        """Get the pandas frequency string for the DataFrame's index.

        None if there is no frequency.
        """
        return self._series.index.tsa.pandas_freqstr

    @property
    def pandas_freq(self) -> Optional[pd_freq.DateOffset]:
        """Get the pandas frequency object for the DataFrame's index.

        None if there is no frequency.
        """
        return self._series.index.tsa.pandas_freq

    @property
    def window_length(self) -> Optional[pd.Timedelta]:
        """Get window length of this data series."""
        return self._series.index.tsa.window_length

    @property
    def _from(self) -> Optional[pd.Timestamp]:
        """Get the `from` specification of this Series."""
        return self._series.index.tsa._from  # pylint: disable=protected-access

    @property
    def until(self) -> Optional[pd.Timestamp]:
        """Get the `until` specification of this Series."""
        return self._series.index.tsa.until

    @property
    def window_spec(self) -> Dict:
        """Get the window specification of this Series."""
        return self._series.index.tsa.window_spec


@pd.api.extensions.register_dataframe_accessor("tsa")
class TsaDataframeMetaAccessor:
    """TSA accessor added under the 'tsa' namespace to Dataframes.

    Attaches additional timeseries functionality.
    """

    def __init__(self, df):
        """Create a TsaDataframeMetaAccessor."""
        self._df = df
        self._table_attributes = OrderedDict()

    @property
    def table_attributes(self):
        """Additional attributes on table level.

        e.g. column metadata that is the same for each column.
        """
        return self._table_attributes

    @property
    def iso_freqstr(self) -> Optional[str]:
        """Get the ISO-8601 frequency string for the DataFrame's index.

        None if there is no frequency.
        """
        return self._df.index.tsa.iso_freqstr

    @property
    def pandas_freqstr(self) -> Optional[str]:
        """Get the pandas frequency string for the DataFrame's index.

        None if there is no frequency.
        """
        return self._df.index.tsa.pandas_freqstr

    @property
    def pandas_freq(self) -> Optional[pd_freq.DateOffset]:
        """Get the pandas frequency object for the DataFrame's index.

        None if there is no frequency.
        """
        return self._df.index.tsa.pandas_freq

    @property
    def window_length(self) -> Optional[str]:
        """Get window length of this DataFrame as an iso 8601 period string."""
        return self._df.index.tsa.window_length

    @property
    def _from(self):
        """Get the `from` specification of this DataFrame."""
        return self._df.index.tsa._from  # pylint: disable=protected-access

    @property
    def until(self):
        """Get the `until` specification of this DataFrame."""
        return self._df.index.tsa.until

    @property
    def window_spec(self):
        """Get the window_spec specification of this DataFrame."""
        return self._df.index.tsa.window_spec  # pylint: disable=protected-access


def to_pandas_freq(freq: Any) -> pd_freq.DateOffset:
    """Convert a frequency or interval to a pandas DateOffset."""
    if freq is None:
        return None
    if isinstance(freq, str) and 'P' in freq:
        freq = isodate.parse_duration(freq)
    if isinstance(freq, isodate.Duration):
        # If we've got a duration, we need to root it somewhere to
        # convert it into a frequency.
        # Best would be to root it at the context time,
        # but that isn't always available, so we just use the unix epoch
        # to have a consistent answer for the same question.
        freq = freq.totimedelta(start=datetime.datetime(1970, 1, 1, 0, 0, 0))
    return pd_freq.to_offset(freq)


def to_pandas_freqstr(freq: Any) -> Optional[str]:
    """Convert a frequency or interval to a pandas frequency string."""
    if freq is None:
        return None
    return to_pandas_freq(freq).freqstr


def _iso_format(postfix, prefix='P', scale=1, value=1):
    if scale != 1:
        value = int(value) * scale
    return "{}{}{}".format(prefix, value, postfix)


def _iso_formatter(postfix, prefix='P', scale=1):
    return functools.partial(_iso_format, postfix, prefix=prefix, scale=scale)


ISO_PERIOD_FORMAT_BY_PANDAS_UNIT = {
    'B': _iso_formatter('D'),
    'C': _iso_formatter('D'),
    'D': _iso_formatter('D'),

    'W': _iso_formatter('W'),

    'M': _iso_formatter('M'),
    'BM': _iso_formatter('M'),
    'CBM': _iso_formatter('M'),
    'MS': _iso_formatter('M'),
    'BMS': _iso_formatter('M'),
    'CBMS': _iso_formatter('M'),

    'SM': _iso_formatter('M', scale=0.5),
    'SMS': _iso_formatter('M', scale=0.5),

    'Q': _iso_formatter('M', scale=3),
    'BQ': _iso_formatter('M', scale=3),
    'QS': _iso_formatter('M', scale=3),
    'BQS': _iso_formatter('M', scale=3),

    'A': _iso_formatter('Y'),
    'Y': _iso_formatter('Y'),
    'BA': _iso_formatter('Y'),
    'BY': _iso_formatter('Y'),
    'AS': _iso_formatter('Y'),
    'YS': _iso_formatter('Y'),
    'BAS': _iso_formatter('Y'),
    'BYS': _iso_formatter('Y'),

    'BH': _iso_formatter('H', 'PT'),
    'H': _iso_formatter('H', 'PT'),

    'T': _iso_formatter('M', 'PT'),
    'min': _iso_formatter('M', 'PT'),

    'S': _iso_formatter('S', 'PT'),

    'L': _iso_formatter('S', 'PT', 0.001),
    'ms': _iso_formatter('S', 'PT', 0.001),
    'U': _iso_formatter('S', 'PT', 0.000001),
    'us': _iso_formatter('S', 'PT', 0.000001),
    'N': _iso_formatter('S', 'PT', 0.000000001),
}


def to_iso_freq(freq, lsnr=None) -> Optional[str]:
    """Convert a frequency or interval to an ISO-8601 Duration."""
    if freq is None:
        return None
    if isinstance(freq, str) and 'P' in freq:
        return freq
    freq = to_pandas_freqstr(freq)
    # didnt find a good way, so like this:
    if '-' in freq:
        # remove anchoring part
        freq = freq.split('-')[0]
    m = re.search(r'(\d+)?([BCDWMSQAYHTminusLUN]+)', freq)
    if m is None:
        if lsnr is not None:
            lsnr.warning("could not convert frequency to isoformat: %s", freq)
        return freq
    freq_n = m.group(1)
    freq_n = '1' if freq_n is None else freq_n
    freq_unit = m.group(2)

    if freq_unit in ISO_PERIOD_FORMAT_BY_PANDAS_UNIT:
        return ISO_PERIOD_FORMAT_BY_PANDAS_UNIT[freq_unit](value=freq_n)
    else:
        if lsnr is not None:
            lsnr.info("could not convert frequency to isoformat: %s", freq)
        return freq
