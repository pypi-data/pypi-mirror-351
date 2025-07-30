from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mwgencode-mcp",
    version="0.1.3",
    author="Your Name",
    author_email="your.email@example.com",
    description="A MCP-based code generation tool for web frameworks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mwgencode-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "mcp>=1.7.1",
        "pyyaml>=6.0.2",
        "mwgencode>=1.4.0",
        "fastmcp>=2.2.10",
    ],
    entry_points={
        "console_scripts": [
            "mwgencode-mcp=mwgencode_mcp.main:main",
        ],
    },
)