import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="no-profanity",
    version="1.0.2",
    author="GlitchedLime",
    author_email="gabcosamuel8@gmail.com",
    description="A library using regexes to detect and block profanity in strings.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
