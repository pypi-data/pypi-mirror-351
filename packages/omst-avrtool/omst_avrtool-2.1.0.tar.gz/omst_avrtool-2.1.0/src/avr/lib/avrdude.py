"""
avrdude.py: AVRdude programmer manager.
            This file is subject to the terms and conditions defined in file 'LICENCE.md', which is part of this source
            code package.
"""


import os
import re
import subprocess
import datetime
import getpass
import socket
import textwrap
from time import sleep


try:
    from avr.lib import report
except (ModuleNotFoundError, ImportError):
    from lib import report

from avr.lib.credentials import get_credentials
# New imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from smb.SMBConnection import SMBConnection
import os

__author__    = "Nuno Vicente"
__copyright__ = "Copyright 2025 OceanScan - Marine Systems & Technology, Lda."
__credits__   = "Ricardo Martins, Renato Campos"


EXECUTABLE = "avrdude"
VERSION_PREFIX = "avrdude version"
SAMBA_SHARE = '//192.168.61.1/certificates'
MOUNT_POINT = '.local/share/avr/certificates'


class AvrProgrammer:
    def __init__(self, author, path,  manifest, board, board_version, firmware_version, inventory_number, port):
        """Initialise variables and miscellaneous."""
        self._author = author

        # Board misc.
        self._full_path = path
        self._manifest = manifest
        self._board_name = board
        self._board_version = board_version
        self._firmware_version = firmware_version
        self._inventory_code = board
        self._inventory_number = inventory_number
        self._avr_programmer = 'atmelice_pdi'  # Default programmer
        self._port = port

        # Version.
        self.version = None
        self._find_version()

        # Manifest info.
        self._mcu = None
        self._fuses = None
        self._memories = None
        self._prog_config = None
        self._prog_version = None
        self._read_manifest()

        # Programmer misc.
        self.output = []
        self._log = None
        self._prog_hw_version = None
        self._prog_fw_version = None
        self._prog_model = None
        self._prog_serial = None
        self._rate = None

        # Microcontroller misc.
        self._vtarget = None
        self._mcu_name = None
        self._mcu_signature = None

        self._report = None
        self._report_name = None

    def _find_version(self):
        """Find AVRDUDE version."""

        try:
            output = subprocess.check_output([EXECUTABLE, "-?"],
                                             stderr=subprocess.STDOUT,
                                             universal_newlines=True)
        except:
            raise RuntimeError("\nUnable to find a suitable AVRDUDE executable.\n")

        version = None
        lines = output.split('\n')
        for line in lines:
            if line.startswith(VERSION_PREFIX):
                parts = line.split(',')
                version = parts[0].replace(VERSION_PREFIX, "").strip()

        if version is None:
            raise RuntimeError("\nFailed to find AVRdude version.\n")

        self.version = version

    def _read_manifest(self):
        """Read manifest file."""
        self._mcu = self._manifest.get("mcu")
        self._fuses = self._manifest.get("fuses")
        self._memories = self._manifest.get("memories")
        self._prog_config = self._manifest.get("programmer_config", None)
        self._prog_version = self._manifest.get("programmer_version")


    def _parse_program_output(self, output):
        lines = output.split("\n")
        self.output += lines
        for line in lines:
            line = line.strip()

            # Vtarget.
            match = re.match(r"Vtarget\s*:\s*([0-9\.]+)", line)
            if match is not None:
                self._vtarget = match.group(1)

            # Programmer Hardware version.
            match = re.match(r"Hardware Version\s*:\s*(\w+)", line)
            if match is not None:
                self._prog_hw_version = match.group(1)
            if self._prog_hw_version is None:
                match = re.match(r"ICE hardware version\s*:\s*(\w+)", line)
                if match is not None:
                    self._prog_hw_version = match.group(1)

            # Programmer Firmware Version Number.
            match = re.match(r"Firmware Version Master\s*:\s*([0-9\.]+)", line)
            if match is not None:
                self._prog_fw_version = match.group(1)
            if self._prog_fw_version is None:
                match = re.match(r"ICE firmware version\s*:\s*([^$]+)", line)
                if match is not None:
                    self._prog_fw_version = match.group(1).strip()

            # Programmer model.
            match = re.match(r"Programmer Model\s*:\s*([\w|\s]+)", line)
            if match is not None:
                self._prog_model = match.group(1)
            if self._prog_model is None:
                match = re.match(r"Programmer Type\s*:\s*([\w|\s]+)", line)
                if match is not None:
                    self._prog_model = match.group(1)

            # Programmer serial.
            match = re.search(r"\s*serno:\s*([0-9]+)", line)
            if match is not None:
                self._prog_serial = match.group(1)
            if self._prog_serial is None:
                match = re.search(r"\s*Serial number\s*:\s*([^$]+)", line)
                if match is not None:
                    self._prog_serial = match.group(1)

            # MCU Name.
            match = re.match(r"AVR Part\s*:\s*(\w+)", line)
            if match is not None:
                self._mcu_name = match.group(1)

            # MCU signature.
            match = re.match(r"avrdude: Device signature\s*=\s*(\w+)", line)
            if match is not None:
                self._mcu_signature = match.group(1)

    def _get_avr_programmer(self):
        """Detect avr programmer."""
        print('Detecting AVR Programmers...')
        programmers = ['avrisp2', 'atmelice']
        founds = []
        tries = 0

        for prg in programmers:
            command = [EXECUTABLE, '-q', '-v', '-p', self._mcu, '-c', prg, '-P', self._port]

            try:
                subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
                founds.append(prg)
                print('Found %s.' % prg)
            except subprocess.SubprocessError as e:
                if 'AVR Part' in e.output:
                    founds.append(prg)
                    print('Found %s.' % prg)
                else:
                    tries += 1

        if tries >= len(programmers):
            raise RuntimeError('\nError: no programmer was found.')
        else:
            if len(founds) == 1:
                prg = founds[0]

                if 'atmelice' in prg:
                    if 'atxmega' in self._mcu:
                        prg = 'atmelice_pdi'    # for xmega mcu
                    elif 'atmega' in self._mcu:
                        prg = 'atmelice_isp'    # for mega mcu
                    else:
                        raise RuntimeError('\n\nError: no atmega or atxmega found.\n\n')
            else:
                print('Please choose which device you want to use:')
                for devices in zip(range(len(founds)), founds):
                    print('%i. %s' % devices)

                while True:
                    try:
                        choice = int(input(': '))

                        if choice not in range(len(founds)):
                            raise ValueError

                        break
                    except ValueError:
                        continue

                prg = founds[choice]
                if 'atmelice' in prg:
                    if 'atxmega' in self._mcu:
                        prg = 'atmelice_pdi'  # for xmega mcu
                    elif 'atmega' in self._mcu:
                        prg = 'atmelice_isp'  # for mega mcu
                    else:
                        raise RuntimeError('\n\nError: no atmega or atxmega found.\n\n')

        print('\n%s will be used for % s.\n' % (prg, self._mcu))
        sleep(0.5)
        self._avr_programmer = prg

    def _exec_avr(self, command, parse = False):
        """Call a subprocess to exec an avrdude command."""
        old_dir = os.getcwd()
        os.chdir(self._full_path)
        print(self._full_path)
        print('Executing: ', ' '.join(command))
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, input='y')
            if parse:
                self._parse_program_output(output)

        except subprocess.SubprocessError as e:
            raise RuntimeError('\n%s\n' % e.output)
        finally:
            os.chdir(old_dir)

        return output

    def flash(self):
        """Program fuses and memories of configured MCU."""
        self._get_avr_programmer()

        if 'atxmega' in self._mcu:
            self._rate = '1MHz'
        elif 'atmega' in self._mcu:
            self._rate = '8'
        else:
            raise RuntimeError('\n\nError placing a frequency.\n\n')

        # Write Fuses
        output = "===================================================================================================="
        output += "\nWrite Fuses:\n"
        output += "====================================================================================================\n"
        command = [EXECUTABLE, "-v", "-V", "-e", 
                "-B", self._rate,
                "-p", self._mcu,
                "-c", self._avr_programmer,
                "-P", self._port]

        if self._prog_config is not None:
            command += ['-C', '+' + self._prog_config]

        fuse_names = list(self._fuses.keys())
        fuse_names.sort()
        for fuse_name in fuse_names:
            command += ["-U", "%s:w:%s:m" % (fuse_name, self._fuses[fuse_name])]

        output += textwrap.fill(' '.join(command) + '\n\n\n', 100) + '\n'
        output += self._exec_avr(command, True)
        
        # Read Fuses
        output += "===================================================================================================="
        output += "\nRead Fuses\n"
        output += "====================================================================================================\n"
        command = [EXECUTABLE,
            "-B", self._rate,
            "-p", self._mcu,
            "-c", self._avr_programmer,
            "-P", self._port]

        if self._prog_config is not None:
            command += ['-C', '+' + self._prog_config]

        for fuse_name in fuse_names:
            command += ["-U", "%s:r:-:h" % fuse_name]

        output += textwrap.fill(' '.join(command) + '\n\n\n', 100) + '\n\n'
        output += self._exec_avr(command)

        for fuse_name in fuse_names:
            if self._fuses[fuse_name] == '0x00':
                self._fuses[fuse_name] = '0x0'
            if not 'avrdude: writing output file <stdout>\n%s' % self._fuses[fuse_name] in output:
                raise RuntimeError('\nFuse %s does not match.\n' % self._fuses[fuse_name])

        # Flash
        output += "===================================================================================================="
        output += "\nFlash\n"
        output += "====================================================================================================\n"
        command = [EXECUTABLE, "-e", 
                   "-B", self._rate,
                   "-p", self._mcu,
                   "-c", self._avr_programmer,
                   "-P", self._port]
        
        if self._prog_config is not None:
            command += ['-C', '+' + self._prog_config]

        memory_names = list(self._memories.keys())
        memory_names.sort()
        for memory_name in memory_names:
            command += ["-U", "%s:w:%s" % (memory_name, self._memories[memory_name])]

        output += textwrap.fill(' '.join(command) + '\n\n\n', 100) + '\n\n'
        output += self._exec_avr(command)

        print(output)
        self._log = output


    # New ReportLab code
    def generate_certificate_pdf(self, output_file):
        # Create document
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        self._report_name =  output_file
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title2_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Build document content
        elements = []
        
        # Add title
        elements.append(Paragraph(f"Certificate for {self._board_name}", title_style))
        elements.append(Spacer(1, 12))
        
        # Add details
        elements.append(Paragraph(f"General Information", title2_style))
        elements.append(Paragraph(f"Inventory Number: {self._inventory_number}", normal_style))
        elements.append(Paragraph(f"Service Computer: {getpass.getuser()}@{socket.gethostname()}", normal_style))
        elements.append(Paragraph(f"Operator: {self._author}", normal_style))
        elements.append(Paragraph(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Spacer(1, 12))

        # Add board information
        elements.append(Paragraph(f"Board Information", title2_style))
        elements.append(Paragraph(f"Model: {self._board_name}", normal_style))
        elements.append(Paragraph(f"Version: {self._board_version}", normal_style))
        elements.append(Paragraph(f"Firmware Version: {self._firmware_version}", normal_style))
        elements.append(Spacer(1, 12))

        # Add microcontroller information
        elements.append(Paragraph(f"Microcontroller Information", title2_style))
        elements.append(Paragraph(f"MCU Name: {self._mcu_name}", normal_style))
        elements.append(Paragraph(f"Signature: {self._mcu_signature}", normal_style))
        elements.append(Paragraph(f"Target Voltage: {self._vtarget}V", normal_style))
        elements.append(Spacer(1, 12))

        # Add programmer information
        elements.append(Paragraph(f"Programmer Information", title2_style))
        elements.append(Paragraph(f"Model: {self._prog_model}", normal_style))
        elements.append(Paragraph(f"Hardware Version: {self._prog_hw_version}", normal_style))
        elements.append(Paragraph(f"Firmware Version: {self._prog_fw_version}", normal_style))
        elements.append(Paragraph(f"Serial Number: {self._prog_serial}", normal_style))
        elements.append(Spacer(1, 12))

        # Add output section
        elements.append(Paragraph(f"Output", title2_style))
        elements.append(Paragraph(self._log.replace('\n', '<br />'), normal_style))
        elements.append(Spacer(1, 12))

        # Add footer
        elements.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Spacer(1, 12))
    
        # Build PDF
        doc.build(elements)

    def mount_firmware_share(self):
        """Access the firmware share without requiring sudo permissions."""
        # Parse server address from SAMBA_SHARE
        server_ip = SAMBA_SHARE.split('/')[2]
        share_name = SAMBA_SHARE.split('/')[3]
        
        # Get credentials from user or environment
        username, password = get_credentials("firmware")
        
        try:
            # Create SMB connection
            conn = SMBConnection(username, password, "omst-avrtool", server_ip, use_ntlm_v2=True)
            if not conn.connect(server_ip, 445):
                raise RuntimeError('\nError connecting to Samba share.\n')
            
            # Just test connection - actual file operations happen in save2samba
            print(f"Successfully connected to {server_ip}")
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error accessing share: {e}")
            raise RuntimeError('\nError connecting to Samba share.\n')

    def save2samba(self):
        """Save certificate to Samba share using SMBConnection."""
        print(f"Saving certificate {self._report_name} to network share")
        
        if not os.path.exists(self._report_name):
            raise RuntimeError(f"Certificate file {self._report_name} not found.")
        
        # Parse server address from SAMBA_SHARE
        server_ip = SAMBA_SHARE.split('/')[2]
        share_name = SAMBA_SHARE.split('/')[3]
        
        # Get credentials from user or environment
        username, password = get_credentials("firmware")
        
        try:
            # Create SMB connection
            conn = SMBConnection(username, password, "omst-avrtool", server_ip, use_ntlm_v2=True)
            if not conn.connect(server_ip, 445):
                raise RuntimeError('\nError connecting to Samba share.\n')
            
            # Create remote directory path
            num = '%04d' % int(self._inventory_number)
            remote_path = f"{self._board_name}/{num}"
            
            # Check if directory exists and create if needed
            try:
                conn.listPath(share_name, remote_path)
            except Exception:
                # Directory doesn't exist, create it
                parent_paths = remote_path.split('/')
                current_path = ""
                
                for path in parent_paths:
                    if path:
                        try:
                            if current_path:
                                current_path = f"{current_path}/{path}"
                            else:
                                current_path = path
                                
                            conn.listPath(share_name, current_path)
                        except Exception:
                            conn.createDirectory(share_name, current_path)
            
            # Upload the file
            file_name = os.path.basename(self._report_name)
            remote_file_path = f"{remote_path}/{file_name}"
            
            with open(self._report_name, 'rb') as file_obj:
                conn.storeFile(share_name, remote_file_path, file_obj)
            
            print(f"Successfully saved certificate to {server_ip}/{share_name}/{remote_file_path}")
            
            # Close connection and delete local file
            conn.close()
            os.remove(self._report_name)
            return True
            
        except Exception as e:
            print(f"Error saving to Samba share: {e}")
            raise RuntimeError(f"Samba Error.\n{str(e)}")
