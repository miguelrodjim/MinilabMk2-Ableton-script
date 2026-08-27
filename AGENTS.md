# Ableton Live 12 Scripting Guide (Minilab Mk2 Custom)

## Context for Future Agents
This repository contains a heavily customized Python Remote Script for the Arturia Minilab Mk2, targeting **Ableton Live 12**.
It originally started as a fork of an older Live 11 script but has evolved significantly to better match the user's workflow, primarily centered around **Arrangement View**.

If you are continuing work on this script, please review the following learnings, debugging techniques, and Live 12 API quirks.

## 1. Project Structure
- The script lives entirely within the `AAMinilabMk2_Live12` directory.
- **`Minilab_Mk2.py`**: The entry point. Handles setup, component instantiation, and MIDI routing.
- **`Elements.py`**: Defines all the physical controls (buttons, pads, encoders) and their corresponding MIDI CCs or notes.
- **`CustomControlComponent.py`**: Contains custom logic (e.g., Clip Gain, scrubbing the timeline, changing tracks).
- **`__init__.py`**: Tells Ableton to treat the folder as a script and exports the `create_instance` function.

## 2. Key Learnings & API Quirks (Live 12)

### 2.1 Timeline Scrubbing (Arrangement View)
- The user uses **Arrangement View** exclusively.
- Do NOT use `Live.Application.get_application().view.scroll_view` for navigating the timeline or tracks, as it is unstable/unpredictable.
- **To scrub the playhead:**
  Modify `song.current_song_time`. 
  - To jump by bars, use `song.signature_numerator` (e.g., in 4/4 time, this is 4 beats = 1 bar).
  - Example: `self.song.current_song_time = max(0.0, self.song.current_song_time + self.song.signature_numerator)`

### 2.2 Track Navigation (Arrangement View)
- **To change the selected track:**
  Modify `song.view.selected_track`.
  ```python
  tracks = list(self.song.visible_tracks)
  index = tracks.index(self.song.view.selected_track)
  # logic to change index
  self.song.view.selected_track = tracks[new_index]
  ```

### 2.3 Encoder Accumulator Pattern
Encoders (knobs) send multiple small increment/decrement values very rapidly. If you map an action directly to an encoder turn, the UI will move uncontrollably fast.
- **Solution:** Use an "accumulator".
- Add the `value` to a local instance variable (`self._accumulator += value`).
- Only trigger the action if `abs(self._accumulator) >= threshold` (e.g., `0.05` or `0.15`).
- Subtract/Add the threshold back to the accumulator after triggering the action to keep it bounded.
- *BUG ALERT:* Make sure to initialize your accumulator (e.g., `self._accumulator = 0.0`) in the `__init__` method of your Component! Failing to do this will cause Python to throw a silent exception, breaking the knob functionality without any obvious error in the UI.

### 2.4 Clip Gain Mapping
- The `Clip.gain` property expects a value between `0.0` and `1.0`.
- To adjust volume naturally, modify it linearly (e.g., `+= 0.01` or `-= 0.01`) per encoder click.
- Limit the gain to `min(1.0, max(0.0, clip.gain + delta))`.

### 2.5 Shift Button Functionality
- The Minilab Mk2 hardware often sends completely different CCs when Shift is held.
- However, if you need to use Shift to modify the behavior of a knob in software, you can pass a reference of the `mixer` (which holds the `_shift_button`) to your custom component.
- Example:
  ```python
  is_shift_pressed = self.mixer._shift_button.is_pressed if hasattr(self, 'mixer') else False
  threshold = 0.15 if is_shift_pressed else 0.05
  ```

## 3. Debugging Ableton Scripts
**There is no console or IDE to show errors.** If a script has a syntax error or a runtime exception, Ableton simply stops executing that specific part of the script, and the control stops working.

- **The Log File is your only friend.**
  - Location on Mac: `~/Library/Preferences/Ableton/Live 12.x/Log.txt`
  - Location on Windows: `\Users\[Username]\AppData\Roaming\Ableton\Live 12.x\Preferences\Log.txt`
- **Use the `logging` module:**
  ```python
  import logging
  logger = logging.getLogger(__name__)
  logger.info("Some variable: {}".format(variable))
  logger.error("Exception: {}".format(str(e)))
  ```
- **Live 12 removes `self.application().view.show_message` (mostly).**
  - Don't rely on the status bar in Live 12 to debug. Always output to `Log.txt`.

## 4. Deployment
To test a script, you must:
1. Compile the script: `python3 -m py_compile *.py`
2. Move it to the User Library: `~/Music/Ableton/User Library/Remote Scripts/AAMinilabMk2_Live12`
3. Restart Ableton or reload the script in the Link/MIDI preferences.

Good luck!
