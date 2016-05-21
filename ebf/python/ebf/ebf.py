
import re
import sys
import argparse

class Ebf():

    def __init__(self):
        self._stdin = sys.stdin
        self._stdout = sys.stdout
        self._program_counter = 0
        self._instructions = []
        self._data_pointer = 0
        self._data_array = bytearray(b'\x00' * 1024)
        self._address_register = 0
        self._address_register_mode = False
        self._data_stack = []
        self._instruction_stack = []
        self._debug = False

    def stdin():
        doc = "The stdin property."
        def fget(self):
            return self._stdin
        def fset(self, value):
            self._stdin = value
        def fdel(self):
            del self._stdin
        return locals()
    stdin = property(**stdin())

    def stdout():
        doc = "The stdout property."
        def fget(self):
            return self._stdout
        def fset(self, value):
            self._stdout = value
        def fdel(self):
            del self._stdout
        return locals()
    stdout = property(**stdout())

    def instructions():
        doc = "The instructions property."
        def fget(self):
            return self._instructions
        def fset(self, value):
            self._instructions = [char for instr in re.findall( "[><+\-.,\[\]\|\(\)]|#0[xX][a-fA-F0-9]+|#0[0-7]+|#[1-9][0-9]*|#0", value ) for char in instr]
        def fdel(self):
            del self._instructions
        return locals()
    instructions = property(**instructions())

    def debug():
        doc = "The debug property."
        def fget(self):
            return self._debug
        def fset(self, value):
            self._debug = value
        def fdel(self):
            del self._debug
        return locals()
    debug = property(**debug())

    def reset(self):
        # reset the program
        self._program_counter = 0
        self._data_pointer = 0
        self._data_array = bytearray()
        self._address_register = 0

    def step(self):
        # run the current instruction and step the program
        if self._program_counter >= len(self._instructions):
            return False

        if self._program_counter < 0:
            raise ValueError( "Negative program counter!" )

        current_instruction = self._instructions[self._program_counter]

        if self._debug:
            print( "Instruction[{}]: {}".format(self._program_counter,current_instruction) )
            print( "Data Pointer:    {}".format(self._data_pointer) )
            print( "Data Value:      {}".format(self._data_array[self._data_pointer]) )
            input()

        if self._address_register_mode == False:
            # Address register is inactive
            if current_instruction == '>':
                self._data_pointer += 1
                if self._data_pointer >= len(self._data_array):
                    self._data_array += 0

            elif current_instruction == '<':
                self._data_pointer = self._data_pointer - 1 if self._data_pointer > 0 else 0

            elif current_instruction == '+':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + 1) % 256

            elif current_instruction == '-':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - 1) % 256

            elif current_instruction == '.':
                self._stdout.write( chr(self._data_array[self._data_pointer]) )

            elif current_instruction == ',':
                self._data_array[self._data_pointer] = ord(self._stdin.read( 1 ))

            elif current_instruction == '[':
                if self._data_array[self._data_pointer] == 0:
                    bracket_count = 0
                    position = self._program_counter + 1
                    while (bracket_count != 0) or (self._instructions[position] != ']'):
                        if self._instructions[position] == '[':
                            bracket_count += 1
                        if self._instructions[position] == ']':
                            bracket_count -= 1
                        position += 1
                    self._program_counter = position

            elif current_instruction == ']':
                if self._data_array[self._data_pointer] != 0:
                    bracket_count = 0
                    position = self._program_counter - 1
                    while (bracket_count != 0) or (self._instructions[position] != '['):
                        if self._instructions[position] == ']':
                            bracket_count += 1
                        if self._instructions[position] == '[':
                            bracket_count -= 1
                        position -= 1
                    self._program_counter = position

            elif current_instruction == '|':
                self._address_register_mode = True

            elif current_instruction == '(':
                self._data_stack.append(self._data_pointer)
                self._data_pointer = self._address_register

            elif current_instruction == ')':
                self._data_pointer = self._data_stack.pop()

            elif current_instruction == '#':
                lit_value = ""
                position = self._program_counter + 1
                while re.findall( "[0-9]|[xX]", self._instructions[position] ):
                    lit_value += re.findall( "[0-9]|[xX]", self._instructions[position] )[0]
                    position += 1

                if re.findall( "\A[1-9][0-9]*", lit_value ):
                    self._data_array[self._data_pointer] = int(lit_value)
                elif re.findall( "\A0[xX][0-9]+", lit_value ):
                    self._data_array[self._data_pointer] = int(lit_value,16)
                elif re.findall( "\A0[0-7]*", lit_value ):
                    self._data_array[self._data_pointer] = int(lit_value,8)
                else:
                    print( "Unknown literal: {}".format(lit_value) )
                self._program_counter = position - 1
                print( lit_value )
                print( self._data_array[self._data_pointer] )

            else:
                # handle unknown instruction
                print( "Unknown instruction: {}".format(current_instruction) )

        else:
            # Address register is active
            if current_instruction == '>':
                self._data_pointer += 1
                if self._data_pointer >= len(self._data_array):
                    self._data_array += 0

            elif current_instruction == '<':
                self._data_pointer = self._data_pointer - 1 if self._data_pointer > 0 else 0

            elif current_instruction == '+':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - 1) % 256

            elif current_instruction == '-':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + 1) % 256

            elif current_instruction == '.':
                self._stdout.write( self._data_array[self._data_pointer] )

            elif current_instruction == ',':
                self._data_array[self._data_pointer] = self._stdin.read( 1 )

            elif current_instruction == '[':
                if self._data_array[self._data_pointer] == 0:
                    bracket_count = 0
                    position = self._program_counter + 1
                    while (bracket_count != 0) and (self._instructions[position] != ']'):
                        if self._instructions[position] == '[':
                            bracket_count += 1
                        if self._instructions[position] == ']':
                            bracket_count = bracket_count - 1
                        position += 1
                    self._program_counter = position

            elif current_instruction == ']':
                pass

            elif current_instruction == '|':
                pass

            elif current_instruction == '(':
                pass

            elif current_instruction == ')':
                pass

            elif current_instruction == '#':
                pass

            else:
                # handle unknown instruction
                pass

        self._program_counter += 1

        return True


def main():
    argparser = argparse.ArgumentParser( description="A python implementation of the Embedded "
                                                     "Brainfuck interpreter." )
    argparser.add_argument( "bf", type=argparse.FileType('r'),
                            help="A file containing Embedded Brainfuck instructions." )
    argparser.add_argument( "--input", type=argparse.FileType('r'),
                            help="A file containing the characters to use as stdin." )
    argparser.add_argument( "--output", type=argparse.FileType('w'),
                            help="A file to which all stdout characters will be written." )
    argparser.add_argument( "-d", "--debug", action='store_true', default=False,
                            help="Enable debugging output while running the program." )

    args = argparser.parse_args()

    bf_file = args.bf

    if args.input is not None:
        in_file = args.input
    else:
        in_file = sys.stdin

    if args.output is not None:
        out_file = args.output
    else:
        out_file = sys.stdout

    ebf = Ebf()
    ebf.stdin = in_file
    ebf.stdout = out_file
    ebf.instructions = bf_file.read()

    if args.debug:
        ebf.debug = True

    while ebf.step():
        pass

if __name__ == "__main__":
    main()