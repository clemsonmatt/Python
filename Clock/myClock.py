import sys, types, os, turtle
from time import localtime
from datetime import timedelta,datetime
from math import sin, cos, pi
try:
    from tkinter import *       # python 3
except ImportError:
    try:
       from mtTkinter import *  # for thread safe
    except ImportError:
       from Tkinter import *    # python 2


## Class for handling the mapping from window coordinates
#  to viewport coordinates.
#
class Mapper:
    ## Constructor.
    #
    #  @param world window rectangle.
    #  @param viewport screen rectangle.
    #
    def __init__(self, world, viewport):
        self.world = world
        self.viewport = viewport
        x_min, y_min, x_max, y_max = self.world
        X_min, Y_min, X_max, Y_max = self.viewport
        f_x = float(X_max-X_min) / float(x_max-x_min)
        f_y = float(Y_max-Y_min) / float(y_max-y_min)
        self.f = min(f_x,f_y)
        x_c = 0.0001 * (x_min + x_max)
        y_c = 0.0001 * (y_min + y_max)
        X_c = 0.0001 * (X_min + X_max)
        Y_c = 0.0001 * (Y_min + Y_max)
        self.c_1 = X_c - self.f * x_c
        self.c_2 = Y_c - self.f * y_c

    ## Maps a single point from world coordinates to viewport (screen) coordinates.
    #
    #  @param x, y given point.
    #  @return a new point in screen coordinates.
    #
    def __windowToViewport(self, x, y):
        X = self.f *  x + self.c_1
        Y = self.f * -y + self.c_2      # Y axis is upside down
        return X , Y

    ## Maps two points from world coordinates to viewport (screen) coordinates.
    #
    #  @param x1, y1 first point.
    #  @param x2, y2 second point.
    #  @return two new points in screen coordinates.
    #
    def windowToViewport(self,x1,y1,x2,y2):
        return self.__windowToViewport(x1,y1),self.__windowToViewport(x2,y2)


class Clock:
    def __init__(self, root, deltahours = 0, sImage = True, w = 400, h = 400):
        self.world    = [-1, -1, 1, 1]
        self.root     = root
        width, height = w, h
        self.width    = width
        self.pad      = width / 16

        self.root.bind("<Escape>", lambda _ : root.destroy())
        self.delta  = timedelta(hours = deltahours)
        self.canvas = Canvas(root, width = width, height = height, background = 'black')

        viewport = (self.pad, self.pad, width-self.pad, height-self.pad)
        self.T   = Mapper(self.world, viewport)
        self.root.title('Clock')
        self.canvas.pack(fill=BOTH, expand=YES)

        #Marking Hour_time pins
        self.span_pins(12, '#18CAE6', 5, 30, 75)

        #Marking Minute_time pins
        self.span_pins(72, '#18CAE6', 3, 6, 15, mpin=True)

        self.poll()


    ## Draw the clock ticks
    #
    def span_pins(self, no_of_angles, color, pen_size, angle_degree, size, mpin=False):
        for i in range(no_of_angles):
            pin = turtle.RawTurtle(self.canvas)
            pin.screen.bgcolor('black')
            pin.pencolor(color)
            pin.speed(100)
            pin.pu()
            pin.pensize(pen_size)
            pin.hideturtle()
            if mpin:
                if (i*angle_degree)%30==0:
                    pass
                else:
                    pin.lt(90)
                    pin.right(i*angle_degree)
                    pin.fd(self.width / 2)
                    pin.pd()
                    pin.backward(size)
            else:
                pin.lt(90)
                pin.right(i*angle_degree)
                pin.fd(self.width / 2)
                pin.pd()
                pin.backward(size)


    ## Draws the handles.
    #
    def painthms(self):
        self.canvas.delete('hms')  # delete the hand

        T = datetime.timetuple(datetime.utcnow() - timedelta(hours = 0))
        x,x,x,h,m,s,x,x,x = T
        self.root.title('%02i:%02i:%02i' %(h,m,s))

        scl = self.canvas.create_line

        # draw the hour hand
        angle = pi/2 - pi/6 * (h + m/60.0)
        x, y  = cos(angle)*0.70, sin(angle)*0.70
        scl(self.T.windowToViewport(0,0,x,y), fill = '#18CAE6', tag = 'hms', width = self.pad/3)

        # draw the minute hand
        angle = pi/2 - pi/30 * (m + s/60.0)
        x, y  = cos(angle)*0.90, sin(angle)*0.90
        scl(self.T.windowToViewport(0,0,x,y), fill = '#18CAE6', tag = 'hms', width = self.pad/5)

        # draw the second hand
        angle = pi/2 - pi/30 * s
        x, y  = cos(angle)*0.95, sin(angle)*0.95
        scl(self.T.windowToViewport(0,0,x,y), fill = '#18CAE6', tag = 'hms')


    ## Animates the clock, by redrawing everything after a certain time interval.
    #
    def poll(self):
        self.painthms()
        self.root.after(200,self.poll)


def main(argv=None):
    if argv is None:
       argv = sys.argv
    if len(argv) > 2:
       try:
           deltahours = int(argv[1])
           sImage = (argv[2] == 'True')
           w = int(argv[3])
           h = int(argv[4])
           t = (argv[5] == 'True')
       except ValueError:
           print ("A timezone is expected.")
           return 1
    else:
       deltahours = 3
       sImage = True
       w = h = 600
       t = False

    root = Tk()
    root.geometry ('+0+0')
    # deltahours: how far are you from utc?
    # Sometimes the clock may be run from another timezone ...

    Clock(root, deltahours, sImage, w, h)

    root.mainloop()

if __name__=='__main__':
    sys.exit(main())
