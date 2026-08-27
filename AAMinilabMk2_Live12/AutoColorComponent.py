# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, Jan 17 2023, 09:28:58) 
# [Clang 14.0.6 ]
# Embedded file name: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/AAMinilabMk2_Live12/AutoColorComponent.py
# Compiled at: 2024-04-01 10:00:00
# Size of source mod 2**32: 3000 bytes
from __future__ import absolute_import, print_function, unicode_literals

import re
import logging
from ableton.v2.base import listens, listens_group, task
from ableton.v2.control_surface import Component

logger = logging.getLogger(__name__)

# Ableton Color Palette mapped via RGB Hex.
# Ableton automatically snaps to the closest palette color.
COLORS = {
    # BATERÍAS (Morado oscuro / violeta)
    0x8A2BE2: ['drums', 'drum', 'bateria'],
    # Elementos batería (Morado pastel)
    0xDDA0DD: ['kick', 'bombo', 'kck', 'snare', 'snr', 'caja', 'hihat', 'hi-hat', 'hat', 'aereos', 'ohs', 'toms', 'tom', 'ride'],
    
    # PERCUSIÓN (Morado rosáceo oscuro)
    0xC71585: ['percs', 'percus', 'percussion'],
    # Elementos percusión (Morado rosáceo pastel)
    0xFFB6C1: ['udu', 'cajon', 'pandero', 'trash', 'cascabeles', 'pandereta', 'castañuela', 'bongo', 'timbales', 'bongos', 'timbal', 'triangulo', 'crotalo', 'crotalos', 'palmas'],
    
    # GUITARRAS ELÉCTRICAS (Rojo oscuro)
    0x8B0000: ['electricas', 'elecs'],
    # Elementos guitarra eléctrica (Rojo pastel)
    0xFA8072: ['pwr', 'power', 'earp', 'lead', 'solo'],
    
    # GUITARRAS ACÚSTICAS (Marrón)
    0x8B4513: ['acusticas'],
    # Elementos acústicas (Marrón clarito pastel)
    0xD2B48C: ['acc', 'acc rhy', 'acc arp', 'flam', 'clasica', 'flam arp', 'flam rhy'],
    
    # TECLAS / KEYS (Naranja)
    0xFF8C00: ['keys'],
    # Elementos keys (Mango / Naranja claro)
    0xFFB90F: ['b3', 'organ', 'synth lead', 'synth bass', 'synth', 'arp2500', 'mini', 'buchla', 'juno', 'jupiter', 'piano', 'rhodes'],
    
    # BAJO (Amarillo)
    0xFFFF00: ['bass', 'bajo'],
    
    # STRINGS (Marrón oscuro)
    0x5C4033: ['strings'],
    # Elementos strings (Marrón ocre dorado)
    0xDAA520: ['violin', 'viola', 'contrabajo', 'cello'],
    
    # VOCES (Verde oscuro)
    0x006400: ['voces'],
    # Elementos voces (Verde un poco más claro)
    0x228B22: ['vox', 'voz', 'voz principal', 'principal', 'coro', 'armo', 'armo hi', 'armo low', 'rapeo', 'coros', 'voz doble', 'armo med']
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
        for hex_color, keywords in COLORS.items():
            for keyword in keywords:
                # \b ensures we only match whole words (e.g., matching 'bajo' won't trigger on 'contrabajo')
                pattern = r'\b' + re.escape(keyword) + r'\b'
                self._compiled_regexes.append((re.compile(pattern, re.IGNORECASE), hex_color, keyword))

        self._on_tracks_changed.subject = self.song
        self._on_tracks_changed()

    @listens('tracks')
    def _on_tracks_changed(self):
        logger.info("AutoColor: _on_tracks_changed called")
        self._on_track_name_changed.replace_subjects(self.song.tracks)
        
        # Immediately colorize any tracks that might have been added
        for track in self.song.tracks:
            self._apply_color_to_track(track)

    @listens_group('name')
    def _on_track_name_changed(self, track):
        logger.info("AutoColor: _on_track_name_changed called for track: " + str(track.name))
        self._apply_color_to_track(track)

    def _apply_color_to_track(self, track):
        if not track:
            return
            
        track_name = track.name
        
        logger.info("AutoColor: Checking track: " + str(track_name))
        for regex, hex_color, keyword in self._compiled_regexes:
            if regex.search(track_name):
                logger.info("AutoColor: Match found for keyword: " + str(keyword) + " color: " + hex(hex_color))
                # Update the track color deferred to avoid 'Changes cannot be triggered by notifications' error
                if track.color != hex_color:
                    self._tasks.add(task.run(lambda t=track, c=hex_color: self._do_color_change(t, c)))
                break # Stop searching after first match

    def _do_color_change(self, track, hex_color):
        try:
            track.color = hex_color
            logger.info("AutoColor: Color applied successfully")
        except Exception as e:
            logger.info("AutoColor: Error applying color: " + str(e))
