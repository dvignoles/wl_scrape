"""
    WeatherLinkScrape.py
    Author: Daniel Vignoles
    WeatherLinkScrape is a tool to scrape .xml data from api.weatherlink.com xml pages
"""

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from xml.etree import ElementTree as ET
from re import search
from datetime import datetime
from os import getcwd,chdir,makedirs

#ElementTree.Element name of Observation Time attribute
OBSERVATION = 'observation_time'
#Regular expresion to parse date string from Observation Time attribute
OBSERVATION_PARSE = r'\w{3} \d{1,2} \d{4}, \d{1,2}:\d{2} \w{2} \w{3}'
#Format of parsed date to for strptime
DATE_FORMAT = '%b %d %Y, %I:%M %p %Z'
#Format for strftime to name files
OBSERVATION_STR = '%Y-%m-%d_%H-%M'

def write_xml(url):
    """
        url: api.weatherlink.com xml webpage
        write_xml writes a .xml to data folder in the appropriate year/month/day/ path
    """
    root_dir = getcwd()
    #chdir(data_dir)

    tree = get_tree(url)
    date_time = get_obs_time(tree)
    year = str(date_time.year)
    month = str(date_time.month)
    day = str(date_time.day)

    path = 'data'+'/'+year+'/'+month+'/'+day

    makedirs(path,exist_ok=True)
    chdir(path)
    tree.write(get_obs_time_str(date_time)+'.xml')
    chdir(root_dir)

def get_obs_time_str(date_time):
    """
        Return str reprensentation in OBSERVATION_STR format of date_time
    """
    return(datetime.strftime(date_time,OBSERVATION_STR))

def get_obs_time(tree):
    """
        Return datetime object parsed from tree
    """
    observation_time = tree.getroot().find(OBSERVATION).text
    match = search(OBSERVATION_PARSE,observation_time)
    return(datetime.strptime(match.group(),DATE_FORMAT))

def get_tree(url):
    """
        Return an ElementTree representing the XML
    """
    xml_raw = simple_get(url)
    root = ET.fromstring(xml_raw)
    tree = ET.ElementTree(root)
    return(tree)

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be xml, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('xml') > -1)


def log_error(e):
    """
    Print Error
    """
    print(e)
    #TODO: Log Errors


