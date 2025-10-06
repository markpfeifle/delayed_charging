import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import NamedTuple


class TimeSeries(NamedTuple):
    start_time: datetime
    end_time: datetime
    resolution: str
    data_points: list[tuple[datetime, float]]


def parse_datetime(dt_str: str) -> datetime:
    """Convert ISO 8601 datetime string to datetime object."""
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M%z")


def parse_resolution(res_str: str) -> timedelta:
    """Convert ISO 8601 duration string to timedelta."""
    # match = re.match(r"PT((\d+)H)?((\d+)M)?((\d+)S)?", res_str)
    if res_str == "PT15M":
        return timedelta(minutes=15)
    elif res_str == "PT60M":
        return timedelta(hours=1)
    else:
        raise ValueError(f"Unsupported resolution: {res_str}")


def parse_xml_file(filepath: str) -> list[TimeSeries]:
    """Parse the XML file and return a list of TimeSeries objects."""

    tree = ET.parse(filepath)
    root = tree.getroot()

    tag = root.tag
    if tag.startswith("{"):
        namespace_uri = tag[1:].split("}")[0]
        ns = {"md": namespace_uri}
        ET.register_namespace("", namespace_uri)
    else:
        ns = None

    result: list[TimeSeries] = []

    # Find all TimeSeries elements
    for ts in root.findall(".//md:TimeSeries", ns):
        # Get Period information
        period = ts.find(".//md:Period", ns)
        if period is None:
            continue
        time_interval = period.find("md:timeInterval", ns)
        if time_interval is None:
            continue
        resolution_element = period.find("md:resolution", ns)
        if resolution_element is None:
            continue

        start_time_element = time_interval.find("md:start", ns)
        end_time_element = time_interval.find("md:end", ns)
        if start_time_element is None or end_time_element is None:
            continue

        start_time = parse_datetime(start_time_element.text or "")
        end_time = parse_datetime(end_time_element.text or "")
        resolution = resolution_element.text or ""

        # Parse all points
        points: list[tuple[datetime, float]] = []
        resolution_delta = parse_resolution(resolution)

        for point in period.findall("md:Point", ns):
            position_element = point.find("md:position", ns)
            price_element = point.find("md:price.amount", ns)
            if position_element is None or price_element is None:
                continue
            pos = position_element.text
            if pos is None or not pos.isdigit():
                continue
            position = int(pos)
            pri = price_element.text
            try:
                price = float(pri or "None")
            except ValueError:
                continue

            # Calculate actual datetime for this point
            point_time = start_time + (position - 1) * resolution_delta
            points.append((point_time, price))

        # Sort points by timestamp
        points.sort(key=lambda x: x[0])

        # Create TimeSeries object
        ts_obj = TimeSeries(start_time=start_time, end_time=end_time, resolution=resolution, data_points=points)
        result.append(ts_obj)

    return result


def main():
    # Example usage
    filepath = "results.xml"
    timeseries_list = parse_xml_file(filepath)

    # Print results
    for i, ts in enumerate(timeseries_list, 1):
        print(f"\nTimeSeries {i}:")
        print(f"Period: {ts.start_time} to {ts.end_time}")
        print(f"Resolution: {ts.resolution}")
        print("First 3 data points:")
        for dt, price in ts.data_points[:3]:
            print(f"  {dt}: {price:.2f} EUR/MWH")
        print(f"Total points: {len(ts.data_points)}")


if __name__ == "__main__":
    main()
