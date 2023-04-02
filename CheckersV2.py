import pygame
import sys
import time

# Initialize Pygame
pygame.init()

# Screen constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False

    def draw(self, screen):
        radius = SQUARE_SIZE // 2 - 10
        x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(screen, self.color, (x, y), radius)
        if self.king:
            pygame.draw.circle(screen, WHITE, (x, y), radius // 2)

    def move(self, row, col):
        self.row = row
        self.col = col

    def is_clicked(self, x, y):
        piece_x = self.col * SQUARE_SIZE + SQUARE_SIZE // 2
        piece_y = self.row * SQUARE_SIZE + SQUARE_SIZE // 2
        distance = ((x - piece_x) ** 2 + (y - piece_y) ** 2) ** 0.5
        return distance < SQUARE_SIZE // 2 - 10

    def make_king(self):
        self.king = True


def check_promotion(piece):
    if piece.color == RED and piece.row == 0:
        piece.make_king()
    elif piece.color == BLUE and piece.row == ROWS - 1:
        piece.make_king()

def create_pieces():
    pieces = []
    for row in range(ROWS):
        row_pieces = []
        for col in range(COLS):
            if row % 2 != col % 2:
                if row < 3:
                    piece = Piece(row, col, BLUE)
                elif row > 4:
                    piece = Piece(row, col, RED)
                else:
                    piece = None
                row_pieces.append(piece)
            else:
                row_pieces.append(None)
        pieces.append(row_pieces)
    return pieces

def draw_board(screen, pieces):
    screen.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            if row % 2 != col % 2:
                pygame.draw.rect(screen, BLACK, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = pieces[row][col]
            if piece:
                piece.draw(screen)

def get_valid_moves(pieces, piece):
    capture_moves = get_capture_moves(pieces, piece)
    if capture_moves:
        return capture_moves

    row, col = piece.row, piece.col
    valid_moves = []
    capture_moves = []

    if piece.king:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    else:
        dir_mult = -1 if piece.color == RED else 1
        directions = [(dir_mult, -1), (dir_mult, 1)]

    for dr, dc in directions:
        newRow, newCol = row + dr, col + dc
        if 0 <= newRow < ROWS and 0 <= newCol < COLS and pieces[newRow][newCol] is None:
            valid_moves.append((newRow, newCol))

        newRow, newCol = row + 2 * dr, col + 2 * dc
        if 0 <= newRow < ROWS and 0 <= newCol < COLS and pieces[newRow][newCol] is None and pieces[row + dr][
            col + dc] is not None and pieces[row + dr][col + dc].color != piece.color:
            capture_moves.append((newRow, newCol))

    return capture_moves if capture_moves else valid_moves


def get_all_valid_moves(pieces, color):
    all_valid_moves = []

    for row in range(ROWS):
        for col in range(COLS):
            piece = pieces[row][col]
            if piece and piece.color == color:
                valid_moves = get_valid_moves(pieces, piece)
                if valid_moves:
                    all_valid_moves.append((piece, valid_moves))

    return all_valid_moves

def get_capture_moves(pieces, piece):
    row, col = piece.row, piece.col
    capture_moves = []

    if piece.king:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    else:
        dir_mult = -1 if piece.color == RED else 1
        directions = [(dir_mult, -1), (dir_mult, 1)]

    for dr, dc in directions:
        newRow, newCol = row + 2 * dr, col + 2 * dc
        if 0 <= newRow < ROWS and 0 <= newCol < COLS and pieces[newRow][newCol] is None and pieces[row + dr][col + dc] is not None and pieces[row + dr][col + dc].color != piece.color:
            capture_moves.append((newRow, newCol))

    return capture_moves

import random




def make_ai_move(pieces, color):

    all_valid_moves = get_all_valid_moves(pieces, color)
    capture_moves = []

    for piece, moves in all_valid_moves:
        for move in moves:
            dr, dc = abs(move[0] - piece.row), abs(move[1] - piece.col)
            if dr == 2 and dc == 2:
                capture_moves.append((piece, move))

    if capture_moves:
        piece, move = random.choice(capture_moves)
    elif all_valid_moves:
        piece, moves = random.choice(all_valid_moves)
        move = random.choice(moves)
    else:
        return

    oldRow, oldCol = piece.row, piece.col
    newRow, newCol = move
    pieces[oldRow][oldCol] = None
    piece.move(newRow, newCol)
    pieces[newRow][newCol] = piece
    check_promotion(piece)

    # Remove captured piece
    if abs(newRow - oldRow) == 2 and abs(newCol - oldCol) == 2:
        captured_row, captured_col = (oldRow + newRow) // 2, (oldCol + newCol) // 2
        pieces[captured_row][captured_col] = None

def check_win(pieces, color):
    for row in range(ROWS):
        for col in range(COLS):
            if pieces[row][col] is not None and pieces[row][col].color == color:
                return False
    return True

# Main loop
def main():
    pieces = create_pieces()
    run = True
    selected_piece = None
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not selected_piece:
                    x, y = pygame.mouse.get_pos()
                    row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                    clicked_piece = pieces[row][col]
                    if clicked_piece and clicked_piece.color == RED:
                        selected_piece = clicked_piece
                        last_move_capture = False
                else:
                    x, y = pygame.mouse.get_pos()
                    row, col = y // SQUARE_SIZE, x // SQUARE_SIZE
                    if (row, col) in get_valid_moves(pieces, selected_piece):
                        oldRow, oldCol = selected_piece.row, selected_piece.col
                        newRow, newCol = row, col
                        pieces[selected_piece.row][selected_piece.col] = None
                        selected_piece.move(newRow, newCol)
                        pieces[newRow][newCol] = selected_piece
                        check_promotion(selected_piece)

                        if abs(newRow - oldRow) == 2 and abs(newCol - oldCol) == 2:
                            captured_row, captured_col = (oldRow + newRow) // 2, (oldCol + newCol) // 2
                            pieces[captured_row][captured_col] = None
                            last_move_capture = True
                        else:
                            last_move_capture = False

                        if not (last_move_capture and get_capture_moves(pieces, selected_piece)):
                            selected_piece = None
                            make_ai_move(pieces, BLUE)

                    # AI makes a move


        draw_board(screen, pieces)
        pygame.display.update()


        if check_win(pieces, RED):
            print("Blue wins!")
            winning_text = pygame.font.SysFont('Arial', 50).render("Blue wins!", True, BLUE)
            screen.blit(winning_text, (WIDTH // 2 - winning_text.get_width() // 2, HEIGHT // 2 - winning_text.get_height() // 2))
            pygame.display.update()
            time.sleep(3)
            run = False

        if check_win(pieces, BLUE):
            print("Red wins!")
            winning_text = pygame.font.SysFont('Arial', 50).render("Red wins!", True, RED)
            screen.blit(winning_text, (WIDTH // 2 - winning_text.get_width() // 2, HEIGHT // 2 - winning_text.get_height() // 2))
            pygame.display.update()
            time.sleep(3)
            run = False

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()