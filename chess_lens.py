#!/usr/bin/python3

import chess
import chess.pgn
import chess.svg

def compute_captures(fen):
    board = chess.Board(fen)
    captures = []
    for i in range(64):
        square = chess.SQUARES[i]
        captures.append((len(board.attackers(chess.WHITE, square)), len(board.attackers(chess.BLACK, square))))
    return captures

def render_svg(board, captures):
    fill = {}
    for i in range(64):
        white, black = captures[i]
        scale = lambda cval: min(255, (255 * cval) // 8)
        fill[i] = '#{:02x}{:02x}{:02x}40'.format(255 - scale(black), 255 - (scale(black) + scale(white)), 255 - scale(white))

    svg = chess.svg.board(board, fill=fill)
    for i in range(64):
        x = i % 8
        y = 7 - i // 8
        white, black = captures[i]
        if white > black:
            color = 'red'
        elif white < black:
            color = 'blue'
        else:
            color = 'gray'

    return svg

if __name__ == "__main__":
    import argparse
    import io
    from reportlab.graphics import renderPM
    import pygifsicle
    import svglib.svglib as svglib
    import tempfile
    import tqdm

    parser = argparse.ArgumentParser(description='Draw a game as an animated GIF, coloring squares by the number of attacking on each side.')

    parser.add_argument('pgn', type=str, help='PGN database file to load a game from.')
    parser.add_argument('--game', type=int, help='Game number, where 0 is the first game (default: 0).', default=0)
    parser.add_argument('--output', type=str, help='Output GIF file.')
    args = parser.parse_args()

    with open(args.pgn) as pgn_file, \
         tempfile.TemporaryDirectory() as tmpdir:
        for i in range(args.game + 1):
            game = chess.pgn.read_game(pgn_file)

        # print basic information about the game so we know it's the right one
        print("Event:", game.headers["Event"])
        print("Site:", game.headers["Site"])
        print("Date:", game.headers["Date"])
        print("Round:", game.headers["Round"])
        print("White:", game.headers["White"])
        print("Black:", game.headers["Black"])
        print("Result:", game.headers["Result"])

        board = game.board()
        frames = []
        for idx, move in enumerate(tqdm.tqdm(list(game.mainline_moves()))):
            board.push(move)
            captures = compute_captures(board.fen())
            svg = render_svg(board, captures)
            rlg = svglib.svg2rlg(io.StringIO(svg), tmpdir + '/frame_{:04d}.pdf'.format(idx))
            framefile = f"{tmpdir}/frame_{idx:04d}.gif"
            renderPM.drawToFile(rlg, framefile, fmt='GIF', dpi=100)
            frames.append(framefile)

        pygifsicle.optimize(frames, args.output, options=['-d100'])
