# Minilab Mk2 Custom Ableton Live 12 Script

This repository contains a heavily customized Python Remote Script for the **Arturia Minilab Mk2**, specifically tailored for **Ableton Live 12**. 

What started as a fork of previous community scripts has been completely overhauled to create a fast, efficient, and Arrangement-focused workflow.

## Key Features

- **Arrangement View Focus:** This script is optimized for users who work primarily in Arrangement View rather than Session View.
- **Custom Timeline Scrubbing:** 
  - **Knob 15** acts as a playhead scrubber.
  - Turn it to jump back and forth by exactly 1 bar.
  - Hold **Shift** while turning Knob 15 to engage "slow mode", which adds physical resistance to the knob to prevent jumping too fast.
- **Custom Track Navigation:**
  - **Knob 16** allows you to scroll up and down through your tracks in Arrangement View.
- **Direct Clip Gain Control:**
  - **Knob 10** is mapped directly to the Clip Gain of the currently selected audio clip, allowing you to intuitively adjust audio levels without using a mouse.
- **Accumulator-smoothed Encoders:** All custom encoders have been carefully tuned with thresholds to ensure that physical rotation translates to smooth and predictable UI changes, preventing erratic jumps.

## Installation

1. **Clone or download** this repository.
2. Locate the `AAMinilabMk2_Live12` folder inside this repository.
3. **Copy** the `AAMinilabMk2_Live12` folder to your Ableton User Library Remote Scripts folder:
   - **Mac:** `~/Music/Ableton/User Library/Remote Scripts/`
   - **Windows:** `\Users\[Username]\Documents\Ableton\User Library\Remote Scripts\`
4. Restart Ableton Live 12.
5. In Ableton, go to **Preferences > Link/Tempo/MIDI**.
6. Select **AAMinilabMk2_Live12** in the Control Surface dropdown, and set your Input and Output to your Arturia Minilab Mk2.

## Development & Customization

If you wish to modify this script further, all the custom logic can be found in `CustomControlComponent.py` and hardware mappings in `Elements.py`. 

Please refer to the `AGENTS.md` file in this repository for technical documentation, architectural notes, and debugging strategies specifically for the Ableton Live 12 Python API.
