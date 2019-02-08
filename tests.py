import unittest
import html2markdown
import markdown
import bs4


class TestGenericTags(unittest.TestCase):

	emptyElements = {
		'embed',
		'img',
		'input',
		'wbr',
	}

	def test_block_tag_content(self):
		"""content of block-type tags should not be converted (except <p>)"""
		testStr = '<div>this is stuff. <strong>stuff</strong></div>'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, testStr)

	def test_p_content(self):
		"""<p>'s content should be converted"""
		testStr = '<p>this is stuff. <strong>stuff</strong></p>'
		expectedStr = 'this is stuff. __stuff__'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, expectedStr)

	def test_inline_tag_break(self):
		"""inline-type tags should not cause line breaks"""
		emptyElements = self.emptyElements
		for tag in html2markdown._inlineTags:
			if tag not in emptyElements:
				testStr = '<p>test <%s>test</%s> test</p>' % (tag, tag)
			else:
				testStr = '<p>test <%s /> test</p>' % tag
			mdStr = html2markdown.convert(testStr)
			bs = bs4.BeautifulSoup(markdown.markdown(mdStr), 'html.parser')

			self.assertEqual(len(bs.find_all('p')), 1)

	def test_inline_tag_content(self):
		"""content of inline-type tags should be converted"""
		emptyElements = self.emptyElements
		for tag in html2markdown._inlineTags:
			if tag in emptyElements:
				continue

			testStr = '<%s style="text-decoration:line-through;">strike <strong>through</strong> some text</%s> here' % (tag, tag)
			expectedStr = '<%s style="text-decoration:line-through;">strike __through__ some text</%s> here' % (tag, tag)

			mdStr = html2markdown.convert(testStr)

			self.assertEqual(mdStr, expectedStr, 'Tag: {}'.format(tag))

			bs = bs4.BeautifulSoup(markdown.markdown(mdStr), 'html.parser')
			self.assertEqual(
				len(bs.find_all('strong')), 1 if tag != 'strong' else 2,
				'Tag: {}. Conversion: {}'.format(tag, mdStr)
			)

class TestEscaping(unittest.TestCase):

	escapableChars = r'\`*_{}[]()#+-.!'

	@classmethod
	def setUpClass(cls):
		cls.escapedChars = html2markdown._escapeCharSequence

	def test_block_tag_escaping(self):
		"""formatting characters should NOT be escaped for block-type tags (except <p>)"""
		for escChar in self.escapableChars:
			testStr = '<div>**escape me**</div>'.replace('*', escChar)
			expectedStr = '<div>**escape me**</div>'.replace('*', escChar)
			mdStr = html2markdown.convert(testStr)
			self.assertEqual(mdStr, expectedStr)

	def test_p_escaping(self):
		"""formatting characters should be escaped for p tags"""
		for escChar in self.escapedChars:
			testStr = '<p>**escape me**</p>'.replace('*', escChar)
			expectedStr = '\*\*escape me\*\*'.replace('*', escChar)
			mdStr = html2markdown.convert(testStr)
			self.assertEqual(mdStr, expectedStr)

	def test_p_escaping_2(self):
		"""ensure all escapable characters are retained for <p>"""
		for escChar in self.escapableChars:
			testStr = '<p>**escape me**</p>'.replace('*', escChar)
			mdStr = html2markdown.convert(testStr)
			reconstructedStr = markdown.markdown(mdStr)
			self.assertEqual(reconstructedStr, testStr)

	def test_inline_tag_escaping(self):
		"""formatting characters should be escaped for inline-type tags"""
		for escChar in self.escapedChars:
			testStr = '<span>**escape me**</span>'
			expectedStr = '<span>\*\*escape me\*\*</span>'
			mdStr = html2markdown.convert(testStr)
			self.assertEqual(mdStr, expectedStr)

	def test_inline_tag_escaping_2(self):
		"""ensure all escapable characters are retained for inline-type tags"""
		for escChar in self.escapableChars:
			testStr = '<p><span>**escape me**</span></p>'
			mdStr = html2markdown.convert(testStr)
			reconstructedStr = markdown.markdown(mdStr)
			self.assertEqual(reconstructedStr, testStr)

	def test_header(self):
		result = html2markdown.convert('<p># test</p>')
		bs = bs4.BeautifulSoup(markdown.markdown(result), 'html.parser')
		self.assertEqual(len(bs.find_all('h1')), 0)

		result = html2markdown.convert('<p><h1>test</h1></p>')
		bs = bs4.BeautifulSoup(markdown.markdown(result), 'html.parser')
		self.assertEqual(len(bs.find_all('h1')), 1)

	def test_links(self):
		result = html2markdown.convert('<p>[http://google.com](test)</p>')
		bs = bs4.BeautifulSoup(markdown.markdown(result), 'html.parser')
		self.assertEqual(len(bs.find_all('a')), 0)

		result = html2markdown.convert('<p><a href="http://google.com">test</a></p>')
		bs = bs4.BeautifulSoup(markdown.markdown(result), 'html.parser')
		self.assertEqual(len(bs.find_all('a')), 1)

class TestTags(unittest.TestCase):

	genericStr = '<div><p>asdf</p></div><h2>Test</h2><pre><code>Here is some code</code></pre>'
	problematic_a_string_1 = "before <a>test</a> after"
	problematic_a_string_2 = "before <a title=\"test_title\">test</a> after"
	problematic_a_string_3 = "<a></a>"
	problematic_a_string_4 = "<a href=\"test\" title=\"test\">test</a>"
	problematic_a_string_5 = "<a href=\"test\">test</a>"
	problematic_a_string_6 = "<a href=\"test2\">test</a>"

	def test_h2(self):
		mdStr = html2markdown.convert(self.genericStr)
		reconstructedStr = markdown.markdown(mdStr)

		bs = bs4.BeautifulSoup(reconstructedStr, 'html.parser')
		childTags = bs.find_all(recursive=False)

		self.assertEqual(childTags[1].name, 'h2')
		self.assertEqual(childTags[1].string, 'Test')

	def test_a(self):
		mdStr = html2markdown.convert(self.problematic_a_string_1)
		self.assertEqual(mdStr, self.problematic_a_string_1,
			"<a> tag without an href attribute should be left alone")

		mdStr = html2markdown.convert(self.problematic_a_string_2)
		self.assertEqual(mdStr, self.problematic_a_string_2,
			"<a> tag without an href attribute should be left alone")

		mdStr = html2markdown.convert(self.problematic_a_string_3)
		self.assertEqual(mdStr, self.problematic_a_string_3,
			"<a> tag without an href attribute should be left alone")

		mdStr = html2markdown.convert(self.problematic_a_string_4)
		self.assertEqual(mdStr, '[test](test "test")')

		mdStr = html2markdown.convert(self.problematic_a_string_5)
		self.assertEqual(mdStr, '<test>')

		mdStr = html2markdown.convert(self.problematic_a_string_6)
		self.assertEqual(mdStr, '[test](test2)')

	def test_span(self):
		"""content of inline-type tags should be converted"""
		testStr = '<span style="text-decoration:line-through;">strike <strong>through</strong> some text</span> here'
		expectedStr = '<span style="text-decoration:line-through;">strike __through__ some text</span> here'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, expectedStr)

if __name__ == '__main__':
	unittest.main()
