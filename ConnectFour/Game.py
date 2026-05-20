from enum import Enum

class GameState(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WIN = "WIN"
    DRAW = "DRAW"

class Game:
    def __init__(self, board:Board, player1:Player, player2:Player, currentPlayer:Player, state:GameState, winnner:Player):
        pass

    def makeMove(self, player, column) -> bool:
        # check valid player
        # check game state
        # check valid column
        # place disc
        # check Win
        # elif check Draw
        # elif change player
        # return True
        if self.currentPlayer != player:
            return False
        
        if self.state != GameState.IN_PROGRESS:
            return False
        
        row = self.board.place_disc(column, player.color)
        if row == -1:
            return False

        if self.board.check_win(row, column, player.color):
            self.winner = player
            self.state = GameState.WIN
            raise #??
        elif self.board.ifFull():
            self.state = GameState.DRAW
            raise #??
        else:
            self.currentPlayer = self.player1 if self.currentPlayer == self.player2 else self.player2

        return True




