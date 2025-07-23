# SMHI Waterflow for Home Assistant

A custom component for Home Assistant that leverages SMHI (Swedish Meteorological and Hydrological Institute) data to create entities representing current and historical waterflow levels in Swedish rivers and streams.

This integration fetches data from SMHI's HydroNu service, providing:
- Current waterflow measurements
- Waterflow forecasts
- Historical waterflow data
- Precipitation data
- Reference flow levels (mean, mean low, mean high)

SMHI data covers Sweden and border areas, making this component primarily useful for Swedish locations.

## Installation

### Option 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → Click the three dots in the top right corner → Custom repositories
3. Add `https://github.com/Kaptensanders/smhi-waterflow` with category "Integration"
4. Click "Add"
5. Search for "SMHI Waterflow" in the Integrations tab and install it
6. Restart Home Assistant

### Option 2: Manual Installation

1. Download the latest release from the [GitHub repository](https://github.com/Kaptensanders/smhi-waterflow)
2. Extract the `custom_components/smhi_waterflow` directory into your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to Settings → Devices & Services
2. Click the "+ Add Integration" button
3. Search for "SMHI Waterflow"
4. Follow the configuration flow, providing:
   - Name: A unique name for this measurement location
   - X: Longitude coordinate
   - Y: Latitude coordinate
   - Subid: The measurement station ID

### Via configuration.yaml

```yaml
smhi-waterflow:
  - name: "My River"
    x: 15.123456
    y: 60.123456
    subid: 12345
```

## Finding Your Measurement Location

To find the correct coordinates and subid for your location:

1. Visit [SMHI's HydroNu service](https://vattenwebb.smhi.se/hydronu/)
2. Navigate to your area of interest on the map
3. Click on a measurement point (blue dot)
4. Note the coordinates and subid from the URL or information panel
5. Use these values in the configuration

## Available Sensors

For each configured location, the integration creates the following sensors:

- **[name] Waterflow**: Current and forecast waterflow data
- **[name] Precipitation**: Current and forecast precipitation data
- **[name] Waterflow History**: Historical waterflow data including averages, minimums, and maximums
- **[name] Info**: Reference flow levels (mq, mlq, mhq)

The data is updated every 6 hours.

## Lovelace Card

This integration includes a custom Lovelace card for visualizing the waterflow data. For installation and configuration instructions, please see the [card's README](./smhi-waterflow-card/README.md).

## Technical Details

- The integration uses SMHI's HydroNu API to fetch data
- Data is updated every 6 hours
- The integration requires pandas >= 2.0.0

## Troubleshooting

If you encounter issues:

1. Check that your coordinates and subid are correct
2. Verify that the SMHI API is accessible from your Home Assistant instance
3. Check the Home Assistant logs for any error messages
4. Ensure you have the required dependencies installed

## Support

For issues, feature requests, or contributions, please use the [GitHub repository](https://github.com/Kaptensanders/smhi-waterflow).