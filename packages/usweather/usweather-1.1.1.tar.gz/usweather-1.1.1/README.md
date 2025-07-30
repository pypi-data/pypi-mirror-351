# usweather

usweather is a library that brings U.S. weather to you in a daily email.

- HomePage: https://github.com/kzhu2099/US-Weather
- Issues: https://github.com/kzhu2099/US-Weather/issues

[![PyPI Downloads](https://static.pepy.tech/badge/usweather)](https://pepy.tech/projects/usweather)

Author: Kevin Zhu

## Features

- Converts city to lat, lon
- Gathers weather data for a weekly or daily forecast
- Converts any forecast to html
- Sends the html to your inbox

## Installation

To install usweather, use pip: ```pip install usweather```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install usweather
source .venv/bin/activate
pip install usweather

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install usweather
.venv\Scripts\activate
pip install usweather

deactivate # when you are completely done
```

## Usage

The most basic features can be found in the examples, but you must setup the emailing yourself (tutorial below).

```python
from usweather import USWeather

w = USWeather('your_email@example.com', 'your appp pass word')
w.set_location_name('New York')

forecast = w.get_forecast(days = 7, skip_nights = False)
html = w.forecast_to_html(forecast)
print(html)

w.send_email('your_email@gmail.com', timezone = 'US/Eastern')
```

## Tutorials

This project brings in many features that require tutorials on how to use.

### Emailing

This library uses smtplib to send emails.
Both Google and Outlook supports sending through the SMTP protocol for Python.

Gmail: `(smtp.gmail.com, 587)`

Outlook: `(smtp.office365.com, 587)`

You may provide this to server info depending on your needs.

For either to work, the user will need to create an app password.

First, to create an app password, you need 2-Step Verification on your account.

This can be through a variety of methods, for both Gmail and Outlook. They both have their own authenticator apps and allow secondary emails or phone numbers.

Then, you need to make the app password.

These links will take you to the page to create an app password after you have 2FA enabled.

Gmail: https://myaccount.google.com/apppasswords

Outlook: https://go.microsoft.com/fwlink/?linkid=2274139

They only appear once and will grant complete access to your account!! You can always make more. Finally, copy and paste the app password into the instantiation for usweather.

Further help can be found here:
Gmail: https://support.google.com/mail/answer/185833?hl=en

Outlook: https://support.microsoft.com/en-us/account-billing/how-to-get-and-use-app-passwords-5896ed9b-4263-e681-128a-a6f2979a7944

### Automatic Execution

If you want a daily email with a snapshot of the NYT at a predetermined time, we have to use automation to make it happen.

#### Crontab: macOS / Linux ONLY

Because this library provides a news summary of the most recent events, you can use it with a Crontab.
Crontab is available on Unix devices and is not for Windows users.

The format of ```minute hour day-of-month month day-of-week command``` allows us to have the following command:

```x y * * * ...``` will run at y:x o' clock (e.g.: if x was 30 and y was 18, it would be at 6:30 PM)

If you would like to have a daily email at 7:00 AM to run main.py, you could have the following command:

```
0 7 * * * cd /home/path/to/your/directory && .venv/bin/python3 main.py
```

For people that want to have two emails a day (at 7AM and 4PM), simply edit the crontab:

```
0 7,15 * * * cd /home/path/to/your/directory && .venv/bin/python3 main.py
```

If you did not use a venv, simply replace ```.venv/bin/python3``` with your path to python, like ```/path/to/your/python3``` or just ```python3``` if it was added to your path..

Visit https://crontab.guru/ to learn more.

#### Task Scheduler: Windows ONLY

Windows users must take a different approach with Task Scheduler.

Press Win + R, type taskschd.msc, and hit Enter.

Create a basic task and name it, choosing your preferred frequency (like daily). The start time can also be chosen, something like 7AM.
It will start a program, with the program ```C:\path\to\your\python.exe``` and argument ```C:\path\to\your\directory\main.py```.

Visit https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page to learn more.

## Disclaimer

This library uses the Open Street Map to convert city names into latitude and longitude.
This library also uses data from the National Weather Service API.
This library povides data "as is".
Though the data that is gathered is of the highest quality, this library and its sources are not responsible for complete accuracy in data.
See the license for more information.