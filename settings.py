# Django settings for zt project.
import logging
import os
os.environ['LANG'] = 'en_US.UTF-8'
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
#    'default': {
#        'ENGINE': 'sql_server.pyodbc', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': 'zt',                      # Or path to database file if using sqlite3.
#        'USER': 'sa',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '192.168.101.73',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '1433',                      # Set to empty string for default. Not used with sqlite3.
#    }
     'default': {
         'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
         'NAME': 'zt2',                      # Or path to database file if using sqlite3.
         'USER': 'wangjian2254',                      # Not used with sqlite3.
         'PASSWORD': '05992254wj',                  # Not used with sqlite3.
         'HOST': 'testdbinstance.cgkvyl8jtz2d.ap-northeast-1.rds.amazonaws.com',                      # Set to empty string for localhost. Not used with sqlite3.
         'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
     }
   #'default': {
   #        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
   #        'NAME': 'zt.db',                      # Or path to database file if using sqlite3.
   #        'USER': 'root',                      # Not used with sqlite3.
   #        'PASSWORD': '123456',                  # Not used with sqlite3.
   #        'HOST': '69.16.97.123',                      # Set to empty string for localhost. Not used with sqlite3.
   #        'PORT': '3306',                      # Set to empty string for default. Not used with sqlite3.
   #    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'static').replace('\\','/')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g9sdfwchq!bcrb$*^qlqh-sao&zaj5+=4^(+uf1%ue!pqsd0l#'

CACHE_BACKEND = 'db://cache_data/?timeout=300&max_entries=5000'
#CACHE_BACKEND = 'locmem:///?timeout=30&max_entries=5000'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'zt.urls'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'zt.ztmanage',
)

DDGENZONG={}

#LEVELS = {'debug': logging.DEBUG,
#          'info': logging.INFO,
#          'warning': logging.WARNING,
#          'error': logging.ERROR,
#          'critical': logging.CRITICAL}
#level = LEVELS.get('debug',logging.NOTSET)
#logging.basicConfig(level = level)
#
#
#logging.basicConfig(
#                level = logging.INFO,
#                format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s',
#                )
logging.basicConfig(
   level = logging.ERROR,
   format = '%(asctime)s %(levelname)s %(module)s.%(funcName)s Line:%(lineno)d %(message)s'
)