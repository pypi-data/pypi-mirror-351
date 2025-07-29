"""
Beat Saber Mapping Framework - Core Data Models

This module provides the Pydantic models representing Beat Saber map structures,
including Info.dat and beatmap data files. These models enable validation, serialization,
and deserialization of Beat Saber map data with proper type checking.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, model_validator
import json
import os

# Constants
DEFAULT_NJS = 10
DEFAULT_OFFSET = 0

class Difficulty(str, Enum):
    """Standard difficulty levels in Beat Saber"""
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"
    EXPERT = "Expert"
    EXPERT_PLUS = "ExpertPlus"

class Characteristic(str, Enum):
    """Official Beat Saber map characteristics"""
    STANDARD = "Standard"
    NO_ARROWS = "NoArrows"
    ONE_SABER = "OneSaber"
    DEGREE_360 = "360Degree"
    DEGREE_90 = "90Degree"
    LEGACY = "Legacy"
    LAWLESS = "Lawless"  # SongCore addition
    LIGHTSHOW = "Lightshow"  # SongCore addition

class NoteColor(int, Enum):
    """Note colors (red = 0, blue = 1)"""
    RED = 0
    BLUE = 1

class NoteDirection(int, Enum):
    """Standard note cut directions"""
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    UP_LEFT = 4
    UP_RIGHT = 5
    DOWN_LEFT = 6
    DOWN_RIGHT = 7
    ANY = 8

class DifficultyBeatmap(BaseModel):
    """Represents a single difficulty beatmap within a characteristic set"""
    difficulty: str = Field(..., alias="_difficulty", description="Difficulty name")
    difficultyRank: int = Field(..., alias="_difficultyRank", description="Difficulty rank (1-9)")
    beatmapFilename: str = Field(..., alias="_beatmapFilename", description="Filename of the beatmap")
    noteJumpMovementSpeed: float = Field(..., alias="_noteJumpMovementSpeed", description="Note jump movement speed")
    noteJumpStartBeatOffset: float = Field(..., alias="_noteJumpStartBeatOffset", description="Note jump start beat offset")
    customData: Optional[Dict[str, Any]] = Field(None, alias="_customData", description="Custom data for the difficulty")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @model_validator(mode='after')
    def validate_difficulty(self):
        """Validate that the difficulty is a known value or a custom one"""
        if self.difficulty not in [d.value for d in Difficulty]:
            # Allow custom difficulties but log a warning
            print(f"Warning: Non-standard difficulty '{self.difficulty}' detected. This may not be compatible with all versions of Beat Saber.")
        return self

class DifficultyBeatmapSet(BaseModel):
    """Represents a set of beatmaps for a particular characteristic"""
    beatmapCharacteristicName: str = Field(..., alias="_beatmapCharacteristicName", description="Characteristic name (e.g., 'Standard')")
    difficultyBeatmaps: List[DifficultyBeatmap] = Field(..., alias="_difficultyBeatmaps", description="List of difficulty beatmaps")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }
    
    @model_validator(mode='after')
    def validate_characteristic(self):
        """Validate the characteristic and check for characteristic-specific requirements"""
        # Check if it's a standard characteristic
        if self.beatmapCharacteristicName not in [c.value for c in Characteristic]:
            print(f"Warning: Non-standard characteristic '{self.beatmapCharacteristicName}' detected. This may not be compatible with unmodded instances of Beat Saber.")
        
        # Characteristic-specific validations
        if self.beatmapCharacteristicName == Characteristic.ONE_SABER.value:
            # OneSaber should only have red notes when validated at runtime
            pass
        
        # 360Degree and 90Degree should have rotation events
        if self.beatmapCharacteristicName in [Characteristic.DEGREE_360.value, Characteristic.DEGREE_90.value]:
            # This would be checked at runtime when beatmap files are loaded
            pass
            
        return self

class InfoDat(BaseModel):
    """Represents the main Info.dat file for a Beat Saber map"""
    version: str = Field(..., alias="_version", description="Version of the map format")
    songName: str = Field(..., alias="_songName", description="Name of the song")
    songSubName: str = Field("", alias="_songSubName", description="Subname of the song")
    songAuthorName: str = Field(..., alias="_songAuthorName", description="Author of the song")
    levelAuthorName: str = Field(..., alias="_levelAuthorName", description="Author of the map")
    beatsPerMinute: float = Field(..., alias="_beatsPerMinute", description="BPM of the song")
    songTimeOffset: float = Field(0, alias="_songTimeOffset", description="Time offset of the song in seconds")
    shuffle: float = Field(0, alias="_shuffle", description="Shuffle value")
    shufflePeriod: float = Field(0, alias="_shufflePeriod", description="Shuffle period")
    previewStartTime: float = Field(0, alias="_previewStartTime", description="Start time of the preview in seconds")
    previewDuration: float = Field(0, alias="_previewDuration", description="Duration of the preview in seconds")
    songFilename: str = Field(..., alias="_songFilename", description="Filename of the song audio file")
    coverImageFilename: str = Field(..., alias="_coverImageFilename", description="Filename of the cover image")
    environmentName: str = Field(..., alias="_environmentName", description="Name of the environment")
    allDirectionsEnvironmentName: Optional[str] = Field(None, alias="_allDirectionsEnvironmentName", description="Name of the all directions environment")
    difficultyBeatmapSets: List[DifficultyBeatmapSet] = Field(..., alias="_difficultyBeatmapSets", description="List of difficulty beatmap sets")
    customData: Optional[Dict[str, Any]] = Field(None, alias="_customData", description="Custom data for the map")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @model_validator(mode='after')
    def validate_environments(self):
        """Validate environment names for compatibility"""
        if self.allDirectionsEnvironmentName is None and any(
            s.beatmapCharacteristicName in [Characteristic.DEGREE_360.value, Characteristic.DEGREE_90.value] 
            for s in self.difficultyBeatmapSets
        ):
            # Default to the same as the main environment if not specified
            self.allDirectionsEnvironmentName = self.environmentName
        
        return self

    def get_beatmap_filename(self, characteristic: str, difficulty: str) -> Optional[str]:
        """
        Get the filename for a specific characteristic and difficulty
        
        Args:
            characteristic: The map characteristic (e.g., "Standard", "OneSaber")
            difficulty: The difficulty level (e.g., "Easy", "Expert")
            
        Returns:
            The filename of the beatmap or None if not found
        """
        for beatmap_set in self.difficultyBeatmapSets:
            if beatmap_set.beatmapCharacteristicName == characteristic:
                for beatmap in beatmap_set.difficultyBeatmaps:
                    if beatmap.difficulty == difficulty:
                        return beatmap.beatmapFilename
        return None

    def add_difficulty(self, characteristic: str, difficulty: str, filename: str, 
                      njs: float = DEFAULT_NJS, offset: float = DEFAULT_OFFSET,
                      custom_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a new difficulty to an existing characteristic or create a new characteristic
        
        Args:
            characteristic: The map characteristic (e.g., "Standard", "OneSaber")
            difficulty: The difficulty level (e.g., "Easy", "Expert")
            filename: The filename for the beatmap file
            njs: Note jump speed
            offset: Note jump start beat offset
            custom_data: Any custom data for the difficulty
            
        Returns:
            True if added successfully, False if the difficulty already exists
        """
        # Check if difficulty already exists
        if self.get_beatmap_filename(characteristic, difficulty) is not None:
            return False
            
        # Get difficulty rank
        rank = {
            Difficulty.EASY.value: 1,
            Difficulty.NORMAL.value: 3,
            Difficulty.HARD.value: 5,
            Difficulty.EXPERT.value: 7,
            Difficulty.EXPERT_PLUS.value: 9
        }.get(difficulty, 1)  # Default to 1 for custom difficulties
        
        # Create new beatmap
        new_beatmap = DifficultyBeatmap(
            difficulty=difficulty,
            difficultyRank=rank,
            beatmapFilename=filename,
            noteJumpMovementSpeed=njs,
            noteJumpStartBeatOffset=offset,
            customData=custom_data
        )
        
        # Find characteristic or create new one
        for beatmap_set in self.difficultyBeatmapSets:
            if beatmap_set.beatmapCharacteristicName == characteristic:
                beatmap_set.difficultyBeatmaps.append(new_beatmap)
                return True
        
        # Characteristic not found, create new set
        self.difficultyBeatmapSets.append(DifficultyBeatmapSet(
            beatmapCharacteristicName=characteristic,
            difficultyBeatmaps=[new_beatmap]
        ))
        
        return True

    def remove_difficulty(self, characteristic: str, difficulty: str) -> bool:
        """
        Remove a difficulty from a characteristic
        
        Args:
            characteristic: The map characteristic
            difficulty: The difficulty level
            
        Returns:
            True if removed successfully, False if not found
        """
        for i, beatmap_set in enumerate(self.difficultyBeatmapSets):
            if beatmap_set.beatmapCharacteristicName == characteristic:
                for j, beatmap in enumerate(beatmap_set.difficultyBeatmaps):
                    if beatmap.difficulty == difficulty:
                        del beatmap_set.difficultyBeatmaps[j]
                        
                        # If no more difficulties in this characteristic, remove the set
                        if not beatmap_set.difficultyBeatmaps:
                            del self.difficultyBeatmapSets[i]
                            
                        return True
        return False

    @classmethod
    def from_file(cls, filename: str) -> 'InfoDat':
        """
        Load an Info.dat file
        
        Args:
            filename: Path to the Info.dat file
            
        Returns:
            Parsed InfoDat object
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.model_validate(data)

    def save_to_file(self, filename: str) -> None:
        """
        Save to an Info.dat file
        
        Args:
            filename: Path where the Info.dat file should be saved
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(exclude_none=True, by_alias=True), f, indent=2)

# Beatmap file models
class BPMEvent(BaseModel):
    """Beat-per-minute change event"""
    b: float = Field(..., description="Beat time")
    m: float = Field(..., description="BPM value")

class RotationEvent(BaseModel):
    """Environment rotation event (for 360/90 degree maps)"""
    b: float = Field(..., description="Beat time")
    e: int = Field(..., description="Event type")
    r: float = Field(..., description="Rotation value in degrees")

class ColorNote(BaseModel):
    """A standard note (red or blue cube)"""
    b: float = Field(..., description="Beat time")
    x: int = Field(..., description="X position (0-3)")
    y: int = Field(..., description="Y position (0-2)")
    c: int = Field(..., description="Color (0=red, 1=blue)")
    d: int = Field(..., description="Direction (0-8)")
    a: int = Field(0, description="Angle offset")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the note")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }
    
    @model_validator(mode='after')
    def validate_position(self):
        """Validate that note position is within the standard play area"""
        if not (0 <= self.x <= 3 and 0 <= self.y <= 2):
            print(f"Warning: Note at beat {self.b} has position outside standard grid: ({self.x}, {self.y})")
        return self

class BombNote(BaseModel):
    """A bomb note"""
    b: float = Field(..., description="Beat time")
    x: int = Field(..., description="X position (0-3)")
    y: int = Field(..., description="Y position (0-2)")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the bomb")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class Obstacle(BaseModel):
    """A wall/obstacle"""
    b: float = Field(..., description="Beat time")
    d: float = Field(..., description="Duration in beats")
    x: int = Field(..., description="X position (0-3)")
    y: int = Field(..., description="Y position (0-2)")
    w: int = Field(..., description="Width")
    h: int = Field(..., description="Height")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the obstacle")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class Slider(BaseModel):
    """A slider note (chain)"""
    c: int = Field(..., description="Color (0=red, 1=blue)")
    b: float = Field(..., description="Beat time")
    x: int = Field(..., description="X position (0-3)")
    y: int = Field(..., description="Y position (0-2)")
    d: int = Field(..., description="Direction (0-8)")
    mu: int = Field(..., description="Multiplier")
    tb: float = Field(..., description="Tail beat")
    tx: int = Field(..., description="Tail X position")
    ty: int = Field(..., description="Tail Y position")
    tc: int = Field(..., description="Tail color")
    tmu: int = Field(..., description="Tail multiplier")
    m: int = Field(..., description="Slider type")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the slider")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class BurstSlider(BaseModel):
    """A burst slider note (arc)"""
    c: int = Field(..., description="Color (0=red, 1=blue)")
    b: float = Field(..., description="Beat time")
    x: int = Field(..., description="X position (0-3)")
    y: int = Field(..., description="Y position (0-2)")
    d: int = Field(..., description="Direction (0-8)")
    tb: float = Field(..., description="Tail beat")
    tx: int = Field(..., description="Tail X position")
    ty: int = Field(..., description="Tail Y position")
    sc: int = Field(..., description="Slice count")
    s: float = Field(..., description="Squish factor")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the burst slider")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class BasicBeatmapEvent(BaseModel):
    """A basic lighting/environment event"""
    b: float = Field(..., description="Beat time")
    et: int = Field(..., description="Event type")
    i: int = Field(..., description="Index")
    f: float = Field(..., description="Float value")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the event")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class ColorBoostBeatmapEvent(BaseModel):
    """Color boost event (lighting boost effect)"""
    b: float = Field(..., description="Beat time")
    o: bool = Field(..., description="On/off")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the event")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class Waypoint(BaseModel):
    """Player movement waypoint for 360/90 degree maps"""
    b: float = Field(..., description="Beat time")
    x: int = Field(..., description="X position")
    y: int = Field(..., description="Y position")
    d: int = Field(..., description="Direction")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the waypoint")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class BasicEventTypesWithKeywords(BaseModel):
    """Maps event keywords to event types"""
    k: str = Field(..., description="Keyword")
    e: List[int] = Field(..., description="Event types")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class CustomEvent(BaseModel):
    """A mod-specific custom event"""
    b: float = Field(..., description="Beat time")
    t: str = Field(..., description="Event type")
    d: Dict[str, Any] = Field(..., description="Event data")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class BeatmapFile(BaseModel):
    """Represents a Beat Saber beatmap file (e.g., Expert.dat)"""
    version: str = Field(..., description="Version of the beatmap format")
    bpmEvents: List[BPMEvent] = Field(default_factory=list, description="BPM events")
    rotationEvents: List[RotationEvent] = Field(default_factory=list, description="Rotation events")
    colorNotes: List[ColorNote] = Field(default_factory=list, description="Color notes")
    bombNotes: List[BombNote] = Field(default_factory=list, description="Bomb notes")
    obstacles: List[Obstacle] = Field(default_factory=list, description="Obstacles")
    sliders: List[Slider] = Field(default_factory=list, description="Sliders")
    burstSliders: List[BurstSlider] = Field(default_factory=list, description="Burst sliders")
    basicBeatmapEvents: List[BasicBeatmapEvent] = Field(default_factory=list, description="Basic beatmap events")
    colorBoostBeatmapEvents: List[ColorBoostBeatmapEvent] = Field(default_factory=list, description="Color boost events")
    waypoints: List[Waypoint] = Field(default_factory=list, description="Waypoints")
    basicEventTypesWithKeywords: Dict[str, List[BasicEventTypesWithKeywords]] = Field(default_factory=dict, description="Basic event types with keywords")
    lightColorEventBoxGroups: List[Dict[str, Any]] = Field(default_factory=list, description="Light color event box groups")
    lightRotationEventBoxGroups: List[Dict[str, Any]] = Field(default_factory=list, description="Light rotation event box groups")
    lightTranslationEventBoxGroups: List[Dict[str, Any]] = Field(default_factory=list, description="Light translation event box groups")
    vfxEventBoxGroups: List[Dict[str, Any]] = Field(default_factory=list, description="VFX event box groups")
    fxEventsCollections: Optional[Dict[str, List[Dict[str, Any]]]] = Field(None, alias="_fxEventsCollections", description="FX events collections")
    useNormalEventsAsCompatibleEvents: bool = Field(False, description="Use normal events as compatible events")
    customData: Optional[Dict[str, Any]] = Field(None, description="Custom data for the beatmap")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    def add_rotation_event(self, beat: float, event_type: int, rotation: float) -> RotationEvent:
        """
        Add a rotation event to the beatmap
        
        Args:
            beat: Beat time
            event_type: Event type
            rotation: Rotation value in degrees
            
        Returns:
            The created RotationEvent object
        """
        rotation_event = RotationEvent(b=beat, e=event_type, r=rotation)
        self.rotationEvents.append(rotation_event)
        return rotation_event

    def ensure_model_objects(self) -> None:
        """
        Ensure all objects in the beatmap are proper model objects and not dictionaries
        
        This is helpful when loading from JSON or when objects were added as dictionaries
        """
        # Convert all objects to their respective model types
        for i, obj in enumerate(self.rotationEvents):
            if isinstance(obj, dict):
                self.rotationEvents[i] = RotationEvent.model_validate(obj)
                
        for i, obj in enumerate(self.colorNotes):
            if isinstance(obj, dict):
                self.colorNotes[i] = ColorNote.model_validate(obj)
        
        for i, obj in enumerate(self.bombNotes):
            if isinstance(obj, dict):
                self.bombNotes[i] = BombNote.model_validate(obj)
        
        for i, obj in enumerate(self.obstacles):
            if isinstance(obj, dict):
                self.obstacles[i] = Obstacle.model_validate(obj)
        
        for i, obj in enumerate(self.bpmEvents):
            if isinstance(obj, dict):
                self.bpmEvents[i] = BPMEvent.model_validate(obj)
                
        for i, obj in enumerate(self.sliders):
            if isinstance(obj, dict):
                self.sliders[i] = Slider.model_validate(obj)
                
        for i, obj in enumerate(self.burstSliders):
            if isinstance(obj, dict):
                self.burstSliders[i] = BurstSlider.model_validate(obj)
                
        for i, obj in enumerate(self.basicBeatmapEvents):
            if isinstance(obj, dict):
                self.basicBeatmapEvents[i] = BasicBeatmapEvent.model_validate(obj)
                
        for i, obj in enumerate(self.colorBoostBeatmapEvents):
            if isinstance(obj, dict):
                self.colorBoostBeatmapEvents[i] = ColorBoostBeatmapEvent.model_validate(obj)
                
        for i, obj in enumerate(self.waypoints):
            if isinstance(obj, dict):
                self.waypoints[i] = Waypoint.model_validate(obj)

    def sort_objects(self) -> 'BeatmapFile':
        """
        Sort all objects by beat time for more efficient processing and better readability
        
        Returns:
            Self for method chaining
        """
        # Helper function to safely sort potentially mixed object types
        def safe_sort(objects_list, attr='b'):
            if not objects_list:
                return
            
            # Check if we need to convert any dictionaries to proper model objects
            for i, obj in enumerate(objects_list):
                if isinstance(obj, dict) and attr in obj:
                    # Convert dictionary to the appropriate model object
                    if objects_list is self.rotationEvents:
                        objects_list[i] = RotationEvent.model_validate(obj)
                    elif objects_list is self.colorNotes:
                        objects_list[i] = ColorNote.model_validate(obj)
                    elif objects_list is self.bombNotes:
                        objects_list[i] = BombNote.model_validate(obj)
                    elif objects_list is self.obstacles:
                        objects_list[i] = Obstacle.model_validate(obj)
                    elif objects_list is self.bpmEvents:
                        objects_list[i] = BPMEvent.model_validate(obj)
                    elif objects_list is self.sliders:
                        objects_list[i] = Slider.model_validate(obj)
                    elif objects_list is self.burstSliders:
                        objects_list[i] = BurstSlider.model_validate(obj)
                    elif objects_list is self.basicBeatmapEvents:
                        objects_list[i] = BasicBeatmapEvent.model_validate(obj)
                    elif objects_list is self.colorBoostBeatmapEvents:
                        objects_list[i] = ColorBoostBeatmapEvent.model_validate(obj)
                    elif objects_list is self.waypoints:
                        objects_list[i] = Waypoint.model_validate(obj)
            
            # Sort using the specified attribute
            try:
                objects_list.sort(key=lambda x: getattr(x, attr) if hasattr(x, attr) else (x[attr] if isinstance(x, dict) and attr in x else 0))
            except (TypeError, KeyError) as e:
                print(f"Warning: Could not sort some objects: {e}")
        
        # Sort all object lists
        safe_sort(self.bpmEvents)
        safe_sort(self.rotationEvents)
        safe_sort(self.colorNotes)
        safe_sort(self.bombNotes)
        safe_sort(self.obstacles)
        safe_sort(self.sliders)
        safe_sort(self.burstSliders)
        safe_sort(self.basicBeatmapEvents)
        safe_sort(self.colorBoostBeatmapEvents)
        safe_sort(self.waypoints)
        
        return self

    def validate_for_characteristic(self, characteristic: str) -> List[str]:
        """
        Validate the beatmap for a specific characteristic
        
        Args:
            characteristic: The map characteristic to validate for
            
        Returns:
            List of validation warnings/errors
        """
        warnings = []
        
        if characteristic == Characteristic.ONE_SABER.value:
            # Check for blue notes in OneSaber maps
            blue_notes = [note for note in self.colorNotes if note.c == NoteColor.BLUE]
            if blue_notes:
                warnings.append(f"OneSaber map contains {len(blue_notes)} blue notes, which is not standard")
        
        if characteristic in [Characteristic.DEGREE_360.value, Characteristic.DEGREE_90.value]:
            # Check for rotation events in 360/90 degree maps
            if not self.rotationEvents:
                warnings.append(f"{characteristic} map contains no rotation events")
                
        if characteristic == Characteristic.NO_ARROWS.value:
            # Check that all notes have direction 8 (any)
            directional_notes = [note for note in self.colorNotes if note.d != NoteDirection.ANY]
            if directional_notes:
                warnings.append(f"NoArrows map contains {len(directional_notes)} directional notes, which is not standard")
        
        return warnings

    # Helper methods
    @classmethod
    def from_file(cls, filename: str) -> 'BeatmapFile':
        """
        Load a beatmap file
        
        Args:
            filename: Path to the beatmap file
            
        Returns:
            Parsed BeatmapFile object
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.model_validate(data)

    def save_to_file(self, filename: str) -> None:
        """
        Save to a beatmap file
        
        Args:
            filename: Path where the beatmap file should be saved
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Ensure all objects are proper model objects before saving
        self.ensure_model_objects()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.model_dump(exclude_none=True, by_alias=True), f, indent=2)

    def get_custom_events(self) -> List[CustomEvent]:
        """
        Get custom events from customData
        
        Returns:
            List of CustomEvent objects
        """
        if not self.customData or 'customEvents' not in self.customData:
            return []
        
        events = []
        for event_data in self.customData['customEvents']:
            events.append(CustomEvent.model_validate(event_data))
        return events

    def add_custom_event(self, event: CustomEvent) -> None:
        """
        Add a custom event to customData
        
        Args:
            event: The CustomEvent to add
        """
        if not self.customData:
            self.customData = {}
        
        if 'customEvents' not in self.customData:
            self.customData['customEvents'] = []
        
        self.customData['customEvents'].append(event.model_dump(exclude_none=True))
        
    def add_fake_note(self, note: ColorNote) -> None:
        """
        Add a fake note to customData.fakeColorNotes
        
        Args:
            note: The ColorNote to add as a fake note
        """
        if not self.customData:
            self.customData = {}
        
        if 'fakeColorNotes' not in self.customData:
            self.customData['fakeColorNotes'] = []
        
        self.customData['fakeColorNotes'].append(note.model_dump(exclude_none=True))
        
    def add_fake_obstacle(self, obstacle: Obstacle) -> None:
        """
        Add a fake obstacle to customData.fakeObstacles
        
        Args:
            obstacle: The Obstacle to add as a fake obstacle
        """
        if not self.customData:
            self.customData = {}
        
        if 'fakeObstacles' not in self.customData:
            self.customData['fakeObstacles'] = []
        
        self.customData['fakeObstacles'].append(obstacle.model_dump(exclude_none=True))