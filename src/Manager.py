import shutil as su 
from datetime import datetime as dt
import os
import hashlib
import logging
from collections import namedtuple

from typing import List

_UNLIMITED_BACKUPS = 0
_DEFAULT_BUFF_SIZE = 2**16

class Manager:
    
    def __init__(self, 
                 backups_folder: str,
                 create_folder_if_missing: bool,
                 blueprints_location: str,
                 n: int,
                 toggle_logging: bool
                 ) -> None:
        
        self.create_folder_if_missing = create_folder_if_missing
        self.toggle_logging = toggle_logging
        self._datetimeFormat = '%Y-%m-%d_%H-%M-%S'
        
        # Perform validity checks
        
        if os.path.isdir(backups_folder):
            self.backups_folder = backups_folder
        elif self.create_folder_if_missing:
            os.makedirs(backups_folder, exist_ok=True)
            self.backups_folder = backups_folder
        else:
            raise FileNotFoundError(f'Could not find the `{backups_folder}` folder. If you want this program to create it, add a `-c` flag as an argument when using the command line terminal.')
            
        # Initialize the logger
        timestamp = dt.today().strftime(self._datetimeFormat)
        self.logs_folder = f'{backups_folder}/logs'
        if self.toggle_logging:
            self.log_file_path = f'{self.logs_folder}/FactorioBlueprintBackupManager_{timestamp}.log'
        else:
            self.log_file_path = None
        if not os.path.isdir(self.logs_folder):
            os.makedirs(self.logs_folder)
        logging.basicConfig(
            level=logging.INFO,
            filename=self.log_file_path,
            format='%(asctime)s [%(levelname)s]: %(message)s'
            )
        self.logging = logging
            
        if os.path.exists(blueprints_location):
            self.blueprints_location = blueprints_location
        else:
            err_msg = 'Could not locate your Factorio Blueprints file! Please check online to see the common locations where Factorio stores it\'s blueprints for you'
            self.logging.error(err_msg)
            raise FileNotFoundError(err_msg)
        
        if n >= 0:
            self.n = n
        else:
            err_msg = '`n` must be positive in order to store at least one backup!'
            self.logging.error(err_msg)
            raise ValueError(err_msg)
        
    def __hash_file(self, filepath: str, BUFF_SIZE: int = _DEFAULT_BUFF_SIZE) -> str:
        '''
        Returns the sha256 hash of a file in the form of a hexadecimal string

        Args:
            filepath (str): The path string to the file to hash
            BUFF_SIZE (int, optional): Specify a buffer to efficiently hash large files. Defaults to 2**16.

        Returns:
            str: The hexadecimal string representation of the sha256 hash of the file
        '''
        
        with open(filepath, mode='rb') as fp:
            
            # Initialize hashing function
            data = fp.read(BUFF_SIZE)
            sha256 = hashlib.sha256()
            
            while data:
                
                sha256.update(data)
                data = fp.read(BUFF_SIZE)
                
        return sha256.hexdigest()
        
    def alreadyBackedUp(self):
        '''
        Checks whether the current Blueprints file is a duplicate of any backed up files.
        '''
        
        blueprints_hash = self.__hash_file(self.blueprints_location)
        for filepath in os.listdir(self.backups_folder):
            filepath = f'{self.backups_folder}/{filepath}'
            if (not os.path.isdir(filepath)) and (blueprints_hash == self.__hash_file(filepath)):
                self.logging.info("File already backed up.")
                return True
        return False
          
    def backupFile(self):
        '''
        Backs up the current Blueprints file
        '''
        
        timestamp = dt.today().strftime(self._datetimeFormat)
        target_path = f'{self.backups_folder}/blueprint-storage_{timestamp}.dat'
        self.backupFileName = target_path
        
        su.copyfile(self.blueprints_location, target_path)
        self.logging.info(f"File `{target_path}` backed up.")
        
    def __extractDatetime(self, filename: str) -> dt:
        
        timestamp = dt.today().strftime(self._datetimeFormat)
        datetime_str = filename[:-len('.dat')]
        datetime_str = datetime_str[-len(timestamp):]
        
        return dt.strptime(datetime_str, self._datetimeFormat)
        
    def __executeCleanUp(self, folder_to_clean_up: str):
        
        # Clean up the folder
        filenames = [f for f in os.listdir(folder_to_clean_up)
                            if os.path.isfile(os.path.join(folder_to_clean_up, f))]
        number_of_files = len(filenames)
        number_files_to_remove = _UNLIMITED_BACKUPS if (self.n==_UNLIMITED_BACKUPS) else (number_of_files - self.n)
        
        if number_files_to_remove > 0:
            
            FileInfo = namedtuple('FileInfo', field_names=['datetime', 'filename'])
            fileInfoList = []
            
            for filename in filenames:
                file_datetime = self.__extractDatetime(filename)
                fileInfoList.append(FileInfo(datetime=file_datetime, filename=filename))
                
            fileInfoList.sort(key=lambda f: f.datetime, reverse=False)
            
            files_to_remove = fileInfoList[0:number_files_to_remove]
            for file_inf in files_to_remove:
                filename = file_inf.filename
                filepath_to_remove = f'{folder_to_clean_up}/{filename}'
                if not ((filepath_to_remove == self.backupFileName) or (filepath_to_remove == self.log_file_path)):
                    os.remove(filepath_to_remove)
                    logging.info(f'{filepath_to_remove} has been deleted.')
            
            self.logging.info(f'{number_files_to_remove} older files removed from `{folder_to_clean_up}/`.')
            
    def cleanUp(self):
        '''
        If number of backups exceeds `n`, then remove the oldest files until 
        the number of backups is equal to `n`.
        '''
        
        self.__executeCleanUp(self.backups_folder)
        self.__executeCleanUp(self.logs_folder)
