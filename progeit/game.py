import pygame as pg
import random, time, sys
from pygame.locals import *
import sqlite3

conn = sqlite3.connect('db/tetris.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tetris (
    id INTEGER PRIMARY KEY,
    board_width INTEGER,
    board_height INTEGER,
    score INTEGER,
    level INTEGER,
    lines_cleared INTEGER,
    current_piece TEXT,
    next_piece TEXT,
    game_board TEXT
)
''')

conn.commit()


fps = 1000
window_w, window_h = 600, 500
block, backet_h, backet_w = 20, 20, 10

side_time, down_time = 0.15, 0.1

side_b = int((window_w - backet_w * block) / 2)
top = window_h - (backet_h * block) - 5

colors = ((0, 0, 225), (0, 225, 0), (225, 0, 0), (225, 225, 0), (248, 24, 148))

white, gray, black = (255, 255, 255), (185, 185, 185), (0, 0, 0)
brd_c, bg_c, txt_c, title_c, info_c = white, black, white, colors[4], colors[0]

w, h = 5, 5
empty = 'o'

figures = {'S': [['ooooo',
                  'ooooo',
                  'ooxxo',
                  'oxxoo',
                  'ooooo'],
                 ['ooooo',
                  'ooxoo',
                  'ooxxo',
                  'oooxo',
                  'ooooo']],
           'Z': [['ooooo',
                  'ooooo',
                  'oxxoo',
                  'ooxxo',
                  'ooooo'],
                 ['ooooo',
                  'ooxoo',
                  'oxxoo',
                  'oxooo',
                  'ooooo']],
           'J': [['ooooo',
                  'oxooo',
                  'oxxxo',
                  'ooooo',
                  'ooooo'],
                 ['ooooo',
                  'ooxxo',
                  'ooxoo',
                  'ooxoo',
                  'ooooo'],
                 ['ooooo',
                  'ooooo',
                  'oxxxo',
                  'oooxo',
                  'ooooo'],
                 ['ooooo',
                  'ooxoo',
                  'ooxoo',
                  'oxxoo',
                  'ooooo']],
           'L': [['ooooo',
                  'oooxo',
                  'oxxxo',
                  'ooooo',
                  'ooooo'],
                 ['ooooo',
                  'ooxoo',
                  'ooxoo',
                  'ooxxo',
                  'ooooo'],
                 ['ooooo',
                  'ooooo',
                  'oxxxo',
                  'oxooo',
                  'ooooo'],
                 ['ooooo',
                  'oxxoo',
                  'ooxoo',
                  'ooxoo',
                  'ooooo']],
           'I': [['ooxoo',
                  'ooxoo',
                  'ooxoo',
                  'ooxoo',
                  'ooooo'],
                 ['ooooo',
                  'ooooo',
                  'xxxxo',
                  'ooooo',
                  'ooooo']],
           'O': [['ooooo',
                  'ooooo',
                  'oxxoo',
                  'oxxoo',
                  'ooooo']],
           'T': [['ooooo',
                  'ooxoo',
                  'oxxxo',
                  'ooooo',
                  'ooooo'],
                 ['ooooo',
                  'ooxoo',
                  'ooxxo',
                  'ooxoo',
                  'ooooo'],
                 ['ooooo',
                  'ooooo',
                  'oxxxo',
                  'ooxoo',
                  'ooooo'],
                 ['ooooo',
                  'ooxoo',
                  'oxxoo',
                  'ooxoo',
                  'ooooo']]}

tetris_db = {
    'board_width': backet_w,
    'board_height': backet_h,
    'score': 0,
    'level': 1,
    'lines_cleared': 0,
    'current_piece': None,
    'next_piece': None,
    'game_board': [[0] * backet_h for _ in range(backet_w)]
}

def pauseScreen():
    pause = pg.Surface((600, 500), pg.SRCALPHA)
    pause.fill((0, 0, 255, 127))
    display_surf.blit(pause, (0, 0))


def main():
    global fps_clock, display_surf, basic_font, big_font
    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((window_w, window_h))
    basic_font = pg.font.SysFont('arial', 20)
    big_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Тетрис')
    showText('Тетрис')
    while True:
        runTetris()
        pauseScreen()
        showText('Game over')


def runTetris():
    backet = emptybacket()
    last_move_down = time.time()
    last_side_move = time.time()
    last_fall = time.time()
    going_down = False
    going_left = False
    going_right = False
    points = 0
    col_wo = 0
    level, fall_speed = calcSpeed(points)
    fallingFig = getNewFig()
    nextFig = getNewFig()

    while True:
        if fallingFig == None:
            fallingFig = nextFig
            nextFig = getNewFig()
            last_fall = time.time()

            if not checkPos(backet, fallingFig):
                return
        quitGame()
        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    pauseScreen()
                    showText('Пауза')
                    last_fall = time.time()
                    last_move_down = time.time()
                    last_side_move = time.time()
                elif event.key == K_LEFT:
                    going_left = False
                elif event.key == K_RIGHT:
                    going_right = False
                elif event.key == K_DOWN:
                    going_down = False
                elif event.key == K_a:
                    going_left = False
                elif event.key == K_d:
                    going_right = False
                elif event.key == K_s:
                    going_down = False

            elif event.type == KEYDOWN:
                if event.key == K_LEFT and checkPos(backet, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                    going_left = True
                    going_right = False
                    last_side_move = time.time()

                elif event.key == K_RIGHT and checkPos(backet, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                    going_right = True
                    going_left = False
                    last_side_move = time.time()

                elif event.key == K_UP:
                    fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(figures[fallingFig['shape']])
                    if not checkPos(backet, fallingFig):
                        fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(figures[fallingFig['shape']])

                elif event.key == K_DOWN:
                    going_down = True
                    if checkPos(backet, fallingFig, adjY=1):
                        fallingFig['y'] += 1
                    last_move_down = time.time()
                if event.key == K_a and checkPos(backet, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                    going_left = True
                    going_right = False
                    last_side_move = time.time()

                elif event.key == K_d and checkPos(backet, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                    going_right = True
                    going_left = False
                    last_side_move = time.time()

                elif event.key == K_w:
                    fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(figures[fallingFig['shape']])
                    if not checkPos(backet, fallingFig):
                        fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(figures[fallingFig['shape']])

                elif event.key == K_s:
                    going_down = True
                    if checkPos(backet, fallingFig, adjY=1):
                        fallingFig['y'] += 1
                    last_move_down = time.time()

                elif event.key == K_RETURN:
                    going_down = False
                    going_left = False
                    going_right = False
                    for i in range(1, backet_h):
                        if not checkPos(backet, fallingFig, adjY=i):
                            break
                        fallingFig['y'] += i - 1

        if (going_left or going_right) and time.time() - last_side_move > side_time:
            if going_left and checkPos(backet, fallingFig, adjX=-1):
                fallingFig['x'] -= 1
            elif going_right and checkPos(backet, fallingFig, adjX=1):
                fallingFig['x'] += 1
            last_side_move = time.time()

        if going_down and time.time() - last_move_down > down_time and checkPos(backet, fallingFig, adjY=1):
            fallingFig['y'] += 1
            last_move_down = time.time()

        if time.time() - last_fall > fall_speed:
            if not checkPos(backet, fallingFig, adjY=1):
                addTobacket(backet, fallingFig)
                points += clearCompleted(backet)
                level, fall_speed = calcSpeed(points)
                fallingFig = None
                col_wo += 1

            else:
                fallingFig['y'] += 1
                last_fall = time.time()

        display_surf.fill(bg_c)
        drawTitle()
        gamebacket(backet)
        drawInfo(points, level, col_wo)
        drawnextFig(nextFig)
        if fallingFig != None:
            drawFig(fallingFig)
        pg.display.update()
        fps_clock.tick(fps)


def txtObjects(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def stopGame():
    pg.quit()
    sys.exit()


def checkKeys():
    quitGame()

    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showText(text):
    titleSurf, titleRect = txtObjects(text, big_font, title_c)
    titleRect.center = (int(window_w / 2) - 3, int(window_h / 2) - 3)
    display_surf.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', basic_font, title_c)
    pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 100)
    display_surf.blit(pressKeySurf, pressKeyRect)

    while checkKeys() == None:
        pg.display.update()
        fps_clock.tick()


def quitGame():
    for event in pg.event.get(QUIT):
        stopGame()
    for event in pg.event.get(KEYUP):
        if event.key == K_ESCAPE:
            stopGame()
        pg.event.post(event)

def figura(cw):
    col_wo =int(cw)
    return col_wo


def calcSpeed(points):
    level = int(points / 10) + 1
    fall_speed = 0.27 + (level * 0.02)
    return level, fall_speed


def getNewFig():
    shape = random.choice(list(figures.keys()))
    newFigure = {'shape': shape,
                 'rotation': random.randint(0, len(figures[shape]) - 1),
                 'x': int(backet_w / 2) - int(w / 2),
                 'y': -2,
                 'color': random.randint(0, len(colors) - 1)}
    return newFigure


def addTobacket(backet, fig):
    for x in range(w):
        for y in range(h):
            if figures[fig['shape']][fig['rotation']][y][x] != empty:
                backet[x + fig['x']][y + fig['y']] = fig['color']
    updateGameBoard()


def updateGameBoard():
    tetris_db['game_board'] = [[0] * backet_h for _ in range(backet_w)]
    for x in range(backet_w):
        for y in range(backet_h):
            tetris_db['game_board'][x][y] = display_surf.get_at((side_b + x * block, top + y * block))

    cursor.execute('''
    INSERT INTO tetris (
        board_width, board_height, score, level, lines_cleared,
        current_piece, next_piece, game_board
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        tetris_db['board_width'], tetris_db['board_height'], tetris_db['score'],
        tetris_db['level'], tetris_db['lines_cleared'],
        str(tetris_db['current_piece']), str(tetris_db['next_piece']),
        str(tetris_db['game_board'])
    ))

    conn.commit()


def emptybacket():
    backet = []
    for i in range(backet_w):
        backet.append([empty] * backet_h)
    return backet


def inbacket(x, y):
    return x >= 0 and x < backet_w and y < backet_h


def checkPos(backet, fig, adjX=0, adjY=0):
    for x in range(w):
        for y in range(h):
            abovebacket = y + fig['y'] + adjY < 0
            if abovebacket or figures[fig['shape']][fig['rotation']][y][x] == empty:
                continue
            if not inbacket(x + fig['x'] + adjX, y + fig['y'] + adjY):
                return False
            if backet[x + fig['x'] + adjX][y + fig['y'] + adjY] != empty:
                return False
    return True


def isCompleted(backet, y):
    for x in range(backet_w):
        if backet[x][y] == empty:
            return False
    return True


def clearCompleted(backet):
    removed_lines = 0
    y = backet_h - 1
    while y >= 0:
        if isCompleted(backet, y):
            for pushDownY in range(y, 0, -1):
                for x in range(backet_w):
                    backet[x][pushDownY] = backet[x][pushDownY - 1]
            for x in range(backet_w):
                backet[x][0] = empty
            removed_lines += 1
        else:
            y -= 1

    tetris_db['lines_cleared'] += removed_lines
    tetris_db['score'] += removed_lines * 100 * tetris_db['level']
    updateGameBoard()
    return removed_lines


def convertCoords(block_x, block_y):
    return (side_b + (block_x * block)), (top + (block_y * block))


def drawBlock(block_x, block_y, color, pixelx=None, pixely=None):
    if color == empty:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertCoords(block_x, block_y)
    pg.draw.rect(display_surf, colors[color], (pixelx + 1, pixely + 1, block - 1, block - 1), 0, 3)



def gamebacket(backet):
    pg.draw.rect(display_surf, brd_c, (side_b - 4, top - 4, (backet_w * block) + 8, (backet_h * block) + 8),
                 5)

    pg.draw.rect(display_surf, bg_c, (side_b, top, block * backet_w, block * backet_h))
    for x in range(backet_w):
        for y in range(backet_h):
            drawBlock(x, y, backet[x][y])


def drawTitle():
    titleSurf = big_font.render('Тетрис', True, title_c)
    titleRect = titleSurf.get_rect()
    titleRect.topleft = (window_w - 380, 10)
    display_surf.blit(titleSurf, titleRect)


def drawInfo(points, level, col_wo):
    pointsSurf = basic_font.render(f'Баллы: {points}', True, txt_c)
    pointsRect = pointsSurf.get_rect()
    pointsRect.topleft = (window_w - 150, 200)
    display_surf.blit(pointsSurf, pointsRect)

    levelSurf = basic_font.render(f'Уровень: {level}', True, txt_c)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (window_w - 150, 250)
    display_surf.blit(levelSurf, levelRect)

    col_woSurf = basic_font.render(f'Кол-во фигур: {col_wo}', True, txt_c)
    col_woRect = col_woSurf.get_rect()
    col_woRect.topleft = (window_w - 170, 300)
    display_surf.blit(col_woSurf, col_woRect)


def drawFig(fig, pixelx=None, pixely=None):
    figToDraw = figures[fig['shape']][fig['rotation']]
    if pixelx == None and pixely == None:
        pixelx, pixely = convertCoords(fig['x'], fig['y'])

    for x in range(w):
        for y in range(h):
            if figToDraw[y][x] != empty:
                drawBlock(None, None, fig['color'], pixelx + (x * block), pixely + (y * block))


def drawnextFig(fig):
    drawFig(fig, pixelx = window_w - 550, pixely = 200)


if __name__ == '__main__':
    main()
    conn.close()