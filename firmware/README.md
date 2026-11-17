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

## Proposal: precise weight message

- Every time the filtered weight changes (it is already filtered: 4-sample moving average, ~11 Hz), send on USB MIDI cable 1:
  `F0 14 0D 72 <w0> <w1> <w2> <w3> F7` — `measure_calculated_value` (raw − tare, counts, can be negative) as a signed
  value in 4 × 7-bit groups, lowest first (offset by 2^27 to keep it unsigned).
- Optional: a setting (id 17, default off) to turn it on, so DAWs that dislike SysEx are not affected.
- Counts, not grams: the counts-per-gram factor differs per unit (±15 %), the host calibrates.
- Also worth fixing: `DELTA_QUARTER_KILO` / `DELTA_HALF_KILO` assume 700 counts/g; with 776.8 the ranges are ~10 % smaller than their names.

Nothing is changed in the firmware repo yet: changes go to the firmware team (Mark, soya-mik) as a branch + PR.
