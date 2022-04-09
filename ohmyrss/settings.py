
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VISITOR_FEEDS = [512, 1, 3, 4, 5, 261, 13, 14, 397, 20, 1046, 536, 163, 420, 38, 424, 41, 558, 47, 179, 69, 1482, 208,
                 468, 222, 223, 227, 104, 1393, 4853, 118, 504, 251]
USER_DEFAULT_FEEDS = [1, 2, 3, 7, 20]

# mpwx third party hosts
# ERSHICIMI_HOST = 'ershicimi.com'
QNMLGB_HOST = 'qnmlgb.tech'
# WEMP_HOST = 'wemp.app'
# CHUANSONGME_HOST = 'chuansongme.com'
# ANYV_HOST = 'anyv.net'

# MPWX_HOST = 'mp.weixin.qq.com'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'this is a secret'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    '192.168.1.5',
    'localhost',
    'ohmyrss.com',
    'www.ohmyrss.com',
]

# Application definition

INSTALLED_APPS = [
    'django_crontab',
    # 'django_rq',
    'web.apps.WebConfig',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'web.middlewares.StatsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ohmyrss.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'tmpl')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'ohmyrss.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

WHOOSH_IDX_DIR = os.path.join(BASE_DIR, 'whoosh')

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRONJOBS = [
   ('1 5 * * 0,2,4,6', 'web.tasks.update_all_atom_cron'),
   ('20 2 * * 1,3,5', 'web.tasks.update_all_podcast_cron'),
   ('11 3 * * *', 'web.tasks.archive_article_cron'),
   ('31 4 * * *', 'web.tasks.build_whoosh_index_cron'),
   ('1 3 * * *', 'web.tasks.cal_site_ranking_cron'),
   ('13 3 * * *', 'web.tasks.cal_user_ranking_cron'),
]
CRONTAB_LOCK_JOBS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/assets/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
]

HTML_DATA2_DIR = os.path.join(BASE_DIR, "dat")

CRAWL_FLAG_DIR = os.path.join(HTML_DATA2_DIR, "crawl")

# redis service
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

# for web use db
REDIS_WEB_DB = 1
# for async job db
# REDIS_RQ_DB = 2

# RQ_QUEUES = {
#     'default': {
#         'HOST': REDIS_HOST,
#         'PORT': REDIS_PORT,
#         'DB': REDIS_RQ_DB,
#         'DEFAULT_TIMEOUT': 1200,
#     },
# }

# page view count, thumb count, open page count
REDIS_VIEW_KEY = 'VIEW/%s'

# register user count
REDIS_REG_KEY = 'REG/%s'

# api response time
REDIS_API_KEY = 'API/ALL'
REDIS_API_AVG_KEY = 'API/AVG/%s/%s'
REDIS_API_TOTAL_KEY = 'API/TOTAL/%s/%s'
REDIS_API_COUNT_KEY = 'API/COUNT/%s/%s'

# for dashboard statistics
REDIS_WEEK_KEY = 'WEEK/%s'
REDIS_VISIT_KEY = 'VISIT/%s/%s'
REDIS_UV_ALL_KEY = 'UV/ALL/%s'
REDIS_UV_NEW_KEY = 'UV/NEW/%s'

# http referer
REDIS_REFER_DAY_KEY = 'REFER/DAY/%s'
REDIS_REFER_PV_DAY_KEY = 'REFER/%s/%s'

# user subscribe list
REDIS_USER_SUB_KEY = 'SUB/%s'

# user read article flag
REDIS_USER_READ_KEY = 'READ/%s/%s'

# active rss in 3 days
REDIS_ACTIVE_RSS_KEY = 'ACTIVE/%s'

REDIS_FEED_RANKING_KEY = 'FEED/RANKING'

# user visit every day record
REDIS_USER_VISIT_DAY_KEY = 'UVD/%s/%s'

REDIS_USER_STAR_KEY = 'STAR2/%s/%s'

REDIS_UPDATED_SITE_KEY = 'UPDATED/%s'

# db index cache
REDIS_ARTICLES_KEY = 'ARTICLES'
REDIS_SITE_ARTICLES_KEY = 'ARTICLES/%s'
REDIS_SITE_LASTID_KEY = 'LASTID/%s'
REDIS_SITES_LASTIDS_KEY = 'LASTIDS'

REDIS_ACTIVE_SITES_KEY = 'ACTIVE/SITES'

REDIS_USER_RANKING_KEY = 'USER/RANKING'
REDIS_INDEXED_KEY = 'INDEXED/%s/%s'

# site name and author alias config
REDIS_USER_CONF_SITE_NAME_KEY = 'CONF/SN/%s/%s'
REDIS_USER_CONF_SITE_AUTHOR_KEY = 'CONF/SA/%s/%s'

USER_SUBS_LIMIT = 50

USER_SITE_ARTICLES_LIMIT = 300
VISITOR_SITE_ARTICLES_LIMIT = 100

RECENT_DAYS = 14
MAX_ARTICLES = 600

# github OAuth
GITHUB_OAUTH_KEY = '4b40da1eb0585bf03dda'
GITHUB_OAUTH_SECRET = 'c985780931b223658064d3218095d916106238d7'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'my_info': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'info.log'),
            'formatter': 'verbose',
            'when': 'D',
            'interval': 1,
            'backupCount': 90,
        },
        'my_warn': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024,
            'filename': os.path.join(BASE_DIR, 'logs', 'warn.log'),
            'formatter': 'verbose',
            'backupCount': 100,
        },
        'my_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024,
            'backupCount': 100,
        },
        'django_warn': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024,
            'backupCount': 100,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_warn'],
            'level': 'INFO',
            'propagate': True,
        },
        'web': {
            'handlers': ['console', 'my_info', 'my_warn', 'my_error'],
            'level': 'INFO',
            'propagate': True,
        },
        # 'rq.worker': {
        #     'handlers': ['my_info', 'my_warn', 'my_error'],
        #     'level': 'INFO',
        #     'propagate': True,
        # },
    },
}
