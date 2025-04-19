import os

def list_files_recursive(folder):
    file_list = []
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            file_list.append(os.path.join(dirpath, f))
    return file_list