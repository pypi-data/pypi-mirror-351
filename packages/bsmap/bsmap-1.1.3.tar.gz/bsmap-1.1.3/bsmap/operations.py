"""
Beat Saber Mapping Framework - Map Operations

This module provides utilities for common map operations like
mirroring, copying sections, and batch modifications.
"""

from typing import List, Callable
import copy

from .models import (
    BeatmapFile, ColorNote, Obstacle, NoteDirection
)

class MapOperations:
    """Utility class for common map operations"""
    
    @staticmethod
    def mirror_notes(
        notes: List[ColorNote],
        keep_colors: bool = False
    ) -> List[ColorNote]:
        """
        Mirror a set of notes horizontally and swap colors
        
        Args:
            notes: List of notes to mirror
            keep_colors: If True, keeps original colors, otherwise swaps them
            
        Returns:
            List of mirrored notes
        """
        mirrored = []
        
        # Direction mapping for mirroring
        direction_map = {
            NoteDirection.LEFT.value: NoteDirection.RIGHT.value,
            NoteDirection.RIGHT.value: NoteDirection.LEFT.value,
            NoteDirection.UP_LEFT.value: NoteDirection.UP_RIGHT.value,
            NoteDirection.UP_RIGHT.value: NoteDirection.UP_LEFT.value,
            NoteDirection.DOWN_LEFT.value: NoteDirection.DOWN_RIGHT.value,
            NoteDirection.DOWN_RIGHT.value: NoteDirection.DOWN_LEFT.value,
            NoteDirection.UP.value: NoteDirection.UP.value,
            NoteDirection.DOWN.value: NoteDirection.DOWN.value,
            NoteDirection.ANY.value: NoteDirection.ANY.value,
        }
        
        for note in notes:
            # Create a copy of the note
            mirrored_note = copy.deepcopy(note)
            
            # Mirror X position (0->3, 1->2, 2->1, 3->0)
            mirrored_note.x = 3 - note.x
            
            # Swap color if not keeping colors
            if not keep_colors:
                mirrored_note.c = 1 if note.c == 0 else 0
            
            # Mirror direction
            mirrored_note.d = direction_map.get(note.d, note.d)
            
            # Mirror custom data if needed
            if mirrored_note.customData and "coordinates" in mirrored_note.customData:
                coords = mirrored_note.customData["coordinates"]
                if isinstance(coords, list) and len(coords) >= 1:
                    # Mirror X coordinate
                    coords[0] = -coords[0]
            
            mirrored.append(mirrored_note)
        
        return mirrored
    
    @staticmethod
    def mirror_obstacles(obstacles: List[Obstacle]) -> List[Obstacle]:
        """
        Mirror a set of obstacles horizontally
        
        Args:
            obstacles: List of obstacles to mirror
            
        Returns:
            List of mirrored obstacles
        """
        mirrored = []
        
        for obstacle in obstacles:
            # Create a copy of the obstacle
            mirrored_obstacle = copy.deepcopy(obstacle)
            
            # Mirror X position
            mirrored_obstacle.x = 3 - (obstacle.x + obstacle.w - 1)
            
            # Mirror custom data if needed
            if mirrored_obstacle.customData and "coordinates" in mirrored_obstacle.customData:
                coords = mirrored_obstacle.customData["coordinates"]
                if isinstance(coords, list) and len(coords) >= 1:
                    # Mirror X coordinate
                    coords[0] = -coords[0]
            
            mirrored.append(mirrored_obstacle)
        
        return mirrored
    
    @staticmethod
    def mirror_map(beatmap: BeatmapFile) -> BeatmapFile:
        """
        Create a mirrored version of an entire beatmap
        
        Args:
            beatmap: The beatmap to mirror
            
        Returns:
            A new mirrored beatmap
        """
        # Create a deep copy of the beatmap
        mirrored = copy.deepcopy(beatmap)
        
        # Mirror notes
        mirrored.colorNotes = MapOperations.mirror_notes(beatmap.colorNotes)
        
        # Mirror bombs (only position)
        for bomb in mirrored.bombNotes:
            bomb.x = 3 - bomb.x
        
        # Mirror obstacles
        mirrored.obstacles = MapOperations.mirror_obstacles(beatmap.obstacles)
        
        # Mirror sliders
        for slider in mirrored.sliders:
            # Swap colors
            slider.c = 1 if slider.c == 0 else 0
            slider.tc = 1 if slider.tc == 0 else 0
            
            # Mirror positions
            slider.x = 3 - slider.x
            slider.tx = 3 - slider.tx
        
        # Mirror burst sliders
        for slider in mirrored.burstSliders:
            # Swap colors
            slider.c = 1 if slider.c == 0 else 0
            
            # Mirror positions
            slider.x = 3 - slider.x
            slider.tx = 3 - slider.tx
        
        return mirrored
    
    @staticmethod
    def copy_section(
        source: BeatmapFile,
        start_beat: float,
        end_beat: float
    ) -> BeatmapFile:
        """
        Copy a section of a beatmap
        
        Args:
            source: Source beatmap
            start_beat: Start beat position (inclusive)
            end_beat: End beat position (exclusive)
            
        Returns:
            A new beatmap containing only the specified section
        """
        # Create a new empty beatmap with same version
        section = BeatmapFile(version=source.version)
        
        # Helper function to copy objects in beat range
        def copy_objects_in_range(source_list, target_list):
            for obj in source_list:
                if start_beat <= obj.b < end_beat:
                    target_list.append(copy.deepcopy(obj))
        
        # Copy all object types
        copy_objects_in_range(source.colorNotes, section.colorNotes)
        copy_objects_in_range(source.bombNotes, section.bombNotes)
        copy_objects_in_range(source.obstacles, section.obstacles)
        copy_objects_in_range(source.bpmEvents, section.bpmEvents)
        copy_objects_in_range(source.rotationEvents, section.rotationEvents)
        copy_objects_in_range(source.sliders, section.sliders)
        copy_objects_in_range(source.burstSliders, section.burstSliders)
        copy_objects_in_range(source.basicBeatmapEvents, section.basicBeatmapEvents)
        copy_objects_in_range(source.colorBoostBeatmapEvents, section.colorBoostBeatmapEvents)
        copy_objects_in_range(source.waypoints, section.waypoints)
        
        # Copy custom data
        if source.customData:
            section.customData = copy.deepcopy(source.customData)
        
        return section
    
    @staticmethod
    def paste_section(
        target: BeatmapFile,
        section: BeatmapFile,
        target_beat: float,
        offset_lighting: bool = True
    ) -> None:
        """
        Paste a section into a target beatmap at a specific beat
        
        Args:
            target: Target beatmap to paste into
            section: Section to paste
            target_beat: Beat position to paste at
            offset_lighting: Whether to offset lighting events
        """
        # Find the earliest beat in the section
        min_beat = float('inf')
        for notes in [section.colorNotes, section.bombNotes, section.obstacles]:
            if notes and notes[0].b < min_beat:
                min_beat = notes[0].b
        
        if min_beat == float('inf'):
            min_beat = 0
        
        # Calculate beat offset
        beat_offset = target_beat - min_beat
        
        # Helper function to paste objects with offset
        def paste_objects_with_offset(source_list, target_list):
            for obj in source_list:
                new_obj = copy.deepcopy(obj)
                new_obj.b += beat_offset
                target_list.append(new_obj)
        
        # Paste all object types
        paste_objects_with_offset(section.colorNotes, target.colorNotes)
        paste_objects_with_offset(section.bombNotes, target.bombNotes)
        paste_objects_with_offset(section.obstacles, target.obstacles)
        paste_objects_with_offset(section.bpmEvents, target.bpmEvents)
        paste_objects_with_offset(section.rotationEvents, target.rotationEvents)
        paste_objects_with_offset(section.sliders, target.sliders)
        paste_objects_with_offset(section.burstSliders, target.burstSliders)
        
        # Only offset lighting events if requested
        if offset_lighting:
            paste_objects_with_offset(section.basicBeatmapEvents, target.basicBeatmapEvents)
            paste_objects_with_offset(section.colorBoostBeatmapEvents, target.colorBoostBeatmapEvents)
        else:
            target.basicBeatmapEvents.extend(section.basicBeatmapEvents)
            target.colorBoostBeatmapEvents.extend(section.colorBoostBeatmapEvents)
        
        paste_objects_with_offset(section.waypoints, target.waypoints)
        
        # Sort all objects
        target.sort_objects()
    
    @staticmethod
    def batch_modify_notes(
        beatmap: BeatmapFile,
        start_beat: float,
        end_beat: float,
        modifier_func: Callable[[ColorNote], None]
    ) -> None:
        """
        Apply a modifier function to all notes in a beat range
        
        Args:
            beatmap: Beatmap to modify
            start_beat: Start beat position (inclusive)
            end_beat: End beat position (exclusive)
            modifier_func: Function to apply to each note
        """
        for note in beatmap.colorNotes:
            if start_beat <= note.b < end_beat:
                modifier_func(note)
        
        # Sort to ensure proper order
        beatmap.sort_objects()
    
    @staticmethod
    def shift_section(
        beatmap: BeatmapFile,
        start_beat: float,
        end_beat: float,
        shift_amount: float
    ) -> None:
        """
        Shift a section of a beatmap by a certain amount of beats
        
        Args:
            beatmap: Beatmap to modify
            start_beat: Start beat position (inclusive)
            end_beat: End beat position (exclusive)
            shift_amount: Amount of beats to shift (positive or negative)
        """
        # Helper function to shift objects in beat range
        def shift_objects(object_list):
            for obj in object_list:
                if start_beat <= obj.b < end_beat:
                    obj.b += shift_amount
        
        # Shift all object types
        shift_objects(beatmap.colorNotes)
        shift_objects(beatmap.bombNotes)
        shift_objects(beatmap.obstacles)
        shift_objects(beatmap.bpmEvents)
        shift_objects(beatmap.rotationEvents)
        shift_objects(beatmap.sliders)
        shift_objects(beatmap.burstSliders)
        shift_objects(beatmap.basicBeatmapEvents)
        shift_objects(beatmap.colorBoostBeatmapEvents)
        shift_objects(beatmap.waypoints)
        
        # Sort to ensure proper order
        beatmap.sort_objects()
    
    @staticmethod
    def adjust_difficulty(
        beatmap: BeatmapFile,
        njs_multiplier: float = 1.0,
        density_multiplier: float = 1.0
    ) -> BeatmapFile:
        """
        Create a new beatmap with adjusted difficulty parameters
        
        Args:
            beatmap: Source beatmap
            njs_multiplier: Multiplier for note jump speed
            density_multiplier: Multiplier for note density (1.0 = no change)
            
        Returns:
            A new beatmap with adjusted difficulty
        """
        # Create a deep copy of the beatmap
        adjusted = copy.deepcopy(beatmap)
        
        # Adjust note jump speed in custom data if present
        if adjusted.customData and "noteJumpMovementSpeed" in adjusted.customData:
            adjusted.customData["noteJumpMovementSpeed"] *= njs_multiplier
        
        # For individual notes with custom NJS
        for note in adjusted.colorNotes:
            if note.customData and "noteJumpMovementSpeed" in note.customData:
                note.customData["noteJumpMovementSpeed"] *= njs_multiplier
        
        # Adjust note density by removing notes if density_multiplier < 1.0
        if density_multiplier < 1.0:
            # Sort notes by beat time
            notes = sorted(adjusted.colorNotes, key=lambda n: n.b)
            
            # Calculate how many notes to keep
            keep_count = int(len(notes) * density_multiplier)
            
            if keep_count < len(notes):
                # Determine notes to keep with even spacing
                indices_to_keep = [int(i * (len(notes) - 1) / (keep_count - 1)) for i in range(keep_count)]
                notes_to_keep = [notes[i] for i in indices_to_keep]
                
                # Replace notes with reduced set
                adjusted.colorNotes = notes_to_keep
        
        return adjusted