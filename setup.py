from distutils.core import setup
setup(
	name='html2markdown',
	py_modules=['html2markdown'],
	version='0.1.2',
	description='Conservatively convert html to markdown',
	author='dlon',
	author_email='dv.lnh.d@gmail.com',
	url='https://github.com/dlon/html2markdown',
	install_requires=[
		'beautifulsoup4'
	],
)