#########################################################
#  orbit.py
# This is the python file for orbiting one robot (id = 1)
# clockwise around another robot (id = 0). When the robot
# is greater than the desired distance, both robots will 
# turn red. If the robot is less than the desired distance,
# the robots will turn green.
##########################################################

# TODO: very unstable path, need to tune PID somehow
# which might include putting anti-integral wind-up

import random
import numpy as np
from bot_api.control import PIDController
import bot_api.math_utils as bot_math


def usr(robot):

    T = random.randint(1000,1300)
    # print(T)
    id = robot.id

    # Global radius variable
    R = 0.3

    # PID Controller
    coeffs = (100,0,20)
    current = bot_math.distance(0, 0, 0, 0.3)
    dist = 0.3
    target = 0.3
    ctl = PIDController(coeffs, current, target)

    # Initial velocity term
    vel_l = 50
    vel_r = 50

    # LED colour, kept across iterations until a message sets it
    r, g, b = (0, 100, 0)

    adjust = 0

    # pose = robot.get_pose()
    # print(id, pose)
    # if id == 5:
    #     robot.delay(1000)
    while True:
        if id == 0:
            val = robot.recv_msg(clear=True)

            if len(val)>0:
                # print(val)
                if len(val[0]) > 1:
                    txt = val[0]
                    # print(val)

                    # Get LED color from message
                    sub_str = 'led:'
                    res = [i for i in range(len(txt)) if txt.startswith(sub_str, i)]

                    # Get the color
                    ind = res[-1]
                    txt = txt[ind:]
                    
                    
                    # print(txt)
                    ind_delim = txt.index(")")
                    # print(ind_delim)
                    rgb_val = txt[5:ind_delim]
                    # print("Delay_val:",delay_val)
                    rgb_val = rgb_val.split(",")
                    # print(rgb_val)
                    r, g, b = (float(val) for val in rgb_val)
                    
                    # Get the distance from message
                    ind = txt.index("distance")
                    ind_delim = ind + 1 + txt[ind+1:].index(";")
                    distance_val = txt[ind+9:ind_delim]
                    print(distance_val)
                    distance_val = float(distance_val)



            # Get id = 0's distance
            pose = robot.get_pose()
            if not pose:
                continue
            pose_x = pose[0]
            pose_y = pose[1]
            # print(id, pose)
            robot.set_led(r, g, b)
            robot.delay(200)
            curr_time = robot.get_clock()
            curr_time = round(curr_time, 2)
            msg = "time:"+ str(curr_time)+';'
            msg2 = "position:" + str(pose_x) + ',' + str(pose_y) + ';'
            robot.send_msg("led:(0,100,0);delay:800;"+msg+msg2)
            robot.set_led(0,0,0)
            # print("id: ", id, "turn off")
            robot.delay(800)
            

        else:
            val = robot.recv_msg(clear=True)
            
            if len(val)>0:
                # print(val)
                if len(val[0]) > 1:
                    txt = val[0]
                    # print(val)
                    sub_str = 'delay'
                    res = [i for i in range(len(txt)) if txt.startswith(sub_str, i)]

                    # print(txt)
                    # Get the delay
                    ind = res[-1]
                    txt = txt[ind:]
                    
                    
                    # print(txt)
                    ind_delim = txt.index(";")
                    # print(ind_delim)
                    delay_val = txt[6:ind_delim]
                    # print("Delay_val:",delay_val)
                    delay_val = float(delay_val)
                    
                    # Get the time 
                    ind = txt.index("time")
                    ind_delim = ind +1 + txt[ind+1:].index(";")
                    time_val = txt[ind+5:ind_delim]
                    time_val = float(time_val)
                    curr_time = robot.get_clock()
                    
                    next_time = time_val + delay_val/1000
                    # print("Next time:",next_time)
                    T = delay_val
                    del_Sleep = next_time - curr_time - 0.05
                    # print("Del Sleep:",del_Sleep)
                    if del_Sleep> 0:
                        robot.delay(int(del_Sleep*1000))

                    # Get position of id = 0
                    ind = txt.index("position")
                    ind_delim = ind +1 + txt[ind+1:].index(";")
                    ind_delim_comma = ind + 1 + txt[ind+1:].index(",")
                    x_val = float(txt[ind+9:ind_delim_comma])
                    y_val = float(txt[ind_delim_comma+1:ind_delim])

                    pose = robot.get_pose()
                    pose_x = pose[0]
                    pose_y = pose[1]

                    # Find distance from id = 0 to other robots
                    dist = bot_math.distance(x_val, y_val, pose_x, pose_y)
                    if dist >= R:
                        r, g, b = (100, 0, 0)
                    else:
                        r, g, b = (0, 100, 0)

            # Error before step
            error1 = ctl.last_error
            drive = ctl.step(dist, sample_period = 0.2 + T/1000)
            # Error after step
            error2 = ctl.last_error

            # Too close
            if error2 > 0:
                # If error is decreasing (closer to desired distance)
                if error2 < error1:
                    adjust = int(round(drive))
                else:
                    adjust = 0
                # print(id, dist, ctl.last_error, drive, adjust)

            # Too far
            else:
                # If error is decreasing (distance is getting further)
                if error2 < error1:
                    adjust = -int(round(drive))
                else:
                    adjust = int(round(drive))

            # print(id, dist, ctl.last_error, drive, adjust)

                

            robot.set_led(r,g,b)
            robot.set_vel(vel_l, vel_r - adjust)
            robot.delay(200)
            T = int(T)
            curr_time = robot.get_clock()
            msg_time = "time:"+ str(curr_time)+';'
            msg = "led:("+ str(r)+","+str(g)+","+str(b)+");" + "delay:"+ str(T)+";" + msg_time + \
                "distance:" + str(dist) + ";"
            robot.send_msg(msg)
            robot.set_led(0,0,0)
            robot.delay(T)