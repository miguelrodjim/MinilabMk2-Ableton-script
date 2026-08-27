# Minilab Mk2 Custom Ableton Live 12 Script

This repository contains a heavily customized Python Remote Script for the **Arturia Minilab Mk2**, specifically tailored for **Ableton Live 12**. 

What started as a fork of previous community scripts has been completely overhauled to create a fast, efficient, and **Arrangement View**-focused workflow.

---

## 🚀 Key Features & Mappings

Unlike the default Arturia script which focuses on Session View, this script reimagines the Minilab Mk2 as a powerhouse for navigating and mixing directly in the Arrangement View.

### 🎛 1. Timeline Scrubbing (Knob 15)
Navigate through your song structure without touching the mouse.
- **Default (Turn):** Jumps the playhead forward or backward by exactly **1 Bar** at a time.
- **Precision Mode (Shift + Turn):** Still jumps by 1 Bar, but physically increases the resistance of the knob. You will need to rotate the knob significantly more to trigger a jump, giving you tactile precision so you don't accidentally overshoot your target.

### 🎚 2. Track Navigation (Knob 16)
Scroll through your project vertically with ease.
- **Turn:** Moves the selected track up or down in the Arrangement View.
- *Note: We built a custom "accumulator" logic to ensure that scrolling feels natural. The knob has a built-in threshold so it doesn't fly through 20 tracks with a tiny nudge.*

### 🔊 3. Direct Clip Gain (Knob 10)
Adjust audio levels surgically without relying on track faders.
- **Turn:** Directly increases or decreases the **Clip Gain** of the currently selected audio clip.
- This is incredibly useful for vocal comping or evening out audio takes dynamically from the hardware.

### ⚙️ 4. Smoothed Encoders
All custom encoders in this script use an internal threshold system (accumulators). This ensures that physical rotation translates to smooth and predictable UI changes in Ableton, completely preventing the erratic jumps common in older MIDI scripts.

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
