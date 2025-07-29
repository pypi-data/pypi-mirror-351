# Beat Saber Mapping Framework (bsmap)

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Core Concepts](#3-core-concepts)
4. [Getting Started](#4-getting-started)
5. [Module Reference](#5-module-reference)
6. [Advanced Features](#6-advanced-features)
7. [Best Practices](#7-best-practices)
8. [Troubleshooting](#8-troubleshooting)
9. [Contributing](#9-contributing)

## 1. Introduction

The Beat Saber Mapping Framework is a comprehensive Python library designed to simplify the creation, manipulation, and analysis of Beat Saber maps. Built on Pydantic for strong type validation, the framework provides an intuitive and object-oriented approach to Beat Saber mapping, supporting all official characteristics and various customization options through mods like Chroma and Noodle Extensions.

### Key Features

- **Complete Data Model:** Full support for all Beat Saber map components with type safety
- **Multi-Characteristic Support:** Support for all official characteristics (Standard, OneSaber, 360Degree, etc.)
- **Pattern Generation:** Built-in utilities for common note patterns
- **Map Analysis:** Automated difficulty estimation and issue detection
- **Lighting Automation:** Tools to generate synchronized lighting effects
- **Template Management:** Save and reuse mapping patterns
- **Map Operations:** Mirror, copy, shift, and manipulate map sections
- **Command-Line Interface:** Scriptable operations for automation

## 2. Installation

### Requirements

- Python 3.9 or higher
- Pydantic 2.0 or higher

### Installation via pip

```bash
pip install bsmap
```

### Manual Installation

```bash
git clone https://github.com/CodeSoftGit/bsmap.git
cd bsmap
pip install -e .
```

## 3. Core Concepts

### Map Structure

A Beat Saber map consists of:
- **Info.dat:** Contains metadata about the song and available difficulties
- **Beatmap Files:** Contains notes, obstacles, events, and other gameplay elements
- **Audio File:** The song audio file
- **Cover Image:** The map's cover art

### Key Components

- **Notes:** The red and blue cubes that players hit
- **Bombs:** Black spheres with points that must be avoided
- **Walls:** Obstacles that players must dodge
- **Events:** Lighting and environment effects
- **Characteristics:** Different play modes (Standard, OneSaber, etc.)
- **Difficulties:** Different difficulty levels (Easy, Normal, Hard, etc.)

### Data Flow

```text
[Disk: Input Files]
  - Info.dat (JSON)
  - <Difficulty>.dat (JSON, e.g., Expert.dat)
  - template.json (JSON, for bsmap.templates)
        |
        | (File Read, JSON Parsing)
        V
+-------------------------------------------------------------------------------------------------+
| bsmap.mapper.BeatSaberMapper                                                                    |
|-------------------------------------------------------------------------------------------------|
| - load_info_dat(filePath)                                                                       |
| - load_beatmap(filePath)                                                                        |
| - load_map_folder(folderPath)                                                                   |
| - create_empty_map(...)                                                                         |
|   (These methods parse JSON and instantiate Pydantic models from bsmap.models)                  |
+-------------------------------------------------------------------------------------------------+
        |
        | (Data converted to In-Memory Pydantic Model Instances)
        V
+-------------------------------------------------------------------------------------------------+
| In-Memory Data Representation (Defined in bsmap.models & bsmap.custom_data)                     |
|-------------------------------------------------------------------------------------------------|
| 1. info_dat_object: bsmap.models.InfoDat                                                        |
|    - Contains: _version, _songName, _bpm, _difficultyBeatmapSets (list of DifficultyBeatmapSet),|
|                _customData (can hold bsmap.custom_data.Settings), etc.                          |
|                                                                                                 |
| 2. beatmap_files_dict: Dict[str, bsmap.models.BeatmapFile]                                      |
|    - Key: beatmapFilename (e.g., "Expert.dat")                                                  |
|    - Value: beatmap_object: bsmap.models.BeatmapFile                                            |
|      - Contains: version, bpmEvents, rotationEvents, waypoints,                                 |
|                  colorNotes: List[bsmap.models.ColorNote]                                       |
|                  bombNotes: List[bsmap.models.BombNote]                                         |
|                  obstacles: List[bsmap.models.Obstacle]                                         |
|                  sliders: List[bsmap.models.Slider]                                             |
|                  basicBeatmapEvents: List[bsmap.models.BasicBeatmapEvent]                       |
|                  customData (can hold bsmap.custom_data.NoodleExtensions,                       |
|                              bsmap.custom_data.ChromaData, bsmap.custom_data.Animation), etc.   |
+-------------------------------------------------------------------------------------------------+
    |         ^                           |         ^                           |         ^
    | (Read)  | (Modify/Create)           | (Read)  | (Modify)                  | (R/W)   | (Create from/to file)
    V         |                           V         |                           V         |
+---------------------------+     +---------------------------------+     +--------------------------------+
| bsmap.analysis            |     | bsmap.autolights                |     | bsmap.templates                |
| (MapAnalysis class)       |     | (LightingAutomation class)      |     | (TemplateManager class)        |
|---------------------------|     |---------------------------------|     |--------------------------------|
| - get_note_statistics()   |---->| (Reads BeatmapFile object)      |<----| - save_template()              |
|   (Input: BeatmapFile)    |     |                                 |     |   (Input: BeatmapFile section) |
|   (Output: Dict stats)    |     | - generate_advanced_lighting()  |--+  |   (Output: template.json file) |
|                           |     |   (Input: BeatmapFile)          |  |  |                                |
| - identify_map_issues()   |     |   (Modifies BeatmapFile by      |  |  | - (load_template())            |
|   (Input: BeatmapFile)    |     |    adding BasicBeatmapEvents)   |  |  |   (Input: template.json file)  |
|   (Output: List issues)   |     +---------------------------------+  |  |   (Output: BeatmapFile object) |
+---------------------------+                           ^                |+--------------------------------+
                                                        | (Returns       |
                                                        |  modified      |
                                                        |  BeatmapFile   |
                                                        |  object)       |
                                                        +----------------+
    (bsmap.operations.MapOperations - also interacts here, modifying BeatmapFile objects)
    (bsmap.utils - provides helper functions)
        |
        | (Processed/Modified In-Memory Pydantic Model Instances)
        V
+-------------------------------------------------------------------------------------------------+
| bsmap.mapper.BeatSaberMapper                                                                    |
|-------------------------------------------------------------------------------------------------|
| - save_info_dat(InfoDat, filePath)                                                              |
| - save_beatmap(BeatmapFile, filePath)                                                           |
| - save_map_folder(folderPath, InfoDat, beatmap_files_dict)                                      |
| - validate_map(InfoDat, beatmap_files_dict) (Reads models, returns validation warnings)         |
|   (These methods serialize Pydantic models to JSON and write to files)                          |
+-------------------------------------------------------------------------------------------------+
        |
        | (File Write, Pydantic Model Serialization to JSON)
        V
[Disk: Output Files]
  - Info.dat (JSON)
  - <Difficulty>.dat (JSON)
  - (Potentially new/modified template.json files via TemplateManager)
```

## 4. Getting Started

### Creating a New Map

```python
from bsmap import BeatSaberMapper, Characteristic, Difficulty

# Create a new map
info, beatmaps = BeatSaberMapper.create_empty_map(
    song_name="My First Map",
    song_author="Artist Name",
    level_author="Your Name",
    bpm=120.0,
    audio_filename="song.ogg",
    cover_filename="cover.jpg",
    characteristics=[Characteristic.STANDARD.value],
    difficulties=[Difficulty.EASY.value, Difficulty.NORMAL.value]
)

# Save the map
BeatSaberMapper.save_map_folder("./my_first_map", info, beatmaps)
```

### Adding Notes

```python
from bsmap import ColorNote, NoteDirection, NoteColor

# Get the Easy difficulty beatmap
easy_beatmap = beatmaps["Easy.dat"]

# Add a red note
easy_beatmap.colorNotes.append(
    ColorNote(
        b=1.0,  # Beat time
        x=1,    # X position (0-3)
        y=0,    # Y position (0-2)
        c=NoteColor.RED.value,  # Color
        d=NoteDirection.UP.value  # Direction
    )
)

# Add a blue note
easy_beatmap.colorNotes.append(
    ColorNote(
        b=2.0,
        x=2,
        y=0,
        c=NoteColor.BLUE.value,
        d=NoteDirection.UP.value
    )
)

# Sort notes by beat time
easy_beatmap.sort_objects()
```

### Adding Lighting

```python
from bsmap.autolights import LightingAutomation

# Generate basic lighting
LightingAutomation.generate_basic_lighting(
    beatmap=easy_beatmap,
    beat_divisor=0.5,  # Eighth notes
    intensity=0.8
)
```

## 5. Module Reference

### Models Module

The `models` module contains Pydantic models representing Beat Saber map structures:

- `InfoDat`: Represents the main Info.dat file
- `BeatmapFile`: Represents a beatmap file (e.g., Expert.dat)
- `ColorNote`: Represents a red/blue note
- `BombNote`: Represents a bomb
- `Obstacle`: Represents a wall/obstacle
- `RotationEvent`: Represents a rotation event for 360/90 maps
- Enums: `Difficulty`, `Characteristic`, `NoteColor`, `NoteDirection`

### Mapper Module

The `mapper` module provides utilities for working with Beat Saber maps:

- `BeatSaberMapper.create_empty_map()`: Create a new map
- `BeatSaberMapper.load_map_folder()`: Load a map from a folder
- `BeatSaberMapper.save_map_folder()`: Save a map to a folder
- `BeatSaberMapper.validate_map()`: Validate a map for issues

### Operations Module

The `operations` module provides utilities for map operations:

- `MapOperations.mirror_map()`: Create a mirrored version of a map
- `MapOperations.copy_section()`: Copy a section of a map
- `MapOperations.paste_section()`: Paste a section into a map
- `MapOperations.shift_section()`: Shift a section of a map
- `MapOperations.adjust_difficulty()`: Adjust difficulty parameters

### Analysis Module

The `analysis` module provides utilities for analyzing maps:

- `MapAnalysis.get_note_statistics()`: Calculate statistics about a map
- `MapAnalysis.identify_mapping_issues()`: Identify potential issues
- `MapAnalysis.compare_maps()`: Compare two maps and calculate differences

### AutoLights Module

The `autolights` module provides utilities for lighting automation:

- `LightingAutomation.generate_basic_lighting()`: Generate basic lighting
- `LightingAutomation.generate_note_sync_lighting()`: Generate note-synchronized lighting
- `LightingAutomation.generate_advanced_lighting()`: Generate advanced lighting

### Templates Module

The `templates` module provides utilities for template management:

- `TemplateManager.save_template()`: Save a section as a template
- `TemplateManager.load_template()`: Load a template
- `TemplateManager.list_templates()`: List available templates
- `TemplateManager.search_templates()`: Search templates

## 6. Advanced Features

### Working with Custom Data

```python
from bsmap.custom_data import NoodleExtensions, ChromaData

# Add Noodle Extensions custom data
note.customData = {
    "track": "example_track",
    "coordinates": [1.5, 0.0],
    "disableNoteLook": True
}

# Using the structured models
noodle_data = NoodleExtensions(
    track="example_track",
    coordinates=[1.5, 0.0],
    disableNoteLook=True
)
note.customData = noodle_data.model_dump(exclude_none=True)
```

### Working with 360/90 Degree Maps

```python
# Create a 360 degree map
info, beatmaps = BeatSaberMapper.create_empty_map(
    # ... other parameters ...
    characteristics=[Characteristic.DEGREE_360.value],
    difficulties=[Difficulty.EXPERT.value]
)

# Get the Expert difficulty beatmap
expert_beatmap = beatmaps["Expert360Degree.dat"]

# Add rotation events
expert_beatmap.rotationEvents.append(
    RotationEvent(
        b=1.0,  # Beat time
        e=0,    # Event type
        r=90    # Rotation in degrees
    )
)
```

### Creating a Custom Pattern Template

```python
from bsmap import BeatmapFile, ColorNote, NoteColor, NoteDirection
from bsmap.operations import MapOperations
from bsmap.templates import TemplateManager

# --- 1. Define the Pattern ---
# Create a temporary BeatmapFile to hold the pattern.
# Notes within this pattern should be timed starting from beat 0 relative to the pattern itself.
pattern_bm = BeatmapFile(version="3.3.0") # Or match your map's specific version

# Example: A short, fast stream of 4 alternating notes
# (e.g., Red on left, Blue on right, all down-cuts)
pattern_notes_data = [
    ColorNote(b=0.0,  x=1, y=1, c=NoteColor.RED.value,  d=NoteDirection.DOWN.value),    # Beat 0 of pattern
    ColorNote(b=0.25, x=2, y=1, c=NoteColor.BLUE.value, d=NoteDirection.DOWN.value),   # Beat 0.25 of pattern
    ColorNote(b=0.5,  x=1, y=1, c=NoteColor.RED.value,  d=NoteDirection.UP.value),    # Beat 0.5 of pattern
    ColorNote(b=0.75, x=2, y=1, c=NoteColor.BLUE.value, d=NoteDirection.UP.value),   # Beat 0.75 of pattern
]
pattern_bm.colorNotes.extend(pattern_notes_data)
pattern_bm.sort_objects() # Good practice after adding or modifying map objects

# --- 2. Save the Pattern as a Template ---
template_name = "MyShortFastStream"
TemplateManager.save_template(
    beatmap_section=pattern_bm, # The BeatmapFile instance containing the pattern
    name=template_name,
    description="A short, fast stream of 4 alternating notes (R-B-R-B)",
    tags=["stream", "fast", "short", "alternating"]
)
# You can confirm by checking if a file like "MyShortFastStream.json" (or similar)
# is created in your templates directory.

# --- 3. Load and Use the Template in an Existing Map ---

# Assume 'target_map_difficulty' is an existing BeatmapFile object you are working on
# (e.g., for an ExpertPlus difficulty).
# It might be loaded like this:
#   info, beatmaps = BeatSaberMapper.load_map_folder("./my_map_project")
#   target_map_difficulty = beatmaps["ExpertPlusStandard.dat"]
#
# For this example, we'll initialize a new BeatmapFile instance to demonstrate the functionality.
target_map_difficulty = BeatmapFile(version="3.3.0")
# Ensure it's sorted if it was empty or newly created
target_map_difficulty.sort_objects()

# Load the template you saved earlier
# - 'loaded_pattern_bm' will be a BeatmapFile containing the notes from the template.
# - 'metadata' will hold the template's name, description, tags, etc.
loaded_pattern_bm, metadata = TemplateManager.load_template(template_name)

# Specify the beat in your 'target_map_difficulty' where the pattern should start
paste_at_beat = 32.0

# Paste the loaded pattern into your target map.
# The notes from 'loaded_pattern_bm' (timed from beat 0 within that template)
# will be offset by 'paste_at_beat' and added to 'target_map_difficulty'.
MapOperations.paste_section(
    target=target_map_difficulty,    # Your main BeatmapFile object to modify
    section=loaded_pattern_bm,       # The BeatmapFile loaded from the template
    target_beat=paste_at_beat        # Beat in 'target' where the pattern begins
)
target_map_difficulty.sort_objects() # Re-sort after adding new objects from the pattern

# Now, 'target_map_difficulty' contains the notes from the pasted pattern.
```

## 7. Best Practices

### Map Organization

1. **Consistent Spacing**: Use consistent spacing between notes for readability
2. **Pattern Recognition**: Create recognizable patterns that flow well
3. **Visual Clarity**: Avoid vision blocks and excessive density
4. **Map Progression**: Gradually increase difficulty throughout the map
5. **Sync to Music**: Ensure notes match the rhythm and energy of the song

### Code Organization

1. **Sort Objects**: Always call `beatmap.sort_objects()` after adding notes
2. **Use Enums**: Use provided enums instead of raw values
3. **Validate Maps**: Run `BeatSaberMapper.validate_map()` to check for issues
4. **Model Validation**: Ensure all objects have required fields properly set
5. **Clear Custom Data**: Use the provided models for custom data

### Performance Optimization

1. **Batch Processing**: Process notes in batches rather than one at a time
2. **Reuse Templates**: Use templates for repeated patterns
3. **Efficient Lighting**: Limit the number of lighting events
4. **Memory Management**: Clear large collections when no longer needed
5. **Object Pooling**: Reuse objects when processing large maps

## 8. Troubleshooting

### Common Errors

1. **AttributeError: 'dict' object has no attribute 'x'**
   - **Cause**: Using a dictionary instead of a proper model object
   - **Solution**: Use the appropriate model class instead of raw dictionaries

2. **TypeError: Object of type x is not JSON serializable**
   - **Cause**: Custom Python objects in customData
   - **Solution**: Ensure all data is JSON serializable

3. **ValueError: field required**
   - **Cause**: Missing required field when creating a model
   - **Solution**: Check model definition to see which fields are required

### Validation Issues

1. **Note Position Outside Grid**
   - **Cause**: Invalid x or y position for notes
   - **Solution**: Ensure x is 0-3 and y is 0-2

2. **Same Hand Double Notes**
   - **Cause**: Multiple notes of the same color at the same time
   - **Solution**: Adjust timing or use different colors

3. **Missing Rotation Events in 360/90 Maps**
   - **Cause**: 360/90 degree map without rotation events
   - **Solution**: Add appropriate rotation events

## 9. Contributing

We welcome contributions to the Beat Saber Mapping Framework! Here's how you can help:

1. **Report Issues**: Submit bug reports and feature requests
2. **Submit Pull Requests**: Contribute code improvements and new features (i work for free, help is greatly appreciated!)
3. **Improve Documentation**: Help clarify and expand the documentation so others can get started easier
4. **Share Templates**: Contribute reusable templates and patterns
5. **Spread the Word**: Tell others about the framework
---

## License

The Beat Saber Mapping Framework (bsmap) is released under the MIT License. See the LICENSE file for details.
