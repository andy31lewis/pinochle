from sys import stderr

from browser import window, document, html, svg
import brySVG.dragcanvas as SVG
from brySVG.dragcanvas import UseObject
from random import sample

CARD_URL = "/static/svg-cards.svg#"

# Intrinsic dimensions of the cards in the deck.
card_width = 170
card_height = 245


class PlayingCard(UseObject):
    def __init__(
        self,
        href=None,
        topleft=(0, 0),
        angle=0,
        linecolour="black",
        linewidth=1,
        fillcolour="yellow",
        face_value="back",
        show_face=True,
        flippable=None,
        movable=True,
    ):
        if href is None:
            href = CARD_URL + (f"{face_value}" if show_face else "back")
        self.face_value = face_value
        self.show_face = show_face
        UseObject.__init__(
            self,
            href=href,
            topleft=topleft,
            angle=angle,
            linecolour=linecolour,
            linewidth=linewidth,
            fillcolour=fillcolour,
        )
        self.flippable = flippable
        self.movable = movable
        self.bind("click", flip_card)
        self.update()

    def update(self):
        super().update()

        try:
            # stderr.write(f"{self.attrs['x']=}")
            # stderr.write(f"{self.attrs['y']=}")
            if (
                self.attrs["id"]
                and self.attrs["show_face"]
                and int(self.attrs["y"]) < card_height
            ):
                stderr.write(f"Throwing {self.id} ({self.attrs['y']=})")
        except KeyError:
            pass

        if self.show_face:
            self.attrs["href"] = CARD_URL + self.face_value
            self.style["fill"] = ""
        else:
            self.attrs["href"] = CARD_URL + "back"
            self.style["fill"] = "crimson"  # darkblue also looks "right"


def flip_card(event):
    # stderr.write("In flip_card()")
    # stderr.write(event.target)
    obj = document[event.target.id]
    if obj.flippable:
        obj.show_face = not obj.show_face
        obj.update()


def ondrop(event):
    """
    Triggered when an object is moved.

    :param event: The event generated by the browser
    :type event: event
    """
    stderr.write(f"{event.target=}")


def place_cards(deck, location="top", kitty=False):
    """
    Place the supplied deck / list of cards on the display. This will need to be
    refactored somewhat if a gradual kitty reveal is desired.

    :param deck: card names in the format that svg-cards.svg wants.
    :type deck: list
    :param location: String of "top", "bottom" or anything else, defaults to "top", instructing where to place the cards vertically.
    :type location: str, optional
    :param kitty: Whether or not to draw backs (True) or faces (False), defaults to False
    :type kitty: bool, optional
    """

    # Where to vertically place first card on the table
    if location.lower() == "top":
        start_y = 0
    elif location.lower() == "bottom":
        # Place cards one card height above the bottom, plus a bit.
        start_y = table_height - card_height - 2
    else:
        # Place cards in the middle.
        start_y = table_height / 2 - card_height / 2

    # Calculate how far to move each card horizontally and based on that calculate the
    # starting horizontal position.
    xincr = int(table_width / (len(deck) + 0.5))
    if xincr > card_width:
        xincr = card_width
        start_x = int(table_width / 2 - xincr * (len(deck) + 0.0) / 2)
    else:
        start_x = 0
    (xpos, ypos) = (start_x, start_y)

    for card_value in deck:
        if not kitty:
            piece = PlayingCard(face_value=card_value)
        else:
            piece = PlayingCard(
                face_value=card_value, show_face=False, flippable=True, movable=False
            )

        canvas.addObject(piece)
        canvas.translateObject(piece, (xpos, ypos))
        xpos += xincr
        if xpos > table_width - xincr:
            xpos = 0
            ypos += yincr


def calculate_dimensions():
    global table_width, table_height
    # Gather information about the display environment
    table_width = document["canvas"].clientWidth
    table_height = document["canvas"].clientHeight


def clear_canvas():
    while canvas.firstChild:
        canvas.removeChild(canvas.firstChild)


def update_display():
    calculate_dimensions()
    clear_canvas()

    # Last-drawn are on top (z-index wise)
    # place_cards(deck, location="blah")
    place_cards(discard_deck, kitty=True)
    place_cards(players_hand, location="bottom")
    SVGRoot <= canvas


window.update_display = update_display
# Locate the card table in the HTML document.
SVGRoot = document["card_table"]

table_width = 0
table_height = 0

# Create the base SVG object for the card table.
canvas = SVG.CanvasObject("95vw", "95vh", None, objid="canvas")
canvas.mouseMode = SVG.MouseMode.DRAG
SVGRoot <= canvas
canvas.setDimensions()

# Calculate relative vertical overlap for cards, if needed.
yincr = int(card_height / 4)

deck = list()
for decks in range(0, 2):  # Double deck
    for card in ["ace", "10", "king", "queen", "jack", "9"]:
        for suit in ["heart", "diamond", "spade", "club"]:
            deck.append(f"{suit}_{card}")

# Collect cards into discard and player's hand
discard_deck = sample(deck, k=4).sort()
for choice in discard_deck:
    deck.remove(choice)
players_hand = sample(deck, k=13).sort()
for choice in players_hand:
    deck.remove(choice)


update_display()
