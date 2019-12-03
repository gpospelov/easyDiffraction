#!/usr/bin/env python3

import os, sys
import xml, dicttoxml
import datetime
import Project
import Functions

def downloadQtInstallerFramework():
    message = "download QtInstallerFramework"
    try:
        config = Project.Config()
        Functions.downloadFile(
            url=config['qtifw']['setup']['download_url'],
            destination=config['qtifw']['setup']['download_path']
        )
    except Exception as exception:
        Functions.printFailMessage(message, exception)
        sys.exit()
    else:
        Functions.printSuccessMessage(message)

def osDependentPreparation():
    config = Project.Config()
    os_name = config['os']['name']
    message = "prepare for os '{0}'".format(os_name)
    if os_name == 'osx':
        try:
            Functions.attachDmg(config['qtifw']['setup']['download_path'])
        except Exception as exception:
            Functions.printFailMessage(message, exception)
            sys.exit()
        else:
            Functions.printSuccessMessage(message)
    elif os_name == 'linux':
        try:
            Functions.setEnvVariable("QT_QPA_PLATFORM", "minimal")
            Functions.addReadPermission(config['qtifw']['setup']['exe_path'])
        except Exception as exception:
            Functions.printFailMessage(message, exception)
            sys.exit()
        else:
            Functions.printSuccessMessage(message)
    else:
        message = "No preparation needed for os '{0}'".format(os_name)
        print(message)

def installQtInstallerFramework():
    message = "install QtInstallerFramework"
    try:
        config = Project.Config()
        Functions.installSilently(
            installer=config['qtifw']['setup']['exe_path'],
            silent_script=config['scripts']['silent_install']
        )
    except Exception as exception:
        Functions.printFailMessage(message, exception)
        sys.exit()
    else:
        Functions.printSuccessMessage(message)

def installerConfigXml():
    message = "create config.xml content"
    try:
        config = Project.Config()
        os_name = config['os']['name']
        app_name = config['app']['name']
        if os_name == 'osx':
            target_dir = '@ApplicationsDir@/{0}'.format(app_name)
        elif os_name == 'windows':
            target_dir = '@ApplicationsDir@\\{0}'.format(app_name)
        elif os_name == 'linux':
            target_dir = '@HomeDir@/{0}'.format(app_name)
        else:
            Functions.printFailMessage("Unsupported os '{0}'".format(os_name))
            sys.exit()
        pydict = {
            'Installer': {
                'Name': config['app']['name'],
                'Version': config['release']['version'],
                'Title': '{0} {1}'.format(config['app']['name'], config['app']['installer']['name_suffix']),
                'Publisher': config['app']['name'],
                'ProductUrl': config['app']['url'],
                'StartMenuDir': config['app']['name'],
                'TargetDir': target_dir,
                'MaintenanceToolName': '{0}{1}'.format(config['app']['name'], 'Uninstaller'),
                'ControlScript': config['installer']['config_control_script']['name'],
                'InstallActionColumnVisible': 'false',
                'AllowSpaceInPath': 'true',
            }
        }
        raw_xml = dicttoxml.dicttoxml(pydict, root=False, attr_type=False)
        pretty_xml = xml.dom.minidom.parseString(raw_xml).toprettyxml()
        #raw_xml = html.fromstring(raw_xml)
        #raw_xml = etree.tostring(raw_xml, xml_declaration=False, encoding='unicode', pretty_print=True)#.decode()
    except Exception as exception:
        Functions.printFailMessage(message, exception)
        sys.exit()
    else:
        Functions.printSuccessMessage(message)
        return pretty_xml

def installerPackageXml():
    message = "create package.xml content"
    try:
        config = Project.Config()
        pydict = {
            'Package': {
                'DisplayName': config['app']['name'],
                'Description': config['app']['description'],
                'Version': config['release']['version'],
                'ReleaseDate': datetime.datetime.strptime(config['release']['date'], "%d %b %Y").strftime("%Y-%m-%d"),
                'Default': 'true',
                'Essential': 'true',
                'ForcedInstallation': 'true',
                #'Licenses': {
                #    'License': {
                #        'name': "GNU General Public License Version 3",
                #        'file': "LICENSE"
                #    }
            	#	<License name="GNU General Public License Version 3" file="LICENSE" /> # SHOULD BE IN THIS FORMAT
                #}
            }
        }
        raw_xml = dicttoxml.dicttoxml(pydict, root=False, attr_type=False)
        pretty_xml = xml.dom.minidom.parseString(raw_xml).toprettyxml()
    except Exception as exception:
        Functions.printFailMessage(message, exception)
        sys.exit()
    else:
        Functions.printSuccessMessage(message)
        return pretty_xml

def createInstallerSourceDir():
    message = "create installer source directory"
    try:
        config = Project.Config()
        Functions.createFile(path=config['installer']['config_xml_path'], content=installerConfigXml())
        Functions.copyFile(source=config['installer']['config_control_script']['path'], destination=config['installer']['config_dir_path'])
        Functions.createFile(path=config['installer']['package_xml_path'], content=installerPackageXml())
        Functions.copyFile(source=config['installer']['package_install_script']['path'], destination=config['installer']['packages_meta_path'])
        Functions.copyFile(source=config['app']['license']['file_path'], destination=config['installer']['packages_meta_path'])
        Functions.createDir(config['installer']['packages_data_path'])
        Functions.moveDir(source=config['app']['freezed']['path'], destination=config['installer']['packages_data_path'])
        Functions.moveDir(source=config['project']['subdirs']['examples']['path'], destination=config['installer']['packages_data_path'])
    except Exception as exception:
        Functions.printFailMessage(message, exception)
        sys.exit()
    else:
        Functions.printSuccessMessage(message)

def createInstallerFile():
    message = "create installer file"
    try:
        config = Project.Config()
        Functions.run(
            config['qtifw']['binarycreator_path'],
            '--verbose',
            '--offline-only',
            '-c', config['installer']['config_xml_path'],
            '-p', config['installer']['packages_dir_path'],
            '-t', config['qtifw']['installerbase_path'],
            config['app']['installer']['exe_path']
        )
    except Exception as exception:
        Functions.printFailMessage(message, exception)
        sys.exit()
    else:
        Functions.printSuccessMessage(message)

if __name__ == "__main__":
    Functions.printTitle('Create Installer')
    downloadQtInstallerFramework()
    osDependentPreparation()
    installQtInstallerFramework()
    createInstallerSourceDir()
    createInstallerFile()
