'''
Author: Kevin Zhu
The main class for the usweather library.
'''

import requests

import time
import datetime
import pytz

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from kzutil import send_email

class USWeather:
    def __init__(self, sender_email, sender_email_app_password, style_sheet = None):

        '''
        The main class for the usweather library.

        Parameters
        ----------
        string sender_email:
            the email of the sender
        string sender_email_app_password:
            the app password of the sender email
        string style_sheet:
            a custom style sheet in CSS format
        '''

        self.weather_api = 'https://api.weather.gov'
        self.location_api = 'https://nominatim.openstreetmap.org/search'

        self.style_sheet = style_sheet or \
'''
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: Verdana, sans-serif;
}

h1 {
    font-size: 15px;
}

p, div {
    font-size: 12px;
}
'''
        self.sender_email = sender_email
        self.sender_email_app_password = sender_email_app_password

    def get_location(self, name):

        '''
        Parameters
        ----------
        string name:
            the name of the location

        Returns
        -------
        string
            the location data
        '''

        params = {
            'q': name,
            'format': 'json',
            'limit': 1
        }

        response = requests.get(self.location_api, params = params, headers = {'User-Agent': 'usweather/1.0'})

        if response.status_code == 200:
            data = response.json()
            return data[0]

        else:
            print(response)
            print(f'Error: {response.status_code}')
            return {}

    def get(self, path):

        '''
        Gets data from the weather.gov source (US only)

        Parameters
        ----------
        string path
            the path to use in extension from the main url, e.g: /path/to/x,y/item

        Returns
        -------
        dict
            the successful data in json format
            if unsuccessful, returns an empty dict and prints the status code
        '''

        response = requests.get(self.weather_api + path, headers = {'User-Agent': f'usweather_user ({self.sender_email})'})

        if response.status_code == 200:
            data = response.json()
            return data

        else:
            print(f'Error: {response.status_code}')
            return {}

    def set_location_name(self, location_name):

        '''
        Sets this class' location name

        Parameters
        ----------
        string location_name:
            the location name to set for this class to use
        '''

        self.location_name = location_name.capitalize()

    def get_forecast(self, days = 7, skip_nights = False):

        '''
        Parameters
        ----------
        string days, defaults to 7:
            the amount of days of data to get (max 7)
        boolean skip_nights, defaults to False:
            whether or not to skip the inclusion of nights

        Returns
        -------
        list
            a list of the forecast requested
        '''

        location = self.get_location(self.location_name)
        path = '/points/{lat},{lon}'.format(
            lat = location['lat'],
            lon = location['lon']
        )

        point = self.get(path)['properties']

        path = '/gridpoints/{wfo}/{x},{y}/forecast'.format(
            wfo = point['gridId'],
            x = point['gridX'],
            y = point['gridY']
        )

        data = self.get(path)

        self.forecast = []

        for i in range(days * 2):
            if skip_nights and i % 2 == 1:
                continue

            self.forecast.append(data['properties']['periods'][i])

        return self.forecast

    def get_hourly_forecast(self, hours = 24):

        '''
        Parameters
        ----------
        string hours, defaults to 24:
            the amount of hours of data to get

        Returns
        -------
        list
            a list of the forecast requested
        '''

        location = self.get_location(self.location_name)
        path = '/points/{lat},{lon}'.format(
            lat = location['lat'],
            lon = location['lon']
        )

        point = self.get(path)['properties']

        path = '/gridpoints/{wfo}/{x},{y}/forecast/hourly'.format(
            wfo = point['gridId'],
            x = point['gridX'],
            y = point['gridY']
        )

        data = self.get(path)

        self.forecast = []

        for i in range(hours):
            self.forecast.append(data['properties']['periods'][i])

        return self.forecast

    def forecast_to_html(self, forecast = None, html_template = None):

        '''
        Parameters
        ----------
        list forecast, defaults to self.forecast:
            the forecast to turn into html
        string html_template, optional:
            a custom template for the html of each forecast item

        Returns
        -------
        string
            the html created
        '''

        self.html_body = ''
        html_template = html_template or \
'''
<div style = 'max-width: 300px; width: 100%; margin-left: 10px; margin-right: 10px;'>
    <h3>{name}</h3>
    <p>
    {short_forecast}<br>
    Temperature: {temperature} °F<br>
    Precipitation: {precipitation}%<br>
    Wind Speed: {wind_speed} {wind_direction}<br>
    </p>
    <hr style = 'margin-left: 10px; margin-right: 10px; width: calc(100% - 20px);'>
</div>
'''

        forecast = forecast or self.forecast
        for item in forecast:
            self.html_body += html_template.format(
                name = f'{(item['name'] + ', ') if item['name'] != '' else ''}{datetime.datetime.fromisoformat(item['startTime']).strftime('%B %d @ %I %p')}',
                short_forecast = item['shortForecast'],
                temperature = item['temperature'],
                precipitation = item['probabilityOfPrecipitation']['value'] or 0,
                wind_speed = item['windSpeed'],
                wind_direction = item['windDirection']
            )

        return self.html_body

    def send_email(self, recipient, server_info = ('smtp.gmail.com', 587), main_subject = 'Daily Weather', timezone = 'US/Eastern', weather_html_body = None, main_html_template = None):

        '''
        Attempts to send an email from the sender email to the recipient with a subject of main_subject @ Date Time.

        Parameters
        ----------
        string recipient:
            the email of the recipient
        string weather_html_body, optional:
            defaults to self.html_body, custom html to send in the email
        string main_subject, optional:
            the main title of the email (excluding date/time)
        string timezone, optional:
            the appropriate pytz name
        string main_html_template, optional:
            custom template for the main email
        '''

        html_body = weather_html_body or self.html_body
        html_template = main_html_template or \
'''
<!DOCTYPE html>
<html>
    <head>
        <style>
            {style_sheet}
        </style>
    </head>
    <body>
        <h1>
            <h1>Weather forecast for {location_name}</h1>
        </h1>
        {html_body}
    </body>
</html>
'''

        full_html = html_template.format(
            style_sheet = self.style_sheet,
            location_name = self.location_name,
            html_body = html_body
        )

        send_email(self.sender_email, self.sender_email_app_password, recipient, main_subject, full_html, server_info, timezone)