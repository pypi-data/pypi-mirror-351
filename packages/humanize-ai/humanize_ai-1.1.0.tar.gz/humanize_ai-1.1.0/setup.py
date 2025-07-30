from setuptools import setup, find_packages

setup(
    name="humanize-ai",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "regex",  # For Unicode property support
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
            "mypy",
            "twine",
        ],
    },
    python_requires=">=3.6",
    description="Humanize AI-generated text by normalizing Unicode characters",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Eric Berry",
    author_email="eric@berrydev.ai",
    url="https://github.com/berrydev-ai/humanize-ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["humanize", "string", "ai", "unicode", "text"],
    entry_points={
        "console_scripts": [
            "humanize-ai=humanize_ai.cli:main",
        ],
    },
)
