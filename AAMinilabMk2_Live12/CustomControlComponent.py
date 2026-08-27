from __future__ import absolute_import, print_function, unicode_literals

import Live
from ableton.v2.control_surface.component import Component
from ableton.v2.control_surface.control import EncoderControl, ButtonControl
from ableton.v2.base import listens, task

class SimpleTransportComponent(Component):
    """
    Custom Transport component that directly manipulates the Live song object
    and updates pad colors dynamically.
    """
    _play_button = ButtonControl(color='Transport.PlayOn')
    _stop_button = ButtonControl(color='DefaultButton.On') # White always
    _record_button = ButtonControl(color='Transport.RecordOn')
    _metronome_button = ButtonControl(color='Transport.MetronomeOn') # Cyan
    _loop_button = ButtonControl(color='Transport.PlayOff')
    _tap_tempo_button = ButtonControl(color='Transport.TapTempo', pressed_color='Transport.TapTempo')

    def __init__(self, *a, **k):
        super(SimpleTransportComponent, self).__init__(*a, **k)
        self._on_playing_changed.subject = self.song
        self._on_record_mode_changed.subject = self.song
        self._on_metronome_changed.subject = self.song
        self._on_loop_changed.subject = self.song
        
        self._blink_state = False
        self._blink_task = self._tasks.add(task.loop(
            task.sequence(
                task.run(self._toggle_blink),
                task.wait(0.3)
            )
        ))
        # Remove kill() so it runs constantly and we update states inside _toggle_blink
        
        self._update_all_colors()

    def set_play_element(self, element):
        self._play_button.set_control_element(element)

    def set_stop_element(self, element):
        self._stop_button.set_control_element(element)

    def set_record_element(self, element):
        self._record_button.set_control_element(element)

    def set_metronome_element(self, element):
        self._metronome_button.set_control_element(element)

    def set_loop_element(self, element):
        self._loop_button.set_control_element(element)

    def set_tap_tempo_element(self, element):
        self._tap_tempo_button.set_control_element(element)

    @_play_button.pressed
    def _on_play_pressed(self, button):
        self.song.is_playing = not self.song.is_playing

    @_stop_button.pressed
    def _on_stop_pressed(self, button):
        self.song.stop_playing()

    @_record_button.pressed
    def _on_record_pressed(self, button):
        self.song.record_mode = not self.song.record_mode

    @_metronome_button.pressed
    def _on_metronome_pressed(self, button):
        self.song.metronome = not self.song.metronome

    @_loop_button.pressed
    def _on_loop_pressed(self, button):
        self.song.loop = not self.song.loop

    @_tap_tempo_button.pressed
    def _on_tap_tempo_pressed(self, button):
        try:
            self.song.tap_tempo()
        except AttributeError:
            pass

    # --- Observers for Dynamic Colors ---
    def _toggle_blink(self):
        self._blink_state = not self._blink_state
        
        # Record Button Blinking
        if self.song.record_mode:
            self._record_button.color = 'Transport.RecordOn' if self._blink_state else 'Transport.PlayOff'
        else:
            self._record_button.color = 'Transport.RecordOn' # Red by default

        # Play Button Blinking
        if self.song.is_playing:
            self._play_button.color = 'Transport.PlayOn' if self._blink_state else 'Transport.PlayOff'
            self._stop_button.color = 'DefaultButton.On' if self._blink_state else 'Transport.PlayOff'
        else:
            self._play_button.color = 'Transport.PlayOn' # Green by default
            self._stop_button.color = 'DefaultButton.On' # White by default
            
        # Metronome Button Blinking
        if self.song.metronome:
            self._metronome_button.color = 'Transport.MetronomeOn' if self._blink_state else 'Transport.PlayOff'
        else:
            self._metronome_button.color = 'Transport.MetronomeOn' # Cyan by default

    @listens('is_playing')
    def _on_playing_changed(self):
        # We handle Play button color in _toggle_blink
        pass

    @listens('record_mode')
    def _on_record_mode_changed(self):
        # We handle Record button color in _toggle_blink
        pass

    @listens('metronome')
    def _on_metronome_changed(self):
        # We handle Metronome button color in _toggle_blink
        pass

    @listens('loop')
    def _on_loop_changed(self):
        self._loop_button.color = 'Transport.LoopOn' if self.song.loop else 'Transport.LoopOff'
        
    def _update_all_colors(self):
        self._on_playing_changed()
        self._on_record_mode_changed()
        self._on_metronome_changed()
        self._on_loop_changed()


class SimpleMixerComponent(Component):
    """
    Custom Mixer component for selected-track volume, pan, mute, solo, arm, and cue volume.
    """
    _volume_encoder = EncoderControl()
    _pan_encoder = EncoderControl()
    _mute_button = ButtonControl(color='Transport.StopOn', pressed_color='Transport.StopOn') # Yellow
    _solo_button = ButtonControl(color='Transport.LoopOn', pressed_color='Transport.LoopOn') # Blue
    _arm_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.On') # White
    _cue_volume_encoder = EncoderControl()
    _shift_button = ButtonControl(color='Transport.ShiftOn', pressed_color='Transport.ShiftOn') # Purple

    def __init__(self, *a, **k):
        super(SimpleMixerComponent, self).__init__(*a, **k)
        
        self._blink_state = False
        self._blink_task = self._tasks.add(task.loop(
            task.sequence(
                task.run(self._toggle_blink),
                task.wait(0.3)
            )
        ))
        
        self._on_selected_track_changed.subject = self.song.view
        self._on_selected_track_changed()

    def set_shift_button(self, element):
        self._shift_button.set_control_element(element)

    def set_volume_element(self, element):
        self._volume_encoder.set_control_element(element)

    def set_pan_element(self, element):
        self._pan_encoder.set_control_element(element)

    def set_mute_element(self, element):
        self._mute_button.set_control_element(element)

    def set_solo_element(self, element):
        self._solo_button.set_control_element(element)

    def set_arm_element(self, element):
        self._arm_button.set_control_element(element)

    def set_cue_volume_element(self, element):
        self._cue_volume_encoder.set_control_element(element)

    def _get_selected_track(self):
        return self.song.view.selected_track

    @_volume_encoder.value
    def _on_volume_changed(self, value, encoder):
        track = self._get_selected_track()
        if track:
            multiplier = 0.003 if self._shift_button.is_pressed else 0.03
            delta = value * multiplier
            track.mixer_device.volume.value = max(0.0, min(1.0, track.mixer_device.volume.value + delta))

    @_pan_encoder.value
    def _on_pan_changed(self, value, encoder):
        track = self._get_selected_track()
        if track:
            multiplier = 0.005 if self._shift_button.is_pressed else 0.05
            delta = value * multiplier
            track.mixer_device.panning.value = max(-1.0, min(1.0, track.mixer_device.panning.value + delta))

    @_mute_button.pressed
    def _on_mute_pressed(self, button):
        track = self._get_selected_track()
        if track and track != self.song.master_track:
            track.mute = not track.mute

    @_solo_button.pressed
    def _on_solo_pressed(self, button):
        track = self._get_selected_track()
        if track and track != self.song.master_track:
            if self._shift_button.is_pressed:
                # Add to solo (Non-exclusive)
                track.solo = not track.solo
            else:
                # Exclusive solo
                will_solo = not track.solo
                if will_solo:
                    for t in self.song.tracks:
                        if t != track:
                            t.solo = False
                    for t in self.song.return_tracks:
                        if t != track:
                            t.solo = False
                track.solo = will_solo

    @_arm_button.pressed
    def _on_arm_pressed(self, button):
        track = self._get_selected_track()
        if track and track.can_be_armed:
            track.arm = not track.arm

    @_cue_volume_encoder.value
    def _on_cue_volume_changed(self, value, encoder):
        delta = value * 0.01
        cue = self.song.master_track.mixer_device.cue_volume
        cue.value = max(0.0, min(1.0, cue.value + delta))

    # --- Listeners for dynamic colors ---
    @listens('selected_track')
    def _on_selected_track_changed(self):
        track = self.song.view.selected_track
        self._on_solo_changed.subject = track
        self._on_mute_changed.subject = track
        self._on_arm_changed.subject = track
        self._on_solo_changed()
        self._on_mute_changed()
        self._on_arm_changed()

    def _toggle_blink(self):
        self._blink_state = not self._blink_state
        track = self.song.view.selected_track
        if track and track != self.song.master_track and track.solo:
            self._solo_button.color = 'Transport.LoopOn' if self._blink_state else 'Transport.PlayOff'
        else:
            self._solo_button.color = 'Transport.LoopOn' # Default Blue

    @listens('solo')
    def _on_solo_changed(self):
        # We handle Solo button color in _toggle_blink
        pass

    @listens('mute')
    def _on_mute_changed(self):
        track = self.song.view.selected_track
        if track and track != self.song.master_track:
            self._mute_button.color = 'Transport.PlayOff' if track.mute else 'Transport.StopOn' # Yellow when NOT muted, Off when muted
        else:
            self._mute_button.color = 'Transport.StopOn' # Yellow by default

    @listens('arm')
    def _on_arm_changed(self):
        track = self.song.view.selected_track
        if track and track.can_be_armed:
            self._arm_button.color = 'Transport.RecordOn' if track.arm else 'DefaultButton.On' # Red when armed, White otherwise
        else:
            self._arm_button.color = 'DefaultButton.On' # White by default


class SimpleDeviceComponent(Component):
    """
    Custom Device component — maps 8 encoders to the first 8 parameters
    of whatever device is currently selected on the selected track.
    """
    _p1 = EncoderControl()
    _p2 = EncoderControl()
    _p3 = EncoderControl()
    _p4 = EncoderControl()
    _p5 = EncoderControl()
    _p6 = EncoderControl()
    _p7 = EncoderControl()
    _p8 = EncoderControl()

    def __init__(self, *a, **k):
        super(SimpleDeviceComponent, self).__init__(*a, **k)
        self._encoders_list = [
            self._p1, self._p2, self._p3, self._p4,
            self._p5, self._p6, self._p7, self._p8
        ]

    def set_encoder_elements(self, elements):
        for i, control in enumerate([
            self._p1, self._p2, self._p3, self._p4,
            self._p5, self._p6, self._p7, self._p8
        ]):
            if i < len(elements):
                control.set_control_element(elements[i])

    def _get_device_params(self):
        track = self.song.view.selected_track
        if track and track.devices:
            device = track.view.selected_device or track.devices[0]
            return list(device.parameters)
        return []

    def _adjust_param(self, index, value):
        params = self._get_device_params()
        # index+1 because params[0] is always "Device On/Off"
        param_index = index + 1
        if param_index < len(params):
            p = params[param_index]
            if not p.is_quantized:
                delta = (p.max - p.min) * 0.01 * value
                p.value = max(p.min, min(p.max, p.value + delta))
            else:
                if value > 0:
                    p.value = min(p.max, p.value + 1)
                else:
                    p.value = max(p.min, p.value - 1)

    @_p1.value
    def _on_p1(self, value, encoder): self._adjust_param(0, value)
    @_p2.value
    def _on_p2(self, value, encoder): self._adjust_param(1, value)
    @_p3.value
    def _on_p3(self, value, encoder): self._adjust_param(2, value)
    @_p4.value
    def _on_p4(self, value, encoder): self._adjust_param(3, value)
    @_p5.value
    def _on_p5(self, value, encoder): self._adjust_param(4, value)
    @_p6.value
    def _on_p6(self, value, encoder): self._adjust_param(5, value)
    @_p7.value
    def _on_p7(self, value, encoder): self._adjust_param(6, value)
    @_p8.value
    def _on_p8(self, value, encoder): self._adjust_param(7, value)


class CustomControlComponent(Component):
    """
    Handles custom encoder mappings: Clip Gain and Scrolling.
    """
    _clip_gain_encoder = EncoderControl()
    _scroll_v_encoder = EncoderControl()
    _scroll_h_encoder = EncoderControl()

    def __init__(self, *a, **k):
        super(CustomControlComponent, self).__init__(*a, **k)
        self._scroll_h_accumulator = 0.0
        self._scroll_v_accumulator = 0.0

    def set_clip_gain_element(self, element):
        self._clip_gain_encoder.set_control_element(element)

    def set_scroll_v_element(self, element):
        self._scroll_v_encoder.set_control_element(element)

    def set_scroll_h_element(self, element):
        self._scroll_h_encoder.set_control_element(element)

    @_clip_gain_encoder.value
    def _on_clip_gain(self, value, encoder):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Clip Gain Turn: {}".format(value))
        clip = self.song.view.detail_clip
        if clip:
            logger.info("Clip: {}, is_audio_clip: {}".format(clip, getattr(clip, 'is_audio_clip', False) if clip else None))
            if clip.is_audio_clip:
                delta = value * 0.05
                try:
                    clip.gain = max(0.0, clip.gain + delta)
                    logger.info("Gain set to: {:.2f}".format(clip.gain))
                except Exception as e:
                    logger.error("Error setting gain: {}".format(str(e)))
        else:
            logger.info("No detail_clip selected.")

    @_scroll_v_encoder.value
    def _on_scroll_v(self, value, encoder):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Knob 15 (Scroll V) Turn: {}".format(value))
        
        # Check if Shift is pressed via the mixer reference
        is_shift_pressed = False
        if hasattr(self, 'mixer') and self.mixer:
            is_shift_pressed = self.mixer._shift_button.is_pressed
        
        self._scroll_v_accumulator += value
        
        # If Shift is pressed, require more physical rotation (higher threshold)
        threshold = 0.15 if is_shift_pressed else 0.05
        
        if abs(self._scroll_v_accumulator) >= threshold:
            try:
                # Always jump by 1 full bar
                bar_length = float(self.song.signature_numerator)
                delta = bar_length if self._scroll_v_accumulator > 0 else -bar_length
                
                new_time = max(0.0, self.song.current_song_time + delta)
                self.song.current_song_time = new_time
                logger.info("Scrubbed to: {} (Shift: {})".format(new_time, is_shift_pressed))
            except Exception as e:
                logger.error("Scrub error: {}".format(str(e)))
            
            if self._scroll_v_accumulator > 0:
                self._scroll_v_accumulator -= threshold
            else:
                self._scroll_v_accumulator += threshold

    @_scroll_h_encoder.value
    def _on_scroll_h(self, value, encoder):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Knob 16 (Scroll H) Turn: {}".format(value))
        
        self._scroll_h_accumulator += value
        
        # Increase threshold to 0.15 (approx 10 physical clicks) to make it much slower and more controlled
        threshold = 0.15
        
        if abs(self._scroll_h_accumulator) >= threshold:
            try:
                tracks = list(self.song.visible_tracks)
                current_track = self.song.view.selected_track
                if current_track in tracks:
                    index = tracks.index(current_track)
                    if self._scroll_h_accumulator > 0 and index < len(tracks) - 1:
                        self.song.view.selected_track = tracks[index + 1]
                    elif self._scroll_h_accumulator < 0 and index > 0:
                        self.song.view.selected_track = tracks[index - 1]
            except Exception:
                pass
            
            if self._scroll_h_accumulator > 0:
                self._scroll_h_accumulator -= threshold
            else:
                self._scroll_h_accumulator += threshold
