
import sys
import argparse
from datetime import date
from mako.template import Template
import compiler

class Ebf(object):

    def __init__(self):
        pass

def main():
    argparser = argparse.ArgumentParser( description="A python implementation of the Embedded "
                                                     "Brainfuck compiler." )
    argparser.add_argument( "-v", "--verbose", action='count',
                            help="Enable verbose output while compiling the program." )
    argparser.add_argument( "infile",
                            help="A file containing Embedded Brainfuck instructions." )

    args = argparser.parse_args()

    with open(args.infile, 'r') as f:
        app = f.read()

    c = compiler.Compiler(app)
    ebf_c_template = Template(filename="templates/ebf.c.mako")
    ebf_h_template = Template(filename="templates/ebf.h.mako")
    main_c_template = Template(filename="templates/main.c.mako")

    with open("ebf.h", 'w') as f:
        f.write(ebf_h_template.render(date=date.today(), cell_type="uint8_t"))
    with open("ebf.c", 'w') as f:
        f.write(ebf_c_template.render(date=date.today()))
    with open("main.c", 'w') as f:
        f.write(main_c_template.render(brief="Main.", author="Liam Bucci", date=date.today(), copyright_blurb="Free", application=c.compile(), includes=None))


if __name__ == "__main__":
    main()

