import cv2
import numpy as np
from typing import Dict, Any, List, Optional

# Standard MediaPipe 33-landmark pose connections
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)
]

class OverlayRenderer:
    def __init__(self):
        pass

    def draw_pose_overlay(
        self,
        frame_bgr: np.ndarray,
        pose_data: Optional[Dict[str, Any]],
        shot_name: str = "Analyzing...",
        confidence: float = 0.0,
        key_angles: Optional[Dict[str, float]] = None,
        frame_number: int = 0
    ) -> np.ndarray:
        """
        Draws biomechanical overlay: skeleton, joint angles, head box, center of mass, HUD panel.
        """
        output = frame_bgr.copy()
        h, w, c = output.shape

        if pose_data and "landmarks_pixel" in pose_data:
            landmarks_pixel = pose_data["landmarks_pixel"]

            # Draw skeleton connections
            for start_idx, end_idx in POSE_CONNECTIONS:
                if start_idx < len(landmarks_pixel) and end_idx < len(landmarks_pixel):
                    pt1 = (landmarks_pixel[start_idx]["x"], landmarks_pixel[start_idx]["y"])
                    pt2 = (landmarks_pixel[end_idx]["x"], landmarks_pixel[end_idx]["y"])
                    cv2.line(output, pt1, pt2, (0, 255, 0), 2)

            # Draw landmark joints
            for lm in landmarks_pixel:
                cv2.circle(output, (lm["x"], lm["y"]), 4, (0, 255, 255), -1)

            # 1. Draw Head Bounding & Stability Box
            nose = landmarks_pixel[0]
            if nose["visibility"] > 0.4:
                box_size = int(h * 0.08)
                cv2.rectangle(
                    output,
                    (max(0, nose["x"] - box_size), max(0, nose["y"] - box_size)),
                    (min(w, nose["x"] + box_size), min(h, nose["y"] + box_size)),
                    (0, 255, 255), 2
                )
                cv2.putText(
                    output, "Head Stability",
                    (max(0, nose["x"] - box_size), max(0, nose["y"] - box_size - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1
                )

            # 2. Draw Center of Mass (CoM approximation from hips)
            left_hip = landmarks_pixel[23]
            right_hip = landmarks_pixel[24]
            if left_hip["visibility"] > 0.4 and right_hip["visibility"] > 0.4:
                com_x = int((left_hip["x"] + right_hip["x"]) / 2)
                com_y = int((left_hip["y"] + right_hip["y"]) / 2)
                cv2.circle(output, (com_x, com_y), 8, (0, 0, 255), -1)
                cv2.circle(output, (com_x, com_y), 12, (255, 255, 255), 2)
                cv2.putText(output, "CoM", (com_x + 14, com_y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # 3. Draw key angle callouts if provided
            if key_angles:
                fk_angle = key_angles.get("front_knee_angle")
                if fk_angle is not None:
                    knee_pt = landmarks_pixel[25] if landmarks_pixel[25]["visibility"] > landmarks_pixel[26]["visibility"] else landmarks_pixel[26]
                    cv2.putText(
                        output, f"Knee: {fk_angle:.1f}deg",
                        (knee_pt["x"] + 10, knee_pt["y"]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
                    )

                fe_angle = key_angles.get("front_elbow_angle")
                if fe_angle is not None:
                    elbow_pt = landmarks_pixel[13] if landmarks_pixel[13]["visibility"] > landmarks_pixel[14]["visibility"] else landmarks_pixel[14]
                    cv2.putText(
                        output, f"Elbow: {fe_angle:.1f}deg",
                        (elbow_pt["x"] + 10, elbow_pt["y"]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 2
                    )

        # 4. HUD Banner at Top
        overlay_banner = output.copy()
        cv2.rectangle(overlay_banner, (0, 0), (w, 65), (20, 24, 33), -1)
        output = cv2.addWeighted(overlay_banner, 0.85, output, 0.15, 0)

        # Shot Badge
        cv2.putText(output, "AI VIRTUAL CRICKET COACH", (15, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        conf_str = f"{confidence * 100:.1f}%" if confidence > 0 else "N/A"
        color = (0, 255, 0) if confidence >= 0.5 else (0, 165, 255)
        cv2.putText(output, f"Shot: {shot_name} (Conf: {conf_str})", (15, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        # Frame counter badge
        cv2.putText(output, f"Frame: {frame_number}", (w - 130, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        return output
