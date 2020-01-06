#!/usr/bin/python3

"""
Checksum Tester calculates the checksums for the given ISO and compares it the with the official checksums.
It automatically downloads the ISO image from Koji.
"""

import datetime
import glob
import os
import fedfind.release
import subprocess
import wget

def provide_compose(rel="Rawhide", comp=None, arch="x86_64", variant="Everything", subvariant=None, typ=None):
    """ Returns a compose download link base on given criteria. """
    if not comp and rel=="Rawhide":
        # If the compose date identificator is not given, 
        today = datetime.date.today()
        year, month, day = str(today.year), str(today.month), str(today.day)
        if len(month) < 2:
            month = "0"+month
        if len(day) < 2:
            day = "0"+day
        comp = year + month + day
        print(f"The compose date were not given. Trying with today's value: {comp}")
    composes = fedfind.release.get_release(release=rel, compose=comp)
    if subvariant:
        links = [compose for compose in composes.all_images if compose['arch'] == arch and compose['variant'] == variant and compose['subvariant'] == subvariant]
    elif typ:
        links = [compose for compose in composes.all_images if compose['arch'] == arch and compose['variant'] == variant and compose['type'] == typ]
    else:
        links = [compose for compose in composes.all_images if compose['arch'] == arch and compose['variant'] == variant]

    return links

def return_iso_filename(url):
    """ Returns the filename from the url. """
    filename = url.split('/')[-1]
    return filename

def download_iso(composes):
    """ Downloads the selected ISO images from Koji. """
    for compose in composes:
        url = compose['url']
        filename = return_iso_filename(url)
        if filename in os.listdir():
            print(f"The ISO file {filename} seems to be downloaded already, skipping.")
        else:
            wget.download(url)
            print("")

def purge_images(isofiles):
    """ Deletes all iso files from the working directory. """
    for iso in isofiles:
        print(f"Deleting {iso}")
        os.remove(iso)

def find_isofiles():
    """ Finds all files with the .iso extension in the working directory. """
    isofiles = glob.glob("*.iso")
    return isofiles
    
def test_compose_sha256(composes):
    """ Checks if the SHA256 checksums match. """
    results = {}
    for compose in composes:
        url = compose['url']
        filename = return_iso_filename(url)
        expected_sha = compose['checksums']['sha256']
        calculate = subprocess.run(['sha256sum', filename], capture_output=True)
        if calculate.returncode != 0:
            print(calculate.stderr.decode('utf-8'))
        else:
            calculated_sha = calculate.stdout.decode('utf-8').split(" ")
            calculated_sha = calculated_sha[0].strip()
        if expected_sha == calculated_sha:
            print(f"The SHA256 checksum test PASSED for this ISO image.")
            print(f"Expected and calculated checksum: {expected_sha}")
            results[url] = "PASSED"
        else:
            print(f"The SHA256 checksum test FAILED for this ISO image.")
            print(f"Expected checksum: {expected_sha}")
            print(f"Calculated checksum: {calculated_sha}")
            results[url] = "FAILED"
    return results

def test_compose_md5(composes):
    """ Checks if the MD5 checksum is correct. """
    results = {}
    for compose in composes:
        url = compose['url']
        filename = return_iso_filename(url)
        checkmd = subprocess.run(['checkisomd5', filename], capture_output=True)
        output = checkmd.stdout.decode('utf-8')
        print(output)
        if checkmd.returncode == 0:
            print("The MD5 checksum test PASSED.")
            results[filename] = "PASSED"
        elif checkmd.returncode == 1:
            print("The MD5 checksum test FAILED.")
            results[filename] = "FAILED"
        elif checkmd.returncode == 2:
            print("The MD5 checksum test was skipped.")
            results[filename] == "SKIPPED"
        else:
            print(checkmd.stderr.decode('utf-8'))
    return results


composes = provide_compose(comp="20200101", arch="x86_64", variant="Cloud")
print(f"{len(composes)} comp. matching the criteria found.")
download_iso(composes)
test_compose_sha256(composes)
test_compose_md5(composes)








