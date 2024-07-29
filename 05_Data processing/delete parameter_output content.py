import os
import shutil

def delete_specific_files_in_folders(root_directory, folder_name, file_extensions):
    for root, dirs, files in os.walk(root_directory):
        for name in dirs:
            if name == folder_name:
                folder_path = os.path.join(root, name)
                for file in os.listdir(folder_path):
                    if file.endswith(tuple(file_extensions)):
                        file_path = os.path.join(folder_path, file)
                        print(f"Deleting file: {file_path}")
                        os.remove(file_path)

# Main directory containing subfolders
main_directory = r'c:\Users\User\Documents\Git Repository\logs'

# Specify the folder name to search for and file extensions to delete
folder_name_to_search = 'parameter_extraction'            # 'parameter_extraction' or 'fitting_parameters'
file_extensions_to_delete = ['csv', '.png']

delete_specific_files_in_folders(main_directory, folder_name_to_search, file_extensions_to_delete)