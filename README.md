# html2markdown

**Experimental**: I have only tested this with the Python markdown module, and under relatively limited circumstances.

Converts html to markdown while preserving unsupported html markup. The goal is to generate markdown that can be converted back into html. This is the major difference between html2markdown and html2text. The latter doesn't purport to necessarily be reversible.

\* Extraneous whitespace may be removed or added.

## Usage example

	import html2markdown
	print html2markdown.convert('<h2>Test</h2><pre><code>Here is some code</code></pre>')

Output:

	## Test
	
	    Here is some code

## Information and caveats

#### Does not convert the content of block-type tags other than \<p\> -- such as \<div\> tags -- into Markdown

It does convert to markdown the content of inline-type tags, e.g. \<span\>.  
**Input**: \<div\>this is stuff. \<strong\>stuff\</strong>\</div\>  
**Result**: \<div\>this is stuff. \<strong\>stuff\</strong\>\</div\>  
**Input**: \<p\>this is stuff. \<strong\>stuff\</strong\>\</p\>  
**Result**: this is stuff. \_\_stuff\_\_ (surrounded by a newline on either side)  
**Input**: \<span style="text-decoration:line-through;"\>strike \<strong\>through\</strong\> some text\</span\> here  
**Result**: \<span style="text-decoration:line-through;"\>strike \_\_through\_\_ some text\</span\> here

#### Except in unprocessed block-type tags, formatting characters are escaped

**Input**: \<p\>\*\*escape me?\*\*\</p\> (in html, we would use \<strong\> here)  
**Result**: \\\*\\\*escape me?\\\*\\\*  
**Input**: \<span\>\*\*escape me?\*\*\</span\>  
**Result**: \<span\>\\\*\\\*escape me?\\\*\\\*\</div\>  
**Input**: \<div\>\*\*escape me?\*\*\</div\>  
**Result**: \<div\>\*\*escape me?\*\*\</div\> (block-type)

#### Attributes not supported by Markdown are kept

**Example**: \<a href="http://myaddress" title="click me"\>\<strong\>link\</strong\>\</a\>  
**Result**: \[\_\_link\_\_\]\(http://myaddress "click me"\)  
**Example**: \<a onclick="javascript:dostuff()" href="http://myaddress" title="click me"\>\<strong\>link\</strong\>\</a\>  
**Result**: \<a onclick="javascript:dostuff()" href="http://myaddress" title="click me"\>\_\_link\_\_\</a\> (the attribute _onclick_ is not supported, so the tag is left alone)


## Limitations

* Currently, only underlines (_) and asterisks (*) are escaped.
* Tables are kept as html.