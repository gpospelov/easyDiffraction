#!/usr/bin/env python3

import os, sys
import ast
import subprocess
import zipfile
import Variables

var = Variables.VarsConfig()

# No code signing needed for linux
if var.os_name == 'linux': exit()

# Passwords
passwords_dict = ast.literal_eval(sys.argv[1]) if len(sys.argv) > 1 else {'osx':'', 'windows':'', 'zip':''}
certificate_password = passwords_dict[var.os_name].replace('\\', '')
zip_password = passwords_dict['zip']

# Unzip certificates
print('\n***** Unzip certificates')
with zipfile.ZipFile(var.certificates_zip_path) as zf:
    zf.extractall(path=var.certificates_dir_path, pwd=bytes(zip_password, 'utf-8'))

# Sign code
if (var.os_name == 'osx'):
    # https://gist.github.com/curiousstranger/309035
    # https://apple.stackexchange.com/questions/242795/command-line-keychain-access-not-showing-any-results
    # https://stackoverflow.com/questions/39868578/security-codesign-in-sierra-keychain-ignores-access-control-settings-and-ui-p
    keychain_name = 'codesign.keychain'
    keychain_password = 'password'
    identity = 'Developer ID Application: European Spallation Source Eric (W2AG9MPZ43)'

    print('\n***** Create keychain') # security create-keychain -p 'password' build.keychain # security delete-keychain build.keychain
    args = ['security', 'create-keychain', '-p', keychain_password, keychain_name]
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** Set it to be default keychain')
    args = ['security', 'default-keychain', '-s', keychain_name] # security default-keychain -s build.keychain # security default-keychain -s login.keychain
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** List keychains') # security list-keychains
    args = ['security', 'list-keychains']
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** Unlock created keychain') # security unlock-keychain -p 'password' build.keychain
    args = ['security', 'unlock-keychain', '-p', keychain_password, keychain_name]
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** Import certificate to created keychain') # security import Certificates/ESS_cert_mac.p12 -k build.keychain -P '<certificate_password>' -T /usr/bin/codesign
    args = ['security', 'import', var.certificate_file_path, '-k', keychain_name, '-P', certificate_password, '-T', '/usr/bin/codesign']
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** Show certificates')
    args = ['security', 'find-identity', '-v'] # security find-identity -v
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** Allow codesign to access certificate key from keychain') # security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k 'password'
    args = ['security', 'set-key-partition-list', '-S', 'apple-tool:,apple:,codesign:', '-s', '-k', keychain_password]
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('***** Sign code with imported certificate') # codesign --deep --force --verbose --sign 'Developer ID Application: European Spallation Source Eric (W2AG9MPZ43)' dist/easyDiffractionInstaller.app
    args = ['codesign', '--deep', '--force', '--verbose', '--sign', identity, var.installer_exe_path] # --timestamp URL
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

elif (var.os_name == 'windows'):
    print('\n***** Paths')
    signtool_exe_path = os.path.join('C:', os.sep, 'Program Files (x86)', 'Windows Kits', '10', 'bin', 'x86', 'signtool.exe')
    print('signtool_exe_path:', signtool_exe_path)

    print('\n***** Import certificate')
    args = ['certutil.exe',
            #'-user', # "Current User" Personal store.
            '-p', certificate_password, # the password for the .pfx file
            '-importpfx', var.certificate_file_path # name of the .pfx file
            ]
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)

    print('\n***** Sign code with imported certificate')
    args = [signtool_exe_path, 'sign', # info - https://msdn.microsoft.com/en-us/data/ff551778(v=vs.71)
            #'/f', certificate_file_path, # signing certificate in a file
            #'/p', certificate_password, # password to use when opening a PFX file
            '/sm', # use a machine certificate store instead of a user certificate store
            '/d', var.project_name, # description of the signed content
            '/du', var.project_url, # URL for the expanded description of the signed content
            '/t', 'http://timestamp.digicert.com', # URL to a timestamp server
            '/debug',
            '/v', # display the verbose version of operation and warning messages
            var.installer_exe_path
            ]
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)