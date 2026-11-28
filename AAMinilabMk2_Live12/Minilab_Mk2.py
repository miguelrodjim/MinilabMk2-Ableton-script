from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
from pathlib import Path
import sys
import time

from ableton.v2.control_surface import ControlSurface, Layer
from ableton.v2.control_surface.component import Component
from _Arturia.ArturiaControlSurface import LIVE_MODE_MSG_HEAD, ON_VALUE, OFF_VALUE, SETUP_MSG_PREFIX, LOAD_MEMORY_COMMAND, SETUP_MSG_SUFFIX

from .Elements import Elements
from .CustomControlComponent import SimpleTransportComponent, SimpleMixerComponent, SimpleDeviceComponent, PluginPushComponent
from .AutoColorComponent import AutoColorComponent

logger = logging.getLogger(__name__)


def _find_control_room_rack(devices, inside_control_room=False):
    for device in devices:
        if device.can_have_chains:
            name = device.name.strip().casefold()
            is_control_room = name == 'control room'
            is_monitor = inside_control_room and name == 'monitor'
            if (is_control_room or is_monitor) and len(device.chains) == 3:
                yield device
            for chain in device.chains:
                yield from _find_control_room_rack(chain.devices, inside_control_room or is_control_room)


def _control_room_selector(rack):
    selector = rack.chain_selector
    if selector is not None:
        return selector
    return next((parameter for parameter in rack.parameters
                 if parameter.original_name.casefold() == 'chain selector'), None)


def _active_monitor_correction(racks):
    if len(racks) != 1 or not racks[0].is_active:
        return ''
    rack = racks[0]
    selector = _control_room_selector(rack)
    if selector is None:
        return ''
    profiles = (('HS7', {'hs7', 'yamahahs7'}), ('DT-990 PRO', {'990pro', 'dt990pro'}))
    position = int(selector.value)
    if not 0 <= position < len(profiles):
        return ''
    label, names = profiles[position]
    for chain in rack.chains:
        if chain.name.casefold().replace('-', '').replace(' ', '') in names and not chain.mute:
            if any(device.is_active and 'pro-q' in device.name.casefold() for device in chain.devices):
                return label
    return ''


class Minilab_Mk2(ControlSurface):
    """
    Minilab Mk2 Control Surface script for Ableton Live 12.
    Uses custom bypass components to avoid Live 12 v2 bugs.
    """

    def __init__(self, c_instance, *a, **k):
        self._monitor_export_request = None
        self._monitor_status_path = None
        self._monitor_status = None
        self._next_monitor_status_check = 0
        if sys.platform == 'darwin':
            cache = Path.home() / 'Library' / 'Caches' / 'midid'
            self._monitor_export_request = cache / ('export-{}.request'.format(os.getpid()))
            self._monitor_status_path = cache / ('monitor-{}.status'.format(os.getpid()))
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
            self._device.set_encoder_elements(self._elements.encoders)
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

            self._elements.pad_15.add_value_listener(self._on_control_room_pad)
            self._elements.pad_15.send_value(20)

            # Announce connection
            self.show_message('Minilab Mk2 Live 12 Loaded!')

    def _on_control_room_pad(self, value):
        if not value:
            return
        self._set_control_room_position()

    def update_display_hook(self):
        super(Minilab_Mk2, self).update_display_hook()
        request = self._monitor_export_request
        if request is None:
            return
        self._publish_monitor_status()
        try:
            stamp = request.stat().st_mtime
            request.unlink()
        except OSError:
            return
        if 0 <= time.time() - stamp < 2:
            self._set_control_room_position(for_export=True)

    def _publish_monitor_status(self):
        now = time.monotonic()
        if now < self._next_monitor_status_check:
            return
        self._next_monitor_status_check = now + 0.25
        try:
            racks = list(_find_control_room_rack(self.song.master_track.devices))
            status = _active_monitor_correction(racks)
        except (RuntimeError, ValueError):
            status = ''
        if status == self._monitor_status:
            return
        try:
            path = self._monitor_status_path
            path.parent.mkdir(exist_ok=True)
            temporary = path.with_suffix('.tmp')
            temporary.write_text(status, encoding='utf-8')
            temporary.replace(path)
            self._monitor_status = status
        except OSError:
            logger.warning('Control Room: could not update the monitor indicator')
            self._next_monitor_status_check = now + 2

    def _set_control_room_position(self, for_export=False):

        racks = list(_find_control_room_rack(self.song.master_track.devices))
        if len(racks) != 1:
            if not for_export or racks:
                self.show_message('Control Room: expected one three-chain MONITOR or CONTROL ROOM rack')
            return

        rack = racks[0]
        selector = _control_room_selector(rack)
        if selector is None:
            logger.warning('Control Room: Chain Selector not exposed. Rack parameters: %s',
                           [parameter.original_name for parameter in rack.parameters])
            self.show_message('Control Room: Live did not expose the Chain Selector')
            return

        try:
            position = int(selector.value)
            if for_export and position == 2:
                return
            next_position = 2 if for_export else (position + 1 if 0 <= position <= 2 else 0) % 3
            if selector.is_enabled:
                selector.value = next_position
            else:
                macro = next((parameter for parameter in rack.parameters
                              if parameter.name.strip().casefold() in ('corrección', 'correccion')), None)
                if macro is None or not macro.is_enabled:
                    self.show_message('Control Room: CORRECCION macro is unavailable')
                    return
                # Values from the existing HS7, DT-990 PRO and none variations.
                macro.value = (0, 61, 127)[next_position]
                # Live applies macro mappings after the MIDI callback returns.
                verify_delay = 3 if for_export else 1
                self.schedule_message(verify_delay, lambda: self._show_control_room_position(rack, selector, for_export))
                return
            self._show_control_room_position(rack, selector, for_export)
        except (RuntimeError, ValueError):
            logger.exception('Control Room: could not write the Chain Selector')
            self.show_message('Control Room: Live did not accept the Chain Selector change')

    def _show_control_room_position(self, rack, selector, for_export=False):
        position = int(selector.value)
        if for_export:
            if position == 2:
                logger.info('Control Room set to none before export')
                self.show_message('Control Room: none (export)')
            else:
                logger.warning('Control Room could not switch to none before export (selector=%s)', position)
                self.show_message('Control Room: correction may still be active')
        else:
            self.show_message('{}: Chain Selector {}'.format(rack.name, position))

    def disconnect(self):
        if self._monitor_status_path is not None:
            try:
                self._monitor_status_path.unlink(missing_ok=True)
            except OSError:
                logger.warning('Control Room: could not clear the monitor indicator')
        if self._elements.pad_15.value_has_listener(self._on_control_room_pad):
            self._elements.pad_15.remove_value_listener(self._on_control_room_pad)
        self._send_midi(LIVE_MODE_MSG_HEAD + (OFF_VALUE,) + SETUP_MSG_SUFFIX)
        super(Minilab_Mk2, self).disconnect()
