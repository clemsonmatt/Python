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

try:
    # Python 3 imports
    from urllib.request import urlopen
    from urllib.parse import quote
    from urllib.parse import urlencode
    from urllib.error import URLError
    # needed for code to work on Python3
    xrange = range
    unicode = str
except ImportError:
    # Python 2 imports
    from urllib2 import urlopen
    from urllib import quote
    from urllib import urlencode
    from urllib2 import URLError
import re
import operator
from math import pow
from xml.dom import minidom
import json

try:
    from unidecode import unidecode
except ImportError:
    pass

import HTMLParser


WEATHER_COM_URL = 'http://wxdata.weather.com/wxdata/weather/local/%s?' + \
                       'unit=%s&dayf=5&cc=*'

DEGREE_SIGN = u'\N{DEGREE SIGN}'


##
 # Weather
 #
class Weather:
    dayInfo = [None] * 5

    class __Weather:
        def __init__(self, root, rightFrame, width, height):
            self.root   = root
            self.canvas = Canvas(rightFrame, width = width, height = height)
            self.canvas.pack(fill=BOTH, expand=YES)

            for i in range(5):
                Weather.dayInfo[i] = Text(self.canvas,
                    width               = 50,
                    height              = 1,
                    background          = '#050D10',
                    borderwidth         = 1,
                    highlightbackground = "#06CFEF")

                Weather.dayInfo[i].pack(side=TOP,
                    fill=BOTH,
                    expand=YES,
                    )  ###


    def __init__(self, root, rightFrame, width, height):
        if not Weather.dayInfo[0]:
            Weather.__Weather(root, rightFrame, width, height)
        else:
            self.deleteCurrent()

        self.printWeather()


    def get_weather_from_weather_com(self, location_id, units = 'imperial'):
        """Fetches weather report from Weather.com

        Parameters:
          location_id: A five digit US zip code or location ID. To find your
          location ID, use function get_loc_id_from_weather_com().

          units: type of units. 'metric' for metric and 'imperial' for non-metric.
          Note that choosing metric units changes all the weather units to metric.
          For example, wind speed will be reported as kilometers per hour and
          barometric pressure as millibars.

        Returns:
          weather_data: a dictionary of weather data that exists in XML feed.

        """
        location_id = quote(location_id)
        if units == 'metric':
            unit = 'm'
        elif units == 'imperial' or units == '':    # for backwards compatibility
            unit = ''
        else:
            unit = 'm'      # fallback to metric
        url = WEATHER_COM_URL % (location_id, unit)
        try:
            handler = urlopen(url)
        except URLError:
            return {'error': 'Could not connect to Weather.com'}
        if sys.version > '3':
            # Python 3
            content_type = dict(handler.getheaders())['Content-Type']
        else:
            # Python 2
            content_type = handler.info().dict['content-type']
        try:
            charset = re.search('charset\=(.*)', content_type).group(1)
        except AttributeError:
            charset = 'utf-8'
        if charset.lower() != 'utf-8':
            xml_response = handler.read().decode(charset).encode('utf-8')
        else:
            xml_response = handler.read()
        dom = minidom.parseString(xml_response)
        handler.close()

        try:
            weather_dom = dom.getElementsByTagName('weather')[0]
        except IndexError:
            error_data = {'error': dom.getElementsByTagName('error')[
                0].getElementsByTagName('err')[0].firstChild.data}
            dom.unlink()
            return error_data

        key_map = {'head':'units', 'ut':'temperature', 'ud':'distance',
                   'us':'speed', 'up':'pressure', 'ur':'rainfall',
                   'loc':'location', 'dnam':'name', 'lat':'lat', 'lon':'lon',
                   'cc':'current_conditions', 'lsup':'last_updated',
                   'obst':'station', 'tmp':'temperature',
                   'flik':'feels_like', 't':'text', 'icon':'icon',
                   'bar':'barometer', 'r':'reading', 'd':'direction',
                   'wind':'wind', 's':'speed', 'gust':'gust', 'hmid':'humidity',
                   'vis':'visibility', 'uv':'uv', 'i':'index', 'dewp':'dewpoint',
                   'moon':'moon_phase', 'hi':'high', 'low':'low', 'sunr':'sunrise',
                   'suns':'sunset', 'bt':'brief_text', 'ppcp':'chance_precip'}

        data_structure = {'head': ('ut', 'ud', 'us', 'up', 'ur'),
                          'loc': ('dnam', 'lat', 'lon'),
                          'cc': ('lsup', 'obst', 'tmp', 'flik', 't',
                                 'icon', 'hmid', 'vis', 'dewp')}
        cc_structure = {'bar': ('r','d'),
                        'wind': ('s','gust','d','t'),
                        'uv': ('i','t'),
                        'moon': ('icon','t')}

        # sanity check, skip missing items
        try:
            for (tag, list_of_tags2) in data_structure.items():
                for tag2 in list_of_tags2:
                    if weather_dom.getElementsByTagName(tag)[0].childNodes.length == 0:
                        data_structure[tag] = []
        except IndexError:
            error_data = {'error': 'Error parsing Weather.com response. Full response: %s' % xml_response}
            return error_data

        try:
            weather_data = {}
            for (tag, list_of_tags2) in data_structure.items():
                key = key_map[tag]
                weather_data[key] = {}
                for tag2 in list_of_tags2:
                    key2 = key_map[tag2]
                    try:
                        weather_data[key][key2] = weather_dom.getElementsByTagName(
                            tag)[0].getElementsByTagName(tag2)[0].firstChild.data
                    except AttributeError:
                        # current tag has empty value
                        weather_data[key][key2] = unicode('')
        except IndexError:
            error_data = {'error': 'Error parsing Weather.com response. Full response: %s' % xml_response}
            return error_data

        if weather_dom.getElementsByTagName('cc')[0].childNodes.length > 0:
            cc_dom = weather_dom.getElementsByTagName('cc')[0]
            for (tag, list_of_tags2) in cc_structure.items():
                key = key_map[tag]
                weather_data['current_conditions'][key] = {}
                for tag2 in list_of_tags2:
                    key2 = key_map[tag2]
                    try:
                        weather_data['current_conditions'][key][key2] = cc_dom.getElementsByTagName(
                            tag)[0].getElementsByTagName(tag2)[0].firstChild.data
                    except AttributeError:
                        # current tag has empty value
                        weather_data['current_conditions'][key][key2] = unicode('')

        forecasts = []
        if len(weather_dom.getElementsByTagName('dayf')) > 0:
            time_of_day_map = {'d':'day', 'n':'night'}
            for forecast in weather_dom.getElementsByTagName('dayf')[0].getElementsByTagName('day'):
                tmp_forecast = {}
                tmp_forecast['day_of_week'] = forecast.getAttribute('t')
                tmp_forecast['date'] = forecast.getAttribute('dt')
                for tag in ('hi', 'low', 'sunr', 'suns'):
                    key = key_map[tag]
                    try:
                        tmp_forecast[key] = forecast.getElementsByTagName(
                        tag)[0].firstChild.data
                    except AttributeError:
                        # if nighttime on current day, key 'hi' is empty
                        tmp_forecast[key] = unicode('')
                for part in forecast.getElementsByTagName('part'):
                    time_of_day = time_of_day_map[part.getAttribute('p')]
                    tmp_forecast[time_of_day] = {}
                    for tag2 in ('icon', 't', 'bt', 'ppcp', 'hmid'):
                        key2 = key_map[tag2]
                        try:
                            tmp_forecast[time_of_day][
                                key2] = part.getElementsByTagName(tag2)[0].firstChild.data
                        except AttributeError:
                            # if nighttime on current day, keys 'icon' and 't' are empty
                            tmp_forecast[time_of_day][key2] = unicode('')
                    tmp_forecast[time_of_day]['wind'] = {}
                    for tag2 in ('s', 'gust', 'd', 't'):
                        key2 = key_map[tag2]
                        tmp_forecast[time_of_day]['wind'][key2] = part.getElementsByTagName(
                            'wind')[0].getElementsByTagName(tag2)[0].firstChild.data
                forecasts.append(tmp_forecast)

        weather_data['forecasts'] = forecasts

        dom.unlink()
        return weather_data


    ### delete current weather
    def deleteCurrent(self):
        for i in range(5):
            Weather.dayInfo[i].delete('1.0', END)


    def printWeather(self):
        weather_com_result = self.get_weather_from_weather_com('29678')

        counter = 0

        for dayForecast in weather_com_result['forecasts']:
            # todaysWeather = "\n\nIt is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "" + DEGREE_SIGN +"F now in Seneca."
            dayTitle   = "%s, %s \n" % (dayForecast['day_of_week'], dayForecast['date'])
            dayTemp    = "%s/%s%sF\n" % (dayForecast['high'], dayForecast['low'], DEGREE_SIGN)
            dayWeather = "Day: %s (%s%% precip) \n Night: %s (%s%% precip)" % (dayForecast['day']['text'], dayForecast['day']['chance_precip'], dayForecast['night']['text'], dayForecast['night']['chance_precip'])


            Weather.dayInfo[counter].insert('1.0', dayTitle, 'dayTitle')
            Weather.dayInfo[counter].tag_configure('dayTitle',
                background  = '#050D10',
                font        = 'helvetica 22',
                relief      = 'raised',
                foreground  = '#015da1',
                borderwidth = 0,
                justify     = CENTER)

            Weather.dayInfo[counter].insert('2.0', dayTemp, 'dayTemp')
            Weather.dayInfo[counter].tag_configure('dayTemp',
                background  = '#050D10',
                font        = 'helvetica 50',
                relief      = 'raised',
                foreground  = '#06CFEF',
                borderwidth = 0,
                justify     = CENTER)

            Weather.dayInfo[counter].insert('3.0', dayWeather, ('dayWeather'))
            Weather.dayInfo[counter].tag_configure('dayWeather',
                background  = '#050D10',
                font        = 'helvetica 18',
                relief      = 'raised',
                foreground  = '#015da1',
                borderwidth = 0,
                justify     = CENTER)

            counter += 1



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
    def __init__(self, root, middleFrame, deltahours = 0, sImage = True, w = 400, h = 400):
        self.world       = [-1, -1, 1, 1]
        self.root        = root
        width, height    = w, h
        self.givenWidth  = w
        self.givenHeight = h
        self.width       = width - 50
        self.pad         = width / 16

        self.root.bind("<Escape>", lambda _ : root.destroy())
        self.delta  = timedelta(hours = deltahours)
        self.canvas = Canvas(middleFrame, width = width, height = height, background = '#050D10', borderwidth = 0, highlightbackground = "#050D10")

        viewport = (self.pad, self.pad, width-self.pad, height-self.pad)
        self.T   = Mapper(self.world, viewport)
        self.root.title('Clock')
        self.canvas.pack(fill=BOTH, expand=YES)

        self.hour = datetime.today().hour
        self.clock_finishings()


    ## Clock finishings
    #
    def clock_finishings(self):

        self.poll()

        # middle small circle
        circle = turtle.RawTurtle(self.canvas)
        circle.begin_fill()
        circle.color('#06CFEF')
        circle.pensize(1)
        circle.pu()
        circle.setposition(0, -15)
        circle.pd()
        circle.speed(0)
        circle.circle(15)
        circle.pu()
        circle.end_fill()
        circle.hideturtle()

        # big dark blue circle
        circle = turtle.RawTurtle(self.canvas)
        circle.color('#011d31')
        circle.pensize(45)
        circle.pu()
        circle.setposition(0, -200)
        circle.pd()
        circle.speed(0)
        circle.circle(200, 290)
        circle.pu()
        circle.hideturtle()

        self.span_pins(30, '#050D10', 2, 12, 20, False, 2.6)

        # connector for big blue
        circle = turtle.RawTurtle(self.canvas)
        circle.color('#011d31')
        circle.pensize(5)
        circle.pu()
        circle.setposition(0, -185)
        circle.pd()
        circle.circle(185, -100)
        circle.pu()
        circle.hideturtle()

        # connector for big blue
        circle = turtle.RawTurtle(self.canvas)
        circle.color('#011d31')
        circle.pensize(5)
        circle.pu()
        circle.setposition(0, -215)
        circle.pd()
        circle.circle(215, -100)
        circle.pu()
        circle.hideturtle()

        # inner light blue dashes
        self.span_pins(30, '#06CFEF', 1, 12, 9, False, 5)

        # inner light blue line
        circle = turtle.RawTurtle(self.canvas)
        circle.color('#06CFEF')
        circle.pensize(10)
        circle.pu()
        circle.setposition(0, -100)
        circle.pd()
        circle.speed(0)
        circle.circle(100, -120)
        circle.pu()
        circle.hideturtle()

        # connector for inner light blue
        circle = turtle.RawTurtle(self.canvas)
        circle.color('#06CFEF')
        circle.pensize(2)
        circle.pu()
        circle.setposition(0, -100)
        circle.pd()
        circle.circle(100)
        circle.pu()
        circle.hideturtle()

        # inner light blue inner invisible
        circle = turtle.RawTurtle(self.canvas)
        circle.color('#050D10')
        circle.pensize(1)
        circle.pu()
        circle.setposition(0, -95)
        circle.pd()
        circle.circle(95, 65)
        circle.pu()
        circle.hideturtle()

        # inner light blue inner invisible
        circle.color('#06CFEF')
        circle.pensize(10)
        circle.pd()
        circle.circle(95, 65)
        circle.pu()
        circle.hideturtle()


        # Marking Hour_time pins
        self.span_pins(12, '#06CFEF', 5, 30, 75)

        # Marking Minute_time pins
        self.span_pins(60, '#06CFEF', 3, 6, 15, mpin=True)

        # decrotive touches
        self.clock_finishings_decorate()


    def clock_finishings_decorate(self):
        # decorotive touches
        circle  = turtle.RawTurtle(self.canvas)
        isFirst = True

        for x in xrange(1,19):
            if x > 6 and self.hour % 12 >= x - 6:
                circle.color('#FFE64D')
            else:
                circle.color('#151D20')
            circle.screen.bgcolor('#050D10')
            circle.pensize(18)
            circle.pu()
            if isFirst:
                circle.setposition(0, -150)
                isFirst = False
            circle.pd()
            circle.speed(0)
            circle.circle(150, -30)

        # decrotive pins
        self.span_pins(60, '#050D10', 2, 6, 18, False, 3.45)

        self.poll()


    ## Draw the clock ticks
    #
    def span_pins(self, no_of_angles, color, pen_size, angle_degree, size, mpin=False, dividedWidth=2):
        for i in range(no_of_angles):
            pin = turtle.RawTurtle(self.canvas)
            pin.screen.bgcolor('#050D10')
            pin.pencolor(color)
            pin.speed(0)
            pin.pu()
            pin.pensize(pen_size)
            pin.hideturtle()
            if mpin:
                if (i*angle_degree)%30==0:
                    pass
                else:
                    pin.lt(90)
                    pin.right(i*angle_degree)
                    pin.fd(self.width / dividedWidth)
                    pin.pd()
                    pin.backward(size)
            else:
                pin.lt(90)
                pin.right(i*angle_degree)
                pin.fd(self.width / dividedWidth)
                pin.pd()
                pin.backward(size)


    ## Draws the handles.
    #
    def painthms(self):
        self.canvas.delete('hms')  # delete the hands

        T = datetime.timetuple(datetime.utcnow() - timedelta(hours = 5))
        x,x,x,h,m,s,x,x,x = T

        if h != self.hour:
            self.hour = h

            # update hour circle
            self.clock_finishings_decorate()

            if (h % 6 == 0 or h == 0):
                layout = Layout(self.root, 3, True, self.givenWidth, self.givenHeight)

                # update the weather every 6 hours
                layout.updateWeather()

                # update verse and quote every day
                if h == 12:
                    layout.updateQuoteAndVerse()

        self.root.title('%02i:%02i:%02i' %(h,m,s))

        scl = self.canvas.create_line

        # draw the hour hand
        angle = pi/2 - pi/6 * (h + m/60.0)
        x, y  = cos(angle)*0.60, sin(angle)*0.60
        scl(self.T.windowToViewport(0,0,x,y), fill = '#06CFEF', tag = 'hms', width = self.pad/4)

        # draw the minute hand
        angle = pi/2 - pi/30 * (m + s/60.0)
        x, y  = cos(angle)*0.80, sin(angle)*0.80
        scl(self.T.windowToViewport(0,0,x,y), fill = '#06CFEF', tag = 'hms', width = self.pad/6)

        # draw the second hand
        angle = pi/2 - pi/30 * s
        x, y  = cos(angle)*0.85, sin(angle)*0.85
        scl(self.T.windowToViewport(0,0,x,y), fill = '#06CFEF', tag = 'hms')


    ## Animates the clock, by redrawing everything after a certain time interval.
    #
    def poll(self):
        self.painthms()
        self.root.after(200,self.poll)


class Verse:
    verseInstance = None

    ### constructor
    class __Verse:
        def __init__(self, root, leftFrame, width, height):
            self.root   = root
            self.canvas = Canvas(leftFrame, width = width, height = height)
            self.canvas.pack(fill=BOTH, expand=YES)

            Verse.verseInstance = Text(self.canvas,
                width               = 50,
                height              = 6,
                background          = '#050D10',
                borderwidth         = 1,
                highlightbackground = "#06CFEF")

            Verse.verseInstance.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )


    ### use of singleton
    def __init__(self, root, leftFrame, width, height):
        if not Verse.verseInstance:
            Verse.__Verse(root, leftFrame, width, height)
        else:
            self.deleteCurrent()

        self.getVerse()


    ### delete the current verse
    def deleteCurrent(self):
        Verse.verseInstance.delete('1.0', END)


    ### retrieve verse and bind to instance
    def getVerse(self):
        url = "http://labs.bible.org/api/?passage=random"

        try:
            handler = urlopen(url)
        except URLError:
            return {'error': 'Could not connect to labs.bible.org'}

        title = "Verse of the day"

        verse  = "\n\n" + handler.read()
        verse  = verse.replace('<b>', '')
        verse  = verse.replace('</b>', '\n')

        handler.close()

        Verse.verseInstance.insert('1.0', title, 'verseTitle')
        Verse.verseInstance.tag_configure('verseTitle',
            background  = '#050D10',
            font        = 'helvetica 22 bold',
            relief      = 'raised',
            foreground  = '#06CFEF',
            borderwidth = 0,
            justify     = CENTER)

        Verse.verseInstance.insert('2.0', verse, 'verse')
        Verse.verseInstance.tag_configure('verse',
            background  = '#050D10',
            font        = 'helvetica 18',
            relief      = 'raised',
            foreground  = '#015da1',
            borderwidth = 0,
            justify     = LEFT)


class Quote:
    quoteInstance = None

    ### constructor
    class __Quote:
        def __init__(self, root, leftFrame, width, height):
            self.root   = root
            self.canvas = Canvas(leftFrame, width = width, height = height)
            self.canvas.pack(fill=BOTH, expand=YES)

            Quote.quoteInstance = Text(self.canvas,
                width               = 50,
                height              = 6,
                background          = '#050D10',
                borderwidth         = 1,
                highlightbackground = "#06CFEF")

            Quote.quoteInstance.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )


    ### use of singleton
    def __init__(self, root, leftFrame, width, height):
        if not Quote.quoteInstance:
            Quote.__Quote(root, leftFrame, width, height)
        else:
            self.deleteCurrent()

        self.getQuoteOfDay()


    ### delete current quote
    def deleteCurrent(self):
        Quote.quoteInstance.delete('1.0', END)


    ### retrieve quote and bind to instance
    def getQuoteOfDay(self):
        url = "http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=en"

        try:
            handler = urlopen(url)
        except URLError:
            return {'error': 'Could not connect to api.forismatic.com'}

        title = "Quote of the day"

        quote  = "\n\n" + handler.read()
        parser = HTMLParser.HTMLParser()
        quote  = parser.unescape(quote)

        handler.close()

        Quote.quoteInstance.insert('1.0', title, 'quoteTitle')
        Quote.quoteInstance.tag_configure('quoteTitle',
            background  = '#050D10',
            font        = 'helvetica 22 bold',
            relief      = 'raised',
            foreground  = '#06CFEF',
            borderwidth = 0,
            justify     = CENTER)

        Quote.quoteInstance.insert('2.0', quote, 'quote')
        Quote.quoteInstance.tag_configure('quote',
            background  = '#050D10',
            font        = 'helvetica 18',
            relief      = 'raised',
            foreground  = '#015da1',
            borderwidth = 0,
            justify     = LEFT)


class Layout:
    fullContainer = None
    fullFrame     = None

    leftFrame       = None
    topLeftFrame    = None
    bottomLeftFrame = None

    middleFrame       = None
    topMiddleFrame    = None
    bottomMiddleFrame = None

    rightFrame = None

    root   = None
    width  = None
    height = None

    ### constructor
    class __Layout:
        def __init__(self, root, deltahours, sImage, w, h):

            Layout.root   = root
            Layout.width  = w
            Layout.height = h

            ### most general frame
            Layout.fullContainer = Frame(root)
            Layout.fullContainer.pack()

            ### full frame
            Layout.fullFrame = Frame(Layout.fullContainer)
            Layout.fullFrame.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )

            ###

            ### left frame
            Layout.leftFrame = Frame(Layout.fullFrame,
                background  = "#050D10",
                borderwidth = 0,
                relief      = RIDGE,
                height      = h,
                width       = w / 4,
                )
            Layout.leftFrame.pack(side=LEFT,
                fill=BOTH,
                expand=YES,
                )

            # top left
            Layout.topLeftFrame = Frame(Layout.leftFrame,
                background  = "#050D10",
                borderwidth = 0,
                relief      = RIDGE,
                height      = 100
                )
            Layout.topLeftFrame.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )

            # bottom left
            Layout.bottomLeftFrame = Frame(Layout.leftFrame,
                background          = "#050D10",
                borderwidth         = 0,
                relief              = RIDGE,
                height              = h - 100,
                highlightbackground = "#050D10"
                )
            Layout.bottomLeftFrame.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )

            ### end left


            ### middle frame
            Layout.middleFrame = Frame(Layout.fullFrame,
                background  = "#050D10",
                borderwidth = 0,
                relief      = RIDGE,
                width       = w / 2 + 100,
                )
            Layout.middleFrame.pack(side=LEFT,
                fill=BOTH,
                expand=YES,
                )

            # top middle
            Layout.topMiddleFrame = Frame(Layout.middleFrame,
                background  = "#050D10",
                borderwidth = 0,
                relief      = RIDGE,
                height      = 100
                )
            Layout.topMiddleFrame.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )

            # set today's date in top middle
            today = datetime.today().strftime("\n %A, %B %d, %Y")

            self.day_title = Text(Layout.topMiddleFrame,
                width               = 1,
                height              = 8,
                background          = '#050D10',
                borderwidth         = 0,
                highlightbackground = "#050D10")
            self.day_title.insert('1.0', today, ('dayTitle'))
            self.day_title.tag_configure('dayTitle',
                background  = '#050D10',
                font        = 'helvetica 34 bold',
                relief      = 'raised',
                # foreground  = '#EF240C',
                foreground  = '#015da1',
                borderwidth = 0,
                justify     = CENTER)
            self.day_title.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )

            # bottom middle
            Layout.bottomMiddleFrame = Frame(Layout.middleFrame,
                background          = "#050D10",
                borderwidth         = 0,
                relief              = RIDGE,
                height              = h - 100,
                highlightbackground = "#050D10"
                )
            Layout.bottomMiddleFrame.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )

            ### end middle


            ### right frame
            Layout.rightFrame = Frame(Layout.fullFrame,
                background  = "#050D10",
                borderwidth = 0,
                relief      = RIDGE,
                width       = w / 4,
                )
            Layout.rightFrame.pack(side=LEFT,
                fill=BOTH,
                expand=YES,
                )

            ### end right

    ### singleton
    def __init__(self, root, deltahours, sImage, w, h):
        if not Layout.leftFrame:
            Layout.__Layout(root, deltahours, sImage, w, h)
            self.updateQuoteAndVerse()
            self.updateWeather()
            self.updateClock()


    ### add verse and qod in bottom left
    def updateQuoteAndVerse(self):
        Quote(Layout.root, Layout.bottomLeftFrame, Layout.width / 2, Layout.height + 25)
        Verse(Layout.root, Layout.bottomLeftFrame, Layout.width / 2, Layout.height + 25)


    ### add weather to right frame
    def updateWeather(self):
        Weather(Layout.root, Layout.rightFrame, Layout.width / 4, Layout.height + 25)


    ### add clock to middle frame
    def updateClock(self):
        Clock(Layout.root, Layout.bottomMiddleFrame, 3, True, Layout.width / 2, Layout.height)




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
       w = 1200
       h = 600
       t = False

    root = Tk()
    root.geometry ('+0+0')
    # deltahours: how far are you from utc?
    # Sometimes the clock may be run from another timezone ...

    Layout(root, deltahours, sImage, w, h)

    root.mainloop()

if __name__=='__main__':
    sys.exit(main())
