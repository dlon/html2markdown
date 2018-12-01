import unittest
import html2markdown
import markdown
import bs4


class TestGenericTags(unittest.TestCase):

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

	def test_inline_tag_content(self):
		"""content of inline-type tags should be converted"""
		testStr = '<span style="text-decoration:line-through;">strike <strong>through</strong> some text</span> here'
		expectedStr = '<span style="text-decoration:line-through;">strike __through__ some text</span> here'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, expectedStr)

class TestEscaping(unittest.TestCase):

	def test_block_tag_escaping(self):
		"""formatting characters should NOT be escaped for block-type tags (except <p>)"""
		testStr = '<div>**escape me**</div>'
		expectedStr = '<div>**escape me**</div>'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, expectedStr)

	def test_p_escaping(self):
		"""formatting characters should be escaped for p tags"""
		testStr = '<p>**escape me**</p>'
		expectedStr = '\*\*escape me\*\*'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, expectedStr)

	def test_inline_tag_escaping(self):
		"""formatting characters should be escaped for inline-type tags"""
		testStr = '<span>**escape me**</span>'
		expectedStr = '<span>\*\*escape me\*\*</span>'
		mdStr = html2markdown.convert(testStr)
		self.assertEqual(mdStr, expectedStr)

class TestTags(unittest.TestCase):

	genericStr = '<div><p>asdf</p></div><h2>Test</h2><pre><code>Here is some code</code></pre>'

	def test_h2(self):
		mdStr = html2markdown.convert(self.genericStr)
		reconstructedStr = markdown.markdown(mdStr)

		bs = bs4.BeautifulSoup(reconstructedStr, 'html.parser')
		childTags = bs.find_all(recursive=False)

		self.assertEqual(childTags[1].name, 'h2')
		self.assertEqual(childTags[1].string, 'Test')

if __name__ == '__main__':
	unittest.main()
