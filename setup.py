import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fedora_checksum_tester",
    version="1.1",
    py_modules=['fedora_checksum_tester'],
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
    entry_points={'console_scripts': ['fedora-checksum-tester = fedora_checksum_tester:main']}
)
