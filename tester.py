import subprocess
import time
WELCOME = "Welcome. Please sign in."
HI_MSG = "Hi {}, good to see you."
INVALID_LOGIN_PREFIX = "Invalid Login Format."
LOGIN_FAIL = "Failed to login."
CALC_RESPONSE = "response: {}."
TOO_BIG_RESULT = "error: result is too big."
MAX_RESPONSE = "the maximum is {}"
FACTORS_RESPONSE = "the prime factors of {} are: {}"
INVALID_COMMAND = "Invalid command."
INVALID_COMMAND_FORMAT = "Invalid command format"
INVALID_FORMAT_FACTOR = "Invalid format for factor."
INVALID_VALUE_FACTOR = "Invalid number for factor."
INVALID_FORMAT_MAX = "Invalid format for max."
INVALID_VALUE_MAX = "Invalid value in max."
INVALID_FORMAT_CALCULATE = "Invalid calculate format."
INVALID_VALUE_CALCULATE = "Invalid value in calculate."



def main():
    server = subprocess.Popen(["./numbers_server.py","tester_db.txt","1442"],executable="./numbers_server.py",
                              stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                              encoding="utf-8")
    time.sleep(0.2)
    print("functionality test:")
    basic_functionality()
    print("stress test:")
    stress_test()
    print("multi-client test:")
    multi_client()
    #print("ip test:")
    #ip_test()
    print("calculate test:")
    calculate_test()
    print("factors test:")
    factor_test()
    print("max test:")
    max_test()
    print("login test:")
    login_test()
    server.send_signal(2)
    server.wait()

def basic_functionality():
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    if readline_stdout(client) != WELCOME:
        print("1 Welcome message error")
        return
    writeline_stdin(client,"User: stav")
    writeline_stdin(client,"Password: 123")
    if readline_stdout(client) != LOGIN_FAIL:
        print("2 Login failed message error")
        return
    writeline_stdin(client,"User: stav")
    writeline_stdin(client,"Password: 1234")
    response = readline_stdout(client)
    if response != HI_MSG.format("stav"):
        print("3 Hi message error")
        print(response)
        return
    writeline_stdin(client, "calculate: 1 + 2")
    if readline_stdout(client) != CALC_RESPONSE.format(3):
        print("4 calc response error")
        return
    writeline_stdin(client, "calculate: 2 ^ 32")
    if readline_stdout(client) != TOO_BIG_RESULT:
        print("5 calc response error")
        return
    writeline_stdin(client, "calculate: 2 / 2")
    if readline_stdout(client) != CALC_RESPONSE.format(f"{1:.2f}"):
        print("6 calc response error")
        return
    writeline_stdin(client, "max: (-2 -32)")
    response = readline_stdout(client)
    if response != MAX_RESPONSE.format(-2):
        print(response)
        print("7 max response error")
        return
    writeline_stdin(client, "factors: 49")
    response = readline_stdout(client)
    if response != FACTORS_RESPONSE.format(49,7):
        print("8 factors response error")
        print(response)
        return
    writeline_stdin(client, "factors: 10251")
    if readline_stdout(client) != FACTORS_RESPONSE.format(10251,f"{3}, {17}, {67}"):
        print("9 factors response error")
        return
    writeline_stdin(client, "quit")
    client.wait()
    print("passed functionality test")
    
def stress_test():
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    if readline_stdout(client) != WELCOME:
        print("1 Welcome message error")
        return
    writeline_stdin(client,"User: stav")
    writeline_stdin(client,"Password: 123")
    if readline_stdout(client) != LOGIN_FAIL:
        print("2 Login failed message error")
        return
    writeline_stdin(client,"User: stav")
    writeline_stdin(client,"Password: 1234")
    if readline_stdout(client) != HI_MSG.format("stav"):
        print("3 Hi message error")
        return
    msg = max_str([i for i in range(2**23)])
    writeline_stdin(client, msg)
    if readline_stdout(client) != MAX_RESPONSE.format(2**23 - 1):
        print("4 max stress error")
        return
    writeline_stdin(client, "quit")
    client.wait()
    print("passed stress test")
    
def multi_client():#not extensive because of tcp buffers
    client1 = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    if readline_stdout(client1) != WELCOME:
        print("1 Welcome message error")
        return
    client2 = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    if readline_stdout(client2) != WELCOME:
        print("2 Welcome message error")
        return
    writeline_stdin(client1,"User: stav")
    writeline_stdin(client1,"Password: 1234")
    if readline_stdout(client1) != HI_MSG.format("stav"):
        print("3 Hi message error")
        return
    writeline_stdin(client2,"User: vats")
    writeline_stdin(client2,"Password: 4321")
    if readline_stdout(client2) != HI_MSG.format("vats"):
        print("4 Hi message error")
        return
    writeline_stdin(client2, "calculate: 3 + 4")
    client3 = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    if readline_stdout(client3) != WELCOME:
        print("5 Welcome message error")
        return
    writeline_stdin(client3,"User: tester")
    writeline_stdin(client3,"Password: retset")
    
    if readline_stdout(client3) != HI_MSG.format("tester"):
        print("6 Hi message error")
        return
    writeline_stdin(client3,"factors: 1337")
    if readline_stdout(client3) != FACTORS_RESPONSE.format("1337","7, 191"):
        print("7 Factors message error")
        return
    writeline_stdin(client3, "quit")
    client3.wait()
    writeline_stdin(client1, "max: (1 2)")
    if readline_stdout(client1) != MAX_RESPONSE.format(2):
        print("8 max message error")
        return
    if readline_stdout(client2) != CALC_RESPONSE.format(7):
        print("9 calc message error")
        return
    client4 = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    if readline_stdout(client4) != WELCOME:
        print("10 Welcome message error")
        return
    writeline_stdin(client4,"User: stav")
    writeline_stdin(client4,"Password: 1234")
    if readline_stdout(client4) != HI_MSG.format("stav"):
        print("11 Hi message error")
        return
    writeline_stdin(client4, "quit")
    client3.wait()
    writeline_stdin(client1, "quit")
    client1.wait()
    writeline_stdin(client2, "quit")
    client2.wait()

    
    print("passed multi-client test")
    
def ip_test():
    server = subprocess.Popen(["./numbers_server.py","tester_db.txt","1503"],executable="./numbers_server.py",
                            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                            encoding="utf-8")
    time.sleep(0.2)
    client = subprocess.Popen(["./numbers_client.py","192.168.56.1","1503"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    
    if readline_stdout(client) != WELCOME:
        print("Welcome message error")
        return
    writeline_stdin(client,"quit")
    client.wait()
    server.send_signal(2)
    server.wait()
    print("passed ip test")

def calculate_test():
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: 230 + -231")
    if readline_stdout(client) != CALC_RESPONSE.format(-1):
        print("1 error calculate")
        return
    writeline_stdin(client,"calculate: {} + {}".format(2**31 - 1,1))
    if readline_stdout(client) != TOO_BIG_RESULT:
        print("2 too big test")
        return
    writeline_stdin(client,"calculate: {} + {}".format(-2**30 - 1,-2**30))
    if readline_stdout(client) != TOO_BIG_RESULT:
        print("3 too big test")
        return
    writeline_stdin(client,"calculate: {} + {}".format("test",-2**30))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("4 invalid test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} + {}".format(1,-2**32))
    if not readline_stdout(client).startswith("Out of range"):
        print("5 Out of range test")
        return
    writeline_stdin(client,"calculate: {} - {}".format(2**30,-2**30))
    if readline_stdout(client) != TOO_BIG_RESULT:
        print("6 too big test")
        return
    writeline_stdin(client,"calculate: {} - {}".format(10,-10))
    if readline_stdout(client) != CALC_RESPONSE.format(20):
        print("7 error, response test")
        return
    writeline_stdin(client,"calculate: {} - {}".format("test",-2**30))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("8 invalid test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} * {}".format(2,-2**30))
    if readline_stdout(client) != CALC_RESPONSE.format(-2**31):
        print("9 error, response test")
        return
    writeline_stdin(client,"calculate: {} * {}".format(4,-2**30))
    if readline_stdout(client) != TOO_BIG_RESULT:
        print("10 error, response test")
        return
    writeline_stdin(client,"calculate: {} * {}".format("t112",-2**30))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("11 error, response test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} / {}".format(4,2))
    if readline_stdout(client) != f"response: {2:.2f}.":
        print("12 error, response test")
        return
    writeline_stdin(client,"calculate: {} / {}".format(-2**31,-1))
    response = readline_stdout(client)
    if response != TOO_BIG_RESULT:
        print("13 error, too big test")
        print(response)
        return
    writeline_stdin(client,"calculate: {} / {}".format(10,3))
    if readline_stdout(client) != f"response: {10/3:.2f}.":
        print("14 error, response test")
        return
    writeline_stdin(client,"calculate: {} / {}".format(10.2,3))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("15 error, response test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} ^ {}".format(2,31))
    if readline_stdout(client) != TOO_BIG_RESULT:
        print("16 error, too big test")
        return
    writeline_stdin(client,"calculate: {} ^ {}".format(1,6))
    if readline_stdout(client) != CALC_RESPONSE.format(1):
        print("17 error, response test")
        return
    writeline_stdin(client,"calculate: {} ^ {}".format(-20,3))
    if readline_stdout(client) != CALC_RESPONSE.format((-20)**3):
        print("18 error, response test")
        return
    writeline_stdin(client,"calculate: {} ^ {}".format(-20,2.3))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("19 error, response test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} ^ {} ".format(-20,2))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("20 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} ^ {} + 2".format(-20,2))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("21 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate: {} {}".format(-20,2))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("22 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"calculate:  {} + {}".format(-20,2))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("23 error, format test")
        return
    client.wait()
    print("passed calculate test")
    
def factor_test():
    client = new_logged_in_client()
    writeline_stdin(client,"factors: {}".format(19539))
    if readline_stdout(client) != FACTORS_RESPONSE.format(19539,"3, 13, 167"):
        print("1 error, response test")
        return
    writeline_stdin(client,"factors: {}".format(49))
    if readline_stdout(client) != FACTORS_RESPONSE.format(49,"7"):
        print("2 error, response test")
        return
    writeline_stdin(client,"factors: {}".format(5))
    if readline_stdout(client) != FACTORS_RESPONSE.format(5,"5"):
        print("3 error, response test")
        return
    writeline_stdin(client,"factors: {}".format(1))
    if readline_stdout(client) != INVALID_VALUE_FACTOR:
        print("4 error, invalid value test")
        return
    writeline_stdin(client,"factors: {}".format(-2))
    if readline_stdout(client) != INVALID_VALUE_FACTOR:
        print("5 error, invalid value test")
        return
    writeline_stdin(client,"factors: {}".format(2**31))
    if not readline_stdout(client).startswith("Out of range"):
        print("6 error, out of range test")
        return
    writeline_stdin(client,"factors: {}".format("t2"))
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("7 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"factors:  2")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("7 error, format test")
        return
    client.wait()
    print("passed factors test")

def max_test():
    client = new_logged_in_client()
    writeline_stdin(client,"max: (-10 -20 -30)")
    if readline_stdout(client) != MAX_RESPONSE.format(-10):
        print("1 error, response test")
        return
    writeline_stdin(client,"max: (-10 -20 293)")
    if readline_stdout(client) != MAX_RESPONSE.format(293):
        print("2 error, response test")
        return
    writeline_stdin(client,"max: (0)")
    if readline_stdout(client) != MAX_RESPONSE.format(0):
        print("3 error, response test")
        return
    writeline_stdin(client,"max: ()")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("4 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"max: ( )")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("5 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"max:  (1 2)")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("6 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"max: ( 1 2)")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("7 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"max: (1 2 )")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("8 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"max: (1  2)")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("9 error, format test")
        return
    client.wait()
    client = new_logged_in_client()
    writeline_stdin(client,"max: (1 2t)")
    if readline_stdout(client) != INVALID_COMMAND_FORMAT:
        print("10 error, format test")
        return
    client.wait()
    print("passed max test")
def login_test():
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    readline_stdout(client)
    writeline_stdin(client,"Use: test")
    readline_stdout(client)
    client.wait()
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    readline_stdout(client)
    writeline_stdin(client,"User: test")
    writeline_stdin(client,"User: test")
    readline_stdout(client)
    client.wait()
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    readline_stdout(client)
    writeline_stdin(client,"quit")
    client.wait()
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    readline_stdout(client)
    writeline_stdin(client,"User: s")
    writeline_stdin(client,"quit")
    client.wait()
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    readline_stdout(client)
    writeline_stdin(client,"User: s")
    writeline_stdin(client,"Password: 1234")
    if readline_stdout(client) != LOGIN_FAIL:
        print("error, login failed test")
    writeline_stdin(client,"User: vats")
    writeline_stdin(client,"Password: 1234")
    if readline_stdout(client) != LOGIN_FAIL:
        print("error, login failed test")
    writeline_stdin(client,"User: vats")
    writeline_stdin(client,"Password: 4321")
    if readline_stdout(client) != HI_MSG.format("vats"):
        print("error, login failed test")
    writeline_stdin(client,"User: vats")
    client.wait()
    print("passed login test")
def new_logged_in_client():
    client = subprocess.Popen(["./numbers_client.py","localhost","1442"],executable="./numbers_client.py",
                        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        encoding="utf-8")
    readline_stdout(client)
    writeline_stdin(client,"User: test")
    writeline_stdin(client,"Password: 123")
    readline_stdout(client)
    return client
def readline_stdout(process : subprocess.Popen) -> str:
    process.stdout.flush()
    line = process.stdout.readline()
    return line[:len(line)-1]

def writeline_stdin(process : subprocess.Popen, line : str) -> None:
    process.stdin.write(line + "\n")
    process.stdin.flush()
    
def max_str(nums : list[int]):
    s = "max: " + str(nums).replace(",","").replace("[","(").replace("]",")")
    return s

if __name__ == "__main__":
    main()