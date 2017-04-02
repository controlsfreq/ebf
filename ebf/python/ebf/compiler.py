import re
import sys
import argparse

class SyntaxError(Exception):
    def __init__(self, message):
        self.message = message

class Compiler(object):

    DATACELL_SIZE_8 = 0
    DATACELL_SIZE_16 = 1
    DATACELL_SIZE_32 = 2
    DATACELL_SIZE_64 = 3

    ENDIANNESS_HOST = 0
    ENDIANNESS_LITTLE = 1
    ENDIANNESS_BIG = 2

    def __init__(self, ebf):
        #self._datacell_size = DATACELL_SIZE_8
        #self._endianness = ENDIANNESS_HOST
        self._working = ebf
        self._config = str()
        self._output = str()

    def _preprocess(self):
        # Read configuration blocks
        self._config = re.findall( "^\#\%\((.*?)\)", self._working, flags=re.DOTALL+re.MULTILINE )

        # Only one config block per application allowed
        if len(self._config) > 1:
            raise SyntaxError("Multiple config blocks.")

        # Remove configuration blocks
        self._working = re.sub( "^\#\%\(.*\)", '', self._working, flags=re.DOTALL+re.MULTILINE )
        # Remove comment lines
        self._working = re.sub( "^\#.*", '', self._working, flags=re.MULTILINE )
        # Condense to a single line
        self._working = self._working.replace('\n', '').replace('\r', '')

    def compile(self):
        self._preprocess()
        pattern = re.compile("([\_\>\<\+\-\[\]\.\,\|\&\^\~\\\/\@\!])([\:\#])?(0[xX][a-fA-F0-9]+|\-?[0-9]+)?(\(?\w+\)?)?")
        instructions = pattern.findall( self._working )
        print(instructions)

        for i in instructions:
            if i[0] == '_':
                if i[1] == '' and i[2] == '':
                    self._output += "__asm__ volatile (\"nop\");\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '>':
                if i[1] == '' and i[2] == '':
                    self._output += "DP += 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "DP += *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "DP += *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "DP += " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '<':
                if i[1] == '' and i[2] == '':
                    self._output += "DP -= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "DP -= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "DP -= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "DP -= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '+':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP += 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP += *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP += *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP += " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '-':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP -= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP -= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP -= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP -= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '[':
                if i[1] == '' and i[2] == '':
                    self._output += "while(*DP!=0) {\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "while(*(" + str(i[2]) + ")!=0) {\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "while(*(DP + " + str(i[2]) + ")!=0) {\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "while(" + str(i[2]) + "!=0) {\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == ']':
                if i[1] == '' and i[2] == '':
                    self._output += "}\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '.':
                if i[1] == '' and i[2] == '':
                    self._output += "putchar(*DP);\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "putchar(*(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "putchar(*(DP + " + str(i[2]) + "));\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "putchar(" + str(i[2]) + ");\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == ',':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP=getchar();\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*(" + str(i[2]) + ")=getchar();\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*(DP + " + str(i[2]) + ")=getchar();\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP=" + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '&':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP &= *(DP+1);\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP &= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP &= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP &= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '|':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP |= *(DP+1);\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP |= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP |= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP |= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '^':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP ^= *(DP+1);\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP ^= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP ^= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP ^= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '~':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP = ~*DP;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP = ~*(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP = ~*(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP = ~" + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '\\':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP <<= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP <<= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP <<= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP <<= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '/':
                if i[1] == '' and i[2] == '':
                    self._output += "*DP >>= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._output += "*DP >>= *(" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._output += "*DP >>= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._output += "*DP >>= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '@':
                if i[3] != '':
                    print(i[3] + ":")
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '!':
                if i[3] != '':
                    self._output += "goto " + i[3] + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            else:
                print(i)
                raise SyntaxError("Unknown instruction")

        return self._output


def main():
    argparser = argparse.ArgumentParser( description="A python implementation of the Embedded "
                                                     "Brainfuck compiler." )
    argparser.add_argument( "-v", "--verbose", action='count',
                            help="Enable verbose output while compiling the program." )
    argparser.add_argument( "infile",
                            help="A file containing Embedded Brainfuck instructions." )
    argparser.add_argument( "outfile",
                            help="A file to which the compiled program will be written." )


    args = argparser.parse_args()

    with open(args.infile, 'r') as f:
        app = f.read()

    c = Compiler(app)

    print(c.compile())


if __name__ == "__main__":
    main()
