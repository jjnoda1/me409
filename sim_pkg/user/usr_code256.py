import struct

def usr(robot):

    while True:
        robot.delay(10)
        if robot.virtual_id==1:
            msg=struct.pack('ffi',0.0,0.0,0)       
            robot.send_msg(msg)  
        else:           
            msgs = robot.recv_msg()      
            if len(msgs) > 0:
                for i in range(len(msgs)):
                    test=struct.unpack('ffi',msgs[i][:12])
                   

            msg=struct.pack('ffi',0.0,0.0,0)       
            robot.send_msg(msg)  # send pose x,y in message