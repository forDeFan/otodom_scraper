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

Configutation files in /config dir.
<br>
For general setup (search params mainly): parameters.yaml<br>
For elements html tags to be scraped: presets.yaml


## Run

Verbose terminal logging is on by default (can be changed in parameters.yaml).<br>
After succesfull run file example.txt will be created in project root (filename and path can be defined in parameters.yaml)

To start scraper:

```
$ python3 main.py
```

## Todo

Tests and possibly contenerization later on.