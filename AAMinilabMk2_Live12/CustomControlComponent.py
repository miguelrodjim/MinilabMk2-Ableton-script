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
    _mute_button = ButtonControl(color='Transport.StopOn', pressed_color='Transport.StopOn') # Yellow
    _solo_button = ButtonControl(color='Transport.SoloOn', pressed_color='Transport.SoloOn') # Blue
    _arm_button = ButtonControl(color='DefaultButton.On', pressed_color='DefaultButton.On') # White
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

    def set_mute_element(self, element):
        self._mute_button.set_control_element(element)

    def set_solo_element(self, element):
        self._solo_button.set_control_element(element)

    def set_arm_element(self, element):
        self._arm_button.set_control_element(element)

    def _get_selected_track(self):
        return self.song.view.selected_track

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
            self._solo_button.color = 'Transport.SoloOn' if self._blink_state else 'Transport.PlayOff'
        else:
            self._solo_button.color = 'Transport.SoloOn' # Default Blue

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
    Custom Device component — maps 16 encoders to device parameters.
    Encoder pushes (Knob 1 push CC 113, Knob 9 push CC 115) are released/unassigned here
    and reserved for future per-plugin profiles.
    """
    _p1 = EncoderControl()
    _p2 = EncoderControl()
    _p3 = EncoderControl()
    _p4 = EncoderControl()
    _p5 = EncoderControl()
    _p6 = EncoderControl()
    _p7 = EncoderControl()
    _p8 = EncoderControl()
    _p9 = EncoderControl()
    _p10 = EncoderControl()
    _p11 = EncoderControl()
    _p12 = EncoderControl()
    _p13 = EncoderControl()
    _p14 = EncoderControl()
    _p15 = EncoderControl()
    _p16 = EncoderControl()

    def __init__(self, *a, **k):
        super(SimpleDeviceComponent, self).__init__(*a, **k)
        self._encoders_list = [
            self._p1, self._p2, self._p3, self._p4,
            self._p5, self._p6, self._p7, self._p8,
            self._p9, self._p10, self._p11, self._p12,
            self._p13, self._p14, self._p15, self._p16
        ]

    def set_encoder_elements(self, elements):
        for i, control in enumerate([
            self._p1, self._p2, self._p3, self._p4,
            self._p5, self._p6, self._p7, self._p8,
            self._p9, self._p10, self._p11, self._p12,
            self._p13, self._p14, self._p15, self._p16
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
                is_shift_pressed = False
                if hasattr(self, 'mixer') and self.mixer:
                    is_shift_pressed = self.mixer._shift_button.is_pressed

                multiplier = 0.005 if is_shift_pressed else 0.10
                delta = (p.max - p.min) * multiplier * value
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
    @_p9.value
    def _on_p9(self, value, encoder): self._adjust_param(8, value)
    @_p10.value
    def _on_p10(self, value, encoder): self._adjust_param(9, value)
    @_p11.value
    def _on_p11(self, value, encoder): self._adjust_param(10, value)
    @_p12.value
    def _on_p12(self, value, encoder): self._adjust_param(11, value)
    @_p13.value
    def _on_p13(self, value, encoder): self._adjust_param(12, value)
    @_p14.value
    def _on_p14(self, value, encoder): self._adjust_param(13, value)
    @_p15.value
    def _on_p15(self, value, encoder): self._adjust_param(14, value)
    @_p16.value
    def _on_p16(self, value, encoder): self._adjust_param(15, value)


class PluginProfile(object):
    """
    Base class for plugin-specific push-button profiles.
    """
    def matches_device(self, device):
        raise NotImplementedError

    def handle_button_press(self, button_id, device, logger):
        raise NotImplementedError


class FabFilterProQ3Profile(PluginProfile):
    """
    Plugin profile for FabFilter Pro-Q 3.
    Binds:
    - encoder_1_button / CC 113 -> 'Band 1 Enabled'
    - encoder_9_button / CC 115 -> 'Band 6 Enabled'
    """
    BUTTON_TO_PARAM = {
        'encoder_1_button': 'Band 1 Enabled',
        'encoder_9_button': 'Band 6 Enabled',
    }

    def matches_device(self, device):
        if not device:
            return False
        names_to_check = []
        for attr in ('name', 'class_name', 'class_display_name'):
            val = getattr(device, attr, None)
            if val and isinstance(val, (str, type(u''))):
                names_to_check.append(val.lower())

        for n in names_to_check:
            if 'pro-q 3' in n or 'pro-q3' in n:
                return True
            if 'pro-q' in n and '3' in n:
                return True
            if 'fabfilter pro-q' in n and '3' in n:
                return True
        return False

    def handle_button_press(self, button_id, device, logger):
        param_name = self.BUTTON_TO_PARAM.get(button_id)
        if not param_name:
            if logger:
                logger.warning("Pro-Q 3 Profile: Unhandled button '{}'".format(button_id))
            return False

        target_param = None
        if hasattr(device, 'parameters'):
            for p in device.parameters:
                p_name = getattr(p, 'name', None)
                p_orig_name = getattr(p, 'original_name', None)
                if p_name == param_name or p_orig_name == param_name:
                    target_param = p
                    break

        dev_name = getattr(device, 'name', getattr(device, 'class_name', 'Pro-Q 3'))

        if target_param is None:
            if logger:
                logger.warning("Pro-Q 3 Profile: Parameter '{}' is not exposed on device '{}'".format(param_name, dev_name))
            return False

        try:
            mid_val = (target_param.min + target_param.max) / 2.0
            if target_param.value > mid_val:
                target_param.value = target_param.min
            else:
                target_param.value = target_param.max

            if logger:
                logger.info("Pro-Q 3 Profile: Toggled '{}' to {} on device '{}'".format(param_name, target_param.value, dev_name))
            return True
        except Exception as e:
            if logger:
                logger.error("Pro-Q 3 Profile: Failed toggling '{}' on device '{}': {}".format(param_name, dev_name, str(e)))
            return False


class FabFilterProC2Profile(PluginProfile):
    """
    Plugin profile for FabFilter Pro-C 2.
    Binds:
    - encoder_1_button / CC 113 -> 'Auto Gain'
    - encoder_9_button / CC 115 -> 'Auto Release'
    """
    BUTTON_TO_PARAM = {
        'encoder_1_button': 'Auto Gain',
        'encoder_9_button': 'Auto Release',
    }

    def matches_device(self, device):
        if not device:
            return False
        names_to_check = []
        for attr in ('name', 'class_name', 'class_display_name'):
            val = getattr(device, attr, None)
            if val and isinstance(val, (str, type(u''))):
                names_to_check.append(val.lower())

        for n in names_to_check:
            if 'pro-q' in n:
                continue
            if 'pro-c 2' in n or 'pro-c2' in n:
                return True
            if ('pro-c' in n or 'proc' in n) and '2' in n and 'fabfilter' in n:
                return True
        return False

    def handle_button_press(self, button_id, device, logger):
        param_name = self.BUTTON_TO_PARAM.get(button_id)
        if not param_name:
            if logger:
                logger.warning("Pro-C 2 Profile: Unhandled button '{}'".format(button_id))
            return False

        target_param = None
        if hasattr(device, 'parameters'):
            for p in device.parameters:
                p_name = getattr(p, 'name', None)
                p_orig_name = getattr(p, 'original_name', None)
                if p_name == param_name or p_orig_name == param_name:
                    target_param = p
                    break

        dev_name = getattr(device, 'name', getattr(device, 'class_name', 'Pro-C 2'))

        if target_param is None:
            if logger:
                logger.warning("Pro-C 2 Profile: Parameter '{}' is not exposed on device '{}'".format(param_name, dev_name))
            return False

        try:
            mid_val = (target_param.min + target_param.max) / 2.0
            if target_param.value > mid_val:
                target_param.value = target_param.min
            else:
                target_param.value = target_param.max

            if logger:
                logger.info("Pro-C 2 Profile: Toggled '{}' to {} on device '{}'".format(param_name, target_param.value, dev_name))
            return True
        except Exception as e:
            if logger:
                logger.error("Pro-C 2 Profile: Failed toggling '{}' on device '{}': {}".format(param_name, dev_name, str(e)))
            return False


class UADxSSLEChannelStripProfile(PluginProfile):
    """
    Plugin profile for UADx SSL E Channel Strip.
    Binds:
    - encoder_1_button / CC 113 -> 'HF Bell'
    - encoder_9_button / CC 115 -> 'LF Bell'
    """
    BUTTON_TO_PARAM = {
        'encoder_1_button': 'HF Bell',
        'encoder_9_button': 'LF Bell',
    }

    def matches_device(self, device):
        if not device:
            return False
        names_to_check = []
        for attr in ('name', 'class_name', 'class_display_name'):
            val = getattr(device, attr, None)
            if val and isinstance(val, (str, type(u''))):
                names_to_check.append(val.lower())

        if not names_to_check:
            return False

        has_uad = any('uad' in n or 'uadx' in n for n in names_to_check)
        has_ssl_e = any(
            'ssl e channel strip' in n or
            ('ssl e' in n and 'channel strip' in n) or
            ('ssl' in n and 'e channel strip' in n) or
            ('ssl' in n and 'e-channel strip' in n)
            for n in names_to_check
        )

        return has_uad and has_ssl_e

    def handle_button_press(self, button_id, device, logger):
        param_name = self.BUTTON_TO_PARAM.get(button_id)
        if not param_name:
            if logger:
                logger.warning("UADx SSL E Channel Strip Profile: Unhandled button '{}'".format(button_id))
            return False

        target_param = None
        if hasattr(device, 'parameters'):
            for p in device.parameters:
                p_name = getattr(p, 'name', None)
                p_orig_name = getattr(p, 'original_name', None)
                if p_name == param_name or p_orig_name == param_name:
                    target_param = p
                    break

        dev_name = getattr(device, 'name', getattr(device, 'class_name', 'UADx SSL E Channel Strip'))

        if target_param is None:
            if logger:
                logger.warning("UADx SSL E Channel Strip Profile: Parameter '{}' is not exposed on device '{}'".format(param_name, dev_name))
            return False

        try:
            mid_val = (target_param.min + target_param.max) / 2.0
            if target_param.value > mid_val:
                target_param.value = target_param.min
            else:
                target_param.value = target_param.max

            if logger:
                logger.info("UADx SSL E Channel Strip Profile: Toggled '{}' to {} on device '{}'".format(param_name, target_param.value, dev_name))
            return True
        except Exception as e:
            if logger:
                logger.error("UADx SSL E Channel Strip Profile: Failed toggling '{}' on device '{}': {}".format(param_name, dev_name, str(e)))
            return False


class UADxLA6176ChannelStripProfile(PluginProfile):
    """
    Plugin profile for UADx LA-6176 Channel Strip.
    Binds:
    - encoder_1_button / CC 113 -> 'EQ Hi Freq'
    - encoder_9_button / CC 115 -> 'EQ Lo Freq'
    Cycles parameter through 3 states: [min, (min+max)/2, max].
    """
    BUTTON_TO_PARAM = {
        'encoder_1_button': 'EQ Hi Freq',
        'encoder_9_button': 'EQ Lo Freq',
    }

    def matches_device(self, device):
        if not device:
            return False
        names_to_check = []
        for attr in ('name', 'class_name', 'class_display_name'):
            val = getattr(device, attr, None)
            if val and isinstance(val, (str, type(u''))):
                names_to_check.append(val.lower())

        if not names_to_check:
            return False

        for n in names_to_check:
            if 'la-2a' in n or 'la2a' in n or 'la 2a' in n:
                return False

        has_uad = any('uad' in n or 'uadx' in n for n in names_to_check)
        has_6176 = any(
            'la-6176' in n or
            'la 6176' in n or
            '6176 channel strip' in n or
            '6176' in n
            for n in names_to_check
        )

        return has_uad and has_6176

    def handle_button_press(self, button_id, device, logger):
        param_name = self.BUTTON_TO_PARAM.get(button_id)
        if not param_name:
            if logger:
                logger.warning("UADx LA-6176 Channel Strip Profile: Unhandled button '{}'".format(button_id))
            return False

        target_param = None
        if hasattr(device, 'parameters'):
            for p in device.parameters:
                p_name = getattr(p, 'name', None)
                p_orig_name = getattr(p, 'original_name', None)
                if p_name == param_name or p_orig_name == param_name:
                    target_param = p
                    break

        dev_name = getattr(device, 'name', getattr(device, 'class_name', 'UADx LA-6176 Channel Strip'))

        if target_param is None:
            if logger:
                logger.warning("UADx LA-6176 Channel Strip Profile: Parameter '{}' is not exposed on device '{}'".format(param_name, dev_name))
            return False

        try:
            min_val = float(target_param.min)
            max_val = float(target_param.max)
            mid_val = min_val + (max_val - min_val) / 2.0
            states = [min_val, mid_val, max_val]

            curr_val = float(target_param.value)
            distances = [abs(curr_val - s) for s in states]
            closest_index = distances.index(min(distances))

            next_index = (closest_index + 1) % len(states)
            target_param.value = states[next_index]

            if logger:
                logger.info("UADx LA-6176 Channel Strip Profile: Cycled '{}' to {} on device '{}'".format(param_name, target_param.value, dev_name))
            return True
        except Exception as e:
            if logger:
                logger.error("UADx LA-6176 Channel Strip Profile: Failed cycling '{}' on device '{}': {}".format(param_name, dev_name, str(e)))
            return False


class PluginPushComponent(Component):
    """
    Component managing plugin-specific encoder push button profiles.
    """
    _encoder_1_button = ButtonControl()
    _encoder_9_button = ButtonControl()

    def __init__(self, *a, **k):
        super(PluginPushComponent, self).__init__(*a, **k)
        self._profiles = [
            FabFilterProQ3Profile(),
            FabFilterProC2Profile(),
            UADxSSLEChannelStripProfile(),
            UADxLA6176ChannelStripProfile(),
        ]

    def set_encoder_1_button(self, element):
        self._encoder_1_button.set_control_element(element)

    def set_encoder_9_button(self, element):
        self._encoder_9_button.set_control_element(element)

    @_encoder_1_button.pressed
    def _on_encoder_1_pressed(self, button):
        self._handle_push('encoder_1_button')

    @_encoder_9_button.pressed
    def _on_encoder_9_pressed(self, button):
        self._handle_push('encoder_9_button')

    def _get_selected_device(self):
        try:
            track = self.song.view.selected_track
            if track and hasattr(track, 'view') and track.view:
                return track.view.selected_device
        except Exception:
            pass
        return None

    def _handle_push(self, button_id):
        import logging
        logger = logging.getLogger(__name__)

        device = self._get_selected_device()
        if not device:
            logger.warning("Plugin Push: No device selected for push button '{}'".format(button_id))
            return

        matched_profile = None
        for profile in self._profiles:
            if profile.matches_device(device):
                matched_profile = profile
                break

        if not matched_profile:
            dev_name = getattr(device, 'name', getattr(device, 'class_name', 'Unknown Device'))
            logger.warning("Plugin Push: Selected device '{}' has no matching plugin profile".format(dev_name))
            return

        matched_profile.handle_button_press(button_id, device, logger)
