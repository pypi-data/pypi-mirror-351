from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bexy",
    version="0.1.26",
    description="A sandbox for safely running Python code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    url="https://github.com/py-lama/bexy",
    packages=find_packages(),
    install_requires=[
        "docker",
        "questionary",
    ],
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'tox',
            'flake8',
            'black',
            'twine',
            'build',
            'wheel'
        ],
    },
    python_requires='>=3.8,<4.0',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'bexy=bexy.examples:main',
        ],
    },
    project_urls={
        'Homepage': 'https://github.com/py-lama/bexy',
        'Documentation': 'https://py-lama.github.io/bexy/',
        'Repository': 'https://github.com/py-lama/bexy',
        'Changelog': 'https://github.com/py-lama/bexy/blob/main/CHANGELOG.md',
        'Tracker': 'https://github.com/py-lama/bexy/issues',
        'Download': 'https://pypi.org/project/bexy/',
    },
)
