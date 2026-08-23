#!/usr/bin/env python3

"""Launch the Phoenix ArduPlane SITL model."""

# AP_FLAKE8_CLEAN

import argparse
import os
from pathlib import Path


PROFILES = {
    "camera": ("phoenix-camera.json", None),
    "camera-conservative": ("phoenix-camera-conservative.json", None),
    "starlink": ("phoenix-starlink.json", "PhoenixSITL-starlink.parm"),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch Phoenix SITL and pass unrecognised arguments to sim_vehicle.py.",
    )
    parser.add_argument(
        "--profile",
        choices=PROFILES,
        default="camera",
        help="payload model to use (default: camera)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="disable the debugger and MAVProxy GUI windows and skip rebuilding",
    )
    parser.add_argument(
        "-N",
        "--no-rebuild",
        action="store_true",
        help="skip rebuilding ArduPlane before launch",
    )
    return parser.parse_known_args()


def main():
    args, sim_vehicle_args = parse_args()
    phoenix_dir = Path(__file__).resolve().parent
    ardupilot_dir = phoenix_dir.parent.parent
    sim_vehicle = ardupilot_dir / "Tools" / "autotest" / "sim_vehicle.py"
    model_name, profile_param_name = PROFILES[args.profile]

    required_files = [sim_vehicle, phoenix_dir / model_name, phoenix_dir / "PhoenixSITL.parm"]
    if profile_param_name is not None:
        required_files.append(phoenix_dir / profile_param_name)
    missing_files = [str(path) for path in required_files if not path.is_file()]
    if missing_files:
        raise SystemExit("Missing required file(s): %s" % ", ".join(missing_files))

    # AP_Filesystem resolves SITL JSON model names relative to the process
    # directory, so run from here and pass the model as a basename.
    os.chdir(phoenix_dir)

    command = [str(sim_vehicle)]
    if not args.headless:
        command.extend(["-D", "-G"])
    command.extend([
        "-f",
        "quadplane:%s" % model_name,
        "--aircraft",
        "PhoenixSITL-headless" if args.headless else "PhoenixSITL",
        "-L",
        "SpringValley2",
    ])
    if args.headless or args.no_rebuild:
        command.append("-N")
    if args.headless:
        command.append("--no-extra-ports")
    else:
        command.append("--console")
    command.append("--add-param-file=%s" % (phoenix_dir / "PhoenixSITL.parm"))
    if profile_param_name is not None:
        command.append("--add-param-file=%s" % (phoenix_dir / profile_param_name))
    command.extend(sim_vehicle_args)

    environment = os.environ.copy()
    if args.headless:
        # Avoid the persistent xterm created by run_in_terminal_window.sh.
        environment["SITL_RITW_TERMINAL"] = "bash"
    os.execvpe(command[0], command, environment)


if __name__ == "__main__":
    main()
