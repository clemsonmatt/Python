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
    def __init__(self, root, rightFrame, width = 400, height = 400):
        self.root   = root
        self.canvas = Canvas(rightFrame, width = width, height = height)
        self.root.title('Weather')
        self.canvas.pack(fill=BOTH, expand=YES)

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


    def printWeather(self):
        weather_com_result = self.get_weather_from_weather_com('29678')

        for dayForecast in weather_com_result['forecasts']:
            # print "%s \t High: %sF \t Low: %sF\n" % (dayForecast['day_of_week'], dayForecast['high'], dayForecast['low'])

            # todaysWeather = "\n\nIt is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "" + DEGREE_SIGN +"F now in Seneca."
            dayTitle   = "%s, %s \n" % (dayForecast['day_of_week'], dayForecast['date'])
            dayTemp    = "%s/%s%sF\n" % (dayForecast['high'], dayForecast['low'], DEGREE_SIGN)
            dayWeather = "Day: %s (%s%% precip) \n Night: %s (%s%% precip)" % (dayForecast['day']['text'], dayForecast['day']['chance_precip'], dayForecast['night']['text'], dayForecast['night']['chance_precip'])

            self.day_title = Text(self.canvas,
                width               = 50,
                height              = 1,
                background          = 'black',
                borderwidth         = 1,
                highlightbackground = "#118da1")

            self.day_title.insert('1.0', dayTitle, 'dayTitle')
            self.day_title.tag_configure('dayTitle',
                background  = 'black',
                font        = 'helvetica 22 bold',
                relief      = 'raised',
                foreground  = '#18CAE6',
                borderwidth = 0,
                justify     = CENTER)

            self.day_title.insert('2.0', dayTemp, 'dayTemp')
            self.day_title.tag_configure('dayTemp',
                background  = 'black',
                font        = 'helvetica 50',
                relief      = 'raised',
                foreground  = '#18CAE6',
                borderwidth = 0,
                justify     = CENTER)

            self.day_title.insert('3.0', dayWeather, ('dayWeather'))
            self.day_title.tag_configure('dayWeather',
                background  = 'black',
                font        = 'helvetica 18',
                relief      = 'raised',
                foreground  = '#18CAE6',
                borderwidth = 0,
                justify     = CENTER)

            self.day_title.pack(side=TOP,
                fill=BOTH,
                expand=YES,
                )  ###
        # print "\n\nWeather.com says: It is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "F now in Seneca."



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
        self.world    = [-1, -1, 1, 1]
        self.root     = root
        width, height = w, h
        self.width    = width - 100
        self.pad      = width / 16

        self.root.bind("<Escape>", lambda _ : root.destroy())
        self.delta  = timedelta(hours = deltahours)
        self.canvas = Canvas(middleFrame, width = width, height = height, background = 'black', borderwidth = 0, highlightbackground = "black")

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
        self.canvas.delete('hms')  # delete the hands

        T = datetime.timetuple(datetime.utcnow() - timedelta(hours = 5))
        x,x,x,h,m,s,x,x,x = T
        self.root.title('%02i:%02i:%02i' %(h,m,s))

        scl = self.canvas.create_line

        # draw the hour hand
        angle = pi/2 - pi/6 * (h + m/60.0)
        x, y  = cos(angle)*0.60, sin(angle)*0.60
        scl(self.T.windowToViewport(0,0,x,y), fill = '#18CAE6', tag = 'hms', width = self.pad/4)

        # draw the minute hand
        angle = pi/2 - pi/30 * (m + s/60.0)
        x, y  = cos(angle)*0.75, sin(angle)*0.75
        scl(self.T.windowToViewport(0,0,x,y), fill = '#18CAE6', tag = 'hms', width = self.pad/6)

        # draw the second hand
        angle = pi/2 - pi/30 * s
        x, y  = cos(angle)*0.80, sin(angle)*0.80
        scl(self.T.windowToViewport(0,0,x,y), fill = '#18CAE6', tag = 'hms')


    ## Animates the clock, by redrawing everything after a certain time interval.
    #
    def poll(self):
        self.painthms()
        self.root.after(200,self.poll)


class Verse:
    def __init__(self, root, leftFrame, width = 400, height = 400):
        self.root   = root
        self.canvas = Canvas(leftFrame, width = width, height = height)
        self.canvas.pack(fill=BOTH, expand=YES)

        self.getVerse()


    def getVerse(self):
        url = "http://labs.bible.org/api/?passage=random"

        try:
            handler = urlopen(url)
        except URLError:
            return {'error': 'Could not connect to labs.bible.org'}

        verse  = "Verse of the day:\n\n" + handler.read()
        verse  = verse.replace('<b>', '')
        verse  = verse.replace('</b>', '\n')
        parser = HTMLParser.HTMLParser()
        verse  = parser.unescape(verse)

        handler.close()

        self.verse = Text(self.canvas,
            width               = 50,
            height              = 6,
            background          = 'black',
            borderwidth         = 1,
            highlightbackground = "#118da1")

        self.verse.insert('1.0', verse, 'verse')
        self.verse.tag_configure('verse',
            background  = 'black',
            font        = 'helvetica 22 bold',
            relief      = 'raised',
            foreground  = '#18CAE6',
            borderwidth = 0,
            justify     = LEFT)

        self.verse.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )


class Quote:
    def __init__(self, root, leftFrame, width = 400, height = 400):
        self.root   = root
        self.canvas = Canvas(leftFrame, width = width, height = height)
        self.canvas.pack(fill=BOTH, expand=YES)

        self.getQuoteOfDay()


    def getQuoteOfDay(self):
        url = "http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=en"

        try:
            handler = urlopen(url)
        except URLError:
            return {'error': 'Could not connect to api.forismatic.com'}

        quote  = "Quote of the day:\n\n" + handler.read()
        parser = HTMLParser.HTMLParser()
        quote  = parser.unescape(quote)

        handler.close()

        self.quote = Text(self.canvas,
            width               = 50,
            height              = 6,
            background          = 'black',
            borderwidth         = 1,
            highlightbackground = "#118da1")

        self.quote.insert('1.0', quote, 'quote')
        self.quote.tag_configure('quote',
            background  = 'black',
            font        = 'helvetica 22 bold',
            relief      = 'raised',
            foreground  = '#18CAE6',
            borderwidth = 0,
            justify     = LEFT)

        self.quote.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )


class Layout:
    def __init__(self, root, deltahours, sImage, w, h):

        self.myParent = root

        ### Our topmost frame is called myContainer1
        self.myContainer1 = Frame(root) ###
        self.myContainer1.pack()

        # top frame
        self.top_frame = Frame(self.myContainer1)
        self.top_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )  ###

        ### left frame
        self.left_frame = Frame(self.top_frame,
            background  = "black",
            borderwidth = 0,
            relief      = RIDGE,
            height      = h,
            width       = w / 4,
            )
        self.left_frame.pack(side=LEFT,
            fill=BOTH,
            expand=YES,
            )

        # top left
        self.top_left_frame = Frame(self.left_frame,
            background  = "black",
            borderwidth = 0,
            relief      = RIDGE,
            height      = 100
            )
        self.top_left_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )

        # bottom left
        self.bottom_left_frame = Frame(self.left_frame,
            background          = "black",
            borderwidth         = 0,
            relief              = RIDGE,
            height              = h - 100,
            highlightbackground = "black"
            )
        self.bottom_left_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )

        ### end left


        ### middle frame
        self.middle_frame = Frame(self.top_frame,
            background  = "black",
            borderwidth = 0,
            relief      = RIDGE,
            width       = w / 2 + 100,
            )
        self.middle_frame.pack(side=LEFT,
            fill=BOTH,
            expand=YES,
            )

        # top middle
        self.top_middle_frame = Frame(self.middle_frame,
            background  = "black",
            borderwidth = 0,
            relief      = RIDGE,
            height      = 100
            )
        self.top_middle_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )

        # set today's date in top middle
        today = datetime.today().strftime("\n %A, %B %d, %Y")

        self.day_title = Text(self.top_middle_frame,
            width               = 1,
            height              = 8,
            background          = 'black',
            borderwidth         = 0,
            highlightbackground = "black")
        self.day_title.insert('1.0', today, ('dayTitle'))
        self.day_title.tag_configure('dayTitle',
            background  = 'black',
            font        = 'helvetica 34 bold',
            relief      = 'raised',
            foreground  = '#18CAE6',
            borderwidth = 0,
            justify     = CENTER)
        self.day_title.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )

        # bottom middle
        self.bottom_middle_frame = Frame(self.middle_frame,
            background          = "black",
            borderwidth         = 0,
            relief              = RIDGE,
            height              = h - 100,
            highlightbackground = "black"
            )
        self.bottom_middle_frame.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )

        ### end middle



        ### right frame
        self.right_frame = Frame(self.top_frame,
            background  = "black",
            borderwidth = 0,
            relief      = RIDGE,
            width       = w / 4,
            )
        self.right_frame.pack(side=LEFT,
            fill=BOTH,
            expand=YES,
            )  ###

        ### add verse and qod in bottom left
        Quote(root, self.bottom_left_frame, w / 2, h + 25)
        Verse(root, self.bottom_left_frame, w / 2, h + 25)

        ### add weather to right frame
        Weather(root, self.right_frame, w / 4, h + 25)

        ### add clock to middle frame
        Clock(root, self.bottom_middle_frame, deltahours, sImage, w / 2, h + 25)




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
