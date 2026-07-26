# UA NOTAM builder

A local map tool for preparing a UA NOTAM for the NAIPS Internet Service. It takes the
ArduPilot mission that will actually be flown, draws the proposed NOTAM area over it and the
approved BVLOS area, works in local time, and prints every NAIPS field ready to paste.

**It does not submit anything.** There is no NAIPS connection at all. Copy the fields into
`NOTAM > New NOTAM`, review them there, and click Submit yourself.

## Why

Every number in a NOTAM appears two or three times — in the Summary, in the Item E subject,
and in the Item E text — and NAIPS cross-checks none of them. On **C3031/25** the Summary
said `21.0NM` and Item E said `20NM`: the same distance, stated twice, differently. The
correct figure from the quoted position is 21.5NM.

This tool derives all of them from one geometry, so they cannot disagree.

## Running it

Open `notam.html` in Chrome. No server and no build step — it is a plain page using classic
`<script>` tags, so it works directly from `file://`, offline, in the field.

## Using it

1. **Load the mission.** Pick or drag an ArduPilot `.txt` / `.waypoints` file. Only nav
   commands are used; `DO_SET_ROI` and other `DO_*` rows carry positions that are not flown
   and would otherwise drag the computed centre a long way off.
2. **Check the area.** *Fit to mission* sets the centre and radius to the smallest circle
   containing every waypoint, plus the buffer. Drag the blue centre marker or edit the radius
   to adjust. The lint panel re-checks that every waypoint is still inside.
3. **Set the max height.** *Max height* is the Item G) upper limit in FT AMSL, and it also
   drives the Q) upper flight level, so the two can never disagree. The 3900 / 4900 / 5900
   buttons are the instrument's altitude steps; type anything else directly. Below the field
   the tool lists which approved-area altitude steps the NOTAM circle actually touches, and
   the lint panel fails the ceiling if it exceeds all of them and warns when part of the area
   sits under a lower step.
4. **Set the times in local time.** The timezone selector resolves AEST/AEDT properly, so
   Items B) and C) come out in UTC without arithmetic in your head.
5. **Read the checks**, then click each field to copy it into NAIPS.

### On the map

| | |
|---|---|
| Solid blue | the NOTAM area |
| Dashed yellow | the Q) line circle — turns red if minute-rounding of the centre pushes it off the area |
| Red | mission track and waypoints, white marker at home |
| Green / cyan | approved flight geography, contingency volume, altitude-limit steps |
| Orange | NFZs |
| Purple | the radial from the reference aerodrome, labelled with the bearing and distance |

## Files

| | |
|---|---|
| `notam.html` | the whole application |
| `profiles.js` | aerodromes, aircraft, contacts, frequencies, saved sites, Item E template |
| `approved_area.js` | the approved area as GeoJSON, generated from the instrument KML |
| `kml2js.py` | regenerates `approved_area.js` — `./kml2js.py ../instrument2.kml > approved_area.js` |
| `example-mission.txt` | a synthetic mission for testing, including rows the parser must ignore |
| `vendor/` | Leaflet, vendored so the page needs no network |

`profiles.js` and `approved_area.js` are loaded as classic scripts rather than fetched,
because Chrome blocks `fetch()` and ES modules on `file://` pages.

## Things to know

**Bearings.** Computed as a WGS84 geodesic from the aerodrome ARP, then corrected by the
variation **published in ERSA** rather than a WMM value, because charted MAG bearings are
against published variation. With YSCB VAR 12°E this reproduces `BRG 209` on C3031/25,
`BRG 227` on C2048/26, and `BRG 263` on stored template 1278 exactly.

**Distances do not match the earlier NOTAMs.** The bearings reproduce exactly but the
distances come out longer: 21.5NM where C3031/25 said 21.0/20, and 13.6NM where template 1278
said 13.1. Both earlier figures are short, which suggests they were measured from something
other than the ARP. Worth resolving before relying on either.

**Unverified entries.** Anything in `profiles.js` marked `verified: false` — every aerodrome
except YSCB, and most aircraft descriptors — is a starting point that has not been checked
against a primary source. The tool badges them in the UI and warns in the lint panel. Check
against current ERSA and the instrument before submitting.

**The Q) line is a cross-check only.** NAIPS generates its own from the Subject and Status.
This tool rounds the centre to the nearest minute and grows the radius so the ring still
contains the area; NAIPS truncates instead, so a 1NM difference is expected.

**Radius units.** C-MAN0284 §7.3 asks for metres below 2NM, but the §12.2 UA templates in
the same document use `0.5NM RADIUS`, and NOF accepted `1NM` on C3031/25. The unit is a
dropdown and the lint only advises.

## Not done here

- The NAIPS **Template Directory** already holds 6 templates for this group, all showing
  `Approved = false`. Getting them approved would reduce a repeat operation to just the
  B)/C) times.
- KML/fence export so the NOTAM boundary shows on the GCS map during the flight.
- Pulling published NOTAMs back out of NAIPS automatically. For now, paste the published text
  into the *Verify a published NOTAM* box, which recomputes every bearing and distance from
  the position the NOTAM quotes.
