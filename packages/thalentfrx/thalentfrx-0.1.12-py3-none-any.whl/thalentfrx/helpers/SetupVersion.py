import json
import os
import sys

root_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

json_file = f'{root_dir}/SetupVersion.json'
version_file = f'{root_dir}/../__init__.py'

def read_version() -> str:
    f = open(json_file)
    ver = json.load(f)
    f.close()
    return ver


def change_version(major, minor, revision, suffix="") -> dict[str, str]:
    ver = {"major": major, "minor": minor, "revision": revision, "suffix": suffix}
    with open(json_file, 'w') as f:
        json.dump(ver, f)
        f.close()

    # resetting __version__ value without impact other line of code in the file.
    remove_line_with_word(version_file, "__version__ = ")
    with open(version_file, 'a') as f:
        f.write(f'__version__ = "{current_version()}"')
        f.close()
    return ver


def current_version() -> str:
    ver = read_version()
    if ver["suffix"] == "":
        return "".join([str(ver["major"]), ".", str(ver["minor"]), ".", str(ver["revision"])])
    else:
        return "".join([str(ver["major"]), ".", str(ver["minor"]), ".", str(ver["revision"]), ".", str(ver["suffix"])])


def increase_version(is_dev_version: bool = True) -> str:
    version_json = read_version()
    if is_dev_version:
        change_version(version_json["major"], version_json["minor"], version_json["revision"] + 1, "dev1")
    else:
        change_version(version_json["major"], version_json["minor"], version_json["revision"] + 1)
    return current_version()


def release_version() -> str:
    version_json = read_version()
    change_version(version_json["major"], version_json["minor"], version_json["revision"])
    return current_version()


def remove_line_with_word(file_path, word_to_remove):
    """
    Finds a word in a file and removes the line containing it.

    Args:
        file_path (str): The path to the file.
        word_to_remove (str): The word to search for and remove its line.
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return

    with open(file_path, 'w') as file:
        for line in lines:
            if word_to_remove not in line:
                file.write(line)

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()

    parser.add_argument('-a', '--addversion', default=False, type=bool,
                        help='Adding version revision by 1, useful to make automatic build version.')

    parser.add_argument('-d', '--dev', default=False, type=bool,
                        help='Dev version or Prod version, default: False (Production)')

    parser.add_argument('-r', '--release', default=False, type=bool,
                        help='Release version, this will ignore --addversion and --dev argument, default: True (Production)')

    args = parser.parse_args()
    add_version: bool = args.addversion
    is_dev: bool = args.dev
    is_release: bool = args.release

    ver_json = read_version()
    print("VERSION : %s" % current_version())

    if is_release:
        release_version()
        print("RELEASE VERSION : %s" % current_version())
        exit(0)

    if add_version:
        increase_version(is_dev_version=is_dev)
        print("NEW VERSION : %s" % current_version())
        exit(0)
