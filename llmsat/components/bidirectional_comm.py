import socket
import threading
import cmd2

class BidirectionalCmd2App(cmd2.Cmd):
    def __init__(self, host='localhost', port=65432):
        super().__init__()
        self.prompt = f"App(port {port})> "
        self.host = host
        self.port = port
        self.intro = "Bidirectional Cmd2 Application. Type 'start_server <port>' to start the server on a specified port, 'connect <host> <port>' to connect to another instance, and 'send <message>' to send messages."

    def do_start_server(self, port):
        """Start the server to listen for incoming messages."""
        try:
            port = int(port)
        except ValueError:
            self.poutput("Please provide a valid port number.")
            return

        self.port = port
        server_thread = threading.Thread(target=self.run_server, daemon=True)
        server_thread.start()
        self.poutput(f"Server started on port {port} and listening for messages...")

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                self.poutput(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    self.poutput(f"Received message: {data.decode()}")

    def do_connect(self, args):
        """Connect to another instance."""
        args = args.split()
        if len(args) != 2:
            self.poutput("Usage: connect <host> <port>")
            return

        try:
            remote_host, remote_port = args[0], int(args[1])
        except ValueError:
            self.poutput("Please provide a valid port number.")
            return

        self.remote_host, self.remote_port = remote_host, remote_port
        self.poutput(f"Ready to connect to {self.remote_host} on port {self.remote_port}")

    def do_send(self, message):
        """Send a message to the connected instance."""
        if not hasattr(self, 'remote_host') or not hasattr(self, 'remote_port'):
            self.poutput("Not connected to any instance. Use 'connect' command first.")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.remote_host, self.remote_port))
                s.sendall(message.encode())
                self.poutput(f"Message sent: {message}")
            except ConnectionRefusedError:
                self.poutput("Connection failed. Is the remote instance running and listening?")

if __name__ == '__main__':
    app = BidirectionalCmd2App()
    app.cmdloop()
