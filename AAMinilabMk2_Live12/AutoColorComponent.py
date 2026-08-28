# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, Jan 17 2023, 09:28:58) 
# [Clang 14.0.6 ]
# Embedded file name: output/Live/mac_universal_64_static/Release/python-bundle/MIDI Remote Scripts/AAMinilabMk2_Live12/AutoColorComponent.py
# Compiled at: 2024-04-01 10:00:00
# Size of source mod 2**32: 3000 bytes
from __future__ import absolute_import, print_function, unicode_literals

import os
import io
import re
import logging
from ableton.v2.base import listens, listens_group, task
from ableton.v2.control_surface import Component

logger = logging.getLogger(__name__)

# Fallback palette if autocolor.txt is not found
DEFAULT_COLORS = {
    0x8A2BE2: ['drums', 'drum', 'bateria'],
    0xDDA0DD: ['kick', 'bombo', 'kck', 'snare', 'snr', 'caja', 'hihat', 'hi-hat', 'hat', 'aereos', 'ohs', 'toms', 'tom', 'ride', 'platos', 'plato'],
    0xC71585: ['percs', 'percus', 'percussion'],
    0xFFB6C1: ['udu', 'cajon', 'pandero', 'trash', 'cascabeles', 'pandereta', 'castañuela', 'bongo', 'timbales', 'bongos', 'timbal', 'triangulo', 'crotalo', 'crotalos', 'palmas', 'nudillos', 'nudillo'],
    0x8B0000: ['electricas', 'elecs'],
    0xE57373: ['pwr', 'power', 'earp', 'lead', 'solo', 'gtr'],
    0x8B4513: ['acusticas'],
    0xD2B48C: ['acc', 'acc rhy', 'acc arp', 'flam', 'clasica', 'flam arp', 'flam rhy'],
    0xFF8C00: ['keys'],
    0xFFB90F: ['b3', 'organ', 'synth lead', 'synth bass', 'synth', 'arp2500', 'mini', 'buchla', 'juno', 'jupiter', 'piano', 'rhodes'],
    0xFFFF00: ['bass', 'bajo'],
    0x5C4033: ['strings'],
    0xDAA520: ['violin', 'viola', 'contrabajo', 'cello'],
    0x006400: ['voces'],
    0x228B22: ['vox', 'voz', 'voz principal', 'principal', 'coro', 'armo', 'armo hi', 'armo low', 'rapeo', 'coros', 'voz doble', 'armo med'],
    0x87CEEB: ['fxs', 'fx']
}

DEFAULT_CONFIG_TEMPLATE = """# ==============================================================================
# 🎨 AUTOCOLOR CONFIGURATION FOR ABLETON LIVE (MiniLab Mk2 Script)
# ==============================================================================
# INSTRUCCIONES:
# - Cada línea define un color y las palabras clave asociadas a ese color.
# - Formato: COLOR_HEX = palabra1, palabra2, palabra3...
# - Puedes usar formato hexadecimal (0xRRGGBB o #RRGGBB).
# - Las líneas que empiezan por '#' son comentarios y se ignoran.
# - Puedes añadir o quitar palabras separadas por comas.
# - Los cambios se detectan automáticamente al guardar este archivo.
# ==============================================================================

# BATERÍAS (Morado oscuro / violeta)
0x8A2BE2 = drums, drum, bateria

# ELEMENTOS BATERÍA (Morado pastel)
0xDDA0DD = kick, bombo, kck, snare, snr, caja, hihat, hi-hat, hat, aereos, ohs, toms, tom, ride, platos, plato

# PERCUSIÓN (Morado rosáceo oscuro)
0xC71585 = percs, percus, percussion

# ELEMENTOS PERCUSIÓN (Rosa pastel)
0xFFB6C1 = udu, cajon, pandero, trash, cascabeles, pandereta, castañuela, bongo, timbales, bongos, timbal, triangulo, crotalo, crotalos, palmas, nudillos, nudillo

# GUITARRAS ELÉCTRICAS (Rojo oscuro)
0x8B0000 = electricas, elecs

# ELEMENTOS GUITARRA ELÉCTRICA (Rojo pastel)
0xE57373 = pwr, power, earp, lead, solo, gtr

# GUITARRAS ACÚSTICAS (Marrón)
0x8B4513 = acusticas

# ELEMENTOS GUITARRA ACÚSTICA (Marrón claro pastel)
0xD2B48C = acc, acc rhy, acc arp, flam, clasica, flam arp, flam rhy

# TECLAS / KEYS (Naranja)
0xFF8C00 = keys

# ELEMENTOS KEYS & SYNTHS (Mango / Naranja claro)
0xFFB90F = b3, organ, synth lead, synth bass, synth, arp2500, mini, buchla, juno, jupiter, piano, rhodes

# BAJO (Amarillo)
0xFFFF00 = bass, bajo

# STRINGS (Marrón oscuro)
0x5C4033 = strings

# ELEMENTOS STRINGS (Marrón ocre dorado)
0xDAA520 = violin, viola, contrabajo, cello

# VOCES (Verde oscuro)
0x006400 = voces

# ELEMENTOS VOCES (Verde claro / lima)
0x228B22 = vox, voz, voz principal, principal, coro, armo, armo hi, armo low, rapeo, coros, voz doble, armo med

# EFECTOS / FX (Azul clarito / Sky Blue)
0x87CEEB = fxs, fx
"""

class AutoColorComponent(Component):
    """
    Automatically colors tracks and their clips based on names defined in autocolor.txt.
    Supports live hot-reloading when autocolor.txt is modified.
    """

    def __init__(self, *a, **k):
        super(AutoColorComponent, self).__init__(*a, **k)
        
        self._config_path = os.path.join(os.path.dirname(__file__), 'autocolor.txt')
        self._config_mtime = 0
        self._compiled_regexes = []
        
        self._load_config()

        self._on_tracks_changed.subject = self.song
        self._on_tracks_changed()

    def _parse_hex_color(self, hex_str):
        hex_str = hex_str.strip()
        if hex_str.startswith('#'):
            return int(hex_str[1:], 16)
        if hex_str.lower().startswith('0x'):
            return int(hex_str, 16)
        return int(hex_str, 16)

    def _load_config(self):
        color_map = {}
        
        # If autocolor.txt does not exist, create it with default template
        if not os.path.exists(self._config_path):
            try:
                with io.open(self._config_path, 'w', encoding='utf-8') as f:
                    f.write(DEFAULT_CONFIG_TEMPLATE)
                logger.info("AutoColor: Created default autocolor.txt at " + str(self._config_path))
            except Exception as e:
                logger.error("AutoColor: Could not create autocolor.txt: " + str(e))

        # Attempt to read autocolor.txt
        if os.path.exists(self._config_path):
            try:
                self._config_mtime = os.path.getmtime(self._config_path)
                with io.open(self._config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        # Support '=' or ':' delimiter
                        delimiter = '=' if '=' in line else (':' if ':' in line else None)
                        if not delimiter:
                            continue
                            
                        parts = line.split(delimiter, 1)
                        color_raw = parts[0].strip()
                        keywords_raw = parts[1].strip()
                        
                        try:
                            hex_color = self._parse_hex_color(color_raw)
                        except ValueError:
                            logger.error("AutoColor: Invalid hex color format: " + str(color_raw))
                            continue
                            
                        keywords = [k.strip() for k in keywords_raw.split(',') if k.strip()]
                        if keywords:
                            if hex_color in color_map:
                                color_map[hex_color].extend(keywords)
                            else:
                                color_map[hex_color] = keywords
                logger.info("AutoColor: Loaded " + str(len(color_map)) + " color rules from autocolor.txt")
            except Exception as e:
                logger.error("AutoColor: Error reading autocolor.txt, using defaults: " + str(e))
                color_map = DEFAULT_COLORS
        else:
            color_map = DEFAULT_COLORS

        # Compile regexes sorted by keyword length descending (longer phrases matched first)
        compiled = []
        for hex_color, keywords in color_map.items():
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                compiled.append((re.compile(pattern, re.IGNORECASE), hex_color, keyword))
                
        compiled.sort(key=lambda item: len(item[2]), reverse=True)
        self._compiled_regexes = compiled

    def _reload_if_modified(self):
        if os.path.exists(self._config_path):
            try:
                current_mtime = os.path.getmtime(self._config_path)
                if current_mtime != self._config_mtime:
                    logger.info("AutoColor: Detected modification in autocolor.txt. Reloading...")
                    self._load_config()
            except Exception as e:
                logger.error("AutoColor: Error checking file mtime: " + str(e))

    @listens('tracks')
    def _on_tracks_changed(self):
        logger.info("AutoColor: _on_tracks_changed called")
        self._reload_if_modified()
        self._on_track_name_changed.replace_subjects(self.song.tracks)
        
        # Listen for new / modified arrangement clips on tracks that support it
        tracks_with_arr = [t for t in self.song.tracks if hasattr(t, 'add_arrangement_clips_listener')]
        self._on_arrangement_clips_changed.replace_subjects(tracks_with_arr)
        
        # Immediately colorize any tracks and clips that might have been added
        for track in self.song.tracks:
            self._apply_color_to_track(track)

    @listens_group('name')
    def _on_track_name_changed(self, track):
        logger.info("AutoColor: _on_track_name_changed called for track: " + str(track.name))
        self._apply_color_to_track(track)

    @listens_group('arrangement_clips')
    def _on_arrangement_clips_changed(self, track):
        logger.info("AutoColor: _on_arrangement_clips_changed called for track: " + str(track.name))
        self._apply_color_to_track(track)

    def _needs_color_update(self, track, hex_color):
        if track.color != hex_color:
            return True
        if hasattr(track, 'arrangement_clips'):
            for clip in track.arrangement_clips:
                if clip and clip.color != hex_color:
                    return True
        if hasattr(track, 'clip_slots'):
            for slot in track.clip_slots:
                if slot and slot.has_clip and slot.clip and slot.clip.color != hex_color:
                    return True
        return False

    def _apply_color_to_track(self, track):
        if not track:
            return
            
        self._reload_if_modified()
        track_name = track.name
        
        for regex, hex_color, keyword in self._compiled_regexes:
            if regex.search(track_name):
                logger.info("AutoColor: Match found for keyword: " + str(keyword) + " color: " + hex(hex_color))
                if self._needs_color_update(track, hex_color):
                    # Update deferred to avoid 'Changes cannot be triggered by notifications' error
                    self._tasks.add(task.run(lambda t=track, c=hex_color: self._do_color_change(t, c)))
                break # Stop searching after first match

    def _do_color_change(self, track, hex_color):
        try:
            if track.color != hex_color:
                track.color = hex_color
            self._apply_color_to_clips(track, hex_color)
            logger.info("AutoColor: Color applied successfully to track and clips")
        except Exception as e:
            logger.info("AutoColor: Error applying color: " + str(e))

    def _apply_color_to_clips(self, track, hex_color):
        # Arrangement clips (Arrangement View)
        if hasattr(track, 'arrangement_clips'):
            for clip in track.arrangement_clips:
                try:
                    if clip and clip.color != hex_color:
                        clip.color = hex_color
                except Exception as e:
                    logger.debug("AutoColor: Error setting arrangement clip color: " + str(e))

        # Session clip slots (Session View)
        if hasattr(track, 'clip_slots'):
            for slot in track.clip_slots:
                try:
                    if slot and slot.has_clip and slot.clip and slot.clip.color != hex_color:
                        slot.clip.color = hex_color
                except Exception as e:
                    logger.debug("AutoColor: Error setting session clip color: " + str(e))
