import argparse
import sys
from genericpath import isdir
import json
from os import listdir

from sentinelc_appfeed.utils.logger import eprint
from .utils.ArgparseCustomTypes import ArgparseCustomTypes

from .validator import validate

version = 6


def build_feed(manifest_path, compile_errors=False):
    apps = list()
    errors = dict()

    # List valid apps
    for folder in listdir(manifest_path):
        item = f"{manifest_path}/{folder}"
        if isdir(item):
            try:
                apps.append(validate(manifest_path, folder))
            except (ValueError, IOError) as e:
                if compile_errors:
                    errors[folder] = e
                    eprint(f"  - app is invalid: {e}")
                else:
                    raise e

    # sort
    apps.sort(key=lambda x: x["name"])

    feed = {"version": version, "apps": apps}

    if compile_errors:
        return feed, errors
    else:
        return feed


def main():

    parser = argparse.ArgumentParser(
        description="""
        Builds a sentinelc app feed JSON file from a manifest folder container one or more apps.

        how to use
        -------------

        `applib-builder -p [manifests] -f [feed.json]`
        Creates a feed based on the manifests folder and output the feed as feed.json
        """  # noqa: W293 E501
    )

    parser.add_argument(
        "-p",
        "--path",
        action="store",
        help='Specify the root of the manifest folder. Default: "manifests"',
        type=ArgparseCustomTypes.dir_path,
        default="manifests",
    )

    parser.add_argument(
        "-f",
        "--filename",
        action="store",
        help='Specify the name of the output file. Default: "feed.json"',
        default="feed.json",
    )

    args = parser.parse_args()

    feed, errors = build_feed(args.path, compile_errors=True)

    if errors:
        eprint("Errors encountered, json feed will not be produced.")
        sys.exit(1)

    with open(args.filename, "w") as outfile:
        json.dump(feed, outfile, indent=4)

    eprint(f"{args.filename} generated")


if __name__ == "__main__":
    main()
