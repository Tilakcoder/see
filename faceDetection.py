from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import math


class faceMaskDetection:
  def __init__(self):
    base_options = python.BaseOptions(model_asset_path='face_landmarker.task')
    options = vision.FaceLandmarkerOptions(base_options=base_options,
                                          output_face_blendshapes=True,
                                          output_facial_transformation_matrixes=True,
                                          num_faces=1)
    self.detector = vision.FaceLandmarker.create_from_options(options)
    self.blinkThresh = 0.018
    print("ALL set")
  
  def draw_iris(self, rgb_image, detection_result):
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)

    s = annotated_image.shape

    x = []
    y = []
    per = 'nope'

    if len(face_landmarks_list) > 0:
        head = face_landmarks_list[0][168:169]
        right_eye_c = face_landmarks_list[0][133:134]
        right_eye_uplid = face_landmarks_list[0][145]
        right_eye_downlid = face_landmarks_list[0][159]
        right_eye_ball = face_landmarks_list[0][468:469]

        left_eye_c = face_landmarks_list[0][362:363]
        left_eye_uplid = face_landmarks_list[0][386]
        left_eye_downlid = face_landmarks_list[0][374]
        left_eye_ball = face_landmarks_list[0][151:152]

        nose_center = face_landmarks_list[0][1:2]
        nose_top = face_landmarks_list[0][168:169]

        reye = math.dist((right_eye_uplid.x, right_eye_uplid.y), (right_eye_downlid.x, right_eye_downlid.y))
        leye = math.dist((left_eye_uplid.x, left_eye_uplid.y), (left_eye_downlid.x, left_eye_downlid.y))

        # print(reye, leye)
        reye = reye<self.blinkThresh
        leye = leye<self.blinkThresh
 
        per = 'nope'
        
        if reye and leye:
          per = "both"
        else:
          if reye:
            per = "right"
          elif leye:
            per = "left"

        ir = nose_center
        ir.extend(head)
        ir.extend(right_eye_c)
        ir.extend(left_eye_c)
        for ri in ir:
            x.append(ri.x)
            y.append(ri.y)
            # annotated_image = cv2.circle(annotated_image, (int(ri.x * s[1]), int(ri.y * s[0])), 5, (0, 0, 255), cv2.FILLED)


    return x, y, per
    # return annotated_image
  

    # face_landmarks_list = detection_result.face_landmarks
    # annotated_image = np.copy(rgb_image)

    # # Loop through the detected faces to visualize.
    # for idx in range(len(face_landmarks_list)):
    #   face_landmarks = face_landmarks_list[idx]
    #   iris_landmarks = face_landmarks.landmark[468:478]

    # return annotated_image

  def draw_landmarks_on_image(self, rgb_image, detection_result):
    face_landmarks_list = detection_result.face_landmarks
    annotated_image = np.copy(rgb_image)

    # Loop through the detected faces to visualize.
    for idx in range(len(face_landmarks_list)):
      face_landmarks = face_landmarks_list[idx]

      # Draw the face landmarks.
      face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
      face_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks
      ])

      solutions.drawing_utils.draw_landmarks(
          image=annotated_image,
          landmark_list=face_landmarks_proto,
          connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
          landmark_drawing_spec=None,
          connection_drawing_spec=mp.solutions.drawing_styles
          .get_default_face_mesh_tesselation_style())

      solutions.drawing_utils.draw_landmarks(
          image=annotated_image,
          landmark_list=face_landmarks_proto,
          connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,
          landmark_drawing_spec=None,
          connection_drawing_spec=mp.solutions.drawing_styles
          .get_default_face_mesh_contours_style())
      solutions.drawing_utils.draw_landmarks(
          image=annotated_image,
          landmark_list=face_landmarks_proto,
          connections=mp.solutions.face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles
            .get_default_face_mesh_iris_connections_style())

    return annotated_image

  
    # Extract the face blendshapes category names and scores.
    face_blendshapes_names = [face_blendshapes_category.category_name for face_blendshapes_category in face_blendshapes]
    face_blendshapes_scores = [face_blendshapes_category.score for face_blendshapes_category in face_blendshapes]
    # The blendshapes are ordered in decreasing score value.
    face_blendshapes_ranks = range(len(face_blendshapes_names))

    fig, ax = plt.subplots(figsize=(12, 12))
    bar = ax.barh(face_blendshapes_ranks, face_blendshapes_scores, label=[str(x) for x in face_blendshapes_ranks])
    ax.set_yticks(face_blendshapes_ranks, face_blendshapes_names)
    ax.invert_yaxis()

    # Label each bar with values
    for score, patch in zip(face_blendshapes_scores, bar.patches):
      plt.text(patch.get_x() + patch.get_width(), patch.get_y(), f"{score:.4f}", va="top")

    ax.set_xlabel('Score')
    ax.set_title("Face Blendshapes")
    plt.tight_layout()
    plt.show()
  
  def detect(self, frame):
    f = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    detection_result = self.detector.detect(f)
    x, y, per = self.draw_iris(frame, detection_result)
    # annotated_image = self.draw_iris(frame, detection_result)
    # annotated_image = self.draw_landmarks_on_image(f.numpy_view(), detection_result)
    return x, y, per
    # return annotated_image

# vid = cv2.VideoCapture(0)
# det = faceMaskDetection()

# while(True):
#   ret, frame = vid.read()

#   annotated_image = det.detect(frame)
#   cv2.imshow('frame', annotated_image)
#   # break

#   if cv2.waitKey(1) & 0xFF == ord('q'):
#     break

# vid.release()
