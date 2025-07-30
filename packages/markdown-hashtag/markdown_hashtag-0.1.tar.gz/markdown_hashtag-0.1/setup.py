from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='markdown-hashtag',
    version='0.1',
    description='Extension for Python-Markdown to parse hashtag (e.g. #Python) into a user-defined URL',
    long_description=long_description,
    long_description_content_type="text/markdown", 
    author='Vinzenz Becke-Stauner (Becksta)',
    author_email='info@becke-stauner.de',
    url='https://github.com/becksta-dev/markdown-hashtag', 
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'markdown>=3.0',
    ],
    entry_points={
        'markdown.extensions': [
            'hashtag = markdown_hashtag:makeExtension',
        ],
    },
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
