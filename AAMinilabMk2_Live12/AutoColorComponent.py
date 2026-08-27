# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, Jan 17 2023, 09:28:58) 
# [Clang 14.0.6 ]
# Embedded file name: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/AAMinilabMk2_Live12/AutoColorComponent.py
# Compiled at: 2024-04-01 10:00:00
# Size of source mod 2**32: 3000 bytes
from __future__ import absolute_import, print_function, unicode_literals

import re
from ableton.v2.base import listens, listens_group
from ableton.v2.control_surface import Component

# Ableton Color Palette (0-69)
COLORS = {
    # BATERÍAS (Morado oscuro / violeta)
    55: ['drums', 'drum', 'bateria'],
    # Elementos batería (Morado pastel)
    50: ['kick', 'bombo', 'kck', 'snare', 'snr', 'caja', 'hihat', 'hi-hat', 'hat', 'aereos', 'ohs', 'toms', 'tom', 'ride'],
    
    # PERCUSIÓN (Morado rosáceo oscuro)
    61: ['percs', 'percus', 'percussion'],
    # Elementos percusión (Morado rosáceo pastel)
    49: ['udu', 'cajon', 'pandero', 'trash', 'cascabeles', 'pandereta', 'castañuela', 'bongo', 'timbales', 'bongos', 'timbal', 'triangulo', 'crotalo', 'crotalos'],
    
    # GUITARRAS ELÉCTRICAS (Rojo oscuro)
    6: ['electricas', 'elecs'],
    # Elementos guitarra eléctrica (Rojo pastel)
    13: ['pwr', 'power', 'earp', 'lead', 'solo'],
    
    # GUITARRAS ACÚSTICAS (Marrón)
    64: ['acusticas'],
    # Elementos acústicas (Marrón clarito pastel)
    65: ['acc', 'acc rhy', 'acc arp', 'flam', 'clasica', 'flam arp', 'flam rhy'],
    
    # TECLAS / KEYS (Naranja)
    9: ['keys'],
    # Elementos keys (Mango / Naranja claro)
    10: ['b3', 'organ', 'synth lead', 'synth bass', 'synth', 'arp2500', 'mini', 'buchla', 'juno', 'jupiter', 'piano', 'rhodes'],
    
    # BAJO (Amarillo)
    11: ['bass', 'bajo'],
    
    # STRINGS (Marrón oscuro)
    63: ['strings'],
    # Elementos strings (Marrón ocre dorado)
    67: ['violin', 'viola', 'contrabajo', 'cello']
}

class AutoColorComponent(Component):
    """
    Automatically colors tracks based on their names using regex word boundaries
    so 'contrabajo' doesn't get colored as 'bajo'.
    """

    def __init__(self, *a, **k):
        super(AutoColorComponent, self).__init__(*a, **k)
        
        # Compile regex dictionary to optimize searching
        # We sort by length (descending) to match longer words first if regex doesn't catch it
        self._compiled_regexes = []
        for color_index, keywords in COLORS.items():
            for keyword in keywords:
                # \b ensures we only match whole words (e.g., matching 'bajo' won't trigger on 'contrabajo')
                pattern = r'\b' + re.escape(keyword) + r'\b'
                self._compiled_regexes.append((re.compile(pattern, re.IGNORECASE), color_index, keyword))

        self._on_tracks_changed.subject = self.song
        self._on_tracks_changed()

    @listens('tracks')
    def _on_tracks_changed(self):
        print("AutoColor: _on_tracks_changed called")
        self._on_track_name_changed.replace_subjects(self.song.tracks)
        
        # Immediately colorize any tracks that might have been added
        for track in self.song.tracks:
            self._apply_color_to_track(track)

    @listens_group('name')
    def _on_track_name_changed(self, track):
        print("AutoColor: _on_track_name_changed called for track: " + str(track.name))
        self._apply_color_to_track(track)

    def _apply_color_to_track(self, track):
        if not track:
            return
            
        track_name = track.name
        
        print("AutoColor: Checking track: " + str(track_name))
        for regex, color_index, keyword in self._compiled_regexes:
            if regex.search(track_name):
                print("AutoColor: Match found for keyword: " + str(keyword) + " color: " + str(color_index))
                # Update the track color
                if track.color_index != color_index:
                    try:
                        track.color_index = color_index
                        print("AutoColor: Color applied successfully")
                    except Exception as e:
                        print("AutoColor: Error applying color: " + str(e))
                break # Stop searching after first match
