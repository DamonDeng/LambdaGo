#!/usr/local/bin/python



from __future__ import print_function
from sys import argv

from gtp import GTPFrontend

# from go_core.goboard import GoBoard
# from robot.delta_robot import SimpleRobot
from robot.simple_robot import SimpleRobot

from robot.lambda_robot import LambdaRobot

test_robot = LambdaRobot()

frontend = GTPFrontend(bot=test_robot)

frontend.run()

# frontend = GTPFrontend(bot=test_robot)

# frontend.run()