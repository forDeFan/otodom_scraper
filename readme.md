<h1>Selenium web scraper for JS dynamically generated page</h1>

Simple scraper (for JS dynamically genarated web page) to perform accumulation of real estate adverts at otodom anouncing service.

<h2>Technologies used (specified versions deifned in requirements.txt)</h2>
* Python 3<br>
* Selenium 4<br>
* Beautiful Soup 4<br>
* Tenacity<br>
* Pydantic<br>


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

1. Install codebase:

```
$ git clone https://github.com/forDeFan/otodom_scraper.git
$ cd otodom_scraper
$ pip install -r requirements.txt
```

2. Download the gecko driver accordingly to your OS distro (save the file in /driver dir):
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