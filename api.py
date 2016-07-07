# -*- coding: utf-8 -*-`
"""
api.py - Create and configure the Tic Tac Toe game API.

"""

import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import (
    StringMessage,
    TicTacToeGame,
    TicTacToeGameForm,
    TicTacToeGameForms,
    TicTacToeGameHistoryForm,
    TicTacToeMakeMoveForm,
    TicTacToeNewGameForm,
    TicTacToePlayerRanking,
    TicTacToePlayerRankingForms,
    TicTacToeScore,
    TicTacToeScoreForms,
    User,
)

from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(TicTacToeNewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    TicTacToeMakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):
    """
    Tic Tac Toe game API
    """

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a new user. Requires a unique user name."""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException('User name already exists!')
        user = User.new_user(request.user_name, request.email)
        return StringMessage(message='User {} created!'.format(user.name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=TicTacToeGameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """
        Creates new 2-player game. Player 1 and Player 2 must both already be
        registered users.
        """
        player1 = User.query(User.name == request.player1_name).get()
        if not player1:
            raise endpoints.NotFoundException('Player 1 does not exist!')

        player2 = User.query(User.name == request.player2_name).get()
        if not player2:
            raise endpoints.NotFoundException('Player 2 does not exist!')
        game = TicTacToeGame.new_two_player_game(player1.key, player2.key)

        # Use a task queue to update the average moves remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        #
        taskqueue.add(url='/tasks/cache_average_moves')
        return game.to_form('Good luck playing Tic Tac Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=TicTacToeGameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """
        Return the current game state. Raises NotFoundException if the game
        does not exist.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, TicTacToeGame)
        if game:
            if game.game_over:
                message = "This game has ended."
            else:
                message = "Time for '{}' to make a move!".format(
                    game.next_to_move())
            return game.to_form(message)
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=TicTacToeGameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, TicTacToeGame)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        # Check to see if the game has already ended
        if game.game_over:
            return game.to_form('Game already over!')

        # make sure it is the correct player's move
        if not (request.player_symbol == game.next_to_move()):
            raise endpoints.BadRequestException(
                "It's not {}'s turn!".format(request.player_symbol))

        # make sure that the square is a valid tic-tac-toe square
        if (request.square < 0 or request.square > 8):
            raise endpoints.BadRequestException(
                "That's an invalid move: {}".format(request.square))

        # make sure that the square is unoccupied
        current_symbol = game.get_square(request.square)
        if (current_symbol != " "):
            raise endpoints.BadRequestException(
                "There is already an {} in square {}".format(current_symbol,
                                                             request.square))

        message = game.make_move(request.player_symbol, request.square)
        return game.to_form(message)

    @endpoints.method(response_message=TicTacToeScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return TicTacToeScoreForms(
            items=[score.to_form() for score in TicTacToeScore.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=TicTacToeScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        # Get the scores for when the user was player1 or player2 and join the
        # results.
        scores1 = TicTacToeScore.query(TicTacToeScore.player1 == user.key)
        scores2 = TicTacToeScore.query(TicTacToeScore.player2 == user.key)
        score_items = [score.to_form() for score in scores1]
        score_items += [score.to_form() for score in scores2]
        return TicTacToeScoreForms(items=score_items)

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=TicTacToeGameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """
        Get a list of all of a user's active games.
        """
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games1 = TicTacToeGame.query(TicTacToeGame.player1 == user.key,
                                     TicTacToeGame.game_over is not True)
        games2 = TicTacToeGame.query(TicTacToeGame.player2 == user.key,
                                     TicTacToeGame.game_over is not True)
        game_items = [game.to_form() for game in games1]
        game_items += [game.to_form() for game in games2]
        return TicTacToeGameForms(games=game_items)

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """
        Cancel a game that has already been started.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, TicTacToeGame)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        if game.game_over:
            message = "This game has already ended."
        else:
            game.cancel_game()
            message = "The game has been cancelled."
        return StringMessage(message=message)

    @endpoints.method(response_message=TicTacToePlayerRankingForms,
                      path='scores/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """
        Return the user rankings
        """
        # Get the rankings in reverse order (from high to low)
        rankings = TicTacToePlayerRanking.query().order(
            -TicTacToePlayerRanking.ranking)
        return TicTacToePlayerRankingForms(
            items=[ranking.to_form() for ranking in rankings])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=TicTacToeGameHistoryForm,
                      path='game/history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """
        Return the move history for a game.
        """
        game = get_by_urlsafe(request.urlsafe_game_key, TicTacToeGame)
        if not game:
            raise endpoints.NotFoundException('Game not found!')
        return game.get_game_history_form()

    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_moves(self, request):
        """Get the cached average moves remaining"""
        return StringMessage(
            message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

    @staticmethod
    def _cache_average_moves():
        """
        Populates memcache with the average moves remaining of all unfinished
        tic-tac-toe games.
        """
        games = TicTacToeGame.query(TicTacToeGame.game_over is False).fetch()
        if games:
            count = len(games)
            total_num_moves = sum([game.number_of_moves for game in games])
            total_moves_remaining = 9 * count - total_num_moves
            average = float(total_moves_remaining) / count
            memcache.set(
                MEMCACHE_MOVES_REMAINING,
                'The average moves remaining is {:.2f}'.format(average))

api = endpoints.api_server([TicTacToeApi])
