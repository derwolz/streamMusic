"""
Network listener for remote control commands
"""
import socket
import threading
from typing import Optional, Callable, Dict

class NetworkListener:
    """Handles network commands for remote control"""
    
    def __init__(self, port: int = 5556, host: str = 'localhost'):
        self.host = host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.server_running = False
        self.command_handlers: Dict[str, Callable[[], None]] = {}
    
    def register_command(self, command: str, handler: Callable[[], None]) -> None:
        """Register a command handler"""
        self.command_handlers[command] = handler
    
    def start_listening(self) -> None:
        """Start the network listener in a separate thread"""
        def listen():
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.listen(5)
                self.server_running = True
                
                while self.server_running:
                    try:
                        client_socket, address = self.server_socket.accept()
                        data = client_socket.recv(1024).decode('utf-8').strip()
                        
                        # Handle the command
                        if data in self.command_handlers:
                            # Execute handler in main thread using after()
                            handler = self.command_handlers[data]
                            # This will be called from UI thread via after()
                            threading.Thread(target=handler, daemon=True).start()
                            
                        client_socket.close()
                    except socket.error:
                        if self.server_running:
                            print(f"Socket error in network listener")
                        break
                        
            except Exception as e:
                print(f"Network listener error: {e}")
        
        threading.Thread(target=listen, daemon=True).start()
    
    def stop_listening(self) -> None:
        """Stop the network listener"""
        self.server_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
    
    def send_command(self, command: str, host: str = None, port: int = None) -> bool:
        """Send a command to another instance (utility method)"""
        target_host = host or self.host
        target_port = port or self.port
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((target_host, target_port))
            client_socket.send(command.encode('utf-8'))
            client_socket.close()
            return True
        except Exception as e:
            print(f"Failed to send command '{command}': {e}")
            return False
