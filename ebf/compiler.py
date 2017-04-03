import re
import datetime
import yaml

class SyntaxError(Exception):
    def __init__(self, message):
        self.message = message

class Compiler(object):

    def __init__(self, ebf):
        self._working = ebf
        self._config = {"cell_width": 16,
                        "includes": None,
                        "init_hook": False,
                        "cleanup_hook": False}
        self._application = str()

    def config(self):
        return self._config

    def application(self):
        return self._application

    def _preprocess(self):
        # Read configuration blocks
        config_match = re.findall( "^\#\%\((.*?)\)", self._working, flags=re.DOTALL+re.MULTILINE )

        # Only one config block per application allowed
        if len(config_match) > 1:
            raise SyntaxError("Multiple config blocks.")

        self._config = yaml.load(config_match[0])

        # Remove configuration blocks
        self._working = re.sub( "^\#\%\(.*?\)", '', self._working, flags=re.DOTALL+re.MULTILINE )
        # Remove comment lines
        self._working = re.sub( "^\#.*", '', self._working, flags=re.MULTILINE )
        # Condense to a single line
        self._working = self._working.replace('\n', '').replace('\r', '')

    def compile(self):
        self._preprocess()
        pattern = re.compile("([\_\>\<\+\-\[\]\.\,\|\&\^\~\\\/\@\!])([\:\#])?(0[xX][a-fA-F0-9]+|\-?[0-9]+)?(\(?\w+\)?)?")
        instructions = pattern.findall( self._working )

        for i in instructions:
            if i[0] == '_':
                if i[1] == '' and i[2] == '':
                    self._application += "__asm__ volatile (\"nop\");\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '>':
                if i[1] == '' and i[2] == '':
                    self._application += "DP += 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "DP += *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "DP += *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "DP += " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '<':
                if i[1] == '' and i[2] == '':
                    self._application += "DP -= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "DP -= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "DP -= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "DP -= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '+':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP += 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP += *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP += *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP += " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '-':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP -= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP -= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP -= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP -= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '[':
                if i[1] == '' and i[2] == '':
                    self._application += "while(*DP!=0) {\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "while(*((cell_t*)" + str(i[2]) + ")!=0) {\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "while(*(DP + " + str(i[2]) + ")!=0) {\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "while(" + str(i[2]) + "!=0) {\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == ']':
                if i[1] == '' and i[2] == '':
                    self._application += "}\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '.':
                if i[1] == '' and i[2] == '':
                    self._application += "putchar(*DP);\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "putchar(*((cell_t*)" + str(i[2]) + "));\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "putchar(*(DP + " + str(i[2]) + "));\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "putchar(" + str(i[2]) + ");\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == ',':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP=getchar();\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*((cell_t*)" + str(i[2]) + ")=getchar();\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*(DP + " + str(i[2]) + ")=getchar();\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP=" + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '&':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP &= *(DP+1);\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP &= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP &= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP &= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '|':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP |= *(DP+1);\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP |= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP |= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP |= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '^':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP ^= *(DP+1);\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP ^= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP ^= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP ^= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '~':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP = ~*DP;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP = ~*((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP = ~*(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP = ~" + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '\\':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP <<= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP <<= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP <<= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP <<= " + str(i[2]) + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            elif i[0] == '/':
                if i[1] == '' and i[2] == '':
                    self._application += "*DP >>= 1;\n"
                elif i[1] == '' and i[2] != '':
                    self._application += "*DP >>= *((cell_t*)" + str(i[2]) + ");\n"
                elif i[1] == ':' and i[2] != '':
                    self._application += "*DP >>= *(DP + " + str(i[2]) + ");\n"
                elif i[1] == '#' and i[2] != '':
                    self._application += "*DP >>= " + str(i[2]) + ";\n"
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
                    self._application += "goto " + i[3] + ";\n"
                else:
                    print(i)
                    raise SyntaxError("Syntax error")
            else:
                print(i)
                raise SyntaxError("Unknown instruction")

        return self._application
