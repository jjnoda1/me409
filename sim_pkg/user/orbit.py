import random
from bot_api.control import PIDController
import bot_api.math_utils as bot_math


def usr(robot):

    T = random.randint(1000,1300)
    # print(T)
    id = robot.id

    # Global radius variable
    r = 0.5

    # PID Controller
    coeffs = (0.1, 0.1, 0)
    # ctl = PIDController(coeffs, current, target)
    # ctl.reset()
    # while abs(ctl.last_error) > max_error:
    #     # Measure input
    #     drive = ctl.step(current)
    #     do_drive(drive)

    # pose = robot.get_pose()
    # print(id, pose)
    # if id == 5:
    #     robot.delay(1000)
    while True:
        if id == 0:
            pose = robot.get_pose()
            if not pose:
                continue
            pose_x = pose[0]
            pose_y = pose[1]
            # print(id, pose)
            robot.set_led(0,100,0)
            # print("id: ", id, "turn on")
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
                    # msg_time = "time:"+ str(curr_time)+';'
                    # r, g, b = (0, 100, 0)
                    # msg = "led:("+ str(r)+","+str(g)+","+str(b)+");" + txt
                    # robot.send_msg(msg)
                    # print(ind)
                    
                    
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

                    dist = bot_math.distance(x_val, y_val, pose_x, pose_y)
                    print(dist)

                    # print("x val:" + x_val + " y val:" + y_val)




            # pose = robot.get_pose()
            # print(id, pose) 
            robot.set_vel(55, 50)       
            r, g, b = (0, 100, 0)
            robot.set_led(r,g,b)
            robot.delay(200)
            T = int(T)
            curr_time = robot.get_clock()
            msg_time = "time:"+ str(curr_time)+';'
            msg = "led:("+ str(r)+","+str(g)+","+str(b)+");" + "delay:"+ str(T)+";" + msg_time
            # robot.send_msg(msg)
            robot.set_led(0,0,0)
            robot.delay(T)