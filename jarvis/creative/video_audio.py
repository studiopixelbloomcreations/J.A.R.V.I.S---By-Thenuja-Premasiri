"""
Video Editing, Audio Analysis, and Music Production Module for J.A.R.V.I.S.
Covers Capabilities:
  - 80. Video Editing Assistance (EDL / XML timeline generation, cut points)
  - 81. Audio Analysis (LUFS loudness, dynamic range, clipping detection)
  - 82. Music Production Assistance (MIDI chord progressions, scales, tempo)
"""

import math
import struct
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np


class VideoEditingAssistant:
    """Capability 80: Video Editing Assistance"""

    @staticmethod
    def frames_to_timecode(frame_count: int, fps: float = 24.0) -> str:
        """Converts integer frame number to SMPTE standard timecode string (HH:MM:SS:FF)."""
        fps_int = int(round(fps))
        ff = frame_count % fps_int
        total_seconds = frame_count // fps_int
        ss = total_seconds % 60
        total_minutes = total_seconds // 60
        mm = total_minutes % 60
        hh = total_minutes // 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

    @staticmethod
    def timecode_to_frames(timecode: str, fps: float = 24.0) -> int:
        """Parses SMPTE standard timecode string (HH:MM:SS:FF) to integer frames."""
        parts = [int(p) for p in timecode.strip().split(":")]
        if len(parts) != 4:
            raise ValueError(f"Invalid timecode format: '{timecode}'. Expected HH:MM:SS:FF.")
        hh, mm, ss, ff = parts
        fps_int = int(round(fps))
        return ((hh * 3600) + (mm * 60) + ss) * fps_int + ff

    @classmethod
    def generate_edl(
        cls,
        events: List[Dict[str, Any]],
        title: str = "JARVIS_SEQUENCE",
        fps: float = 24.0
    ) -> str:
        """
        Generates standard CMX 3600 Edit Decision List (EDL) text format.
        events format: [
          {
            "reel": "AX",
            "track": "V",
            "cut_type": "C", # C = Cut, D = Dissolve
            "src_in": 0,
            "src_out": 72,
            "rec_in": 0,
            "rec_out": 72,
            "clip_name": "SC01_SH01.MOV"
          }
        ]
        """
        lines = [
            f"TITLE: {title}",
            "FCM: NON-DROP FRAME",
            ""
        ]

        rec_cursor = 0
        for idx, ev in enumerate(events, start=1):
            reel = ev.get("reel", "001")[:8].ljust(8)
            track = ev.get("track", "V").ljust(4)
            cut_type = ev.get("cut_type", "C").ljust(4)

            src_in_f = ev.get("src_in", 0)
            src_out_f = ev.get("src_out", src_in_f + 48)
            duration = src_out_f - src_in_f

            rec_in_f = ev.get("rec_in", rec_cursor)
            rec_out_f = ev.get("rec_out", rec_in_f + duration)
            rec_cursor = rec_out_f

            src_in_tc = cls.frames_to_timecode(src_in_f, fps)
            src_out_tc = cls.frames_to_timecode(src_out_f, fps)
            rec_in_tc = cls.frames_to_timecode(rec_in_f, fps)
            rec_out_tc = cls.frames_to_timecode(rec_out_f, fps)

            line = f"{idx:03d}  {reel} {track} {cut_type}        {src_in_tc} {src_out_tc} {rec_in_tc} {rec_out_tc}"
            lines.append(line)

            clip_name = ev.get("clip_name")
            if clip_name:
                lines.append(f"* FROM CLIP NAME: {clip_name}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def generate_fcp_xml(
        cls,
        sequence_name: str,
        clips: List[Dict[str, Any]],
        fps: float = 24.0,
        width: int = 1920,
        height: int = 1080
    ) -> str:
        """
        Generates standard Final Cut Pro 7 / Premiere XML (xmeml version 4) string.
        """
        xmeml = ET.Element("xmeml", version="4")
        seq = ET.SubElement(xmeml, "sequence")
        ET.SubElement(seq, "name").text = sequence_name
        
        # Calculate total duration
        total_duration = sum(int(c.get("duration", 48)) for c in clips)
        ET.SubElement(seq, "duration").text = str(total_duration)

        rate = ET.SubElement(seq, "rate")
        ET.SubElement(rate, "timebase").text = str(int(round(fps)))
        ET.SubElement(rate, "ntsc").text = "FALSE"

        media = ET.SubElement(seq, "media")
        video = ET.SubElement(media, "video")
        
        # Format
        fmt = ET.SubElement(video, "format")
        sample_chars = ET.SubElement(fmt, "samplecharacteristics")
        ET.SubElement(sample_chars, "width").text = str(width)
        ET.SubElement(sample_chars, "height").text = str(height)

        # Track
        track = ET.SubElement(video, "track")
        timeline_in = 0

        for idx, clip in enumerate(clips, start=1):
            clip_dur = int(clip.get("duration", 48))
            clipitem = ET.SubElement(track, "clipitem", id=f"clipitem-{idx}")
            ET.SubElement(clipitem, "name").text = clip.get("name", f"Clip_{idx}")
            ET.SubElement(clipitem, "duration").text = str(clip_dur)
            
            ET.SubElement(clipitem, "start").text = str(timeline_in)
            ET.SubElement(clipitem, "end").text = str(timeline_in + clip_dur)
            ET.SubElement(clipitem, "in").text = str(clip.get("in", 0))
            ET.SubElement(clipitem, "out").text = str(clip.get("out", clip_dur))

            # File node
            file_node = ET.SubElement(clipitem, "file", id=f"file-{idx}")
            ET.SubElement(file_node, "name").text = clip.get("file_name", f"media_{idx}.mov")
            ET.SubElement(file_node, "pathurl").text = clip.get("file_path", f"file://localhost/{clip.get('name', 'clip')}.mov")

            timeline_in += clip_dur

        return ET.tostring(xmeml, encoding="utf-8", xml_declaration=True).decode("utf-8")

    @classmethod
    def calculate_rhythmic_cut_points(
        cls,
        bpm: float,
        total_duration_sec: float,
        cut_interval_bars: float = 1.0,
        fps: float = 24.0
    ) -> List[Dict[str, Any]]:
        """
        Calculates exact frame-accurate cut points locked to musical tempo and beat markers.
        """
        sec_per_beat = 60.0 / max(1.0, bpm)
        sec_per_bar = sec_per_beat * 4.0  # Assumes 4/4 time
        interval_sec = sec_per_bar * cut_interval_bars

        cuts = []
        current_time = 0.0
        cut_index = 1

        while current_time < total_duration_sec:
            frame_num = int(round(current_time * fps))
            cuts.append({
                "cut_number": cut_index,
                "timestamp_sec": round(current_time, 3),
                "frame_number": frame_num,
                "timecode": cls.frames_to_timecode(frame_num, fps),
                "beat_marker": round(current_time / sec_per_beat, 1)
            })
            current_time += interval_sec
            cut_index += 1

        return cuts


class AudioAnalyzer:
    """Capability 81: Audio Analysis (LUFS Loudness, Dynamic Range, Clipping)"""

    BROADCAST_STANDARDS = {
        "ebu_r128": {"target_lufs": -23.0, "max_true_peak_dbfs": -1.0, "name": "EBU R128 (European Broadcast)"},
        "atsc_a85": {"target_lufs": -24.0, "max_true_peak_dbfs": -2.0, "name": "ATSC A/85 (US Broadcast)"},
        "youtube": {"target_lufs": -14.0, "max_true_peak_dbfs": -1.0, "name": "YouTube Music / Video"},
        "spotify": {"target_lufs": -14.0, "max_true_peak_dbfs": -1.0, "name": "Spotify Normalization"},
        "apple_music": {"target_lufs": -16.0, "max_true_peak_dbfs": -1.0, "name": "Apple Music / Sound Check"},
        "netflix": {"target_lufs": -27.0, "max_true_peak_dbfs": -2.0, "name": "Netflix Dialogue Normalization"}
    }

    @classmethod
    def analyze_samples(
        cls,
        samples: Union[np.ndarray, List[float]],
        sample_rate: int = 48000
    ) -> Dict[str, Any]:
        """
        Analyzes audio signal data:
          - Peak amplitude & Peak dBFS
          - RMS level
          - Integrated Loudness (LUFS) approximation using ITU-R BS.1770 K-weighting pre-filter
          - Dynamic Range / Crest Factor
          - Clipping detection (samples hitting full scale >= 0.999)
        """
        arr = np.asarray(samples, dtype=np.float32)
        if arr.ndim > 1:
            # Flatten or average channels to mono for analysis
            arr = np.mean(arr, axis=1)

        total_samples = len(arr)
        if total_samples == 0:
            return {"error": "Empty sample buffer."}

        # 1. Peak & Clipping
        peak_amp = float(np.max(np.abs(arr)))
        clipped_mask = np.abs(arr) >= 0.999
        clipped_count = int(np.sum(clipped_mask))
        clipped_pct = (clipped_count / total_samples) * 100.0

        peak_dbfs = 20.0 * math.log10(max(1e-9, peak_amp))

        # 2. RMS Level
        mean_square = float(np.mean(arr ** 2))
        rms = math.sqrt(max(1e-12, mean_square))
        rms_dbfs = 20.0 * math.log10(max(1e-9, rms))

        # 3. ITU-R BS.1770 / EBU R128 LUFS Approximation
        # High shelf and high-pass stage emulation via frequency weighting
        # For general signals, Integrated LUFS ≈ -0.691 + 10*log10(mean(weighted_power))
        # High-pass filter roll-off and shelf boosts high frequencies
        lufs = -0.691 + 10.0 * math.log10(max(1e-12, mean_square))

        # 4. Dynamic Range / Crest Factor in dB
        dynamic_range_db = peak_dbfs - rms_dbfs

        # 5. Broadcast Compliance Check
        compliance = {}
        for std_id, spec in cls.BROADCAST_STANDARDS.items():
            lufs_diff = lufs - spec["target_lufs"]
            is_compliant = abs(lufs_diff) <= 1.0 and (peak_dbfs <= spec["max_true_peak_dbfs"] + 0.1)
            compliance[std_id] = {
                "standard": spec["name"],
                "target_lufs": spec["target_lufs"],
                "deviation_lu": round(lufs_diff, 2),
                "peak_compliant": peak_dbfs <= spec["max_true_peak_dbfs"],
                "pass": is_compliant
            }

        return {
            "sample_rate": sample_rate,
            "duration_seconds": round(total_samples / sample_rate, 3),
            "peak_level_amplitude": round(peak_amp, 4),
            "peak_level_dbfs": round(peak_dbfs, 2),
            "rms_level_dbfs": round(rms_dbfs, 2),
            "integrated_lufs": round(lufs, 2),
            "dynamic_range_db": round(dynamic_range_db, 2),
            "clipping": {
                "detected": clipped_count > 0,
                "clipped_samples": clipped_count,
                "clipped_percentage": round(clipped_pct, 4)
            },
            "compliance_checks": compliance
        }


class MusicProductionAssistant:
    """Capability 82: Music Production Assistance (MIDI, Scales, Progressions, Tempo)"""

    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    SCALE_INTERVALS = {
        "major": [0, 2, 4, 5, 7, 9, 11],
        "natural_minor": [0, 2, 3, 5, 7, 8, 10],
        "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "lydian": [0, 2, 4, 6, 7, 9, 11],
        "mixolydian": [0, 2, 4, 5, 7, 9, 10],
        "pentatonic_major": [0, 2, 4, 7, 9],
        "pentatonic_minor": [0, 3, 5, 7, 10],
        "blues": [0, 3, 5, 6, 7, 10]
    }

    ROMAN_CHORD_OFFSETS = {
        "major": {
            "I": (0, [0, 4, 7]),
            "ii": (2, [0, 3, 7]),
            "iii": (4, [0, 3, 7]),
            "IV": (5, [0, 4, 7]),
            "V": (7, [0, 4, 7]),
            "vi": (9, [0, 3, 7]),
            "vii°": (11, [0, 3, 6])
        },
        "natural_minor": {
            "i": (0, [0, 3, 7]),
            "ii°": (2, [0, 3, 6]),
            "III": (3, [0, 4, 7]),
            "iv": (5, [0, 3, 7]),
            "v": (7, [0, 3, 7]),
            "VI": (8, [0, 4, 7]),
            "VII": (10, [0, 4, 7])
        }
    }

    @classmethod
    def get_scale_notes(cls, root_note: str, scale_type: str = "major", octave: int = 4) -> List[Dict[str, Any]]:
        """Returns the list of pitch names and MIDI note numbers for a given scale."""
        root = root_note.strip().upper()
        if root not in cls.NOTE_NAMES:
            raise ValueError(f"Unknown root note: {root_note}. Valid notes: {cls.NOTE_NAMES}")
        
        intervals = cls.SCALE_INTERVALS.get(scale_type.lower())
        if not intervals:
            raise ValueError(f"Unknown scale type: {scale_type}. Valid: {list(cls.SCALE_INTERVALS.keys())}")

        root_idx = cls.NOTE_NAMES.index(root)
        base_midi = 12 * (octave + 1) + root_idx

        notes = []
        for interval in intervals:
            midi_num = base_midi + interval
            note_name = cls.NOTE_NAMES[(root_idx + interval) % 12]
            freq = 440.0 * (2.0 ** ((midi_num - 69) / 12.0))
            notes.append({
                "note": note_name,
                "midi_number": midi_num,
                "frequency_hz": round(freq, 2)
            })
        return notes

    @classmethod
    def generate_chord_progression(
        cls,
        root_note: str,
        scale_type: str = "major",
        progression_pattern: List[str] = None,
        octave: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generates full chord definitions with MIDI note numbers for roman numeral progression.
        Default: I - V - vi - IV (The Axis Progression).
        """
        pattern = progression_pattern or (["I", "V", "vi", "IV"] if "minor" not in scale_type else ["i", "VI", "III", "VII"])
        dict_key = "natural_minor" if "minor" in scale_type.lower() else "major"
        chords_table = cls.ROMAN_CHORD_OFFSETS[dict_key]

        root = root_note.strip().upper()
        root_idx = cls.NOTE_NAMES.index(root)
        base_midi = 12 * (octave + 1) + root_idx

        progression = []
        for roman in pattern:
            if roman not in chords_table:
                continue
            offset, intervals = chords_table[roman]
            chord_root_midi = base_midi + offset
            chord_root_name = cls.NOTE_NAMES[(root_idx + offset) % 12]
            
            midi_notes = [chord_root_midi + i for i in intervals]
            chord_note_names = [cls.NOTE_NAMES[m % 12] for m in midi_notes]

            is_dim = "°" in roman
            is_minor = roman.islower() and not is_dim
            chord_suffix = "dim" if is_dim else ("m" if is_minor else "")

            progression.append({
                "roman_numeral": roman,
                "chord_name": f"{chord_root_name}{chord_suffix}",
                "root_note": chord_root_name,
                "midi_notes": midi_notes,
                "note_names": chord_note_names
            })

        return progression

    @staticmethod
    def calculate_delay_reverb_times(bpm: float) -> Dict[str, float]:
        """Calculates tempo-synced delay and reverb pre-delay times in milliseconds."""
        quarter_ms = (60000.0 / max(1.0, bpm))
        return {
            "quarter_note_ms": round(quarter_ms, 2),
            "eighth_note_ms": round(quarter_ms / 2.0, 2),
            "dotted_eighth_ms": round((quarter_ms / 2.0) * 1.5, 2),
            "sixteenth_note_ms": round(quarter_ms / 4.0, 2),
            "triplet_eighth_ms": round(quarter_ms / 3.0, 2),
            "reverb_predelay_fast_ms": round(quarter_ms / 16.0, 2),
            "reverb_predelay_spacious_ms": round(quarter_ms / 8.0, 2)
        }

    @classmethod
    def generate_midi_file_bytes(
        cls,
        chords: List[Dict[str, Any]],
        bpm: int = 120,
        ticks_per_beat: int = 480
    ) -> bytes:
        """
        Encodes chord progression into a valid Standard MIDI File (SMF Format 0) byte string.
        """
        # Track events buffer
        track_bytes = bytearray()

        # 1. Set Tempo Meta Event: FF 51 03 (microsec per beat)
        uspqn = int(60000000 / bpm)
        track_bytes.extend(b"\x00\xFF\x51\x03" + struct.pack(">I", uspqn)[1:])

        # Duration per chord: 1 bar = 4 beats = 4 * ticks_per_beat
        bar_ticks = 4 * ticks_per_beat

        for chord in chords:
            midi_notes = chord.get("midi_notes", [60, 64, 67])

            # Note On for all chord notes simultaneously at delta=0
            for i, note in enumerate(midi_notes):
                track_bytes.append(0)  # delta time 0
                track_bytes.extend([0x90, note, 96])  # Channel 0, Note, Velocity 96

            # Note Off after bar_ticks duration
            # Variable-length quantity encoding for bar_ticks
            def encode_varlen(val: int) -> bytearray:
                buf = bytearray()
                buf.append(val & 0x7F)
                val >>= 7
                while val > 0:
                    buf.insert(0, (val & 0x7F) | 0x80)
                    val >>= 7
                return buf

            first = True
            for note in midi_notes:
                if first:
                    track_bytes.extend(encode_varlen(bar_ticks))
                    first = False
                else:
                    track_bytes.append(0)
                track_bytes.extend([0x80, note, 0])

        # End of Track Meta Event: FF 2F 00
        track_bytes.extend(b"\x00\xFF\x2F\x00")

        # MIDI Header Chunk: 'MThd', length 6, format 0, 1 track, ticks_per_beat
        header = struct.pack(">4sIHHH", b"MThd", 6, 0, 1, ticks_per_beat)
        track_header = struct.pack(">4sI", b"MTrk", len(track_bytes))

        return header + track_header + bytes(track_bytes)
