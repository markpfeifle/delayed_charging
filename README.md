# Delayed Charging

A Home Assistant custom integration that helps optimize battery charging based on electricity spot market prices. Starting in 2025, newly installed photovoltaic systems in Germany will receive zero feed-in remuneration during periods of negative electricity prices. This integration provides sensor entities to help you optimize battery charging timing to maximize economic benefits.

## Background

Typically, home battery systems start charging immediately when solar production begins in the morning. While this seems intuitive, it may not be economically optimal:

- Morning hours often have positive electricity prices, allowing profitable grid feed-in
- By noon/afternoon, prices frequently turn negative due to peak solar production
- If your battery is already full from morning charging, you can't store the excess energy during negative price periods
- Starting 2025, feeding solar power to the grid during negative price periods will yield zero compensation in many newly built setups

This integration helps you delay battery charging to coincide with negative price periods, maximizing the economic value of your PV system.

## Installation

1. Copy the `custom_components/delayed_charging` folder to your Home Assistant configuration directory
2. Restart Home Assistant
3. Add the integration through the UI: Settings -> Devices & Services -> Add Integration -> Delayed Charging

## Configuration

The integration offers two configuration options:

- **Country ID**: Select your market area (default: Germany/Luxembourg).
- **Price Threshold**: The price threshold (in €/MWh) below which charging should be initiated (default: 0). Set this to 0 to charge only during negative prices, or higher if you want to charge during low-price periods.

## Provided Entities

The integration creates the following entities:

### Current Price Sensor
- Entity ID: `sensor.current_price`
- Shows the current electricity price in €/MWh
- Includes historical price data for the day in its attributes (can be potentially used for custom visualization)

### Delayed Charging Start
- Entity ID: `sensor.delayed_charging_start`
- Timestamp indicating when charging should begin based on your threshold
- Returns `null` if no suitable charging period is found today (shown as Unknown in the GUI)

### Delayed Charging Active
- Entity ID: `binary_sensor.delayed_charging_active`
- Indicates whether the charging delay should be enabled on the current day
- `True` if the prices drop below the threshold today, `false` otherwise

## Example Automation Concept

The integration's sensors could be used to control battery charging through three basic automations:

1. Early morning check (5:00 AM) - Disables charging if negative prices are expected:
   ```pseudocode
   IF binary_sensor.delayed_charging_active is ON THEN
     set_battery_charging_power(0)
   ```

2. Optimal charging start - Enables charging when prices turn negative:
   ```pseudocode
   WHEN time equals sensor.delayed_charging_start AND
        binary_sensor.delayed_charging_active is ON THEN
     set_battery_charging_power(maximum_power)
   ```

3. Safety fallback (16:00) - Ensures battery gets charged even if previous automations fail:
   ```pseudocode
   set_battery_charging_power(maximum_power)
   ```

## Notes

- Make sure your battery control automations include additional safety checks (e.g., battery state of charge limits)
- The integration updates price data every 2 minutes from the SMARD API
- Time values are in your system's timezone

