import threading
import socket
import json
from pyperclip import copy,paste
import argparse

import os

"""
For clipboard:
On Linux, install xclip, xsel, or wl-clipboard (for "wayland" sessions) via package manager.
For example, in Debian:
    sudo apt-get install xclip
    sudo apt-get install xsel
    sudo apt-get install wl-clipboard
"""
try:
    os.system('title g++')
except Exception as e:
    print('Error occured while setting title: ', e)
    pass

def get_clipboard():
    try:
        return paste()
    except Exception as e:
        print("Clipboard paste failed: ", e)
        return None
    
def set_clipboard(data):
    try:
        copy(data)
    except Exception as e:
        print("Clipboard copy failed: ", e)

class MesssageType:
    JOIN = 1
    LEAVE = 2
    TEXT = 3
    FILE = 4
    PARTIAL_FILE = 5
    END_FILE = 6


snippets = {
    # keys should be in lowercase
}
from snp import snippets


class Message:
    def __init__(self, sender, content, message_type: MesssageType,file_name=None,seq=0) -> None:
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.file_name = file_name
        self.seq = seq

    def __str__(self) -> str:
        return f'{self.sender} - {self.content}'

    def __repr__(self) -> str:
        return f'{self.sender} - {self.content}'

    def to_json(self):
        return json.dumps({
            'sender': self.sender,
            'content': self.content,
            'message_type': self.message_type,
            'file_name': self.file_name,
            'seq': self.seq
        })

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return Message(data['sender'], data['content'], data['message_type'], data.get('file_name', None), data.get('seq', 0))

class Peer:
    def __init__(self, host = '0.0.0.0', port = 12345) -> None:
        self.peerlist = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = port
        self.server.bind((host, self.port))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Increase the send buffer size
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        
        # Increase the receive buffer size
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.Sender_thread = threading.Thread(target=self.Sender,daemon=True)
        self.name = input('Enter your name: ')
        self.send_data(self.name, MesssageType.JOIN)
        self.run = True
        #Get address of the peer
        self.ip = socket.gethostbyname(socket.gethostname())
        print(f'Your IP Address is: {self.ip}')
        self.Sender_thread.start()
        self.listen()

    def Sender(self):
        while self.run:
            try:
                msg = input(':> ')
            except:
                print('Error occured while sending message')
                self.run = False
                break
            if msg == 'exit':
                self.send_data(self.name, MesssageType.LEAVE)
                self.server.close()
                break
            if msg == 'list':
                print(self.peerlist)
            elif msg in ['paste', 'p']:
                data = get_clipboard()
                if data:
                    self.send_data(data, MesssageType.TEXT)
            elif msg in ['list-snippets', 'ls']:
                snippet_indexing = {i: key for i, key in enumerate(snippets.keys())}
                print("Available snippets:")
                for i, key in snippet_indexing.items():
                    print(f'{i}. {key}')
            elif msg == 'cls':
                os.system('cls')
            elif msg in ['snippets', 's']:
                snippet_indexing = {i: key for i, key in enumerate(snippets.keys())}
                for i, key in snippet_indexing.items():
                    print(f'{i}. {key}')
                try:
                    required_snippet = int(input('Enter the snippet number: '))
                except:
                    print('Invalid input')
                    continue
                try:
                    snippet = snippets[snippet_indexing[required_snippet]]
                    print(snippet)
                    set_clipboard(snippet)
                    print(f"✓ Snippet '{snippet_indexing[required_snippet]}' copied to clipboard!")
                except:
                    print('Invalid snippet number')

            elif msg.startswith('file'):
                filename = msg.split(' ')[1]
                self.send_data(filename, MesssageType.FILE)
            elif msg.startswith('copy'):
                parts = msg.split(' ', 1)
                if len(parts) == 1:
                    print("Usage: copy <snippet_name_or_number>")
                    print("Example: copy DFS  or  copy 0")
                    continue
                
                target = parts[1].strip()
                snippet_indexing = {i: key for i, key in enumerate(snippets.keys())}
                snippet_found = False
                
                try:
                    snippet_num = int(target)
                    if snippet_num in snippet_indexing:
                        snippet_name = snippet_indexing[snippet_num]
                        snippet = snippets[snippet_name]
                        set_clipboard(snippet)
                        print(f"✓ Snippet '{snippet_name}' copied to clipboard!")
                        snippet_found = True
                except ValueError:
                    pass
                
                if not snippet_found:
                    for key in snippets.keys():
                        if key.lower() == target.lower():
                            snippet = snippets[key]
                            set_clipboard(snippet)
                            print(f"✓ Snippet '{key}' copied to clipboard!")
                            snippet_found = True
                            break
                
                if not snippet_found:
                    print(f"Snippet '{target}' not found.")
                    print("Available snippets:")
                    for i, key in snippet_indexing.items():
                        print(f'{i}. {key}')
                        
            elif msg in ('help', 'h'):
                print("""
Commands:
1. list: List all the peers
2. paste - p: Send clipboard data
3. cls: Clear the screen
4. list-snippets - ls: Show available snippets
5. snippets - s: List all the snippets and select one to copy
6. copy <name_or_number>: Copy specific snippet to clipboard
7. file <filename>: Send file (alpha)
8. help - h: Show this help message
                """
                )
            else:
                self.send_data(msg, MesssageType.TEXT)
            


    def listen(self):
        file_data = dict()
        while self.run:
            try:
                data, addr = self.server.recvfrom(65536)
            except socket.error as e:
                print(e)
                break
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
                self.run = False
                break
            message = Message.from_json(data)
            
            if addr[0] == self.ip:
                continue
            
            elif message.message_type == MesssageType.JOIN:
                name = message.content
                if addr not in self.peerlist:
                #self.server.sendto(f'join:{self.name}'.encode(), addr)
                    print(f'{name} joined the chat')
                    self.send_data(self.name, MesssageType.JOIN)
                    self.peerlist[addr] = name
            elif message.message_type == MesssageType.PARTIAL_FILE:
                if message.file_name not in file_data:
                    file_data[message.file_name] = dict()
                file_data[message.file_name][message.seq] = message.content
                
            elif message.message_type == MesssageType.END_FILE:
                keys = list(file_data[message.file_name].keys())
                keys.sort()
                with open(self.name+message.file_name, 'w') as file:
                    for key in keys:
                        file.write(file_data[message.file_name][key])
                    
                print(f'File {message.file_name} received')
            elif message.message_type == MesssageType.LEAVE:
                name = message.content
                print(f'{name} left the chat')
                self.peerlist.pop(addr)
            else:
                print(f"{message.sender}:{message.content}")

    def send_msg(self, data):
        self.server.sendto(data.encode(), ('255.255.255.255', 12345))
        

    def send_data(self, content, message_type: MesssageType):
        
        if message_type == MesssageType.TEXT:
            message = Message(self.name, content, message_type)
        elif message_type == MesssageType.FILE:
            with open(content, 'r') as file:
                seq = 0
                data = file.read(100)
                while data:
                    message = Message(self.name, data, MesssageType.PARTIAL_FILE, content,seq)
                    seq+=1
                    self.send_msg(message.to_json())
                    data = file.read(100)

                message = Message(self.name, '', MesssageType.END_FILE, content)
                
        else:
            message = Message(self.name, content, message_type)
        self.send_msg(message.to_json())
        



if __name__ == '__main__':

    peer=Peer()

