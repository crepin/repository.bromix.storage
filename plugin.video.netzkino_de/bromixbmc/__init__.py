"""
Version 2.0.2 (2014.07.10)
- FIX: Android won't return a valid language so I added a default value 

Version 2.0.1 (2014.07.08)
- complete restructuring

Version 1.0.2 (2014.06.25)
- added 'getFavorites', 'addFavorite' and 'removeFavorite'
- set the encoding for the favorite routines to utf-8
- removed 'duration' and 'plot' from addVideoLink -> therefore use 'additionalInfoLabels'

Version 1.0.1 (2014.06.24)
- added support for helping with favorites
- initial release
"""

import locale
import re
import sys
import urlparse

from plugin import Plugin
from keyboard import Keyboard

def stripHtmlFromText(text):
    return re.sub('<[^<]+?>', '', text)

def getParam(name, default=None):
    args = urlparse.parse_qs(sys.argv[2][1:])
    value = args.get(name, None)
    if value and len(value)>=1:
        return value[0]
    
    return default

def getLanguageId(default='en-US'):
    result = default
    
    try:
        language = locale.getdefaultlocale()
        if language and len(language)>=1 and language[0]:
            result = language[0].replace('_', '-')
    except:
        # do nothing
        pass
    
    return result