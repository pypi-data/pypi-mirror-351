"""
Beat Saber Mapping Framework - Map Analysis

This module provides utilities for analyzing Beat Saber maps,
calculating statistics, and identifying potential issues.
"""

from typing import Dict, List, Any
import math
from collections import defaultdict

from .models import (
    BeatmapFile
)

class MapAnalysis:
    """Utility class for analyzing Beat Saber maps"""
    
    @staticmethod
    def get_note_statistics(beatmap: BeatmapFile) -> Dict[str, Any]:
        """
        Calculate statistics about notes in a beatmap
        
        Args:
            beatmap: Beatmap to analyze
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            "total_notes": len(beatmap.colorNotes),
            "red_notes": sum(1 for note in beatmap.colorNotes if note.c == 0),
            "blue_notes": sum(1 for note in beatmap.colorNotes if note.c == 1),
            "bombs": len(beatmap.bombNotes),
            "obstacles": len(beatmap.obstacles),
            "sliders": len(beatmap.sliders) + len(beatmap.burstSliders),
            "events": len(beatmap.basicBeatmapEvents),
            "direction_counts": defaultdict(int),
            "position_heatmap": [[0 for _ in range(4)] for _ in range(3)],
        }
        
        # Empty map check
        if not beatmap.colorNotes:
            return stats
        
        # Calculate beat range
        min_beat = min(note.b for note in beatmap.colorNotes)
        max_beat = max(note.b for note in beatmap.colorNotes)
        
        stats["beat_range"] = (min_beat, max_beat)
        stats["duration_beats"] = max_beat - min_beat
        
        # Count note directions
        for note in beatmap.colorNotes:
            stats["direction_counts"][note.d] += 1
            
            # Update position heatmap
            if 0 <= note.x < 4 and 0 <= note.y < 3:
                stats["position_heatmap"][note.y][note.x] += 1
        
        # Calculate note density (notes per beat)
        if stats["duration_beats"] > 0:
            stats["note_density"] = stats["total_notes"] / stats["duration_beats"]
        else:
            stats["note_density"] = 0
        
        # Calculate difficulty factors
        
        # 1. Calculate speed difficulty based on minimum time between consecutive notes
        if len(beatmap.colorNotes) > 1:
            # Sort notes by beat time
            sorted_notes = sorted(beatmap.colorNotes, key=lambda n: n.b)
            
            # Calculate minimum time between consecutive notes
            min_gap = float('inf')
            for i in range(1, len(sorted_notes)):
                gap = sorted_notes[i].b - sorted_notes[i-1].b
                if gap < min_gap:
                    min_gap = gap
            
            stats["min_note_gap"] = min_gap
            
            # Calculate speed difficulty factor (higher value = more difficult)
            if min_gap > 0:
                stats["speed_factor"] = 1.0 / min_gap
            else:
                stats["speed_factor"] = 100  # Very high value for simultaneous notes
        else:
            stats["min_note_gap"] = float('inf')
            stats["speed_factor"] = 0
        
        # 2. Calculate pattern complexity
        
        # Count jumps (two notes at same time)
        jumps = 0
        beat_to_notes = defaultdict(list)
        
        for note in beatmap.colorNotes:
            beat_to_notes[note.b].append(note)
        
        for beat, notes in beat_to_notes.items():
            if len(notes) > 1:
                jumps += 1
        
        stats["jumps"] = jumps
        
        # Calculate jump frequency
        if stats["duration_beats"] > 0:
            stats["jump_frequency"] = jumps / stats["duration_beats"]
        else:
            stats["jump_frequency"] = 0
        
        # Overall estimated difficulty score (simplified)
        stats["estimated_difficulty"] = (
            stats["note_density"] * 0.4 +
            stats["speed_factor"] * 0.3 +
            stats["jump_frequency"] * 0.3
        )
        
        return stats
    
    @staticmethod
    def identify_mapping_issues(beatmap: BeatmapFile) -> List[Dict[str, Any]]:
        """
        Identify potential issues in a beatmap
        
        Args:
            beatmap: Beatmap to analyze
            
        Returns:
            List of issues with description, location, and severity
        """
        issues = []
        
        # Sort notes by beat time
        sorted_notes = sorted(beatmap.colorNotes, key=lambda n: n.b)
        
        # 1. Check for vision blocks (walls directly in front of notes)
        for note in sorted_notes:
            for obstacle in beatmap.obstacles:
                # Check if obstacle is active when note appears
                if obstacle.b <= note.b < obstacle.b + obstacle.d:
                    # Check if obstacle blocks the note
                    if obstacle.x <= note.x < obstacle.x + obstacle.w and obstacle.y <= note.y < obstacle.y + obstacle.h:
                        issues.append({
                            "type": "vision_block",
                            "description": f"Wall blocks note at beat {note.b:.2f}",
                            "beat": note.b,
                            "severity": "high"
                        })
        
        # 2. Check for too fast patterns
        if len(sorted_notes) > 1:
            for i in range(1, len(sorted_notes)):
                gap = sorted_notes[i].b - sorted_notes[i-1].b
                
                # Consider gaps less than 1/16th note as potentially too fast
                if 0 < gap < 0.0625:
                    issues.append({
                        "type": "too_fast",
                        "description": f"Very small gap ({gap:.4f} beats) between notes at beats {sorted_notes[i-1].b:.2f} and {sorted_notes[i].b:.2f}",
                        "beat": sorted_notes[i].b,
                        "severity": "medium"
                    })
        
        # 3. Check for same-hand double notes (same color at exactly same time)
        beat_to_notes = defaultdict(list)
        
        for note in sorted_notes:
            beat_to_notes[note.b].append(note)
        
        for beat, notes in beat_to_notes.items():
            red_count = sum(1 for note in notes if note.c == 0)
            blue_count = sum(1 for note in notes if note.c == 1)
            
            if red_count > 1:
                issues.append({
                    "type": "same_hand_double",
                    "description": f"{red_count} red notes at the same time (beat {beat:.2f})",
                    "beat": beat,
                    "severity": "high"
                })
                
            if blue_count > 1:
                issues.append({
                    "type": "same_hand_double",
                    "description": f"{blue_count} blue notes at the same time (beat {beat:.2f})",
                    "beat": beat,
                    "severity": "high"
                })
        
        # 4. Check for uncomfortable patterns
        for i in range(1, len(sorted_notes) - 1):
            prev_note = sorted_notes[i-1]
            curr_note = sorted_notes[i]
            next_note = sorted_notes[i+1]
            
            # Check for same color notes that require very sharp angle changes
            if prev_note.c == curr_note.c == next_note.c:
                # Simplified angle calculation
                angle1 = math.atan2(curr_note.y - prev_note.y, curr_note.x - prev_note.x)
                angle2 = math.atan2(next_note.y - curr_note.y, next_note.x - curr_note.x)
                angle_diff = abs(angle1 - angle2)
                
                # If angle difference is close to 180 degrees and notes are close in time
                if angle_diff > 2.7 and curr_note.b - prev_note.b < 0.5 and next_note.b - curr_note.b < 0.5:
                    issues.append({
                        "type": "sharp_angle",
                        "description": f"Sharp angle change for {('red' if curr_note.c == 0 else 'blue')} notes at beat {curr_note.b:.2f}",
                        "beat": curr_note.b,
                        "severity": "medium"
                    })
        
        # 5. Check for excessive note density
        window_size = 4.0  # 4 beat window
        max_notes_per_window = 32  # Reasonable maximum for Expert+
        
        for window_start in range(int(sorted_notes[0].b), int(sorted_notes[-1].b) + 1):
            notes_in_window = sum(1 for note in sorted_notes if window_start <= note.b < window_start + window_size)
            
            if notes_in_window > max_notes_per_window:
                issues.append({
                    "type": "high_density",
                    "description": f"High note density ({notes_in_window} notes in {window_size} beats) starting at beat {window_start}",
                    "beat": window_start,
                    "severity": "medium"
                })
        
        # 6. Check for very long walls
        for obstacle in beatmap.obstacles:
            if obstacle.d > 8:  # More than 8 beats is very long
                issues.append({
                    "type": "long_wall",
                    "description": f"Very long wall ({obstacle.d:.2f} beats) at beat {obstacle.b:.2f}",
                    "beat": obstacle.b,
                    "severity": "low"
                })
        
        return issues
    
    @staticmethod
    def compare_maps(map1: BeatmapFile, map2: BeatmapFile) -> Dict[str, Any]:
        """
        Compare two beatmaps and calculate differences
        
        Args:
            map1: First beatmap
            map2: Second beatmap
            
        Returns:
            Dictionary of comparison statistics
        """
        stats1 = MapAnalysis.get_note_statistics(map1)
        stats2 = MapAnalysis.get_note_statistics(map2)
        
        comparison = {
            "note_count_diff": stats2["total_notes"] - stats1["total_notes"],
            "note_count_percent": (stats2["total_notes"] / max(1, stats1["total_notes"]) * 100) - 100,
            "density_diff": stats2["note_density"] - stats1["note_density"],
            "difficulty_diff": stats2["estimated_difficulty"] - stats1["estimated_difficulty"],
        }
        
        # Calculate pattern similarity
        if stats1["total_notes"] > 0 and stats2["total_notes"] > 0:
            # Compare direction distributions
            dir_similarity = 0
            total_dirs = sum(stats1["direction_counts"].values())
            
            for dir_id, count1 in stats1["direction_counts"].items():
                count2 = stats2["direction_counts"].get(dir_id, 0)
                # Calculate weighted similarity for this direction
                if total_dirs > 0:
                    dir_similarity += min(count1, count2) / total_dirs
            
            comparison["direction_similarity"] = dir_similarity * 100
            
            # Compare position distributions
            pos_similarity = 0
            for y in range(3):
                for x in range(4):
                    count1 = stats1["position_heatmap"][y][x]
                    count2 = stats2["position_heatmap"][y][x]
                    pos_similarity += min(count1, count2)
            
            comparison["position_similarity"] = (pos_similarity / max(1, stats1["total_notes"])) * 100
            
            # Overall similarity score
            comparison["overall_similarity"] = (
                comparison["direction_similarity"] * 0.5 +
                comparison["position_similarity"] * 0.5
            )
        else:
            comparison["direction_similarity"] = 0
            comparison["position_similarity"] = 0
            comparison["overall_similarity"] = 0
        
        return comparison