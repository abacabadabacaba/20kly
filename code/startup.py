#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006.
#

# Version check. This file can be much shorter for Debian.

import sys

def Check_Version() -> None:
    fault = False
    if ( sys.__dict__.get("version_info", None) ):
        (major, minor, micro, releaselevel, serial) = sys.version_info
        if (( major < 3 )
        or (( major == 3 ) and ( minor < 8 ))):
            fault = True
    else:
        major = 1
        minor = 0
        fault = True

    if ( fault ):
        sys.stderr.write("\n")
        sys.stderr.write("Python 3 version 3.8 or higher is required.\n")
        sys.stderr.write("You appear to be using version " + repr((major, minor)) + "\n")
        sys.exit(1)

    try:
        import pygame
    except:
        sys.stderr.write("\n")
        sys.stderr.write("Pygame does not appear to be installed.\n")
        sys.stderr.write("Please install the latest version from http://www.pygame.org/\n")
        sys.exit(1)

    try:
        # The size of this field changed between
        # ver. 1.6 and ver. 1.7. Arrgh.
        [major, minor] = list(pygame.version.vernum)[ 0:2 ]
        x = pygame.version.ver
    except:
        sys.stderr.write("\n")
        sys.stderr.write("Pygame is installed, but you have an old version.\n")
        sys.stderr.write("Please install the latest version from http://www.pygame.org/\n")
        sys.exit(1)

    if ( major < 2 ):
        sys.stderr.write("\n")
        sys.stderr.write(repr(pygame.version.ver))
        sys.stderr.write("Pygame version 2.x or higher is required.\n")
        sys.stderr.write("Please install the latest version from http://www.pygame.org/\n")
        sys.exit(1)


def Get_Game_Version() -> str:
    return "1.5"

def Main(data_dir: str, ignore = None) -> None:
    Check_Version()
    import main
    main.Main(data_dir)


