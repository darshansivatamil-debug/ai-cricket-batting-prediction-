from typing import Dict, Any, List

class BowlingAnalyzer:
    """
    Evaluates cricket bowling mechanics, ICC action legality, kinetic chain bracing, and lumbar spine injury risks.
    """

    @staticmethod
    def analyze_bowling_delivery(summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        observations = []

        action_name = summary.get("bowling_action", "Semi-Open Bowling Action")
        is_mixed = summary.get("is_mixed_action_risk", False)
        fkba = summary.get("front_knee_brace_angle_release", 180.0)
        arm_bend = summary.get("arm_bend_degrees", 0.0)
        icc_ok = summary.get("icc_compliant", True)
        lateral_flexion = summary.get("max_trunk_lateral_flexion", 0.0)

        # 1. Action Classification & Injury Risk Check
        if is_mixed:
            observations.append({
                "category": "Injury Risk & Action Classification",
                "severity": "high",
                "observation": (
                    f"Dangerous Mixed Bowling Action detected (counter-rotation divergence: {summary.get('shoulder_hip_alignment_diff', 0):.1f}°). "
                    "Hips are front-on while shoulders remain side-on at Back-Foot Contact, imposing high twisting shear stress on lumbar spine."
                ),
                "confidence": 0.92,
                "metric_name": "mixed_action_risk",
                "metric_value": summary.get("shoulder_hip_alignment_diff", 0.0)
            })
        else:
            observations.append({
                "category": "Bowling Action Classification",
                "severity": "info",
                "observation": f"Classified as a {action_name}. Shoulder and hip alignment is synchronized during delivery stride.",
                "confidence": 0.89,
                "metric_name": "bowling_action",
                "metric_value": 1.0
            })

        # 2. ICC Legality Check (< 15° arm extension limit)
        if not icc_ok:
            observations.append({
                "category": "Action Legality (ICC Rules)",
                "severity": "high",
                "observation": (
                    f"Bowling arm flexes/extends by {arm_bend:.1f}° during delivery, exceeding the ICC 15° threshold limit. "
                    "Focus on maintaining a straight bowling arm throughout the upper arm arc."
                ),
                "confidence": 0.90,
                "metric_name": "arm_bend_degrees",
                "metric_value": arm_bend
            })
        else:
            observations.append({
                "category": "Action Legality (ICC Rules)",
                "severity": "info",
                "observation": f"Legal bowling action. Bowling arm extension flex ({arm_bend:.1f}°) complies with ICC <15° regulation.",
                "confidence": 0.95,
                "metric_name": "arm_bend_degrees",
                "metric_value": arm_bend
            })

        # 3. Front Knee Bracing (Kinetic Chain Transfer)
        if fkba >= 155.0 and fkba <= 178.0:
            observations.append({
                "category": "Lower Body & Kinetic Chain",
                "severity": "info",
                "observation": f"Excellent front leg bracing at release ({fkba:.1f}°). Stiff front leg acts as a solid lever to maximize ball release velocity.",
                "confidence": 0.88,
                "metric_name": "front_knee_brace_angle_release",
                "metric_value": fkba
            })
        elif fkba < 145.0:
            observations.append({
                "category": "Lower Body & Kinetic Chain",
                "severity": "moderate",
                "observation": f"Front knee collapses ({fkba:.1f}°) during delivery stride. A soft front knee absorbs momentum and reduces pace.",
                "confidence": 0.84,
                "metric_name": "front_knee_brace_angle_release",
                "metric_value": fkba
            })

        # 4. Trunk Lateral Flexion Check
        if lateral_flexion > 35.0:
            observations.append({
                "category": "Spine & Posture",
                "severity": "moderate",
                "observation": f"High lateral trunk flex ({lateral_flexion:.1f}°). Excessive sideways leaning puts added load on side abdominals and lower back.",
                "confidence": 0.82,
                "metric_name": "max_trunk_lateral_flexion",
                "metric_value": lateral_flexion
            })

        return observations
