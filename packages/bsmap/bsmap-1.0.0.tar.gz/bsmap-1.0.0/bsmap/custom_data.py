"""
Beat Saber Mapping Framework - Custom Data Models

This module provides Pydantic models for Beat Saber custom data structures,
including player settings, modifiers, and object properties for mods like
Chroma and Noodle Extensions.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, model_validator

# Custom data models for settings
class PlayerOptions(BaseModel):
    """Player-specific options and preferences"""
    leftHanded: Optional[bool] = Field(None, alias="_leftHanded", description="Enable left-handed mode")
    playerHeight: Optional[float] = Field(None, alias="_playerHeight", description="Override player height in meters")
    automaticPlayerHeight: Optional[bool] = Field(None, alias="_automaticPlayerHeight", description="Automatically adjust height based on player")
    sfxVolume: Optional[float] = Field(None, alias="_sfxVolume", description="Sound effects volume (0.0-1.0)")
    reduceDebris: Optional[bool] = Field(None, alias="_reduceDebris", description="Reduce debris particles")
    noTextsAndHuds: Optional[bool] = Field(None, alias="_noTextsAndHuds", description="Hide all UI elements")
    noFailEffects: Optional[bool] = Field(None, alias="_noFailEffects", description="Hide 'Miss' text")
    advancedHud: Optional[bool] = Field(None, alias="_advancedHud", description="Show advanced HUD elements")
    autoRestart: Optional[bool] = Field(None, alias="_autoRestart", description="Auto restart on fail")
    saberTrailIntensity: Optional[float] = Field(None, alias="_saberTrailIntensity", description="Saber trail intensity (0.0-1.0)")
    noteJumpDurationTypeSettings: Optional[str] = Field(None, alias="_noteJumpDurationTypeSettings", description="Dynamic/Static jump duration")
    noteJumpFixedDuration: Optional[float] = Field(None, alias="_noteJumpFixedDuration", description="Fixed jump duration in seconds")
    noteJumpStartBeatOffset: Optional[float] = Field(None, alias="_noteJumpStartBeatOffset", description="Note jump start beat offset")
    hideNoteSpawnEffect: Optional[bool] = Field(None, alias="_hideNoteSpawnEffect", description="Hide note spawn effects")
    adaptiveSfx: Optional[bool] = Field(None, alias="_adaptiveSfx", description="Enable adaptive sound effects")
    environmentEffectsFilterDefaultPreset: Optional[str] = Field(None, alias="_environmentEffectsFilterDefaultPreset", description="Default environment effects filter")
    environmentEffectsFilterExpertPlusPreset: Optional[str] = Field(None, alias="_environmentEffectsFilterExpertPlusPreset", description="Expert+ environment effects filter")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

    @model_validator(mode='after')
    def validate_values(self):
        """Validate numerical ranges"""
        if self.sfxVolume is not None and not (0 <= self.sfxVolume <= 1):
            raise ValueError("sfxVolume must be between 0.0 and 1.0")
            
        if self.saberTrailIntensity is not None and not (0 <= self.saberTrailIntensity <= 1):
            raise ValueError("saberTrailIntensity must be between 0.0 and 1.0")
            
        if self.noteJumpDurationTypeSettings is not None and self.noteJumpDurationTypeSettings not in ["Dynamic", "Static"]:
            raise ValueError("noteJumpDurationTypeSettings must be 'Dynamic' or 'Static'")
            
        return self

class Modifiers(BaseModel):
    """Gameplay modifiers that affect scoring and difficulty"""
    energyType: Optional[str] = Field(None, alias="_energyType", description="Energy type (Bar/Battery)")
    noFailOn0Energy: Optional[bool] = Field(None, alias="_noFailOn0Energy", description="Don't fail when energy reaches 0")
    instaFail: Optional[bool] = Field(None, alias="_instaFail", description="Fail on first miss")
    failOnSaberClash: Optional[bool] = Field(None, alias="_failOnSaberClash", description="Fail when sabers clash")
    enabledObstacleType: Optional[str] = Field(None, alias="_enabledObstacleType", description="All/FullHeightOnly/NoObstacles")
    fastNotes: Optional[bool] = Field(None, alias="_fastNotes", description="Force NJS to 20")
    strictAngles: Optional[bool] = Field(None, alias="_strictAngles", description="Enable strict angles for scoring")
    disappearingArrows: Optional[bool] = Field(None, alias="_disappearingArrows", description="Hide arrows on notes")
    ghostNotes: Optional[bool] = Field(None, alias="_ghostNotes", description="Make notes partially transparent")
    noBombs: Optional[bool] = Field(None, alias="_noBombs", description="Remove bombs from map")
    songSpeed: Optional[str] = Field(None, alias="_songSpeed", description="Normal/Faster/Slower/SuperFast")
    noArrows: Optional[bool] = Field(None, alias="_noArrows", description="Hide arrows on notes")
    proMode: Optional[bool] = Field(None, alias="_proMode", description="Enable pro mode scoring")
    zenMode: Optional[bool] = Field(None, alias="_zenMode", description="Remove fail conditions")
    smallCubes: Optional[bool] = Field(None, alias="_smallCubes", description="Use smaller note cubes")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }
    
    @model_validator(mode='after')
    def validate_values(self):
        """Validate enum values"""
        if self.energyType is not None and self.energyType not in ["Bar", "Battery"]:
            raise ValueError("energyType must be 'Bar' or 'Battery'")
            
        if self.enabledObstacleType is not None and self.enabledObstacleType not in ["All", "FullHeightOnly", "NoObstacles"]:
            raise ValueError("enabledObstacleType must be 'All', 'FullHeightOnly', or 'NoObstacles'")
            
        if self.songSpeed is not None and self.songSpeed not in ["Normal", "Faster", "Slower", "SuperFast"]:
            raise ValueError("songSpeed must be 'Normal', 'Faster', 'Slower', or 'SuperFast'")
            
        return self

class Environments(BaseModel):
    """Environment-related settings"""
    overrideEnvironments: Optional[bool] = Field(None, alias="_overrideEnvironments", description="Override user's environment settings")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class Colors(BaseModel):
    """Color-related settings"""
    overrideDefaultColors: Optional[bool] = Field(None, alias="_overrideDefaultColors", description="Override user's color scheme")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class Graphics(BaseModel):
    """Graphics-related settings"""
    mirrorGraphicsSettings: Optional[int] = Field(None, alias="_mirrorGraphicsSettings", description="Mirror quality (0-3)")
    mainEffectGraphicsSettings: Optional[int] = Field(None, alias="_mainEffectGraphicsSettings", description="Main effects quality (0-1)")
    smokeGraphicsSettings: Optional[int] = Field(None, alias="_smokeGraphicsSettings", description="Smoke effects quality (0-1)")
    burnMarkTrailsEnabled: Optional[bool] = Field(None, alias="_burnMarkTrailsEnabled", description="Enable burn trails left by sabers")
    screenDisplacementEffectsEnabled: Optional[bool] = Field(None, alias="_screenDisplacementEffectsEnabled", description="Enable screen displacement effects")
    maxShockwaveParticles: Optional[int] = Field(None, alias="_maxShockwaveParticles", description="Maximum shockwave particles (0-2)")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }
    
    @model_validator(mode='after')
    def validate_values(self):
        """Validate numerical ranges"""
        if self.mirrorGraphicsSettings is not None and not (0 <= self.mirrorGraphicsSettings <= 3):
            raise ValueError("mirrorGraphicsSettings must be between 0 and 3")
            
        if self.mainEffectGraphicsSettings is not None and not (0 <= self.mainEffectGraphicsSettings <= 1):
            raise ValueError("mainEffectGraphicsSettings must be 0 or 1")
            
        if self.smokeGraphicsSettings is not None and not (0 <= self.smokeGraphicsSettings <= 1):
            raise ValueError("smokeGraphicsSettings must be 0 or 1")
            
        if self.maxShockwaveParticles is not None and not (0 <= self.maxShockwaveParticles <= 2):
            raise ValueError("maxShockwaveParticles must be between 0 and 2")
            
        return self

class Chroma(BaseModel):
    """Chroma mod specific settings"""
    disableChromaEvents: Optional[bool] = Field(None, alias="_disableChromaEvents", description="Disable Chroma lighting events")
    disableEnvironmentEnhancements: Optional[bool] = Field(None, alias="_disableEnvironmentEnhancements", description="Disable Chroma environment enhancements")
    disableNoteColoring: Optional[bool] = Field(None, alias="_disableNoteColoring", description="Disable Chroma custom note colors")
    forceZenModeWalls: Optional[bool] = Field(None, alias="_forceZenModeWalls", description="Force walls to be non-solid like in Zen Mode")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

class Settings(BaseModel):
    """Container for all map settings"""
    playerOptions: Optional[PlayerOptions] = Field(None, alias="_playerOptions", description="Player-specific options")
    modifiers: Optional[Modifiers] = Field(None, alias="_modifiers", description="Gameplay modifiers")
    environments: Optional[Environments] = Field(None, alias="_environments", description="Environment settings")
    colors: Optional[Colors] = Field(None, alias="_colors", description="Color settings")
    graphics: Optional[Graphics] = Field(None, alias="_graphics", description="Graphics settings")
    chroma: Optional[Chroma] = Field(None, alias="_chroma", description="Chroma mod settings")

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }

# Custom data models for objects
class NoodleExtensions(BaseModel):
    """Noodle Extensions custom data for notes/obstacles"""
    coordinates: Optional[List[float]] = Field(None, description="Custom coordinates [x, y]")
    worldRotation: Optional[Union[float, List[float]]] = Field(None, description="World rotation (degrees)")
    localRotation: Optional[List[float]] = Field(None, description="Local rotation [x, y, z]")
    scale: Optional[List[float]] = Field(None, description="Scale [x, y, z]")
    noteJumpMovementSpeed: Optional[float] = Field(None, description="Custom NJS for this object")
    noteJumpStartBeatOffset: Optional[float] = Field(None, description="Custom offset for this object")
    uninteractable: Optional[bool] = Field(None, description="Make object uninteractable")
    flip: Optional[List[float]] = Field(None, description="Flip animation [line index, jump]")
    disableNoteGravity: Optional[bool] = Field(None, description="Disable floating animation")
    disableNoteLook: Optional[bool] = Field(None, description="Disable rotation toward player")
    disableBadCutDirection: Optional[bool] = Field(None, description="Disable wrong direction cut penalty")
    disableBadCutSpeed: Optional[bool] = Field(None, description="Disable insufficient speed cut penalty")
    disableBadCutSaberType: Optional[bool] = Field(None, description="Disable wrong saber cut penalty")
    link: Optional[str] = Field(None, description="Link group ID")
    track: Optional[Union[str, List[str]]] = Field(None, description="Track name or list of tracks")
    size: Optional[List[float]] = Field(None, description="Size override [w, h, l]")

    model_config = {
        "extra": "allow",
    }

class ChromaData(BaseModel):
    """Chroma mod custom data for notes/obstacles"""
    color: Optional[List[float]] = Field(None, description="RGBA color [r, g, b, a]")
    spawnEffect: Optional[bool] = Field(None, description="Enable/disable spawn effect")
    disableDebris: Optional[bool] = Field(None, description="Disable debris on cut")

    model_config = {
        "extra": "allow",
    }
    
    @model_validator(mode='after')
    def validate_color(self):
        """Validate RGBA color values"""
        if self.color:
            # Check color values are between 0-1
            if any(c < 0 or c > 1 for c in self.color):
                raise ValueError("Color values must be between 0.0 and 1.0")
                
            # Make sure there are 3 or 4 components
            if len(self.color) not in (3, 4):
                raise ValueError("Color must have 3 (RGB) or 4 (RGBA) components")
                
        return self

class Animation(BaseModel):
    """Animation data for objects"""
    offsetPosition: Optional[List[List[float]]] = Field(None, description="Position offset animation")
    localRotation: Optional[List[List[float]]] = Field(None, description="Local rotation animation")
    offsetWorldRotation: Optional[List[List[float]]] = Field(None, description="World rotation offset animation")
    scale: Optional[List[List[float]]] = Field(None, description="Scale animation")
    dissolve: Optional[List[List[float]]] = Field(None, description="Dissolve animation")
    dissolveArrow: Optional[List[List[float]]] = Field(None, description="Arrow dissolve animation")
    interactable: Optional[List[List[float]]] = Field(None, description="Interactable state animation")
    definitePosition: Optional[List[List[float]]] = Field(None, description="Absolute position animation")
    time: Optional[List[List[float]]] = Field(None, description="Time progression animation")
    color: Optional[List[List[float]]] = Field(None, description="Color animation")

    model_config = {
        "extra": "allow",
    }
    
    @model_validator(mode='after')
    def validate_animations(self):
        """Validate animation point definitions"""
        # Each animation type has specific requirements for point structure
        # Basic structure check for animation points
        for anim_name, points in self.model_dump(exclude_none=True).items():
            if not isinstance(points, list):
                raise ValueError(f"Animation '{anim_name}' must be a list of points")
                
            for i, point in enumerate(points):
                if not isinstance(point, list):
                    raise ValueError(f"Point {i} in '{anim_name}' must be a list of values")
        
        return self