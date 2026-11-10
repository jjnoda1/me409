import struct
from bot_api import math_utils
import numpy as np

def usr(robot):
    # This is per robot
    a = 0.1
    seeds = {}      # {seed id: minimum hop count ever received}
    coord_estimate = []
    x_possible = np.linspace(0, 2.64, 9)
    y_possible = np.linspace(0, 3.72, 17)
    r = 0.3
    smoothing = True

    avg_nei = 8.75


    grid = np.array([[1, 1, 0, 0, 0, 1, 1, 1],
                     [1, 1, 0, 0, 0, 1, 1, 1],
                     [1, 1, 0, 0, 0, 1, 1, 1],
                     [1, 1, 0, 0, 0, 0, 1, 1],
                     [1, 1, 1, 0, 0, 0, 1, 1],
                     [1, 1, 1, 1, 0, 0, 1, 1],
                     [1, 1, 1, 1, 1, 0, 1, 1],
                     [1, 1, 1, 1, 1, 1, 1, 1],
                     [1, 1, 0, 1, 1, 1, 1, 1],
                     [1, 1, 0, 0, 1, 1 ,1 ,1],
                     [1 ,1 ,0 ,0 ,1 ,1 ,1 ,1],
                     [1 ,1 ,0 ,0 ,0 ,1 ,1 ,1],
                     [1 ,1 ,0 ,0 ,0 ,0 ,1 ,1],
                     [1 ,1 ,1 ,0 ,0 ,0 ,1 ,1],
                     [1 ,1 ,1 ,1 ,0 ,0 ,1 ,1],
                     [1 ,1 ,1 ,1 ,0 ,0 ,1 ,1]])

    def d_hop(r, n_local):
        def f(t):
            return np.exp((-n_local / np.pi) * (np.arccos(t)-t*np.sqrt(1-t**2)))
        times = np.linspace(-1, 1, 1000)
        return r*(1+np.exp(-n_local) - np.trapezoid(f(times), times))

    while True:
        robot.delay(10)
        if robot.virtual_id==1:
            msg=struct.pack('ii',1, 100)  # Coordinates
            robot.send_msg(msg)
            robot.set_led(128, 0, 128)

        elif robot.virtual_id==2:
            msg=struct.pack('ii', 100, 1)  # Coordinates
            robot.send_msg(msg)
            robot.set_led(128, 0, 128)
            
        else:
            # Need to relay messages to other robots in the area
            # Need to check if the unpacked message has a hop count greater than the current hop count
            # Also need to calculate distance based on other's hop count
            # Strategy: make one robot white/off from one seed and make another one purple
            # hop%2 for color       
            # Get at least 3 calculations for coords   
            # 
            # PART 1: 
            msgs = robot.recv_msg()      
            if len(msgs) > 0:
                n1 = 0  
                n2 = 0
                hop_sum_1 = 0
                hop_sum_2 = 0

                for i in range(len(msgs)):
                    test = struct.unpack('ii',msgs[i][:8])
                    hop1 = test[0]
                    hop2 = test[1]
                    hops = [hop1, hop2]

                    # Check if hop count is not from seed
                    if hop1 < 100:
                        hop_sum_1 += hop1 - 1
                        n1 += 1
                    if hop2 < 100:
                        n2 += 1
                        hop_sum_2 += hop2 - 1
                    # Keep the minimum hop count received from this seed; ignore larger values
                    for i in range(1, len(hops)+ 1):
                        seed = i
                        if seed not in seeds or hops[i-1] < seeds[seed]:
                            seeds[seed] = hops[i-1]

                    smoothing_factor_1 = (hop_sum_1 + seeds[1]) / (n1 + 1) - 0.5
                    smoothing_factor_2 = (hop_sum_2 + seeds[2]) / (n2 + 1) - 0.5



                # # PART 2:
                # min_hop = min(seeds.values()) # Closest seed's hop count
                seed = min(seeds, key=seeds.get)
                # after the coord_estimate update:





                # if min_hop % 2 == 0:
                #     if seed == 1:
                #         robot.set_led(255, 0, 0) # red on even hops from seed 1
                #     elif seed == 2:
                #         robot.set_led(0, 255, 0) # green on even hops from seed 2
                # else:
                #     robot.set_led(0, 0, 0)# off on odd hops

                if coord_estimate == []:
                    if seed == 1:
                        coord_estimate = [0.01, 0.01]
                    elif seed == 2:
                        coord_estimate = [0.01, 3.59]

                calc_distance_1 = math_utils.distance(coord_estimate[0], coord_estimate[1], 0, 0)
                calc_distance_2 = math_utils.distance(coord_estimate[0], coord_estimate[1], 0, 3.6)
                if smoothing == True:
                    d_hat_1 = d_hop(r, avg_nei) * smoothing_factor_1
                    d_hat_2 = d_hop(r, avg_nei) * smoothing_factor_2
                else:
                    d_hat_1 = seeds[1] * r
                    d_hat_2 = seeds[2] * r
                dE_dx = (coord_estimate[0] - 0)*(1-d_hat_1/calc_distance_1) + (coord_estimate[0] - 0)*(1-d_hat_2/calc_distance_2)
                dE_dy = (coord_estimate[1] - 0)*(1-d_hat_1/calc_distance_1) + (coord_estimate[1] - 3.60)*(1-d_hat_2/calc_distance_2)
                coord_estimate[0] = coord_estimate[0] - a*dE_dx
                coord_estimate[1] = coord_estimate[1] - a*dE_dy

                bin_x = np.clip(np.digitize(coord_estimate[0], x_possible) - 1, 0, 7)
                bin_y = np.clip(np.digitize(coord_estimate[1], y_possible) - 1, 0, 15)
                if grid[15 - bin_y, bin_x] == 1:
                    robot.set_led(128, 0, 128)
                else:
                    robot.set_led(255, 255, 255)


                msg = struct.pack('ii', seeds[1] + 1, seeds[2] + 1)  # Hop counts
                robot.send_msg(msg)
                