import os
import cv2
import numpy as np
import mediapipe as mp
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

def extract_static_pose(
    image_url_path: str,
    min_detection_confidence: float,
    min_tracking_confidence: float,
    model_complexity: int,
) -> tuple[list[mp.solutions.pose.PoseLandmark], np.ndarray]:
  mp_pose = mp.solutions.pose

  try:
    with mp_pose.Pose(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence, model_complexity=model_complexity) as pose:
      image = cv2.imread(image_url_path)
      rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      results = pose.process(rgb_image)
      landmarks = results.pose_landmarks.landmark
      annotated_image = annotate_pose(landmarks, rgb_image)

  except FileNotFoundError as e:
    logger.error("Error: %s", e)
    return False
  except Exception as e:
    logger.error("Unexpected error: %s", e)
    return False

  if not landmarks:
    return False
  
  return landmarks, annotated_image

def annotate_pose(landmarks: list[mp.solutions.pose.PoseLandmark], rgb_image: np.ndarray) -> np.ndarray:
    annotated_image = rgb_image.copy()
    i = 0
    for landmark in landmarks:
        # Convert landmark coordinates to pixel values
        landmark_px = (int(landmark.x * rgb_image.shape[1]), int(landmark.y * rgb_image.shape[0]))
        
        if i < 11:
            # marks red for head
            cv2.circle(annotated_image, landmark_px, 5, (0, 0, 255), -1)
        elif 10 < i < 23:
            # marks green for mid body
            cv2.circle(annotated_image, landmark_px, 5, (0, 255, 0), -1)
        elif 22 < i < 29:
            # marks blue for lower body
            cv2.circle(annotated_image, landmark_px, 5, (255, 0, 0), -1)
        elif 28 < i < 33:
            # marks magenta for feet
            cv2.circle(annotated_image, landmark_px, 5, (255, 0, 255), -1)
        i += 1
    return annotated_image

def download_landmarks_csv(landmarks: list[mp.solutions.pose.PoseLandmark], image_url_path: str, output_dir: str) -> bool:
  try:
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_url_path))[0]}.csv")

    with open(output_path, "w") as f:
      f.write("x,y,z,v\n")
      for landmark in landmarks:
        f.write(f"{landmark.x},{landmark.y},{landmark.z},{landmark.visibility}\n")
  except Exception as e:
    logger.error("Unexpected error: %s", e)
    return False
  return True

def download_landmarks_png(annotated_image: np.ndarray, image_url_path: str, output_dir: str) -> bool:
  try:
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_url_path))[0]}.png")
    cv2.imwrite(output_path, annotated_image)
  except Exception as e:
    logger.error("Unexpected error: %s", e)
    return False
  return True
