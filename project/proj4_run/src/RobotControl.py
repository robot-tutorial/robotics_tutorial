import pybullet as p
import Helper
import time
import numpy as np
import math
from MPC_controller import Walk
from MPC_controller import Fly


def loadRobot(initPos):
    robotName = 'MarioTheRobot.urdf'
    initOrn = [1.0, 0.0, 0.0, 0.0]
    return p.loadURDF(Helper.findURDF(robotName), initPos, initOrn)


def generateTraj(robotId):
    # work in this function to make a plan before actual control
    # the output can be in any data structure you like
    landing_steps = 200
    fy = []
    theta = []
    x = []
    y = []
    for i in range(landing_steps):
        fy.append(0)
        theta.append(0)
        x.append(0)
        y.append(0)

    # forward_step = 1000
    # for i in range(forward_step):
    #     fy.append(0)
    #     theta.append(0.2)
    #     x.append(i / forward_step)
    #     y.append(0.05)

    # bending_step = 200
    # for i in range(bending_step):
    #     fy.append(np.pi / 2 * i / bending_step)
    #     theta.append(- np.pi / 4 * i / bending_step)
    #     x.append(0)
    #     y.append(0.05)
    #
    # stretching_step = 5
    # omega = np.pi / 4
    # for i in range(stretching_step):
    #     fy.append(np.pi / 2 - 2 * omega * i / stretching_step)
    #     theta.append(-np.pi / 4 + omega * i / stretching_step)
    #     x.append(0)
    #     y.append(0.05)
    #
    # wait_step = 1000
    # for i in range(wait_step):
    #     fy.append(0)
    #     theta.append(0)
    #     x.append(0)
    #     y.append(0.05)
    # plan = [reference_theta, reference_x, reference_fy]
    plan = [np.array(theta), np.array(fy), np.array(x), np.array(y)]
    return plan


def realTimeControl(robotId, plan, count):
    # work in this function to calculate real time control signal
    # the output should be a list of two float
    start = time.time()

    predict_step = 10
    plan = np.transpose(plan)
    reference = plan[count: count + predict_step]
    reference = np.transpose(reference)
    state = getstate(robotId)
    mpc = Fly(state, reference)
    # mpc = Walk(state, reference)
    controlSignal = mpc.Solve()
    # controlSignal = [0, 0]
    if count % 10 == 0:
        print('Count   ', count)
        print('reference', reference)
        print('state', state)
        print('M1, M2', controlSignal)
        end = time.time()
        print('time', end - start)
        print()
    # controlSignal = AnswerByTA.realTimeControl(robotId, plan)
    count += 1
    return controlSignal


def addDebugItems(robotId):
    # work in this function to add any debug visual items you need
    p.addUserDebugLine((0.0, 0.0, 0.0), (0.0, 0.0, -10.0), lineWidth=1, parentObjectUniqueId=robotId, parentLinkIndex=5)
    p.addUserDebugLine((0.0, 0.0, 0.05), (2.0, 0.0, 0.05), lineWidth=1)


def getstate(robotId):
    name = ['engine1', 'engine2']
    motors = []
    jointState_0 = []

    for jointId in range(p.getNumJoints(robotId)):
        jointName = p.getJointInfo(robotId, jointId)[1]
        if jointName.decode() in name:
            motors.append(jointId)
    jointState_0 = p.getJointState(robotId, motors[0])

    pos_wheel = p.getLinkState(robotId, 5, 1)
    pos_leg = p.getLinkState(robotId, 4, 1)
    Euler_leg = Quaternion2Angle(pos_leg[1])
    Euler_wheel = Quaternion2Angle(pos_wheel[1])

    theta = Euler_leg
    v_theta = pos_leg[7][1]
    fy = jointState_0[0]
    v_fy = jointState_0[1]
    x = pos_wheel[0][0]
    v_x = pos_wheel[6][0]
    y = -pos_wheel[0][2]
    v_y = -pos_wheel[6][2]
    alpha = Euler_wheel
    v_alpha = pos_wheel[7][1]

    return [theta, fy, x, v_theta, v_fy, v_x, y, v_y, alpha, v_alpha]


def Quaternion2Angle(quaternion):
    a1 = quaternion[0]
    a3 = quaternion[2]
    if a1 == 0:
        angle = np.pi
    elif a1 > 0:
        if a3 >= 0:
            angle = -2 * np.arctan(a3 / a1)
        else:
            angle = 2 * np.arctan(- a3 / a1)
    else:
        angle = 2 * np.arctan(- a3 / a1)
    return angle

