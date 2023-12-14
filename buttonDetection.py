import cv2
import pyautogui
import time
import numpy as np

class Buttons:
    def __init__(self):
        print("Screen Texts")
        # 1920 1080
        self.mw = 1920
        self.mh = 1080
    
    def getbest(self, contour):
        allx = []
        # ally = []
        for i in contour:
            i=i[0]
            allx.append(i[0])
            # ally.append(i[1])
        po = allx.index(min(allx))
        return contour[po][0]
    
    def find_closed_figures(self, canny_image, min_vertex_count=0, max_vertex=60):
        contours, hierarchy = cv2.findContours(canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        closed_contours = []
        for contour in contours:
            hull = cv2.convexHull(contour)
            is_closed = cv2.arcLength(contour, True) / cv2.arcLength(hull, True) > 0.95
            vertex_count = len(contour)
            if is_closed and vertex_count >= min_vertex_count and vertex_count<max_vertex:
                closed_contours.append(contour)
        return closed_contours
    
    def predict(self, xStart=0, yStart=0, width=400, height=500):
        original = pyautogui.screenshot(region=(xStart, yStart, width, height))
        original = np.array(original)
        bgr_image = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        canny_edges = cv2.Canny(bgr_image, 70, 120)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thick_edges = cv2.dilate(canny_edges, kernel, iterations=4)

        closed_contours = self.find_closed_figures(thick_edges)

        dots_needed = []
        # Draw and display closed figures
        for contour in closed_contours:
            p = self.getbest(contour)
            dots_needed.append(p)
            # cv2.circle(bgr_image, p, 8, (0, 0, 255), -1)
            # cv2.drawContours(bgr_image, [contour], -1, (0, 255, 0), 2)

        # cv2.imshow("wow", bgr_image)
        # cv2.waitKey(0)
        return dots_needed
    
    def predictCenter(self, x, y):
        x = x - (self.mw/2)
        y = y - (self.mh/2)
        return self.predict(x, y, x+self.mw, y+self.mh)
    
# button = Buttons()
# button.predict(0, 0, 300, 300)
# button.predict(0, 0, 1920, 1080)