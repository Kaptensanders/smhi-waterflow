import pandas as pd
from datetime import datetime
from custom_components.waterflow.core.processor import SMHIProcessor
import pytest

def generate_leap_year_background():
    """Generate background data including Feb 29 from a leap year (2024)."""
    background = []
    for day in range(366):  # Leap year has 366 days
        timestamp = pd.Timestamp("2024-01-01") + pd.Timedelta(days=day)
        timestamp_ms = int(timestamp.timestamp() * 1000)
        values = [year + day for year in range(2022, 1990, -1)]
        background.append([timestamp_ms, values])
    return background

def test_process_background_leap_year_removal():
    """Test leap year handling with Feb 29 skipped and correct day shifting."""
    processor = SMHIProcessor()
    background = generate_leap_year_background()
    result = processor.process_background(background)

    for year, data in result["history"].items():
        assert len(data) == 365

        feb_28_index = 58  # Feb 28
        mar_1_index = 59   # March 1

        # Feb 28 must have valid data (still correctly mapped)
        assert data[feb_28_index] != -1

        # March 1 should also have valid data and correspond to the shifted day (after Feb 29 is skipped)
        assert data[mar_1_index] != -1

        # Ensure that no unexpected -1s in this region after Feb 28
        assert all(val != -1 for val in data[feb_28_index:mar_1_index+1])

def test_merge_series_positive():
    processor = SMHIProcessor()
    hindcast = {"data": [[1609459200000, 10]]}
    forecast = {"data": [[1609545600000, 20]]}
    result = processor.merge_series(hindcast, forecast)
    assert result["startindex"] is not None
    assert isinstance(result["firstdate"], datetime)
    assert isinstance(result["lastdate"], datetime)
    assert isinstance(result["data"], list)

def test_merge_series_empty():
    processor = SMHIProcessor()
    result = processor.merge_series({}, {})
    assert result["startindex"] is None
    assert result["firstdate"] is None
    assert result["lastdate"] is None
    assert isinstance(result["data"], list)
    assert result["data"] == []
