# -*- coding: utf-8 -*-

"""
Version 1.0.1 (2014.07.04)
- initial release
"""

import urllib
import urllib2
import json
import time
import hashlib
import uuid
import re
import random

__CONFIG_RTL_NOW__ = {'salt_phone': 'ba647945-6989-477b-9767-870790fcf552',
                      'salt_tablet': 'ba647945-6989-477b-9767-870790fcf552',
                      'key_phone': '46f63897-89aa-44f9-8f70-f0052050fe59',
                      'key_tablet': '56f63897-89aa-44f9-8f70-f0052050fe59',
                      'url': 'https://rtl-now.rtl.de',
                      'id': '9',
                      'episode-thumbnail-url': 'http://autoimg.rtl.de/rtlnow/%PIC_ID%/660x660/formatimage.jpg',
                      'http-header': {'X-App-Name': 'RTL NOW App',
                                      'X-Device-Type': 'rtlnow_android',
                                      'X-App-Version': '1.3.1',
                                      'X-Device-Checksum': 'ed0226e4e613e4cd81c6257bced1cb1b',
                                      'Host': 'rtl-now.rtl.de',
                                      'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; GT-I9505 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
                                      }
                      }

__CONFIG_RTL2_NOW__ = {'salt_phone': '9be405a6-2d5c-4e62-8ba0-ba2b5f11072d',
                      'salt_tablet': '4bfab4aa-705a-4e8c-b1a7-b551b1b2613f',
                      'key_phone': '26c0d1ac-e6a0-4df9-9f79-e07727f33380',
                      'key_tablet': '83bbc955-c96e-4b50-b263-bc7bcbcdf8c8',
                      'url': 'https://rtl2now.rtl2.de',
                      'id': '37',
                      'episode-thumbnail-url': 'http://autoimg.rtl.de/rtl2now/%PIC_ID%/660x660/formatimage.jpg',
                      'http-header': {'X-App-Name': 'RTL II NOW App',
                                      'X-Device-Type': 'rtl2now_android',
                                      'X-App-Version': '1.3.1',
                                      'X-Device-Checksum': 'ed0226e4e613e4cd81c6257bced1cb1b',
                                      'Host': 'rtl2now.rtl2.de',
                                      'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; GT-I9505 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
                                      }
                      }

__CONFIG_VOX_NOW__ = {'salt_phone': '9fb130b5-447e-4bbc-a44a-406f2d10d963',
                      'salt_tablet': '0df2738e-6fce-4c44-adaf-9981902de81b',
                      'key_phone': 'b11f23ac-10f1-4335-acb8-ebaaabdb8cde',
                      'key_tablet': '2e99d88e-088e-4108-a319-c94ba825fe29',
                      'url': 'https://www.voxnow.de',
                      'id': '41',
                      'episode-thumbnail-url': 'http://autoimg.rtl.de/voxnow/%PIC_ID%/660x660/formatimage.jpg',
                      'http-header': {'X-App-Name': 'VOX NOW App',
                                      'X-Device-Type': 'voxnow_android',
                                      'X-App-Version': '1.3.1',
                                      'X-Device-Checksum': 'a5fabf8ef3f4425c0b8ff716562dd1a3',
                                      'Host': 'www.voxnow.de',
                                      'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; GT-I9505 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
                                      }
                      }

class Client:
    def __init__(self, config):
        self.Config = config
        
    def _calculateToken(self, timestamp, params={}):
        token = ""
        
        hashmap = {}
        hashmap.update(params)
        
        stringbuilder = ""
        stringbuilder += self.Config.get('key_tablet', '')
        stringbuilder += ";"
        stringbuilder += self.Config.get('salt_tablet', '')
        stringbuilder += ";"
        stringbuilder += timestamp
        
        params = sorted(hashmap.items())
        
        for param in params:
            stringbuilder += ";"
            stringbuilder += param[1]
        
        if len(hashmap)==0:
            stringbuilder += ";"
           
        try:
            messagedigest = hashlib.md5()
            messagedigest.update(stringbuilder);
            abyte0 = messagedigest.digest();
            length = len(abyte0);
            
            for b in bytearray(abyte0):
                val = b
                val = 0x100 | 0xFF & val
                hval = hex(val).lower()
                token += hval[3:]
        except:
            token = ""
            
        return token
        
    def _createQueryArgs(self, params={}):
        result = {}
        result.update(params)
        
        result['_key'] = self.Config.get('key_tablet', '')
        timestamp = str(int(time.time()))
        result['_ts'] = timestamp
        result['_tk'] = self._calculateToken(timestamp, params)
        result['_auth'] = 'integrity'
        
        return result
        
    def _createRequest(self, url_path, params={}):
        if not url_path.startswith(self.Config.get('url', '')):
            url = self.Config.get('url', '')
            if not url.endswith('/') and not url_path.startswith('/'):
                url+='/'
            url = url+url_path

        request = urllib2.Request(url)
        
        # always set the id
        params['id'] = self.Config.get('id', '0')
        
        # prepare header
        header = self.Config.get('http-header', {})
        for key in header:
            request.add_header(key, header.get(key, ''))
            
        # calculate token and set params
        query_args = self._createQueryArgs(params)
        request.add_data(urllib.urlencode(query_args))
        return request
                               
    def _request(self, url_path, params={}):
        request = self._createRequest(url_path, params)
        
        result = {}
        try:
            content = urllib2.urlopen(request)
            result = json.load(content, encoding='utf-8')
            success = result.get('success', False)
            if success==True:
                result = result.get('result', {})
        except:
            # do nothing
            pass
        
        return result
    
    def _createSessionId(self):
        sId = str(uuid.uuid4())
        sId = sId.replace('-', '')
        return sId
        
    def getShows(self):
        return self._request('/api/query/json/content.list_formats')
    
    def getTips(self):
        return self._request('/api/query/json/content_redaktion.tipplist')
    
    def getNewest(self):
        return self._request('/api/query/json/content.toplist_newest')
    
    def getTop10(self):
        return self._request('/api/query/json/content.toplist_views')
    
    def getEpisodes(self, format_id, amount='25', page='1'):
        params = {'userid': '0',
                  'formatid': format_id,
                  'amount': amount,
                  'page': page}
        return self._request('/api/query/json/content.list_films', params)
    
    def getEpisodeDetails(self, id):
        params = {'filmid': id}
        return self._request('/api/query/json/content.film_details', params)
    
    def search(self, text):
        params = {'word': text,
                  'extend': '1'}
        return self._request('/api/query/json/content.format_search', params)
    
    def getLivestreams(self):
        params = {'sessionid': self._createSessionId()}
        return self._request('/api/query/json/livestream.available', params)
    
    def getEpisodeVideoUrl(self, id):
        finalUrl = None
        film = self.getEpisodeDetails(id)
        film = film.get('content', {})
        film = film.get('film', {})
        videoUrl = film.get('videourl', None)
        if videoUrl!=None:
            """
            This is part an implementation of rtl_now provided by AddonScriptorDE
            """
            opener = urllib2.build_opener()
            userAgent = "Mozilla/5.0 (Windows NT 5.1; rv:24.0) Gecko/20100101 Firefox/24.0"
            opener.addheaders = [('User-Agent', userAgent)]
            content = opener.open(videoUrl).read()
            match = re.compile("data:'(.+?)'", re.DOTALL).findall(content)
            hosterURL = videoUrl[videoUrl.find("//")+2:]
            hosterURL = hosterURL[:hosterURL.find("/")]
            url = "http://"+hosterURL+urllib.unquote(match[0])
            content = opener.open(url).read()
            match = re.compile('<filename.+?><(.+?)>', re.DOTALL).findall(content)
            url = match[0].replace("![CDATA[", "")
            matchRTMPE = re.compile('rtmpe://(.+?)/(.+?)/(.+?)]', re.DOTALL).findall(url)
            matchHDS = re.compile('http://(.+?)/(.+?)/(.+?)/(.+?)/(.+?)\\?', re.DOTALL).findall(url)
            if matchRTMPE:
                playpath = matchRTMPE[0][2]
                if ".flv" in playpath:
                    playpath = playpath[:playpath.rfind('.')]
                else:
                    playpath = "mp4:"+playpath
                finalUrl = "rtmpe://"+matchRTMPE[0][0]+"/"+matchRTMPE[0][1]+"/ playpath="+playpath+" swfVfy=1 swfUrl=http://"+hosterURL+"/includes/vodplayer.swf app="+matchRTMPE[0][1]+"/_definst_ tcUrl=rtmpe://"+matchRTMPE[0][0]+"/"+matchRTMPE[0][1]+"/ pageUrl="+videoUrl
            elif matchHDS:
                finalUrl = "rtmpe://fms-fra"+str(random.randint(1, 34))+".rtl.de/"+matchHDS[0][2]+"/ playpath=mp4:"+matchHDS[0][4].replace(".f4m", "")+" swfVfy=1 swfUrl=http://"+hosterURL+"/includes/vodplayer.swf app="+matchHDS[0][2]+"/_definst_ tcUrl=rtmpe://fms-fra"+str(random.randint(1, 34))+".rtl.de/"+matchHDS[0][2]+"/ pageUrl="+videoUrl
                
        return finalUrl
    
    def getEpisodeThumbnailImage(self, episode):
        url = ''
        
        pictures = episode.get('pictures', {})
        if len(pictures)>0: 
            pic_id = pictures.get('pic_0', None)
            if pic_id!=None:
                url = self.Config.get('episode-thumbnail-url', '')
                url = url.replace('%PIC_ID%', pic_id)
        else:
            # fallback - show the fanart image
            url = episode.get('bigaufmacherimg', '')
        
        return url