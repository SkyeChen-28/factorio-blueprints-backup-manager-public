import os
import hashlib
import shutil

import pandas as pd

'''
Migrates my Factorio backups to a different folder, removes duplicates
'''

def hash_file(filepath: str, BUFF_SIZE: int = 2**16) -> str:
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
        sha256 = hashlib.sha256(data)
        
        while data:
            
            sha256.update(data)
            data = fp.read(BUFF_SIZE)
            
    return sha256.hexdigest()
            

def main():
    
    # Define directories to migrate between
    src = 'backups'
    dst = 'old_backups'
    
    # Initialize a dict
    filehash_dict = {'filename': [], 'hash': []}
    
    # Iterate through all the files and store their hash to determine which are dups
    for filepath in os.listdir(src):
        filehash_dict['filename'].append(filepath)
        filehash_dict['hash'].append(hash_file(f'{src}/{filepath}'))
        
    df = pd.DataFrame(filehash_dict)   
    df = df.drop_duplicates(subset='hash')

    # Migrate the dedup'd files to dst
    for filepath in df['filename']:
        shutil.copyfile(f'{src}/{filepath}', f'{dst}/{filepath}')
    

if __name__ == "__main__":
    main()
