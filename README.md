# factorio-blueprints-backup-manager-public
 This program works with your OS's task scheduler to regularly backup your Factorio blueprints

## Usage

```
FactorioBlueprintBackupManager.py [-h] [-c] [-b BLUEPRINTS_LOCATION] [-n N] [-l] backups_folder
```

A script that backs up your Factorio blueprints. Best used with a task scheduler.

positional arguments:
  backups_folder        The folder to back up your blueprints to.

options:
  -h, --help            show this help message and exit
  -c, --create-folder-if-missing
                        Creates the backup folder if it is missing
  -b BLUEPRINTS_LOCATION, --blueprints-location BLUEPRINTS_LOCATION
                        The location of your Factorio blueprints folder.
  -n N                  The maximum number of backups to keep. Set to 0 to keep an unlimited number
  -l, --toggle-logging  Toggles whether log files are created