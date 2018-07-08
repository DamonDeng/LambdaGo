from go_core.goboard import GoBoard
from robot.simple_robot import SimpleRobot

from gtp import GTPFrontend
from sys import argv


def simple_test():
    testBoard = GoBoard()

    testBoard.apply_move('b', (1, 1))
    testBoard.apply_move('b', (11, 1))
    testBoard.apply_move('b', (12, 13))
    testBoard.apply_move('w', (15, 7))
    testBoard.apply_move('w', (17, 9))
    testBoard.apply_move('w', (18, 10))
    testBoard.apply_move('b', (17, 11))



    print(str(testBoard))


def gtp_test():
    test_robot = SimpleRobot()

    frontend = GTPFrontend(bot=test_robot)

    frontend.run()


gtp_test()