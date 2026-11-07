import struct
from bot_api import math_utils

def usr(robot):

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
                    coords = [tuple(test[0], test[1])]
                    if hop in hops:
                        hops(hop).append(coords)
                    else:
                        hops.update(hop, coords)
                min_hop = min(hops) # Value that you need to increase in the outgoing message
                coords = hops.get(min_hop)
                # Get minimum distance from all of the minimum coords (if length of mins is at least 3)
                # and do gradient descent
                
                # Find coords that minimize total squared error and then incrementally update
                # with the given formula
                if len(coords >= 3):
                    for coord in coords:
                        dist = math_utils.distance(0, 0, coord[0], coord[1])
                        est_dist = 0.3*min_hop  # 0.3 is comm distance
                        error = (dist - est_dist)**2



                        
                   

            msg=struct.pack('ffi',0.0,0.0,0)       
            robot.send_msg(msg)  # send pose x,y in message