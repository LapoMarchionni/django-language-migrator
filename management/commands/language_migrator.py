from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from django.utils.translation import ugettext
from sys import stdout
import os
import os.path
import re
import sys
import py_compile
from distutils import dir_util


class Command(BaseCommand):

    args = 'Language'
    help = 'Translate all html and py files in your project to a selected language from a po file'

    def handle(self, *args, **options):

        def query_yes_no(question):
            valid = {"yes": True, "y": True,
                     "ye": True, "no": False, "n": False}
            while True:
                sys.stdout.write(question)
                choice = raw_input().lower()
                if choice in valid:
                    return valid[choice]
                else:
                    return False

        def get_files():
            counter_html, counter_py = 0, 0
            directories = {}
            for root, dirs, files in os.walk('.'):
                accepted_files = []
                if 'migrations' not in root and 'django_language_migrator' not in root:
                    for file in files:
                        if file.endswith('.html'):
                            accepted_files.append(file)
                            counter_html += 1
                        elif file.endswith('.py'):
                            accepted_files.append(file)
                            counter_py += 1
                    if len(accepted_files) != 0:
                        directories[root] = accepted_files
            return counter_html, counter_py, directories

        def translate_file(path):
            with open(path, 'r+') as f:
                text = f.read().decode('utf-8')
                if file.endswith('.py'):
                    r = r'gettext.*?["|\'](.+?)["|\']\s?\)'
                    strings = re.findall(r, text)
                else:
                    r = r'\%\s?trans\s?["|\'](.+?)["|\']\s?\%'
                    strings = re.findall(r, text)

                if len(strings) != 0:
                    for string in strings:
                        try:
                            finder = r'["|\']' + re.escape(string) + r'["|\']'
                            apex_string = re.search(finder, text).group()
                            text = re.sub(re.escape(apex_string),
                                          '"' + ugettext(string) + '"', text)
                        except:
                            pass
                    f.seek(0)
                    f.write(text.encode('utf-8'))
                    f.truncate()
                if file.endswith('.py'):
                    py_compile.compile(path, doraise=True)

        try:
            lang = args[0]
            translation.activate(lang)
        except:
            print 'Insert a valid language from your local directories or type help'
            return

        counter_html, counter_py, directories = get_files()
        print 'Found %s files across %s directories [%s .html and %s .py]\n' % (counter_html + counter_py, len(directories), counter_html, counter_py)
        if query_yes_no('These files will be modified, are you sure? ') == False:
            return

        print 'Backupping project folder...'
        dir_util.copy_tree('.', './mig_bkup_dta')

        error_files = []
        dir_count = 0
        for root in directories:
            dir_count += 1
            file_count = 0
            for file in directories[root]:
                path = root + '/' + file
                try:
                    translate_file(path)
                except Exception as e:
                    error_files.append(path)
                file_count += 1
                stdout.write("\r[%s of %s]\tTranslated %s of %s \t\t%s" % (
                    dir_count, len(directories), file_count, len(directories[root]), root))
                stdout.flush()
            stdout.write('\n')

        if len(error_files) != 0:
            print 'There were %s errors with these files: \n%s' % (len(error_files), '\n'.join(error_files))
            print 'Reverting this files from backup...'
            for file_path in error_files:
                print file_path

        if query_yes_no('Translation done, do you want to revert to the backup data? '):
            dir_util.copy_tree('./mig_bkup_dta', '.')
            print 'Reverted to original state'
        if query_yes_no('Do you want to keep the backup? '):
            dir_util.remove_tree('./mig_bkup_dta')
        else:
            print 'Backup saved in folder /mig_bkup_dta in your project folder'
        print 'Done'
