#!/usr/bin/env python3

import argparse as ap
import os

from src.Manager import Manager

def main():
    
    # Initialize program's argparse
    parser = ap.ArgumentParser(
        description='A script that backs up your Factorio blueprints. Best used with a task scheduler.'
                              )
    _APPDATA = os.getenv('APPDATA')
    
    # Define the arguments
    parser.add_argument('backups_folder',
        help='The folder to back up your blueprints to.',
    )
    parser.add_argument(
        '-c', '--create-folder-if-missing',
        help='Creates the backup folder if it is missing',
        default=True,
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '-b', '--blueprints-location',
        help='The location of your Factorio blueprints folder.',
        default=f'{_APPDATA}\\Factorio\\blueprint-storage.dat',
        required=False
    )
    parser.add_argument(
        '-n',
        help='The maximum number of backups to keep. Set to 0 to keep an unlimited number',
        default=30,
        required=False,
        type=int
    )
    parser.add_argument(
        '-l', '--toggle-logging',
        help='Toggles whether log files are created',
        default=False,
        required=False,
        action='store_true'
    )
    
    # Parse the arguments
    args = parser.parse_args()
    backups_folder = args.backups_folder
    create_folder_if_missing = args.create_folder_if_missing
    blueprints_location = args.blueprints_location
    n = args.n
    toggle_logging = args.toggle_logging
    
    backupManager = Manager(backups_folder=backups_folder,
                            create_folder_if_missing=create_folder_if_missing,
                            blueprints_location=blueprints_location,
                            n=n,
                            toggle_logging=toggle_logging)
    if not backupManager.alreadyBackedUp():
        backupManager.backupFile()
        backupManager.cleanUp()


if __name__ == "__main__":
    main()
    