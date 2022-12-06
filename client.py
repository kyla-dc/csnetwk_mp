import socket
import json
import threading
import random 

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789
# randomPort = random.randint(8000,9000)

def convert_and_send(sock, data, ip_and_port): # convert and send json to server;
    json_data = json.dumps(data) #convert to json
    try: # error checking
        sock.sendto(json_data.encode(), ip_and_port) # send to server   
        return 1
    except:
        return 0


try:
    clientSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # clientSock.bind((UDP_IP_ADDRESS, randomPort))
except socket.error as err:
    print("Socket error because of %s", err)



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
                    handle = data_parsed["handle"]
                    print(f"Welcome {handle}!")
                case "msg":
                    message = data_parsed["message"]
                    handle = data_parsed["handle"]
                    print(f"[{handle}]: {message}")
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
    input_list = data.split(" ")
    command = input_list[0]
    command_cut = command[1:]

    match command: # still need to check for command parameters
        case "/join": #Note: we shouldn't allow them to input any other commands if they have not joined yet 
            check = 1 
            server_ip = input_list[1]
            chosen_port = int(input_list[2]) 

            if server_ip != UDP_IP_ADDRESS:
                check = 0
                print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")

            if check: 
                # client must be bound to chosen port before being sent to the server 
                clientSock.bind((server_ip, chosen_port))
                command_dict = {"command": command_cut} # convert to dict
                if not convert_and_send(clientSock, command_dict, (UDP_IP_ADDRESS, UDP_PORT_NO)): # run and check if successful
                    print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
            
        case "/leave": #DONE 
            command_dict = {"command": command_cut}
            if not convert_and_send(clientSock, command_dict, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                print("Erorr: Disconnection failed. Please connect to the server first.")
            print("Connection closed. Thank you!")
            break
        
        case "/all": #DONE 
            message = ' '.join(input_list[1:]) # get index 1 till the end for message
            msg_data = {"command": command_cut, "message": message} # convert to dict
            convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO))

        case "/register": #DONE
            handle = input_list[1] # get handle
            reg_data = {"command": command_cut, "handle": handle} #convert to dict
            if not convert_and_send(clientSock, reg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                print("Registration failed. Handle or alias already exists.")

        case "/msg": #DONE
            handle = input_list[1] # get handle
            message = ' '.join(input_list[2:])  # get index 2 till the end for message
            msg_data = {"command": command_cut, "handle": handle, "message": message} # convert to dict
            if not convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                print("Handle or alias not found")

        case "/grp": #DONE 
            group_name = input_list[1] # get group name
            message = ' '.join(input_list[2:])  # get index 2 till the end for message
            msg_data = {"command": command_cut,"group_name": group_name,"message": message} # convert to dict
            if not convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                print("")

        case "/?": #DONE
            print("[ALL ACCEPTED COMMANDS] ")
            print("/join <server_ip_add> <port> - Join a server")
            print("/leave - leave a server")
            print("/register <handle> - register a user")
            print("/all <message> - send a message to all users")
            print("/msg <handle> <message> - send a private message to a user")
            print("/grp <group_name> <message> - join/create a group chat and send a message to it")
            print("/? - show all commands")
        
        case _: #DONE
            print("Error: Command not found")


clientSock.close() 