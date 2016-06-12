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
two human players, or between one human player and a computer player. Players are
assigned to be either X's or O's and then one player goes first. Players take turns marking the board with their assigned letter until on player gets three marks in 
a row (horizontally, vertically or diagonally). The player that does this first is
the winner. If no moves are available and no player has won then the game is a draw.

The tic-tac-toe board looks like:
```
   |   |  
---+---+---
   |   | 
---+---+---
   |   | 
```

A full game of tic-tac-toe might look like this:
```
1)  X |   |    2)  X |   |    3)  X |   |    4)  X | O |    5)  X | O |   
   ---+---+---    ---+---+---    ---+---+---    ---+---+---    ---+---+---
      |   |          | O |          | O |          | O |        X | O |   
   ---+---+---    ---+---+---    ---+---+---    ---+---+---    ---+---+---
      |   |          |   |        X |   |        X |   |        X |   |   
```

In the example above, player 1 (X's) won the game by getting three X's in column 1.

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
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

- **get_user_games**

- **cancel_game**

- **get_high_scores**

- **get_user_rankings**

- **get_game_history**
    

##Models Included:
 - **User**
    - Stores unique user name and (optional) email address.
    
 - **TicTacToeGame**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **TicTacToeScore**
    - Records completed games. Associated with Users model via KeyProperty.
    
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
 - **StringMessage**
    - General purpose String container.