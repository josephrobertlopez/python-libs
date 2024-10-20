import os
import sys

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):  # Running in a PyInstaller bundle
        base_path = sys._MEIPASS  # PyInstaller's temp folder
    else:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)
