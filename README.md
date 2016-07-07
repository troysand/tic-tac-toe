# Tic-Tac-Toe

## Set-Up Instructions:
1.  Edit app.yaml with an application id that you get from 
<http://console.developers.google.com>.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
[Tic-Tac-Toe ](https://en.wikipedia.org/wiki/Tic-tac-toe) is a game played between
two players on a 3x3 grid. Players are assigned to be either X's or O's and then one player goes 
first. Players take turns marking the board with their assigned letter until one 
player gets three marks in a row either horizontally, vertically or diagonally. 
The player that does this first is the winner. If no moves are available and no 
player has won then the game is a draw.

###Game Board
The tic-tac-toe board looks like:
```
   |   |  
---+---+---
   |   | 
---+---+---
   |   | 
```

###Game Example
A full game of tic-tac-toe might look like this:
```
1)  X |   |    2)  X |   |    3)  X |   |    4)  X | O |    5)  X | O |   
   ---+---+---    ---+---+---    ---+---+---    ---+---+---    ---+---+---
      |   |          | O |          | O |          | O |        X | O |   
   ---+---+---    ---+---+---    ---+---+---    ---+---+---    ---+---+---
      |   |          |   |        X |   |        X |   |        X |   |   
```

In the example above, player 1 (X's) won the game by getting three X's in column 1.

###Playing the Game
In this version of tic-tac-toe, the squares are numbered from 0 to 8. The 
board below shows each of the square numbers on the grid:

```
 0 | 1 | 2
---+---+---
 3 | 4 | 5
---+---+---
 6 | 7 | 8
```

A player makes
a move by calling the make_move endpoint with the player's symbol and the square
the player wishes to mark. After a legal move has been made, A TicTacToeGameForm
is returned representing the new game state, and with a message indicating
whether the game is over or if it is the next player's turn.

###Scoring
In this implementation of tic-tac-toe, players receive 3 points for a win, 1 point for
a draw, and 0 points for a loss.

###Player Rankings
Players are ranked according to their averages scores. The average score is determined by 
adding up a players total score and dividing by the number of games played.

##Files Included:
 - api.py: 
 - app.yaml: 
 - cron.yaml: 
 - main.py: 
 - models.py: 
 - utils.py: 

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, min, max, attempts
    - Returns: TicTacToeGameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: TicTacToeGameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, player symbol, square
    - Returns: TicTacToeGameForm with new game state.
    - Description: Makes a move in a tic-tac-toe game. Takes a player symbol
    and a square number and then marks the square with the player's symbol.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: TicTacToeScoreForms.
    - Description: Returns all TicTacToeScores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: TicTacToeScoreForms. 
    - Description: Returns all TicTacToeScores recorded by the provided player 
    (unordered).

- **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name 
    - Returns: TicTacToeGameForms
    - Description: Gets all of the active games for a user.

- **cancel_game**
    - Path: 'game/cancel/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key 
    - Returns: TicTacToeGameForms
    - Description: Cancels a game in progress, and deletes the game from the 
    datastore. Cannot be used to delete a game that has already finished.

- **get_user_rankings**
    - Path: 'scores/rankings'
    - Method: GET
    - Parameters: None
    - Returns: TicTacToePlayerRankingForms 
    - Description: Gets the player game record and rankings in order from 
    highest ranking to lowest.

- **get_game_history**
    - Path: game/history/{urlsafe_game_key}
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: TicTacToeGameHistoryForm
    - Description: Gets the game history showing each player's moves in
    the proper order.
    

##Models Included:
 - **User**
    - Stores unique user name and (optional) email address.
    
 - **TicTacToeGame**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **TicTacToeScore**
    - Records completed games. Associated with Users model via KeyProperty.

 - **TicTacToePlayerRanking**
    - Contains the player's game record and current ranking.
    
##Forms Included:
 - **TicTacToeGameForm**
    - Representation of a Game's state (urlsafe_key, player1_name, player2_name, computer_game flag, number_of_moves, game_over flag, message, board).
 - **TicTacToeNewGameForm**
    - Used to create a new game (player1_name, player2_name, player1_symbol, 
    player2_symbol, computer_game flag)
 - **TicTacToeMakeMoveForm**
    - Inbound make move form (move).
 - **TicTacToeScoreForm**
    - Representation of a completed game's Score (player1_name, player2_name, 
    date, winner, number_of_moves).
 - **TicTacToeScoreForms** 
    - Multiple ScoreForm container.
 - **TicTacToePlayerRankingForm**
    - Representation of the player's game record, including wins, draws, 
    total games and current ranking.
 - **TicTacToePlayerRankingForms**
    - Multiple TicTacToePlayerRankingForm container.
 - **TicTacToeSingleMoveForm**
    - Representation of a single move in a game history.
 - **TicTacToeGameHistoryForm**
    - A representation of a game showing each move in order.
 - **StringMessage**
    - General purpose String container.