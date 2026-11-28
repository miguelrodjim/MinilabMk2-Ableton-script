# Ableton Live 12 Remote Script for Arturia MiniLab MkII

A customized MIDI Remote Script for the Arturia MiniLab MkII, targeting Ableton Live 12 Arrangement View.

## Hardware controls

Encoders 1–16 adjust parameters 1–16 of the selected device, in the order exposed by Live. If no device is selected, rotation targets the first device on the track. Hold pad 16 for finer adjustment of continuous parameters.

| Selected plugin | Press encoder 1 | Press encoder 9 |
| --- | --- | --- |
| FabFilter Pro-Q 3 | Toggle band 1 | Toggle band 6 |
| FabFilter Pro-C 2 | Auto Gain | Auto Release |
| UADx SSL E Channel Strip | HF Bell | LF Bell |
| UADx LA-6176 Channel Strip | Cycle EQ Hi Freq | Cycle EQ Lo Freq |

The plugin must expose the corresponding parameters in Live.

The physical Pad 1–8 / 9–16 button switches between note messages (MIDI notes 36–43) and control messages:

| Pad | Function |
| --- | --- |
| 9 | Toggle playback |
| 10 | Stop |
| 11 | Toggle global Arrangement recording |
| 12 | Toggle arm for the selected track |
| 13 | Toggle mute for the selected track |
| 14 | Toggle exclusive solo. Hold pad 16 for non-exclusive solo. |
| 15 | Cycle Control Room monitoring EQ on Main |
| 16 | Hold for fine encoder adjustment or non-exclusive solo |

Pad 15 finds the three-chain `MONITOR` rack inside `CONTROL ROOM` on Main, or a `CONTROL ROOM` rack that holds the three chains directly. It cycles the Chain Selector through positions 0, 1, and 2 regardless of chain names or list order. Set the chain zones to 0 for HS7, 1 for 990 PRO, and 2 for none, and keep the chains enabled. Live shows the rack name and resulting selector position after each press.

When Live disables direct editing of the selector, pad 15 uses the rack's `CORRECCIÓN` macro with the values from the monitoring variations (0, 61, and 127).

On macOS, the matching Hammerspoon configuration switches this rack to `none` when Live opens Export Audio/Video. The rack stays on `none` after the dialog closes.

## Auto-Color Engine

The script includes an `AutoColorComponent` that listens for track creation, name changes, and new arrangement clips in real-time, applying matching colors to both tracks and clips.

### Smart Recognition Rules

- Word-boundary matching prevents false positives (e.g., "contrabajo" does not trigger "bajo")
- Case-insensitive matching
- True RGB Hex snapping (24-bit hex sent directly to Ableton Live 12)
- Asynchronous task deferral to bypass Live 12 API restrictions
- User-configurable via `autocolor.txt` (hot-reloaded on save)

### Color Categories

| Category | Keywords | Color |
| :--- | :--- | :--- |
| Drums (Group) | drums, drum, bateria | Dark Violet |
| Drum Elements | kick, bombo, snare, hihat, toms, ride, platos | Pastel Purple |
| Percussion (Group) | percs, percus, percussion | Medium Violet Red |
| Percussion Elements | udu, cajon, pandero, bongo, palmas, nudillos | Pastel Pink |
| Electric Guitars (Group) | electricas, elecs | Dark Red |
| Electric Guitar Elements | pwr, lead, solo, gtr | Pastel Red |
| Acoustic Guitars (Group) | acusticas | Saddle Brown |
| Acoustic Guitar Elements | acc, flam, clasica | Tan |
| Keys / Synths (Group) | keys | Dark Orange |
| Keys / Synth Elements | b3, organ, synth, piano, rhodes | Mango |
| Bass | bass, bajo | Yellow |
| Strings (Group) | strings | Very Dark Brown |
| String Elements | violin, viola, contrabajo, cello | Goldenrod |
| Vocals (Group) | voces | Dark Green |
| Vocal Elements | vox, voz, principal, coro, armo | Forest Green |
| Effects & FX | fxs, fx | Sky Blue |

## Installation

1. Copy the `AAMinilabMk2_Live12` directory to:
   - macOS: `~/Music/Ableton/User Library/Remote Scripts/AAMinilabMk2_Live12`
   - Windows: `\\Users\\[Username]\\Documents\\Ableton\\User Library\\Remote Scripts\\AAMinilabMk2_Live12`

2. Set your Arturia MiniLab MkII to Factory Preset 8 (Ableton Live):
   - Hold Shift on the MiniLab MkII
   - Press Pad 8

3. In Ableton Live:
   - Go to Settings / Preferences (CMD+,) > Link, Tempo & MIDI
   - Under Control Surface, select `AAMinilabMk2_Live12`
   - Set both Input and Output to `Arturia MiniLab mkII`
   - Enable Track and Remote for the MiniLab inputs in the MIDI Ports table

## Customization

### Modifying Auto-Color Keywords

Edit `AAMinilabMk2_Live12/autocolor.txt`:

```
COLOR_HEX = keyword1, keyword2, keyword3
```

Changes are detected and reloaded automatically on save.

## Architecture

- `Minilab_Mk2.py`: Main entry point and component lifecycle manager
- `Elements.py`: Hardware button, encoder, pad, and color skin definitions
- `CustomControlComponent.py`: Transport, mixer, device, clip gain, and scrolling implementations
- `AutoColorComponent.py`: Track naming listener and auto-coloring engine

## License

MIT License.
