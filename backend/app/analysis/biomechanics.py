import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import math

class BiomechanicsCalculator:
    @staticmethod
    def calculate_angle_3d(pointA: Dict[str, float], pointB: Dict[str, float], pointC: Dict[str, float]) -> float:
        """
        Calculates the angle (in degrees) formed at vertex B by points A, B, and C in 3D/2D space.
        Uses mathematically exact vector formula:
        angle = arccos( ((A-B) . (C-B)) / (|A-B| * |C-B|) )
        Applies safe numerical clamping to prevent domain error in arccos.
        """
        # Vector BA = A - B
        ba = np.array([pointA['x'] - pointB['x'], pointA['y'] - pointB['y'], pointA.get('z', 0.0) - pointB.get('z', 0.0)])
        # Vector BC = C - B
        bc = np.array([pointC['x'] - pointB['x'], pointC['y'] - pointB['y'], pointC.get('z', 0.0) - pointB.get('z', 0.0)])

        norm_ba = np.linalg.norm(ba)
        norm_bc = np.linalg.norm(bc)

        if norm_ba < 1e-7 or norm_bc < 1e-7:
            return 0.0

        # Dot product
        cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
        # Safe numerical clamping to [-1.0, 1.0]
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

        angle_rad = np.arccos(cosine_angle)
        return float(np.degrees(angle_rad))

    @staticmethod
    def calculate_trunk_inclination(shoulder_mid: Dict[str, float], hip_mid: Dict[str, float]) -> float:
        """
        Calculates trunk inclination angle (in degrees) relative to vertical axis (0 deg = perfectly upright).
        """
        dx = shoulder_mid['x'] - hip_mid['x']
        dy = shoulder_mid['y'] - hip_mid['y'] # Note: image y goes downwards

        # Vector from hip to shoulder: (-dx, -dy) in standard Cartesian
        # Angle with vertical axis (0, -1)
        length = math.sqrt(dx*dx + dy*dy)
        if length < 1e-7:
            return 0.0

        # Cosine with vertical vector (0, -1)
        cos_angle = -dy / length
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle_deg = math.degrees(math.acos(cos_angle))
        
        # Determine direction of tilt (+ = forward, - = backward)
        if dx > 0:
            return float(angle_deg)
        else:
            return float(-angle_deg)

    @staticmethod
    def compute_frame_biomechanics(landmarks: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Extracts all instantaneous joint angles & biomechanical metrics for a single frame.
        """
        if not landmarks or len(landmarks) < 33:
            return {}

        # Key Landmarks
        nose = landmarks[0]
        l_shoulder, r_shoulder = landmarks[11], landmarks[12]
        l_elbow, r_elbow = landmarks[13], landmarks[14]
        l_wrist, r_wrist = landmarks[15], landmarks[16]
        l_hip, r_hip = landmarks[23], landmarks[24]
        l_knee, r_knee = landmarks[25], landmarks[26]
        l_ankle, r_ankle = landmarks[27], landmarks[28]

        # Calculate joint angles
        left_knee_angle = BiomechanicsCalculator.calculate_angle_3d(l_hip, l_knee, l_ankle)
        right_knee_angle = BiomechanicsCalculator.calculate_angle_3d(r_hip, r_knee, r_ankle)
        
        left_elbow_angle = BiomechanicsCalculator.calculate_angle_3d(l_shoulder, l_elbow, l_wrist)
        right_elbow_angle = BiomechanicsCalculator.calculate_angle_3d(r_shoulder, r_elbow, r_wrist)

        left_hip_angle = BiomechanicsCalculator.calculate_angle_3d(l_shoulder, l_hip, l_knee)
        right_hip_angle = BiomechanicsCalculator.calculate_angle_3d(r_shoulder, r_hip, r_knee)

        # Midpoints for trunk and shoulders
        shoulder_mid = {"x": (l_shoulder['x'] + r_shoulder['x']) / 2.0, "y": (l_shoulder['y'] + r_shoulder['y']) / 2.0}
        hip_mid = {"x": (l_hip['x'] + r_hip['x']) / 2.0, "y": (l_hip['y'] + r_hip['y']) / 2.0}

        trunk_inclination = BiomechanicsCalculator.calculate_trunk_inclination(shoulder_mid, hip_mid)

        # Stance width (distance between ankles normalized by hip width)
        hip_width = math.sqrt((l_hip['x'] - r_hip['x'])**2 + (l_hip['y'] - r_hip['y'])**2)
        ankle_dist = math.sqrt((l_ankle['x'] - r_ankle['x'])**2 + (l_ankle['y'] - r_ankle['y'])**2)
        stance_width_ratio = (ankle_dist / hip_width) if hip_width > 1e-5 else 1.0

        # Shoulder alignment angle relative to horizontal
        s_dx = r_shoulder['x'] - l_shoulder['x']
        s_dy = r_shoulder['y'] - l_shoulder['y']
        shoulder_orientation = math.degrees(math.atan2(s_dy, s_dx))

        return {
            "left_knee_angle": round(left_knee_angle, 2),
            "right_knee_angle": round(right_knee_angle, 2),
            "left_elbow_angle": round(left_elbow_angle, 2),
            "right_elbow_angle": round(right_elbow_angle, 2),
            "left_hip_angle": round(left_hip_angle, 2),
            "right_hip_angle": round(right_hip_angle, 2),
            "trunk_inclination": round(trunk_inclination, 2),
            "stance_width_ratio": round(stance_width_ratio, 2),
            "shoulder_orientation": round(shoulder_orientation, 2),
            "head_x": round(nose['x'], 4),
            "head_y": round(nose['y'], 4),
            "com_x": round(hip_mid['x'], 4),
            "com_y": round(hip_mid['y'], 4)
        }

    @staticmethod
    def compute_temporal_summary(frame_metrics_list: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Computes aggregate metrics across time: head displacement standard deviation, min knee flex, max elbow extension, etc.
        """
        if not frame_metrics_list:
            return {}

        head_xs = [m["head_x"] for m in frame_metrics_list if "head_x" in m]
        head_ys = [m["head_y"] for m in frame_metrics_list if "head_y" in m]
        
        l_knees = [m["left_knee_angle"] for m in frame_metrics_list if "left_knee_angle" in m]
        r_knees = [m["right_knee_angle"] for m in frame_metrics_list if "right_knee_angle" in m]

        l_elbows = [m["left_elbow_angle"] for m in frame_metrics_list if "left_elbow_angle" in m]
        r_elbows = [m["right_elbow_angle"] for m in frame_metrics_list if "right_elbow_angle" in m]

        trunks = [m["trunk_inclination"] for m in frame_metrics_list if "trunk_inclination" in m]

        # Standard deviation of head position (head stability indicator)
        head_disp_x = float(np.std(head_xs)) if head_xs else 0.0
        head_disp_y = float(np.std(head_ys)) if head_ys else 0.0
        head_instability_score = round(math.sqrt(head_disp_x**2 + head_disp_y**2) * 100.0, 2)

        # Min knee angle (peak flex at front foot plant)
        min_front_knee = round(float(min(min(l_knees, default=180.0), min(r_knees, default=180.0))), 2)
        avg_trunk_inclination = round(float(np.mean(trunks)), 2) if trunks else 0.0

        max_elbow_angle = round(float(max(max(l_elbows, default=0.0), max(r_elbows, default=0.0))), 2)

        return {
            "head_instability_score": head_instability_score,
            "min_knee_flex_angle": min_front_knee,
            "avg_trunk_inclination": avg_trunk_inclination,
            "max_elbow_extension": max_elbow_angle
        }
