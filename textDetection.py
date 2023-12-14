import tensorflow as tf
from imutils.object_detection import non_max_suppression
import numpy as np
import time
import cv2
import pyautogui

class TextfromScreen:
    def __init__(self):
        self.loadModel()
        print("Screen Texts")
        self.mw = 2
        self.mh = 2

    def loadModel(self):
        quantization = "dr" #@param ["dr", "int8", "float16"]
        converter = tf.compat.v1.lite.TFLiteConverter.from_frozen_graph(
            graph_def_file='east/frozen_east_text_detection.pb', 
            input_arrays=['input_images'],
            output_arrays=['feature_fusion/Conv_7/Sigmoid', 'feature_fusion/concat_3'],
            input_shapes={'input_images': [1, 320, 320, 3]}
        )

        converter.optimizations = [tf.lite.Optimize.DEFAULT]

        if quantization=="float16":
            converter.target_spec.supported_types = [tf.float16]
        
        tflite_model = converter.convert()
        open('east/east_model_{}.tflite'.format(quantization), 'wb').write(tflite_model)

        tflite_path=f'east/east_model_{quantization}.tflite'
        self.interpreter = tf.lite.Interpreter(model_path=tflite_path)
        self.input_details = self.interpreter.get_input_details()
    
    def perform_inference(self, preprocessed_image):
        if self.input_details[0]["dtype"]==np.uint8:
            # print("Integer quantization!")
            input_scale, input_zero_point = self.input_details[0]["quantization"]
            preprocessed_image = preprocessed_image / input_scale + input_zero_point
        preprocessed_image = preprocessed_image.astype(self.input_details[0]["dtype"])
        self.interpreter.allocate_tensors()
        self.interpreter.set_tensor(self.input_details[0]['index'], preprocessed_image)
        self.interpreter.invoke()
        # print(f"Inference took: {time.time()-start} seconds")

        scores = self.interpreter.tensor(
            self.interpreter.get_output_details()[0]['index'])()
        geometry = self.interpreter.tensor(
            self.interpreter.get_output_details()[1]['index'])()

        return scores, geometry


    def preprocess_image(self, image):
        # load the input image and grab the image dimensions
        orig = image.copy()
        (H, W) = image.shape[:2]
        
        # set the new width and height and then determine the ratio in change
        # for both the width and height
        (newW, newH) = (320, 320)
        rW = W / float(newW)
        rH = H / float(newH)

        # resize the image and grab the new image dimensions
        image = cv2.resize(image, (newW, newH))
        (H, W) = image.shape[:2]

        # convert the image to a floating point data type and perform mean
        # subtraction
        image = image.astype("float32")
        mean = np.array([123.68, 116.779, 103.939][::-1], dtype="float32")
        image -= mean
        image = np.expand_dims(image, 0)

        return image, orig, rW, rH


    def post_process(self, score, geo, ratioW, ratioH, original):
        (numRows, numCols) = score.shape[2:4]
        rects = []
        confidences = []

        for y in range(0, numRows):
            scoresData = score[0, 0, y]
            xData0 = geo[0, 0, y]
            xData1 = geo[0, 1, y]
            xData2 = geo[0, 2, y]
            xData3 = geo[0, 3, y]
            anglesData = geo[0, 4, y]

            for x in range(0, numCols):
                if scoresData[x] < 0.5:
                    continue

                (offsetX, offsetY) = (x * 4.0, y * 4.0)

                angle = anglesData[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                h = xData0[x] + xData2[x]
                w = xData1[x] + xData3[x]

                endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
                endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
                startX = int(endX - w)
                startY = int(endY - h)

                rects.append((startX, startY, endX, endY))
                confidences.append(scoresData[x])

        boxes = non_max_suppression(np.array(rects), probs=confidences)

        # loop over the bounding boxes
        for (startX, startY, endX, endY) in boxes:
            startX = int(startX * ratioW)
            startY = int(startY * ratioH)
            endX = int(endX * ratioW)
            endY = int(endY * ratioH)

            # draw the bounding box on the image
            cv2.rectangle(original, (startX, startY), (endX, endY), (0, 255, 0), 2)

        # show the output image
        cv2.imshow("Wow", original)
        cv2.waitKey(0)
        # return original
        return boxes

    def predict(self, xStart=0, yStart=0, width=400, height=500):
        original = pyautogui.screenshot(region=(xStart, yStart, width, height))
        original = np.array(original)
        image, orig, rW, rH = self.preprocess_image(original)
        s = time.time()
        scores, geometry = self.perform_inference(preprocessed_image=image)
        e = time.time()
        print(e-s, 'sa')
        scores = np.transpose(scores, (0, 3, 1, 2))
        geometry = np.transpose(geometry, (0, 3, 1, 2))
        boxes = self.post_process(scores, geometry, rW, rH, original)
        return boxes
    
    def predictCenter(self, x, y):
        x = x - (self.mw/2)
        y = y - (self.mh/2)
        return self.predict(x, y, x+self.mw, y+self.mh)

# 1920 1080
# sct = TextfromScreen()
# s = time.time()
# print("SS")
# print(sct.predictCenter(400, 500))
# e = time.time()
# print(e-s)
#print("SS")
#print(sct.predictCenter(400, 500))
