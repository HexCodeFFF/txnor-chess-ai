import chess.engine
import chess.svg
import pyperclip


def writeboard():
    with open("board.svg", "w+") as f:
        arrows = []
        if lastmove:
            arrows.append(chess.svg.Arrow(lastmove.from_square, lastmove.to_square))
        if ponder:
            arrows.append(chess.svg.Arrow(ponder.from_square, ponder.to_square, color="yellow"))
        f.write(chess.svg.board(board, lastmove=lastmove, size=500, arrows=arrows))
        f.truncate()


timetothink = 20
engine = chess.engine.SimpleEngine.popen_uci("stockfish_15_x64_avx2.exe")
board = chess.Board()
lastmove = None
ponder = None
nextmove = input("Input existing moves if any: ")
if nextmove:
    for move in nextmove.split(" "):
        board.push(chess.Move.from_uci(move))

writeboard()
while True:
    print("Engine is thinking...")
    latestinfodict = {}
    with engine.analysis(board, chess.engine.Limit(time=timetothink)) as analysis:
        for info in analysis:
            latestinfodict = latestinfodict | info
            try:
                print(f"depth {latestinfodict['depth']} "
                      f"eval {latestinfodict['score'].white()} "
                      f"best move {latestinfodict['pv'][0]}",
                      end=" " * 40 + "\r")
            except KeyError:
                pass
    print(" " * 40 + "\r", end="")
    result = analysis.wait()
    lastmove = result.move
    ponder = result.ponder
    pyperclip.copy(f"s/g/$&{result.move}")
    print(f"Best move is {result.move}, eval is {latestinfodict['score'].white()}, predicted continuation is {result.ponder}")
    board.push(result.move)
    writeboard()
    nextmove = input("Input move here: ")
    if not nextmove:
        break
    lastmove = nextmove = chess.Move.from_uci(nextmove)
    board.push(nextmove)
    ponder = None
    writeboard()

engine.quit()
