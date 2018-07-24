from robot.mtcs_robot import MTCSRobot
from robot.self_trainer import SelfTrainer

import sys

def start_self_train(res_layer_number=19, steps=100, old_model=None):

    if old_model is None:
        teacher_model = MTCSRobot(layer_number=res_layer_number)
        student_model = MTCSRobot(layer_number=res_layer_number)
        test_trainer = SelfTrainer(teacher_model, student_model, layer_number=res_layer_number)
    else:
        teacher_model = MTCSRobot(layer_number=res_layer_number, old_model=old_model)
        student_model = MTCSRobot(layer_number=res_layer_number, old_model=old_model)
        test_trainer = SelfTrainer(teacher_model, student_model, layer_number=res_layer_number)

    test_trainer.self_train(steps)

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



