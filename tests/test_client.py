import pytest
import aiohttp
import asyncio
from unittest.mock import patch, MagicMock
from custom_components.smhi_waterflow.core.client import SMHIClient

# Mock constants to avoid dependency on const.py during tests
@pytest.fixture(autouse=True)
def mock_constants(monkeypatch):
    """Mock constants from const.py for testing."""
    monkeypatch.setattr(SMHIClient, "BASE_URL", "https://test.example.com/")
    monkeypatch.setattr("custom_components.smhi_waterflow.core.client.USER_AGENT", "Test User Agent")
    monkeypatch.setattr("custom_components.smhi_waterflow.core.client.DEFAULT_TIMEOUT", 10)
    monkeypatch.setattr("custom_components.smhi_waterflow.core.client.MAX_RETRIES", 2)
    monkeypatch.setattr("custom_components.smhi_waterflow.core.client.RETRY_DELAY", 1)

@pytest.mark.asyncio
async def test_fetch_data_success(monkeypatch):
    """Test successful fetching with mocked responses."""
    subid = "14054"
    x = "374751.999939161"
    y = "6795215.999998116"

    point_response = {"productionTime": "202507050800"}
    chart_response = {"subid": int(subid), "mq": 10}

    async with aiohttp.ClientSession() as session:
        client = SMHIClient(session)

        class MockResponse:
            def __init__(self, json_data):
                self._json = json_data
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            def raise_for_status(self): pass
            async def json(self): return self._json

        def mock_get(url, *args, **kwargs):
            if "point" in url:
                return MockResponse(point_response)
            elif "chart" in url:
                return MockResponse(chart_response)
            raise ValueError("Unexpected URL")

        monkeypatch.setattr(session, "get", mock_get)
        result = await client.fetch_data(subid, x, y)

    assert result["production_time"] == "202507050800"
    assert result["chart_data"]["mq"] == 10

@pytest.mark.asyncio
async def test_fetch_with_retry_success_after_retry(monkeypatch):
    """Test successful fetching after a retry."""
    async with aiohttp.ClientSession() as session:
        client = SMHIClient(session)
        
        # Mock sleep to avoid waiting in tests
        async def mock_sleep(seconds):
            return None
        monkeypatch.setattr(asyncio, "sleep", mock_sleep)
        
        # Create a counter to track retry attempts
        call_count = 0
        
        class MockResponse:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            def raise_for_status(self): pass
            async def json(self): return {"test": "data"}
        
        def mock_get(url, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # Fail on first attempt, succeed on second
            if call_count == 1:
                raise aiohttp.ClientError("Test error")
            return MockResponse()
        
        monkeypatch.setattr(session, "get", mock_get)
        
        result = await client._fetch_with_retry("https://test.url", "test data")
        
        assert result == {"test": "data"}
        assert call_count == 2  # Verify it retried once

@pytest.mark.asyncio
async def test_custom_timeout(monkeypatch):
    """Test that custom timeout is used when provided."""
    async with aiohttp.ClientSession() as session:
        custom_timeout = 20
        client = SMHIClient(session, timeout=custom_timeout)
        
        # Create a mock to capture kwargs
        kwargs_captured = {}
        
        class MockResponse:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            def raise_for_status(self): pass
            async def json(self): return {"test": "data"}
        
        def mock_get(url, **kwargs):
            nonlocal kwargs_captured
            kwargs_captured = kwargs
            return MockResponse()
        
        monkeypatch.setattr(session, "get", mock_get)
        
        await client._fetch_with_retry("https://test.url", "test data")
        
        # Verify timeout was passed correctly
        assert "timeout" in kwargs_captured
        assert kwargs_captured["timeout"] == custom_timeout
@pytest.mark.asyncio
async def test_fetch_data_missing_production_time(monkeypatch):
    """Test missing productionTime in point response (error case)."""
    subid = "14054"
    x = "374751.999939161"
    y = "6795215.999998116"

    async with aiohttp.ClientSession() as session:
        client = SMHIClient(session)

        class MockResponse:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            def raise_for_status(self): pass
            async def json(self): return {}

        def mock_get(url, *args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(session, "get", mock_get)

        with pytest.raises(ValueError, match="Missing productionTime"):
            await client.fetch_data(subid, x, y)

@pytest.mark.asyncio
async def test_fetch_data_http_error(monkeypatch):
    """Test HTTP error during point data fetch."""
    subid = "14054"
    x = "374751.999939161"
    y = "6795215.999998116"

    async with aiohttp.ClientSession() as session:
        client = SMHIClient(session)

        class MockResponse:
            async def __aenter__(self): return self
            async def __aexit__(self, exc_type, exc_val, exc_tb): pass
            def raise_for_status(self):
                # Create a proper mock for request_info
                request_info = MagicMock()
                request_info.real_url = "https://test.example.com"
                raise aiohttp.ClientResponseError(
                    request_info=request_info,
                    history=None,
                    status=500,
                    message="Error"
                )
            async def json(self): return {}

        def mock_get(url, *args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(session, "get", mock_get)

        with pytest.raises(aiohttp.ClientResponseError):
            await client.fetch_data(subid, x, y)
