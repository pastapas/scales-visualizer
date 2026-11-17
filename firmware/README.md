# Scales firmware: build setup and the planned weight message

## Build environment (set up 2026-11-17 on Sasha's Mac, Apple Silicon)

- Docker runs in **colima** (no Docker Desktop): `brew install colima docker docker-buildx`.
- Start it after a reboot: `colima start` (VM: 4 CPU, 6 GB RAM, 40 GB disk).
- Firmware source: `~/Projects/scales-firmware` (clone of `Playtronica/scales-firmware`, private).
- Build:

  ```bash
  cd ~/Projects/scales-firmware && make build
  ```

  Result: `output/scales.uf2`. The first build creates the image `plsdk-build-env:v2` (5.3 GB, ~7.5 min);
  later builds reuse it.
- The Dockerfile clones the **latest** pico-sdk, so the image depends on the day it was built
  (this one has pico-sdk 2.3.1). Builds by the firmware team can differ.
- Version numbers are 0.0.0 with `make build`; `make release MAJOR_VERSION=… MINOR_VERSION=… PATCH_VERSION=…` sets them.

## Flashing

1. Reboot into the USB bootloader: SysEx action `F0 14 0D 65 01 01 F7`
   (or WebMidi "Update Firmware", or hold the BOOT pins while plugging in).
2. A drive `RPI-RP2` appears: copy `output/scales.uf2` onto it. The device reboots by itself.
3. To go back: the released firmware is in `Playtronica/scales-releases` (`output/scales-firmware_v1.0.8.uf2`).

## Why a firmware change

The device sends the weight only as CC90 (0–127 over the Sensitivity range), so weight precision is one CC step:
1.8 g at Sensitivity 0 … 14 g at Sensitivity 4. The load cell itself resolves ~0.01 g
(776.8 counts/g measured, Sensorcon SC133-3KG, 1.0 ± 0.15 mV/V).

## Branch `sasha/weight-notes` (in `~/Projects/scales-firmware`, not pushed yet)

Built file: `firmware/scales-weight-notes.uf2` (version 0.0.0, pico-sdk 2.3.1). What it adds, documented in the firmware's
`SettingsDescription.md` ("Note Map", "Weight Stream"):

- **Weight stream** (setting 18, not saved): `F0 14 0D 72 <w0..w3> F7` with the weight in sensor counts on every new sample.
- **Note map** (setting 17 + SysEx 74 learn / 75 set / 76 get / 77 clear): up to 16 learned weight → note points, saved to
  flash; the weight plays the nearest learned note instead of the scale. A new note plays only after the raw sensor samples are steady
  for 150 ms (setting 19, ~0.2–0.3 s after the object stops), so putting an object on or taking it off does not play
  the notes in between.
- Settings of the current firmware are kept on update (layout migration), the map starts empty.

## Notes for the firmware team

- The weight message carries `raw − tare + MEASURE_TARE_MARGIN` (true weight in counts, signed, not limited by the
  Sensitivity range), offset by 2^27, 4 × 7-bit groups, lowest first. Counts, not grams: the factor differs per unit (±15 %).
- The stream is off by default (runtime setting 18), so DAWs that dislike SysEx are not affected.
- Objects under ~4.5 g are taken into the tare by the drift compensation (`MEASURE_TARE_ADAPT_THRESHOLD`).
- Also worth fixing: `DELTA_QUARTER_KILO` / `DELTA_HALF_KILO` assume 700 counts/g; with 776.8 the ranges are ~10 % smaller than their names.
- PLSDK got `plsdk_settings_mark_changed()` to save data that is not a registered setting (the 16 points don't fit a VALUE message).

The branch goes to the firmware team (Mark, soya-mik) as a PR; it is not pushed yet.
