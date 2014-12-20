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

    def _process_addons(self):
        result = []

        for addon in self._json_data['addons']:
            display_name = self._make_addon_display_name(addon)
            print '================================================================================'
            print 'Checking "%s"...' % display_name

            try:
                xml = self._download_atom_feed(addon)
                feed = xml.getroot()
                local_updated = addon.get('updated', '')
                remote_updated = feed.find('{http://www.w3.org/2005/Atom}updated').text
                if remote_updated != local_updated:
                    print 'Adding "%s" (updated)' % display_name
                    zip_filename = self._download_addon(addon)
                    source_folder = self._extract_addon(addon, zip_filename)
                    self._create_repo_addon(addon, source_folder)
                    pass
                else:
                    print 'Up to date "%s"' % display_name
                    pass
                pass
            except Exception, ex:
                print 'Failed "%s" (%s)' % (display_name, ex.__str__())
                pass
            pass
        pass

    def _download_addon(self, addon):
        display_name = self._make_addon_display_name(addon)
        print 'Downloading "%s"...' % display_name

        username = self._get_user_name_from_addon(addon)
        git_url = self._json_data['global']['git']
        download_url = '%s%s/%s/archive/%s.zip' % (git_url, username, addon['name'], addon['branch'])
        zip_filename = '%s-%s.zip' % (addon['name'], addon['branch'])
        zip_filename = os.path.join(self._download_tmp, zip_filename)
        if os.path.exists(zip_filename):
            os.remove(zip_filename)
            pass
        with open(zip_filename, 'wb') as handle:
            response = requests.get(download_url, stream=True)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)
                pass
            pass
        return zip_filename

    def _extract_addon(self, addon, zip_filename):
        display_name = self._make_addon_display_name(addon)
        print 'Extracting "%s"' % display_name

        zip_file = zipfile.ZipFile(open(zip_filename, 'rb'))
        old_folder_name = '%s-%s' % (addon['name'], addon['branch'])
        new_folder_name = '%s' % (addon['name'])

        ignore_list = self._json_data['global']['ignore']
        for name in zip_file.namelist():
            last_component = name.split('/')
            last_component = last_component[len(last_component)-1]

            # skip ignored files
            if last_component in ignore_list:
                continue
            correct_path = os.path.join(self._download_tmp, name)
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
        os.remove(zip_filename)
        return os.path.join(self._download_tmp, addon['name'])

    def execute(self):
        print('Preparing...')
        self._create_download_temp()

        self._process_addons()

        self._remove_download_temp()
        print('Update finished')
        return self._json_data

    def _create_repo_addon(self, addon, source_folder):
        def _read_addon_data(addon_xml_filename):
            xml = ET.parse(addon_xml_filename)
            root = xml.getroot();
            addon_id = root.get('id', None)
            addon_version = root.get('version', None)
            return {'id': addon_id, 'version': addon_version}

        def _zip_files(source_path, zip_filename):
            zip_file = zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED)

            # get length of characters of what we will use as the root path
            root_len = len(os.path.dirname(os.path.abspath(source_path)))

            # recursive writer
            for root, directories, files in os.walk(source_path):
                # subtract the source file's root from the archive root - ie. make /Users/me/desktop/zipme.txt into just /zipme.txt
                archive_root = os.path.abspath(root)[root_len:]

                for f in files:
                    full_path = os.path.join(root, f)
                    archive_name = os.path.join(archive_root, f)
                    zip_file.write(full_path, archive_name, zipfile.ZIP_DEFLATED)
                    pass
                pass
            zip_file.close()
            pass

        def _copy_files(source_folder, target_folder, addon_version):
            files = ['addon.xml', 'changelog.txt', 'fanart.jpg', 'icon.png']
            for filename in files:
                needed = True
                if filename == 'fanart.jpg':
                    needed = False
                    pass

                source_filename = os.path.join(source_folder, filename)
                if filename == 'changelog.txt':
                    filename = 'changlelog-%s.txt' % addon_version
                    pass
                target_filename = os.path.join(target_folder, filename)

                if os.path.exists(target_filename):
                    os.remove(target_filename)
                    pass
                if needed or os.path.exists(source_filename):
                    shutil.copy(source_filename, target_filename)
                    pass
                pass
            pass

        display_name = self._make_addon_display_name(addon)
        print 'Update repo addon "%s"' % display_name
        target_folder = os.path.join(self._working_path, addon['name'])
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
            pass
        if not os.path.exists(target_folder):
            os.mkdir(target_folder)
            pass

        addon_xml_filename = os.path.join(source_folder, 'addon.xml')
        addon_data = _read_addon_data(addon_xml_filename)
        zip_filename = os.path.join(target_folder, '%s-%s.zip' % (addon_data['id'], addon_data['version']))
        _zip_files(source_folder, zip_filename)
        _copy_files(source_folder, target_folder, addon_data['version'])
        pass


if __name__ == "__main__":
    working_path = os.getcwd()
    json_filename = os.path.join(working_path, 'config.json')
    json_file = open(json_filename)
    json_data = json.load(json_file)
    json_file.close()

    updater = Updater(working_path, json_data)
    json_data = updater.execute()

    with open(json_filename, 'w') as json_file:
        json.dump(json_data, json_file, sort_keys=True, indent=4, encoding='utf-8')
        pass
    """
    compress()
    generateXml()
    cleanUp()
    print("Done")
    """