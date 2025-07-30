"""
program.py: Setup flash environment.
            This file is subject to the terms and conditions defined in file 'LICENCE.md', which is part of this source
            code package.
"""

import os
import json
import datetime
try:
    from avr.lib.avrdude import AvrProgrammer
except (ModuleNotFoundError, ImportError):
    from lib.avrdude import AvrProgrammer

__author__    = "Nuno Vicente"
__copyright__ = "Copyright 2025 OceanScan - Marine Systems & Technology, Lda."
__credits__   = "Ricardo Martins, Renato Campos"


class Program:
    def __init__(self, firmware):
        self._firmware_path = firmware
        self._boards = os.listdir(self._firmware_path)
        self._boards.remove('.svn')
        self._board_ver = None
        self._firmware_ver = None

    def _check_versions(self, board, b_ver, f_ver):
        """Catch the latest version of board and firmware, if not passed by argument."""
        # Board version
        board_path = os.path.join(self._firmware_path, board)
        board_versions = os.listdir(board_path)
        
        if b_ver is None:
            if len(board_versions) < 1:
                raise RuntimeError('\nError: No board versions available\n')
            else:
                self._board_ver = max(board_versions)
        else:
            self._board_ver = b_ver

        # Firmware version
        if f_ver is None:
            firmware_path = os.path.join(board_path, self._board_ver)
            firmware_versions = os.listdir(firmware_path)

            if len(firmware_versions) < 1:
                raise RuntimeError('\nError: No firmware versions available.\n')
            else:
                self._firmware_ver = max(firmware_versions)
        else:
            self._firmware_ver = f_ver

    def list_boards(self):
        """Print available boards to flash."""
        print()
        for board in self._boards:
            print('├─ %s' % board)

            board_path = os.path.join(self._firmware_path, board)
            board_versions = os.listdir(board_path)

            for board_ver in board_versions:
                print('│   └── %s' % board_ver)

                firmware_path = os.path.join(board_path, board_ver)
                if not (os.path.isdir(firmware_path)): continue
                firmware_versions = os.listdir(firmware_path)

                for firmware_ver in firmware_versions:
                    print('│       └── %s' % firmware_ver)

        print()

    def program(self, author, board, board_ver, firmware_ver, inventory_number, port, report):
        """Flash board routine."""
        self._check_versions(board, board_ver, firmware_ver)

        full_path = os.path.join(self._firmware_path, board, self._board_ver, self._firmware_ver)

        if not os.path.exists(full_path):
            print('\nWrong options. Please choose from the list below:')
            self.list_boards()
            raise RuntimeError

        manifest_path = os.path.join(self._firmware_path, board, self._board_ver, self._firmware_ver, "manifest.json")
        manifest = json.load(open(manifest_path, "r"))

        # Flash board.
        avrp = AvrProgrammer(author, full_path, manifest, board, self._board_ver, self._firmware_ver, inventory_number, port)
        avrp.flash()

        # Report
        if report:
            print('\n==================================================\nGenerating report...\n\n')
            output_file = '%s_%04d_Setup_Certificate_%s.pdf' % (board, int(inventory_number), datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
            avrp.generate_certificate_pdf(output_file)
            print('Done\n')

            print('\n==================================================\nSaving to Baltico...\n\n')
            avrp.save2samba()
