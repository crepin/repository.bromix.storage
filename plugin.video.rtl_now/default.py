# -*- coding: utf-8 -*-

import xbmcplugin
import xbmcgui
import xbmcaddon

import os
import re

#import pydevd
#pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)

from bromixbmc import Bromixbmc
bromixbmc = Bromixbmc("plugin.video.rtl_now", sys.argv)

import rtlinteractive

__now_client__ = rtlinteractive.now.Client(rtlinteractive.now.__CONFIG_RTL_NOW__)

__FANART__ = os.path.join(bromixbmc.Addon.Path, "fanart.jpg")
__ICON_FAVOURITES__ = os.path.join(bromixbmc.Addon.Path, "resources/media/favorites.png")
__ICON_NEWEST__ = os.path.join(bromixbmc.Addon.Path, "resources/media/newest.png")
__ICON_HIGHLIGHTS__ = os.path.join(bromixbmc.Addon.Path, "resources/media/highlight.png")
__ICON_LIBRARY__ = os.path.join(bromixbmc.Addon.Path, "resources/media/library.png")
__ICON_SEARCH__ = os.path.join(bromixbmc.Addon.Path, "resources/media/search.png")
__ICON_LIVE__ = os.path.join(bromixbmc.Addon.Path, "resources/media/livestream.png")

__ACTION_SHOW_LIBRARY__ = 'showLibrary'
__ACTION_SHOW_TIPS__ = 'showTips'
__ACTION_SHOW_NEWEST__ = 'showNewest'
__ACTION_SHOW_TOP10__ = 'showTop10'
__ACTION_SHOW_EPISODES__ = 'showEpisodes'
__ACTION_SEARCH__ = 'search'
__ACTION_LIVE_STREAM__ = 'playLivestream'
__ACTION_SHOW_FAVS__ = 'showFavs'
__ACTION_ADD_FAV__ = 'addFav'
__ACTION_REMOVE_FAV__ = 'removeFav'
__ACTION_PLAY__ = 'play'

__SETTING_SHOW_FANART__ = bromixbmc.Addon.getSetting('showFanart')=="true"
__SETTING_SHOW_PUCLICATION_DATE__ = bromixbmc.Addon.getSetting('showPublicationDate')=="true"

def showIndex():
    if len(bromixbmc.Addon.getFavorites())>0:
        params = {'action': __ACTION_SHOW_FAVS__}
        bromixbmc.addDir("[B]"+bromixbmc.Addon.localize(30008)+"[/B]", params = params, thumbnailImage=__ICON_FAVOURITES__, fanart=__FANART__)
        
    # add 'Sendungen A-Z'
    params = {'action': __ACTION_SHOW_LIBRARY__}
    bromixbmc.addDir(bromixbmc.Addon.localize(30000), params = params, thumbnailImage=__ICON_LIBRARY__, fanart=__FANART__)
    
    params = {'action': __ACTION_SHOW_NEWEST__}
    bromixbmc.addDir(bromixbmc.Addon.localize(30002), params = params, thumbnailImage=__ICON_NEWEST__, fanart=__FANART__)
    
    params = {'action': __ACTION_SHOW_TIPS__}
    bromixbmc.addDir(bromixbmc.Addon.localize(30001), params = params, thumbnailImage=__ICON_HIGHLIGHTS__, fanart=__FANART__)
    
    params = {'action': __ACTION_SHOW_TOP10__}
    bromixbmc.addDir(bromixbmc.Addon.localize(30003), params = params, thumbnailImage=__ICON_HIGHLIGHTS__, fanart=__FANART__)
    
    params = {'action': __ACTION_SEARCH__}
    bromixbmc.addDir(bromixbmc.Addon.localize(30004), params = params, thumbnailImage=__ICON_SEARCH__, fanart=__FANART__)
    
    params = {'action': __ACTION_LIVE_STREAM__}
    bromixbmc.addVideoLink(bromixbmc.Addon.localize(30005), params = params, thumbnailImage=__ICON_LIVE__, fanart=__FANART__)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showLibrary():
    def _sort_key(d):
        return d[1].get('formatlong', '').lower()
     
    shows = __now_client__.getShows()
    shows = shows.get('content', {})
    shows = shows.get('formatlist', {})
    
    sorted_shows = sorted(shows.items(), key=_sort_key, reverse=False)
    
    for item in sorted_shows:
        if len(item)>=2:
            show = item[1]
            title = show.get('formatlong', None)
            id = show.get('formatid', None)
            free_episodes = int(show.get('free_episodes', '0'))
            fanart = None
            if __SETTING_SHOW_FANART__:
                fanart = show.get('bigaufmacherimg', '')
                fanart = fanart.replace('/640x360/', '/768x432/')
                
            thumbnailImage = show.get('biggalerieimg', '')
            thumbnailImage = thumbnailImage.replace('/271x152/', '/768x432/')
            
            if free_episodes>=1 and title!=None and id!=None:
                params = {'action': __ACTION_SHOW_EPISODES__,
                          'id': id}
                
                contextParams = {'action': __ACTION_ADD_FAV__,
                                 'id': id,
                                 'title': title.encode('utf-8'),
                                 'fanart': fanart,
                                 'thumb': thumbnailImage}
                contextRun = 'RunPlugin('+bromixbmc.createUrl(contextParams)+')'
                contextMenu = [("[B]"+bromixbmc.Addon.localize(30006)+"[/B]", contextRun)]
                
                bromixbmc.addDir(title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, contextMenu=contextMenu)
    
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def _listEpisodes(episodes, format_id, func={}, break_at_none_free_episode=True):
    xbmcplugin.setContent(bromixbmc.Addon.Handle, 'episodes')
    
    episodes = episodes.get('content', {})
    page = episodes.get('page', '1')
    maxpage = episodes.get('maxpage', '1')
    episodes = episodes.get('filmlist', {})
        
    sorted_episodes = sorted(episodes.items(), key=func.get('sort_func', None), reverse=func.get('sort_reverse', True))
    
    show_next = False
    for item in sorted_episodes:
        if len(item)>=2:
            episode = item[1]
            title = func.get('title_func', None)(episode)
            id = episode.get('id', None)
            free = episode.get('free', '0')
            duration = episode.get('duration', '00:00:00')
            match = re.compile('(\d*)\:(\d*)\:(\d*)', re.DOTALL).findall(duration)
            if match!=None and len(match[0])>=3:
                hours = int(match[0][0])
                minutes = hours*60 + int(match[0][1]) 
                duration = str(minutes)

            year = ''
            aired = ''
            match = re.compile('(\d*)\-(\d*)\-(\d*) (\d*)\:(\d*)\:(\d*)', re.DOTALL).findall(episode.get('sendestart', '0000-00-00'))
            if match!=None and len(match[0])>=3:
                year = match[0][0]
                aired = match[0][0]+"-"+match[0][1]+"-"+match[0][2]
                if __SETTING_SHOW_PUCLICATION_DATE__:
                    date_format = xbmc.getRegion('dateshort')
                    
                    date_format = date_format.replace('%d', match[0][0])
                    date_format = date_format.replace('%m', match[0][1])
                    date_format = date_format.replace('%Y', match[0][2])
                    title = date_format+" - "+title
                
            fanart = None
            if __SETTING_SHOW_FANART__:
                fanart = episode.get('bigaufmacherimg', '')
                fanart = fanart.replace('/640x360/', '/768x432/')
                
            thumbnailImage = __now_client__.getEpisodeThumbnailImage(episode)

            additionalInfoLabels = {'duration': duration,
                                    'plot': episode.get('articleshort', ''),
                                    'episode': episode.get('episode', ''),
                                    'season': episode.get('season', ''),
                                    'year': year,
                                    'aired': aired}
                
            if free=='1' and title!=None and id!=None:
                params = {'action': __ACTION_PLAY__,
                          'id': id}
                bromixbmc.addVideoLink(title, params=params, thumbnailImage=thumbnailImage, fanart=fanart, additionalInfoLabels=additionalInfoLabels)
                show_next = True
            elif free=='0':
                show_next = False
                
    if page<maxpage and show_next:
        params = {'action': __ACTION_SHOW_EPISODES__,
                  'id': format_id,
                  'page': str(page+1)
                  }
        bromixbmc.addDir(bromixbmc.Addon.localize(30009)+' ('+str(page+1)+')', params=params, fanart=__FANART__)
        pass
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def showTips():
    def _sort_key(d):
        return d[0]
    
    def _get_title(d):
        return d.get('formatlong', '')+" - "+d.get('headlinelong', '')
    
    episodes = __now_client__.getTips()
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': False,
                                  'title_func': _get_title}
                  )
    
def showNewest():
    def _sort_key(d):
        return d[0]
    
    def _get_title(d):
        return d.get('formatlong', '')+" - "+d.get('headlinelong', '')
    
    episodes = __now_client__.getNewest()
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': False,
                                  'title_func': _get_title}
                  )
    
def showTop10():
    def _sort_key(d):
        return d[0]
    
    def _get_title(d):
        return d.get('formatlong', '')+" - "+d.get('headlinelong', '')
    
    episodes = __now_client__.getTop10()
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': False,
                                  'title_func': _get_title}
                  )

def showEpisodes(id):
    def _sort_key(d):
        return d[1].get('sendestart', '').lower()
    
    def _get_title(d):
        return d.get('headlinelong', '')
    
    page = bromixbmc.getParam('page', '1')
    
    episodes = __now_client__.getEpisodes(id, page=page)
    _listEpisodes(episodes, id, func={'sort_func': _sort_key,
                                  'sort_reverse': True,
                                  'title_func': _get_title}
                  )
    
def search():
    success = False
    keyboard = xbmc.Keyboard('', bromixbmc.Addon.localize(30004))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        success = True
        
        search_string = keyboard.getText().replace(" ", "+")
        result = __now_client__.search(search_string)
        result = result.get('content', {})
        result = result.get('list', {})
        for key in result:
            item = result.get(key,None)
            if item!=None:
                title = item.get('result', None)
                id = item.get('formatid', None)
                if title!=None and id!=None:
                    params = {'action': __ACTION_SHOW_EPISODES__,
                              'id': id}
                    bromixbmc.addDir(title, params=params)
        
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle, succeeded=success)
    return True

def playLivestream():
    streams = __now_client__.getLivestreams()
    
    lsq = bromixbmc.Addon.getSetting('liveStreamQuality')
    key = 'high_android4'
    if lsq=='1':
        key='high_android4'
    elif lsq=='0':
        key='high_android2'
    else:
        key='high_android4'
    
    url = streams.get(key, None)
    if url!=None:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(bromixbmc.Addon.Handle, True, listitem) 
    pass

def removeFav(id):
    bromixbmc.Addon.removeFavorite(id)
    xbmc.executebuiltin("Container.Refresh");
    pass

def addFav(id):
    title = bromixbmc.getParam('title', '').decode('utf-8')
    fanart = bromixbmc.getParam('fanart', '')
    thumbnailImage = bromixbmc.getParam('thumb', '')
    
    if id!=None and title!='':
        newFav = {}
        newFav['title'] = title
        newFav['fanart'] = fanart
        newFav['thumbnailImage'] = thumbnailImage
        
        bromixbmc.Addon.addFavorite(id, newFav)
    pass

def showFavs():
    def _sort_key(d):
        return d[1].get('title', "")
    
    _favs = bromixbmc.Addon.getFavorites()
    favs = sorted(_favs, key=_sort_key, reverse=False)
    
    for fav in favs:
        if len(fav)==2:
            item = fav[1]
            params = {'action': __ACTION_SHOW_EPISODES__,
                      'id': fav[0]}
            title = item.get('title', None)
            if title!=None:
                contextParams = {'action': __ACTION_REMOVE_FAV__,
                                 'id': fav[0]
                                 }
                contextRun = 'RunPlugin('+bromixbmc.createUrl(contextParams)+')'
                contextMenu = [("[B]"+bromixbmc.Addon.localize(30007)+"[/B]", contextRun)]
                
                bromixbmc.addDir(title, params=params, thumbnailImage=item.get('thumbnailImage', ''), fanart=item.get('fanart', ''), contextMenu=contextMenu)
                
    xbmcplugin.endOfDirectory(bromixbmc.Addon.Handle)
    return True

def play(id):
    url = __now_client__.getEpisodeVideoUrl(id)
    if url!=None:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(bromixbmc.Addon.Handle, True, listitem) 
    pass

action = bromixbmc.getParam('action')
id = bromixbmc.getParam('id')

if action == __ACTION_SHOW_LIBRARY__:
    showLibrary()
elif action == __ACTION_SHOW_TIPS__:
    showTips()
elif action == __ACTION_SHOW_NEWEST__:
    showNewest()
elif action == __ACTION_SHOW_TOP10__:
    showTop10()
elif action == __ACTION_SHOW_EPISODES__ and id!=None:
    showEpisodes(id)
elif action == __ACTION_SEARCH__:
    search()
elif action == __ACTION_LIVE_STREAM__:
    playLivestream()
elif action == __ACTION_SHOW_FAVS__:
    showFavs()
elif action == __ACTION_ADD_FAV__ and id!=None:
    addFav(id)
elif action == __ACTION_REMOVE_FAV__ and id!=None:
    removeFav(id)
elif action == __ACTION_PLAY__ and id!=None:
    play(id)
else:
    showIndex()