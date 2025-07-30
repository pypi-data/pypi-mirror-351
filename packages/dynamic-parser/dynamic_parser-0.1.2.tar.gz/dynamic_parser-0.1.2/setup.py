from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='dynamic_parser',  # Must be unique on PyPI
    version='0.1.2',
    packages=find_packages(include=['dynamic_parser', 'dynamic_parser.*',]),
    install_requires=["langchain_groq","regex","pydantic"],  # or list of dependencies
    author='Jay Telgote',
    author_email='ijaytelgote@gmail.com',
    description='Fix json structure and parse it',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ijaytelgote/dynamic_parser',
    license='MIT',

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
