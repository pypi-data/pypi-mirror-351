from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='prompt_galary',  # Must be unique on PyPI
    version='0.1.1',
    packages=find_packages(include=['prompt_galary', 'prompt_galary.*']),
    install_requires=["langchain_groq","pydantic"],  # or list of dependencies
    author='Jay Telgote',
    author_email='ijaytelgote@gmail.com',
    description='a prompt galary for llm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ijaytelgote/prompt_galary',
    license='MIT',

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
