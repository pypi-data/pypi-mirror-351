from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aPowerConverter",
    version="1.0.0",
    author="Attoz",
    author_email="attoz@users.noreply.github.com",
    description="A powerful DOCX to AsciiDoc converter with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Attoz/aPowerConverter",
    project_urls={
        "Bug Tracker": "https://github.com/Attoz/aPowerConverter/issues",
        "Documentation": "https://github.com/Attoz/aPowerConverter#readme",
        "Source Code": "https://github.com/Attoz/aPowerConverter",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Office/Business",
    ],
    keywords="docx, asciidoc, converter, documentation, word, markup, text processing",
    python_requires=">=3.7",
    install_requires=[
        "pandoc>=2.19.2",  # For document conversion
    ],
    entry_points={
        "console_scripts": [
            "apowerconverter=aPowerConverter.converter:main",
        ],
    },
    package_data={
        "aPowerConverter": ["README.md"],
    },
    include_package_data=True,
) 