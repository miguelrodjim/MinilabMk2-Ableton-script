# 🎹 Arturia MiniLab MkII — Custom Ableton Live 12 Script

[![Ableton Live 12](https://img.shields.io/badge/Ableton%20Live-12.0%2B-blue?logo=ableton&style=for-the-badge)](https://www.ableton.com)
[![Hardware](https://img.shields.io/badge/Hardware-Arturia%20MiniLab%20MkII-orange?style=for-the-badge)](https://www.arturia.com/products/hybrid-synths/minilab-mkii/overview)
[![Python 3.11](https://img.shields.io/badge/Python-3.11%20(Live%20API)-yellow?logo=python&style=for-the-badge)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

A high-performance, heavily customized **MIDI Remote Script** for the **Arturia MiniLab MkII**, specially built to supercharge mixing, navigation, editing, and organization inside **Ableton Live 12 (Arrangement View)**.

---

## ✨ Key Highlights

- 🚀 **Arrangement View Centric:** Replaces Session-clip launching with direct mixing, clip-gain editing, timeline scrubbing, and track navigation.
- 🎨 **Auto-Color Engine:** Automatically colors your tracks in real time as soon as you name them (e.g., naming a track `kick` instantly colors it pastel purple).
- 🎛️ **Fast & Responsive Encoders:** VST/Device knobs are tuned for fast response (10x speed multiplier) without skipping or jumping.
- 🧠 **Precision Scrubbing:** Knob 15 jumps 1 bar per step, with fine-tuned resistance when holding **Shift** (Pad 16).
- 🔓 **Free Mappings:** Knobs 13 & 14 and Pad 15 are unlinked from the script engine so you can use Ableton's native `CMD + M` MIDI Learn for whatever you want.

---

## 🎛️ Hardware Layout & Control Map

```
 _________________________________________________________________________
|  [ 1 ] [ 2 ] [ 3 ] [ 4 ]   [ 5 ] [ 6 ] [ 7 ] [ 8 ]                      |
|  [ 9 ] [10 ] [11 ] [12 ]   [13 ] [14 ] [15 ] [16 ]   [ PADS 1 - 8 / 9-16 ]|
|_________________________________________________________________________|
```

### 🎚️ Encoders (Knobs 1 - 16)

| Knob | Mode / Function | Description |
| :---: | :--- | :--- |
| **1 – 8** | **Device / VST Macros** | Controls the 8 macro parameters of the currently selected device or plugin with high-speed response. |
| **9** | **Cue Volume & Metronome** | **Rotate:** Controls Master Cue/Solo volume.<br>**Click:** Toggles the **Metronome** On/Off. |
| **10** | **Clip Gain** | *(Custom)* Directly alters the `gain` parameter of the selected audio clip. Ideal for quick vocal levelling and comping. |
| **11** | **Track Pan** | Adjusts the stereo pan of the currently selected track. |
| **12** | **Track Volume** | Controls the volume fader of the currently selected track. |
| **13** | 🔓 **FREE (MIDI Learn)** | Completely unassigned. Map it to whatever you want via `CMD + M` (e.g. Master utility, filters, macro overrides). |
| **14** | 🔓 **FREE (MIDI Learn)** | Completely unassigned. Map it to whatever you want via `CMD + M`. |
| **15** | **Timeline Scrubbing** | **Rotate:** Jumps the playhead forward/backward by **1 Bar**.<br>**Hold Pad 16 (Shift) + Rotate:** High resistance precision scrub to prevent accidental jumps. |
| **16** | **Track Navigation** | Smooth vertical scrolling up and down through your tracks in Arrangement View. |

---

### 🟩 Pads (Bank 2 / Transport & Modifiers)

*To access these controls, ensure **Pad Bank 2 (Pads 9–16)** is active on the controller.*

| Pad | LED Color | Function | Description |
| :---: | :---: | :--- | :--- |
| **9** | 🟢 Green | **Play** | Starts transport playback. |
| **10** | 🔴 Red | **Stop** | Stops transport playback. |
| **11** | 🔴 Red | **Global Record** | Toggles global Arrangement recording. |
| **12** | 🔴 Red | **Arm Track** | Toggles Arm/Record for the currently selected track. |
| **13** | 🟠 Orange | **Mute Track** | Mutes / unmutes the selected track. |
| **14** | 🔵 Blue | **Solo Track** | Solos / unsolos the selected track. |
| **15** | 🩵 Cyan | 🔓 **FREE (Custom Action)** | Lit in permanent Cyan. Unmapped by the script so you can MIDI-map it (e.g., Master Mono switch, Loop toggle). |
| **16** | 🟣 Purple | ⇧ **Shift Modifier** | Lit in Purple. Hold down to activate precision mode on Knob 15. |

---

## 🎨 Intelligent Auto-Color Engine

The script includes a dedicated `AutoColorComponent` that listens for track creation and name changes in real-time, automatically applying color coding based on standard production nomenclature.

### 🧠 Smart Recognition Rules
- **Word-Boundary Matching (`\b`):** Prevents false positives (e.g., a track named `contrabajo` will **not** trigger the rule for `bajo`).
- **Case-Insensitive:** Works identically with `KICK`, `Kick`, or `kick`.
- **True RGB Hex Snapping:** Sends 24-bit Hex colors (`0xRRGGBB`) directly to Ableton Live 12, which snaps them to your active theme's palette.
- **Asynchronous Task Deferral:** Bypasses Ableton Live 12's internal API restrictions to prevent notification crashes.

### 🌈 Color Category Dictionary

| Category | Target Keywords | Color Preview | RGB Hex |
| :--- | :--- | :---: | :---: |
| **Drums (Group)** | `drums`, `drum`, `bateria` | 🟣 Violeta Oscuro | `0x8A2BE2` |
| **Drum Elements** | `kick`, `bombo`, `kck`, `snare`, `snr`, `caja`, `hihat`, `hi-hat`, `hat`, `aereos`, `ohs`, `toms`, `tom`, `ride` | 🪻 Morado Pastel | `0xDDA0DD` |
| **Percussion (Group)** | `percs`, `percus`, `percussion` | 🌺 Morado Rosáceo | `0xC71585` |
| **Percussion Elements** | `udu`, `cajon`, `pandero`, `trash`, `cascabeles`, `pandereta`, `castañuela`, `bongo`, `timbales`, `bongos`, `timbal`, `triangulo`, `crotalo`, `crotalos`, `palmas` | 🌸 Rosa Pastel | `0xFFB6C1` |
| **Electric Guitars (Group)** | `electricas`, `elecs` | 🔴 Rojo Oscuro | `0x8B0000` |
| **Electric Guitar Elements** | `pwr`, `power`, `earp`, `lead`, `solo` | 🪸 Rojo Pastel | `0xFA8072` |
| **Acoustic Guitars (Group)** | `acusticas` | 🟤 Marrón | `0x8B4513` |
| **Acoustic Guitar Elements** | `acc`, `acc rhy`, `acc arp`, `flam`, `clasica`, `flam arp`, `flam rhy` | 🪵 Marrón Claro Pastel | `0xD2B48C` |
| **Keys / Synths (Group)** | `keys` | 🟠 Naranja | `0xFF8C00` |
| **Keys / Synth Elements** | `b3`, `organ`, `synth lead`, `synth bass`, `synth`, `arp2500`, `mini`, `buchla`, `juno`, `jupiter`, `piano`, `rhodes` | 🥭 Mango / Naranja Claro | `0xFFB90F` |
| **Bass** | `bass`, `bajo` | 🟡 Amarillo | `0xFFFF00` |
| **Strings (Group)** | `strings` | 🟫 Marrón Muy Oscuro | `0x5C4033` |
| **String Elements** | `violin`, `viola`, `contrabajo`, `cello` | 🍯 Marrón Ocre Dorado | `0xDAA520` |
| **Vocals (Group)** | `voces` | 🟢 Verde Oscuro | `0x006400` |
| **Vocal Elements** | `vox`, `voz`, `voz principal`, `principal`, `coro`, `armo`, `armo hi`, `armo low`, `rapeo`, `coros`, `voz doble`, `armo med` | 🍏 Verde Lima / Claro | `0x228B22` |
| **Effects & FX** | `fxs`, `fx` | 🩵 Azul Clarito / Sky Blue | `0x87CEEB` |

---

## 📦 Installation & Setup

### 1. Copy the Script to Ableton's Remote Scripts Directory
Download or clone this repository and copy the `AAMinilabMk2_Live12` directory to:

* **macOS:**
  ```bash
  ~/Music/Ableton/User Library/Remote Scripts/AAMinilabMk2_Live12
  ```
* **Windows:**
  ```text
  \Users\<Your-Username>\Documents\Ableton\User Library\Remote Scripts\AAMinilabMk2_Live12
  ```

### 2. Configure Hardware Memory Preset
Make sure your Arturia MiniLab MkII is running the default **Factory Preset 8 (Ableton Live)**:
1. Hold the **Shift** button on the MiniLab MkII.
2. Press **Pad 8** (Preset 8).

### 3. Select the Script in Ableton Preferences
1. Open **Ableton Live 12**.
2. Go to **Settings / Preferences (`CMD + ,`) > Link, Tempo & MIDI**.
3. Under **Control Surface**, select `AAMinilabMk2_Live12`.
4. Set both **Input** and **Output** to `Arturia MiniLab mkII` (or `Arturia MiniLab mkII (Port 1)`).
5. In the MIDI Ports table below, ensure **Track** and **Remote** are enabled for the MiniLab inputs.

---

## 🛠️ Customization

### Modifying Auto-Color Keywords & Hex Values
Open `AAMinilabMk2_Live12/AutoColorComponent.py` and modify the `COLORS` dictionary:
```python
COLORS = {
    0x00FFFF: ['my_custom_keyword', 'another_name'], # Cyan
    0xFF00FF: ['synth_lead'],                        # Magenta
}
```
Any standard 24-bit Hex color (`0xRRGGBB`) can be used.

---

## 📜 Architecture & Source Files

* [`Minilab_Mk2.py`](file:///Volumes/DATA/DEVELOPMENT/minilab/MinilabMk2-Ableton-script/AAMinilabMk2_Live12/Minilab_Mk2.py): Main Control Surface entry point and component lifecycle manager.
* [`Elements.py`](file:///Volumes/DATA/DEVELOPMENT/minilab/MinilabMk2-Ableton-script/AAMinilabMk2_Live12/Elements.py): Hardware button, encoder, pad, and color skin definitions.
* [`CustomControlComponent.py`](file:///Volumes/DATA/DEVELOPMENT/minilab/MinilabMk2-Ableton-script/AAMinilabMk2_Live12/CustomControlComponent.py): Custom transport, accumulator-based scrubbing, and clip gain implementations.
* [`AutoColorComponent.py`](file:///Volumes/DATA/DEVELOPMENT/minilab/MinilabMk2-Ableton-script/AAMinilabMk2_Live12/AutoColorComponent.py): Smart asynchronous track naming listener and auto-coloring engine.

---

## 📄 License
MIT License. Feel free to use, modify, and distribute.
