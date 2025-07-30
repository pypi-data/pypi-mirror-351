"""
Set up Nuke so it can see the Conductor installation.

Companion calls this module automatically after installation.

It writes stuff into <nuke_home_folder>/init.py
"""
import os
import sys
import errno

# /users/me/Conductor/cionuke
PKG_DIR = os.path.dirname(os.path.abspath(__file__))
CIO_NUKE_PLUGIN = os.path.join(os.path.dirname(PKG_DIR), 'nuke').replace("\\", "/")  # /users/me/Conductor/nuke
NUKE_HOME_PATH = os.path.expanduser("~/.nuke/")  # /Users/me/.nuke/
SUFFIX = "# Added by Conductor\n" # Don't change as it will cause duplicate lines in previous installs


def main():
    """
    Write Conductor stuff to Nuke's init.py and menu.py.
    """
    
    init_file = os.path.join(NUKE_HOME_PATH, "init.py")

    init_file_lines = [
        "nuke.pluginAppendPath('{}')".format(CIO_NUKE_PLUGIN),
    ]
 
    ensure_directory(NUKE_HOME_PATH)

    replace_conductor_lines(init_file, init_file_lines)

    sys.stdout.write("Added conductor setup commands to \"{}\"!\n".format(init_file))
    sys.stdout.write("Completed Nuke setup!\n")


def replace_conductor_lines(filename, new_lines):
    """
    Replace previous Conductor lines with new Conductor lines.

    Conductor lines are identified by the suffix: # Added by Conductor

    Obviously we don't want a double import, so we check for import sys
    """

    # Read the file and ignore any lines ending with the Conductor suffix
    try:
        with open(filename, "r") as f:
            lines = [line for line in f.readlines() if line.strip() and not line.endswith(SUFFIX)]
    except IOError:
        lines = []

    with open(filename, "w") as f:
        
        # Copy lines from the existing file
        for line in lines:
            f.write(line)
        
        f.write("\n\n")
        
        # Add all the new lines with the suffix
        for line in new_lines:
            f.write("{} {}".format(line, SUFFIX))


def ensure_directory(directory):
    try:
        os.makedirs(directory)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(directory):
            pass
        else:
            raise


if __name__ == '__main__':
    main()
