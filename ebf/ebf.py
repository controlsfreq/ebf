import os
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
    argparser.add_argument( "--prefix", default="",
                            help="The prefix to add to all output files." )
    argparser.add_argument( "--out_dir", default="",
                            help="The directory to write all output files to." )

    args = argparser.parse_args()

    with open(args.infile, 'r') as f:
        app = f.read()

    c = compiler.Compiler(app)
    c.compile()

    path = os.path.dirname(os.path.realpath(__file__))
    ebf_h_template = Template(filename=os.path.join(path, "templates", "ebf.h.mako"))
    main_c_template = Template(filename=os.path.join(path, "templates", "main.c.mako"))
    kwargs = c.config()

    with open(os.path.join( args.out_dir, args.prefix, "ebf.h"), 'w') as f:
        f.write(ebf_h_template.render(strict_undefined=True, **kwargs))

    with open(os.path.join( args.out_dir, args.prefix, "main.c"), 'w') as f:
        f.write(main_c_template.render(strict_undefined=True, application=c.application(), **kwargs))


if __name__ == "__main__":
    main()

