import zmq

from llmsat.libs import utils


def main():
    context = zmq.Context()
    socket = context.socket(zmq.PAIR)
    socket.connect("tcp://localhost:5556")

    print("Client started. Enter message type and data to send to the server.")
    while True:
        # Get the message type from the user and convert it to uppercase
        message_type_input = input("Enter message type: ").strip().upper()

        # Assuming the user enters a valid message type
        message_type = utils.MessageType[message_type_input]
        data_input = (
            input("Enter message data (optional, press enter to skip): ").strip()
            or None
        )

        message = utils.Message(type=message_type, data=data_input)
        socket.send_pyobj(message)
        print("Message sent to the server.")


if __name__ == "__main__":
    main()
