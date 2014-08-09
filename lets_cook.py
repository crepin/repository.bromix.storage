root_url = 'https://github.com/bromix/'

resources = [{'name': 'plugin.video.bromix.youtube',
              'branch': 'master'},
             {'name': 'plugin.picture.bromix.break',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.break',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.netzkino_de',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.tlc_de',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.dmax_de',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.rtl_now',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.rtl2_now',
              'branch': 'master'},
             {'name': 'plugin.video.bromix.vox_now',
              'branch': 'master'},
             {'name': 'plugin.video.7tv',
              'branch': 'beta2'},#'branch': 'master'},
             {'name': 'repository.bromix',
              'branch': 'master'},
             ]

import urllib2
import os
import shutil
import md5
import zipfile
import xml.etree.cElementTree as ET

def cleanUp():
    print("Cleaning up...")
    local_path = os.getcwd()
    dl_path = os.path.join(local_path, '_dl_tmp')
    if os.path.exists(dl_path):
        shutil.rmtree(dl_path)
    
def generateXml():
    def _save_file(filename, data):
        if os.path.exists(filename):
            os.remove(filename)
        open(filename, "w" ).write(data)
        pass
    
    addons_xml = u"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n"
     
    print("Creating addon.xml and addon.xml.md5...")
    local_path = os.getcwd()
    for resource in resources:
        resource_path = os.path.join(local_path, resource['name'])
        if os.path.exists(resource_path):
            print("Reading '%s'" % (resource['name']))
            addon_xml_file_name = os.path.join(resource_path, 'addon.xml')
            if os.path.exists(addon_xml_file_name):
                xml_lines = open(addon_xml_file_name, "r" ).read().splitlines()
                # new addon
                addon_xml = ""

                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find( "<?xml" ) >= 0 ):
                        continue
                    # add line
                    addon_xml += unicode( line.rstrip() + "\n", "UTF-8" )

                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
        else:
            print("Skipping '%s' (Folder no found)" % (resource['name']))
        pass
    
    # clean and add closing tag
    addons_xml = addons_xml.strip() + u"\n</addons>\n"
    
    addons_xml_file_name = os.path.join(local_path, 'addons.xml') 
    _save_file(addons_xml_file_name, addons_xml.encode( "UTF-8" ))
    
    m = md5.new(open(addons_xml_file_name).read()).hexdigest()
    _save_file(addons_xml_file_name+'.md5', m)
    pass
    
def compress():
    def _readAddon(xml_file_name):
        xml = ET.parse(xml_file_name)
        root = xml.getroot();
        addon_id = root.get('id', None)
        addon_version = root.get('version', None)
        return {'id': addon_id,
                'version': addon_version
                }
        
    def _zipFiles(source_path, target_file_name):
        zip_file = zipfile.ZipFile(target_file_name, 'w', compression=zipfile.ZIP_DEFLATED )

        # get length of characters of what we will use as the root path       
        root_len = len( os.path.dirname(os.path.abspath(source_path)) )

        #recursive writer
        for root, directories, files in os.walk(source_path):
            # subtract the source file's root from the archive root - ie. make /Users/me/desktop/zipme.txt into just /zipme.txt 
            archive_root = os.path.abspath(root)[root_len:]
            
            for f in files:
                fullpath = os.path.join( root, f )
                archive_name = os.path.join( archive_root, f )
                zip_file.write( fullpath, archive_name, zipfile.ZIP_DEFLATED )
        zip_file.close()
    
    print("Compressing resources...")
    local_path = os.getcwd()
    for resource in resources:
        resource_path = os.path.join(local_path, '_dl_tmp', resource['name'])
        target_path = os.path.join(local_path, resource['name'])
        
        if os.path.exists(resource_path):
            if not os.path.exists(target_path):
                os.mkdir(target_path)
            
            print("Processing '%s'" % resource['name'])
            addon_xml_file_name = os.path.join(resource_path, 'addon.xml')
            addon_info = _readAddon(addon_xml_file_name)
            
            addon_zip_file_name = os.path.join(target_path, '%s-%s.zip' % (addon_info['id'], addon_info['version']))
            if not os.path.exists(addon_zip_file_name):
                _zipFiles(resource_path, addon_zip_file_name)
            else:
                print("Skipping '%s' (already exists)" % (addon_zip_file_name))
            
            changelog_file_name = os.path.join(target_path, 'changelog-%s.txt' % (addon_info['version']))
            files_to_copy = [{'From': os.path.join(resource_path, 'addon.xml'),
                              'To': os.path.join(target_path, 'addon.xml')},
                             
                             {'From': os.path.join(resource_path, 'fanart.jpg'),
                              'To': os.path.join(target_path, 'fanart.jpg')},
                             
                             {'From': os.path.join(resource_path, 'icon.png'),
                              'To': os.path.join(target_path, 'icon.png')},
                             
                             {'From': os.path.join(resource_path, 'changelog.txt'),
                              'To': changelog_file_name}
                             ]
            
            for file_to_copy in files_to_copy:
                if os.path.exists(file_to_copy['To']):
                    os.remove(file_to_copy['To'])
                
                if os.path.exists(file_to_copy['From']):
                    shutil.copy(file_to_copy['From'], file_to_copy['To'])
                pass
        else:
            print("Skipping '%s' (path not found)" % resource['name'])
        pass
    pass
    
def downloadAndExtract():
    print("Downloading resources...")
    
    local_path = os.getcwd()
    local_path = os.path.join(local_path, '_dl_tmp')
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    if not os.path.exists(local_path):
        os.mkdir(local_path)
    
    for resource in resources:
        download_url = '%s%s/archive/%s.zip' % (root_url, resource['name'] ,resource['branch'])
        zip_file_name = '%s-%s.zip' % (resource['name'] ,resource['branch'])
        zip_file_name = os.path.join(local_path, zip_file_name)
        
        print("Downloading '%s' from '%s'" % ( resource['name'], download_url ))
        if os.path.exists(zip_file_name):
            os.remove(zip_file_name)
        download_file = open(zip_file_name, 'wb')
        req = urllib2.urlopen(download_url)
        download_file.write(req.read())
        download_file.close()
        download_file = open(zip_file_name, 'rb')
        zip_file = zipfile.ZipFile(download_file)
        
        old_folder_name = '%s-%s' % (resource['name'] ,resource['branch'])
        new_folder_name = '%s' % (resource['name'])
               
        print("Extracting '%s'" % (zip_file_name))
        for name in zip_file.namelist():
            correct_path = os.path.join(local_path, name)
            correct_path = correct_path.replace(old_folder_name, new_folder_name)
            if correct_path.endswith('/'):
                if not os.path.exists(correct_path):
                    os.mkdir(correct_path)
            else:
                tmp_file = open(correct_path, 'wb')
                tmp_file.write(zip_file.read(name))
                tmp_file.close()
            pass
        
        zip_file.close()
        download_file.close()
        os.remove(zip_file_name)
    print("Done downloading")

if __name__ == "__main__":
    downloadAndExtract()
    compress()
    generateXml()
    cleanUp()
    print("Done")