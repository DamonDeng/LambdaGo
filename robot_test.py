from robot.simple_robot import SimpleRobot
from robot.lambda_robot import LambdaRobot
from robot.mcts_robot import MCTSRobot
from robot.self_trainer import SelfTrainer

import sys
import argparse

def start_self_train(robot='SimpleRobot', res_layer_number=19, steps=100, old_model=None, board_size=19, komi=7.5, train_iter=2):

    if old_model is None:
        if robot == 'MCTSRobot':
            teacher_model = MCTSRobot(name='Teacher', layer_number=res_layer_number, board_size=board_size, komi=komi)
            student_model = MCTSRobot(name='Student', layer_number=res_layer_number, board_size=board_size, komi=komi)
        elif robot == 'LambdaRobot':
            teacher_model = LambdaRobot(name='Teacher', layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
            student_model = LambdaRobot(name='Student', layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
        else: # 'SimpleRobot':
            teacher_model = SimpleRobot(name='Teacher', layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
            student_model = SimpleRobot(name='Student', layer_number=res_layer_number, board_size=board_size, komi=komi, train_iter=train_iter)
            
        test_trainer = SelfTrainer(teacher_model, student_model, layer_number=res_layer_number)
    else:
        if robot == 'MCTSRobot':
            teacher_model = MCTSRobot(name='Teacher', layer_number=res_layer_number, old_model=old_model, board_size=board_size, komi=komi)
            student_model = MCTSRobot(name='Student', layer_number=res_layer_number, old_model=old_model, board_size=board_size, komi=komi)
        elif robot == 'LambdaRobot':
            teacher_model = LambdaRobot(name='Teacher', layer_number=res_layer_number, old_model=old_model, board_size=board_size, komi=komi, train_iter=train_iter)
            student_model = LambdaRobot(name='Student', layer_number=res_layer_number, old_model=old_model, board_size=board_size, komi=komi, train_iter=train_iter)    
        else: # 'SimpleRobot':
            teacher_model = SimpleRobot(name='Teacher', layer_number=res_layer_number, old_model=old_model, board_size=board_size, komi=komi, train_iter=train_iter)
            student_model = SimpleRobot(name='Student', layer_number=res_layer_number, old_model=old_model, board_size=board_size, komi=komi, train_iter=train_iter)
            
        test_trainer = SelfTrainer(teacher_model, student_model, layer_number=res_layer_number)

    test_trainer.self_train(steps)

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--layer_number', type=int, default=1, help='number of Res block')
    parser.add_argument('--steps', '-s', type=int, default=100, help='loop times')
    parser.add_argument('--model_path', '-m', help='file path of old model')
    parser.add_argument('--board_size', '-b', type=int, default=19, help='board size')
    parser.add_argument('--komi', '-k', type=float, default=7.5, help='komi')
    parser.add_argument('--robot', '-r', help='name of the robot')
    parser.add_argument('--train_iter', '-t', type=int, default=2, help='trainning time of each train iter')
    
    
    args = parser.parse_args()

    start_self_train(robot=args.robot, res_layer_number=args.layer_number, steps=args.steps, old_model=args.model_path, \
                    board_size=args.board_size, komi=args.komi, train_iter=args.train_iter)


if __name__ == '__main__':
    main(sys.argv)



