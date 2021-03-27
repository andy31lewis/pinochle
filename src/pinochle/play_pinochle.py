"""
This is the module that handles Pinochle game play.
"""
from flask import abort

from pinochle import hand, round_
from pinochle.cards.const import SUITS
from pinochle.cards.utils import convert_to_svg_names, deal_hands
from pinochle.models import utils


def deal_pinochle(player_ids: list, kitty_len: int = 0, kitty_id: str = None) -> None:
    """
    Deal a deck of Pinochle cards into player's hands and the kitty.

    :param player_ids: [description]
    :type player_ids: list
    :param kitty_len: [description]
    :type kitty_len: int
    :param kitty_id: [description]
    :type kitty_id: str
    """
    # print(f"player_ids={player_ids}")
    hand_decks, kitty_deck = deal_hands(players=len(player_ids), kitty_cards=kitty_len)

    if kitty_len > 0 and kitty_id is not None:
        hand.addcards(hand_id=kitty_id, cards=convert_to_svg_names(kitty_deck))
    for index, __ in enumerate(player_ids):
        player_info = utils.query_player(player_ids[index])
        hand_id = str(player_info.hand_id)
        hand.addcards(hand_id=hand_id, cards=convert_to_svg_names(hand_decks[index]))


def submit_bid(round_id: str, player_id: str, bid: int):
    """
    This function processes a bid submission for a player.

    :param round_id:   Id of the round to delete
    :param game_id:    Id of the player submitting the bid
    :return:           200 on successful delete, 404 if not found,
                       409 if requirements are not satisfied.
    """
    # print(f"\nround_id={round_id}, player_id={player_id}")
    # Get the round requested
    a_round: dict = utils.query_round(round_id)
    player: dict = utils.query_player(player_id=player_id)

    # Did we find a round?
    if a_round is None or a_round == {}:
        abort(404, f"Round {round_id} not found.")

    # Did we find a player?
    if player is None or player == {}:
        abort(404, f"Player {player_id} not found.")

    # New bid must be higher than current bid.
    if a_round.bid >= bid:
        abort(409, f"Bid {bid} is below current bid {a_round.bid}.")

    return round_.update(round_id, {"bid": bid, "bid_winner": player_id})


def set_trump(round_id: str, player_id: str, trump: str):
    """
    This function processes trump submission by a player.

    :param round_id:   Id of the round to delete
    :param game_id:    Id of the player submitting the bid
    :return:           200 on successful delete, 404 if not found,
                       409 if requirements are not satisfied.
    """
    # print(f"\nround_id={round_id}, player_id={player_id}")
    # Get the round requested
    a_round: dict = utils.query_round(round_id)
    player: dict = utils.query_player(player_id=player_id)

    # Did we find a round?
    if a_round is None or a_round == {}:
        abort(404, f"Round {round_id} not found.")

    # Did we find a player?
    if player is None or player == {}:
        abort(404, f"Player {player_id} not found.")

    # New trump must not be already be set.
    # print("Bid winner=%s, player_id=%s" % (a_round.bid_winner, player_id))
    if str(a_round.bid_winner) != player_id:
        abort(409, f"Bid winner {a_round.bid_winner} must submit trump.")

    trump = trump.capitalize()
    if trump not in SUITS:
        abort(409, f"Trump suit must be one of {SUITS}.")

    return round_.update(round_id, {"trump": trump})
