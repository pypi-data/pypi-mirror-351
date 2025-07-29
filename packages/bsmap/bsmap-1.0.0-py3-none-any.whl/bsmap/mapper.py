"""
Beat Saber Mapping Framework - Mapper Utility

This module provides utility functions for working with Beat Saber maps,
including loading, saving, and creating maps with different characteristics.
"""

from typing import Dict, List, Tuple
from pathlib import Path

from .models import (
    InfoDat, BeatmapFile, DifficultyBeatmapSet, DifficultyBeatmap, 
    Characteristic, Difficulty
)
from .custom_data import Settings

class BeatSaberMapper:
    """Main class for working with Beat Saber maps"""
    
    @staticmethod
    def load_info_dat(filename: str) -> InfoDat:
        """
        Load an Info.dat file
        
        Args:
            filename: Path to the Info.dat file
            
        Returns:
            Parsed InfoDat object
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        return InfoDat.from_file(filename)
    
    @staticmethod
    def load_beatmap(filename: str) -> BeatmapFile:
        """
        Load a beatmap file
        
        Args:
            filename: Path to the beatmap file
            
        Returns:
            Parsed BeatmapFile object
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        return BeatmapFile.from_file(filename)
    
    @staticmethod
    def ensure_proper_objects(beatmap: BeatmapFile) -> None:
        """
        Ensure all objects in the beatmap are proper model objects
        
        Args:
            beatmap: The BeatmapFile to check and convert
        """
        beatmap.ensure_model_objects()
    
    @staticmethod
    def save_info_dat(info: InfoDat, filename: str) -> None:
        """
        Save an Info.dat file
        
        Args:
            info: The InfoDat object to save
            filename: Path where the file should be saved
        """
        info.save_to_file(filename)
    
    @staticmethod
    def save_beatmap(beatmap: BeatmapFile, filename: str) -> None:
        """
        Save a beatmap file
        
        Args:
            beatmap: The BeatmapFile object to save
            filename: Path where the file should be saved
        """
        # Ensure all objects are proper model objects before saving
        BeatSaberMapper.ensure_proper_objects(beatmap)
        beatmap.save_to_file(filename)
    
    @staticmethod
    def load_map_folder(folder_path: str) -> Tuple[InfoDat, Dict[str, BeatmapFile]]:
        """
        Load a map folder with Info.dat and all beatmap files
        
        Args:
            folder_path: Path to the map folder
            
        Returns:
            Tuple containing the Info.dat object and a dictionary of beatmap files
            
        Raises:
            FileNotFoundError: If Info.dat doesn't exist
        """
        folder_path = Path(folder_path)
        info_path = folder_path / "Info.dat"
        
        if not info_path.exists():
            raise FileNotFoundError(f"Info.dat not found in {folder_path}")
            
        info = BeatSaberMapper.load_info_dat(str(info_path))
        
        beatmaps = {}
        for beatmap_set in info.difficultyBeatmapSets:
            for beatmap in beatmap_set.difficultyBeatmaps:
                beatmap_path = folder_path / beatmap.beatmapFilename
                if beatmap_path.exists():
                    beatmaps[beatmap.beatmapFilename] = BeatSaberMapper.load_beatmap(str(beatmap_path))
                else:
                    print(f"Warning: Beatmap file {beatmap.beatmapFilename} referenced in Info.dat but not found")
        
        return info, beatmaps
    
    @staticmethod
    def save_map_folder(folder_path: str, info: InfoDat, beatmaps: Dict[str, BeatmapFile]) -> None:
        """
        Save a map folder with Info.dat and all beatmap files
        
        Args:
            folder_path: Path to the map folder
            info: The InfoDat object to save
            beatmaps: Dictionary of beatmap files to save
        """
        folder_path = Path(folder_path)
        folder_path.mkdir(parents=True, exist_ok=True)
        
        info_path = folder_path / "Info.dat"
        BeatSaberMapper.save_info_dat(info, str(info_path))
        
        for filename, beatmap in beatmaps.items():
            beatmap_path = folder_path / filename
            BeatSaberMapper.save_beatmap(beatmap, str(beatmap_path))
    
    @staticmethod
    def create_empty_map(
        song_name: str,
        song_author: str,
        level_author: str,
        bpm: float,
        audio_filename: str,
        cover_filename: str,
        environment: str = "DefaultEnvironment",
        characteristics: List[str] = [Characteristic.STANDARD.value],
        difficulties: List[str] = [d.value for d in Difficulty]
    ) -> Tuple[InfoDat, Dict[str, BeatmapFile]]:
        """
        Create an empty map with specified characteristics and difficulties
        
        Args:
            song_name: Name of the song
            song_author: Author of the song
            level_author: Author of the map
            bpm: Beats per minute
            audio_filename: Filename of the audio file
            cover_filename: Filename of the cover image
            environment: Environment name
            characteristics: List of characteristics to include
            difficulties: List of difficulties to include for each characteristic
            
        Returns:
            Tuple containing the Info.dat object and a dictionary of beatmap files
        """
        # Create difficulty beatmap sets
        difficulty_beatmap_sets = []
        beatmaps = {}
        
        for characteristic in characteristics:
            # Create difficulty beatmaps for this characteristic
            difficulty_beatmaps = []
            
            for diff in difficulties:
                # Create filename based on characteristic and difficulty
                if characteristic == Characteristic.STANDARD.value:
                    filename = f"{diff}.dat"
                else:
                    filename = f"{diff}{characteristic}.dat"
                
                # Create difficulty beatmap
                difficulty_beatmaps.append(DifficultyBeatmap(
                    difficulty=diff,
                    difficultyRank={"Easy": 1, "Normal": 3, "Hard": 5, "Expert": 7, "ExpertPlus": 9}.get(diff, 1),
                    beatmapFilename=filename,
                    noteJumpMovementSpeed=10,
                    noteJumpStartBeatOffset=0
                ))
                
                # Create empty beatmap file
                beatmaps[filename] = BeatmapFile(
                    version="3.3.0",
                    bpmEvents=[],
                    colorNotes=[]
                )
                
                # Add rotation events placeholder for 360/90 degree maps
                if characteristic in [Characteristic.DEGREE_360.value, Characteristic.DEGREE_90.value]:
                    beatmaps[filename].rotationEvents = []
                    beatmaps[filename].waypoints = []
            
            # Create difficulty beatmap set
            difficulty_beatmap_sets.append(DifficultyBeatmapSet(
                beatmapCharacteristicName=characteristic,
                difficultyBeatmaps=difficulty_beatmaps
            ))
        
        # Create all directions environment name if needed
        all_directions_env = None
        if any(c in [Characteristic.DEGREE_360.value, Characteristic.DEGREE_90.value] for c in characteristics):
            all_directions_env = environment
        
        # Create info.dat
        info = InfoDat(
            version="2.0.0",
            songName=song_name,
            songSubName="",
            songAuthorName=song_author,
            levelAuthorName=level_author,
            beatsPerMinute=bpm,
            songTimeOffset=0,
            shuffle=0,
            shufflePeriod=0,
            previewStartTime=0,
            previewDuration=0,
            songFilename=audio_filename,
            coverImageFilename=cover_filename,
            environmentName=environment,
            allDirectionsEnvironmentName=all_directions_env,
            difficultyBeatmapSets=difficulty_beatmap_sets
        )
        
        return info, beatmaps
    
    @staticmethod
    def apply_settings_to_difficulty(
        info: InfoDat, 
        characteristic: str, 
        difficulty: str, 
        settings: Settings
    ) -> None:
        """
        Apply settings to a specific difficulty
        
        Args:
            info: The InfoDat object to modify
            characteristic: The characteristic name
            difficulty: The difficulty name
            settings: The settings to apply
            
        Raises:
            ValueError: If the characteristic or difficulty is not found
        """
        for beatmap_set in info.difficultyBeatmapSets:
            if beatmap_set.beatmapCharacteristicName == characteristic:
                for beatmap in beatmap_set.difficultyBeatmaps:
                    if beatmap.difficulty == difficulty:
                        if not beatmap.customData:
                            beatmap.customData = {}
                        
                        if "_settings" not in beatmap.customData:
                            beatmap.customData["_settings"] = {}
                        
                        beatmap.customData["_settings"] = settings.model_dump(exclude_none=True, by_alias=True)
                        return
        
        raise ValueError(f"Difficulty {difficulty} for characteristic {characteristic} not found")
    
    @staticmethod
    def validate_map(
        info: InfoDat, 
        beatmaps: Dict[str, BeatmapFile]
    ) -> Dict[str, List[str]]:
        """
        Validate a complete map for issues
        
        Args:
            info: The InfoDat object
            beatmaps: Dictionary of beatmap files
            
        Returns:
            Dictionary of validation warnings/errors by filename
        """
        warnings = {}
        
        # Check Info.dat
        info_warnings = []
        
        # Check if all referenced beatmap files exist
        for beatmap_set in info.difficultyBeatmapSets:
            for beatmap in beatmap_set.difficultyBeatmaps:
                if beatmap.beatmapFilename not in beatmaps:
                    info_warnings.append(f"Beatmap file {beatmap.beatmapFilename} referenced in Info.dat not found")
        
        if info_warnings:
            warnings["Info.dat"] = info_warnings
        
        # Check beatmap files
        for filename, beatmap in beatmaps.items():
            beatmap_warnings = []
            
            # Find the characteristic for this beatmap
            characteristic = None
            for beatmap_set in info.difficultyBeatmapSets:
                for beatmap_info in beatmap_set.difficultyBeatmaps:
                    if beatmap_info.beatmapFilename == filename:
                        characteristic = beatmap_set.beatmapCharacteristicName
                        break
                if characteristic:
                    break
            
            # If we found the characteristic, validate for it
            if characteristic:
                characteristic_warnings = beatmap.validate_for_characteristic(characteristic)
                beatmap_warnings.extend(characteristic_warnings)
            
            # General beatmap validation
            if not beatmap.colorNotes:
                beatmap_warnings.append("Beatmap has no notes")
            
            if beatmap_warnings:
                warnings[filename] = beatmap_warnings
        
        return warnings

    @staticmethod
    def get_available_characteristics() -> List[str]:
        """
        Get a list of available characteristics
        
        Returns:
            List of characteristic names
        """
        return [c.value for c in Characteristic]