from pathlib import Path

import setuptools

VERSION = "0.0.3"

NAME = "mendive"

INSTALL_REQUIRES = [
    "aegypti>=0.2.9"
]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description="Solve the Claw-Free Problem for an undirected graph encoded in DIMACS format.",
    url="https://github.com/frankvegadelgado/mendive",
    project_urls={
        "Source Code": "https://github.com/frankvegadelgado/mendive",
        "Documentation Research": "https://dev.to/frank_vega_987689489099bf/claw-finding-algorithm-using-aegypti-2p0k",
    },
    author="Frank Vega",
    author_email="vega.frank@gmail.com",
    license="MIT License",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires=">=3.10",
    # Requirements
    install_requires=INSTALL_REQUIRES,
    packages=["mendive"],
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'claw = mendive.app:main',
            'test_claw = mendive.test:main'
        ]
    }
)