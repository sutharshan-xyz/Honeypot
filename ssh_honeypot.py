# Libraries
import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading

# Constants
Logging_Format = logging.Formatter('%(message)s')
SSH_BANNER = "SSH-2.0-MySSHServer_1.0"

host_key = paramiko.RSAKey(filename='server.key')

# Loggers & Logging Files
funnel_logger = logging.getLogger('FunnelLogger')
funnel_logger.setLevel(logging.INFO)
funnel_handler = RotatingFileHandler('audits.log',maxBytes=2000,backupCount=5)
funnel_handler.setFormatter(Logging_Format)
funnel_logger.addHandler(funnel_handler)

creds_logger = logging.getLogger('CredsLogger')
creds_logger.setLevel(logging.INFO)
creds_handler = RotatingFileHandler('cmd_audits.log',maxBytes=2000,backupCount=5)
creds_handler.setFormatter(Logging_Format)
creds_logger.addHandler(creds_handler)

# Emulated Shell

def emulated_shell(channel, client_ip):
    channel.send(b'corporate-jumpbox2$ ')
    command = b""
    while True:
        try:
            char = channel.recv(1)
            if not char:
                # Properly check if channel is closed
                if channel.closed:
                    break
                else:
                    continue   # just wait for more input
        except Exception:
            break

        # echo the character
        try:
            channel.send(char)
        except Exception:
            break

        command += char

        # process command on Enter
        if char in (b'\r', b'\n'):
            cmd_stripped = command.strip()
            if cmd_stripped == b'exit':
                channel.send(b'\n Gooodbye! \r\n')
                channel.close()
                break
            elif cmd_stripped == b'pwd':
                response = b'\n/usr/local/\r\n'
                creds_logger.info(f'Command {cmd_stripped.decode()} executed by {client_ip}')
            elif cmd_stripped == b'whoami':
                response = b"\ncorpuser1\r\n"
                creds_logger.info(f'Command {cmd_stripped.decode()} executed by {client_ip}')
            elif cmd_stripped == b'ls':
                response = b"\njumpbox1.conf\r\n"
                creds_logger.info(f'Command {cmd_stripped.decode()} executed by {client_ip}')
            elif cmd_stripped == b'cat jumpbox1.conf':
                response = b"\nGo to deeboodah.com.\r\n"
                creds_logger.info(f'Command {cmd_stripped.decode()} executed by {client_ip}')
            else:
                response = b"\n" + cmd_stripped + b"\r\n"

            channel.send(response)
            channel.send(b'corporate-jumpbox2$ ')
            command = b""
        
                
# SSH Server + Sockets

class Server(paramiko.ServerInterface):
    
    def __init__(self, client_ip , input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password
        
    def check_channel_request(self, kind, chanid):
         if kind == 'session':
             return paramiko.OPEN_SUCCEEDED
         
    def get_allowed_auth(self,):
         return "password"
        
    def check_auth_password(self, username, password):
        funnel_logger.info(f'Client {self.client_ip} attempted connection with ' f'username: {username}',f'password: {password}')
        creds_logger.info(f'{self.client_ip}, {username} , {password}')
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL
        
    def check_channel_shell_request(self,channel):
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True
    
    def check_channel_exec_request(self, channel, command):
        command = str(command)
        return True
    
def client_handle(client, addr, username, password):
    client_ip = addr[0]
    print(f"{client_ip} has connected to the server.")
    
    try:
        
        transport = paramiko.Transport(client)
        transport.local_version = SSH_BANNER
        server = Server(client_ip=client_ip, input_username=username, input_password=password)
        
        transport.add_server_key(host_key)
        
        transport.start_server(server=server)
        
        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.") 
            
        standard_banner = "Welcome to Ubuntu 22.04 LTS (Jammy Jellyfish)!\r\n\r\n"
        channel.send(standard_banner)
        emulated_shell(channel, client_ip=client_ip)       
        
    except Exception as error:
        print(error)
        print("!!! error !!!")
    finally:
        try:
            transport.close()
        except Exception as error:
            print(error)
            print("!!! error !!!")
        client.close()    
    
    
# Provision SSH-based Honeypot

def honeypot(address, port, username, password):
    
    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))
    
    socks.listen(100)
    print(f"SSH server is listening on {port}.")
    
    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
            
        except Exception as error:
            print(error)
            
honeypot('127.0.0.1' ,2222 ,username=None, password=None)


""" 1:07 """