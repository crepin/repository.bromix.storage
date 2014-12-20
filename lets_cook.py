import json

root_url = 'https://github.com/bromix/'

# official repository
resources = [{'name': 'plugin.video.9gagtv', 'branch': 'master'},
             {'name': 'plugin.audio.soundcloud', 'branch': 'master'},
             {'name': 'plugin.video.7tv', 'branch': 'master'},
             {'name': 'plugin.picture.bromix.break', 'branch': 'master'},
             {'name': 'plugin.video.bromix.tlc_de', 'branch': 'master'},
             {'name': 'plugin.video.bromix.dmax_de', 'branch': 'master'},
             {'name': 'plugin.video.netzkino_de', 'branch': 'master'},

             # bromix repository
             {'name': 'plugin.video.bromix.youtube', 'branch': 'alpha29'},
             {'name': 'plugin.video.bromix.myvideo_de', 'branch': 'master'},
             {'name': 'plugin.video.bromix.break', 'branch': 'master'},
             {'name': 'plugin.video.bromix.rtl_now', 'branch': 'master'},
             {'name': 'plugin.video.bromix.rtl2_now', 'branch': 'master'},
             {'name': 'plugin.video.bromix.vox_now', 'branch': 'master'},

             {'name': 'repository.bromix', 'branch': 'master'}]

import urllib2
import os
import shutil
import md5
import zipfile


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
        open(filename, "w").write(data)
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
                xml_lines = open(addon_xml_file_name, "r").read().splitlines()
                # new addon
                addon_xml = ""

                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find("<?xml") >= 0 ):
                        continue
                    # add line
                    addon_xml += unicode(line.rstrip() + "\n", "UTF-8")

                # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
        else:
            print("Skipping '%s' (Folder no found)" % (resource['name']))
        pass

    # clean and add closing tag
    addons_xml = addons_xml.strip() + u"\n</addons>\n"

    addons_xml_file_name = os.path.join(local_path, 'addons.xml')
    _save_file(addons_xml_file_name, addons_xml.encode("UTF-8"))

    m = md5.new(open(addons_xml_file_name).read()).hexdigest()
    _save_file(addons_xml_file_name + '.md5', m)
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
        zip_file = zipfile.ZipFile(target_file_name, 'w', compression=zipfile.ZIP_DEFLATED)

        # get length of characters of what we will use as the root path       
        root_len = len(os.path.dirname(os.path.abspath(source_path)))

        # recursive writer
        for root, directories, files in os.walk(source_path):
            # subtract the source file's root from the archive root - ie. make /Users/me/desktop/zipme.txt into just /zipme.txt 
            archive_root = os.path.abspath(root)[root_len:]

            for f in files:
                fullpath = os.path.join(root, f)
                archive_name = os.path.join(archive_root, f)
                zip_file.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
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
    for resource in resources:
        download_url = '%s%s/archive/%s.zip' % (root_url, resource['name'], resource['branch'])
        zip_file_name = '%s-%s.zip' % (resource['name'], resource['branch'])
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

        old_folder_name = '%s-%s' % (resource['name'], resource['branch'])
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


import requests
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    pass


class Updater(object):
    def __init__(self, working_path, json_data):
        self._working_path = working_path
        self._json_data = json_data
        self._download_tmp = os.path.join(self._working_path, '_download_tmp_')
        pass

    pass

    def _create_download_temp(self):
        if os.path.exists(self._download_tmp):
            shutil.rmtree(self._download_tmp)
            pass
        if not os.path.exists(self._download_tmp):
            print('Creating "%s"...' % self._download_tmp)
            os.mkdir(self._download_tmp)
            pass
        pass

    def _remove_download_temp(self):
        if os.path.exists(self._download_tmp):
            print('Removing "%s"...' % self._download_tmp)
            shutil.rmtree(self._download_tmp)
            pass
        pass

    def _download_atom_feed(self, addon):
        username = self._get_user_name_from_addon(addon)
        url = 'https://github.com/%s/%s/commits/%s.atom' % (username, addon['name'], addon['branch'])
        result = requests.get(url)
        xml = ET.ElementTree(ET.fromstring(result.text))
        return xml

    def _get_user_name_from_addon(self, addon):
        global_user = self._json_data['global']['user']
        return addon.get('user', global_user)

    def _make_addon_display_name(self, addon):
        user_name = self._get_user_name_from_addon(addon)
        return '%s/%s [%s]' % (user_name, addon['name'], addon['branch'])

    def _create_addon_batch_list(self):
        result = []

        for addon in self._json_data['addons']:
            display_name = self._make_addon_display_name(addon)

            local_updated = addon.get('updated', '')
            if not local_updated:
                print 'Adding "%s" (no update)' % display_name
                result.append(addon)
                continue

            print 'Checking "%s"...' % display_name
            xml = self._download_atom_feed(addon)
            feed = xml.getroot()
            remote_updated = feed.find('{http://www.w3.org/2005/Atom}updated').text
            if remote_updated != local_updated:
                print 'Adding "%s" (updated)' % display_name
                result.append(addon)
                pass
            pass

        return result

    def _process_addon_list(self, addon_list):
        for addon in addon_list:
            display_name = self._make_addon_display_name(addon)

            pass
        pass

    def execute(self):
        print('Preparing...')
        self._create_download_temp()

        addon_list = self._create_addon_batch_list()
        self._process_addon_list(addon_list)

        self._remove_download_temp()
        print('Update finished')
        return self._json_data


if __name__ == "__main__":
    working_path = os.getcwd()
    json_filename = os.path.join(working_path, 'config.json')
    json_file = open(json_filename)
    json_data = json.load(json_file)
    json_file.close()

    updater = Updater(working_path, json_data)
    json_data = updater.execute()

    """
    downloadAndExtract()
    compress()
    generateXml()
    cleanUp()
    print("Done")
    """