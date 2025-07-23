import pytest
import aiohttp
import json
import copy
from datetime import datetime
from pathlib import Path
from custom_components.smhi_waterflow.core.client import SMHIClient
from custom_components.smhi_waterflow.core.processor import SMHIProcessor

def convert_datetime_to_timestamp(obj):
    """Convert datetime objects to timestamps (milliseconds since epoch) for JSON serialization."""
    if isinstance(obj, dict):
        return {key: convert_datetime_to_timestamp(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetime_to_timestamp(item) for item in obj]
    elif isinstance(obj, datetime):
        return int(obj.timestamp() * 1000)  # Convert to milliseconds
    else:
        return obj

@pytest.mark.asyncio
async def test_live_smhi_fetch_and_process():
    """Live E2E test: Fetch real SMHI data, save responses, process, and verify."""
    subid = "14054"

    async with aiohttp.ClientSession() as session:
        client = SMHIClient(session)
        result = await client.fetch_data(subid)

    processor = SMHIProcessor()
    processed = processor.process_data(result["chart_data"])

    # Prepare output dir
    output_dir = Path("tests/test_outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save outputs
    (output_dir / "chart_data.json").write_text(json.dumps(result["chart_data"], indent=2), encoding="utf-8")
    
    # Convert datetime objects to timestamps for JSON serialization
    json_serializable_processed = convert_datetime_to_timestamp(copy.deepcopy(processed))
    (output_dir / "live_processed_data.json").write_text(json.dumps(json_serializable_processed, indent=2), encoding="utf-8")

    # Minimal assertions
    assert "production_time" in result
    assert "waterflow" in processed
    assert "precipitation" in processed
    assert "waterflow_history" in processed

    print(f"\n[Test] Production time: {result['production_time']}")
    print(f"[Test] Data saved to {output_dir}/")

    # ✅ Check July 1 Mapping (Index 181 in 365-day calendar)
    july_1_index = 181
    print("\n[Test] Verifying July 1 values in waterflow_history:")
    for year, values in processed["waterflow_history"]["history"].items():
        val = values[july_1_index]
        print(f"  {year} → July 1 value: {val}")
