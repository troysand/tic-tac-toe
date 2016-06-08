"""
tic-tac-toe.py 

This file implements the game logic for a tic-tac-toe game. Tic-tac-toe
is played between two players, or between one player and the computer.
Players are randomly assigned to be X's or O's and then one player goes
first. Players take turns marking the board with their assigned letter
until one player gets three marks in a row (horzontally, vertically, or
diagonally). The player that does this first is the winner. If no moves 
are available and no player has won then the game is a draw.

The tic-tac-toe board looks like:

 0 | 1 | 2
---+---+---
 3 | 4 | 5
---+---+---
 6 | 7 | 8



"""

import random

X = 'X'
O = 'O'

class TicTacToe(object):

	class Player(object):
		def __init__( self, name, symbol ):
			"""Initialize the Player instance."""
			self.name = name
			self.symbol = symbol

	def __init__(self, playerOneName, playerTwoName):
		"""Initalize a TicTacToe instance."""
		self.board = [ ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ' ]
		# todo: randomize the X's and O's
		self.player1 = TicTacToe.Player(playerOneName, X)
		self.player2 = TicTacToe.Player(playerTwoName, O)


	def playerIsWinner( player ):
		"""Return True if the player has won, False otherwise."""

		# todo: implement game board check to determine if player has won
		return False

	def makeMove( self, player, square ):
		"""Marks the sqaure with the players symbol (X or O)."""
		self.board[square] = player.symbol

	def getBoardString(self):
		"""Get a formatted string that dispalys the current game board state."""
		boardString = ' {0} | {1} | {2}\n---+---+---\n {3} | {4} | {5}\n---+---+---\n {6} | {7} | {8}\n'.format(
			self.board[0], self.board[1], self.board[2],
			self.board[3], self.board[4], self.board[5], 
			self.board[6], self.board[7], self.board[8])
		return boardString


tictactoe = TicTacToe("troy", "computer")
tictactoe.makeMove(tictactoe.player1, 4)
tictactoe.makeMove(tictactoe.player2, 0)
print(tictactoe.getBoardString())