import socket
import json
import threading 
import queue

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

messages = queue.Queue() #command--handle--sender_handle--group_name--message--error--address
clients = []
names = []
groups = []
used_ports = [] 

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((UDP_IP_ADDRESS, UDP_PORT_NO))

def convert_and_send(sock, data, ip_and_port): 
    json_data = json.dumps(data) 
    try:
        sock.sendto(json_data.encode(), ip_and_port)   
        return 1
    except:
        return 0


#[2] get info from client and add to queue/array 
def receive(): 
    while True:
        try:
            handle = "unreg"
            sender_handle = ""
            group_name = ""
            message = ""
            error = 0

            data, addr = server.recvfrom(1024)
            data = data.decode("utf-8")
            data_parsed = json.loads(data)
            command = data_parsed["command"]
            
            match command:
                case "leave": 
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
                    print("Client left. Sucessfully removed client's informaion.")

                case "all": 
                    print(addr)
                    message = data_parsed["message"]                    
                    if addr in clients:
                        name_index = clients.index(addr) 
                        handle = names[name_index]
                    messages.put((command, handle, sender_handle, group_name, message, error, addr)) 
                
                case "register":
                    handle = data_parsed["handle"]
                    messages.put((command, handle, sender_handle, group_name, message, error, addr))
                    if handle == "unreg":
                        error = 2
                        messages.put((command, handle, sender_handle, group_name, message, error, addr))
                    if handle not in names: 
                        if addr not in clients: 
                            clients.append(addr)
                            names.append(handle)
                        elif addr in clients: 
                            name_index = clients.index(addr)
                            if names[name_index] != handle: 
                                names[name_index] = handle
                    else: 
                        if error == 0: 
                            error = 1 
                            messages.put((command, handle, sender_handle, group_name, message, error, addr))
                       
                case "msg": 
                    handle = data_parsed["handle"]
                    message = data_parsed["message"]
                    if addr in clients:
                        name_index = clients.index(addr) 
                        sender_handle = names[name_index]
                    else: 
                        sender_handle = ""
                    messages.put((command, handle, sender_handle, group_name, message, error, addr))

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
                        handle = "unreg"

                    if group_name not in groups: 
                        groups.append(group_name)
                        groups.append([])
                        curr_group_membs = groups.index([])
                        groups[curr_group_membs].append(addr)
                    else: 
                        group_index = groups.index(group_name) + 1
                        if addr not in groups[group_index]: 
                            groups[group_index].append(addr)
                    messages.put((command, handle, sender_handle, group_name, message, error, addr))     
        except: 
            pass 


#[3] get info form queue/array and send to client 
def broadcast(): 
    while True: 
        while not messages.empty(): 
            command, handle, sender_handle, group_name, message, error, addr = messages.get() 

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
                        reg_data = {"command": command, "handle": handle, "error": error}
                        if not convert_and_send(server, reg_data, client):
                            print("Sever sending of REGISTER command has failed.")
                    if error == 0:
                        print(f"Register: {handle}")
                    elif error == 1: 
                        print("Register failed: Handle already exists")
                    elif error == 2: 
                        print("Register failed: Invalid handle (unreg)")
                
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
                    print(f"MSG: To {handle}, from {sender_handle}: {message}")
                
                case "grp":
                    group_index = groups.index(group_name) + 1
                    for member in groups[group_index]:
                        msg_data = {"command": command, "handle": "From " + handle , "group_name": "To " + group_name, "message": message} 
                        if not convert_and_send(server, msg_data, member): 
                            print("Sever sending of GRP command has failed.")
                    print(f"GRP: To {group_name}, From {handle}: {message}")   


t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start() 
