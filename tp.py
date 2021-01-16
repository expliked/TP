import sys
import re
import os.path
from msvcrt import getch

def pause():
    print("Press any key to continue . . .")
    getch()

commands = [
    "USE",
    "NEW",
    "OLD",
    "GET",
    "REM",
    "YES",
    "NUL",
    "END",
    "DIS",
    "ASK"
]

commands_actual = [
    command + "_TP" for command in commands
]

class IncorrectFileExtension(Exception):
    pass

class RollOverflowError(Exception):
    pass

class NegativeRollError(Exception):
    pass

class InvalidSyntaxError(Exception):
    pass

class _command_parser:
    def __init__(self, commands):
        self.commands = commands
        self.command = self.commands[0]
        self.position = 0
        self.scanning_commands = True
        self.number_of_number_statements = 0
        
        # tp rolls
        self.rolls = [255]
        self.roll_idx = 0

    def get_statement(self):
        return f"statement #{(self.position + 1) - self.number_of_number_statements}"
    
    def advance(self):
        self.position += 1

        if (self.position == len(self.commands)):
            self.scanning_commands = False
            return

        else:
            self.command = self.commands[self.position]

    def parse_current_command(self):
            if (self.command not in commands_actual):
                if (self.command.isdigit()):
                    self.number_of_number_statements += 1
                    pass
                
                raise(InvalidSyntaxError(f"Invalid syntax at statement #{self.get_statement()}. '{self.command.replace('_', ' ')}'."))

            if (self.command == "USE_TP"):
                if (self.rolls[self.roll_idx] == 0):
                    raise(NoMoreTPError("No more TP is on the current roll. Statement #{(self.position + 1) - self.number_of_number_statements}. '{self.command.replace('_', ' ')}'."))
                
                self.rolls[self.roll_idx] -= 1

            if (self.command == "NEW_TP"):
                if (self.roll_idx == len(self.rolls)):
                    raise(RollOverflowError(f"No more rolls exist in the pile. Statement #{(self.position + 1) - self.number_of_number_statements}. '{self.command.replace('_', ' ')}'."))

                self.roll_idx += 1

            if (self.command == "OLD_TP"):
                if (self.roll_idx == 0):
                    raise(NegativeRollError(f"Not enough rolls in pile to go back. Statement #{(self.position + 1) - self.number_of_number_statements}. '{self.command.replace('_', ' ')}'."))

                self.roll_idx -= 1

            if (self.command == "GET_TP"):
                self.rolls.append(255)

            if (self.command == "REM_TP"):
                if (len(self.rolls) == 0):
                    raise(NegativeRollError(f"Not enough rolls in pile to remove. Statement #{(self.position + 1) - self.number_of_number_statements}. '{self.command.replace('_', ' ')}'."))

                self.rolls.pop()

            if (self.command == "YES_TP"):
                if (self.rolls[self.roll_idx] > 0):
                    while (self.scanning_commands):
                        self.advance()

                        if (self.command == "END_TP"):
                            break

                        self.parse_current_command()

                else:
                    while (self.scanning_commands):
                        self.advance()

                        if (self.command == "END_TP"):
                            break
                        
            if (self.command == "NUL_TP"):
                if (self.rolls[self.roll_idx] == 0):
                    while (self.scanning_commands):
                        self.advance()

                        if (self.command == "END_TP"):
                            break

                        self.parse_current_command()
                        
                else:
                    while (self.scanning_commands):
                        self.advance()

                        if (self.command == "END_TP"):
                            break
                        
            if (self.command == "DIS_TP"):
                print(chr(self.rolls[self.roll_idx]), end="")

            if (self.command == "ASK_TP"):
                self.advance()

                self.number_of_number_statements += 1
                if (self.command.isdigit()):
                    self.rolls[self.roll_idx] -= int(self.command)

                else:
                    self.rolls[self.roll_idx] -= ord(self.command)
                
    def parse(self):
        while (self.scanning_commands):
            self.parse_current_command()
            self.advance()


def parse(code):
    code = re.sub(re.compile("\#.*?\n"), "", code + "\n") # remove comments
    code = code.upper()
    
    for command in commands:
        code = code.replace(f"{command} ", f"{command}_")

    # Splitting code into commands to parse later
    code = list(filter(
        None, code         \
        .replace("\n", " ") \
        .replace("\t", "")   \
        .replace(", ", " ")   \
        .replace(",", "")      \
        .split(" ")
    ))
    
    command_parser = _command_parser(code)
    command_parser.parse()

def start_interpreter():
    code = ""

    print("TP Interpreter\nEnter your commands, and once finished, enter 'RUN'")
    while (True):
        user_input = input()

        if (user_input.upper() == "RUN"):
            parse(code)
            print("\n")
            
        else:
            code += user_input + "\n"
            
def main(argv):
    if (len(argv) == 1):
        start_interpreter()

    else:
        filename = str(argv[1])
        ext = os.path.splitext(filename)[1]
        
        if (ext != ".tp"):
            raise(IncorrectFileExtension(f"Incorrect file extension {ext}"))
        
        with open(filename, "r") as file:
            file_contents = file.read()

        parse(file_contents)

if (__name__ == "__main__"):
    try:
        main(sys.argv)
    except Exception as error:
        print(error)
    pause()
