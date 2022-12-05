import socket
import json
import threading 
import queue

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

messages = queue.Queue() #command--handle--message--address
clients = []
names = []
groups = []
used_ports = [] 

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

def convert_and_send(sock, data, ip_and_port): # convert and send json to server;
    json_data = json.dumps(data) #convert to json
    try: # error checking
        sock.sendto(json_data.encode(), ip_and_port) # send to server   
        return 1
    except:
        return 0


#[2] get info from client and add to queue/array 
def receive(): 
    while True:
        try:
            handle = "[anon]"
            message = " "

            data, addr = server.recvfrom(1024)
            data = data.decode("utf-8")
            data_parsed = json.loads(data)
            command = data_parsed["command"]
            

            match command: 
                case "all":
                    message = data_parsed["message"]                    
                    if addr in clients:
                        name_index = clients.index(addr) 
                        handle = names[name_index]
                    messages.put((command, handle, "", "", message, addr)) #adds current message to messages array
                case "register":
                    handle = data_parsed["handle"]
                    messages.put((command, handle, "", "", message, addr))
                    if handle not in names: 
                        if addr not in clients: 
                            clients.append(addr)
                            names.append(handle)
                        elif addr in clients: 
                            name_index = clients.index(addr)
                            if names[name_index] != handle: 
                                names[name_index] = handle
                            # print(clients[name_index])
                            # print(names[name_index])
                    #else: 
                        # TO DO 
                        #
                        #
                        #
                        # (this happens if handle already exists in names array)
                        # code should not accept duplicate handles/names 
                        # must print wanring in client.py 
                        #
                        #
                        #
                        #
                case "msg": 
                    handle = data_parsed["handle"]
                    message = data_parsed["message"]
                    if addr in clients:
                        name_index = clients.index(addr) 
                        sender_handle = names[name_index]
                    else: 
                        sender_handle = ""
                    messages.put((command, handle, sender_handle, "", message, addr))

                    # TO DO 
                    #
                    #
                    # check if sender already has a handle 
                    # if wala, they can't send a direct message 
                    # must print wanring in client.py 
                    #
                    #
                    #

                    # if handle not in names: 
                        # TO DO 
                        #
                        #
                        #
                        # (this happens if handle doesnt already exists in names array)
                        # code cant send message to a name that doesnt exist  
                        # must print wanring in client.py 
                        #
                        #
                        #
                        #
                case "grp":
                    group_name = data_parsed["group_name"]
                    message = data_parsed["message"]
                    if addr in clients:
                        name_index = clients.index(addr) 
                        handle = names[name_index]
                    else: 
                        handle = "you can't do this yo"

                    if group_name not in groups: 
                        groups.append(group_name)
                        groups.append([])
                        curr_group_membs = groups.index([])
                        groups[curr_group_membs].append(addr)
                        print(curr_group_membs)
                    else: 
                        group_index = groups.index(group_name) + 1
                        if addr not in groups[group_index]: 
                            groups[group_index].append(addr)
                    messages.put((command, handle, "", group_name, message, addr))
                # case "join": 
                #     if
                  
            # if client wants to close connection 
            # if data == "/leave":
            #     print("Client disconnected.")
            #     break
        except: 
            pass 


#[3] get info form queue/array and send to client 
def broadcast(): 
    while True: 
        while not messages.empty(): 
            command, handle, sender_handle, group_name, message, addr = messages.get() 
            print(message)

            if addr not in clients: 
                clients.append(addr)
                names.append("[anon]")
                       
            match command: 
                case "all":
                    for client in clients:
                        msg_data = {"command": command, "handle": handle, "message": message} # convert to dict
                        if not convert_and_send(server, msg_data, client):
                            print("Sever sending of ALL command has failed.")
                case "register": 
                    for client in clients:
                        reg_data = {"command": command, "handle": handle}
                        if not convert_and_send(server, reg_data, client):
                            print("Sever sending of REGISTER command has failed.")
                case "msg": 
                    to_data = {"command": command, "handle": "To " + handle, "message": message} 
                    from_data =  {"command": command, "handle": "From " + sender_handle, "message": message} 
                    if handle in names: 
                        addr_index = names.index(handle)
                        to_send = clients[addr_index] 

                    if not convert_and_send(server, from_data, to_send): #display for person being sent to
                        print("Sever sending of MSG command has failed.")
                    if not convert_and_send(server, to_data, addr): #display for person sending 
                        print("Sever sending of MSG command has failed.")
                case "grp":
                    group_index = groups.index(group_name) + 1
                    for members in groups[group_index]:
                        msg_data = {"command": command, "handle": "From " + handle , "group_name": "To " + group_name, "message": message} 
                        if not convert_and_send(server, msg_data, members): #display for person being sent to
                            print("Sever sending of GRP command has failed.")   


t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start() 

# server.close()