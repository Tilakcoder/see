from faceDetection import faceMaskDetection
from onScreen import ScreenLabel
# from textDetection import TextfromScreen
from buttonDetection import Buttons
from voiceDetection import SpeechtoText
import time
import cv2
import math
import pyautogui
import threading
import re

def extract_digit_after_a(input_str):
    input_str = input_str.replace(" ", "").replace(",", "").replace("-","")
    pattern = r'a(\d+)'  # 'a' followed by a digit, capturing the digit

    # Use re.search() to find the pattern in the input string
    match = re.search(pattern, input_str)

    # Check if the pattern is found
    if match:
        digit = match.group(1)
        # print(f"Pattern matched in '{input_str}', digit: {digit}")
        return digit
    else:
        # print(f"Pattern not found in '{input_str}'")
        return False

label = ScreenLabel()
face = faceMaskDetection()
button = Buttons()
voice = SpeechtoText()
vid = cv2.VideoCapture(0)
ret, frame = vid.read()
bpoint = {}
refrence = {}
# label.start()
# label.addLabel()

class Cursor:
    def __init__(self):
        print("control Done!")
        self.avgX = []
        self.avgY = []
        self.thresh = 35
    
    def setCenter(self, x, y):
        self.centerX = x
        self.centerY = y
    
    def setTop(self, x, y):
        self.topY = y
    
    def setBottom(self, x, y):
        self.bottomY = y
    
    def setLeft(self, x, y):
        self.leftX = x
    
    def setRight(self, x, y):
        self.rightX = x
    
    def showsets(self):
        print(self.topY, self.centerY, self.bottomY)
        print(self.leftX, self.centerX, self.rightX)
    
    def calculate(self, x, y):
        if len(self.avgX) == 0:
            self.avgX.append(x)
            self.avgX = self.avgX * self.thresh
        else:
            self.avgX.pop(0)
            self.avgX.append(x)
        x = sum(self.avgX)/self.thresh

        if len(self.avgY) == 0:
            self.avgY.append(y)
            self.avgY = self.avgY * self.thresh
        else:
            self.avgY.pop(0)
            self.avgY.append(y)
        y = sum(self.avgY)/self.thresh

        if x>self.centerX:
            px = 0.5-(((x-self.centerX)/(self.leftX-self.centerX))/2)
        else:
            px = (0.5-(((x-self.rightX)/(self.centerX-self.rightX))/2))+0.5
        
        if y<self.centerY:
            py = ((y-self.topY)/(self.centerY-self.topY))/2
        else:
            py = (((y-self.centerY)/(self.bottomY-self.centerY))/2)+0.5
        return px, py

control = Cursor()

def caliEach(w, h):
    label.draw_circle(w, h, 20)
    time.sleep(5)
    ret, frame = vid.read()
    x,y,per = face.detect(frame)
    while len(x)==0:
        ret, frame = vid.read()
        x,y,per = face.detect(frame)
    return x,y

def calibrate():
    w = label.root.winfo_screenwidth()  # WIDTH X
    h = label.root.winfo_screenheight()  # HEIGHT Y
    # print(w, h, "s"*10)
    global control

    # Center of screen
    x, y = caliEach(w // 2, h // 2)
    control.setCenter(math.dist((x[2], y[2]), (x[1], y[1])), math.dist((x[0], y[0]), (x[1], y[1])))
    label.draw_circle(w // 2, h // 2, 20, "black")

    # top
    x, y = caliEach(w // 2, 20)
    control.setTop(math.dist((x[2], y[2]), (x[1], y[1])), math.dist((x[0], y[0]), (x[1], y[1])))
    label.draw_circle(w // 2, 20, 20, "black")

    # bottom
    x, y = caliEach(w // 2, h-20)
    control.setBottom(math.dist((x[2], y[2]), (x[1], y[1])), math.dist((x[0], y[0]), (x[1], y[1])))
    label.draw_circle(w // 2, h-20, 20, "black")

    # left
    x, y = caliEach(20, h//2)
    control.setLeft(math.dist((x[2], y[2]), (x[1], y[1])), math.dist((x[0], y[0]), (x[1], y[1])))
    label.draw_circle(20, h//2, 20, "black")

    # right
    x, y = caliEach(w-20, h//2)
    control.setRight(math.dist((x[2], y[2]), (x[1], y[1])), math.dist((x[0], y[0]), (x[1], y[1])))
    label.draw_circle(w-20, h//2, 20, "black")

    control.showsets()

    label.close()
    label.start()
    label.addCursor()

    # track()
    label.root.after(1000, track)
    label.begin()


def updateLabel():
    global bpoint
    w = label.root.winfo_screenwidth()  # WIDTH X
    h = label.root.winfo_screenheight()  # HEIGHT Y
    label.removeLabel()
    bmark = button.predict(0, 0, w, h)
    r = 1
    for bp in bmark:
        label.addLabel(bp[0]/w, bp[1]/h, str(r))
        bpoint[r] = bp
        r+=1
    # pyautogui.moveTo(size.width * ws, size.height*hs)

def track():
    w = label.root.winfo_screenwidth()  # WIDTH X
    h = label.root.winfo_screenheight()  # HEIGHT Y
    size = pyautogui.size()
    pyautogui.FAILSAFE = False
    while True:
        ret, frame = vid.read()
        x,y,per = face.detect(frame)
        if len(x)>0:
            ws, hs =control.calculate(math.dist((x[2], y[2]), (x[1], y[1])), math.dist((x[0], y[0]), (x[1], y[1])))
            label.updateCursor(ws, hs)
            if per=='right':
                pyautogui.moveTo((ws*w)-1, (hs*h)-1)
                pyautogui.click()

def litsen():
    while True:
        label.curs = "  "
        if voice.getRecord(0.25, trig=True):
            label.curs = " R "
            command = voice.text(voice.audio_from_mic())
            command = command.lower()
            getContext = extract_digit_after_a(command)
            if 'update' in command.lower():
                updateLabel()
            elif 'clear' in command.lower():
                label.removeLabel()
            if getContext != False:
                ps = bpoint[int(getContext)]
                print(label.items[int(getContext)-1])
                label.items[int(getContext)-1].destroy()
                pyautogui.moveTo(ps[0], ps[1])
                pyautogui.click()
            
            if 'type' in command:
                label.curs = " T "
                text = voice.text(voice.audio_from_mic(10))
                pyautogui.typewrite(text)
            elif 'press' in command:
                if 'enter' in command:
                    pyautogui.press('enter')
            print(command)

thread1 = threading.Thread(target=litsen)
thread1.start()

# Run at last
label.calibrateScreen()
label.root.after(1000, calibrate)
label.begin()

thread1.join()
