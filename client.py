import socket
import json
import threading
import random

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789
randomPort = random.randint(8000,9000)

# global current_user
current_user = "[unreg]"

def convert_and_send(sock, data, ip_and_port): # convert and send json to server;
    json_data = json.dumps(data) #convert to json
    try: # error checking
        sock.sendto(json_data.encode(), ip_and_port) # send to server   
        return 1
    except:
        return 0


try:
    clientSock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Note: this is probably what join does??
    #
    # ip address should be the same and port number should be differnet for each client 
    # they can type whatever port number tho 
    clientSock.bind((UDP_IP_ADDRESS, randomPort)) #DEFINE THE PORT OF THE CLIENT 
except socket.error as err:
    print("Socket error because of %s", err)




#[4] get info from server and display to clients 
def receive():

    # Issue found: 
    #     the program will change the handle of the current user based on 
    #     the newest handle that was registred -- thats no bueno 

    # global handle 
    # handle = "[unregsitered]" 

    while True: 
        try:
            data, addr = clientSock.recvfrom(1024)
            data = data.decode("utf-8")
            data_parsed = json.loads(data)
            command = data_parsed["command"]

            match command: 
                case "all": 
                    message = data_parsed["message"]
                    print(f"{handle}: {message}")       #all now displays the user name of the last person to register
                case "register":                        #      rather than the username of the person posting 
                    handle = data_parsed["handle"]
                    print(f"Welcome {handle}!")
                case "msg":
                    message = data_parsed["message"]
                    handle = data_parsed["handle"]
                    print(f"[To {handle}]: {message}") 

                    #displaying for the person sent to still incomplete 
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
        # case "/join":
        #     command_dict = {"command": command_cut} # convert to dict
        #     if not convert_and_send(clientSock, command_dict, (UDP_IP_ADDRESS, UDP_PORT_NO)): # run and check if successful
        #         print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")
            
        # case "/leave": 
        #     command_dict = {"command": command_cut}
        #     if not convert_and_send(clientSock, command_dict, (UDP_IP_ADDRESS, UDP_PORT_NO)):
        #         print("Erorr: Disconnection failed. Please connect to the server first.")
        #     # print("Connection closed. Thank you!")
        #     # break
        
        case "/all":
            message = ' '.join(input_list[1:]) # get index 1 till the end for message
            msg_data = {"command": command_cut, "message": message} # convert to dict
            convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO))

        case "/register":
            handle = input_list[1] # get handle
            current_user = handle 
            reg_data = {"command": command_cut, "handle": handle} #convert to dict
            if not convert_and_send(clientSock, reg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                print("Registration failed. Handle or alias already exists.")

        case "/msg":
            handle = input_list[1] # get handle
            message = ' '.join(input_list[2:])  # get index 2 till the end for message
            msg_data = {"command": command_cut, "handle": handle, "message": message} # convert to dict
            if not convert_and_send(clientSock, msg_data, (UDP_IP_ADDRESS, UDP_PORT_NO)):
                print("Handle or alias not found")

        # case "/?":
        #     command_dict = {"command": command_cut}
        #     convert_and_send(clientSock, command_dict, (UDP_IP_ADDRESS, UDP_PORT_NO))
        
        case _:
            print("Error: Command not found")


#client.close() 
