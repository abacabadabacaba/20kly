#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import pygame
from lib20k import main
from lib20k.primitives import *
from lib20k.game_types import *
from .unit_test import *

def test_Game_Events() -> None:
    """Test for game.py.

    This test looks at the popup menu which can
    appear during the game. Correctness of the test is
    established by 100% coverage of the menu-related code
    within game.py.
    """
    event_list = [NoEvent(),
                  Push(pygame.K_n), # new game
                  NoEvent(),
                  Push(pygame.K_i), # intermediate
                  NoEvent(),
                  Click((10, 10)),
                  NoEvent(),
                  RightClick((20, 20)),
                  NoEvent(),
                  Move((30, 30)),
                  NoEvent(),
                  Release((40, 40)),
                  NoEvent(),
                  Other(),
                  NoEvent(),
                  VideoResize(),
                  NoEvent(),
                  ActiveEvent(),
                  NoEvent(),
                  Click((100, 100)),        # click in unused space
                  NoEvent(),
                  Push(pygame.K_F9),        # fill the screen with white (test refresh)
                  NoEvent(),
                  Push(pygame.K_F15),       # fast forward
                  NoEvent(),
                  Release((50, 50)),        # stop fast forward
                  NoEvent(),
                  Push(pygame.K_F10),       # skip to next season
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Move((40, 40)),
                  NoEvent(),
                  Click((50, 50)),
                  NoEvent(),
                  RightClick((60, 60)),
                  NoEvent(),
                  VideoResize(),
                  NoEvent(),
                  ActiveEvent(),
                  NoEvent(),
                  Push(pygame.K_m),         # mute (stays in the menu)
                  NoEvent(),
                  Screenshot("mute1.png"),
                  NoEvent(),
                  Push(pygame.K_m),         # mute again
                  NoEvent(),
                  Screenshot("mute2.png"),
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # leave menu (return to game)
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_r),         # restore
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # leave menu (cancelling restore)
                  NoEvent(),
                  Push(pygame.K_ESCAPE),    # enter menu
                  NoEvent(),
                  Push(pygame.K_q),         # leave menu (quit to main menu)
                  NoEvent(),
                  Quit(),
                  NoEvent()]
    main.Main(data_dir="data", args=[],
              event=Fake_Events(event_list))

