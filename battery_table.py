#!/usr/bin/env python3

"""Generate an HTML battery-by-waypoint comparison from DataFlash logs."""

# AP_FLAKE8_CLEAN

import argparse
import html
from pathlib import Path

from pymavlink import mavutil


PARAMETER_NAMES = ("AIRSPEED_CRUISE", "SIM_WIND_SPD", "SIM_WIND_DIR")


def format_parameter(value):
    if value is None:
        return "not logged"
    return "%g" % value


def load_flight(path):
    parameters = {}
    waypoint_battery = {}
    battery_remaining = None
    connection = mavutil.mavlink_connection(str(path))

    try:
        while True:
            message = connection.recv_match(type=["BAT", "MISE", "PARM"])
            if message is None:
                break

            data = message.to_dict()
            message_type = message.get_type()
            if message_type == "PARM" and data.get("Name") in PARAMETER_NAMES:
                parameters[data["Name"]] = data.get("Value")
            elif message_type == "BAT":
                instance = data.get("Inst", data.get("Instance", data.get("I", 0)))
                remaining = data.get("RemPct")
                if instance == 0 and remaining is not None and 0 <= remaining <= 100:
                    battery_remaining = remaining
            elif message_type == "MISE" and battery_remaining is not None:
                # MISE is logged when a mission item becomes active.  The most
                # recent BAT sample is therefore the battery state at that item.
                waypoint_battery.setdefault(int(data["CNum"]), battery_remaining)
    finally:
        connection.close()

    if not waypoint_battery:
        raise ValueError("no mission-item transitions with BAT[0].RemPct data found")

    return {
        "path": path,
        "parameters": parameters,
        "waypoints": waypoint_battery,
    }


def make_html(flights):
    differing_parameters = {
        name
        for name in PARAMETER_NAMES
        if len({flight["parameters"].get(name) for flight in flights}) > 1
    }
    all_waypoints = sorted({
        waypoint
        for flight in flights
        for waypoint in flight["waypoints"]
    })

    legend_items = []
    for flight_number, flight in enumerate(flights, 1):
        parameter_items = []
        for name in PARAMETER_NAMES:
            css_class = ' class="different"' if name in differing_parameters else ""
            value = format_parameter(flight["parameters"].get(name))
            parameter_items.append(
                "<span%s>%s=%s</span>" % (
                    css_class,
                    html.escape(name),
                    html.escape(value),
                )
            )
        legend_items.append(
            "<li><strong>Flight%d</strong> &mdash; %s<br>%s</li>" % (
                flight_number,
                html.escape(str(flight["path"])),
                ", ".join(parameter_items),
            )
        )

    headings = "".join(
        "<th scope=\"col\">Flight%d</th>" % flight_number
        for flight_number in range(1, len(flights) + 1)
    )
    rows = []
    for waypoint in all_waypoints:
        cells = []
        for flight in flights:
            remaining = flight["waypoints"].get(waypoint)
            cells.append("<td>%s</td>" % ("&mdash;" if remaining is None else "%g%%" % remaining))
        rows.append(
            "<tr><th scope=\"row\">%d</th>%s</tr>" % (waypoint, "".join(cells))
        )

    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Battery Remaining by Waypoint</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; color: #1f2937; }
    h1 { margin-bottom: 0.4rem; }
    .legend { background: #f3f4f6; border-radius: 0.4rem; padding: 1rem 2rem; }
    .legend li { margin: 0.5rem 0; }
    .different { color: #075985; font-weight: 700; }
    table { border-collapse: collapse; margin-top: 1.5rem; min-width: 32rem; }
    th, td { border: 1px solid #cbd5e1; padding: 0.45rem 0.8rem; text-align: right; }
    thead th { background: #e2e8f0; }
    tbody th { background: #f8fafc; }
    th:first-child { text-align: left; }
  </style>
</head>
<body>
  <h1>Battery Remaining by Waypoint</h1>
  <p>Highlighted parameter values differ between flights.</p>
  <ul class="legend">
    %s
  </ul>
  <table>
    <thead><tr><th scope="col">Waypoint</th>%s</tr></thead>
    <tbody>
      %s
    </tbody>
  </table>
</body>
</html>
""" % ("\n    ".join(legend_items), headings, "\n      ".join(rows))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="DataFlash .bin logs to compare")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("battery_table.html"),
        help="output HTML file (default: battery_table.html)",
    )
    return parser.parse_args(), parser


def main():
    args, parser = parse_args()
    flights = []
    for path in args.logs:
        if not path.is_file():
            parser.error("log does not exist: %s" % path)
        try:
            flights.append(load_flight(path))
        except (OSError, ValueError) as error:
            parser.error("%s: %s" % (path, error))

    args.output.write_text(make_html(flights), encoding="utf-8")
    print("Wrote %s" % args.output)


if __name__ == "__main__":
    main()
