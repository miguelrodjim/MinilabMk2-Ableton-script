# Ableton Live 12 Remote Script for Arturia MiniLab MkII

A customized MIDI Remote Script for the Arturia MiniLab MkII, targeting Ableton Live 12 Arrangement View.

## Features

- **Arrangement View Centric**: Direct mixing, clip-gain editing, timeline scrubbing, and track navigation
- **Auto-Color Engine**: Automatically colors tracks and clips based on track names (e.g., naming a track "kick" colors it pastel purple)
- **Fast Encoders**: VST/Device knobs tuned for fast response (10x speed multiplier)
- **Precision Scrubbing**: Knob 15 jumps 1 bar per step, with fine-tuned resistance when holding Shift (Pad 16)
- **Free Mappings**: Knobs 13 & 14 and Pad 15 are unlinked for custom MIDI Learn

## Hardware Layout

```
 _________________________________________________________________________
|  [ 1 ] [ 2 ] [ 3 ] [ 4 ]   [ 5 ] [ 6 ] [ 7 ] [ 8 ]                      |
|  [ 9 ] [10 ] [11 ] [12 ]   [13 ] [14 ] [15 ] [16 ]   [ PADS 1 - 8 / 9-16 ]|
|_________________________________________________________________________|
```

### Encoders (Knobs 1-16)

| Knob | Mode / Function | Description |
| :--- | :--- | :--- |
| 1-8 | Device / VST Macros | Controls the 8 macro parameters of the currently selected device |
| 9 | Cue Volume & Metronome | Rotate: Master Cue/Solo volume. Click: Toggle Metronome |
| 10 | Clip Gain | Directly alters the gain parameter of the selected audio clip |
| 11 | Track Pan | Adjusts the stereo pan of the currently selected track |
| 12 | Track Volume | Controls the volume fader of the currently selected track |
| 13 | FREE (MIDI Learn) | Unassigned. Map via CMD+M |
| 14 | FREE (MIDI Learn) | Unassigned. Map via CMD+M |
| 15 | Timeline Scrubbing | Rotate: Jumps playhead by 1 bar. Hold Pad 16 (Shift): Precision scrub |
| 16 | Track Navigation | Vertical scrolling through tracks in Arrangement View |

### Pads (Bank 2 / Transport & Modifiers)

Access these controls with Pad Bank 2 (Pads 9-16) active on the controller.

| Pad | LED Color | Function | Description |
| :--- | :--- | :--- | :--- |
| 9 | Green | Play | Starts transport playback |
| 10 | Red | Stop | Stops transport playback |
| 11 | Red | Global Record | Toggles global Arrangement recording |
| 12 | Red | Arm Track | Toggles Arm/Record for the selected track |
| 13 | Orange | Mute Track | Mutes/unmutes the selected track |
| 14 | Blue | Solo Track | Solos/unsolos the selected track |
| 15 | Cyan | FREE (Custom Action) | Unmapped by the script for custom MIDI mapping |
| 16 | Purple | Shift Modifier | Hold to activate precision mode on Knob 15 |

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
