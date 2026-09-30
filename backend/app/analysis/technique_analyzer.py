from typing import Dict, Any, List

class TechniqueAnalyzer:
    """
    Evaluates cricket batting technique based on biomechanical measurements and detected shot type.
    Outputs structured observations with severity and confidence scores.
    """
    
    # Reference ideal ranges for cricket shots (Academic baseline thresholds)
    SHOT_REFERENCE_RANGES = {
        "Forward Defence": {
            "min_front_knee_flex": (110.0, 150.0), # degrees
            "max_head_instability": 3.5,            # instability score threshold
            "trunk_inclination": (5.0, 25.0),       # forward lean
            "front_elbow_angle": (70.0, 130.0)      # high front elbow
        },
        "Cover Drive": {
            "min_front_knee_flex": (100.0, 140.0),
            "max_head_instability": 4.0,
            "trunk_inclination": (10.0, 30.0),
            "front_elbow_angle": (80.0, 145.0)
        },
        "Straight Drive": {
            "min_front_knee_flex": (110.0, 145.0),
            "max_head_instability": 3.8,
            "trunk_inclination": (8.0, 25.0),
            "front_elbow_angle": (85.0, 140.0)
        },
        "Pull Shot": {
            "min_front_knee_flex": (130.0, 175.0), # weight back, flatter knee
            "max_head_instability": 5.0,
            "trunk_inclination": (-10.0, 15.0),     # slightly upright or back
            "front_elbow_angle": (120.0, 175.0)     # full arm extension
        },
        "Cut Shot": {
            "min_front_knee_flex": (120.0, 170.0),
            "max_head_instability": 4.8,
            "trunk_inclination": (0.0, 20.0),
            "front_elbow_angle": (110.0, 170.0)
        }
    }

    @staticmethod
    def analyze_technique(
        shot_type: str,
        metrics_summary: Dict[str, float],
        frame_metrics: List[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """
        Analyzes measured biomechanics against shot reference criteria.
        Returns list of structured technique observations.
        """
        observations = []
        ref = TechniqueAnalyzer.SHOT_REFERENCE_RANGES.get(shot_type, TechniqueAnalyzer.SHOT_REFERENCE_RANGES["Cover Drive"])

        head_instability = metrics_summary.get("head_instability_score", 0.0)
        min_knee_flex = metrics_summary.get("min_knee_flex_angle", 180.0)
        trunk_incl = metrics_summary.get("avg_trunk_inclination", 0.0)
        max_elbow = metrics_summary.get("max_elbow_extension", 180.0)

        # 1. Head Stability Check
        max_allowed_head_instability = ref["max_head_instability"]
        if head_instability > max_allowed_head_instability * 1.5:
            observations.append({
                "category": "Head Position",
                "observation": "Excessive head movement detected during the shot execution.",
                "severity": "high",
                "confidence": 0.88,
                "metric_name": "head_instability_score",
                "metric_value": head_instability
            })
        elif head_instability > max_allowed_head_instability:
            observations.append({
                "category": "Head Position",
                "observation": "Moderate lateral or vertical head displacement observed.",
                "severity": "moderate",
                "confidence": 0.78,
                "metric_name": "head_instability_score",
                "metric_value": head_instability
            })

        # 2. Front Knee Flexion / Stance Check
        knee_min_ref, knee_max_ref = ref["min_front_knee_flex"]
        if min_knee_flex > knee_max_ref + 5.0:
            observations.append({
                "category": "Lower Body Stability",
                "observation": f"Front knee remains excessively stiff ({min_knee_flex:.1f}°). Reduced stride flex toward ball.",
                "severity": "moderate",
                "confidence": 0.82,
                "metric_name": "min_knee_flex_angle",
                "metric_value": min_knee_flex
            })
        elif min_knee_flex < knee_min_ref - 10.0:
            observations.append({
                "category": "Lower Body Stability",
                "observation": f"Deep front knee bend ({min_knee_flex:.1f}°) may cause loss of balance or over-commitment.",
                "severity": "low",
                "confidence": 0.75,
                "metric_name": "min_knee_flex_angle",
                "metric_value": min_knee_flex
            })

        # 3. Trunk Inclination / Body Alignment Check
        trunk_min_ref, trunk_max_ref = ref["trunk_inclination"]
        if trunk_incl < trunk_min_ref:
            observations.append({
                "category": "Trunk & Posture",
                "observation": f"Trunk inclination ({trunk_incl:.1f}°) indicates leaning backward relative to recommended stance.",
                "severity": "moderate",
                "confidence": 0.80,
                "metric_name": "avg_trunk_inclination",
                "metric_value": trunk_incl
            })
        elif trunk_incl > trunk_max_ref + 10.0:
            observations.append({
                "category": "Trunk & Posture",
                "observation": f"High forward trunk lean ({trunk_incl:.1f}°). Risk of falling over the front toe.",
                "severity": "moderate",
                "confidence": 0.79,
                "metric_name": "avg_trunk_inclination",
                "metric_value": trunk_incl
            })

        # 4. Upper Body / Arm Follow-Through Check
        if shot_type in ["Cover Drive", "Straight Drive", "Forward Defence"]:
            elbow_min, elbow_max = ref["front_elbow_angle"]
            if max_elbow < 90.0:
                observations.append({
                    "category": "Upper Body & Arm Extension",
                    "observation": f"Restricted front elbow extension ({max_elbow:.1f}°). High front elbow control could be improved.",
                    "severity": "low",
                    "confidence": 0.74,
                    "metric_name": "max_elbow_extension",
                    "metric_value": max_elbow
                })

        if not observations:
            observations.append({
                "category": "Overall Technique",
                "observation": "Good mechanical alignment. Key joint angles match target reference ranges.",
                "severity": "info",
                "confidence": 0.90,
                "metric_name": "overall_alignment",
                "metric_value": 1.0
            })

        return observations
