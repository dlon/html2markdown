"""html2markdown converts an html string to markdown while preserving unsupported markup."""
# TODO:
#	escape all characters (in _escapeCharacters. cf. https://daringfireball.net/projects/markdown/syntax#backslash)
#	implement standard <table> (i.e. without attributes)
import bs4
from bs4 import BeautifulSoup
import re

_supportedTags = (
	# NOTE: will be ignored if they have unsupported attributes (cf. _supportedAttributes)
	'blockquote',
	'p',
	'a',
	'h1','h2','h3','h4','h5','h6',
	'strong','b',
	'em','i',
	'ul','ol','li',
	'br',
	'img',
	'pre','code',
	'hr'
)
_supportedAttributes = (
	'a href',
	'a title',
	'img alt',
	'img src',
	'img title',
)

_inlineTags = (
	# these can be mixed with markdown (when unprocessed)
	# block tags will be surrounded by newlines and be unprocessed inside
	# (unless supported tag + supported attribute[s])
	'span',
	'strong','b',
	'em','i',
	'a',
	'img',
	'code'
)

def _supportedAttrs(tag):
	sAttrs = [attr.split(' ')[1] for attr in _supportedAttributes if attr.split(' ')[0]==tag.name]
	for attr in tag.attrs:
		if attr not in sAttrs:
			return False
	return True

def _recursivelyValid(tag):
	# not all tags require this property
	# requires: <blockquote><p style="...">asdf</p></blockquote>
	# does not: <div><p style="...">asdf</p></div>
	children = tag.find_all(recursive = False)
	for child in children:
		if not _recursivelyValid(child):
			return False
	if tag.name == '[document]':
		return True
	elif tag.name in _inlineTags:
		return True
	elif tag.name not in _supportedTags:
		return False
	if not _supportedAttrs(tag):
		return False
	return True

def _escapeCharacters(tag):
	'''non-recursively escape underlines and asterisks
	in the tag'''
	for i,c in enumerate(tag.contents):
		if type(c) != bs4.element.NavigableString:
			continue
		c.replace_with(c.replace('_','\\_').replace('*','\\*'))

def _breakRemNewlines(tag):
	'''non-recursively break spaces and remove newlines in the tag'''
	for i,c in enumerate(tag.contents):
		if type(c) != bs4.element.NavigableString:
			continue
		c.replace_with(re.sub(r' {2,}', ' ', c).replace('\n',''))

def _markdownify(tag, _listType=None, _blockQuote=False, _listIndex=1):
	'''recursively converts a tag into markdown'''
	children = tag.find_all(recursive=False)

	if tag.name == '[document]':
		for child in children:
			_markdownify(child)
		return

	if tag.name not in _supportedTags or not _supportedAttrs(tag):
		if tag.name not in _inlineTags:
			tag.insert_before('\n\n')
			tag.insert_after('\n\n')
		else:
			_escapeCharacters(tag)
			for child in children:
				_markdownify(child)
		return
	if tag.name not in ('pre', 'code'):
		_escapeCharacters(tag)
		_breakRemNewlines(tag)
	if tag.name == 'p':
		if tag.string != None:
			if tag.string.strip() == u'':
				# FIXME: leave only &nbsp;
				#tag.string = u'\xa0'
				return
		if not _blockQuote:
			tag.insert_before('\n\n')
			tag.insert_after('\n\n')
		else:
			tag.insert_before('\n')
			tag.insert_after('\n')
		tag.unwrap()

		for child in children:
			_markdownify(child)
	elif tag.name == 'br':
		tag.string = '  \n'
		tag.unwrap()
	elif tag.name == 'img':
		# FIXME: is this in the right place?
		alt = ''
		title = ''
		if tag.has_attr('alt'):
			alt = tag['alt']
		if tag.has_attr('title') and tag['title']:
			title = ' "%s"' % tag['title']
		tag.string = '![%s](%s%s)' % (alt, tag['src'], title)
		tag.unwrap()
	elif tag.name == 'hr':
		tag.string = '\n---\n'
		tag.unwrap()
	elif tag.name == 'pre':
		tag.insert_before('\n\n')
		tag.insert_after('\n\n')
		if tag.code:
			if not _supportedAttrs(tag.code):
				return
			for child in tag.code.find_all(recursive=False):
				if child.name != 'br':
					return
			# code block
			for br in tag.code.find_all('br'):
				br.string = '\n'
				br.unwrap()
			tag.code.unwrap()
			lines = unicode(tag).strip().split('\n')
			lines[0] = lines[0][5:]
			lines[-1] = lines[-1][:-6]
			if not lines[-1]:
				lines.pop()
			for i,line in enumerate(lines):
				line = line.replace(u'\xa0', ' ') # FIXME: should this be done by the client?
				lines[i] = '    %s' % line
			tag.replace_with(BeautifulSoup('\n'.join(lines), 'html.parser'))
		return
	elif tag.name == 'code':
		# inline code
		if children:
			return
		tag.insert_before('`` ')
		tag.insert_after(' ``')
		tag.unwrap()
	elif _recursivelyValid(tag):
		if tag.name == 'blockquote':
			# ! FIXME: hack
			tag.insert_before('<<<BLOCKQUOTE: ')
			tag.insert_after('>>>')
			tag.unwrap()
			for child in children:
				_markdownify(child, _blockQuote=True)
			return
		elif tag.name == 'a':
			# process children first
			for child in children:
				_markdownify(child)
			if tag.string != tag['href'] or tag.has_attr('title'):
				title = ''
				if tag.has_attr('title') and tag['title']:
					title = ' "%s"' % tag['title']
				tag.string = '[%s](%s%s)' % (BeautifulSoup(unicode(tag), 'html.parser').string,
					tag['href'],
					title)
			else:
				# ! FIXME: hack
				tag.string = '<<<FLOATING LINK: %s>>>' % tag.string
			tag.unwrap()
			return
		elif tag.name == 'h1':
			tag.insert_before('\n\n# ')
			tag.insert_after('\n\n')
			tag.unwrap()
		elif tag.name == 'h2':
			tag.insert_before('\n\n## ')
			tag.insert_after('\n\n')
			tag.unwrap()
		elif tag.name == 'h3':
			tag.insert_before('\n\n### ')
			tag.insert_after('\n\n')
			tag.unwrap()
		elif tag.name == 'h4':
			tag.insert_before('\n\n#### ')
			tag.insert_after('\n\n')
			tag.unwrap()
		elif tag.name == 'h5':
			tag.insert_before('\n\n##### ')
			tag.insert_after('\n\n')
			tag.unwrap()
		elif tag.name == 'h6':
			tag.insert_before('\n\n###### ')
			tag.insert_after('\n\n')
			tag.unwrap()
		elif tag.name in ('ul', 'ol'):
			tag.insert_before('\n\n')
			tag.insert_after('\n\n')
			tag.unwrap()
			for i, child in enumerate(children):
				_markdownify(child, _listType=tag.name, _listIndex=i+1)
			return
		elif tag.name == 'li':
			if not _listType:
				# <li> outside of list; ignore
				return
			if _listType == 'ul':
				tag.insert_before('*   ')
			else:
				tag.insert_before('%d.   ' % _listIndex)
			for child in children:
				_markdownify(child)
			for c in tag.contents:
				c.replace_with('\n    '.join(c.split('\n')))
			tag.insert_after('\n')
			tag.unwrap()
			return
		elif tag.name in ('strong','b'):
			tag.insert_before('__')
			tag.insert_after('__')
			tag.unwrap()
		elif tag.name in ('em','i'):
			tag.insert_before('_')
			tag.insert_after('_')
			tag.unwrap()
		for child in children:
			_markdownify(child)

def toMarkdown(html):
	"""converts an html string to markdown while preserving unsupported markup."""
	#html = ''.join(line.strip() for line in html.split('\n'))
	# FIXME: will this work? (need to preserve newlines for code blocks)
	bs = BeautifulSoup(html, 'html.parser')
	_markdownify(bs)
	ret = unicode(bs).replace(u'\xa0', '&nbsp;')
	ret = re.sub(r'\n{3,}', r'\n\n', ret)
	# ! FIXME: hack
	ret = re.sub(r'&lt;&lt;&lt;FLOATING LINK: (.+)&gt;&gt;&gt;', r'<\1>', ret)
	# ! FIXME: hack
	sp = re.split(r'(&lt;&lt;&lt;BLOCKQUOTE: .*?&gt;&gt;&gt;)', ret, flags=re.DOTALL)
	for i,e in enumerate(sp):
		if e[:len('&lt;&lt;&lt;BLOCKQUOTE:')] == '&lt;&lt;&lt;BLOCKQUOTE:':
			sp[i] = '> ' + e[len('&lt;&lt;&lt;BLOCKQUOTE:') : -len('&gt;&gt;&gt;')]
			sp[i] = sp[i].replace('\n', '\n> ')
	ret = ''.join(sp)
	return ret.strip()