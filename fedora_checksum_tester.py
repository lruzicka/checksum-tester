#!/usr/bin/python3

"""
Checksum-Tester calculates the SHA256 and MD5 checksums for the Fedora image files and compares it with the officially provided checksums.
If the checksums match, this script reports PASSED, otherwise it reports FAILED.
The images are automatically downloaded from Koji, if they have not been previously downloaded into the working directory. If so, they
are not downloaded again, unless chosen so with a switch.
"""

import argparse
import datetime
import glob
import os
import fedfind.release
import subprocess
import sys
import wget

def read_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--release', default="Rawhide", help="Fedora release")
    parser.add_argument('-c', '--compose', default=None, help="Compose identifier, YYYYMMDD for Rawhide.")
    parser.add_argument('-a', '--arch', default="x86_64", help="Architecture")
    parser.add_argument('-v', '--variant', default="Everything", help="Variant (Everything, Server, Workstation, Spins, Cloud")
    parser.add_argument('-s', '--subvariant', default=None, help="Subvariant (For spins: KDE, LXCD, XFCE)")
    parser.add_argument('-t', '--type', default=None, help="Type of image (For server: boot, dvd)")
    parser.add_argument('-p', '--purge', default=False, help="Use 'True' if you want to delete downloaded after testing.")
    parser.add_argument('-f', '--forcedownload', default=False, help="Use 'True' if you want to download images even when they already exist locally.")
    args = parser.parse_args()
    return args
    
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
    try:    
        composes = fedfind.release.get_release(release=rel, compose=comp)
    except NameError:
        print("fedfind is required to search for the images, you need to install it.")
    if subvariant:
        images = [compose for compose in composes.all_images if compose['arch'] == arch and compose['variant'] == variant and compose['subvariant'] == subvariant]
    elif typ:
        images = [compose for compose in composes.all_images if compose['arch'] == arch and compose['variant'] == variant and compose['type'] == typ]
    else:
        images = [compose for compose in composes.all_images if compose['arch'] == arch and compose['variant'] == variant]
    return images

def return_iso_filename(url):
    """ Returns the filename from the url. """
    filename = url.split('/')[-1]
    return filename

def download_iso(composes, forced="False"):
    """ Downloads the selected ISO images from Koji. """
    for compose in composes:
        url = compose['url']
        filename = return_iso_filename(url)
        if filename in os.listdir() and forced == "True":
            print(f"The ISO file {filename} seems to be downloaded already, skipping the download.")
        else:
            print("Downloading images:")
            try:
                wget.download(url)
            except NameError:
                print("Downloading uses the wget module, but it is not installed.")
            print("")

def purge_images(composes):
    """ Deletes all iso files from the working directory. """
    for compose in composes:
        url = compose['url']
        target = return_iso_filename(url)
        print(f"Deleting {target}")
        os.remove(target)

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
            results[filename] = "PASSED"
        else:
            results[filename] = "FAILED"
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
            results[filename] = "PASSED"
        elif checkmd.returncode == 1:
            results[filename] = "FAILED"
        elif checkmd.returncode == 2:
            results[filename] == "SKIPPED"
        else:
            print(checkmd.stderr.decode('utf-8'))
    return results

def print_results(field, results):
    """ Prints results of the tests. """
    print(f"================ {field} RESULTS ============================")
    print("")
    for result in results.keys():
        print(f"{result}: {results[result]}")
    print("")
    
def print_available_composes(composes):
    """ Prints a list of available ISO files to test. """
    if len(composes) > 1:
        message = f"{len(composes)} image files matching the criteria found: "
    elif len(composes) == 1:
        message = "One image file matching the criteria found: "
    else:
        message = "No image file matching the criteria found."
    print(message)
    print("")
    for compose in composes:
        url = compose['url']
        print(url)
    print("")

def main():
    """ Main program. """
    args = read_cli()
    composes = provide_compose(rel=args.release, comp=args.compose, arch=args.arch, variant=args.variant, subvariant=args.subvariant, typ=args.type)
    purge = args.purge
    print_available_composes(composes)
    download_iso(composes)
    sha_results = test_compose_sha256(composes)
    print_results("SHA256 CHECKSUM", sha_results)
    md_results = test_compose_md5(composes)
    print_results("MD5 CHECKSUM", md_results)
    if purge == "True":
        purge_images(composes)
    if "FAILED" in sha_results.values() or "FAILED" in md_results.values():
        sys.exit(1)

if __name__ == '__main__':
    main()