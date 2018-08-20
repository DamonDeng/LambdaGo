from robot.simple_robot import SimpleRobot
from robot.self_trainer import SelfTrainer

import sys
import argparse

def start_self_train(res_layer_number=19, steps=100, old_model=None, boardsize=19, komi=7.5):

    if old_model is None:
        teacher_model = SimpleRobot(name='Teacher', layer_number=res_layer_number, boardsize=boardsize, komi=komi)
        student_model = SimpleRobot(name='Student', layer_number=res_layer_number, boardsize=boardsize, komi=komi)
        test_trainer = SelfTrainer(teacher_model, student_model, layer_number=res_layer_number)
    else:
        teacher_model = SimpleRobot(name='Teacher', layer_number=res_layer_number, old_model=old_model, boardsize=boardsize, komi=komi)
        student_model = SimpleRobot(name='Student', layer_number=res_layer_number, old_model=old_model, boardsize=boardsize, komi=komi)
        test_trainer = SelfTrainer(teacher_model, student_model, layer_number=res_layer_number)

    test_trainer.self_train(steps)

def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--layernumber', type=int, default=1, help='number of Res block')
    parser.add_argument('--steps', '-s', type=int, default=100, help='loop times')
    parser.add_argument('--modelpath', '-m', help='file path of old model')
    parser.add_argument('--boardsize', '-b', type=int, default=19, help='board size')
    parser.add_argument('--komi', '-k', type=float, default=7.5, help='komi')
    
    
    args = parser.parse_args()

    # if argv == None:
    #     start_self_train()
    # elif len(argv) == 2:
    #     start_self_train(res_layer_number=int(argv[1]))
    # elif len(argv) == 3:
    #     # print ('argv[0] is:' + argv[1])
    #     start_self_train(res_layer_number=int(argv[1]), steps=int(argv[2]))
    # elif len(argv) == 4:
    #     # print ('argv[0] is:' + argv[1])

    start_self_train(res_layer_number=args.layernumber, steps=args.steps, old_model=args.modelpath, boardsize=args.boardsize, komi=args.komi)


if __name__ == '__main__':
    main(sys.argv)



