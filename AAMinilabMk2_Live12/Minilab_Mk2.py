from __future__ import absolute_import, print_function, unicode_literals

from ableton.v2.control_surface import ControlSurface, Layer
from ableton.v2.control_surface.component import Component
from _Arturia.ArturiaControlSurface import LIVE_MODE_MSG_HEAD, ON_VALUE, OFF_VALUE, SETUP_MSG_PREFIX, LOAD_MEMORY_COMMAND, SETUP_MSG_SUFFIX

from .Elements import Elements
from .CustomControlComponent import SimpleTransportComponent, SimpleMixerComponent, SimpleDeviceComponent, PluginPushComponent
from .AutoColorComponent import AutoColorComponent


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
            self._transport.set_enabled(True)

            # Mixer
            self._mixer = SimpleMixerComponent()
            self._mixer.name = 'Mixer'

            # Bind Pads
            self._mixer.set_arm_element(self._elements.pad_arm)
            self._mixer.set_mute_element(self._elements.pad_mute)
            self._mixer.set_solo_element(self._elements.pad_solo)
            self._mixer.set_shift_button(self._elements.pad_shift)

            self._mixer.set_enabled(True)

            # Device
            self._device = SimpleDeviceComponent()
            self._device.name = 'Device'
            self._device.mixer = self._mixer
            self._device.set_encoder_elements(self._elements.encoders[0:16])
            self._device.set_enabled(True)

            # Plugin Push Controls (FabFilter Pro-Q 3 profile)
            self._plugin_push = PluginPushComponent()
            self._plugin_push.name = 'PluginPush'
            self._plugin_push.set_encoder_1_button(self._elements.encoder_1_button)
            self._plugin_push.set_encoder_9_button(self._elements.encoder_9_button)
            self._plugin_push.set_enabled(True)

            # Auto-Color
            self._auto_color = AutoColorComponent()
            self._auto_color.name = 'AutoColor'
            self._auto_color.set_enabled(True)

            # Force hardware into Preset 8 (Ableton Mode)
            self._send_midi(SETUP_MSG_PREFIX + (LOAD_MEMORY_COMMAND, 7) + SETUP_MSG_SUFFIX)

            # Activate Arturia Live Mode for the hardware (enables pads 9-16 as CCs)
            self._send_midi(LIVE_MODE_MSG_HEAD + (ON_VALUE,) + SETUP_MSG_SUFFIX)

            # Keep Pad 15 (unassigned) lit in Cyan (20) for aesthetics
            self._elements.pad_15.send_value(20)

            # Announce connection
            self.show_message('Minilab Mk2 Live 12 Loaded!')

    def disconnect(self):
        self._send_midi(LIVE_MODE_MSG_HEAD + (OFF_VALUE,) + SETUP_MSG_SUFFIX)
        super(Minilab_Mk2, self).disconnect()
