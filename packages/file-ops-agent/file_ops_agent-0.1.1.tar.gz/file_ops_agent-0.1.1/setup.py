from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="file_ops_agent",
    version="0.1.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="Command-line file operations agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/file_ops_agent",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "agent=file_ops_agent.cli:main",
        ],
    },
    install_requires=[],
    license="MIT",
)