from logParser import *
import timeit

if __name__ == "__main__":
    parse("log_3025085.log") # STANDARD 5 CP
    #print(timeit.timeit(f"{parse('log_3025085.log')}"))
    #parse("log_3025115.log") # COMBINED LOG
    #parse("log_3024266.log") # PAYLOAD 