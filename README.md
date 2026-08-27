# Minilab Mk2 Custom Ableton Live 12 Script

This repository contains a heavily customized Python Remote Script for the **Arturia Minilab Mk2**, specifically tailored for **Ableton Live 12**. 

What started as a fork of previous community scripts has been completely overhauled to create a fast, efficient, and **Arrangement View**-focused workflow.

---

## 🚀 Key Features

Unlike the default Arturia script which focuses on Session View, this script reimagines the Minilab Mk2 as a powerhouse for navigating and mixing directly in the Arrangement View.

- **Accumulator-smoothed Encoders:** All custom encoders in this script use an internal threshold system (accumulators). This ensures that physical rotation translates to smooth and predictable UI changes in Ableton, completely preventing the erratic jumps common in older MIDI scripts.
- **Custom Hardware Mapping:** Almost every pad and knob has been carefully assigned to maximize workflow speed in the Arrangement View without needing to touch your mouse.

---

## 🎛 Complete Hardware Mapping

### **Encoders (Knobs 1 - 16)**

| Knob | Function | Description |
| :--- | :--- | :--- |
| **1-8** | **Device Macros** | Controls the 8 macro parameters of the currently selected device/plugin. |
| **9** | **Metronome** | Toggles the click track / metronome on and off. |
| **10** | **Clip Gain** | *(Custom)* Directly alters the `gain` parameter of the currently selected audio clip. Incredibly useful for vocal comping or evening out audio takes dynamically. |
| **11** | **Track Pan** | Pans the currently selected track left/right. |
| **12** | **Track Volume** | Adjusts the volume fader of the currently selected track. |
| **13** | *(Unassigned)* | Reserved for future custom mappings. |
| **14** | *(Unassigned)* | Reserved for future custom mappings. |
| **15** | **Timeline Scrubbing** | *(Custom)* Jumps the playhead forward or backward by exactly **1 Bar** at a time. <br><br>👉 **Precision Mode:** Hold **Pad 16 (Shift)** while turning to physically increase the resistance of the knob. You will need to rotate the knob significantly more to trigger a jump, preventing accidental overshoots. |
| **16** | **Track Navigation** | *(Custom)* Scrolls up and down through your tracks in the Arrangement View. |

### **Pads (1 - 16)**

| Pad | Function | Description |
| :--- | :--- | :--- |
| **1-8** | **MIDI Notes** | Standard MIDI notes (Drum Rack/Keys). |
| **9** | **Play** | Starts playback. |
| **10** | **Stop** | Stops playback. |
| **11** | **Record** | Toggles Global Record. |
| **12** | **Arm Track** | Arms/Disarms the currently selected track for recording. |
| **13** | **Mute Track** | Mutes/Unmutes the currently selected track. |
| **14** | **Solo Track** | Solos/Unsolos the currently selected track. |
| **15** | *(Unassigned)* | Reserved for future custom mappings. |
| **16** | **Shift** | Modifier button. Hold this while turning **Knob 15** to engage Precision Scrubbing Mode. |

---

## 📦 Installation

1. **Clone or download** this repository.
2. Locate the `AAMinilabMk2_Live12` folder inside this repository.
3. **Copy** the `AAMinilabMk2_Live12` folder to your Ableton User Library Remote Scripts folder:
   - **Mac:** `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows:** `\Users\[Username]\Documents\Ableton\User Library\Remote Scripts\`
4. Restart Ableton Live 12.
5. In Ableton, go to **Preferences > Link/Tempo/MIDI**.
6. Select **AAMinilabMk2_Live12** in the Control Surface dropdown, and set your Input and Output to your Arturia Minilab Mk2.

---

## 🛠 Development & Customization

If you wish to modify this script further, all the custom logic can be found in `CustomControlComponent.py` and hardware mappings in `Elements.py`. 

Please refer to the `AGENTS.md` file in this repository for technical documentation, architectural notes, and debugging strategies specifically for the Ableton Live 12 Python API.
