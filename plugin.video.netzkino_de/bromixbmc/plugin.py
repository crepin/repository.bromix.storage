import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui

import os
import sys
import urllib
import json

class Plugin(object):
    def __init__(self, name=None, addon_id=None):
        if addon_id:
            self._addon = xbmcaddon.Addon(id=addon_id)
        else:
            self._addon =  xbmcaddon.Addon()

        self._addon_uri = sys.argv[0]
        self._addon_handle = int(sys.argv[1])            
        self._addon_id = addon_id or self._addon.getAddonInfo('id')
        self._name = name or self._addon.getAddonInfo('name')
        self._addon_path = xbmc.translatePath(self._addon.getAddonInfo('path'))
        
        self._addon_data_path = xbmc.translatePath('special://profile/addon_data/%s' % self._addon_id)
        if not os.path.isdir(self._addon_data_path):
            os.mkdir(self._addon_data_path)
            
        self._favs_file = os.path.join(self._addon_data_path, "favs.dat")
        
    def createUrl(self, params={}):
        if params and len(params)>0:
            return self._addon_uri + '?' + urllib.urlencode(params)
        
        # default
        return self._addon_uri
    
    def getHandle(self):
        return self._addon_handle
    
    def setContent(self, content_type):
        xbmcplugin.setContent(self._addon_handle, content_type)
        
    def getPath(self):
        return self._addon_path
    
    def localize(self, id):
        return self._addon.getLocalizedString(id)
    
    def getSettingAsBool(self, name):
        return self._addon.getSetting(name)=="true"
    
    def addDirectory(self, name, params={}, thumbnailImage='', fanart='', contextMenu=None):
        url = self.createUrl(params)
        
        item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=thumbnailImage)
        if fanart and len(fanart)>0:
            item.setProperty("fanart_image", fanart)
            
        if contextMenu!=None:
            item.addContextMenuItems(contextMenu);
            
        return xbmcplugin.addDirectoryItem(handle=self._addon_handle,url=url,listitem=item,isFolder=True)
    
    def addVideoLink(self, name, params={}, thumbnailImage='', fanart='', infoLabels={}):
        url = self.createUrl(params)
        
        item = xbmcgui.ListItem(unicode(name), iconImage="DefaultVideo.png", thumbnailImage=thumbnailImage)
        
        # prepare infoLabels
        _infoLabels = {'title': name}
        _infoLabels.update(infoLabels)
            
        item.setInfo(type="video", infoLabels=_infoLabels)
        item.setProperty('IsPlayable', 'true')
        if fanart and len(fanart)>0:
            item.setProperty("fanart_image", fanart)
        
        return xbmcplugin.addDirectoryItem(handle=self._addon_handle, url=url, listitem=item)
    
    def endOfDirectory(self, success=True):
        xbmcplugin.endOfDirectory(self._addon_handle, succeeded=success)
        
    def setResolvedUrl(self, url):
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(self._addon_handle, True, listitem)
        
        # just to be sure :)
        tries = 100
        while tries>0:
            xbmc.sleep(50)
            if xbmc.Player().isPlaying() and xbmc.getCondVisibility("Player.Paused"):
                xbmc.Player().pause()
                break
            tries-=1
            
    def _loadFavs(self):
        favs = {'favs': {}}
        if self._favs_file and os.path.exists(self._favs_file):
            try:
                file = open(self._favs_file, 'r')
                favs = json.loads(file.read(), encoding='utf-8')
            except:
                #do nothing
                pass
                
        return favs
    
    def getFavorites(self):
        favs = self._loadFavs()
        return favs.get('favs', {}).items()
    
    def setFavorite(self, id, fav):
        favs = self._loadFavs()
        
        favs['favs'][id] = fav
        self._storeFavs(favs)
        
    def removeFavorite(self, id):
        favs = self._loadFavs()
        fav = favs.get('favs', {}).get(id, None)
        if fav!=None:
            del favs['favs'][id]
            self._storeFavs(favs)
            
        return self.getFavorites()
    
    def _storeFavs(self, favs):
        if self._favs_file and favs:
            with open(self._favs_file, 'w') as outfile:
                json.dump(favs, outfile, sort_keys = True, indent = 4, encoding='utf-8')