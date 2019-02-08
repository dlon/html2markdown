# -*- coding:utf8 -*-
"""html2markdown converts an html string to markdown while preserving unsupported markup."""
#
# Copyright 2017-2018 David Lönnhager (dlon)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import bs4
from bs4 import BeautifulSoup
import re

import sys
if sys.version_info[0] > 2:
	unicode = str

_supportedTags = {
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
}
_supportedAttributes = (
	'a href',
	'a title',
	'img alt',
	'img src',
	'img title',
)

_inlineTags = {
	# these can be mixed with markdown (when unprocessed)
	# block tags will be surrounded by newlines and be unprocessed inside
	# (unless supported tag + supported attribute[s])
	'a',
	'abbr',
	'acronym',
	'audio',
	'b',
	'bdi',
	'bdo',
	'big',
	#'br',
	'button',
	#'canvas',
	'cite',
	'code',
	'data',
	'datalist',
	'del',
	'dfn',
	'em',
	#'embed',
	'i',
	#'iframe',
	#'img',
	#'input',
	'ins',
	'kbd',
	'label',
	'map',
	'mark',
	'meter',
	#'noscript',
	'object',
	#'output',
	'picture',
	#'progress',
	'q',
	'ruby',
	's',
	'samp',
	#'script',
	'select',
	'slot',
	'small',
	'span',
	'strike',
	'strong',
	'sub',
	'sup',
	'svg',
	'template',
	'textarea',
	'time',
	'u',
	'tt',
	'var',
	#'video',
	'wbr',
}

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



_escapeCharSequence = tuple(r'\`*_[]#')
_escapeCharRegexStr = '([{}])'.format(''.join(re.escape(c) for c in _escapeCharSequence))
_escapeCharSub = re.compile(_escapeCharRegexStr).sub


def _escapeCharacters(tag):
	"""non-recursively escape underlines and asterisks
	in the tag"""
	for i,c in enumerate(tag.contents):
		if type(c) != bs4.element.NavigableString:
			continue
		c.replace_with(_escapeCharSub(r'\\\1', c))

def _breakRemNewlines(tag):
	"""non-recursively break spaces and remove newlines in the tag"""
	for i,c in enumerate(tag.contents):
		if type(c) != bs4.element.NavigableString:
			continue
		c.replace_with(re.sub(r' {2,}', ' ', c).replace('\n',''))

def _markdownify(tag, _listType=None, _blockQuote=False, _listIndex=1):
	"""recursively converts a tag into markdown"""
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
				tag.string = u'\xa0'
				tag.unwrap()
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
				line = line.replace(u'\xa0', ' ')
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
			if not tag.has_attr('href'):
				return
			if tag.string != tag.get('href') or tag.has_attr('title'):
				title = ''
				if tag.has_attr('title'):
					title = ' "%s"' % tag['title']
				tag.string = '[%s](%s%s)' % (BeautifulSoup(unicode(tag), 'html.parser').string,
					tag.get('href', ''),
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
				if type(c) != bs4.element.NavigableString:
					continue
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

def convert(html):
	"""converts an html string to markdown while preserving unsupported markup."""
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
	return ret.strip('\n')
