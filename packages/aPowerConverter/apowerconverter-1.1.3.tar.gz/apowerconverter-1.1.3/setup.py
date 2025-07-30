from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aPowerConverter",
    version="1.1.3",
    author="Attoz",
    author_email="attoz@users.noreply.github.com",
    description="A powerful bidirectional converter between DOCX and AsciiDoc formats using Pandoc and Asciidoctor",
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
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    keywords="docx, asciidoc, converter, documentation, word, markup, text processing, pandoc, asciidoctor, bidirectional",
    python_requires=">=3.7",
    install_requires=[
        "pypandoc>=1.11",  # Python interface for Pandoc
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