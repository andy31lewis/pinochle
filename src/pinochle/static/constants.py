"""
Module to provide constants.
"""

CARD_URL = "/static/playingcards.svg"

#                0      1        2           3        4       5
GAME_MODES = ["game", "bid", "bidfinal", "reveal", "meld", "trick"]
PLAYER_DECK_CONFIG = {
    1: {"flippable": False, "movable": False},  # Bid
    2: {"flippable": False, "movable": False},  # Bidfinal
    3: {"flippable": False, "movable": False},  # Reveal
    4: {"flippable": False, "movable": True},  # Meld
    5: {"flippable": False, "movable": True},  # Trick
}

# TODO: Mode 'reveal' needs to be non-flippable for all but the bid winner.
OTHER_DECK_CONFIG = {  # Doubles as the mode for the meld pile used in the "bid" mode.
    # Also doubles as the mode for the discard pile used in the "trick" mode.
    1: {"flippable": False, "movable": False, "show_face": False},  # Bid (Kitty)
    2: {"flippable": False, "movable": False, "show_face": False},  # Bidfinal (Kitty)
    3: {"flippable": True, "movable": False, "show_face": False},  # Reveal (Kitty)
    4: {"flippable": False, "movable": False, "show_face": True},  # Meld (Meld)
    5: {"flippable": False, "movable": False, "show_face": True},  # Trick (Discard)
}
