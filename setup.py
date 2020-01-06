import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fedora-checksum-tester",
    version="1.0",
    py_modules=['checksum-tester'],
    author="Lukáš Růžička",
    author_email="lruzicka@redhat.com",
    description="Image checksum tester for Fedora",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lruzicka/checksum-tester",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    install_requires=['wget', 'fedfind'],
    entry_points={'console_scripts': ['checksum-tester = checksum-tester:main']}
)
