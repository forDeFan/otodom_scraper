<h1>Selenium web scraper for otodom</h1>

Simple web page scrapper to accumulate real estate adverts from otodom anouncing service.


## Table of contents

* [Setup](#setup)
* [Run](#run)
* [TODO](#todo)

## Setup

### Prerequisites

* python 3.X
* linux distro (tested on Ubuntu x86_64 5.4.0-144-generic)


### Install

Advice to set up virtual environment before packages installation.

Install codebase and run the app:

```
$ git clone https://github.com/forDeFan/otodom_scraper.git
$ cd otodom_scraper
$ pip install -r requirements.txt
```

Download the gecko driver accordingly to your OS distro (save the file in /driver dir):
<br>
https://github.com/mozilla/geckodriver/releases

### Parametrization

for general setup: parameters.yaml<br>
for elements html tags to be scraped: presets.yaml


### Run

Configuration is made thru parameters.yaml, web page elements class defined in prestes.yaml - can be changed accordingly if needed.
<br>
Configutation files in /config dir.
<br>
Verbose terminal logging is on by default.
After succesfull run example.txt (with results) will be created in project root.

To start scraper:

```
$ python3 main.py
```

## Todo

Will add user interation thru command prompt in order to prepare the app for contenerization later on.