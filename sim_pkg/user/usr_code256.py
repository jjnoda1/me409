import struct
from bot_api import math_utils

def usr(robot):

    a = 0.01
    while True:
        robot.delay(10)
        if robot.virtual_id==1:
            msg=struct.pack('ffi',0.0,0.0,1)  # Coordinates
            robot.send_msg(msg)  
        else:
            # Need to relay messages to other robots in the area
            # Need to check if the unpacked message has a hop count greater than the current hop count
            # Also need to calculate distance based on other's hop count
            # Strategy: make one robot white/off from one seed and make another one purple
            # hop%2 for color       
            # Get at least 3 calculations for coords    
            msgs = robot.recv_msg()      
            if len(msgs) > 0:
                hops = {}
                for i in range(len(msgs)):
                    test=struct.unpack('ffi',msgs[i][:12])
                    hop = test[2]
                    hop_coords = [tuple([test[0], test[1]])]
                    if hop in hops:
                        hops.setdefault(hop, []).append((test[0], test[1]))
                    else:
                        hops.update({hop: hop_coords})
                min_hop = min(hops) # Value that you need to increase in the outgoing message
                # v = 255*(min_hop % 2)
                # robot.set_led(v, 0, 0)   # red on odd hops, off on even

                coords = hops.get(min_hop)
                # Get minimum distance from all of the minimum coords (if length of mins is at least 3)
                # and do gradient descent
                
                # Find coords that minimize total squared error and then incrementally update
                # with the given formula
                coord = (0.0, 0.0)  # fallback if fewer than 3 neighbors
                if len(coords) >= 3:
                    # Estimated distance to the closest seed (lowest hop count)
                    min_est_dist = 0.3*min_hop  # 0.3 is comm distance
                    # Neighbor coord whose distance to the seed best matches the estimate
                    best = min(coords, key=lambda c: (math_utils.distance(0, 0, c[0], c[1]) - min_est_dist)**2)
                    min_dist = math_utils.distance(0, 0, best[0], best[1]) # Do this with other seed too
                    if min_est_dist > 0 and min_dist > 0:
                        dE_dx = best[0]*(1-min_dist/min_est_dist)
                        dE_dy = best[1]*(1-min_dist/min_est_dist)
                        coord = (best[0] - a*dE_dx, best[1] - a*dE_dy)
                    else:
                        coord = best
                if coord[0] > 100:
                    robot.set_led(100, 0, 0)
                else:
                    robot.set_led(0, 100, 0)
                msg = struct.pack('ffi', coord[0], coord[1], min_hop + 1)
                robot.send_msg(msg)
                