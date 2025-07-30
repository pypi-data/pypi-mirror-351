from setuptools import setup, find_packages
import os

# README.mdの内容を読み込み
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

setup(
    name="sercher",
    version="1.0.0",
    description="GrokでWeb検索を実行するコマンドラインツール",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Sugar Knight",
    author_email="your.email@example.com",
    url="https://github.com/sugarkwork/sercher",
    py_modules=["sercher"],
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "sercher=sercher:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Utilities",
    ],
    keywords="search, web, grok, ai, cli",
    python_requires=">=3.6",
    include_package_data=True,
)