import numpy as np
import random

def randPair(s,e, legal_pos=None):
    return np.random.randint(s,e), np.random.randint(s,e)

class BoardPiece:
    
    def __init__(self, name, code, pos):
        self.name = name #name of the piece
        self.code = code #an ASCII character to display on the board
        self.pos = pos #2-tuple e.g. (1,4)

class GridBoard:
    def __init__(self, size=4):
        self.size = size #Board dimensions, e.g. 4 x 4
        self.components = {} #name : board piece
        self.components["Walls"] = []
        self.components["Goals"] = []
        self.components["Pits"] = []
        self.components["Paths"] = []
        self.starting_pos = (0,0)
    
    def addPiece(self, name, code, pos=(0,0)):
        newPiece = BoardPiece(name, code, pos)
        if name == 'Wall':
            self.components['Walls'].append(newPiece)
        if name == 'Goal':
            self.components['Goals'].append(newPiece)
        if name == 'Pit':
            self.components['Pits'].append(newPiece)
        if name == 'Path':
            self.components['Paths'].append(newPiece)
        else:
            self.components[name] = newPiece
    
    def movePiece(self, name, pos):
        self.components[name].pos = pos
    
    def delPiece(self, name):
        if name == "Wall":
            self.components["Walls"].pop()
        elif name == "Pit":
            self.components["Pits"].pop()
        elif name == "Goal":
            self.components["Goals"].pop()
        elif name == "Path":
            self.components["Paths"].pop()
        else:
            del self.components[name]
    
    def render(self):
        dtype = '<U2'
        displ_board = np.zeros((self.size, self.size), dtype=dtype)
        displ_board[:] = ' '
        
        for name, piece in self.components.items():
            if name == 'Walls':
                for wall in piece:
                    displ_board[wall.pos] = wall.code
            elif name == 'Pits':
                for pit in piece:
                    displ_board[pit.pos] = pit.code
            elif name == 'Paths':
                for path in piece:
                    displ_board[path.pos] = path.code
            elif name == 'Goals':
                for goal in piece:
                    displ_board[goal.pos] = goal.code
            else:
                displ_board[piece.pos] = piece.code
        player = self.components["Player"]
        displ_board[player.pos] = player.code
        return displ_board
    
    def render_np(self):
        num_pieces = len(self.components)
        displ_board = np.zeros((num_pieces, self.size, self.size), dtype=np.uint8)
        layer = 0
        for name, piece in self.components.items():
            if name == 'Walls':
                for wall in piece:
                    pos = (layer,) + wall.pos
                    displ_board[pos] = 1
                    layer += 1
            elif name == 'Pits':
                for pit in piece:
                    pos = (layer,) + pit.pos
                    displ_board[pos] = 1
                    layer += 1
            elif name == 'Paths':
                for path in piece:
                    pos = (layer,) + path.pos
                    displ_board[pos] = 1
                    layer += 1
            elif name == 'Goals':
                for goal in piece:
                    pos = (layer,) + goal.pos
                    displ_board[pos] = 1
                    layer += 1
            else:
                pos = (layer,) + piece.pos
                displ_board[pos] = 1
                layer += 1
        return displ_board
        
        
def addTuple(a,b):
    return tuple([sum(x) for x in zip(a,b)])
        
class Gridworld:
    def __init__(self, size=4, mode='static'):
        if size >= 4:
            self.board = GridBoard(size=size)
        else:
            print("Minimum board size is 4. Initialized to size 4.")
            self.board = GridBoard(size=4)
        
        #Add pieces, positions will be updated later
            
        if mode == 'static':
            self.initGridStatic()
        elif mode == 'player':
            self.initGridPlayer()
        else:
            self.initGridRand()
    
    #Initialize stationary grid, all items are placed deterministically
    def initGridStatic(self):
        #Setup static pieces
        self.board.addPiece('Player', 'P', (0,3))
        self.board.addPiece('Goal', 'G', (0,0))
        self.board.addPiece('Pit', 'O', (0,1))
        self.board.addPiece('Wall', 'X', (2,0))

    #Check if board is initialized appropriately (no overlapping pieces)
    def validateBoard(self):
        all_positions = []
        for name, piece in self.board.components.items():
            if name == 'Walls':
                for wall in piece:
                    all_positions.append(wall.pos)
            elif name == 'Goals':
                for goal in piece:
                    all_positions.append(goal.pos)
            elif name == 'Pits':
                for pit in piece:
                    all_positions.append(pit.pos)
            else:
                all_positions.append(piece.pos)
        if len(all_positions) > len(set(all_positions)):
            return False
        else:
            return True

    #Initialize player in random location, but keep wall, goal and pit stationary
    def initGridPlayer(self):
        #height x width x depth (number of pieces)
        self.initGridStatic()
        #place player
        self.board.components['Player'].pos = randPair(0,self.board.size)

        if (not self.validateBoard()):
            #print('Invalid grid. Rebuilding..')
            self.initGridPlayer()

    #Initialize grid so that goal, pit, wall, player are all randomly placed
    def initGridRand(self):
        #height x width x depth (number of pieces)
        legal_pos = []
        player_pos = []
        for i in range(0, self.board.size):
            for j in range(0, self.board.size-1):
                legal_pos.append((i,j))
                if j == 0:
                    player_pos.append((i,j))

        propose_pos = random.choice(player_pos)
        self.board.addPiece('Player', 'P', propose_pos)
        self.board.starting_pos = propose_pos
        legal_pos.remove(propose_pos)

        propose_pos = random.choice(legal_pos)
        for j in range(0, self.board.size):
            self.board.addPiece('Goal', 'G', (j, self.board.size-1))
        legal_pos.remove(propose_pos)


        placed_walls = 0
        while placed_walls <= (self.board.size * self.board.size) / 10:
            propose_pos = random.choice(legal_pos)
            self.board.addPiece('Wall', 'W', propose_pos)
            legal_pos.remove(propose_pos)

            # Get rid of all the illegal stuff so that we have free spaces here
            illegal_moves = []
            illegal_moves.append((propose_pos[0]+1, propose_pos[1]))
            illegal_moves.append((propose_pos[0]+1, propose_pos[1]+1))
            illegal_moves.append((propose_pos[0]+1, propose_pos[1]-1))
            illegal_moves.append((propose_pos[0]-1, propose_pos[1]))
            illegal_moves.append((propose_pos[0]-1, propose_pos[1]+1))
            illegal_moves.append((propose_pos[0]-1, propose_pos[1]-1))
            illegal_moves.append((propose_pos[0], propose_pos[1]))
            illegal_moves.append((propose_pos[0], propose_pos[1]+1))
            illegal_moves.append((propose_pos[0], propose_pos[1]-1))

            for move in illegal_moves:
                if move in legal_pos:
                    legal_pos.remove(move)

            placed_walls += 1

        placed_pits = 0
        while placed_pits <= (self.board.size * self.board.size) / 20:
            propose_pos = random.choice(legal_pos)
            self.board.addPiece('Pit', '-', propose_pos)
            legal_pos.remove(propose_pos)
            # Get rid of all the illegal stuff so that we have free spaces here
            illegal_moves = []
            illegal_moves.append((propose_pos[0]+1, propose_pos[1]))
            illegal_moves.append((propose_pos[0]+1, propose_pos[1]+1))
            illegal_moves.append((propose_pos[0]+1, propose_pos[1]-1))
            illegal_moves.append((propose_pos[0]-1, propose_pos[1]))
            illegal_moves.append((propose_pos[0]-1, propose_pos[1]+1))
            illegal_moves.append((propose_pos[0]-1, propose_pos[1]-1))
            illegal_moves.append((propose_pos[0], propose_pos[1]))
            illegal_moves.append((propose_pos[0], propose_pos[1]+1))
            illegal_moves.append((propose_pos[0], propose_pos[1]-1))

            for move in illegal_moves:
                if move in legal_pos:
                    legal_pos.remove(move)

            placed_pits += 1
        
    def makeMove(self, action):
        #need to determine what object (if any) is in the new grid spot the player is moving to
        #actions in {u,d,l,r}
        def checkMove(addpos=(0,0)):
            player = self.board.components['Player']
            new_pos = addTuple(self.board.components['Player'].pos, addpos)
            valid = self.valid_move(new_pos)
            if valid:
                if player.pos == self.board.starting_pos:
                    self.board.addPiece('Path', 'S', player.pos)
                elif self.is_pit(player.pos):
                    self.board.addPiece('Path', 'X', player.pos)
                else:
                    self.board.addPiece('Path', '*', player.pos)
                self.board.movePiece('Player', new_pos)
                return True
            else:
                return False
        if action == 'u': #up
            return checkMove((-1,0))
        elif action == 'd': #down
            return checkMove((1,0))
        elif action == 'l': #left
            return checkMove((0,-1))
        elif action == 'r': #right
            return checkMove((0,1))
        else:
            return False
    
    def valid_move(self, pos):
        legal_move = True

        # If its a wall
        for wall in self.board.components['Walls']:
            if pos == wall.pos:
                legal_move = False
        
        # out of bounds in rows
        if pos[0] < 0 or pos[0] >= self.board.size:
            legal_move = False

        # out of bounds in cols
        if pos[1] < 0 or pos[1] >= self.board.size:
            legal_move = False
        
        return legal_move
    
    # Check if a position is a goal node.
    def is_goal(self, pos):
        for goal in self.board.components['Goals']:
            if pos == goal.pos:
                return True
        
        return False

    def is_wall(self, pos):
        for wall in self.board.components['Walls']:
            if pos == wall.pos:
                return True
        
        return False

    def is_pit(self, pos):
        for pit in self.board.components['Pits']:
            if pos == pit.pos:
                return True
        
        return False

    def is_player(self, pos):
        if pos == self.board.components['Player'].pos:
            return True
        return False
    
    def mark_trace(self, trace):
        for (pos, _, _) in trace:
            if not self.is_goal(pos) and not self.is_player(pos):
                self.board.addPiece('Path', '*', pos)
            if self.is_pit(pos):
                self.board.addPiece('Path', 'X', pos)
            if self.is_goal(pos):
                self.board.addPiece('Path', '$', pos)
    
    def remove_trace(self):
        while self.board.components['Paths']:
            self.board.delPiece('Path')

    def getReward(self):
        if (self.board.components['Player'].pos == self.board.components['Pit'].pos):
            return -10
        elif (self.board.components['Player'].pos == self.board.components['Goal'].pos):
            return 10
        else:
            return -1

    def dispGrid(self):
        print(self.board.render())
