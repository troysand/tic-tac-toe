"""
models.py - This file contains the class definitions for the Datastore
entities used by the Tic Tac Toe game. 
"""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

# Empty board used to initialize the board for a new game. Also used
# to initialize the moves string.
EMPTY_BOARD = '         '

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty(required=False)

class TicTacToeGame(ndb.Model):
    """This class represents a Tic Tac Toe game."""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player2 = ndb.KeyProperty(required=True, kind='User')
    player1_symbol = ndb.StringProperty(required=True, default='X')
    player2_symbol = ndb.StringProperty(required=True, default='O')
    number_of_moves = ndb.IntegerProperty(required=True, default=0)
    game_over = ndb.BooleanProperty(required=True, default=False)
    board = ndb.StringProperty(required=True, default=EMPTY_BOARD)
    moves = ndb.StringProperty(required=True, default=EMPTY_BOARD)

    @classmethod
    def new_two_player_game(cls, player1, player2):
        """
        Create a new Tic Tac Toe game initialized for two players.
        """
        game = TicTacToeGame(player1=player1,
            player2=player2,
            player1_symbol='X',
            player2_symbol='O',
            number_of_moves=0,
            game_over=False,
            board=EMPTY_BOARD,
            moves=EMPTY_BOARD)

        game.put()
        return game

    def cancel_game(self):
        """
        Delete a game from the datastore.
        """
        self.key.delete()


    def to_form(self, message=""):
        """
        Returns a TicTacToeGameForm representation of the game.
        """
        form = TicTacToeGameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.player1_name = self.player1.get().name
        form.player1_symbol = self.player1_symbol
        form.player2_name = self.player2.get().name
        form.player2_symbol = self.player2_symbol
        form.number_of_moves = self.number_of_moves
        form.game_over = self.game_over
        form.message = message
        form.board = self.board
        form.moves = self.moves

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

        # Calculate scores for each player. Players get 3 points for a win,
        # 1 point for a draw, and 0 points for a loss.
        if winner == 'Draw':
            player1_score = 1
            player2_score = 1
        else:
            if self.player1_symbol == winner:
                player1_score = 3
                player2_score = 0
            else:
                player1_score = 0
                player2_score = 3

        # Add the game to the score 'board'
        score = TicTacToeScore(player1=self.player1,
            player2=self.player2,
            player1_symbol=self.player1_symbol,
            player2_symbol=self.player2_symbol,
            player1_score=player1_score,
            player2_score=player2_score,
            date=date.today(), 
            winner=winner,
            number_of_moves=self.number_of_moves,
            game=self.key)
        score.put()

    def is_winner(self, player_symbol):
        """
        Determine if the player indicated by the given symbol is the winner.
        Returns True if the player has won or False otherwise.
        """
        
        winning_string = player_symbol * 3
        # Check each row for for a winning string
        if ((winning_string == self.board[0:3]) or
            (winning_string == self.board[3:6]) or
            (winning_string == self.board[6:9])):
            return True
        # Check each column for a winning string
        if ((winning_string == self.board[0:1] + self.board[3:4] + self.board[6:7]) or
            (winning_string == self.board[1:2] + self.board[4:5] + self.board[7:8]) or
            (winning_string == self.board[2:3] + self.board[5:6] + self.board[8:9])):
            return True
        # Check each diagonal for a winning string
        if ((winning_string == self.board[0:1] + self.board[4:5] + self.board[8:9]) or
            (winning_string == self.board[2:3] + self.board[4:5] + self.board[6:7])):
            return True

        return False

    def get_square(self, square):
        """
        Get the symbol occupying the given square. Returns the player's symbol
        that occupies the square or ' ' if the square is unoccupied.
        """
        return self.board[square:square+1]

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

            # save the move
            moveslist = list(self.moves)
            moveslist[self.number_of_moves] = str(square)
            self.moves = "".join(moveslist)

            self.number_of_moves = self.number_of_moves + 1

            # determine if the move has created a winner
            if self.is_winner(player_symbol):
                self.end_game(player_symbol)
            elif self.number_of_moves >= 9:
                self.end_game('Draw')
            self.put()


class TicTacToeScore(ndb.Model):
    """Score object"""
    player1 = ndb.KeyProperty(required=True, kind='User')
    player2 = ndb.KeyProperty(required=False, kind='User')
    player1_symbol = ndb.StringProperty(required=True, default='X')
    player2_symbol = ndb.StringProperty(required=True, default='O')
    player1_score = ndb.IntegerProperty(required=True, default=0)
    player2_score = ndb.IntegerProperty(required=True, default=0)
    date = ndb.DateProperty(required=True)
    winner = ndb.StringProperty(required=True)
    number_of_moves = ndb.IntegerProperty(required=True) 
    game = ndb.KeyProperty(required=True, kind='TicTacToeGame')

    def to_form(self):
        return TicTacToeScoreForm(player1_name=self.player1.get().name,
            player2_name=self.player2.get().name, 
            player1_symbol=self.player1_symbol,
            player2_symbol=self.player2_symbol,
            player1_score=self.player1_score,
            player2_score=self.player2_score,
            date=str(self.date), 
            winner=self.winner,
            number_of_moves=self.number_of_moves,
            urlsafe_game_key = self.game.urlsafe())

class TicTacToeGameForm(messages.Message):
    """TicTacToeGameForm for outbound game state information."""
    urlsafe_key = messages.StringField(1, required=True)
    player1_name = messages.StringField(2, required=True)
    player1_symbol = messages.StringField(3, required=True)
    player2_name = messages.StringField(4, required=True)
    player2_symbol = messages.StringField(5, required=True)
    number_of_moves = messages.IntegerField(7, required=True)
    game_over = messages.BooleanField(8, required=True)
    message = messages.StringField(9, required=True)
    board = messages.StringField(10, required=True)
    moves = messages.StringField(11, required=True)

class TicTacToeGameForms(messages.Message):
    """
    Return multiple TicTactoeGameForm.
    """
    games = messages.MessageField(TicTacToeGameForm, 1, repeated=True)

class TicTacToeNewGameForm(messages.Message):
    """
    Used to create a new tic tac toe game.
    """
    player1_name = messages.StringField(1, required=True)
    player2_name = messages.StringField(2, required=False)
    player1_symbol = messages.StringField(3, required=False)
    player2_symbol = messages.StringField(4, required=False)

class TicTacToeMakeMoveForm(messages.Message):
    """
    Used to make a move in an existing game.
    """
    player_symbol = messages.StringField(1, required=True)
    square = messages.IntegerField(2, required=True)

class TicTacToeScoreForm(messages.Message):
    """
    TicTacToeScoreForm for outbound score information
    """
    player1_name = messages.StringField(1, required=True)
    player1_symbol = messages.StringField(2, required=True)
    player2_name = messages.StringField(3, required=True)
    player2_symbol = messages.StringField(4, required=True)
    player1_score = messages.IntegerField(5, required=True)
    player2_score = messages.IntegerField(6, required=True)
    date = messages.StringField(7, required=True)
    winner = messages.StringField(8, required=True)
    number_of_moves = messages.IntegerField(9, required=True)
    urlsafe_game_key = messages.StringField(11, required=True)

class TicTacToeScoreForms(messages.Message):
    """
    Return multiple TicTacToeScoreForms.
    """
    items = messages.MessageField(TicTacToeScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """
    StringMessage-- outbound (single) string message
    """
    message = messages.StringField(1, required=True)
