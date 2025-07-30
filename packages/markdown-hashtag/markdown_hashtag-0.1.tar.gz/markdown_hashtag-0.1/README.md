[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# Markdown Extension for Hashtags

This is an extension for [Python-Markdown](https://pypi.org/project/Markdown/) to support hashtag parsing to clickable links.

```
# Heading

#hashtag at beginning of line and #within line.

This is no#hashtag. 

#Markdown
```

will be rendered to:

```html
<h1>Heading</h1>
<p>⁠<a class="hashtag" href="https://tags.example.com/hashtag">#hashtag</a> at beginning of line and <a class="hashtag" href="https://tags.example.com/within">#within</a> line.</p>
<p>This is no#hashtag. </p>
<p>⁠<a class="hashtag" href="https://tags.example.com/Markdown">#Markdown</a></p>
```

You can easily specify the used link prefix and the class name of the link, see [# Usage](#usage) below.

# Installation

The markdown-hashtag package can be installed via:

```bash
pip install markdown-hashtag
```

# Usage

The following python code example shows how to use the hashtag extension and style the hashtag links in a pretty way with CSS (similar to how Obsidian renderns hashtags).

Note that you can define the link prefix of the href attribute and the class name by defining `extension_configs` in the `markdown.markdown()` function, see example.

```python
import markdown

text = """\
# Heading

#hashtag at beginning of line and #within line.

This is no#hashtag. 

#Markdown
<style>
a.hashtag {
  background-color: #e0e0e0;      /* hellgrauer Hintergrund */
  border-radius: 4px;             /* abgerundete Ecken */
  padding: 2px 6px;               /* innen etwas Abstand */
  color: #3b6ea5;                /* blaue Farbe für Links */
  text-decoration: none;          /* keine Unterstreichung */
  font-weight: 500;               /* etwas fetter */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

a.hashtag:hover {
  background-color: #cfd8dc;      /* dunkleres Grau beim Hover */
  text-decoration: underline;     /* Unterstreichung beim Hover */
}
</style>
"""

html = markdown.markdown(text,
    extensions=["hashtag"],
    extension_configs={
        "hashtag": {
            "base_url": "https://tags.example.com/",
            "span_class": "hashtag"
        }
    }
)

print(html)
```
The result looks like this:

![rendered ouput in Browser](renderedHashtags.png)

# License

This project is licensed under the terms of the GNU General Public License v3.0.  
See the [LICENSE](./LICENSE) file for details.


