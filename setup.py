import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="raymon",  # Replace with your own username
    version="0.0.1",
    author="Raymon.ai",
    author_email="dev@raymon.ai",
    description="Python package for raymon logging and monitoring.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://raymon.ai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        ],
    python_requires='>=3.6',
    install_requires=[
        # For manifest parsing -- move to api
        "pyyaml",
        # For plotting --move to separate repo
        "bokeh>=1.4.0",
        "matplotlib"
        ],
    entry_points='''
        [console_scripts]
        rayctl=raymon.cli.rayctl:cli
    ''',
)
