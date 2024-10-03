import sys, os, django

# Find the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#print(BASE_DIR)

os.chdir(BASE_DIR) # make everything relative to root

# this already added
# Add the project base directory to the sys.path
# This means the script will look in the base directory for any module imports
# Therefore you'll be able to import analysis.models etc
# sys.path.insert(0, BASE_DIR)
# print(sys.path)

# The DJANGO_SETTINGS_MODULE has to be set to allow us to access django imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dashboard.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# This is for setting up django
django.setup()

# notebook_dir = globals()['_dh'][0] # gets the path to the current notebook
# import os, sys
# os.chdir(os.path.join(notebook_dir, '../')) # make everything relative to root