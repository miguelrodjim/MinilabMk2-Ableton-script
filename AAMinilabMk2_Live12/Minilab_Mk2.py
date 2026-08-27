from __future__ import absolute_import, print_function, unicode_literals

from ableton.v2.control_surface import ControlSurface, Layer
from ableton.v2.control_surface.component import Component
from _Arturia.ArturiaControlSurface import LIVE_MODE_MSG_HEAD, ON_VALUE, OFF_VALUE, SETUP_MSG_PREFIX, LOAD_MEMORY_COMMAND, SETUP_MSG_SUFFIX

from .Elements import Elements
from .CustomControlComponent import SimpleTransportComponent, SimpleMixerComponent, SimpleDeviceComponent, CustomControlComponent


class DebugComponent(Component):
    def __init__(self, encoders, show_message_fn, *a, **k):
        super(DebugComponent, self).__init__(*a, **k)
        self._encoders = encoders
        self._show_message = show_message_fn
        for i, enc in enumerate(self._encoders):
            if enc is not None:
                enc.add_value_listener(lambda value, index=i: self._on_value(value, index))
            
    def _on_value(self, value, index):
        msg = "Knob {} (CC {}) turned: {}".format(index + 1, self._encoders[index].message_identifier(), value)
        self._show_message(msg)
        import logging
        logging.getLogger(__name__).info(msg)


class Minilab_Mk2(ControlSurface):
    """
    Minilab Mk2 Control Surface script for Ableton Live 12.
    Uses custom bypass components to avoid Live 12 v2 bugs.
    """

    def __init__(self, c_instance, *a, **k):
        super(Minilab_Mk2, self).__init__(c_instance, *a, **k)

        with self.component_guard():
            self._elements = Elements()
            
            # Transport
            self._transport = SimpleTransportComponent()
            self._transport.name = 'Transport'
            self._transport.set_play_element(self._elements.pad_play)
            self._transport.set_stop_element(self._elements.pad_stop)
            self._transport.set_record_element(self._elements.pad_record)
            self._transport.set_metronome_element(self._elements.encoder_9_button)
            self._transport.set_enabled(True)

            # Mixer
            self._mixer = SimpleMixerComponent()
            self._mixer.name = 'Mixer'
            
            # Bind Pads
            self._mixer.set_arm_element(self._elements.pad_arm)
            self._mixer.set_mute_element(self._elements.pad_mute)
            self._mixer.set_solo_element(self._elements.pad_solo)
            self._mixer.set_shift_button(self._elements.pad_shift)
            
            # Bind Knobs 9-12
            self._mixer.set_cue_volume_element(self._elements.encoder_cue_volume)
            self._mixer.set_pan_element(self._elements.encoder_pan)
            self._mixer.set_volume_element(self._elements.encoder_volume)
            self._mixer.set_enabled(True)

            # Custom Controls (Clip Gain, Scroll)
            self._custom = CustomControlComponent()
            self._custom.name = 'CustomControls'
            self._custom.mixer = self._mixer
            self._custom.set_clip_gain_element(self._elements.encoder_clip_gain)
            self._custom.set_scroll_v_element(self._elements.encoder_scroll_v)
            self._custom.set_scroll_h_element(self._elements.encoder_scroll_h)
            self._custom.set_enabled(True)

            # Device
            self._device = SimpleDeviceComponent()
            self._device.name = 'Device'
            self._device.mixer = self._mixer
            self._device.set_encoder_elements(self._elements.encoders[0:8])
            self._device.set_enabled(True)

            # Debugger
            self._debug = DebugComponent(self._elements.encoders, self.show_message)
            self._debug.name = 'Debug'
            self._debug.set_enabled(True)

            # Force hardware into Preset 8 (Ableton Mode)
            self._send_midi(SETUP_MSG_PREFIX + (LOAD_MEMORY_COMMAND, 7) + SETUP_MSG_SUFFIX)

            # Activate Arturia Live Mode for the hardware (enables pads 9-16 as CCs)
            self._send_midi(LIVE_MODE_MSG_HEAD + (ON_VALUE,) + SETUP_MSG_SUFFIX)

            # Keep Pad 15 (unassigned) lit in Cyan (17) for aesthetics
            self._elements.pad_15.send_value(17)

            # Announce connection
            self.show_message('Minilab Mk2 Live 12 Loaded!')

    def receive_midi(self, midi_bytes):
        # Show exactly what MIDI bytes are being received in the status bar
        if len(midi_bytes) >= 2:
            msg = "MIDI RCV: {} {} {}".format(midi_bytes[0], midi_bytes[1], midi_bytes[2] if len(midi_bytes) > 2 else "")
            self.show_message(msg)
        super(Minilab_Mk2, self).receive_midi(midi_bytes)

    def disconnect(self):
        self._send_midi(LIVE_MODE_MSG_HEAD + (OFF_VALUE,) + SETUP_MSG_SUFFIX)
        super(Minilab_Mk2, self).disconnect()
