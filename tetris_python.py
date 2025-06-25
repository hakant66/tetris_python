# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 13:48:27 2025
@author: hakan
to show usage of Tkinter library for GUI 
"""
import tkinter as tk # Import the Tkinter library for GUI development
from tkinter import messagebox # Import messagebox for pop-up messages
import random # Import random for selecting random Tetrominoes
import time # Import time (though not strictly necessary for this specific implementation of the game loop, sometimes used for delays)

# --- Game Configuration ---
# Define constants for the game board dimensions and block size.
BOARD_WIDTH = 10 # Number of blocks wide the game board is
BOARD_HEIGHT = 20 # Number of blocks high the game board is
BLOCK_SIZE = 30 # Size of each square block in pixels (e.g., 30x30 pixels)

# Define a dictionary of colors for each Tetromino type and for the game board.
COLORS = {
    'I': '#00FFFF', # Cyan for the 'I' shape
    'O': '#FFFF00', # Yellow for the 'O' shape
    'T': '#800080', # Purple for the 'T' shape
    'S': '#00FF00', # Green for the 'S' shape
    'Z': '#FF0000', # Red for the 'Z' shape
    'J': '#0000FF', # Blue for the 'J' shape
    'L': '#FFA500', # Orange for the 'L' shape
    'G': '#808080', # Grey for blocks that have settled onto the board
    'B': '#2C3E50'  # Dark blue-grey for the background color of the game board
}

# Define Tetromino shapes as 2D lists (matrices).
# Each '1' represents a filled block, '0' represents an empty space.
# The dimensions (3x3 or 4x4) are designed to contain the piece and its rotations.
SHAPES = {
    'I': [[0, 0, 0, 0], # The 'I' piece (straight line) is 4x4 for rotation
          [1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, 0, 0]],
    'J': [[1, 0, 0],   # The 'J' piece
          [1, 1, 1],
          [0, 0, 0]],
    'L': [[0, 0, 1],   # The 'L' piece
          [1, 1, 1],
          [0, 0, 0]],
    'O': [[1, 1],      # The 'O' piece (square) is 2x2 and doesn't rotate visually
          [1, 1]],
    'S': [[0, 1, 1],   # The 'S' piece
          [1, 1, 0],
          [0, 0, 0]],
    'T': [[0, 1, 0],   # The 'T' piece
          [1, 1, 1],
          [0, 0, 0]],
    'Z': [[1, 1, 0],   # The 'Z' piece
          [0, 1, 1],
          [0, 0, 0]]
}

# A comprehensive dictionary storing information about each Tetromino type.
# 'shape': The actual 2D list representing the piece.
# 'color': The corresponding color from the COLORS dictionary.
# 'dim': The dimension (side length) of the square matrix that contains the shape (e.g., 3 for J,L,S,T,Z; 4 for I; 2 for O).
TETROMINOES = {
    'I': {'shape': SHAPES['I'], 'color': COLORS['I'], 'dim': 4},
    'J': {'shape': SHAPES['J'], 'color': COLORS['J'], 'dim': 3},
    'L': {'shape': SHAPES['L'], 'color': COLORS['L'], 'dim': 3},
    'O': {'shape': SHAPES['O'], 'color': COLORS['O'], 'dim': 2},
    'S': {'shape': SHAPES['S'], 'color': COLORS['S'], 'dim': 3},
    'T': {'shape': SHAPES['T'], 'color': COLORS['T'], 'dim': 3},
    'Z': {'shape': SHAPES['Z'], 'color': COLORS['Z'], 'dim': 3}
}


class TetrisGame:
    """
    Main class for the Tetris game application.
    Manages game state, UI elements, and game logic.
    """
    def __init__(self, master): # CORRECTED: Removed (object) from self parameter
        """
        Initializes the Tetris game. This is the constructor for the TetrisGame class.

        Args:
            master: The Tkinter root window instance (e.g., tk.Tk()) where the game will be displayed.
        """
        self.master = master # Store the main Tkinter window
        self.master.title("Tkinter Tetris") # Set the title of the game window
        self.master.resizable(False, False) # Prevent the game window from being resized (width, height)

        # Create the main game canvas where the Tetris blocks will be drawn.
        self.canvas = tk.Canvas(
            master, # Parent widget is the main window
            width=BOARD_WIDTH * BLOCK_SIZE, # Calculate canvas width based on board blocks and block size
            height=BOARD_HEIGHT * BLOCK_SIZE, # Calculate canvas height
            bg=COLORS['B'], # Set background color of the canvas (game board)
            highlightthickness=0 # Remove the default border highlight around the canvas
        )
        self.canvas.pack(padx=10, pady=10) # Place the canvas in the window with padding

        # Create a frame to hold game information (score, next piece)
        self.info_frame = tk.Frame(master, bg='#34495E') # Darker background for the info frame
        self.info_frame.pack(pady=10) # Place the info frame below the canvas

        # Label to display the current score.
        self.score_label = tk.Label(
            self.info_frame, # Parent widget is the info frame
            text="Score: 0", # Initial text
            font=("Inter", 16, "bold"), # Font style and size
            fg="white", # Foreground (text) color
            bg='#34495E', # Background color to match the info frame
            padx=10, pady=5 # Internal padding for the label
        )
        self.score_label.pack(side=tk.TOP, pady=(0, 10)) # Pack at the top of info_frame with top padding

        # Label to indicate the "Next Piece" display area.
        self.next_piece_label = tk.Label(
            self.info_frame,
            text="Next:",
            font=("Inter", 16, "bold"),
            fg="white",
            bg='#34495E'
        )
        self.next_piece_label.pack(side=tk.TOP)

        # Canvas for displaying the next upcoming Tetromino.
        self.next_piece_canvas = tk.Canvas(
            self.info_frame,
            width=4 * BLOCK_SIZE, # Canvas size (e.g., 4x4 blocks) to fit any Tetromino
            height=4 * BLOCK_SIZE,
            bg='#4A6572', # Slightly different background for visual separation
            highlightthickness=0
        )
        self.next_piece_canvas.pack(side=tk.TOP, padx=5, pady=5, expand=True) # Place it within the info frame

        # Bind keyboard events to game control functions.
        # These lines associate specific key presses with methods of the TetrisGame class.
        self.master.bind('<Left>', self.move_left) # Left arrow key moves piece left
        self.master.bind('<Right>', self.move_right) # Right arrow key moves piece right
        self.master.bind('<Down>', self.move_down) # Down arrow key performs a soft drop
        self.master.bind('<Up>', self.rotate_piece) # Up arrow key rotates the piece
        self.master.bind('<space>', self.hard_drop) # Spacebar performs a hard drop
        self.master.bind('<Escape>', self.pause_game) # Escape key pauses/resumes the game

        # --- Game State Variables ---
        # A 2D list (matrix) representing the game board.
        # Each cell stores the color of the settled block at that position, or '' if empty.
        self.board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = None # Stores the 2D list (shape matrix) of the currently falling Tetromino.
        self.current_color = None # Stores the color of the current piece.
        self.current_dim = None   # Stores the dimension (e.g., 3 or 4) of the current piece's shape matrix.
        self.current_x = 0        # X-coordinate (column) of the top-left corner of the current piece on the board.
        self.current_y = 0        # Y-coordinate (row) of the top-left corner of the current piece on the board.
        self.score = 0            # The player's current score.
        self.game_over = False    # Boolean flag: True if the game is over, False otherwise.
        self.paused = False       # Boolean flag: True if the game is paused, False otherwise.
        self.game_loop_id = None  # Stores the ID returned by master.after(), used to cancel the game loop.

        # A list to act as a queue for upcoming Tetrominoes.
        # This ensures players know what piece is next.
        self.piece_queue = []
        self.fill_piece_queue() # Initialize the queue with pieces

        self.start_game() # Call the method to start the game immediately upon initialization

    def fill_piece_queue(self):
        """
        Ensures the piece queue is filled with random tetrominoes.
        Shuffles the list of all Tetromino keys and extends the queue.
        """
        if not self.piece_queue: # Check if the queue is empty
            keys = list(TETROMINOES.keys()) # Get all Tetromino names (e.g., 'I', 'J', 'L')
            random.shuffle(keys) # Randomize the order of these names
            self.piece_queue.extend(keys) # Add them to the end of the queue

    def get_next_piece_from_queue(self):
        """
        Retrieves and removes the next piece key from the piece queue.
        Calls fill_piece_queue to ensure there's always a piece ready.

        Returns:
            str: The key (name) of the next Tetromino (e.g., 'T', 'O').
        """
        self.fill_piece_queue() # Make sure the queue has pieces
        return self.piece_queue.pop(0) # Remove and return the first element from the queue

    def draw_next_piece(self):
        """
        Draws the next piece from the queue onto its dedicated `next_piece_canvas`.
        This gives the player a preview of the upcoming Tetromino.
        """
        self.next_piece_canvas.delete("all") # Clear anything currently drawn on the next piece canvas
        if self.piece_queue: # Only draw if there's a piece in the queue
            next_piece_key = self.piece_queue[0] # Get the key of the next piece without removing it
            next_piece_info = TETROMINOES[next_piece_key] # Get its shape, color, and dimension
            next_shape = next_piece_info['shape']
            next_color = next_piece_info['color']
            next_dim = next_piece_info['dim']

            for r in range(next_dim): # Iterate through rows of the next piece's shape matrix
                for c in range(next_dim): # Iterate through columns
                    if next_shape[r][c] == 1: # If there's a block at this position in the shape
                        # Calculate coordinates for drawing the block.
                        # (4 - next_dim) * BLOCK_SIZE / 2 is used to visually center the piece
                        # in the 4x4 next_piece_canvas, regardless of its actual dimension (2x2, 3x3, 4x4).
                        x1 = c * BLOCK_SIZE + (4 - next_dim) * BLOCK_SIZE / 2
                        y1 = r * BLOCK_SIZE + (4 - next_dim) * BLOCK_SIZE / 2
                        x2 = x1 + BLOCK_SIZE
                        y2 = y1 + BLOCK_SIZE
                        self.next_piece_canvas.create_rectangle( # Draw the rectangle representing the block
                            x1, y1, x2, y2,
                            fill=next_color, # Fill color
                            outline='black', # Border color
                            width=2 # Border width
                        )

    def start_game(self):
        """
        Resets the game state and begins a new game.
        Called at the start and after a "Game Over" restart.
        """
        self.board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)] # Clear the game board
        self.score = 0 # Reset score
        self.game_over = False # Reset game over flag
        self.paused = False # Ensure game is not paused
        self.update_score() # Update the score display to 0
        self.piece_queue = [] # Clear and refill piece queue for new game
        self.fill_piece_queue()
        self.spawn_piece() # Spawn the first piece
        self.game_loop() # Start the main game loop

    def spawn_piece(self):
        """
        Selects a new random Tetromino from the queue and places it at the top center of the board.
        Checks for immediate game over conditions.
        """
        piece_key = self.get_next_piece_from_queue() # Get the key of the next piece from the queue
        piece_info = TETROMINOES[piece_key] # Retrieve its full info
        self.current_piece = piece_info['shape'] # Set the current piece's shape
        self.current_color = piece_info['color'] # Set the current piece's color
        self.current_dim = piece_info['dim'] # Set the current piece's dimension
        # Calculate initial X position to center the piece horizontally
        self.current_x = BOARD_WIDTH // 2 - self.current_dim // 2
        self.current_y = 0 # Start the piece at the very top of the board

        # Check for immediate game over: if the new piece collides upon spawning
        if self.check_collision(self.current_piece, self.current_x, self.current_y):
            self.game_over = True # Set game over flag
            self.display_game_over() # Show game over message
        else:
            self.draw_board() # Redraw the board to show the newly spawned piece
            self.draw_next_piece() # Update the 'Next' piece display

    def draw_board(self):
        """
        Draws the entire game board on the canvas.
        Includes all settled blocks and the current falling piece.
        """
        self.canvas.delete("all") # Clear everything currently drawn on the main game canvas

        # Draw settled blocks (those merged into the self.board matrix)
        for r in range(BOARD_HEIGHT): # Iterate through each row of the board
            for c in range(BOARD_WIDTH): # Iterate through each column
                if self.board[r][c] != '': # If a block exists at this cell (not empty string)
                    color = self.board[r][c] # Get the color of the settled block
                    # Calculate pixel coordinates for the rectangle
                    x1, y1 = c * BLOCK_SIZE, r * BLOCK_SIZE
                    x2, y2 = x1 + BLOCK_SIZE, y1 + BLOCK_SIZE
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='black', width=2)

        # Draw the current falling piece (if game is not over)
        if self.current_piece and not self.game_over:
            for r in range(self.current_dim): # Iterate through rows of the current piece's shape matrix
                for c in range(self.current_dim): # Iterate through columns
                    if self.current_piece[r][c] == 1: # If there's a block in the piece's shape at (r, c)
                        # Calculate pixel coordinates for the falling block on the main board
                        x1, y1 = (self.current_x + c) * BLOCK_SIZE, (self.current_y + r) * BLOCK_SIZE
                        x2, y2 = x1 + BLOCK_SIZE, y1 + BLOCK_SIZE
                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.current_color, outline='black', width=2)

    def check_collision(self, piece, x, y):
        """
        Checks if the given `piece` (at potential `x`, `y` coordinates) collides
        with board boundaries or any already settled blocks.

        Args:
            piece: The shape matrix (2D list) of the piece to check.
            x: The proposed x-coordinate (column) of the piece's top-left corner.
            y: The proposed y-coordinate (row) of the piece's top-left corner.

        Returns:
            True if a collision is detected, False otherwise.
        """
        for r in range(len(piece)): # Iterate through rows of the piece's shape
            for c in range(len(piece[0])): # Iterate through columns
                if piece[r][c] == 1: # If this part of the piece is a solid block
                    board_x, board_y = x + c, y + r # Calculate its absolute position on the game board

                    # 1. Check horizontal boundaries (left and right walls)
                    if not (0 <= board_x < BOARD_WIDTH):
                        return True
                    # 2. Check vertical boundaries (bottom of the board)
                    if not (0 <= board_y < BOARD_HEIGHT):
                        return True
                    # 3. Check collision with existing blocks on the board
                    # Only check if the board_y is valid (prevents IndexError for blocks spawning off board)
                    if self.board[board_y][board_x] != '':
                        return True
        return False # No collision detected

    def merge_piece_to_board(self):
        """
        When a piece lands, this method merges its blocks into the static `self.board` matrix.
        After merging, it triggers line clearing.
        """
        for r in range(self.current_dim): # Iterate through rows of the current piece's shape
            for c in range(self.current_dim): # Iterate through columns
                if self.current_piece[r][c] == 1: # If this part of the piece is a solid block
                    # Place the block's color onto the main board at its absolute position
                    self.board[self.current_y + r][self.current_x + c] = self.current_color
        self.clear_lines() # After merging, immediately check and clear any full lines

    def clear_lines(self):
        """
        Iterates through the board from bottom to top, checks for and clears any full lines.
        Shifts all blocks above cleared lines down. Updates the score.
        """
        lines_cleared = 0 # Counter for how many lines were cleared in this operation
        # Create a new, empty board to reconstruct the state after clearing lines
        new_board = [['' for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        current_row = BOARD_HEIGHT - 1 # Start filling the new board from the bottom-most row

        # Iterate through the board from bottom to top
        for r in range(BOARD_HEIGHT - 1, -1, -1):
            is_full = True # Assume the current row is full
            for c in range(BOARD_WIDTH): # Check all columns in the current row
                if self.board[r][c] == '': # If any cell is empty, the line is not full
                    is_full = False
                    break # No need to check further columns in this row
            if not is_full: # If the line is NOT full, copy it to the new board
                for c in range(BOARD_WIDTH):
                    new_board[current_row][c] = self.board[r][c]
                current_row -= 1 # Move up one row in the new board for the next non-full line
            else:
                lines_cleared += 1 # If the line IS full, increment the counter

        self.board = new_board # Replace the old board with the new, cleared board
        self.score += lines_cleared * 100 # Add points for cleared lines (100 points per line)
        if lines_cleared == 4: # Special bonus for clearing 4 lines at once (a "Tetris")
            self.score += 400 # Additional 400 points
        self.update_score() # Update the score display on the UI

    def update_score(self):
        """Updates the score display label on the Tkinter UI."""
        self.score_label.config(text=f"Score: {self.score}") # Set the text of the score_label

    def game_loop(self):
        """
        The core game loop that drives the falling of Tetrominoes.
        It attempts to move the current piece down, handles collisions,
        and then reschedules itself to run again after a delay.
        """
        if self.game_over or self.paused: # If game is over or paused, stop the loop
            return

        # Attempt to move the piece down
        if not self.check_collision(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1 # Move the piece down by one row
        else:
            # If a collision is detected (piece has landed)
            self.merge_piece_to_board() # Merge the landed piece into the board
            self.spawn_piece() # Spawn a new piece

        self.draw_board() # Redraw the entire board to reflect changes

        # Schedule the next iteration of the game loop.
        # This creates a recurring timer event. The '500' means 500 milliseconds (0.5 seconds).
        self.game_loop_id = self.master.after(500, self.game_loop) # Store the ID to be able to cancel it later

    # --- Piece Movement Functions (called by keyboard binds) ---

    def move_left(self, event=None):
        """
        Moves the current piece one block to the left.
        Triggered by the '<Left>' arrow key.
        """
        if self.game_over or self.paused: return # Do nothing if game is over or paused
        # Check if moving left causes a collision
        if not self.check_collision(self.current_piece, self.current_x - 1, self.current_y):
            self.current_x -= 1 # Update the piece's x-coordinate
            self.draw_board() # Redraw the board to show the new position

    def move_right(self, event=None):
        """
        Moves the current piece one block to the right.
        Triggered by the '<Right>' arrow key.
        """
        if self.game_over or self.paused: return # Do nothing if game is over or paused
        # Check if moving right causes a collision
        if not self.check_collision(self.current_piece, self.current_x + 1, self.current_y):
            self.current_x += 1 # Update the piece's x-coordinate
            self.draw_board() # Redraw the board

    def move_down(self, event=None):
        """
        Moves the current piece one block down (soft drop).
        Triggered by the '<Down>' arrow key.
        This is essentially a manual trigger of one step of the game_loop's downward movement.
        """
        if self.game_over or self.paused: return # Do nothing if game is over or paused
        # Check if moving down causes a collision
        if not self.check_collision(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1 # Update the piece's y-coordinate
            self.draw_board() # Redraw the board
        else:
            # If it collides, it has landed, so merge and spawn a new one
            self.merge_piece_to_board()
            self.spawn_piece()

    def hard_drop(self, event=None):
        """
        Instantly drops the current piece to the lowest possible position.
        Triggered by the '<space>' bar.
        """
        if self.game_over or self.paused: return # Do nothing if game is over or paused
        # Repeatedly move the piece down until it collides
        while not self.check_collision(self.current_piece, self.current_x, self.current_y + 1):
            self.current_y += 1
        self.merge_piece_to_board() # Merge the piece immediately after it lands
        self.spawn_piece() # Spawn a new piece
        self.draw_board() # Redraw the board to show the new state

    def rotate_piece(self, event=None):
        """
        Rotates the current piece 90 degrees clockwise.
        Includes a simple "wall kick" mechanism to try and shift the piece
        if a rotation would otherwise cause a collision.
        Triggered by the '<Up>' arrow key.
        """
        if self.game_over or self.paused: return # Do nothing if game is over or paused

        # Create a new matrix for the rotated piece
        rotated_piece = [[0 for _ in range(self.current_dim)] for _ in range(self.current_dim)]
        for r in range(self.current_dim):
            for c in range(self.current_dim):
                # Apply the rotation transformation (clockwise 90 degrees)
                rotated_piece[c][self.current_dim - 1 - r] = self.current_piece[r][c]

        # First, check collision with the rotated piece at its current position
        if not self.check_collision(rotated_piece, self.current_x, self.current_y):
            self.current_piece = rotated_piece # If no collision, apply the rotation
            self.draw_board() # Redraw the board
        else:
            # If initial rotation causes a collision, try "wall kicks" (simple version)
            # This attempts to shift the piece slightly left or right to allow rotation.
            for offset_x in [-1, 1]: # Try moving 1 unit left, then 1 unit right
                if not self.check_collision(rotated_piece, self.current_x + offset_x, self.current_y):
                    self.current_x += offset_x # Apply the horizontal offset
                    self.current_piece = rotated_piece # Apply the rotation
                    self.draw_board() # Redraw
                    return # Rotation successful with kick, exit function
            # If no kick works, the piece cannot rotate in its current position, so do nothing.

    def pause_game(self, event=None):
        """
        Toggles the pause state of the game.
        When paused, the game loop stops; when unpaused, it resumes.
        Triggered by the '<Escape>' key.
        """
        self.paused = not self.paused # Toggle the paused flag

        if self.paused:
            if self.game_loop_id: # Check if there's an active game loop scheduled
                self.master.after_cancel(self.game_loop_id) # Cancel the next scheduled call of game_loop
                self.game_loop_id = None # Clear the ID
            messagebox.showinfo("Game Paused", "Press 'Esc' to resume.") # Inform the user
        else:
            self.game_loop() # If unpaused, restart the game loop immediately

    def display_game_over(self):
        """
        Stops the game loop, displays a "Game Over" message with the final score,
        and asks the player if they want to play again.
        """
        if self.game_loop_id: # If there's an active game loop
            self.master.after_cancel(self.game_loop_id) # Cancel it to fully stop the game
            self.game_loop_id = None

        # Display a message box asking to restart
        response = messagebox.askyesno(
            "Game Over", # Title of the message box
            f"Game Over!\nYour final score: {self.score}\nDo you want to play again?" # Message content
        )
        if response: # If the user clicks 'Yes'
            self.start_game() # Restart the game
        else: # If the user clicks 'No'
            self.master.destroy() # Close the main Tkinter window

# --- Main execution block ---
# This block ensures the code runs only when the script is executed directly.
if __name__ == "__main__":
    # Create the main Tkinter window instance. This is the root of the GUI application.
    root = tk.Tk()

    # Create an instance of the TetrisGame class, passing the root window.
    # This initializes the game, sets up the UI, and starts the game loop.
    game = TetrisGame(root)

    # Start the Tkinter event loop.
    # This line is crucial; it listens for user interactions (key presses, window events)
    # and keeps the GUI window open and responsive. It must be called at the end of the script.
    root.mainloop()
