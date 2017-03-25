
import re
import sys
import argparse

class Ebf(object):

    def __init__(self):
        self._COMMENT_PATTERN = "\{\{.*?\}\}"
        self._IDENTIFIER_PATTERN = "\(\@([a-zA-Z][a-zA-Z0-9]*)\)"
        self._PATTERNS_NO_GROUPS = [ # Standard instruction pattern
                                     "[\>\<\+\-\.\,\[\]\~\%\!]",
                                     # All > patterns
                                     "\(\>\@0[xX][a-fA-F0-9]+\)|\(\>\@\-?[0-9]+\)",
                                     "\(\>\@\*0[xX][a-fA-F0-9]+\)|\(\>\@\*\-?[0-9]+\)",
                                     "\(\>\@\:0[xX][a-fA-F0-9]+\)|\(\>\@\:\-?[0-9]+\)",
                                     "\(\>\@\:\*0[xX][a-fA-F0-9]+\)|\(\>\@\:\*\-?[0-9]+\)",
                                     "\(\>\#0[xX][a-fA-F0-9]+\)|\(\>\#\-?[0-9]+\)",
                                     "\(\>\#\*0[xX][a-fA-F0-9]+\)|\(\>\#\*\-?[0-9]+\)",
                                     "\(\>\#\:0[xX][a-fA-F0-9]+\)|\(\>\#\:\-?[0-9]+\)",
                                     "\(\>\#\:\*0[xX][a-fA-F0-9]+\)|\(\>\#\:\*\-?[0-9]+\)",
                                     # All < patterns
                                     "\(\<\@0[xX][a-fA-F0-9]+\)|\(\<\@\-?[0-9]+\)",
                                     "\(\<\@\*0[xX][a-fA-F0-9]+\)|\(\<\@\*\-?[0-9]+\)",
                                     "\(\<\@\:0[xX][a-fA-F0-9]+\)|\(\<\@\:\-?[0-9]+\)",
                                     "\(\<\@\:\*0[xX][a-fA-F0-9]+\)|\(\<\@\:\*\-?[0-9]+\)",
                                     "\(\<\#0[xX][a-fA-F0-9]+\)|\(\<\#\-?[0-9]+\)",
                                     "\(\<\#\*0[xX][a-fA-F0-9]+\)|\(\<\#\*\-?[0-9]+\)",
                                     "\(\<\#\:0[xX][a-fA-F0-9]+\)|\(\<\#\:\-?[0-9]+\)",
                                     "\(\<\#\:\*0[xX][a-fA-F0-9]+\)|\(\<\#\:\*\-?[0-9]+\)",
                                     # All + patterns
                                     "\(\+\@0[xX][a-fA-F0-9]+\)|\(\+\@\-?[0-9]+\)",
                                     "\(\+\@\*0[xX][a-fA-F0-9]+\)|\(\+\@\*\-?[0-9]+\)",
                                     "\(\+\@\:0[xX][a-fA-F0-9]+\)|\(\+\@\:\-?[0-9]+\)",
                                     "\(\+\@\:\*0[xX][a-fA-F0-9]+\)|\(\+\@\:\*\-?[0-9]+\)",
                                     "\(\+\#0[xX][a-fA-F0-9]+\)|\(\+\#\-?[0-9]+\)",
                                     "\(\+\#\*0[xX][a-fA-F0-9]+\)|\(\+\#\*\-?[0-9]+\)",
                                     "\(\+\#\:0[xX][a-fA-F0-9]+\)|\(\+\#\:\-?[0-9]+\)",
                                     "\(\+\#\:\*0[xX][a-fA-F0-9]+\)|\(\+\#\:\*\-?[0-9]+\)",
                                     # All - patterns
                                     "\(\-\@0[xX][a-fA-F0-9]+\)|\(\-\@\-?[0-9]+\)",
                                     "\(\-\@\*0[xX][a-fA-F0-9]+\)|\(\-\@\*\-?[0-9]+\)",
                                     "\(\-\@\:0[xX][a-fA-F0-9]+\)|\(\-\@\:\-?[0-9]+\)",
                                     "\(\-\@\:\*0[xX][a-fA-F0-9]+\)|\(\-\@\:\*\-?[0-9]+\)",
                                     "\(\-\#0[xX][a-fA-F0-9]+\)|\(\-\#\-?[0-9]+\)",
                                     "\(\-\#\*0[xX][a-fA-F0-9]+\)|\(\-\#\*\-?[0-9]+\)",
                                     "\(\-\#\:0[xX][a-fA-F0-9]+\)|\(\-\#\:\-?[0-9]+\)",
                                     "\(\-\#\:\*0[xX][a-fA-F0-9]+\)|\(\-\#\:\*\-?[0-9]+\)",
                                     # All . patterns
                                     "\(\.\@0[xX][a-fA-F0-9]+\)|\(\.\@\-?[0-9]+\)",
                                     "\(\.\@\*0[xX][a-fA-F0-9]+\)|\(\.\@\*\-?[0-9]+\)",
                                     "\(\.\@\:0[xX][a-fA-F0-9]+\)|\(\.\@\:\-?[0-9]+\)",
                                     "\(\.\@\:\*0[xX][a-fA-F0-9]+\)|\(\.\@\:\*\-?[0-9]+\)",
                                     "\(\.\#0[xX][a-fA-F0-9]+\)|\(\.\#\-?[0-9]+\)",
                                     "\(\.\#\*0[xX][a-fA-F0-9]+\)|\(\.\#\*\-?[0-9]+\)",
                                     "\(\.\#\:0[xX][a-fA-F0-9]+\)|\(\.\#\:\-?[0-9]+\)",
                                     "\(\.\#\:\*0[xX][a-fA-F0-9]+\)|\(\.\#\:\*\-?[0-9]+\)",
                                     # All , patterns
                                     "\(\,\@0[xX][a-fA-F0-9]+\)|\(\,\@\-?[0-9]+\)",
                                     "\(\,\@\*0[xX][a-fA-F0-9]+\)|\(\,\@\*\-?[0-9]+\)",
                                     "\(\,\@\:0[xX][a-fA-F0-9]+\)|\(\,\@\:\-?[0-9]+\)",
                                     "\(\,\@\:\*0[xX][a-fA-F0-9]+\)|\(\,\@\:\*\-?[0-9]+\)",
                                     "\(\,\#0[xX][a-fA-F0-9]+\)|\(\,\#\-?[0-9]+\)",
                                     "\(\,\#\*0[xX][a-fA-F0-9]+\)|\(\,\#\*\-?[0-9]+\)",
                                     "\(\,\#\:0[xX][a-fA-F0-9]+\)|\(\,\#\:\-?[0-9]+\)",
                                     "\(\,\#\:\*0[xX][a-fA-F0-9]+\)|\(\,\#\:\*\-?[0-9]+\)",
                                     # All [ patterns
                                     "\(\[\@0[xX][a-fA-F0-9]+\)|\(\[\@\-?[0-9]+\)",
                                     "\(\[\@\*0[xX][a-fA-F0-9]+\)|\(\[\@\*\-?[0-9]+\)",
                                     "\(\[\@\:0[xX][a-fA-F0-9]+\)|\(\[\@\:\-?[0-9]+\)",
                                     "\(\[\@\:\*0[xX][a-fA-F0-9]+\)|\(\[\@\:\*\-?[0-9]+\)",
                                     "\(\[\#0[xX][a-fA-F0-9]+\)|\(\[\#\-?[0-9]+\)",
                                     "\(\[\#\*0[xX][a-fA-F0-9]+\)|\(\[\#\*\-?[0-9]+\)",
                                     "\(\[\#\:0[xX][a-fA-F0-9]+\)|\(\[\#\:\-?[0-9]+\)",
                                     "\(\[\#\:\*0[xX][a-fA-F0-9]+\)|\(\[\#\:\*\-?[0-9]+\)",
                                     # All ] patterns
                                     "\(\]\@0[xX][a-fA-F0-9]+\)|\(\]\@\-?[0-9]+\)",
                                     "\(\]\@\*0[xX][a-fA-F0-9]+\)|\(\]\@\*\-?[0-9]+\)",
                                     "\(\]\@\:0[xX][a-fA-F0-9]+\)|\(\]\@\:\-?[0-9]+\)",
                                     "\(\]\@\:\*0[xX][a-fA-F0-9]+\)|\(\]\@\:\*\-?[0-9]+\)",
                                     "\(\]\#0[xX][a-fA-F0-9]+\)|\(\]\#\-?[0-9]+\)",
                                     "\(\]\#\*0[xX][a-fA-F0-9]+\)|\(\]\#\*\-?[0-9]+\)",
                                     "\(\]\#\:0[xX][a-fA-F0-9]+\)|\(\]\#\:\-?[0-9]+\)",
                                     "\(\]\#\:\*0[xX][a-fA-F0-9]+\)|\(\]\#\:\*\-?[0-9]+\)",
                                     # All & patterns
                                     "\(\&\@0[xX][a-fA-F0-9]+\)|\(\&\@\-?[0-9]+\)",
                                     "\(\&\@\*0[xX][a-fA-F0-9]+\)|\(\&\@\*\-?[0-9]+\)",
                                     "\(\&\@\:0[xX][a-fA-F0-9]+\)|\(\&\@\:\-?[0-9]+\)",
                                     "\(\&\@\:\*0[xX][a-fA-F0-9]+\)|\(\&\@\:\*\-?[0-9]+\)",
                                     "\(\&\#0[xX][a-fA-F0-9]+\)|\(\&\#\-?[0-9]+\)",
                                     "\(\&\#\*0[xX][a-fA-F0-9]+\)|\(\&\#\*\-?[0-9]+\)",
                                     "\(\&\#\:0[xX][a-fA-F0-9]+\)|\(\&\#\:\-?[0-9]+\)",
                                     "\(\&\#\:\*0[xX][a-fA-F0-9]+\)|\(\&\#\:\*\-?[0-9]+\)",
                                     # All | patterns
                                     "\(\|\@0[xX][a-fA-F0-9]+\)|\(\|\@\-?[0-9]+\)",
                                     "\(\|\@\*0[xX][a-fA-F0-9]+\)|\(\|\@\*\-?[0-9]+\)",
                                     "\(\|\@\:0[xX][a-fA-F0-9]+\)|\(\|\@\:\-?[0-9]+\)",
                                     "\(\|\@\:\*0[xX][a-fA-F0-9]+\)|\(\|\@\:\*\-?[0-9]+\)",
                                     "\(\|\#0[xX][a-fA-F0-9]+\)|\(\|\#\-?[0-9]+\)",
                                     "\(\|\#\*0[xX][a-fA-F0-9]+\)|\(\|\#\*\-?[0-9]+\)",
                                     "\(\|\#\:0[xX][a-fA-F0-9]+\)|\(\|\#\:\-?[0-9]+\)",
                                     "\(\|\#\:\*0[xX][a-fA-F0-9]+\)|\(\|\#\:\*\-?[0-9]+\)",
                                     # All ^ patterns
                                     "\(\^\@0[xX][a-fA-F0-9]+\)|\(\^\@\-?[0-9]+\)",
                                     "\(\^\@\*0[xX][a-fA-F0-9]+\)|\(\^\@\*\-?[0-9]+\)",
                                     "\(\^\@\:0[xX][a-fA-F0-9]+\)|\(\^\@\:\-?[0-9]+\)",
                                     "\(\^\@\:\*0[xX][a-fA-F0-9]+\)|\(\^\@\:\*\-?[0-9]+\)",
                                     "\(\^\#0[xX][a-fA-F0-9]+\)|\(\^\#\-?[0-9]+\)",
                                     "\(\^\#\*0[xX][a-fA-F0-9]+\)|\(\^\#\*\-?[0-9]+\)",
                                     "\(\^\#\:0[xX][a-fA-F0-9]+\)|\(\^\#\:\-?[0-9]+\)",
                                     "\(\^\#\:\*0[xX][a-fA-F0-9]+\)|\(\^\#\:\*\-?[0-9]+\)",
                                     # All / patterns
                                     "\(\/\@0[xX][a-fA-F0-9]+\)|\(\/\@\-?[0-9]+\)",
                                     "\(\/\@\*0[xX][a-fA-F0-9]+\)|\(\/\@\*\-?[0-9]+\)",
                                     "\(\/\@\:0[xX][a-fA-F0-9]+\)|\(\/\@\:\-?[0-9]+\)",
                                     "\(\/\@\:\*0[xX][a-fA-F0-9]+\)|\(\/\@\:\*\-?[0-9]+\)",
                                     "\(\/\#0[xX][a-fA-F0-9]+\)|\(\/\#\-?[0-9]+\)",
                                     "\(\/\#\*0[xX][a-fA-F0-9]+\)|\(\/\#\*\-?[0-9]+\)",
                                     "\(\/\#\:0[xX][a-fA-F0-9]+\)|\(\/\#\:\-?[0-9]+\)",
                                     "\(\/\#\:\*0[xX][a-fA-F0-9]+\)|\(\/\#\:\*\-?[0-9]+\)",
                                     # All \ patterns
                                     "\(\\\@0[xX][a-fA-F0-9]+\)|\(\\\@\-?[0-9]+\)",
                                     "\(\\\@\*0[xX][a-fA-F0-9]+\)|\(\\\@\*\-?[0-9]+\)",
                                     "\(\\\@\:0[xX][a-fA-F0-9]+\)|\(\\\@\:\-?[0-9]+\)",
                                     "\(\\\@\:\*0[xX][a-fA-F0-9]+\)|\(\\\@\:\*\-?[0-9]+\)",
                                     "\(\\\#0[xX][a-fA-F0-9]+\)|\(\\\#\-?[0-9]+\)",
                                     "\(\\\#\*0[xX][a-fA-F0-9]+\)|\(\\\#\*\-?[0-9]+\)",
                                     "\(\\\#\:0[xX][a-fA-F0-9]+\)|\(\\\#\:\-?[0-9]+\)",
                                     "\(\\\#\:\*0[xX][a-fA-F0-9]+\)|\(\\\#\:\*\-?[0-9]+\)",
                                     # All misc patterns
                                     "\(\@[a-zA-Z][a-zA-Z0-9]*\)",
                                     "\(\![a-zA-Z][a-zA-Z0-9]*\)",
                                     "\(\!\:[a-zA-Z][a-zA-Z0-9]*\)" ]
        self._PATTERNS_WITH_GROUPS = [ # Standard instruction pattern
                                       "[\>\<\+\-\.\,\[\]\~\%\!]",
                                       # All > patterns
                                       "\(\>\@(0[xX][a-fA-F0-9]+)\)|\(\>\@(\-?[0-9]+)\)",
                                       "\(\>\@\*(0[xX][a-fA-F0-9]+)\)|\(\>\@\*(\-?[0-9]+)\)",
                                       "\(\>\@\:(0[xX][a-fA-F0-9]+)\)|\(\>\@\:(\-?[0-9]+)\)",
                                       "\(\>\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\>\@\:\*(\-?[0-9]+)\)",
                                       "\(\>\#(0[xX][a-fA-F0-9]+)\)|\(\>\#(\-?[0-9]+)\)",
                                       "\(\>\#\*(0[xX][a-fA-F0-9]+)\)|\(\>\#\*(\-?[0-9]+)\)",
                                       "\(\>\#\:(0[xX][a-fA-F0-9]+)\)|\(\>\#\:(\-?[0-9]+)\)",
                                       "\(\>\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\>\#\:\*(\-?[0-9]+)\)",
                                       # All < patterns
                                       "\(\<\@(0[xX][a-fA-F0-9]+)\)|\(\<\@(\-?[0-9]+)\)",
                                       "\(\<\@\*(0[xX][a-fA-F0-9]+)\)|\(\<\@\*(\-?[0-9]+)\)",
                                       "\(\<\@\:(0[xX][a-fA-F0-9]+)\)|\(\<\@\:(\-?[0-9]+)\)",
                                       "\(\<\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\<\@\:\*(\-?[0-9]+)\)",
                                       "\(\<\#(0[xX][a-fA-F0-9]+)\)|\(\<\#(\-?[0-9]+)\)",
                                       "\(\<\#\*(0[xX][a-fA-F0-9]+)\)|\(\<\#\*(\-?[0-9]+)\)",
                                       "\(\<\#\:(0[xX][a-fA-F0-9]+)\)|\(\<\#\:(\-?[0-9]+)\)",
                                       "\(\<\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\<\#\:\*(\-?[0-9]+)\)",
                                       # All + patterns
                                       "\(\+\@(0[xX][a-fA-F0-9]+)\)|\(\+\@(\-?[0-9]+)\)",
                                       "\(\+\@\*(0[xX][a-fA-F0-9]+)\)|\(\+\@\*(\-?[0-9]+)\)",
                                       "\(\+\@\:(0[xX][a-fA-F0-9]+)\)|\(\+\@\:(\-?[0-9]+)\)",
                                       "\(\+\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\+\@\:\*(\-?[0-9]+)\)",
                                       "\(\+\#(0[xX][a-fA-F0-9]+)\)|\(\+\#(\-?[0-9]+)\)",
                                       "\(\+\#\*(0[xX][a-fA-F0-9]+)\)|\(\+\#\*(\-?[0-9]+)\)",
                                       "\(\+\#\:(0[xX][a-fA-F0-9]+)\)|\(\+\#\:(\-?[0-9]+)\)",
                                       "\(\+\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\+\#\:\*(\-?[0-9]+)\)",
                                       # All - patterns
                                       "\(\-\@(0[xX][a-fA-F0-9]+)\)|\(\-\@(\-?[0-9]+)\)",
                                       "\(\-\@\*(0[xX][a-fA-F0-9]+)\)|\(\-\@\*(\-?[0-9]+)\)",
                                       "\(\-\@\:(0[xX][a-fA-F0-9]+)\)|\(\-\@\:(\-?[0-9]+)\)",
                                       "\(\-\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\-\@\:\*(\-?[0-9]+)\)",
                                       "\(\-\#(0[xX][a-fA-F0-9]+)\)|\(\-\#(\-?[0-9]+)\)",
                                       "\(\-\#\*(0[xX][a-fA-F0-9]+)\)|\(\-\#\*(\-?[0-9]+)\)",
                                       "\(\-\#\:(0[xX][a-fA-F0-9]+)\)|\(\-\#\:(\-?[0-9]+)\)",
                                       "\(\-\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\-\#\:\*(\-?[0-9]+)\)",
                                       # All . patterns
                                       "\(\.\@(0[xX][a-fA-F0-9]+)\)|\(\.\@(\-?[0-9]+)\)",
                                       "\(\.\@\*(0[xX][a-fA-F0-9]+)\)|\(\.\@\*(\-?[0-9]+)\)",
                                       "\(\.\@\:(0[xX][a-fA-F0-9]+)\)|\(\.\@\:(\-?[0-9]+)\)",
                                       "\(\.\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\.\@\:\*(\-?[0-9]+)\)",
                                       "\(\.\#(0[xX][a-fA-F0-9]+)\)|\(\.\#(\-?[0-9]+)\)",
                                       "\(\.\#\*(0[xX][a-fA-F0-9]+)\)|\(\.\#\*(\-?[0-9]+)\)",
                                       "\(\.\#\:(0[xX][a-fA-F0-9]+)\)|\(\.\#\:(\-?[0-9]+)\)",
                                       "\(\.\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\.\#\:\*(\-?[0-9]+)\)",
                                       # All , patterns
                                       "\(\,\@(0[xX][a-fA-F0-9]+)\)|\(\,\@(\-?[0-9]+)\)",
                                       "\(\,\@\*(0[xX][a-fA-F0-9]+)\)|\(\,\@\*(\-?[0-9]+)\)",
                                       "\(\,\@\:(0[xX][a-fA-F0-9]+)\)|\(\,\@\:(\-?[0-9]+)\)",
                                       "\(\,\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\,\@\:\*(\-?[0-9]+)\)",
                                       "\(\,\#(0[xX][a-fA-F0-9]+)\)|\(\,\#(\-?[0-9]+)\)",
                                       "\(\,\#\*(0[xX][a-fA-F0-9]+)\)|\(\,\#\*(\-?[0-9]+)\)",
                                       "\(\,\#\:(0[xX][a-fA-F0-9]+)\)|\(\,\#\:(\-?[0-9]+)\)",
                                       "\(\,\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\,\#\:\*(\-?[0-9]+)\)",
                                       # All [ patterns
                                       "\(\[\@(0[xX][a-fA-F0-9]+)\)|\(\[\@(\-?[0-9]+)\)",
                                       "\(\[\@\*(0[xX][a-fA-F0-9]+)\)|\(\[\@\*(\-?[0-9]+)\)",
                                       "\(\[\@\:(0[xX][a-fA-F0-9]+)\)|\(\[\@\:(\-?[0-9]+)\)",
                                       "\(\[\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\[\@\:\*(\-?[0-9]+)\)",
                                       "\(\[\#(0[xX][a-fA-F0-9]+)\)|\(\[\#(\-?[0-9]+)\)",
                                       "\(\[\#\*(0[xX][a-fA-F0-9]+)\)|\(\[\#\*(\-?[0-9]+)\)",
                                       "\(\[\#\:(0[xX][a-fA-F0-9]+)\)|\(\[\#\:(\-?[0-9]+)\)",
                                       "\(\[\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\[\#\:\*(\-?[0-9]+)\)",
                                       # All ] patterns
                                       "\(\]\@(0[xX][a-fA-F0-9]+)\)|\(\]\@(\-?[0-9]+)\)",
                                       "\(\]\@\*(0[xX][a-fA-F0-9]+)\)|\(\]\@\*(\-?[0-9]+)\)",
                                       "\(\]\@\:(0[xX][a-fA-F0-9]+)\)|\(\]\@\:(\-?[0-9]+)\)",
                                       "\(\]\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\]\@\:\*(\-?[0-9]+)\)",
                                       "\(\]\#(0[xX][a-fA-F0-9]+)\)|\(\]\#(\-?[0-9]+)\)",
                                       "\(\]\#\*(0[xX][a-fA-F0-9]+)\)|\(\]\#\*(\-?[0-9]+)\)",
                                       "\(\]\#\:(0[xX][a-fA-F0-9]+)\)|\(\]\#\:(\-?[0-9]+)\)",
                                       "\(\]\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\]\#\:\*(\-?[0-9]+)\)",
                                       # All & patterns
                                       "\(\&\@(0[xX][a-fA-F0-9]+)\)|\(\&\@(\-?[0-9]+)\)",
                                       "\(\&\@\*(0[xX][a-fA-F0-9]+)\)|\(\&\@\*(\-?[0-9]+)\)",
                                       "\(\&\@\:(0[xX][a-fA-F0-9]+)\)|\(\&\@\:(\-?[0-9]+)\)",
                                       "\(\&\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\&\@\:\*(\-?[0-9]+)\)",
                                       "\(\&\#(0[xX][a-fA-F0-9]+)\)|\(\&\#(\-?[0-9]+)\)",
                                       "\(\&\#\*(0[xX][a-fA-F0-9]+)\)|\(\&\#\*(\-?[0-9]+)\)",
                                       "\(\&\#\:(0[xX][a-fA-F0-9]+)\)|\(\&\#\:(\-?[0-9]+)\)",
                                       "\(\&\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\&\#\:\*(\-?[0-9]+)\)",
                                       # All | patterns
                                       "\(\|\@(0[xX][a-fA-F0-9]+)\)|\(\|\@(\-?[0-9]+)\)",
                                       "\(\|\@\*(0[xX][a-fA-F0-9]+)\)|\(\|\@\*(\-?[0-9]+)\)",
                                       "\(\|\@\:(0[xX][a-fA-F0-9]+)\)|\(\|\@\:(\-?[0-9]+)\)",
                                       "\(\|\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\|\@\:\*(\-?[0-9]+)\)",
                                       "\(\|\#(0[xX][a-fA-F0-9]+)\)|\(\|\#(\-?[0-9]+)\)",
                                       "\(\|\#\*(0[xX][a-fA-F0-9]+)\)|\(\|\#\*(\-?[0-9]+)\)",
                                       "\(\|\#\:(0[xX][a-fA-F0-9]+)\)|\(\|\#\:(\-?[0-9]+)\)",
                                       "\(\|\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\|\#\:\*(\-?[0-9]+)\)",
                                       # All ^ patterns
                                       "\(\^\@(0[xX][a-fA-F0-9]+)\)|\(\^\@(\-?[0-9]+)\)",
                                       "\(\^\@\*(0[xX][a-fA-F0-9]+)\)|\(\^\@\*(\-?[0-9]+)\)",
                                       "\(\^\@\:(0[xX][a-fA-F0-9]+)\)|\(\^\@\:(\-?[0-9]+)\)",
                                       "\(\^\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\^\@\:\*(\-?[0-9]+)\)",
                                       "\(\^\#(0[xX][a-fA-F0-9]+)\)|\(\^\#(\-?[0-9]+)\)",
                                       "\(\^\#\*(0[xX][a-fA-F0-9]+)\)|\(\^\#\*(\-?[0-9]+)\)",
                                       "\(\^\#\:(0[xX][a-fA-F0-9]+)\)|\(\^\#\:(\-?[0-9]+)\)",
                                       "\(\^\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\^\#\:\*(\-?[0-9]+)\)",
                                       # All / patterns
                                       "\(\/\@(0[xX][a-fA-F0-9]+)\)|\(\/\@(\-?[0-9]+)\)",
                                       "\(\/\@\*(0[xX][a-fA-F0-9]+)\)|\(\/\@\*(\-?[0-9]+)\)",
                                       "\(\/\@\:(0[xX][a-fA-F0-9]+)\)|\(\/\@\:(\-?[0-9]+)\)",
                                       "\(\/\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\/\@\:\*(\-?[0-9]+)\)",
                                       "\(\/\#(0[xX][a-fA-F0-9]+)\)|\(\/\#(\-?[0-9]+)\)",
                                       "\(\/\#\*(0[xX][a-fA-F0-9]+)\)|\(\/\#\*(\-?[0-9]+)\)",
                                       "\(\/\#\:(0[xX][a-fA-F0-9]+)\)|\(\/\#\:(\-?[0-9]+)\)",
                                       "\(\/\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\/\#\:\*(\-?[0-9]+)\)",
                                       # All \ patterns
                                       "\(\\\@(0[xX][a-fA-F0-9]+)\)|\(\\\@(\-?[0-9]+)\)",
                                       "\(\\\@\*(0[xX][a-fA-F0-9]+)\)|\(\\\@\*(\-?[0-9]+)\)",
                                       "\(\\\@\:(0[xX][a-fA-F0-9]+)\)|\(\\\@\:(\-?[0-9]+)\)",
                                       "\(\\\@\:\*(0[xX][a-fA-F0-9]+)\)|\(\\\@\:\*(\-?[0-9]+)\)",
                                       "\(\\\#(0[xX][a-fA-F0-9]+)\)|\(\\\#(\-?[0-9]+)\)",
                                       "\(\\\#\*(0[xX][a-fA-F0-9]+)\)|\(\\\#\*(\-?[0-9]+)\)",
                                       "\(\\\#\:(0[xX][a-fA-F0-9]+)\)|\(\\\#\:(\-?[0-9]+)\)",
                                       "\(\\\#\:\*(0[xX][a-fA-F0-9]+)\)|\(\\\#\:\*(\-?[0-9]+)\)",
                                       # All misc patterns
                                       "\(\@([a-zA-Z][a-zA-Z0-9]*)\)",
                                       "\(\!([a-zA-Z][a-zA-Z0-9]*)\)",
                                       "\(\!\:([a-zA-Z][a-zA-Z0-9]*)\)" ]
        self._stdin = sys.stdin
        self._stdout = sys.stdout
        self._instructions = []
        self._identifier_dict = dict()

    def instructions():
        doc = "The instructions property."
        def fget(self):
            return self._instructions
        def fset(self, value):
            instructions = re.sub( "{{.*?}}", '', value, flags=re.DOTALL ) # Remove block comments
            pattern = re.compile( '|'.join( self._PATTERNS_NO_GROUPS ) ) # Compile the regex for valid instructions
            instructions = pattern.findall( instructions )
            for instr in instructions:
                # Find all (@id) instructions, store them in the identifier dictionary, and remove them from the instruction set
                if re.match( self._IDENTIFIER_PATTERN, instr ) is not None:
                    match = re.match( self._IDENTIFIER_PATTERN, instr )
                    self._identifier_dict[ match.group(1) ] = instructions.index( instr )
                    del instructions[ instructions.index( instr ) ]

            self._instructions = instructions
        def fdel(self):
            del self._instructions
        return locals()
    instructions = property(**instructions())

    def find_matching_bracket(self, current_position):
        if re.search( '\[', self._instructions[current_position] ) is not None:
            bracket = '\['
            matching = '\]'
            step = 1
        elif re.search( '\]', self._instructions[current_position] ) is not None:
            bracket = '\]'
            matching = '\['
            step = -1
        else:
            raise SyntaxError("Unexpected instruction {} encountered".format(self._instructions[current_position]))

        bracket_count = 1
        search_position = current_position + step

        while True:
            if re.search( bracket, self._instructions[search_position] ) is not None:
                bracket_count += 1
            if re.search( matching, self._instructions[search_position] ) is not None:
                bracket_count -= 1
            if bracket_count == 0:
                break

            if bracket_count < 0:
                raise SyntaxError("Unmatched {} bracket: {}".format(bracket,self._instruction_pointer))
            if search_position >= len(self._data_array) - 1:
                raise SyntaxError("Unmatched {} bracket: {}".format(matching,self._instruction_pointer))

            search_position += step

        return search_position

class Compiler(object):
    INSTRUCTION_SIZE_16 = 2
    INSTRUCTION_SIZE_32 = 4
    INSTRUCTION_SIZE_64 = 8
    ENDIANNESS_LITTLE = 0
    ENDIANNESS_BIG = 1
    MASK_OPERAND_SIDE = 0x80
    MASK_INDIRECTION = 0x40
    MASK_RELATIVE = 0x20
    MASK_DOUBLE_SIZE = 0x10
    MASK_INSTRUCTION = 0x0F
    INSTRUCTION_SPL = 0x00 # Special low
    INSTRUCTION_GT  = 0x01 # >
    INSTRUCTION_LT  = 0x02 # <
    INSTRUCTION_ADD = 0x03 # +
    INSTRUCTION_SUB = 0x04 # -
    INSTRUCTION_DOT = 0x05 # .
    INSTRUCTION_COM = 0x06 # ,
    INSTRUCTION_OPN = 0x07 # [
    INSTRUCTION_CLS = 0x08 # ]
    INSTRUCTION_AND = 0x09 # &
    INSTRUCTION_OR  = 0x0A # |
    INSTRUCTION_XOR = 0x0B # ^
    INSTRUCTION_SRT = 0x0C # /
    INSTRUCTION_SLT = 0x0D # \
    INSTRUCTION_SPH = 0x0F # Special high
    SPECIAL_LOW_NOP = 0x00 # No operation
    SPECIAL_LOW_NOT = 0x10 # ~
    SPECIAL_LOW_PCT = 0x20 # %
    SPECIAL_LOW_GO  = 0x30 # (!id)
    SPECIAL_LOW_GOR = 0x40 # (!:id)
    SPECIAL_LOW_RET = 0x50 # !
    SPECIAL_HI_NOP  = 0xF0

    def __init__(self, app):
        self._app = app
        self._stdin = None
        self._stdout = None
        self._instruction_size = INSTRUCTION_SIZE_32
        self._endianness = ENDIANNESS_LITTLE
        self._instruction_array = bytearray()

    def compile(self):
        if self._endianness == ENDIANNESS_BIG:
            endian_symbol = '>'
        else:
            endian_symbol = '<'

        for instr in self._app.instructions:
            if current_instruction == '>':
                # Move data pointer right one
                self._instruction_array.append( struct.pack( endian_symbol + ""))


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


def main():
    argparser = argparse.ArgumentParser( description="A python implementation of the Embedded "
                                                     "Brainfuck interpreter." )
    argparser.add_argument( "ebf", type=argparse.FileType('r'),
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

    app = Ebf()
    app.instructions = args.ebf.read()

    if args.size is not None:
        interp = Interpreter( app, args.size )
    else:
        interp = Interpreter( app )

    if args.debug:
        interp.debug = args.debug

    if args.input is not None:
        in_file = args.input
    else:
        in_file = sys.stdin

    if args.output is not None:
        out_file = args.output
    else:
        out_file = sys.stdout

    interp.stdin = in_file
    interp.stdout = out_file

    while interp.step():
        pass

if __name__ == "__main__":
    main()
