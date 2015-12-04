import turtle
import time

def give_time():
    return [int(i) for i in time.ctime().split()[3].split(':')]

win=turtle.Screen()
#win.bgpic('light.gif')
win.bgcolor('black')
# sq=turtle.Turtle()
# sq.speed(10)
# sq.color('#6FC3DF')
# sq.pensize(7)
turt=turtle.Turtle()
turt.speed(10)
home=(0,0)

#Draw outer square rim
# sq.pu()
# sq.lt(90)
# sq.fd(450)
# sq.lt(90)
# sq.pd()
# sq.fd(550)
# sq.lt(90)
# sq.fd(900)
# sq.lt(90)
# sq.fd(1100)
# sq.lt(90)
# sq.fd(900)
# sq.lt(90)
# sq.fd(550)



#Drawing outer second rim to make space for pins
# sq.color('#6FC3DF')
# sq.fillcolor('black')
# sq.pu()
# sq.lt(90)
# sq.fd(450)
# sq.lt(90)
# sq.pd()
# sq.fd(550)
# sq.lt(90)
# sq.fd(900)
# sq.lt(90)
# sq.fd(1100)
# sq.lt(90)
# sq.fd(900)
# sq.lt(90)
# sq.fd(550)

#Drawing outer second rim to make space for pins
# sq.color('#6FC3DF')
# sq.fillcolor('black')
# sq.pu()
# sq.rt(180)
# sq.setpos((0,-450))
# sq.begin_fill()
# sq.pd()
# sq.circle(450)
# sq.end_fill()
# sq.hideturtle()

#completeing outer and inner dials
turt.pu()
turt.setpos((0,-400))
turt.pd()
turt.begin_fill()
turt.circle(400)
turt.end_fill()
turt.pu()
turt.setpos((0,-25))
turt.pd()
turt.fillcolor('#6FC3DF')
turt.begin_fill()
turt.circle(25)
turt.end_fill()
turt.hideturtle()

def span_pins(no_of_angles,color,pen_size,angle_degree,size,mpin=False):
    for i in range(no_of_angles):
        pin=turtle.Turtle()
        pin.pencolor(color)
        pin.speed(10)
        pin.shape('turtle')
        pin.pu()
        pin.pensize(pen_size)
        pin.hideturtle()
        if mpin:
            if (i*angle_degree)%30==0:
                pass
            else:
                pin.lt(90)
                pin.right(i*angle_degree)
                pin.fd(400)
                pin.pd()
                pin.backward(size)
        else:
            pin.lt(90)
            pin.right(i*angle_degree)
            pin.fd(400)
            pin.pd()
            pin.backward(size)

#Marking Hour_time pins
span_pins(12,'white',5,30,75)

#Marking Minute_time pins
span_pins(72,'hotpink',3,6,15,mpin=True)

#logic for clock rotation

sec_hand=turtle.Turtle(shape='turtle')
min_hand=turtle.Turtle(shape='arrow')
hour_hand=turtle.Turtle(shape='classic')

sec_hand.shapesize(4,4,12)
hour_hand.shapesize(4,4,12)

sec_hand.hideturtle()
min_hand.hideturtle()
hour_hand.hideturtle()

sec_hand.color('gold')
min_hand.color('grey')
hour_hand.color('blue')

sec_hand.speed(10)
min_hand.speed(10)
hour_hand.speed(10)

sec_hand.pensize(10)
min_hand.pensize(10)
hour_hand.pensize(10)

sec_hand.pu()
min_hand.pu()
hour_hand.pu()

while True:
    curr_time=give_time()
    #Get formatted time
    hour=curr_time[0]%12
    minutes=curr_time[1]
    seconds=curr_time[2]
    #For seconds
    sec_hand.setheading(90)
    sec_hand.rt(seconds*6)
    sec_hand.fd(250)
    sec_id=sec_hand.stamp()
    sec_hand.setpos(home)
    sec_hand.setheading(90)
    sec_hand.clearstamp(sec_id)
    #For minutes
    min_hand.setheading(90)
    min_hand.rt(minutes*6)
    min_hand.fd(200)
    min_id=min_hand.stamp()
    min_hand.setpos(home)
    min_hand.setheading(90)
    min_hand.clearstamp(min_id)
    #For Hour
    hour_hand.setheading(90)
    hour_hand.rt(hour*30+minutes*0.5)
    hour_hand.fd(100)
    hour_id=hour_hand.stamp()
    hour_hand.setpos(home)
    hour_hand.setheading(90)
    hour_hand.clearstamp(hour_id)

win.exitonclick()
