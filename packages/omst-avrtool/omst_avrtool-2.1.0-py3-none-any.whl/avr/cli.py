#!/usr/bin/python3
"""
cli.py: Client to flash AVR boards.
        This file is subject to the terms and conditions defined in file 'LICENCE.md', which is part of this source code package.
"""

import os
import argparse
import subprocess
from appdirs import AppDirs
import shutil

# Use a cleaner import approach
from avr.lib.program import Program
from avr.lib.credentials import get_credentials
from avr import __version__
from smb.SMBConnection import SMBConnection
import tempfile

__author__    = "Nuno Vicente"
__copyright__ = "Copyright 2025 OceanScan - Marine Systems & Technology, Lda."
__credits__   = "Ricardo Martins, Renato Campos"

APP_NAME = 'omst-avrtool'
APP_VENDOR = 'OMST'
APP_VERSION = __version__

SAMBA_SHARE = '//192.168.61.1/firmware'

def mount_firmware_share(firmware_path):
    """Access the firmware share without requiring sudo permissions."""
    # Create directory if it doesn't exist
    os.makedirs(firmware_path, exist_ok=True)
    
    # Get credentials from user or environment
    username, password = get_credentials("firmware")
    
    # Parse server address from SAMBA_SHARE
    server_ip = SAMBA_SHARE.split('/')[2]
    share_name = SAMBA_SHARE.split('/')[3]
    
    try:
        # Create SMB connection
        conn = SMBConnection(username, password, "omst-avrtool", server_ip, use_ntlm_v2=True)
        if not conn.connect(server_ip, 445):
            raise RuntimeError('\nError connecting to Samba share.\n')
        
        print(f"Connected to {server_ip}, downloading files to {firmware_path}")
        
        # Clear the destination directory but keep it
        for item in os.listdir(firmware_path):
            item_path = os.path.join(firmware_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        
        # Download all files and directories recursively
        download_directory(conn, share_name, '/', firmware_path)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error accessing share: {e}")
        return False

def download_directory(conn, share_name, remote_dir, local_dir):
    """Recursively download a directory from SMB share."""
    # List contents of the directory
    file_list = conn.listPath(share_name, remote_dir)
    
    # Process each file/directory
    for item in file_list:
        # Skip . and ..
        if item.filename in ['.', '..']:
            continue
        
        remote_path = remote_dir + '/' + item.filename if remote_dir != '/' else '/' + item.filename
        local_path = os.path.join(local_dir, item.filename)
        
        if item.isDirectory:
            # Create local directory
            os.makedirs(local_path, exist_ok=True)
            # Recursively download contents
            download_directory(conn, share_name, remote_path, local_path)
        else:
            # Download file
            with open(local_path, 'wb') as file_obj:
                conn.retrieveFile(share_name, remote_path, file_obj)


def handler_checkout(res, folder, p):
    if mount_firmware_share(folder):
        print('\nSuccess: checkout completed to', folder, '\n')
    else:
        print('\nError: checkout failed\n')

def handler_update(res, folder, p):
    if mount_firmware_share(folder):
        print('\nSuccess: update completed to', folder, '\n')
    else:
        print('\nError: update failed\n')

def handler_programmers(res, folder, p):
    if not subprocess.call(['avrdude', '-c', '?'], stderr=subprocess.STDOUT, universal_newlines=True):
        print('\n Error finding avrdude.\n')


def handler_flash(res, folder, p):
    if not os.path.exists(folder):
        print("Firmware folder not found.")
        print("Please checkout the firmware folder from Samba.")
    else:
        prg = Program(folder)

        if res.l:
            prg.list_boards()

        elif res.b and not res.no_report:
            res.a = None
            res.n = None
            prg.program(res.a, res.b, res.o, res.f, res.n, res.p, res.no_report)

        elif res.a and res.b and res.n:
            prg.program(res.a, res.b, res.o, res.f, res.n, res.p, res.no_report)

        else:
            p.print_help()
            print()
            if not res.a and res.no_report:
                print('avr-scrt-cli.py flash: error: the following arguments are required: -a')
            if not res.b:
                print('avr-scrt-cli.py flash: error: the following arguments are required: -b')
            if not res.n and res.no_report:
                print('avr-scrt-cli.py flash: error: the following arguments are required: -n')
            print()


def main():
    app_dirs = AppDirs(APP_NAME, APP_VENDOR, version=APP_VERSION)

    if not os.path.exists(app_dirs.user_data_dir):
        os.makedirs(app_dirs.user_data_dir)

    firmware_path = os.path.join(app_dirs.user_data_dir, 'firmware')

    # Option parser.
    parser = argparse.ArgumentParser(prog='avr-scrt-cli.py', description='Tool to flash AVR supported boards.')
    subparsers = parser.add_subparsers()

    # Checkout sub-parser.
    checkout_parser = subparsers.add_parser('checkout', description='Checkout firmware folder from baltco.')
    checkout_parser.set_defaults(func=handler_checkout)

    # Update sub-parser.
    update_parser = subparsers.add_parser('update', description='Update firmware folder from baltico.')
    update_parser.set_defaults(func=handler_update)

    # List available programmers.
    prog_parser = subparsers.add_parser('programmers', description='List all available programmers')
    prog_parser.set_defaults(func=handler_programmers)

    # Flash sub-parser.
    flash_parser = subparsers.add_parser('flash', description="Flash board's firmware.")
    flash_parser.set_defaults(func=handler_flash)
    flash_parser.add_argument('-l', action='store_true', required=False, help='List available boards and firmware '
                                                                              'to flash.')
    flash_parser.add_argument('-a', required=False, help='Author of the operation.')
    flash_parser.add_argument('-b', required=False, help='Board to be flashed.')
    flash_parser.add_argument('-o', required=False, default=None, help='Board version. [default=latest version]')
    flash_parser.add_argument('-f', required=False, default=None, help='Firmware version. [default=latest version]')
    flash_parser.add_argument('-n', required=False, help='Inventory number.')
    flash_parser.add_argument('-p', required=False, default='usb', help='AVRdude programmer port. [default=usb]')
    flash_parser.add_argument('--no-report', action='store_false', required=False,
                              help='Skips the report generation for a flash only mode. This mode only requires -b arg.')

    # Parsing arguments.
    results = parser.parse_args()
    if not vars(results):
        parser.print_help()
    else:
        try:
            results.func(results, firmware_path, flash_parser)
        except RuntimeError as err:
            print(err)


if __name__ == '__main__':
    main()
