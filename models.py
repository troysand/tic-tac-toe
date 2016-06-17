"""
models.py - This file contains the class definitions for the Datastore
entities used by the Tic Tac Toe game. 
"""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

EMPTY_BOARD = '         '

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()

class TicTacToeGame(ndb.Model):
    """This class represents a Tic Tac Toe game."""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player2 = ndb.KeyProperty(required=False, kind='User')
    player1_symbol = ndb.StringProperty(required=True, default='X')
    player2_symbol = ndb.StringProperty(required=True, default='O')
    computer_game = ndb.BooleanProperty(required=True, default=True)
    number_of_moves = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)
    board = ndb.StringProperty(required=True, default=EMPTY_BOARD)

    @classmethod
    def new_one_player_game(cls, player1, player1_symbol):
        """
        Create a new Tic Tac Toe game initialized for one player against the 
        computer.
        """
        game = TicTacToeGame(player1=player1,
            player1_symbol='X',
            player2_symbol='O',
            player1_first=True,
            computer_game=True,
            number_of_moves=0,
            board=EMPTY_BOARD,
            game_over=False)

        game.put()
        return game

    @classmethod
    def new_two_player_game(cls, player1, player2):
        """
        Create a new Tic Tac Toe game initialized for two players.
        """
        game = TicTacToeGame(player1=player1,
            player2=player2,
            player1_symbol='X',
            player2_symbol='O',
            computer_game=False,
            number_of_moves=0,
            board=EMPTY_BOARD,
            game_over=False)

        game.put()
        return game

    def to_form(self, message):
        """
        Returns a TicTacToeGameForm representation of the game.
        """
        form = TicTacToeGameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player1_name = self.player1.get().name
        form.player1_symbol = self.player1_symbol
        if self.computer_game:
            form.player2_name = "Computer"
        else:
            form.player2_name = self.player2.get().name
        form.player2_symbol = self.player2_symbol
        form.computer_game = self.computer_game
        form.number_of_moves = self.number_of_moves
        form.game_over = self.game_over
        form.message = message
        #form.message = "Message"
        form.board = self.board

        return form

    def next_to_move(self):
        """
        Get the symbol of the next player to move. i.e. 'X' or 'O'
        """
        if (self.number_of_moves % 2 == 0):
            return self.player1_symbol
        else:
            return self.player2_symbol

    def end_game(self, winner):
        """
        Ends the game - 
        """
        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        if self.computer_game:
            score = TicTacToeScore(player1=self.player1,
                player1_symbol=self.player1.symbol,
                player2_symbol=self.player2_symbol,
                computer_game=True,
                date=date.today(), 
                winner=winner,
                number_of_moves=self.number_of_moves)
        score.put()

    def is_winner(self, player_symbol):
        """
        Determine if the player has won the game.
        """
        # todo: implement logic here to determine if there is a winner
        return False

    def make_move(self, player_symbol, square):
        """
        Make a tic-tac-toe move by marking a player's symbol into a given
        square.
        """
        if not self.game_over:
            # mark the symbol on the board
            boardlist = list(self.board)
            boardlist[square] = player_symbol
            self.board = "".join(boardlist)

            self.number_of_moves = self.number_of_moves + 1

            # determine if the move has created a winner
            if self.is_winner(player_symbol):
                self.end_game(player_symbol)
            elif self.number_of_moves >= 9:
                self.end_game('Draw')
            self.put


class TicTacToeScore(ndb.Model):
    """Score object"""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player2 = ndb.KeyProperty(required=False, kind='User')
    player1_symbol = ndb.StringProperty(required=True, default='X')
    player2_symbol = ndb.StringProperty(required=True, default='O')
    computer_game = ndb.BooleanProperty(required=True, default=True)
    date = ndb.DateProperty(required=True)
    winner = ndb.StringProperty(required=True)
    number_of_moves = ndb.IntegerProperty(required=True)

    def to_form(self):
        return TicTacToeScoreForm(player1=self.player1.get().name,
            player2=self.player2.get().name, 
            player1_symbol=self.player1_symbol,
            player2_symbol=self.player2_symbol,
            computer_game=self.computer_game,
            date=str(self.date), 
            winner=self.winner,
            number_of_moves=self.number_of_moves)

# class Game(ndb.Model):
#     """Game object"""
#     target = ndb.IntegerProperty(required=True)
#     attempts_allowed = ndb.IntegerProperty(required=True)
#     attempts_remaining = ndb.IntegerProperty(required=True, default=5)
#     game_over = ndb.BooleanProperty(required=True, default=False)
#     user = ndb.KeyProperty(required=True, kind='User')

#     @classmethod
#     def new_game(cls, user, min, max, attempts):
#         """Creates and returns a new game"""
#         if max < min:
#             raise ValueError('Maximum must be greater than minimum')
#         game = Game(user=user,
#                     target=random.choice(range(1, max + 1)),
#                     attempts_allowed=attempts,
#                     attempts_remaining=attempts,
#                     game_over=False)
#         game.put()
#         return game

#     def to_form(self, message):
#         """Returns a GameForm representation of the Game"""
#         form = GameForm()
#         form.urlsafe_key = self.key.urlsafe()
#         form.user_name = self.user.get().name
#         form.attempts_remaining = self.attempts_remaining
#         form.game_over = self.game_over
#         form.message = message
#         return form

#     def end_game(self, won=False):
#         """Ends the game - if won is True, the player won. - if won is False,
#         the player lost."""
#         self.game_over = True
#         self.put()
#         # Add the game to the score 'board'
#         score = Score(user=self.user, date=date.today(), won=won,
#                       guesses=self.attempts_allowed - self.attempts_remaining)
#         score.put()


# class Score(ndb.Model):
#     """Score object"""
#     user = ndb.KeyProperty(required=True, kind='User')
#     date = ndb.DateProperty(required=True)
#     won = ndb.BooleanProperty(required=True)
#     guesses = ndb.IntegerProperty(required=True)

#     def to_form(self):
#         return ScoreForm(user_name=self.user.get().name, won=self.won,
#                          date=str(self.date), guesses=self.guesses)


# class GameForm(messages.Message):
#     """GameForm for outbound game state information"""
#     urlsafe_key = messages.StringField(1, required=True)
#     attempts_remaining = messages.IntegerField(2, required=True)
#     game_over = messages.BooleanField(3, required=True)
#     message = messages.StringField(4, required=True)
#     user_name = messages.StringField(5, required=True)

class TicTacToeGameForm(messages.Message):
    """TicTacToeGameForm for outbound game state information."""
    urlsafe_key = messages.StringField(1, required=True)
    player1_name = messages.StringField(2, required=True)
    player1_symbol = messages.StringField(3, required=True)
    player2_name = messages.StringField(4, required=True)
    player2_symbol = messages.StringField(5, required=True)
    computer_game = messages.BooleanField(6, required=True)
    number_of_moves = messages.IntegerField(7, required=True)
    game_over = messages.BooleanField(8, required=True)
    message = messages.StringField(9, required=True)
    board = messages.StringField(10, required=True)

class TicTacToeNewGameForm(messages.Message):
    """Used to create a new tic tac toe game."""
    player1_name = messages.StringField(1, required=True)
    player2_name = messages.StringField(2, required=False)
    player1_symbol = messages.StringField(3, required=False)
    player2_symbol = messages.StringField(4, required=False)
    computer_game = messages.BooleanField(5, required=True)

class TicTacToeMakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    player_symbol = messages.StringField(1, required=True)
    square = messages.IntegerField(2, required=True)

class TicTacToeScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    player1_name = messages.StringField(1, required=True)
    player2_name = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    winner = messages.StringField(4, required=True)
    number_of_moves = messages.IntegerField(5, required=True)

class TicTacToeScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(TicTacToeScoreForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, default=10)
    attempts = messages.IntegerField(4, default=5)

# class MakeMoveForm(messages.Message):
#     """Used to make a move in an existing game"""
#     guess = messages.IntegerField(1, required=True)


# class ScoreForm(messages.Message):
#     """ScoreForm for outbound Score information"""
#     user_name = messages.StringField(1, required=True)
#     date = messages.StringField(2, required=True)
#     won = messages.BooleanField(3, required=True)
#     guesses = messages.IntegerField(4, required=True)


# class ScoreForms(messages.Message):
#     """Return multiple ScoreForms"""
#     items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
