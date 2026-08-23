# Phoenix camera-payload SITL calibration

Calibration flight: `log5.bin`, 2026-08-21. Camera-free reference:
`log2.bin`, 2026-07-27. The camera-equipped aircraft was weighed at 11.84 kg;
the camera payload adds 0.65 kg, so the applicable camera-free mass is 11.19 kg.

Run the reproducible fit with:

```bash
python3 ../../Tools/autotest/phoenix_payload_fit.py \
    --baseline-mass 11.19 --payload-mass 11.84 \
    ~/project/UAV/Phoenix/logs/2026-07-27/log2.bin \
    ~/project/UAV/Phoenix/logs/2026-08-21/log5.bin
```

## Result

The fit uses the camera-free idle glide to establish the drag polar, then
calibrates thrust against the two forward ESC RPM streams. Using RPM instead of
throttle matters because the two flights have different pack voltage. The
camera-flight fit gives:

| Quantity | Camera-free | Camera fitted | Change |
|---|---:|---:|---:|
| Mass | 11.19 kg | 11.84 kg | +0.65 kg |
| Parasitic drag coefficient | 0.068 | 0.071 | +0.002 |
| Drag at 20 m/s EAS | 12.44 N | 13.29 N | +0.85 N (+6.8%) |
| Non-propulsive current | baseline model | baseline about +1.2 A | about +53 W at 46 V |

The parasitic-drag estimate is noisy because log5 contains no idle glide and
mostly flies a compact repeating circuit. As a cross-check, the preceding
camera flight (`log4.bin`) gives Cd0 0.075 and +1.30 N total drag at 20 m/s.
The selected log5 values therefore should not be treated as better than about
plus or minus 0.5 N. For operational reserve planning, run a second case with
`c_drag_p` raised from 0.071 to 0.075.

The active `phoenix-camera.json` profile carries the measured mass and central
drag estimate. `PhoenixSITL.parm` adds a 1.16 A payload load (central to the
log5 fit and log4 cross-check) to the existing forward-motor current curve.
`go.py` selects that profile by default. Select the upper drag cross-check
with:

```bash
./go.py --profile camera-conservative --headless -w
```

To reproduce the Starlink-only configuration from `orroral4-log2.bin`, select
the `starlink` profile. It uses the measured 11.19 kg camera-free mass, Cd0
0.068, and the original 1.83 A fixed electrical load:

```bash
./go.py --profile starlink -w
```

The `-w` wipes SITL parameter storage so the selected profile's electrical
overlay takes effect; back up `eeprom.bin` first if it contains settings you
want to retain. After MAVProxy starts, load `orroral4.txt` and verify the
profile before arming:

```text
wp load orroral4.txt
param show SIM_FWD_I_FIXED
```

The Starlink-only value must be `1.83`; the camera profiles must show `2.99`.

### Starlink-only validation

Battery comparisons must use the arm-to-disarm change in `BAT.CurrTot` and
`BAT.EnrgTot`, not their raw final values. The real aircraft had already used
81.5 Wh when it armed, whereas the original SITL run had used 31.4 Wh.

The measured wind vector averaged 4.05 m/s from 344 degrees, but its magnitude
varied from 4.41 m/s at p50 to 6.47 m/s at p95. SITL's high-frequency turbulence
did not reproduce the resulting mission-time penalty. A constant 5.7 m/s from
344 degrees is the effective replay wind for this particular flight:

```text
param set SIM_WIND_SPD 5.7
param set SIM_WIND_DIR 344
param set SIM_WIND_TURB 0.1
```

The original `96.37*throttle^4.48 + 1.83` electrical curve was fitted to three
selected throttle/current operating points. In the complete mission replay it
under-predicted the climb and level-flight energy. The Starlink parameter
overlay instead fits the throttle curve to the measured climb, level and
descent phase currents, while retaining the original 1.83 A fixed load.

| Result | Real `orroral4-log2.bin` | Updated Starlink SITL | Error |
|---|---:|---:|---:|
| Arm-to-disarm time | 93.96 min | 93.67 min | -0.29 min (-0.3%) |
| Battery used | 17.444 Ah | 17.022 Ah | -0.422 Ah (-2.4%) |
| Energy used | 806.6 Wh | 801.7 Wh | -4.9 Wh (-0.6%) |
| Reported percentage change | 44 points | 43 points | -1 point |

The whole-flight agreement is better than the phase agreement. SITL used 18.3
Wh less in level flight and 14.4 Wh more in descent; its mean level-flight
current was 10.16 A versus 10.57 A measured. A mission with a materially
different climb/descent mix can therefore differ by more than the 0.6% total
above. For a predominantly level long mission, allow at least the roughly 4%
level-current shortfall in addition to the operational reserve.

The 5.7 m/s value is for reproducing this historical log, not mission planning.
For a future flight, use the forecast wind and retain the normal operational
reserve.

The validation log is
`/data/buildlogs/phoenix/2026-08-23/orroral4-starlink-fit.BIN`. Reproduce the
arm-window and phase comparison with:

```bash
python3 ../../Tools/autotest/phoenix_mission_compare.py \
    orroral4-log2.bin \
    /data/buildlogs/phoenix/2026-08-23/orroral4-starlink-fit.BIN
```

## Orroral 4 prediction

The camera counterfactual was replayed with the same mission and effective
historical wind as the updated Starlink case. Pairing the camera and Starlink
SITL runs isolates the payload increment; adding that increment to the real
camera-free result corrects most of the common model bias.

| Result | Real, no camera | Camera central | Camera conservative |
|---|---:|---:|---:|
| Arm-to-disarm time | 93.96 min | 93.50 min | 93.50 min |
| Raw SITL battery use | n/a | 19.948 Ah / 933.1 Wh | 20.329 Ah / 950.2 Wh |
| Payload increment from paired SITL | n/a | +2.926 Ah / +131.4 Wh | +3.307 Ah / +148.5 Wh |
| Bias-corrected expected use | 17.444 Ah / 806.6 Wh | 20.370 Ah / 938.0 Wh | 20.751 Ah / 955.1 Wh |
| 39 Ah nameplate used | 44.7% | 52.2% | 53.2% |

Thus, had the camera been fitted for `orroral4-log2.bin`, the best estimate is
about **20.4 Ah / 938 Wh**, with the higher-drag cross-check giving about
**20.8 Ah / 955 Wh**. This is an extra 2.93 to 3.31 Ah, or 131 to 149 Wh, over
the actual flight. Starting from the same 95% indicated state seen at arming,
the model implies roughly 42% to 43% indicated remaining at disarm. The
integer percentage is only a cross-check; plan against Ah/Wh plus reserve.

The validation logs are:

- `/data/buildlogs/phoenix/2026-08-23/orroral4-camera-central.BIN`
- `/data/buildlogs/phoenix/2026-08-23/orroral4-camera-conservative.BIN`

Both camera cases completed all 61 executed mission items, including VTOL
takeoff and landing. Reproduce their analysis by adding the two log paths to
the `phoenix_mission_compare.py` command above.

For a future mission, use mission-specific wind cases to form the planning
envelope; do not simply plan to consume the reported remainder.

For example, after startup set the forecast wind before arming:

```text
param set SIM_WIND_SPD 4.3
param set SIM_WIND_DIR 341
param set SIM_WIND_TURB 0.1
```

`SIM_WIND_DIR` is the direction the wind comes from. Run still-air, forecast,
and conservative forecast cases; compare their arm-to-land Ah rather than only
the integer remaining-percent field.

## Important limitation

This model is suitable for comparing mission time and battery use in fixed-wing
flight. It is not a flight-release calculation. VTOL and transition energy are
still weakly calibrated, wind can dominate a long out-and-back mission, and the
39 Ah nameplate capacity is not the same as a safe usable capacity. Retain the
normal operational battery reserve and validate the prediction against another
representative camera flight before relying on it for a long mission.
