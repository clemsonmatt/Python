#!/usr/bin/python

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
import sys
import re
import operator
from math import pow
from xml.dom import minidom
import json

try:
    from unidecode import unidecode
except ImportError:
    pass

try:
    from tkinter import *       # python 3
except ImportError:
    try:
       from mtTkinter import *  # for thread safe
    except ImportError:
       from Tkinter import *    # python 2


WEATHER_COM_URL = 'http://wxdata.weather.com/wxdata/weather/local/%s?' + \
                       'unit=%s&dayf=5&cc=*'


DEGREE_SIGN = u'\N{DEGREE SIGN}'


##
 # Main Class
 ##
class Weather:
    def __init__(self, root, width = 400, height = 400):
        self.root   = root
        self.canvas = Canvas(root, width = width, height = height)
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

        # for dayForecast in weather_com_result['forecasts']:
            # print "%s \t High: %sF \t Low: %sF\n" % (dayForecast['day_of_week'], dayForecast['high'], dayForecast['low'])

        # todaysWeather = "\n\nIt is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "" + DEGREE_SIGN +"F now in Seneca."
        dayForecast = weather_com_result['forecasts'][1]
        dayWeather = "%s, %s \n High: %sF \n Low: %sF \n Day: %s (%s%% precip) \n Night: %s (%s%% precip)" % (dayForecast['day_of_week'], dayForecast['date'], dayForecast['high'], dayForecast['low'], dayForecast['day']['text'], dayForecast['day']['chance_precip'], dayForecast['night']['text'], dayForecast['night']['chance_precip'])

        self.day_title = Text(self.canvas,
            width               = 100,
            height              = 20,
            background          = 'black',
            borderwidth         = 0,
            highlightbackground = "black")
        self.day_title.insert('1.0', dayWeather, ('dayTitle'))
        self.day_title.tag_configure('dayTitle',
            background  = 'black',
            font        = 'helvetica 24 bold',
            relief      = 'raised',
            foreground  = '#18CAE6',
            borderwidth = 0,
            justify     = CENTER)
        self.day_title.pack(side=TOP,
            fill=BOTH,
            expand=YES,
            )  ###
        # print "\n\nWeather.com says: It is " + weather_com_result['current_conditions']['text'].lower() + " and " + weather_com_result['current_conditions']['temperature'] + "F now in Seneca."


class Main:
    root = Tk()

    Weather(root)

    root.mainloop()
