import itertools
import copy
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1
        else:
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            pass

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def return_neighbors(self, cell):
        neighbors = set(cell)
        for rows in range(self.height):
            for cols in range(self.width):
                if abs(cell[0] - rows) <= 1 and abs(cell[1] - cols) <= 1 and (rows, cols) != cell:
                    neighbors.add((rows, cols))
        return neighbors

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #Marking the cell as one of the moves made in the game
        self.moves_made.add(cell)

        #Marking the cell as safe
        self.mark_safe(cell)

        #Adding new sentence to the Ai's knowlege base
        new_cells = set()
        cont_deepcpy = copy.deepcopy(count)

        neighboring_cells = self.return_neighbors(cell)

        for cl in neighboring_cells:
            if cl in self.mines:
                cont_deepcpy -= 1
            if cl not in self.mines or self.safes:
                new_cells.add(cl)

        new_sentence = Sentence(new_cells, cont_deepcpy)

        #adding the sentence only if not empty
        if len(new_sentence.cells) > 0:
            self.knowledge.append(new_sentence)

        self.check_knowledge()

        self.inference()

    def check_knowledge(self):
        knowledge_cpy = copy.deepcopy(self.knowledge)

        #iterating through each sentence
        for sentence in knowledge_cpy:
            if len(sentence.cells) == 0:
                try:
                    self.knowledge.remove(sentence)
                except ValueError:
                    pass

        #Getting all the mines and safes
            mines = sentence.known_mines()
            safes = sentence.known_safes()
            if mines:
                for mn in mines:
                    self.mark_mine(mn)
                    self.check_knowledge()
            if safes:
                for sf in safes:
                    self.mark_safe(sf)
                    self.check_knowledge()

    def inference(self):
        for sentence1 in self.knowledge:
            for sentence2 in self.knowledge:
                if sentence1.cells.issubset(sentence2.cells):
                    new_cells= sentence2.cells - sentence1.cells
                    new_count = sentence2.count = sentence1.count
                    new_sentence = Sentence(new_cells, new_count)

                    mines = new_sentence.known_mines()
                    safes = new_sentence.known_safes()
                    if mines:
                        for mn in mines:
                            self.mark_mine(mn)
                    if safes:
                        for sf in safes:
                            self.mark_safe(sf)

    def make_safe_move(self):
        """Returns a safe cell to choose on the Minesweeper board."""
        for cell in self.safes - self.moves_made:
            if isinstance(cell, tuple) and len(cell) == 2:
                return cell
        return None

    def make_random_move(self):
        """Returns a move to make on the Minesweeper board."""
        max_moves = self.width * self.height
        while max_moves > 0:
            max_moves -= 1
            rand_row = random.randrange(self.height)
            rand_col = random.randrange(self.width)
            move = (rand_row, rand_col)
            if move not in self.moves_made and move not in self.mines:
                return move
        return None

