
import re
import sys
import argparse

class Ebf(object):

    def __init__(self, data_array_size=1024):
        self._stdin = sys.stdin
        self._stdout = sys.stdout
        self._instructions = []
        self._data_array = bytearray(b'\x00' * data_array_size)
        self._instruction_pointer = 0
        self._shadow_instruction_pointer = 0
        self._data_pointer = 0
        self._shadow_data_pointer = 0
        self._identifier_dict = dict()
        self._debug = 0

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
            instructions = re.sub( "{{.*?}}", '', value, flags=re.DOTALL ) # Remove block comments
            pattern = re.compile( "[\>\<\+\-\.\,\[\]\~\%\!]|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\:0[xX][a-fA-F0-9]+\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\:0[0-7]+\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\:[1-9][0-9]*\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\:0\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\$0[xX][a-fA-F0-9]+\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\$0[0-7]+\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\$\-?[1-9][0-9]*\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\$0\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\#0[xX][a-fA-F0-9]+\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\#0[0-7]+\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\#\-?[1-9][0-9]*\)|\([\>\<\+\-\.\,\[\]\&\|\^\\\/]\#0\)|\(\@.*\)|\(\*.*\)" )
            instructions = pattern.findall( instructions )
            for instr in instructions:
                if re.match( "\(\@(.*)\)", instr ) is not None:
                    match = re.match( "\(\@(.*)\)", instr )
                    self._identifier_dict[ match.group(1) ] = instructions.index( instr )
                    del instructions[ instructions.index( instr ) ]

            self._instructions = instructions
            if self._debug >= 0:
                print( "Instructions:\n{}".format( self._instructions ) )
                print( "Identifiers:\n{}".format( self._identifier_dict ) )
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
        self.__init__()

    def step(self):
        # run the current instruction and step the program
        if self._instruction_pointer >= len(self._instructions):
            return False

        if self._instruction_pointer < 0:
            raise ValueError( "Negative instruction pointer!" )

        current_instruction = self._instructions[self._instruction_pointer]

        if self._debug:
            print( "Instruction[{}]:  {}".format(self._instruction_pointer,current_instruction) )
            print( "Data Array:       {}".format([ str(x).zfill(3) for x in self._data_array[max(self._data_pointer-5,0):max(11,min(self._data_pointer+6,len(self._data_array)-1))] ]) )
            print( "Current Cell:     {}^{}".format( '    '+' '*7*min( 5, self._data_pointer ), str(self._data_pointer) ) )
            print( "Shadow Registers:" )
            print( "  Instruction:    {}".format(self._shadow_instruction_pointer) )
            print( "  Data:           {}".format(self._shadow_data_pointer) )
            if self._debug >= 2:
                empty = raw_input( "Press Return To Continue" )

        if current_instruction == '>':
            # Move data pointer right one
            self._data_pointer += 1
            if self._debug >= 1:
                if self._data_pointer >= len(self._data_array):
                    print( "Overran data array!" )
                    empty = raw_input( "Press enter to continue" )


        elif current_instruction == '<':
            # Move data pointer left one
            self._data_pointer -= 1
            if self._data_pointer < 0:
                self._data_pointer = len(self._data_array) - 1

        elif current_instruction == '+':
            # Increment current data value
            self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + 1) % 256

        elif current_instruction == '-':
            # Decrement current data value
            self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - 1) % 256

        elif current_instruction == '.':
            # Output the current data value to _stdout
            self._stdout.write( chr(self._data_array[self._data_pointer]) )

        elif current_instruction == ',':
            # Input a value from _stdin
            self._data_array[self._data_pointer] = ord(self._stdin.read( 1 ))

        elif current_instruction == '[':
            if self._data_array[self._data_pointer] == 0:
                bracket_count = 0
                position = self._instruction_pointer + 1
                while True:
                    if (bracket_count == 0) and (re.search( "\]", self._instructions[position]) is not None):
                        break
                    if re.search( "\[", self._instructions[position] ) is not None:
                        bracket_count += 1
                    if re.search( "\]", self._instructions[position] ) is not None:
                        bracket_count -= 1
                    if bracket_count < 0:
                        raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                    if position >= len(self._data_array) - 1:
                        raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                    position += 1
                self._instruction_pointer = position

        elif current_instruction == ']':
            if self._data_array[self._data_pointer] != 0:
                bracket_count = 0
                position = self._instruction_pointer - 1
                while True:
                    if (bracket_count == 0) and (re.search( "\[", self._instructions[position]) is not None):
                        break
                    if re.search( "\[", self._instructions[position] ) is not None:
                        bracket_count -= 1
                    if re.search( "\]", self._instructions[position] ) is not None:
                        bracket_count += 1
                    if bracket_count < 0:
                        raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                    if position < 0:
                        raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                    position -= 1
                self._instruction_pointer = position

        elif current_instruction == '~':
            self._data_array[self._data_pointer] = (~self._data_array[self._data_pointer]) & 0xFF

        elif current_instruction == '%':
            temp = self._data_pointer
            self._data_pointer = self._shadow_data_pointer
            self._shadow_data_pointer = temp

        elif current_instruction == '!':
            temp = self._instruction_pointer
            self._instruction_pointer = self._shadow_instruction_pointer
            self._shadow_instruction_pointer = temp

        elif re.match( "\((.)\:(.*)\)", current_instruction ) is not None:
            match = re.match( "\((.):(.*)\)", current_instruction )
            if match.group(1) == '>':
                self._shadow_data_pointer = self._data_pointer
                self._data_pointer = int(match.group(2),0) # todo: bounds check
            elif match.group(1) == '<':
                self._shadow_data_pointer = self._data_pointer
                self._data_pointer = int(match.group(2),0) # todo: bounds check
            elif match.group(1) == '+':
                self._data_array[int(match.group(2),0)] = (self._data_array[int(match.group(2),0)] + 1) % 256
            elif match.group(1) == '-':
                self._data_array[int(match.group(2),0)] = (self._data_array[int(match.group(2),0)] - 1) % 256
            elif match.group(1) == '.':
                self._data_array[int(match.group(2),0)] = self._data_array[self._data_pointer]
            elif match.group(1) == ',':
                self._data_array[self._data_pointer] = self._data_array[int(match.group(2),0)]
            elif match.group(1) == '[':
                if self._data_array[int(match.group(2),0)] == 0:
                    bracket_count = 0
                    position = self._instruction_pointer + 1
                    while True:
                        if (bracket_count == 0) and (re.search( "\]", self._instructions[position]) is not None):
                            break
                        if re.search( "\[", self._instructions[position] ) is not None:
                            bracket_count += 1
                        if re.search( "\]", self._instructions[position] ) is not None:
                            bracket_count -= 1
                        if bracket_count < 0:
                            raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                        if position >= len(self._data_array) - 1:
                            raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                        position += 1
                    self._instruction_pointer = position
            elif match.group(1) == ']':
                if self._data_array[int(match.group(2),0)] != 0:
                    bracket_count = 0
                    position = self._instruction_pointer - 1
                    while True:
                        if (bracket_count == 0) and (re.search( "\[", self._instructions[position]) is not None):
                            break
                        if re.search( "\[", self._instructions[position] ) is not None:
                            bracket_count -= 1
                        if re.search( "\]", self._instructions[position] ) is not None:
                            bracket_count += 1
                        if bracket_count < 0:
                            raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                        if position < 0:
                            raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                        position -= 1
                    self._instruction_pointer = position
            elif match.group(1) == '&':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & self._data_array[int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '|':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | self._data_array[int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '^':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ self._data_array[int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '/':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> self._data_array[int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '\\':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << self._data_array[int(match.group(2),0)]) & 0xFF
            else:
                raise SyntaxError("Unknown absolute addressed instruction: {}: {}".format(self._instruction_pointer,current_instruction))

        elif re.match( "\((.)\$(.*)\)", current_instruction ) is not None:
            match = re.match( "\((.)\$(.*)\)", current_instruction )
            if match.group(1) == '>':
                self._shadow_data_pointer = self._data_pointer
                self._data_pointer = (self._data_pointer + int(match.group(2),0)) % len(self._data_array)
            elif match.group(1) == '<':
                self._shadow_data_pointer = self._data_pointer
                self._data_pointer = (self._data_pointer - int(match.group(2),0)) % len(self._data_array)
            elif match.group(1) == '+':
                self._data_array[self._data_pointer + int(match.group(2),0)] = (self._data_array[self._data_pointer + int(match.group(2),0)] + 1) % 256
            elif match.group(1) == '-':
                self._data_array[self._data_pointer + int(match.group(2),0)] = (self._data_array[self._data_pointer + int(match.group(2),0)] - 1) % 256
            elif match.group(1) == '.':
                self._data_array[self._data_pointer + int(match.group(2),0)] = self._data_array[self._data_pointer]
            elif match.group(1) == ',':
                self._data_array[self._data_pointer] = self._data_array[self._data_pointer + int(match.group(2),0)]
            elif match.group(1) == '[':
                if self._data_array[self._data_pointer + int(match.group(2),0)] == 0:
                    bracket_count = 0
                    position = self._instruction_pointer + 1
                    while True:
                        if (bracket_count == 0) and (re.search( "\]", self._instructions[position]) is not None):
                            break
                        if re.search( "\[", self._instructions[position] ) is not None:
                            bracket_count += 1
                        if re.search( "\]", self._instructions[position] ) is not None:
                            bracket_count -= 1
                        if bracket_count < 0:
                            raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                        if position >= len(self._data_array) - 1:
                            raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                        position += 1
                    self._instruction_pointer = position
            elif match.group(1) == ']':
                if self._data_array[self._data_pointer + int(match.group(2),0)] != 0:
                    bracket_count = 0
                    position = self._instruction_pointer - 1
                    while True:
                        if (bracket_count == 0) and (re.search( "\[", self._instructions[position]) is not None):
                            break
                        if re.search( "\[", self._instructions[position] ) is not None:
                            bracket_count -= 1
                        if re.search( "\]", self._instructions[position] ) is not None:
                            bracket_count += 1
                        if bracket_count < 0:
                            raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                        if position < 0:
                            raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                        position -= 1
                    self._instruction_pointer = position
            elif match.group(1) == '&':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & self._data_array[self._data_pointer + int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '|':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | self._data_array[self._data_pointer + int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '^':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ self._data_array[self._data_pointer + int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '/':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> self._data_array[self._data_pointer + int(match.group(2),0)]) & 0xFF
            elif match.group(1) == '\\':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << self._data_array[self._data_pointer + int(match.group(2),0)]) & 0xFF
            else:
                raise SyntaxError("Unknown relative addressed instruction: {}: {}".format(self._instruction_pointer,current_instruction))

        elif re.match( "\((.)\#(.*)\)", current_instruction ) is not None:
            match = re.match( "\((.)#(.*)\)", current_instruction )
            if match.group(1) == '>':
                self._data_pointer = (self._data_pointer + int(match.group(2),0)) % len(self._data_array)
            elif match.group(1) == '<':
                self._data_pointer = (self._data_pointer - int(match.group(2),0)) % len(self._data_array)
            elif match.group(1) == '+':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + int(match.group(2),0)) % 256
            elif match.group(1) == '-':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - int(match.group(2),0)) % 256
            elif match.group(1) == '.':
                self._stdout.write( chr(int(match.group(2),0)) )
            elif match.group(1) == ',':
                self._data_array[self._data_pointer] = int(match.group(2),0)
            elif match.group(1) == '[':
                if int(match.group(2),0) == 0:
                    bracket_count = 0
                    position = self._instruction_pointer + 1
                    while True:
                        if (bracket_count == 0) and (re.search( "\]", self._instructions[position]) is not None):
                            break
                        if re.search( "\[", self._instructions[position] ) is not None:
                            bracket_count += 1
                        if re.search( "\]", self._instructions[position] ) is not None:
                            bracket_count -= 1
                        if bracket_count < 0:
                            raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                        if position >= len(self._data_array) - 1:
                            raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                        position += 1
                    self._instruction_pointer = position
            elif match.group(1) == ']':
                if int(match.group(2),0) != 0:
                    bracket_count = 0
                    position = self._instruction_pointer - 1
                    while True:
                        if (bracket_count == 0) and (re.search( "\[", self._instructions[position]) is not None):
                            break
                        if re.search( "\[", self._instructions[position] ) is not None:
                            bracket_count -= 1
                        if re.search( "\]", self._instructions[position] ) is not None:
                            bracket_count += 1
                        if bracket_count < 0:
                            raise SyntaxError("Unmatched opening bracket: {}".format(self._instruction_pointer))
                        if position < 0:
                            raise SyntaxError("Unmatched closing bracket: {}".format(self._instruction_pointer))
                        position -= 1
                    self._instruction_pointer = position
            elif match.group(1) == '&':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & int(match.group(2),0)) & 0xFF
            elif match.group(1) == '|':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | int(match.group(2),0)) & 0xFF
            elif match.group(1) == '^':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ int(match.group(2),0)) & 0xFF
            elif match.group(1) == '/':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> int(match.group(2),0)) & 0xFF
            elif match.group(1) == '\\':
                self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << int(match.group(2),0)) & 0xFF
            else:
                raise SyntaxError("Unknown absolute addressed instruction: {}: {}".format(self._instruction_pointer,current_instruction))

        elif re.match( "\(\@(.*)\)", current_instruction ) is not None:
            # todo: Move this to a preprocessing step so that identifiers may be defined after their calls
            match = re.match( "\(\@(.*)\)", current_instruction )
            self._identifier_dict[ match.group(1) ] = self._instruction_pointer

        elif re.match( "\(\*(.*)\)", current_instruction ) is not None:
            match = re.match( "\(\*(.*)\)", current_instruction )
            # todo: Catch KeyError in case of undefined identifier
            if self._debug >= 2:
                print( "Jumping from {} to {}.".format( self._instruction_pointer, self._identifier_dict[ match.group(1) ] ) )
            self._shadow_instruction_pointer = self._instruction_pointer
            self._instruction_pointer = self._identifier_dict[ match.group(1) ] - 1

        else:
            raise SyntaxError("Unknown instruction: {}: {}".format(self._instruction_pointer,current_instruction))

        self._instruction_pointer += 1
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
    argparser.add_argument( "-s", "--size", type=int,
                            help="The size of the data array (default: 1024)." )
    argparser.add_argument( "-d", "--debug", action='count',
                            help="Enable debugging output while running the program." )

    args = argparser.parse_args()

    if args.size is not None:
        ebf = Ebf( args.size )
    else:
        ebf = Ebf()

    if args.debug:
        ebf.debug = args.debug

    bf_file = args.bf

    if args.input is not None:
        in_file = args.input
    else:
        in_file = sys.stdin

    if args.output is not None:
        out_file = args.output
    else:
        out_file = sys.stdout

    ebf.stdin = in_file
    ebf.stdout = out_file
    ebf.instructions = bf_file.read()

    while ebf.step():
        pass

if __name__ == "__main__":
    main()
