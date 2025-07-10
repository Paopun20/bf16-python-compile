import socket
import time
import threading

class BF16Server:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None
        self.addr = None
        self.running = False
        self.client_connected_event = threading.Event()

    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f"[BF16Server] Listening on {self.host}:{self.port}")
            self.running = True

            # Accept connection in background
            threading.Thread(target=self._accept_connection, daemon=True).start()
        except Exception as e:
            print(f"[BF16Server] Error in start(): {e}")

    def _accept_connection(self):
        try:
            self.conn, self.addr = self.socket.accept()
            print(f"[BF16Server] Connected by {self.addr}")
            self.client_connected_event.set()  # Signal ready

            # Handle the client
            threading.Thread(target=self.handle_client, args=(self.conn,), daemon=True).start()
        except Exception as e:
            print(f"[BF16Server] Accept failed: {e}")

    def wait_for_client(self, timeout: float = None) -> bool:
        """Block until a client connects (or timeout in seconds). Returns True if connected."""
        connected = self.client_connected_event.wait(timeout)
        if connected:
            print("[BF16Server] Client is ready.")
        else:
            print("[BF16Server] Wait for client timed out.")
        return connected

    def handle_client(self, conn):
        try:
            with conn:
                while self.running:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            break
                        print(f"[BF16Server] Received: {data.decode()}")
                        conn.sendall(data)
                        time.sleep(0.01)
                    except ConnectionResetError:
                        print("[BF16Server] Client disconnected.")
                        break
        finally:
            print("[BF16Server] Client handler terminated.")
            self.conn = None

    def send_data_to_client(self, data: any):
        if self.conn:
            try:
                self.conn.sendall(str(data).encode())
            except BrokenPipeError:
                print("[BF16Server] Broken pipe — client disconnected.")
                self.conn = None
            except Exception as e:
                print(f"[BF16Server] Error sending data: {e}")

    def stop(self):
        self.running = False
        if self.conn:
            try:
                self.conn.shutdown(socket.SHUT_RDWR)
                self.conn.close()
            except:
                pass
        self.socket.close()
        print("[BF16Server] Server stopped.")

class BF16Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"Connection refused. Is the server running at {self.host}:{self.port}?")
            return False
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False

    def send_data(self, data: str):
        try:
            self.socket.sendall(data.encode())
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive_data(self):
        try:
            data = self.socket.recv(1024)
            return data.decode()
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None

    def close(self):
        self.socket.close()
        print("Connection closed.")