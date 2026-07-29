#!/bin/bash
# Interactive Phoenix SITL - MAVProxy console + map, gdb attached.
#
# Vehicle tuning, battery model and environment come from PhoenixSITL.parm,
# which sim_vehicle.py passes to the binary as defaults. Values already saved
# in eeprom.bin take precedence, so to pick up edits to the .parm file:
#
#     rm eeprom.bin && ./go.sh
#     wp load orroral4.txt
#
# PhoenixSITL.parm sets SIM_SPEEDUP 100. For interactive flying, either edit it
# or type "speedup 1" at the MAVProxy prompt.
cd "$(dirname "$0")"

exec ../../Tools/autotest/sim_vehicle.py \
     -D -G \
     -f quadplane \
     --aircraft PhoenixSITL \
     --console \
     -L SpringValley2 \
     --add-param-file=PhoenixSITL.parm \
     "$@"
