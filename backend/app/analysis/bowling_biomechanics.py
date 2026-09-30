import math
import numpy as np
from typing import Dict, Any, List, Tuple
from backend.app.analysis.biomechanics import BiomechanicsCalculator

class BowlingBiomechanicsCalculator:
    """
    Computes biomechanical metrics for cricket bowling deliveries:
    - Front Knee Brace Angle at Ball Release
    - Bowling Arm Angle at Release & Flexion/Extension Check (ICC 15° rule)
    - Shoulder-Hip Alignment Angle at Back Foot Contact (Action Classification)
    - Mixed Action Injury Risk Indicator (Lumbar spine stress)
    - Trunk Lateral Flexion Angle
    """

    @staticmethod
    def calculate_shoulder_hip_alignment(
        l_shoulder: Dict[str, float],
        r_shoulder: Dict[str, float],
        l_hip: Dict[str, float],
        r_hip: Dict[str, float]
    ) -> float:
        """
        Calculates the alignment divergence angle between the shoulder line and hip line.
        Used to classify Side-on, Front-on, Semi-open, or Mixed bowling actions.
        """
        s_dx = r_shoulder['x'] - l_shoulder['x']
        s_dy = r_shoulder['y'] - l_shoulder['y']
        shoulder_angle = math.degrees(math.atan2(s_dy, s_dx))

        h_dx = r_hip['x'] - l_hip['x']
        h_dy = r_hip['y'] - l_hip['y']
        hip_angle = math.degrees(math.atan2(h_dy, h_dx))

        alignment_diff = abs(shoulder_angle - hip_angle)
        if alignment_diff > 180.0:
            alignment_diff = 360.0 - alignment_diff

        return round(float(alignment_diff), 2)

    @staticmethod
    def classify_bowling_action(alignment_diff: float, shoulder_orientation: float) -> Tuple[str, bool]:
        """
        Classifies bowling action and flags dangerous Mixed Action.
        Mixed action occurs when hips and shoulders have counter-rotational divergence > 35° at back foot contact.
        Returns: (action_name, is_mixed_action_risk)
        """
        is_mixed = False

        if alignment_diff > 35.0:
            action_name = "Mixed Action (High Lumbar Injury Risk)"
            is_mixed = True
        elif abs(shoulder_orientation) < 25.0:
            action_name = "Side-on Bowling Action"
        elif abs(shoulder_orientation) > 65.0:
            action_name = "Front-on Bowling Action"
        else:
            action_name = "Semi-Open Bowling Action"

        return action_name, is_mixed

    @staticmethod
    def compute_bowling_frame_metrics(landmarks: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Calculates instantaneous bowling metrics for a frame.
        """
        if not landmarks or len(landmarks) < 33:
            return {}

        l_shoulder, r_shoulder = landmarks[11], landmarks[12]
        l_elbow, r_elbow = landmarks[13], landmarks[14]
        l_wrist, r_wrist = landmarks[15], landmarks[16]
        l_hip, r_hip = landmarks[23], landmarks[24]
        l_knee, r_knee = landmarks[25], landmarks[26]
        l_ankle, r_ankle = landmarks[27], landmarks[28]

        # Determine dominant bowling arm (assume arm with higher wrist elevation at release)
        if l_wrist['y'] < r_wrist['y']:
            bowling_shoulder, bowling_elbow, bowling_wrist = l_shoulder, l_elbow, l_wrist
            front_hip, front_knee, front_ankle = r_hip, r_knee, r_ankle # Lead landing foot
        else:
            bowling_shoulder, bowling_elbow, bowling_wrist = r_shoulder, r_elbow, r_wrist
            front_hip, front_knee, front_ankle = l_hip, l_knee, l_ankle

        # 1. Front Knee Brace Angle (FKBA)
        front_knee_brace_angle = BiomechanicsCalculator.calculate_angle_3d(front_hip, front_knee, front_ankle)

        # 2. Bowling Arm Elbow Angle (for ICC 15° arm extension compliance check)
        bowling_arm_elbow_angle = BiomechanicsCalculator.calculate_angle_3d(bowling_shoulder, bowling_elbow, bowling_wrist)

        # 3. Shoulder-Hip Divergence Angle
        alignment_diff = BowlingBiomechanicsCalculator.calculate_shoulder_hip_alignment(
            l_shoulder, r_shoulder, l_hip, r_hip
        )

        # 4. Trunk Lateral Flexion (tilt sideways relative to vertical)
        s_mid = {"x": (l_shoulder['x'] + r_shoulder['x'])/2.0, "y": (l_shoulder['y'] + r_shoulder['y'])/2.0}
        h_mid = {"x": (l_hip['x'] + r_hip['x'])/2.0, "y": (l_hip['y'] + r_hip['y'])/2.0}
        
        dx = s_mid['x'] - h_mid['x']
        dy = s_mid['y'] - h_mid['y']
        trunk_lateral_flexion = abs(math.degrees(math.atan2(dx, -dy)))

        return {
            "front_knee_brace_angle": round(front_knee_brace_angle, 2),
            "bowling_elbow_angle": round(bowling_arm_elbow_angle, 2),
            "shoulder_hip_alignment_diff": round(alignment_diff, 2),
            "trunk_lateral_flexion": round(trunk_lateral_flexion, 2),
            "release_wrist_y": round(bowling_wrist['y'], 4)
        }

    @staticmethod
    def compute_bowling_delivery_summary(frame_metrics_list: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Segment delivery stride and compute summary release statistics.
        """
        if not frame_metrics_list:
            return {}

        # Identify release frame (lowest wrist y coordinate / highest elevation in video)
        release_frame = min(frame_metrics_list, key=lambda m: m.get("release_wrist_y", 1.0))

        fkba_at_release = release_frame.get("front_knee_brace_angle", 180.0)
        elbow_at_release = release_frame.get("bowling_elbow_angle", 180.0)
        alignment_diff = release_frame.get("shoulder_hip_alignment_diff", 0.0)
        max_lateral_flexion = max([m.get("trunk_lateral_flexion", 0.0) for m in frame_metrics_list], default=0.0)

        # Action classification
        action_name, is_mixed_risk = BowlingBiomechanicsCalculator.classify_bowling_action(
            alignment_diff=alignment_diff,
            shoulder_orientation=0.0
        )

        # ICC Legality Check (Elbow flex allowance < 15 degrees from straight 180)
        arm_bend_deg = round(abs(180.0 - elbow_at_release), 1)
        icc_compliant = arm_bend_deg <= 15.0

        return {
            "bowling_action": action_name,
            "is_mixed_action_risk": is_mixed_risk,
            "front_knee_brace_angle_release": fkba_at_release,
            "bowling_elbow_angle_release": elbow_at_release,
            "arm_bend_degrees": arm_bend_deg,
            "icc_compliant": icc_compliant,
            "max_trunk_lateral_flexion": round(max_lateral_flexion, 2),
            "shoulder_hip_alignment_diff": alignment_diff
        }
