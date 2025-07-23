import asyncio
import argparse
import logging
import json
import aiohttp
from custom_components.smhi_waterflow.core.processor import SMHIProcessor

class StandaloneSMHIClient:
    BASE_URL = "https://vattenwebb.smhi.se/hydronu/"

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SMHIWaterflowIntegration/1.0; +https://github.com/your-repo)"
        }

    async def fetch_data(self, subid: str, x: str, y: str) -> dict:
        async with aiohttp.ClientSession() as session:
            point_url = f"{self.BASE_URL}data/point?x={x}&y={y}"
            self.logger.debug(f"Fetching point data: {point_url}")
            async with session.get(point_url, headers=self.headers) as resp:
                resp.raise_for_status()
                point_data = await resp.json()

            production_time = point_data.get("productionTime")
            if not production_time:
                raise ValueError("Missing productionTime in point data")

            chart_url = f"{self.BASE_URL}data/chart?subid={subid}&productionTime={production_time}"
            self.logger.debug(f"Fetching chart data: {chart_url}")
            async with session.get(chart_url, headers=self.headers) as resp:
                resp.raise_for_status()
                chart_data = await resp.json()

        return {
            "point_data": point_data,
            "chart_data": chart_data,
            "production_time": production_time
        }

async def main(subid: str, x: str, y: str):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("waterflow.runner")

    client = StandaloneSMHIClient(logger)
    result = await client.fetch_data(subid, x, y)

    processor = SMHIProcessor()
    processed = processor.process_data(result["chart_data"])

    with open("chart_data.json", "w", encoding="utf-8") as f:
        json.dump(result["chart_data"], f, indent=2)
    with open("processed_data.json", "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    print(f"\nProduction time used: {result['production_time']}")
    print("Results saved to 'chart_data.json' and 'processed_data.json'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and process SMHI Waterflow data")
    parser.add_argument("--subid", required=True, help="SMHI Subid")
    parser.add_argument("--x", required=True, help="X coordinate")
    parser.add_argument("--y", required=True, help="Y coordinate")
    args = parser.parse_args()

    asyncio.run(main(args.subid, args.x, args.y))
