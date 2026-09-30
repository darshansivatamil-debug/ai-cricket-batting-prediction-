import os
import cv2
import numpy as np
import math

def generate_cricket_sample_video(output_path: str, duration_sec: float = 3.0, fps: int = 30):
    """
    Generates a synthetic 720p cricket video depicting an animated human player executing a Cover Drive shot.
    This enables offline end-to-end testing of MediaPipe pose landmarker and biomechanical extraction.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    width, height = 1280, 720
    total_frames = int(duration_sec * fps)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Base positions for human figure
    center_x = width // 2
    ground_y = height - 120
    hip_y = ground_y - 200

    for frame_idx in range(total_frames):
        t = frame_idx / total_frames # 0.0 to 1.0 animation progress

        # Background pitch & grass
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:ground_y, :] = (45, 30, 20) # Dark navy stadium
        frame[ground_y:, :] = (34, 139, 34) # Green pitch ground

        # Crease line
        cv2.line(frame, (center_x - 150, ground_y), (center_x + 150, ground_y), (255, 255, 255), 3)

        # Animation parameters for Cover Drive:
        # Phase 1: Stance (0 to 0.3)
        # Phase 2: Downswing & Front Knee Stride (0.3 to 0.7)
        # Phase 3: Impact & Follow-through (0.7 to 1.0)
        
        stride_x = 0
        front_knee_bend = 0
        head_shift_x = 0
        bat_angle = -30

        if t < 0.3:
            stride_x = int(50 * (t / 0.3))
        elif t < 0.7:
            p = (t - 0.3) / 0.4
            stride_x = 50 + int(90 * math.sin(p * math.pi / 2))
            front_knee_bend = int(40 * math.sin(p * math.pi))
            head_shift_x = int(35 * p)
            bat_angle = -30 + int(110 * p)
        else:
            p = (t - 0.7) / 0.3
            stride_x = 140
            front_knee_bend = 20
            head_shift_x = 35
            bat_angle = 80 + int(20 * p)

        # Body Keypoints (simulated human player)
        head = (center_x + head_shift_x, hip_y - 140)
        l_shoulder = (center_x + head_shift_x - 30, hip_y - 80)
        r_shoulder = (center_x + head_shift_x + 30, hip_y - 80)

        l_hip = (center_x - 20, hip_y)
        r_hip = (center_x + 20, hip_y)

        # Legs (Back leg stationary, Front leg striding forward)
        back_knee = (l_hip[0] - 20, hip_y + 100)
        back_ankle = (l_hip[0] - 30, ground_y)

        front_knee = (r_hip[0] + stride_x // 2 + 10, hip_y + 100 + front_knee_bend)
        front_ankle = (r_hip[0] + stride_x, ground_y)

        # Arms & Bat
        r_elbow = (r_shoulder[0] + 40, r_shoulder[1] + 40)
        r_wrist = (r_shoulder[0] + 20, r_shoulder[1] + 90)

        l_elbow = (l_shoulder[0] - 30, l_shoulder[1] + 40)
        l_wrist = (l_shoulder[0] + 10, l_shoulder[1] + 90)

        # Draw Player Figure (Light skin/white clothing)
        color_body = (240, 240, 240)
        color_skin = (200, 220, 255)
        color_bat = (30, 100, 180) # Wood brown

        # Head
        cv2.circle(frame, head, 28, color_skin, -1)
        cv2.circle(frame, head, 28, (0, 0, 0), 2)
        # Helmet cap
        cv2.ellipse(frame, head, (28, 20), 0, 180, 360, (120, 50, 20), -1)

        # Torso
        cv2.line(frame, l_shoulder, r_shoulder, color_body, 14)
        cv2.line(frame, ((l_shoulder[0]+r_shoulder[0])//2, l_shoulder[1]), ((l_hip[0]+r_hip[0])//2, hip_y), color_body, 22)
        cv2.line(frame, l_hip, r_hip, color_body, 14)

        # Legs
        cv2.line(frame, l_hip, back_knee, color_body, 12)
        cv2.line(frame, back_knee, back_ankle, color_body, 10)
        cv2.line(frame, r_hip, front_knee, color_body, 12)
        cv2.line(frame, front_knee, front_ankle, color_body, 10)

        # Arms
        cv2.line(frame, r_shoulder, r_elbow, color_skin, 10)
        cv2.line(frame, r_elbow, r_wrist, color_skin, 8)
        cv2.line(frame, l_shoulder, l_elbow, color_skin, 10)
        cv2.line(frame, l_elbow, l_wrist, color_skin, 8)

        # Bat
        bat_length = 110
        rad = math.radians(bat_angle)
        bat_end_x = int(r_wrist[0] + bat_length * math.sin(rad))
        bat_end_y = int(r_wrist[1] + bat_length * math.cos(rad))
        cv2.line(frame, r_wrist, (bat_end_x, bat_end_y), color_bat, 12)

        # HUD Title overlay
        cv2.putText(frame, "Synthetic Cover Drive Shot Sample", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        out.write(frame)

    out.release()
    print(f"Sample video generated successfully at: {output_path}")

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw", "sample_cover_drive.mp4")
    generate_cricket_sample_video(output_file)
