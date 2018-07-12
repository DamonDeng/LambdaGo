from robot.simple_robot import SimpleRobot

import sys

def start_self_train(res_layer_number=19, steps=100, old_model=None):

    if old_model is None:
        test_robot = SimpleRobot(layer_number=res_layer_number)
    else:
        test_robot = SimpleRobot(layer_number=res_layer_number, old_model=old_model)

    test_robot.self_train(steps)

def main(argv):
    if argv == None:
        start_self_train()
    elif len(argv) == 2:
        start_self_train(res_layer_number=int(argv[1]))
    elif len(argv) == 3:
        # print ('argv[0] is:' + argv[1])
        start_self_train(res_layer_number=int(argv[1]), steps=int(argv[2]))
    elif len(argv) == 4:
        # print ('argv[0] is:' + argv[1])
        start_self_train(res_layer_number=int(argv[1]), steps=int(argv[2]), old_model=argv[3])


if __name__ == '__main__':
    main(sys.argv)



