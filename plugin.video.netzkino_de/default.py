# -*- coding: utf-8 -*-

import os
import re
import json
import urllib2
import urllib

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

import bromixbmc

__plugin__ = bromixbmc.Plugin()

__FANART__ = os.path.join(__plugin__.getPath(), "fanart.jpg")
__ICON_HIGHLIGHTS__ = os.path.join(__plugin__.getPath(), "resources/media/highlight.png")
__ICON_SEARCH__ = os.path.join(__plugin__.getPath(), "resources/media/search.png")

__ACTION_SHOW_CATEGORY__ = 'showCategory'
__ACTION_SEARCH__ = 'search'
__ACTION_PLAY__ = 'play'

__SETTING_SHOW_FANART__ = __plugin__.getSettingAsBool('showFanart')
if not __SETTING_SHOW_FANART__:
    __FANART__ = ''

def _request(url_path, params={}):
    language = bromixbmc.getLanguageId('de-DE')
    params['d'] = 'android-tablet'
    if language:
        params['l'] = language
        region = language.split('-')
        if region and len(region)>=2:
            params['g'] = region[1]
    
    result = {}
    
    url = 'http://api.netzkino.de.simplecache.net'
    if not url_path.startswith('/'):
        url = url+'/'
        
    url = url+url_path
        
    if len(params)>0:
        query_args = urllib.urlencode(params)
        if not url.endswith('?'):
            url = url+'?'
        url = url+query_args
        
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', 'stagefright/1.2 (Linux;Android 4.4.2)'),
                         ('Host', 'api.netzkino.de.simplecache.net')]
    try:
        content = opener.open(url)
        result = json.load(content, encoding='utf-8')
    except:
        # do nothing
        pass
    
    return result

def _listCategories(json_categories):
    for category in json_categories:
        id = category.get('id', None)
        name = category.get('title', None)
        if id and name:
            thumbnailImage = 'http://dyn.netzkino.de/wp-content/themes/netzkino/imgs/categories/'+str(id)+'.png'
            if id==8 or id==161:
                thumbnailImage = __ICON_HIGHLIGHTS__
            params = {'action': __ACTION_SHOW_CATEGORY__,
                      'id': id}
            __plugin__.addDirectory(name=name, params=params, thumbnailImage=thumbnailImage, fanart=__FANART__)

def showIndex():
    params = {'action': __ACTION_SEARCH__}
    __plugin__.addDirectory("[B]"+__plugin__.localize(30000)+"[/B]", params = params, thumbnailImage=__ICON_SEARCH__, fanart=__FANART__)
    
    categories = _request('/capi-2.0a/index.json')
    
    # first list the homepage categories
    homepage_categories = categories.get('homepage_categories', {})
    _listCategories(homepage_categories)
            
    # after that load all other categories
    categories = categories.get('categories', {})
    _listCategories(categories)
            
    __plugin__.endOfDirectory()

def _listPosts(json_posts):
    __plugin__.setContent('movies')
    for post in json_posts:
        id = post.get('id', None)
        name = post.get('title', None)
        thumbnailImage = post.get('thumbnail', '')
        plot = bromixbmc.stripHtmlFromText(post.get('content', ''))
        
        custom_fields = post.get('custom_fields', None)
        if custom_fields:
            fanart = ''
            if __SETTING_SHOW_FANART__:
                fanart = custom_fields.get('featured_img_all', [__FANART__])[0]
            streaming = custom_fields.get('Streaming', None)
            if streaming and len(streaming)>0:
                streamId = streaming[0]
                params = {'action': __ACTION_PLAY__,
                          'id': streamId}
                
                infoLabels = {'plot': plot}
                year = custom_fields.get('Jahr', [])
                if len(year)>0:
                    infoLabels['year'] = year[0]
                    
                cast = custom_fields.get('Stars', [])
                if len(cast)>0:
                    cast = cast[0].split(',')
                    _cast = []
                    for c in cast:
                        _cast.append(c.strip())
                    infoLabels['cast'] = _cast
                    
                director = custom_fields.get('Regisseur', [])
                if len(director)>0:
                    infoLabels['director'] = director[0]
                    
                ratings = custom_fields.get('IMDb-Bewertung', ['0,0'])
                for rating in ratings:
                    try:
                        rating = rating.replace(',', '.')
                        rating = float(rating)
                        infoLabels['rating']=rating
                        break
                    except:
                        # do nothing
                        pass
                
                __plugin__.addVideoLink(name=name, params=params, thumbnailImage=thumbnailImage, fanart=fanart, infoLabels=infoLabels)

def showCategory(id):
    category = _request('/capi-2.0a/categories/'+id)
    posts = category.get('posts', {})
    _listPosts(posts)
    
    __plugin__.endOfDirectory()

def play(id):
    streamer_url = 'http://netzkino_and-vh.akamaihd.net/i/'
    
    try:
        response = urllib2.urlopen('http://www.netzkino.de/adconf/android-new.php')
        result = json.load(response)
        streamer_url = result.get('streamer', 'http://netzkino_and-vh.akamaihd.net/i/')
    except:
        # do nothing
        pass
    
    
    url = streamer_url+id+'.mp4/master.m3u8'
    __plugin__.setResolvedUrl(url)
    
def search():
    success = False
    
    keyboard = bromixbmc.Keyboard(__plugin__.localize(30000))
    if keyboard.doModal():
        success = True
        
        search_string = keyboard.getText().replace(" ", "+")
        result = _request('/capi-2.0a/search', params = {'q': search_string})
        posts = result.get('posts', [])
        _listPosts(posts)
        
    __plugin__.endOfDirectory(success)

action = bromixbmc.getParam('action')
id = bromixbmc.getParam('id')

if action == __ACTION_SEARCH__:
    search()
elif action == __ACTION_SHOW_CATEGORY__ and id:
    showCategory(id)
elif action == __ACTION_PLAY__ and id:
    play(id)
else:
    showIndex()