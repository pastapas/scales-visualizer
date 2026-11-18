# Scales firmware with weight notes (beta)

`scales-weight-notes.uf2` is a beta firmware for **Playtronica Scales**. It keeps everything the released firmware does
and adds:

- **Note map**: teach the scales your own objects. Put an object on, pick a note, press *Learn this weight* in the
  visualizer (key **K**). Up to 16 objects, saved on the device. With the map on, each object plays its note in Hold,
  Arpeggio and BPM modes, also without a computer. A new note plays once the weight is steady (~0.2–0.3 s), so putting
  an object on or taking it off does not play the notes in between.
- **Press to bend**: while a note sounds, pressing on the object with a finger bends it with pitch bend (harder = higher).
  The pitch bend is sent on MIDI channel 1 for all notes, arpeggio included.
- **Precise weight**: the device can send the weight at full sensor precision (the visualizer turns this on), so the
  weight readout works on every Sensitivity.

Your settings from the released firmware are kept on update; the note map starts empty.

## How to update

1. Download [`scales-weight-notes.uf2`](scales-weight-notes.uf2) (or from the latest release of this repository).
2. Put Scales into update mode, either way:
   - open the visualizer, press **K**, then **Update mode** in the *Firmware* section, or
   - use *Update Firmware* in the Playtronica WebMidi app.
3. A drive called **RPI-RP2** appears. Copy the `.uf2` file onto it. Scales restarts by itself with the new firmware.

**Going back** to the released firmware: do the same with `scales-firmware_v1.0.8.uf2` from
[Playtronica/scales-releases](https://github.com/Playtronica/scales-releases). The note map is lost, your other settings stay.

This is a beta: the firmware version shows as 0.0.0. Settings *wait before a note* and *press for full bend* (visualizer
sliders) go back to their defaults (150 ms, 300 g) when Scales restarts.

## For developers

SysEx after `F0 14 0D`:

| Bytes | Direction | Meaning |
|---|---|---|
| `72 w0 w1 w2 w3` | device → host | weight in sensor counts (~777 per gram, differs per unit by up to ±15 %) |
| `74 index note` | host → device | learn the current weight as point `index` (0–15) with `note` |
| `75 index note w0..w3` | both | set point / point answer; note 127 deletes the point |
| `76` | host → device | get all points (one `75` each, then `77`) |
| `77 count` | both | host: clear all points; device: number of points |

Weights are signed, sent as value + 2^27 in four 7-bit groups, lowest first.
Settings by id: 17 note map on (saved), 18 weight stream on, 19 settle time in ms (default 150),
20 full bend weight in 100 counts (default 2330 ≈ 300 g, 0 = off); 18–20 are not saved.

Objects under ~4.5 g are absorbed by the scale's drift compensation.

## Third-party software in the firmware

The firmware is built with the [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk) (BSD-3-Clause, includes
TinyUSB, MIT) and [hx711-pico-c](https://github.com/endail/hx711-pico-c) (MIT, © 2023 Daniel Robertson).
The firmware itself is © Playtronica, all rights reserved.
