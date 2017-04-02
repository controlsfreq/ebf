class Interpreter(object):

    def __init__(self, app, data_array_size=1024):
        self._app = app
        self._data_array_size = data_array_size
        self._data_array = bytearray(b'\x00' * data_array_size)
        self._instruction_pointer = 0
        self._shadow_instruction_pointer = 0
        self._data_pointer = 0
        self._shadow_data_pointer = 0

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
        self._data_array = bytearray(b'\x00' * self._data_array_size)
        self._instruction_pointer = 0
        self._shadow_instruction_pointer = 0
        self._data_pointer = 0
        self._shadow_data_pointer = 0

    def step(self):
        # run the current instruction and step the program
        if self._instruction_pointer >= len(self._app.instructions):
            return False

        if self._instruction_pointer < 0:
            raise ValueError( "Negative instruction pointer!" )

        current_instruction = self._app.instructions[self._instruction_pointer]

        if self._debug:
            print( "Instruction[{}]:  {}".format(self._instruction_pointer,current_instruction) )
            print( "Data Array:       {}".format([ str(x).zfill(3) for x in self._data_array[max(self._data_pointer-5,0):max(11,min(self._data_pointer+6,len(self._data_array)-1))] ]) )
            print( "Current Cell:     {}^{}".format( '    ' + ' '*7*min( 5, self._data_pointer ), str(self._data_pointer) ) )
            print( "Shadow Registers:" )
            print( "  Instruction:    {}".format(self._shadow_instruction_pointer) )
            print( "  Data:           {}".format(self._shadow_data_pointer) )
            if self._debug >= 2:
                empty = raw_input( "Press Return To Continue" )

        if current_instruction == '>':
            # Move data pointer right one
            self._data_pointer = (self._data_pointer + 1) % len(self._data_array)
            if self._debug >= 1:
                if self._data_pointer == 0:
                    print( "Overran data array!" )
                    empty = raw_input( "Press enter to continue" )


        elif current_instruction == '<':
            # Move data pointer left one
            self._data_pointer = (self._data_pointer - 1) % len(self._data_array)
            if self._debug >= 1:
                if self._data_pointer == (len(self._data_array) - 1):
                    print( "Underran data array!" )
                    empty = raw_input( "Press enter to continue" )

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
                self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )

        elif current_instruction == ']':
            if self._data_array[self._data_pointer] != 0:
                self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )

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

        elif re.match( "\(([\>\<\+\-\.\,\[\]\&\|\^\\\/])([\@\#]\:?\*?)(.*)\)", current_instruction ) is not None:
            match = re.match( "\(([\>\<\+\-\.\,\[\]\&\|\^\\\/])([\@\#]\:?\*?)(.*)\)", current_instruction )

            instruction = match.group(1)
            modifiers = match.group(2)
            if match.group(3) == '%':
                value = self._shadow_data_pointer
            else:
                value = int(match.group(3),0)

            if instruction == '>':
                if modifiers == '@':
                    self._data_pointer = value # todo: bounds check
                elif modifiers == '@*':
                    self._data_pointer = self._data_array[ value ]
                elif modifiers == '@:':
                    self._data_pointer += value
                elif modifiers == '@:*':
                    self._data_pointer += self._data_array[ value ]
                elif modifiers == '#':
                    self._data_pointer = value # todo: bounds check
                elif modifiers == '#*':
                    self._data_pointer = self._data_array[ value ]
                elif modifiers == '#:':
                    self._data_pointer += value
                elif modifiers == '#:*':
                    self._data_pointer += self._data_array[ value ]
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '<':
                if modifiers == '@':
                    self._data_pointer = value # todo: bounds check
                elif modifiers == '@*':
                    self._data_pointer = self._data_array[ value ]
                elif modifiers == '@:':
                    self._data_pointer -= value
                elif modifiers == '@:*':
                    self._data_pointer -= self._data_array[ value ]
                elif modifiers == '#':
                    self._data_pointer = value # todo: bounds check
                elif modifiers == '#*':
                    self._data_pointer = self._data_array[ value ]
                elif modifiers == '#:':
                    self._data_pointer -= value
                elif modifiers == '#:*':
                    self._data_pointer -= self._data_array[ value ]
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '+':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] + 1) % 256
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] + 1) % 256
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] + 1) % 256
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] + 1) % 256
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + value) % 256
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + self._data_array[value]) % 256
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + self._data_array[self._data_pointer + value]) % 256
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] + self._data_array[self._data_array[self._data_pointer + value]]) % 256
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '-':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] - 1) % 256
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] - 1) % 256
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] - 1) % 256
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] - 1) % 256
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - value) % 256
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - self._data_array[value]) % 256
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - self._data_array[self._data_pointer + value]) % 256
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] - self._data_array[self._data_array[self._data_pointer + value]]) % 256
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '.':
                if modifiers == '@':
                    self._data_array[value] = self._data_array[self._data_pointer]
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = self._data_array[self._data_pointer]
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = self._data_array[self._data_pointer]
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = self._data_array[self._data_pointer]
                elif modifiers == '#':
                    self._stdout.write( chr(value) )
                elif modifiers == '#*':
                    self._stdout.write( chr(self._data_array[value]) )
                elif modifiers == '#:':
                    self._stdout.write( chr(self._data_array[self._data_pointer + value]) )
                elif modifiers == '#:*':
                    self._stdout.write( chr(self._data_array[self._data_array[self._data_pointer + value]]) )
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == ',':
                if modifiers == '@':
                    self._data_array[value] = self._stdin.read(1)
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = self._stdin.read(1)
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = self._stdin.read(1)
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = self._stdin.read(1)
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = value
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = self._data_array[value]
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = self._data_array[self._data_pointer + value]
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = self._data_array[self._data_array[self._data_pointer + value]]
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '[':
                if modifiers == '@':
                    if self._data_array[value] == 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '@*':
                    if self._data_array[self._data_array[value]] == 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '@:':
                    if self._data_array[self._data_pointer + value] == 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '@:*':
                    if self._data_array[self._data_array[self._data_pointer + value]] == 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#':
                    if self._data_array[self._data_pointer] == value:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#*':
                    if self._data_array[self._data_pointer] == self._data_array[value]:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#:':
                    if self._data_array[self._data_pointer] == self._data_array[self._data_pointer + value]:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#:*':
                    if self._data_array[self._data_pointer] == self._data_array[self._data_array[self._data_pointer + value]]:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == ']':
                if modifiers == '@':
                    if self._data_array[value] != 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '@*':
                    if self._data_array[self._data_array[value]] != 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '@:':
                    if self._data_array[self._data_pointer + value] != 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '@:*':
                    if self._data_array[self._data_array[self._data_pointer + value]] != 0:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#':
                    if self._data_array[self._data_pointer] != value:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#*':
                    if self._data_array[self._data_pointer] != self._data_array[value]:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#:':
                    if self._data_array[self._data_pointer] != self._data_array[self._data_pointer + value]:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                elif modifiers == '#:*':
                    if self._data_array[self._data_pointer] != self._data_array[self._data_array[self._data_pointer + value]]:
                        self._instruction_pointer = self.find_matching_bracket( self._instruction_pointer )
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '&':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] & self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] & self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] & self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] & self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & value) & 0xFF
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & self._data_array[value]) & 0xFF
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & self._data_array[self._data_pointer + value]) & 0xFF
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] & self._data_array[self._data_array[self._data_pointer + value]]) & 0xFF
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '|':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] | self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] | self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] | self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] | self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | value) & 0xFF
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | self._data_array[value]) & 0xFF
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | self._data_array[self._data_pointer + value]) & 0xFF
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] | self._data_array[self._data_array[self._data_pointer + value]]) & 0xFF
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '^':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] ^ self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] ^ self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] ^ self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] ^ self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ value) & 0xFF
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ self._data_array[value]) & 0xFF
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ self._data_array[self._data_pointer + value]) & 0xFF
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] ^ self._data_array[self._data_array[self._data_pointer + value]]) & 0xFF
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '/':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] >> self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] >> self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] >> self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] >> self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> value) & 0xFF
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> self._data_array[value]) & 0xFF
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> self._data_array[self._data_pointer + value]) & 0xFF
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] >> self._data_array[self._data_array[self._data_pointer + value]]) & 0xFF
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))

            elif instruction == '\\':
                if modifiers == '@':
                    self._data_array[value] = (self._data_array[value] << self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@*':
                    self._data_array[self._data_array[value]] = (self._data_array[self._data_array[value]] << self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:':
                    self._data_array[self._data_pointer + value] = (self._data_array[self._data_pointer + value] << self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '@:*':
                    self._data_array[self._data_array[self._data_pointer + value]] = (self._data_array[self._data_array[self._data_pointer + value]] << self._data_array[self._data_pointer]) & 0xFF
                elif modifiers == '#':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << value) & 0xFF
                elif modifiers == '#*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << self._data_array[value]) & 0xFF
                elif modifiers == '#:':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << self._data_array[self._data_pointer + value]) & 0xFF
                elif modifiers == '#:*':
                    self._data_array[self._data_pointer] = (self._data_array[self._data_pointer] << self._data_array[self._data_array[self._data_pointer + value]]) & 0xFF
                else:
                    raise SyntaxError("Unexpected modifiers in {}: {}".format(current_instruction, self._instruction_pointer))
            else:
                raise SyntaxError("Unknown absolute addressed instruction: {}: {}".format(self._instruction_pointer,current_instruction))

        elif re.match( "\(\!(\:?)([a-zA-Z][a-zA-Z0-9]*)\)", current_instruction ) is not None:
            match = re.match( "\(\!(\:?)([a-zA-Z][a-zA-Z0-9]*)\)", current_instruction )
            identifier = match.group(2)
            if match.group(1) == ':':
                self._shadow_instruction_pointer = self._instruction_pointer
            # todo: Catch KeyError in case of undefined identifier
            self._instruction_pointer = self._identifier_dict[ identifier ] - 1 # back one to account for later step of instruction pointer
            if self._debug >= 2:
                print( "Jumping from {} to {}.".format( self._instruction_pointer, self._identifier_dict[ identifier ] ) )

        else:
            raise SyntaxError("Unknown instruction: {}: {}".format(self._instruction_pointer,current_instruction))

        self._instruction_pointer += 1
        return True