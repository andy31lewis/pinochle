"""
This is the game module and supports all the REST actions for the
game data
"""
from flask import abort, make_response

from pinochle.models import utils
from pinochle.models.core import db
from pinochle.models.game import GameSchema

# Suppress invalid no-member messages from pylint.
# pylint: disable=no-member


def read_all():
    """
    This function responds to a request for /api/game
    with the complete lists of games

    :return:        json string of list of games
    """
    # Create the list of game from our data
    # games = Game.query.order_by(Game.timestamp).all()
    games = utils.query_game_list()

    # Serialize the data for the response
    game_schema = GameSchema(many=True)
    data = game_schema.dump(games)
    return data


def read_one(game_id: str):
    """
    This function responds to a request for /api/game/{game_id}
    with one matching game from game

    :param game_id:    Id of game to find
    :return:           game matching id
    """
    # Build the initial query
    game = utils.query_game(game_id=game_id)

    # Did we find a game?
    if game is not None:
        # Serialize the data for the response
        game_schema = GameSchema()
        data = game_schema.dump(game)
        return data

    # Otherwise, nope, didn't find that game
    abort(404, f"Game not found for Id: {game_id}")


def create(kitty_size=0):
    """
    This function creates a new game in the game structure

    :param kitty_size:  Number of cards to allocate to the kitty, optional
    :type kitty_size:   int
    :return:            201 on success, 406 on game exists
    """

    # print(f"game.create: kitty_size={kitty_size}")
    # Create a game instance using the schema and the passed in game
    schema: GameSchema = GameSchema()
    new_game = schema.load({"kitty_size": kitty_size}, session=db.session)
    # print(f"game.create: new_game={new_game}")

    # Add the game to the database
    db.session.add(new_game)
    db.session.commit()

    # Serialize and return the newly created game in the response
    data = schema.dump(new_game)

    return data, 201


def update(game_id: str, kitty_size: int):
    """
    This function updates an existing game in the game structure

    :param game_id:     Id of the game to update in the game structure
    :param kitty_size:  Size of the new kitty.
    :return:            Updated record.
    """
    return _update_data(game_id, {"kitty_size": kitty_size})


def _update_data(game_id: str, data: dict):
    """
    This function updates an existing game in the game structure

    :param game_id:     Id of the game to update in the game structure
    :param data:        Dictionary containing the data to update.
    :return:            Updated record.
    """
    # Get the game requested from the db into session
    update_game = utils.query_game(game_id=game_id)

    # Did we find an existing game?
    if update_game is None or update_game == {}:
        # Otherwise, nope, didn't find that game
        abort(404, f"Game not found for Id: {game_id}")

    # turn the passed in game into a db object
    db_session = db.session()
    local_object = db_session.merge(update_game)

    # Update any key present in game that isn't game_id or game_seq.
    for key in [x for x in data if x not in ["game_id", "game_seq"]]:
        setattr(local_object, key, data[key])

    # Add the updated data to the transaction.
    db_session.add(local_object)
    db_session.commit()

    # return updated game in the response
    schema = GameSchema()
    data = schema.dump(update_game)

    return data, 200


def delete(game_id: str):
    """
    This function deletes a game from the game structure

    :param game_id:   Id of the game to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the game requested
    game = utils.query_game(game_id=game_id)

    # Did we find a game?
    if game is None or game == {}:
        # Otherwise, nope, didn't find that game
        abort(404, f"Game not found for Id: {game_id}")

    db.session.delete(game)
    db.session.commit()
    return make_response(f"Game {game_id} deleted", 200)
