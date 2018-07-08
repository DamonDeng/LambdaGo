#!/usr/local/bin/python



from __future__ import print_function
from sys import argv

from gtp import GTPFrontend

from go_core.goboard import GoBoard
from robot.simple_robot import SimpleRobot



test_robot = SimpleRobot()

frontend = GTPFrontend(bot=test_robot)

frontend.run()

frontend = GTPFrontend(bot=test_robot)

frontend.run()