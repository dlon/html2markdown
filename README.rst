=============
html2markdown
=============

**Experimental**

**Purpose**: Converts html to markdown while preserving unsupported html markup. The goal is to generate markdown that can be converted back into html. This is the major difference between html2markdown and html2text. The latter doesn't purport to be reversible.

Usage example
=============
::

	import html2markdown
	print html2markdown.convert('<h2>Test</h2><pre><code>Here is some code</code></pre>')

Output::

	## Test
	
	    Here is some code

Information and caveats
=======================

Does not convert the content of block-type tags other than ``<p>`` -- such as ``<div>`` tags -- into Markdown
-------------------------------------------------------------------------------------------------------------

It does convert to markdown the content of inline-type tags, e.g. ``<span>``.

**Input**: ``<div>this is stuff. <strong>stuff</strong></div>``

**Result**: ``<div>this is stuff. <strong>stuff</strong></div>``  

**Input**: ``<p>this is stuff. <strong>stuff</strong></p>``  

**Result**: ``this is stuff. __stuff__`` (surrounded by a newline on either side)  

**Input**: ``<span style="text-decoration:line-through;">strike <strong>through</strong> some text</span> here``  

**Result**: ``<span style="text-decoration:line-through;">strike __through__ some text</span> here``  

Except in unprocessed block-type tags, formatting characters are escaped
------------------------------------------------------------------------

**Input**: ``<p>**escape me?**</p>`` (in html, we would use \<strong\> here)  

**Result**: ``\*\*escape me?\*\*``  

**Input**: ``<span>**escape me?**</span>``  

**Result**: ``<span>\*\*escape me?\*\*</span>``  

**Input**: ``<div>**escape me?**</div>``  

**Result**: ``<div>**escape me?**</div>`` (block-type)  

Attributes not supported by Markdown are kept
---------------------------------------------

**Example**: ``<a href="http://myaddress" title="click me"><strong>link</strong></a>``  

**Result**: ``[__link__](http://myaddress "click me")``  

**Example**: ``<a onclick="javascript:dostuff()" href="http://myaddress" title="click me"><strong>link</strong></a>``  

**Result**: ``<a onclick="javascript:dostuff()" href="http://myaddress" title="click me">__link__</a>`` (the attribute *onclick* is not supported, so the tag is left alone)  


Limitations
===========

- Tables are kept as html.

Changes
=======

0.1.7:

- Improved handling of inline tags.
- Fix: Ignore ``<a>`` tags without an href attribute.
- Improve escaping.

0.1.6: Added tests and support for Python versions below 2.7.

0.1.5: Fix Unicode issue in Python 3.

0.1.0: First version.
