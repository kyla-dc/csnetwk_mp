import socket
import json
import threading 
import queue

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

messages = queue.Queue() #command--handle--sender_handle--group_name--message--address
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
            handle = "[unreg]"
            message = " "

            data, addr = server.recvfrom(1024)
            data = data.decode("utf-8")
            data_parsed = json.loads(data)
            command = data_parsed["command"]
            

            match command:
                case "join": 
                    port = addr[1]                    
                    if port not in used_ports:
                        used_ports.append(port)
                        print(f"Port {port} succesffully linked to server.")
                        #return to client -- "Connection to message board server is successful" 
                        #note: we could also send the errors via a json ??? or somethin 
                        #we can send them to section 3 to go to client 
                    else:
                        print(f"Port {port} already in use") 
                        #also we can't allow them to do any other actions until they have joined 
                        #return an error in client -- cannot use that port, it's already in use
                        #note: we could also send the errors via a json ??? or somethin 
                        #we can send them to section 3 to go to client  


                case "leave": 
                    # print(">>>>    Before remove")
                    # print(clients)
                    # print(names)
                    # print(used_ports)
                    # print(groups)
                    port = addr[1]
                    if addr in clients: 
                        addr_index = clients.index(addr)
                        add_name = names[addr_index]
                        clients.remove(addr)
                        names.remove(add_name)
                    if port in used_ports: 
                        used_ports.remove(port)
                    for group in groups: 
                        if type(group) == list: 
                            if addr in group:
                                group.remove(addr)
                                if len(group) == 0: 
                                    index = groups.index(group)
                                    groups.remove(group)
                                    groups.pop(index-1)
                    
                    # print(">>>>   After remove")
                    # print(clients)
                    # print(names)
                    # print(used_ports)
                    # print(groups)
                    print("Sucessfully removed client's informaion.")

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
                        sender_handle = "unreg"
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
                        handle = "[unreg]"

                    if group_name not in groups: 
                        groups.append(group_name)
                        groups.append([])
                        curr_group_membs = groups.index([])
                        groups[curr_group_membs].append(addr)
                    else: 
                        group_index = groups.index(group_name) + 1
                        if addr not in groups[group_index]: 
                            groups[group_index].append(addr)
                    messages.put((command, handle, "", group_name, message, addr))
                
        except: 
            pass 


#[3] get info form queue/array and send to client 
def broadcast(): 
    while True: 
        while not messages.empty(): 
            command, handle, sender_handle, group_name, message, addr = messages.get() 

            if addr not in clients: 
                clients.append(addr)
                names.append("unreg")
                       
            match command: 
                case "all":
                    for client in clients:
                        msg_data = {"command": command, "handle": handle, "message": message} # convert to dict
                        if not convert_and_send(server, msg_data, client):
                            print("Sever sending of ALL command has failed.")
                    print(f"ALL: {message}")
                case "register": 
                    for client in clients:
                        reg_data = {"command": command, "handle": handle}
                        if not convert_and_send(server, reg_data, client):
                            print("Sever sending of REGISTER command has failed.")
                    print(f"Register: {handle}")
                case "msg": 
                    print("Server handle: ", sender_handle)
                    if sender_handle != "unreg":
                        to_data = {"command": command, "handle": "To " + handle, "message": message} 
                        from_data =  {"command": command, "handle": "From " + sender_handle, "message": message}

                        if handle in names: 
                            try:
                                addr_index = names.index(handle)
                                to_send = clients[addr_index] 
                            except:
                                convert_and_send(server, "Error: Failed to send message. Please contact administrator", addr)

                            try: 
                                convert_and_send(server, from_data, to_send) #display for person being sent to
                                convert_and_send(server, to_data, addr) #display for person sending 
                                print(f"MSG: To {handle}, from {sender_handle}: {message}") # Send to server
                            except:
                                convert_and_send(server, "Error: Failed to send message. Please contact administrator", addr)
                        else:
                            print("Error: Handle or alias not found")
                            convert_and_send(server, "Error: Handle or alias not found", addr)
                    else:
                        convert_and_send(server, "Error: Please register before sending a private message.", addr)
                        print("Error: Please register before sending a private message.")

                case "grp":
                    group_index = groups.index(group_name) + 1
                    for member in groups[group_index]:
                        msg_data = {"command": command, "handle": "From " + handle , "group_name": "To " + group_name, "message": message} 
                        if not convert_and_send(server, msg_data, member): #display for person being sent to
                            print("Sever sending of GRP command has failed.")
                    print(f"GRP: To {group_name}, From {handle}: {message}")   


t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start() 
