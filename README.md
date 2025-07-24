# SMHI Waterflow for Home Assistant

A custom component for Home Assistant that leverages SMHI (Swedish Meteorological and Hydrological Institute) data to create entities representing current, historical and forecast waterflow levels in Swedish rivers and streams.


This integration fetches data from SMHI's HydroNu service (https://vattenwebb.smhi.se/hydronu/), providing:
- Current waterflow measurements
- Waterflow forecasts
- Historical waterflow data
- Precipitation data
- Reference flow levels (mean, mean low, mean high)

SMHI data covers Sweden and border areas, making this component primarily useful for Swedish locations.

## Installation

### HACS (Recommended)

Find "SMHI Waterflow Integration" -> Install -> Restart Home Assistant

### Manual Installation

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
   - Subid: The measurement station ID, as found on https://vattenwebb.smhi.se/hydronu/

### Via configuration.yaml

```yaml
smhi_waterflow:
  - name: "My River"
    subid: 12345
```

## Finding Your Measurement Station id (subid)

To find the correct coordinates and subid for your location:

1. Visit [SMHI's HydroNu service](https://vattenwebb.smhi.se/hydronu/)
2. Navigate to your area of interest on the map
3. Click/Select a measurement in your river/stream
4. Note the point number from the top of the chart box and use this value as ´subid´
5. Use values in the configuration

## Available Sensors

For each configured location, the integration creates the following sensors:

- **[name] Waterflow**: Current and forecast waterflow data
- **[name] Precipitation**: Current and forecast precipitation data
- **[name] Waterflow History**: Historical waterflow data including averages, minimums, and maximums
- **[name] Info**: Reference flow levels (mq, mlq, mhq)

The data is updated every 6 hours.

## Lovelace Card

There is a companion Lovelace card for visualizing the waterflow data.
Find it at https://github.com/Kaptensanders/smhi-waterflow-card

## Troubleshooting

If you encounter issues:

1. Check that subid is correct and graph displays fine at https://vattenwebb.smhi.se/hydronu/
2. Verify that the SMHI API is accessible from your Home Assistant instance
3. Check the Home Assistant logs for any error messages
4. Create and issue or even better, Help fix it

## Support

For issues, feature requests, or contributions, please use the [GitHub repository](https://github.com/Kaptensanders/smhi-waterflow).

