# -*- coding: utf-8 -*-`
"""
api.py - Create and configure the Tic Tac Toe game API.

"""

import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, TicTacToeGame, TicTacToeScore
from models import StringMessage, TicTacToeNewGameForm, TicTacToeGameForm
from models import TicTacToeMakeMoveForm, TicTacToeScoreForms
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
    if request.user_name == "Computer":
      raise endpoints.ConflictException('Cannot create user: Computer')
    if User.query(User.name == request.user_name).get():
      raise endpoints.ConflictException('User name already exists!')
    user = User(name=request.user_name, email=request.email)
    user.put()
    return StringMessage(message='User {} created!'.format(request.user_name))

  @endpoints.method(request_message=NEW_GAME_REQUEST,
                    response_message=TicTacToeGameForm,
                    path='game',
                    name='new_game',
                    http_method='POST')
  def new_game(self, request):
    """Creates new game"""
    player1 = User.query(User.name == request.player1_name).get()
    if not player1:
      raise endpoints.NotFoundException('Player 1 does not exist!')

    # If the user requested a game against the computer, then create
    # a new one-player game. Otherwise, get the second player's name
    # and make sure the user exists. Then create a two-player game.
    if request.computer_game:
      game = TicTacToeGame.new_one_player_game(player1.key)
    else:
      if not request.player2_name:
        raise BadRequestException('Player 2 name required except when playing against the computer.')
      player2 = User.query(User.name == request.player2_name).get()
      if not player2:
        raise endpoints.NotFoundException('Player 2 does not exist!')
      game = TicTacToeGame.new_two_player_game(player1.key, player2.key)
      

    # Use a task queue to update the average attempts remaining.
    # This operation is not needed to complete the creation of a new game
    # so it is performed out of sequence.
    #
    # Todo: implement a task queue task
    #
    #taskqueue.add(url='/tasks/cache_average_attempts')
    return game.to_form('Good luck playing Tic Tac Toe!')

  @endpoints.method(request_message=GET_GAME_REQUEST,
                    response_message=TicTacToeGameForm,
                    path='game/{urlsafe_game_key}',
                    name='get_game',
                    http_method='GET')
  def get_game(self, request):
    """Return the current game state."""
    game = get_by_urlsafe(request.urlsafe_game_key, TicTacToeGame)
    if game:
      return game.to_form('Time to make a move!')
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
    game.make_move(request.player_symbol, request.square)
    if game.game_over:
      return game.to_form('Game over!')
    return game.to_form("{} moved, now it's {}'s turn.".format(request.player_symbol,
      game.next_to_move()))

  # @endpoints.method(response_message=ScoreForms,
  #                   path='scores',
  #                   name='get_scores',
  #                   http_method='GET')
  # def get_scores(self, request):
  #   """Return all scores"""
  #   return ScoreForms(items=[score.to_form() for score in Score.query()])

  # @endpoints.method(request_message=USER_REQUEST,
  #                   response_message=ScoreForms,
  #                   path='scores/user/{user_name}',
  #                   name='get_user_scores',
  #                   http_method='GET')
  # def get_user_scores(self, request):
  #   """Returns all of an individual User's scores"""
  #   user = User.query(User.name == request.user_name).get()
  #   if not user:
  #     raise endpoints.NotFoundException('A User with that name does not exist!')
  #   scores = Score.query(Score.user == user.key)
  #   return ScoreForms(items=[score.to_form() for score in scores])

  # @endpoints.method(response_message=StringMessage,
  #                   path='games/average_attempts',
  #                   name='get_average_attempts_remaining',
  #                   http_method='GET')
  # def get_average_attempts(self, request):
  #   """Get the cached average moves remaining"""
  #   return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')

  # @staticmethod
  # def _cache_average_attempts():
  #   """Populates memcache with the average moves remaining of Games"""
  #   games = Game.query(Game.game_over == False).fetch()
  #   if games:
  #     count = len(games)
  #     total_attempts_remaining = sum([game.attempts_remaining for game in games])
  #     average = float(total_attempts_remaining)/count
  #     memcache.set(MEMCACHE_MOVES_REMAINING,
  #       'The average moves remaining is {:.2f}'.format(average))

api = endpoints.api_server([TicTacToeApi])
