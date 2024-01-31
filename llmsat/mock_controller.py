import zmq


def main():
    context = zmq.Context()

    # Connect to the server socket
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:5556")

    print("Client started. Type messages to send to the server.")
    while True:
        message = input("Enter message: ")
        socket.send_string(message)
        reply = socket.recv_string()
        print("Server replied:", reply)


if __name__ == "__main__":
    main()
