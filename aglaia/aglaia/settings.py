"""
Django settings for aglaia project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b^jrfnul^@=#2@gu!8jxs9y#xz30!(uhol1f3h+o6uu!@$mr$w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

# import ldap
# from django_auth_ldap.config import LDAPSearch
#
# AUTHENTICATION_BACKENDS = (
# 	'django_auth_ldap.backend.LDAPBackend',
# 	'django.contrib.auth.backends.ModelBackend',
# )
# AUTH_LDAP_SERVER_URI = 'ldap://192.168.1.207:389'
# AUTH_LDAP_BIND_DN = 'CN=admin,DC=lsms,DC=com'
# AUTH_LDAP_BIND_PASSWORD = "lsms"
# AUTH_LDAP_USER_SEARCH = LDAPSearch("OU=People,DC=lsms,DC=com", ldap.SCOPE_SUBTREE, "(&(objectClass=person)(uid=%(user)s))")
# AUTH_LDAP_USER_ATTR_MAP = {
# 	"username": "uid",
# 	"password": "userPassword",
# 	"first_name": "givenName",
# 	"last_name": "sn",
# 	"email": "mail",
# }
# AUTH_LDAP_ALWAYS_UPDATE_USER = True



# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'account',
	'computing',
	'goods',
	'log',
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	# 'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'aglaia.urls'

WSGI_APPLICATION = 'aglaia.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
		# 'ENGINE': 'django.db.backends.mysql',
		# 'NAME': 'aglaia',
		# 'USER': 'root',
		# 'PASSWORD': 'root',
		# 'HOST': '127.0.0.1',
		# 'PORT': '3306',
	}
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

DEFAULT_CHARSET = 'utf-8'

FILE_CHARSET = 'utf-8'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)

# Template directories

TEMPLATE_DIRS = (
	os.path.join(BASE_DIR, 'templates'),
)

# Some redirect url

ROOT_ADDRESS = 'http://166.111.206.89/'

LOGIN_URL = '/account/signin/'

ACCOUNT_HOME_URL = '/account/'


# E-mail settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.163.com'

EMAIL_PORT = 25

EMAIL_HOST_USER = 'AglaiaSys@163.com'

EMAIL_HOST_PASSWORD = 'agsys123456'

EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SERVER_EMAIL = EMAIL_HOST_USER

EMAIL_AUTH_PREFIX = ROOT_ADDRESS + 'account/auth_email/'

USER_RETURN_MESSAGE = '申请归还'

USER_MISS_MESSAGE = '申请挂失'

SEND_MAIL_NOTIFY = True
