from __future__ import absolute_import, print_function, unicode_literals

import Live
from ableton.v2.control_surface.elements import ButtonElement, EncoderElement, ButtonMatrixElement
from ableton.v2.control_surface import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from ableton.v2.control_surface.elements.color import Color
from ableton.v2.control_surface.skin import Skin

class Colors:
    class DefaultButton:
        On = Color(127) # White
        Off = Color(0)  # Off
        Disabled = Color(0)

    class Transport:
        PlayOn = Color(4)        # Green
        PlayOff = Color(0)       # Off
        StopOn = Color(5)        # Yellow
        StopOff = Color(0)       # Off
        RecordOn = Color(1)      # Red
        RecordOff = Color(0)     # Off
        LoopOn = Color(16)       # Blue
        LoopOff = Color(0)       # Off
        MetronomeOn = Color(20)  # Magenta / Purple
        MetronomeOff = Color(0)  # Off
        TapTempo = Color(127)    # White
        ShiftOn = Color(17)      # Cyan

skin = Skin(Colors)

class MinilabPadButtonElement(ButtonElement):
    def __init__(self, is_momentary, msg_type, channel, identifier, pad_index, *a, **k):
        super(MinilabPadButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, *a, **k)
        self._pad_index = pad_index

    def send_value(self, value, force=False, channel=None):
        if value is None:
            return
            
        try:
            val = int(value)
        except (TypeError, ValueError):
            val = 0
            
        # Call super with the safe int to avoid C++ crashes if a string was passed by mistake
        super(MinilabPadButtonElement, self).send_value(val, force, channel)
        
        sysex_msg = (240, 0, 32, 107, 127, 66, 2, 0, 16, 112 + self._pad_index, val, 247)
        self.send_midi(sysex_msg)

# MIDI Channels (0-indexed in Python: 9 -> 9, 1 -> 1)
# The original script used channel 9 for pads (which is MIDI channel 10, typically drums)
# and channel 1 for encoders. But wait, in the framework, channels are 0-15.
# If original script used `self.pad_channel = 9`, it means MIDI Channel 10.
# `self.encoder_msg_channel = 1` means MIDI Channel 2.
PAD_CHANNEL = 9
ENCODER_CHANNEL = 1

# Note mappings for Pads 1-8 (Bank 1)
PAD_NOTES = [36, 37, 38, 39, 40, 41, 42, 43]

# CC mappings for Pads 9-16 (Bank 2) used for Transport/Control
PAD_CCS_BANK2 = [56, 57, 58, 59, 60, 61, 62, 63]

# CC mappings for Encoders 1-16
ENCODER_CCS = (22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 52, 53, 54, 55)

# Clickable Encoder CCs
ENCODER_PUSH_1 = 113
ENCODER_PUSH_9 = 115

class Elements(object):
    """
    Centralizes the definition of all hardware elements for the Minilab Mk2.
    """
    def __init__(self):
        super(Elements, self).__init__()

        # Encoders
        self.encoders = []
        for i, cc in enumerate(ENCODER_CCS):
            encoder = EncoderElement(
                MIDI_CC_TYPE,
                ENCODER_CHANNEL,
                cc,
                Live.MidiMap.MapMode.relative_smooth_two_compliment,
                name='Encoder_{}'.format(i + 1)
            )
            # Remove mapping_sensitivity override to let standard knobs go at default (faster) speed
            # encoder.mapping_sensitivity = 2.0 
            self.encoders.append(encoder)

        self.encoders_matrix = ButtonMatrixElement(
            rows=[self.encoders],
            name='Encoders_Matrix'
        )

        # Device Encoders (Knobs 1-8)
        self.device_encoders_matrix = ButtonMatrixElement(
            rows=[self.encoders[0:8]],
            name='Device_Encoders_Matrix'
        )

        # Specific Mixing/Navigation Encoders (Knobs 9-16)
        self.encoder_cue_volume = self.encoders[8] # Knob 9
        self.encoder_clip_gain = self.encoders[9] # Knob 10
        self.encoder_pan = self.encoders[10] # Knob 11
        self.encoder_volume = self.encoders[11] # Knob 12
        self.encoder_custom = self.encoders[12] # Knob 13
        self.encoder_zoom = self.encoders[13] # Knob 14
        self.encoder_scroll_v = self.encoders[14] # Knob 15
        self.encoder_scroll_h = self.encoders[15] # Knob 16

        # Clickable Encoder Buttons
        self.encoder_1_button = ButtonElement(True, MIDI_CC_TYPE, PAD_CHANNEL, ENCODER_PUSH_1, name='Encoder_1_Button')
        self.encoder_9_button = ButtonElement(True, MIDI_CC_TYPE, PAD_CHANNEL, ENCODER_PUSH_9, name='Encoder_9_Button')

        # Pads Bank 1 (1-8) - Notes
        self.pads_bank_1 = []
        for i, note in enumerate(PAD_NOTES):
            pad = ButtonElement(True, MIDI_NOTE_TYPE, PAD_CHANNEL, note, name='Pad_{}'.format(i + 1))
            self.pads_bank_1.append(pad)
        
        self.pads_bank_1_matrix = ButtonMatrixElement(
            rows=[self.pads_bank_1],
            name='Pads_Bank_1_Matrix'
        )

        # Pads Bank 2 (9-16) - CCs for Transport and Control
        self.pads_bank_2 = []
        for i, cc in enumerate(PAD_CCS_BANK2):
            pad = MinilabPadButtonElement(True, MIDI_CC_TYPE, PAD_CHANNEL, cc, pad_index=(i + 8), skin=skin, name='Pad_{}'.format(i + 9))
            self.pads_bank_2.append(pad)

        self.pad_play = self.pads_bank_2[0]       # Pad 9
        self.pad_stop = self.pads_bank_2[1]       # Pad 10
        self.pad_record = self.pads_bank_2[2]     # Pad 11
        self.pad_arm = self.pads_bank_2[3]        # Pad 12
        self.pad_mute = self.pads_bank_2[4]       # Pad 13
        self.pad_solo = self.pads_bank_2[5]       # Pad 14
        self.pad_metronome = self.pads_bank_2[6]  # Pad 15
        self.pad_shift = self.pads_bank_2[7]      # Pad 16 (Shift Modifier)
