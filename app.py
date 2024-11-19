
from enum import Enum
class NextAction(Enum):
    SEND = 1
    RECV = 2
    QUIT = 3

class State(Enum):
    INIT = 0
    W_WELCOME = 1
    R_USERNAME = 2
    R_PASSWORD = 3
    W_FAILED_LOGIN = 4
    W_HI_LOGIN = 5
    R_COMMAND = 6
    W_RESULT = 7
    
USERNAME_COMMAND = "User: "
PASSWORD_COMMAND = "Password: "
CALCULATE_COMMAND = "calculate: "
MAX_COMMAND = "max: "
FACTORS_COMMAND = "factors: "
QUIT_COMMAND = "quit"

class AppInstance:
    def __init__(self, auth_dict : dict[str,str]) -> None:
        self._auth_dict = auth_dict
        self._username = ""
        self._password = ""
        self._state = State.INIT
        
    def next(self,message : bytes | None = None) -> tuple[NextAction, bytes | None]:
        if message != None:
            print(message)
            message = message.decode()
        if self._state == State.INIT:
            self._state = State.W_WELCOME
            return NextAction.SEND, b"Welcome. Please sign in."
        
        elif self._state == State.W_WELCOME:
            self._state = State.R_USERNAME
            return NextAction.RECV, None
        
        elif self._state == State.R_USERNAME:
            if message == None or not message.startswith(USERNAME_COMMAND):
                return NextAction.QUIT, None
            self._username = message[len(USERNAME_COMMAND):]
            self._state = State.R_PASSWORD
            return NextAction.RECV, None
        
        elif self._state == State.R_PASSWORD:
            if message == None or not message.startswith(PASSWORD_COMMAND):
                return NextAction.QUIT, None
            self._password = message[len(PASSWORD_COMMAND):]
            if self.authenticate():
                self._state = State.W_HI_LOGIN
                return NextAction.SEND, f"Hi {self._username}, good to see you.".encode()
            else:
                self._state = State.W_FAILED_LOGIN
                return NextAction.SEND, "Failed to login.".encode()
            
        elif self._state == State.W_HI_LOGIN:
            self._state = State.R_COMMAND
            return NextAction.RECV, None
        
        elif self._state == State.W_FAILED_LOGIN:
            self._state = State.R_USERNAME
            return NextAction.RECV, None
        
        elif self._state == State.R_COMMAND:
            if message == None:
                raise Exception("Expected command")
            self._state = State.W_RESULT
            return process_command(message)
        elif self._state == State.W_RESULT:
            self._state = State.R_COMMAND
            return NextAction.RECV, None
        raise Exception("Unexpected state")
            
    def authenticate(self):
        if self._username in self._auth_dict:
            if self._auth_dict[self._username] == self._password:
                return True
        return False
    
def process_command(message : str) -> tuple[NextAction, bytes | None]:
    if message.startswith(CALCULATE_COMMAND):
        return calculate(message[len(CALCULATE_COMMAND):].split(" "))
    elif message.startswith(MAX_COMMAND):
        return get_max(message[len(MAX_COMMAND)+1:len(message)-1].split(" "))
    elif message.startswith(FACTORS_COMMAND):
        return factors(message[len(FACTORS_COMMAND):])
    else:
        return NextAction.QUIT, None
    
def factors(arg : str):
    try:
        x = int(arg)
    except:
        return NextAction.QUIT, None
    if x < 2:
        return NextAction.QUIT, None
    x_factors = set()
    y = 2
    while x > 1:
        if x % y == 0:
            x_factors.add(y)
            x = x // y
            y = 2
            continue
        y += 1
    s = f"the prime factors of {arg} are: "
    for factor in sorted(x_factors):
        s += str(factor) + ","
    return NextAction.SEND, s[:len(s)-1].encode()
        
def get_max(args : list[str]) -> tuple[NextAction, bytes | None]:
    try:
        return NextAction.SEND, f"the maximum is {max([int(s) for s in args])}.".encode()
    except:
        return NextAction.QUIT, None 
def calculate(args : list[str]) -> tuple[NextAction, bytes | None]:
    try:
        x = int(args[0])
        op = args[1]
        y = int(args[2])
        if op == "+":
            z = x + y
        elif op == "-":
            z = x - y
        elif op == "*":
            z = x * y
        elif op == "^":
            z = x ** y
        elif op == "/":
            z = x / y
            if z > 2**31 - 1 or z < -2**31:
                return NextAction.SEND, f"error: result is too big.".encode()
            return NextAction.SEND, f"response: {z:.2f}.".encode()
        else:
            return NextAction.QUIT, None
        if z > 2**31 - 1 or z < -2**31:
            return NextAction.SEND, f"error: result is too big.".encode()
        return NextAction.SEND, f"response: {z}.".encode()
    except:
        return NextAction.QUIT, None
    