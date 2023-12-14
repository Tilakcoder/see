from tkinter import *

class ScreenLabel():
    def __init__(self):
        self.root = Tk()
        self.items = []
        self.root.wm_attributes("-topmost", True)
        self.root.attributes('-fullscreen',True)
        self.should_close = False
        self.curs = '  '
    
    def start(self):
        self.root = Tk()
        self.items = []
        self.root.wm_attributes("-topmost", True)
        self.root.attributes('-fullscreen',True)
        self.should_close = False
        # self.root.wm_attributes("-topmost", True)
        # self.root.attributes('-fullscreen',True)
        self.root.wm_attributes('-transparentcolor','#add123')
        self.root.config(bg = '#add123')
        initial_opacity = 0.4
        self.root.attributes("-alpha", initial_opacity)
        # self.root.mainloop()

    def draw_circle(self, x=0.5, y=0.5, radius=20, color="white"):
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=color, width=2)
        self.root.update()
    
    def calibrateScreen(self):
        self.canvas = Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight(), bg='black')
        self.canvas.pack()
        self.canvas.configure(background='black')
    
    def begin(self):
        self.root.after(100, self.check_close)
        self.root.mainloop()

    def check_close(self):
        if self.should_close:
            self.root.attributes("-fullscreen", False)
            self.root.destroy()  # Destroy the window
        else:
            self.root.after(100, self.check_close)  # Continue checking for close request
    
    def close(self):
        self.should_close = True
        self.check_close()

    def addLabel(self, x=0.5, y=0.5, t='1'):
        label = Label(self.root, text=t, font= ('Helvetica 12 bold'), foreground= "red3")
        label.place(relx = x, rely = y)
        self.items.append(label)
    
    def addCursor(self, x=0.5, y=0.5, t='  '):
        t = self.curs
        label = Label(self.root, text=t, font= ('Helvetica 12 bold'), foreground= "red3")
        label.place(relx = x, rely = y)
        self.cursor = label
    
    def updateCursor(self, px, py):
        self.cursor.destroy()
        self.addCursor(px, py)
        self.root.update()

    def removeLabel(self):
        for label in self.items:
            label.destroy()
        self.items.clear()
        self.root.update()

# sl = ScreenLabel()
# sl.close()
# sl.calbrateScreen()
# sl.start()
# sl.addCursor()
# sl.updateCursor(0.9, 0.9)

# sl.addLabel()

# run at last
# sl.begin()