"""
Beat Saber Mapping Framework - Lighting Automation

This module provides utilities for automating lighting events
based on beat patterns and common lighting techniques.
"""

from typing import List, Optional, Tuple

from .models import (
    BeatmapFile, BasicBeatmapEvent, ColorBoostBeatmapEvent
)

class LightingAutomation:
    """Utility class for automating lighting events"""
    
    # Event type constants
    BACK_LASERS = 0
    RING_LIGHTS = 1
    LEFT_LASERS = 2
    RIGHT_LASERS = 3
    CENTER_LIGHTS = 4
    BOOST_COLORS = 5
    EXTRA_LEFT_LIGHTS = 6
    EXTRA_RIGHT_LIGHTS = 7
    
    # Color constants
    OFF = 0
    RED = 1
    BLUE = 5
    WHITE = 7
    
    @staticmethod
    def generate_basic_lighting(
        beatmap: BeatmapFile,
        beat_divisor: float = 1.0,
        intensity: float = 1.0
    ) -> None:
        """
        Generate basic lighting that follows the beat pattern
        
        Args:
            beatmap: Beatmap to add lighting to
            beat_divisor: Beat division for lighting (1.0 = quarter notes)
            intensity: Lighting intensity (0.0-1.0)
        """
        # Clear existing lighting events
        beatmap.basicBeatmapEvents = []
        beatmap.colorBoostBeatmapEvents = []
        
        # Find min and max beats
        if not beatmap.colorNotes:
            return
            
        min_beat = min(note.b for note in beatmap.colorNotes)
        max_beat = max(note.b for note in beatmap.colorNotes)
        
        # Generate basic beat lighting
        current_beat = min_beat
        while current_beat <= max_beat:
            # Create back laser events
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=current_beat,
                et=LightingAutomation.BACK_LASERS,
                i=1,
                f=1.0 * intensity
            ))
            
            # Create ring lights events
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=current_beat,
                et=LightingAutomation.RING_LIGHTS,
                i=1,
                f=1.0 * intensity
            ))
            
            # Create left/right laser events alternating colors
            if int(current_beat / beat_divisor) % 2 == 0:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=current_beat,
                    et=LightingAutomation.LEFT_LASERS,
                    i=LightingAutomation.RED,
                    f=1.0 * intensity
                ))
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=current_beat,
                    et=LightingAutomation.RIGHT_LASERS,
                    i=LightingAutomation.BLUE,
                    f=1.0 * intensity
                ))
            else:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=current_beat,
                    et=LightingAutomation.LEFT_LASERS,
                    i=LightingAutomation.BLUE,
                    f=1.0 * intensity
                ))
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=current_beat,
                    et=LightingAutomation.RIGHT_LASERS,
                    i=LightingAutomation.RED,
                    f=1.0 * intensity
                ))
            
            # Advance to next beat
            current_beat += beat_divisor
        
        # Sort events
        beatmap.sort_objects()
    
    @staticmethod
    def generate_note_sync_lighting(beatmap: BeatmapFile) -> None:
        """
        Generate lighting that syncs with note hits
        
        Args:
            beatmap: Beatmap to add lighting to
        """
        # Clear existing lighting events
        beatmap.basicBeatmapEvents = []
        
        # Create light events for each note
        for note in beatmap.colorNotes:
            # Choose light type based on note color
            if note.c == 0:  # Red
                light_type = LightingAutomation.LEFT_LASERS
                color = LightingAutomation.RED
            else:  # Blue
                light_type = LightingAutomation.RIGHT_LASERS
                color = LightingAutomation.BLUE
            
            # Create light event
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=note.b,
                et=light_type,
                i=color,
                f=1.0
            ))
            
            # Add center lights for emphasis
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=note.b,
                et=LightingAutomation.CENTER_LIGHTS,
                i=color,
                f=1.0
            ))
            
            # Turn off lights slightly after
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=note.b + 0.5,
                et=light_type,
                i=LightingAutomation.OFF,
                f=1.0
            ))
            
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=note.b + 0.5,
                et=LightingAutomation.CENTER_LIGHTS,
                i=LightingAutomation.OFF,
                f=1.0
            ))
        
        # Sort events
        beatmap.sort_objects()
    
    @staticmethod
    def generate_advanced_lighting(
        beatmap: BeatmapFile,
        boost_sections: Optional[List[Tuple[float, float]]] = None
    ) -> None:
        """
        Generate advanced lighting with more varied patterns and boosts
        
        Args:
            beatmap: Beatmap to add lighting to
            boost_sections: List of (start_beat, end_beat) tuples for boost sections
        """
        # Clear existing lighting events
        beatmap.basicBeatmapEvents = []
        beatmap.colorBoostBeatmapEvents = []
        
        # Find min and max beats
        if not beatmap.colorNotes:
            return
            
        min_beat = min(note.b for note in beatmap.colorNotes)
        max_beat = max(note.b for note in beatmap.colorNotes)
        
        # Create dictionary of notes by beat
        notes_by_beat = {}
        for note in beatmap.colorNotes:
            beat = note.b
            if beat not in notes_by_beat:
                notes_by_beat[beat] = []
            notes_by_beat[beat].append(note)
        
        # Generate boost sections if not provided
        if not boost_sections:
            boost_sections = []
            section_length = 16  # 16 beats per section
            
            for section_start in range(int(min_beat), int(max_beat), section_length * 2):
                # Add boost section for first half
                boost_sections.append((section_start, section_start + section_length))
        
        # Add boost events
        for start_beat, end_beat in boost_sections:
            # Turn on boost
            beatmap.colorBoostBeatmapEvents.append(ColorBoostBeatmapEvent(
                b=start_beat,
                o=True
            ))
            
            # Turn off boost
            beatmap.colorBoostBeatmapEvents.append(ColorBoostBeatmapEvent(
                b=end_beat,
                o=False
            ))
        
        # Process each beat with notes
        for beat in sorted(notes_by_beat.keys()):
            notes = notes_by_beat[beat]
            
            # Determine if this beat is in a boost section
            in_boost = any(start <= beat < end for start, end in boost_sections)
            
            # Count notes by color
            red_count = sum(1 for note in notes if note.c == 0)
            blue_count = sum(1 for note in notes if note.c == 1)
            
            # Determine primary color for this beat
            if red_count > blue_count:
                primary_color = LightingAutomation.RED
                secondary_color = LightingAutomation.BLUE
            else:
                primary_color = LightingAutomation.BLUE
                secondary_color = LightingAutomation.RED
            
            # For jumps (multiple notes), use more intense lighting
            is_jump = len(notes) > 1
            
            # Intensity based on boost and jump
            intensity = 1.0
            if in_boost:
                intensity = 1.2
            if is_jump:
                intensity = min(1.5, intensity * 1.2)
            
            # Add lighting events
            
            # Ring lights
            beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                b=beat,
                et=LightingAutomation.RING_LIGHTS,
                i=primary_color if not in_boost else LightingAutomation.WHITE,
                f=intensity
            ))
            
            # Center lights
            if is_jump:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat,
                    et=LightingAutomation.CENTER_LIGHTS,
                    i=LightingAutomation.WHITE if in_boost else primary_color,
                    f=intensity
                ))
            
            # Left/right lasers based on note colors
            if red_count > 0:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat,
                    et=LightingAutomation.LEFT_LASERS,
                    i=LightingAutomation.RED,
                    f=intensity
                ))
            
            if blue_count > 0:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat,
                    et=LightingAutomation.RIGHT_LASERS,
                    i=LightingAutomation.BLUE,
                    f=intensity
                ))
            
            # Back lasers - alternate patterns
            if int(beat * 2) % 4 == 0:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat,
                    et=LightingAutomation.BACK_LASERS,
                    i=secondary_color,
                    f=intensity * 0.8
                ))
            
            # Extra lights for emphasis at certain intervals
            if int(beat) % 8 == 0:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat,
                    et=LightingAutomation.EXTRA_LEFT_LIGHTS,
                    i=LightingAutomation.WHITE if in_boost else primary_color,
                    f=intensity
                ))
                
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat,
                    et=LightingAutomation.EXTRA_RIGHT_LIGHTS,
                    i=LightingAutomation.WHITE if in_boost else secondary_color,
                    f=intensity
                ))
            
            # Turn off some lights after the beat
            fade_time = 0.25 if is_jump else 0.5
            
            if int(beat * 2) % 2 == 0:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat + fade_time,
                    et=LightingAutomation.RING_LIGHTS,
                    i=LightingAutomation.OFF,
                    f=0.0
                ))
            
            if is_jump:
                beatmap.basicBeatmapEvents.append(BasicBeatmapEvent(
                    b=beat + fade_time,
                    et=LightingAutomation.CENTER_LIGHTS,
                    i=LightingAutomation.OFF,
                    f=0.0
                ))
        
        # Sort events
        beatmap.sort_objects()