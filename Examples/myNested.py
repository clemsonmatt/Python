from Tkinter import *

class MyApp:
    def __init__(self, parent):

        self.myParent = parent

        ### Our topmost frame is called myContainer1
        self.myContainer1 = Frame(parent) ###
        self.myContainer1.pack()

        ### We will use VERTICAL (top/bottom) orientation inside myContainer1.
        ### Inside myContainer1, first we create buttons_frame.
        ### Then we create top_frame and bottom_frame.
        ### These will be our demonstration frames.

        # top frame
        self.top_frame = Frame(self.myContainer1)
        self.top_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )  ###


        ### Now we will put two more frames, left_frame and right_frame,
        ### inside top_frame.  We will use HORIZONTAL (left/right)
        ### orientation within top_frame.

        # left_frame
        self.left_frame = Frame(self.top_frame, background="red",
            borderwidth=0,  relief=RIDGE,
            height=600,
            width=200,
            ) ###
        self.left_frame.pack(side=LEFT,
            fill=BOTH,
            expand=YES,
            )  ###


        ### right_frame
        self.right_frame = Frame(self.top_frame, background="tan",
            borderwidth=0,  relief=RIDGE,
            width=500,
            )
        self.right_frame.pack(side=RIGHT,
            fill=BOTH,
            expand=YES,
            )  ###


root = Tk()
myapp = MyApp(root)
root.mainloop()
