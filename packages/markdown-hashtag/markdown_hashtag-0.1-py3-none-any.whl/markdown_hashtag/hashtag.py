import markdown
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
from xml.etree import ElementTree as etree
import re

# Preprocessor that inserts ZWSP before hashtags to prevent header parsing
class HashtagPreprocessor(Preprocessor):
    HEADER_PATTERN = re.compile(r'^\#{1,6}\s+')
    INLINE_HASHTAG_LINE = re.compile(r'^#(\w[\w_-]*)(\s.*)?$')

    def run(self, lines):
        new_lines = []
        for line in lines:
            if self.HEADER_PATTERN.match(line):
                new_lines.append(line)
            elif self.INLINE_HASHTAG_LINE.match(line):
                # WORD JOINER voranstellen (unsichtbares Unicode-Zeichen)
                new_lines.append('\u2060' + line)
            else:
                new_lines.append(line)
        return new_lines

# InlineProcessor for hashtags
class HashtagInlineProcessor(InlineProcessor):
    PATTERN = r'(?<!\w)(#\w[\w_-]*)'

    def __init__(self, pattern, base_url='', span_class='hashtag'):
        super().__init__(pattern)
        self.base_url = base_url
        self.span_class = span_class

    def handleMatch(self, m, data):
        tag = m.group(1)[1:]
        a = etree.Element('a')
        a.set('href', f'{self.base_url}{tag}')
        if self.span_class:
            a.set('class', self.span_class)
        a.text = f'#{tag}'
        return a, m.start(0), m.end(0)

class HashtagExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'base_url': ['https://tags.example.com/', 'Base URL for hashtags'],
            'span_class': ['hashtag', 'CSS class for hashtag links'],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(HashtagPreprocessor(md), 'hashtagpreprocessor', 25)

        inline_processor = HashtagInlineProcessor(
            HashtagInlineProcessor.PATTERN,
            base_url=self.getConfig('base_url'),
            span_class=self.getConfig('span_class'),
        )
        md.inlinePatterns.register(inline_processor, 'hashtaginline', 175)

def makeExtension(**kwargs):
    return HashtagExtension(**kwargs)
