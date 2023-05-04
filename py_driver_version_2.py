# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 13:41:08 2021

@author: Vikas
"""
    
## Library details required
import socket
import time

## function to select the required model
def model_selection(Command_transfer,veh_number):
    loop_tracker = 0
    while ((Command_transfer == True)&(loop_tracker<5)):
        msg,add = sock.recvfrom(buffer_size)
        # print(msg.decode())
        if msg.decode() == 'Model to select is':
            sock.sendto(str(veh_number).encode(),address_to_send)
            msg,add = sock.recvfrom(buffer_size)
            select = msg.decode()
            Command_transfer = False
        else:
            Command_transfer = True
            select = "No model"
        loop_tracker = loop_tracker + 1
        return select

## setting the initial parameters for the model
def initial_model_set(IntegrationStep,veh_mass,veh_X_0,veh_Y_0):
    model_ini_set = True
    loop_tracker = 0
    while (model_ini_set == True):
        loop_tracker = loop_tracker + 1
        info_counter = 0
        sock.sendto(str(IntegrationStep).encode(),address_to_send)
        msg,add = sock.recvfrom(buffer_size)
        # print(msg.decode())
        if msg.decode() == 'IntegrationStep info received':
            info_counter = info_counter + 1
        sock.sendto(str(veh_mass).encode(),address_to_send)
        msg,add = sock.recvfrom(buffer_size)
        # print(msg.decode())
        if msg.decode() == 'Vehicle mass info received':
            info_counter = info_counter + 1
        sock.sendto(str(veh_X_0).encode(),address_to_send)
        msg,add = sock.recvfrom(buffer_size)
        # print(msg.decode())
        if msg.decode() == 'Vehicle X0 info received':
            info_counter = info_counter + 1
        sock.sendto(str(veh_Y_0).encode(),address_to_send)
        msg,add = sock.recvfrom(buffer_size)
        # print(msg.decode())
        if msg.decode() == 'Vehicle Y0 info received':
            info_counter = info_counter + 1
        if info_counter == 4:
            sock.sendto(str(1).encode(),address_to_send)
            f_msg,add = sock.recvfrom(buffer_size)
            f_msg = f_msg.decode()
            model_ini_set = False
        else:
            sock.sendto(str(0).encode(),address_to_send)
            continue
        if loop_tracker > 5:
            f_msg = "not updated"
            break
    return f_msg

## Steering and Velocity Command transfer to the model


## Actual ptogram start
if __name__ == '__main__':
    sock = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

    ## details for the receiving and sending addresses on the PC
    local_ip = '127.0.0.1';                                                    # Local PC IP address
    local_port = 9090;                                                         # Port to receive command from python
    remote_ip = '127.0.0.1';                                                   # Remote PC IP address
    remote_port = 9091;                                                        # Port to send the address at the remote PC
    
    ## preparing touple for furher use in program
    address_to_send = (remote_ip,remote_port)                                  # Binding address to send the infor from python
    address_to_receive = (local_ip,local_port)                                 # Binding address to receive information from matlab
    buffer_size = 1024                                                         # Data size at the receiving end
    
    ## binding variable udp to particular socket for data storage
    sock.bind(address_to_receive)
    sock.settimeout(10)
    
    ## Initial handshake between the two systems before data transmission    
    initial_hanshake = False
    loop_tracker = 0
    while ((initial_hanshake is False) & (loop_tracker < 5)):
        loop_tracker = loop_tracker + 1
        try:
            msg,add = sock.recvfrom(buffer_size)
            print(msg.decode())
            if msg.decode() == 'Matlab is ready to receive the data':
                initial_hanshake = True
                Command_transfer = True
                sock.sendto(b'1',address_to_send)
            else:
                initial_hanshake = False
                Command_transfer = False
        except:
            initial_hanshake = False
            Command_transfer = False
    
    ## Model details information
    # inial_info_structure = (IntegrationStep,veh_mass,veh_X_0,veh_Y_0)
    initial_info = [(0.1,1000,0,0),(0.2,1200,3,-5)]
    
    ## Setting up the basic details for the model
    for i in range(1,3):
        a = model_selection(Command_transfer,i) 
        print(a)
        msg,add = sock.recvfrom(buffer_size)
        print(msg.decode(),'model',i)
        if msg.decode() == 'Send model parameters':
            status = 'To Update'
            loop_tracker = 0
            while status != 'Updated':
                loop_tracker = loop_tracker + 1
                if loop_tracker > 5:
                    print("Model update went into continuous loop")
                    break
                status = initial_model_set(initial_info[i-1][0],initial_info[i-1][1],initial_info[i-1][2],initial_info[i-1][3])
                print("Vehicle model ",i,' is ',status,' for initial conditions')
                
        if i == len(range(1,3)):
            sock.sendto(b'-1',address_to_send)
        else:
            sock.sendto(b'0',address_to_send)
    
    ## Running the simulations on the models
    
    
    ## Closing the port
    sock.close()
    print("Closed the port now and can be used for other communication")