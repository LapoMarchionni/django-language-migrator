from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from django.utils.translation import ugettext
from sys import stdout
import os, os.path
import re

class Command(BaseCommand):

	args = 'Language'
	help = 'Translate all html and py files in your project to a selected language from a po file'

	def handle(self, *args, **options):

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
							text = re.sub(re.escape(apex_string), '"' + ugettext(string) + '"', text)
						except:
							pass
					f.seek(0)
					f.write(text.encode('utf-8'))
					f.truncate()

		try:
			lang = args[0]
			translation.activate(lang)
		except:
			print 'Insert a valid language from your local directories or type help'
			return

		counter_html, counter_py, directories = get_files()
		print 'Found %s html files and %s py files across %s directories' % (counter_html, counter_py, len(directories))

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
					error_files.append(path + ' Error: ' + str(e))
				file_count += 1
				stdout.write("\r[%s of %s]\tTranslated %s of %s \t\t%s" % (dir_count, len(directories), file_count, len(directories[root]), root))
				stdout.flush()
			stdout.write('\n')

		if len(error_files) != 0:
			print 'There were %s errors with these files: \n%s' %(len(error_files), '\n'.join(error_files))
