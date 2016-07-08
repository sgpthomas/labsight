""" Symbols """
class Symbol:    
    GET = "?"
    SET = "!"
    ANSWER = "$"
    OPEN_STREAM = ">"
    CLOSE_STREAM = "/"

"""Commands"""
class Command:
    ID = "id"
    STEP = "step"
    KILL = "kill"
    SPEED = "speed"

""" Message Structure """
class Message:
    def __init__(self, symbol, command, data):
        self.symbol = symbol
        self.command = command
        self.data = data

    def __repr__(self):
        return "Message({}, {}, {})".format(self.symbol, self.command, self.data)

def sendMessage(msg, ser, func=None):
    # define delay because of serial gods looking down on us
    delay = 0.6
    try:
        # create message
        msg_string = "{} {} {}".format(msg.symbol, msg.command, msg.data)

        # ask the gods of serial about the delays
        # sleep(delay)
        ser.write(bytes(msg_string, "ascii"))
        # sleep(delay)

        # read response and strip extrenous space and split it
        response = ser.readline().strip().decode("ascii").split(" ")

        # make sure that there are 3 parts
        if len(response) != 3:
            raise Exception("Arduino response was not proper length, but was {}".format(response))

        # format response array into a Message object
        response = Message(response[0], response[1], response[2])

        # make sure that response has the same command as initial message
        if response.command != msg.command:
            raise Exception("Arduino responded with incorrect command. {} instead of {}".format(response.command, msg.command))

        # if response opens a stream, pass the serial instance to a given function
        if response.symbol == Symbol.OPEN_STREAM:
            while True:
                response = ser.readline().strip().decode("ascii").split(" ")

                # check if received full message or just data
                if len(response) == 3:
                    # format response array into a Message object
                    response = Message(response[0], response[1], response[2])

                    if (response.symbol == Symbol.CLOSE_STREAM):
                        break
                if func != None:
                    func(response)

        return response
    except SerialException:
        print("Failed to open {}".format(port))