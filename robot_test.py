from robot.simple_robot import SimpleRobot
from robot.lambda_robot import LambdaRobot
from robot.mcts_robot import MCTSRobot
from robot.self_trainer import SelfTrainer

from global_config.config import Config

import sys
import argparse

def start_self_train(robot='SimpleRobot', old_model=None):

    if old_model is None:
        if robot == 'MCTSRobot':
            teacher_model = MCTSRobot(name='Teacher') #, layer_number=res_layer_number, board_size=board_size, komi=komi)
            student_model = MCTSRobot(name='Student') #, layer_number=res_layer_number, board_size=board_size, komi=komi)
        elif robot == 'LambdaRobot':
            teacher_model = LambdaRobot(name='Teacher') #, layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
            student_model = LambdaRobot(name='Student') #, layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
        else: # 'SimpleRobot':
            teacher_model = SimpleRobot(name='Teacher') #, layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
            student_model = SimpleRobot(name='Student') #, layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
            
        test_trainer = SelfTrainer(teacher_model, student_model) #, layer_number=res_layer_number)
    else:
        if robot == 'MCTSRobot':
            teacher_model = MCTSRobot(name='Teacher', old_model=old_model)
            student_model = MCTSRobot(name='Student', old_model=old_model)
        elif robot == 'LambdaRobot':
            teacher_model = LambdaRobot(name='Teacher', old_model=old_model)
            student_model = LambdaRobot(name='Student', old_model=old_model)    
        else: # 'SimpleRobot':
            teacher_model = SimpleRobot(name='Teacher', old_model=old_model)
            student_model = SimpleRobot(name='Student', old_model=old_model)
            
        test_trainer = SelfTrainer(teacher_model, student_model)

    test_trainer.self_train()

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--layer_number', type=int, default=1, help='number of Res block')
    parser.add_argument('--steps', '-s', type=int, default=100, help='loop times')
    parser.add_argument('--model_path', '-m', help='file path of old model')
    parser.add_argument('--board_size', '-b', type=int, default=19, help='board size')
    parser.add_argument('--komi', '-k', type=float, default=7.5, help='komi')
    parser.add_argument('--robot', '-r', help='name of the robot')
    parser.add_argument('--train_iter', '-t', type=int, default=2, help='trainning time of each train iter')
    parser.add_argument('--is_debug', '-d', type=bool, default=False, help='use debuf mode or not')
    
    
    args = parser.parse_args()

    Config.layer_number = args.layer_number
    Config.board_size = args.board_size
    Config.komi = args.komi
    Config.train_iter = args.train_iter
    Config.steps = args.steps
    Config.is_debug = args.is_debug


    start_self_train(robot=args.robot, old_model=args.model_path)


if __name__ == '__main__':
    main(sys.argv)



