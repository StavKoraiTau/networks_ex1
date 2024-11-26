
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

FAILED_LOGIN_RESPONSE = "Failed to login."
LOGIN_SUCCESS_RESPONSE_TEMPLATE = "Hi {}, good to see you."

MAX_INT32 = 2**31 - 1
MIN_INT32 = - 2**31

def login_success_template(username):
    return LOGIN_SUCCESS_RESPONSE_TEMPLATE.format(username)

class ServerAppInstance:
    def __init__(self, auth_dict):
        self._auth_dict = auth_dict
        self._username = ""
        self._password = ""
        self._state = State.INIT
        
    def next(self, message):
        if message != None:
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
    
def process_command(message):
    if message.startswith(CALCULATE_COMMAND):
        return calculate(message[len(CALCULATE_COMMAND):].split(" "))
    elif message.startswith(MAX_COMMAND):
        return get_max(message[len(MAX_COMMAND):])
    elif message.startswith(FACTORS_COMMAND):
        return factors(message[len(FACTORS_COMMAND):])
    elif message == QUIT_COMMAND:
        return NextAction.QUIT, None
    else:
        return NextAction.SEND, "Invalid command.".encode()
    
def factors(arg):
    try:
        x = int(arg)
    except:
        return NextAction.SEND, "Invalid format for factor.".encode()
    if x < 2:
        return NextAction.SEND, "Invalid number for factor.".encode()
    if not in_int32_range(x):
        return NextAction.SEND, "Out of range value for factor.".encode()
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
        s += str(factor) + ", "
    return NextAction.SEND, s[:len(s)-2].encode()
        
def get_max(args):
    if len(args) < 3 or args[0] != "(" or args[len(args)-1] != ")":
        return NextAction.SEND, "Invalid format for max.".encode() 
    args = args[1:len(args)-1].split(" ")
    try:
        int_args = [int(s) for s in args]
        max_arg = max(int_args)
        min_args = min(int_args)
        if not in_int32_range(max_arg) or not in_int32_range(min_args):
            return NextAction.SEND, "error: result is too big.".encode() 
        return NextAction.SEND, f"the maximum is {max_arg}".encode()
    except:
        return NextAction.SEND, "Invalid value in max.".encode() 
    
def calculate(args):
    if len(args) != 3:
        return NextAction.SEND, "Invalid calculate format.".encode()
    try:
        x = int(args[0])
        op = args[1]
        y = int(args[2])
        if not in_int32_range(x) or not in_int32_range(y):
            return NextAction.SEND, "Out of range calculate values.".encode()
        if op == "+":
            z = x + y
        elif op == "-":
            z = x - y
        elif op == "*":
            z = x * y
        elif op == "^":
            if y < 0:
                return NextAction.SEND, "Out of range calculate values.".encode()
            z = x ** y
        elif op == "/":
            try:
                z = x / y
            except ZeroDivisionError:
                return NextAction.SEND, f"error: division by zero.".encode()
            if not in_int32_range(z):
                return NextAction.SEND, f"error: result is too big.".encode()
            return NextAction.SEND, f"response: {z:.2f}.".encode()
        else:
            return NextAction.SEND, "Invalid calculate format.".encode()
        if not in_int32_range(z):
            return NextAction.SEND, f"error: result is too big.".encode()
        return NextAction.SEND, f"response: {z}.".encode()
    except:
        return NextAction.SEND, "Invalid value in calculate.".encode()

def in_int32_range(val):
    if val > MAX_INT32 or val < MIN_INT32:
        return False
    return True