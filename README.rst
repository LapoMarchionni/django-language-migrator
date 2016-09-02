# django-language-migrator
Check every .py and .html files in every directory of your django project and convert strings inside `{% trans "..." %}` tags or `gettext("...")` functions (and its derivated) to a selected language from a .po file.

Not compatible with **Python 3**

Add `django-language-migrator` to the installed apps
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rosetta',
    ...
    'django-language-migrator'
]
```
Start from your app directory as a Django command:
```
python manage.py language_migrator [language]
```
Where `[language]` is a valide language code for which you own the relative .po file. Example:
```
python manage.py lanugage_migrator en-US
```
A project backup will be created inside `./mig_bkup_data` inside your project root folder