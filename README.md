# Scales Visualizer

Web visualizer and FM bell synth for **Playtronica Scales** (the weight → MIDI controller).
Every note the weight plays becomes a 3D resin object on a black screen; size follows the weight (CC90).

## Run

```bash
python3 -m http.server 8768 --directory .
```

Open http://localhost:8768 in **Chrome** (Web MIDI), connect Scales by USB, click the screen and allow MIDI **with SysEx**
(the page asks the device for its play mode, CC number and sensitivity).

Without a device: drag up/down on the screen to simulate weight.

| Key | Action |
|---|---|
| drag ↕ | simulated weight |
| Space / + | FUNCTION (+) |
| T | TARE |
| M | Hold / Arpeggio (simulator) |
| B | normal / screen blending |
| G | grams readout on/off |
| K | note map panel |
| C | clear |
| F | fullscreen |
| H | hide help |

## How it reads the device

- **Live shape**: one shape in the center. Its size follows the weight (up and down) and it changes form with the note, until "+" saves it; a saved shape keeps its size.
- **Hold**: a saved note is detected when the old weight note does not get its note-off (it was stuck with "+").
  MUTE dims the saved shapes in place; they light up again on unmute. After TARE they fade out.
- **Arpeggio**: arp steps are told apart from weight notes by timing. The firmware sends the weight note in the
  same millisecond as its CC and turns the old weight note off first; arp steps come on a fixed grid (Arp Rate × BPM),
  which the page learns. Saved arp notes stay in place, breathe and flash on each step.
- **Play mode** is polled every 1.5 s (`F0 14 0D 61 <req> 16 F7`): the device does not report a mode change made with its button.
- **Colors** are random from the resin palette (red, orange, yellow, green, blue, purple, dark), new for every shape and
  every new note, never the same twice in a row. **Form** goes by note
  (10 objects from `models/Scales Objects.stl`).

## Note map (needs the firmware from `firmware/`)

Press **K** or the "note map" button. Put an object on the scales, pick a note, press **Learn this weight**: the device
stores the weight of the object for that note (up to 16 objects, saved on the device). With the map on, the weight plays
the note of the nearest learned object in Hold, Arpeggio and BPM modes, also without the computer. Zones are split halfway
between learned weights. The next note is preselected one step up the major scale.

**Press to bend**: once a note sounds, pressing on the object with a finger bends the note with pitch bend while the
weight moves (harder = higher); the live shape squashes as you press. When the weight is steady again (an object added,
or a press held still) the note is chosen again for the new weight. The panel has two sliders, sent to the device
(not saved there, reset on reboot): *wait before a note* (settle time, default 150 ms) and *press for full bend*
(default 300 g; off = 0).

With this firmware the page also turns on the weight stream, so grams are precise (0.1 g) on every Sensitivity, and the
shape size follows the real weight: against the heaviest learned object × 1.4 with the note map on, else the Sensitivity range.

## Weight in grams

Calibrated 2026-11-17 on one unit with 10 / 50 / 100 / 200 g weights: **776.8 sensor counts per gram**, linear within 0.02 g.
The load cell is a Sensorcon SC133-3KG (1.0 ± 0.15 mV/V), so other units can differ by up to ~15 %: calibrate each device.

The firmware assumes 700 counts/g, so the real Sensitivity ranges are ~225 / 450 / 900 / 1350 / 1800 g (settings 0–4).

Grams are computed from CC90, so the precision is one CC step: 1.8 g (sens 0) … 14 g (sens 4). Below one step the screen
shows a bound (`<15 g`). Precise weight on every range needs a firmware change: the device would have to send the weight
itself (see `firmware/README.md`).

How the calibration was measured: SysEx `F0 0B 14 0D 02 F7` (logging on) and `F0 0B 14 0D 00 F7` (test mode) make the device
print `SCALE VALUE: <raw>` on its USB serial port while weight is on. `F0 0B 14 0D 01 F7` / `03` switch it back.

## Files

| Path | What |
|---|---|
| `index.html` | the whole app (three.js from jsDelivr, Web MIDI, Web Audio) |
| `objects.json` | meshes made from the STL by `tools/stl2json.py` |
| `models/Scales Objects.stl` | source objects (Shapr3D) |
| `logs/session*.txt` | real MIDI from the device, for replaying the note detection |

Log format: one event per word, `time.status.data1.data2` in base 36 (time in ms). `255` as status = play mode answer.
Replay in the browser console:

```js
const ev = (await (await fetch('logs/session3.txt')).text()).trim().split(/\s+/).map(w => w.split('.').map(x => parseInt(x, 36)));
const t0 = performance.now();
for (const [t, a, b, c] of ev) a === 255 ? app.setMode(['hold','arp','pitch','sens','bpm'][b], 'device') : app.onMidi({ data: [a, b, c], timeStamp: t0 + t });
```
