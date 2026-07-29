#!/bin/bash
# Headless variant of go.sh - no MAVProxy console/map windows, no gdb.
# Same vehicle, params and location as go.sh; safe to run without disturbing
# the desktop.
#
#   ./go-headless.sh                                  # MAVProxy on stdio
#   ./go-headless.sh -m "--daemon --out 127.0.0.1:14560"   # detached, scriptable
#
# Vehicle tuning, battery model and environment come from PhoenixSITL.parm.
# Those are applied as defaults, so eeprom.bin wins where it has a value. To
# start from the .parm file alone:
#
#     rm eeprom.bin && ./go-headless.sh
#     wp load orroral4.txt
#
# Differences from go.sh:
#   -G  (gdb)      dropped  - opened a debugger window
#   --console      dropped  - MAVProxy console window
#   mavinit.scr    bypassed via --aircraft PhoenixSITL-headless (it loads
#                            map/horizon/console)
#   added: -N (no rebuild) and --no-extra-ports for a quiet start
cd "$(dirname "$0")"

# sim_vehicle launches the ArduPlane binary via run_in_terminal_window.sh, which
# spawns an "xterm -hold" per run even with --console and -G dropped. -hold means
# the window survives the binary exiting, so repeated runs leave stray xterms
# lying around. SITL_RITW_TERMINAL overrides that: run the generated script with
# plain bash and no terminal at all.
export SITL_RITW_TERMINAL="bash"

exec ../../Tools/autotest/sim_vehicle.py \
     -f quadplane \
     --aircraft PhoenixSITL-headless \
     -L SpringValley2 \
     -N \
     --no-extra-ports \
     --add-param-file=PhoenixSITL.parm \
     "$@"
