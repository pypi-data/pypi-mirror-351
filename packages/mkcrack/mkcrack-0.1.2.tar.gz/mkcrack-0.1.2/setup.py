from setuptools import setup, find_packages

# Read the README.md content
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mkcrack',
    version='0.1.2',
    packages=find_packages(),
    description='A simple Yescrypt hash cracker by Manju',
    long_description=long_description,
    long_description_content_type='text/markdown',  # This tells PyPI that your README is in Markdown
    author='Manju',
    author_email='kotabagimanju240@gmail.com',
    python_requires='>=3.6',
)
