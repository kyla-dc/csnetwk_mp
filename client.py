import socket
import json
import threading

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789
join_checker = 0

def convert_and_send(sock, data, ip_and_port):
    json_data = json.dumps(data) 
    try: 
        sock.sendto(json_data.encode(), ip_and_port) 
        return 1
    except:
        return 0


#[4] get info from server and display to clients 
def receive():
    while True: 
        try:
            data, addr = clientSock.recvfrom(1024)
            data = data.decode("utf-8")
            data_parsed = json.loads(data)
            command = data_parsed["command"]

            match command:
                case "all":
                    handle = data_parsed["handle"]
                    message = data_parsed["message"]
                    print(f"{handle}: {message}")       
                case "register":           
                    error = data_parsed["error"]
                    if error == 0:                     
                        handle = data_parsed["handle"]
                        print(f"Welcome {handle}!")
                    elif error == 1: 
                        print("Error: Registration failed. Handle or alias already exists.")
                    elif error == 2: 
                         print("Error: Registration failed. That is an invalid handle or alias.")
                case "msg":
                    message = data_parsed["message"]
                    handle = data_parsed["handle"]
                    error = data_parsed["error"]
                    if error == 0: 
                        print(f"[{handle}]: {message}")
                    elif error == 1: 
                        print("Error: Handle or alias not found.")
                    elif error == 2: 
                        print("Error: Cannot direct message yourself.")
                    elif error == 3: 
                        print("Error: Cannot direct message an unregistered client.")
                case "grp":
                    message = data_parsed["message"]
                    handle = data_parsed["handle"]
                    group_name = data_parsed["group_name"]
                    print(f"[{group_name}, {handle}]: {message}")
        except: 
            pass 


t = threading.Thread(target=receive) 
t.start() 

#[1] get info form input and send to server 
while True: 
    data = input()
    og_input_list = data.split(" ")
    command = og_input_list[0]
    command_cut = command[1:]

    input_list = list(filter(None, og_input_list))

    if ((join_checker == 0 and (command == "/join" or command == "/leave" or command =="/?"))) or join_checker == 1: 
        match command: 
            case "/join": #DONE 
                if len(input_list) == 3: 
                    check = 1 
                    server_ip = input_list[1]
                    try: #2 byte unsigned
                        chosen_port = int(input_list[2])
                        clientSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) 
                        if server_ip == "127.0.0.1":
                            try: clientSock.bind((server_ip, chosen_port))  # client must be bound to chosen port before being sent to the server 
                            except: check = 0
                            if check: 
                                join_checker = 1
                                print("Connection to the Message Board Server is successful!")
                            else: 
                                print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
                        else:
                            print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
                    except:
                        print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
                else: 
                    print("Error: Command parameters do not match or is not allowed.")
                
            case "/leave": #DONE 
                if len(input_list) == 1: 
                    command_dict = {"command": command_cut}
                    if join_checker == 1: 
                        if not convert_and_send(clientSock, command_dict, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                            print("Erorr: Disconnection failed. Please connect to the server first.")
                        print("Connection closed. Thank you!")
                        break
                    else: 
                        print("Error: Disconnection failed. Please connect to the server first.")
                else:
                    print("Error: Command parameters do not match or is not allowed.")
            
            case "/all": 
                if len(input_list) >= 2:
                    message = ' '.join(input_list[1:]) # get index 1 till the end for message
                    msg_data = {"command": command_cut, "message": message} # convert to dict
                    convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO))
                else:
                    print("Error: Command parameters do not match or is not allowed.")

            case "/register":
                if len(input_list) == 2: 
                    handle = input_list[1] # get handle
                    reg_data = {"command": command_cut, "handle": handle} #convert to dict
                    if not convert_and_send(clientSock, reg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                        print("Error: Register command was not sent to server.")
                else:
                    print("Error: Command parameters do not match or is not allowed.")

            case "/msg": 
                if len(input_list) >= 3:
                    handle = input_list[1] # get handle
                    message = ' '.join(input_list[2:])  # get index 2 till the end for message
                    msg_data = {"command": command_cut, "handle": handle, "message": message} # convert to dict
                    if not convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                        print("Error: Msg command was not sent to server.")
                else:
                    print("Error: Command parameters do not match or is not allowed.")

            case "/grp":  
                if len(input_list) >= 3:
                    group_name = input_list[1] # get group name
                    message = ' '.join(input_list[2:])  # get index 2 till the end for message
                    msg_data = {"command": command_cut,"group_name": group_name,"message": message} # convert to dict
                    if not convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                        print("Error: Grp command was not sent to server.")
                else:
                    print("Error: Command parameters do not match or is not allowed.")

            case "/?": #DONE 
                if len(input_list) == 1:
                    print("[ALL ACCEPTED COMMANDS] ")
                    print("/join <server_ip_add> <port> - Join a server")
                    print("/leave - leave a server")
                    print("/register <handle> - register a user")
                    print("/all <message> - send a message to all users")
                    print("/msg <handle> <message> - send a private message to a user")
                    print("/grp <group_name> <message> - join/create a group chat and send a message to it")
                    print("/? - show all commands")
                else:
                    print("Error: Command parameters do not match or is not allowed.")
            
            case _: #DONE
                print("Error: Command not found")  

    else: 
        print("Please join the server before typing any other commands.")


clientSock.close() 

