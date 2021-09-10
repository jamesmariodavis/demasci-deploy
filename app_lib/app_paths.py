import os

# infer path of current file
__this_file_location = os.path.dirname(os.path.abspath(__file__))
# infer path of root
ROOT_DIR = os.path.join(__this_file_location, os.pardir)

LIB_DIR = os.path.join(ROOT_DIR, 'app_lib')
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
LOCAL_CACHE_DIR = os.path.join(ROOT_DIR, 'cache')
LOCAL_FILE_DIR = os.path.join(ROOT_DIR, 'local_files')

# check that this file exists according to the logic above
if not os.path.exists(os.path.join(LIB_DIR, 'app_paths.py')):
    raise Exception()
