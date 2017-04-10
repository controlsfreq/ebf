# Embedded Brain Fuck (EBF)

## Introduction

Embedded Brain Fuck (or EBF) is an extension of the Brain Fuck language to allow easier usage on
embedded systems. EBF adds a number of extra commands that make writing and manipulating registers
and various places in memory simpler. It also provides mechanisms for literal writes into memory.

## Overview

EBF maps the data array from classic Brain Fuck to the entire system memory (this may be overridden
via configuration options). This allows for architecture specific applications to access chip
configuration registers.

EBF programs are compiled into portable C code instead of interpreted directly. This allows the user
to then compile the application using whatever C compiler works for their system.

## Programming Model

EBF follows the same model as original Brain Fuck, with a large, contiguous array of memory which
may be accessed a single cell at a time. However, EBF adds several features which enable easier
program and data flow on embedded systems. Most instructions allow for these modifiers:

* Absolute Addressing - Take an absolute address to work on instead of using the current data cell.
* Relative Addressing - Take a relative address, using an offset from the current working cell as an
  operand.
* Literals - Take a literal value as an operand to the instruction.

See the Instructions section below for specifics on how each instruction works with these modifiers.

### Data Pointer

EBF uses a variable to keep track of the current working cell: `DP`. This pointer is incremented and
decremented to access different cells and may be used to access or modify the value inside a cell.
User defined functions may access this variable by including `ebf.h`.

### Configuration

A single configuration block may be inserted into each EBF application which modifies the generated
code in particular ways. The configuration block must be contained within a `#%(...)` expression.
It may be multi-lined, and must adhere to YAML formatting. All options are either key/value pairs or
sequences. Below is a listing of all options and what they do:

* `cell_width`: The width in bits of each data cell. Valid values are 8, 16, 32, and 64.
* `includes`: Any user supplied header files that should be included in the EBF application. Allows
  the application to call user supplied functions and hooks. Must be formatted as a sequence.
* `init_hook`: A boolean option that turns on the `init_hook()` function before the application
  code. This function must be defined by the user.
* `cleanup_hook`: A boolean option that turns on the `cleanup_hook()` function after the application
  code. This function must be defined by the user.

## Instructions

This section describes all of the valid instructions available in EBF, including both the classic
and extended commands. The extended commands are a superset of the original commands and thus a
classic Brain Fuck program will still be compiled correctly.

### Unary Instructions

Standard instructions are single character (unary) commands that typically operate using the current
cell and/or data pointer.

* `>` - Increment data pointer.
* `<` - Decrement data pointer.
* `+` - Increment current cell value.
* `-` - Decrement current cell value.
* `.` - Write the current cell value to `stdout`.
* `,` - Read a value from `stdin` and store it in the current cell.
* `[` - If the current cell is zero, jump forward to one after the matching `]`.
* `]` - If the current data value is non-zero, jump back to one after the matching `[`. Must close a
        previous `[`.
* `|` - Bitwise OR the current cell and the next cell to the right and store the result in the
        current cell.
* `&` - Bitwise AND the current cell and the next cell to the right and store the result in the
        current cell.
* `^` - Bitwise XOR the current cell and the next cell to the right and store the result in the
        current cell.
* `~` - Bitwise NOT the current cell and store the result in the current cell.
* `\` - Bitwise left shift the current cell by one and store the result in the current cell.
* `/` - Bitwise right shift the current cell by one and store the result in the current cell.

### Modified Instructions

Modified instructions are multi-character instructions that have a modifier character and take a
number `N` as an operand. There are three different classes of extended commands: absolute address,
relative address, and literal.

The general form of a modified instruction is: `IMN`, where `I` is the instruction character, `M` is
the modifier character, and `N` is a number in either decimal (positive or negative), octal, or
hexadecimal.

#### Absolute Address Instructions

Absolute address instructions interpret the `N` parameter as an absolute address. That address is
dereferenced and the value at that cell is used to perform the given instruction. For example,
`+*0xDEADBEEF` reads the value at cell `0xDEADBEEF` and adds that value to the current cell.

Below is a list of all of the absolute address instructions:

* `>*N` - Increment data pointer by the value at `N`.
* `<*N` - Decrement data pointer by the value at `N`.
* `+*N` - Increment current cell value by the value at `N`.
* `-*N` - Decrement current cell value by the value at `N`.
* `.*N` - Write the value at `N` to `stdout`.
* `,*N` - Read a value from `stdin` and store it in cell `N`.
* `[*N` - If the value at `N` is zero, jump forward to one after the matching `]`.
* `|*N` - Bitwise OR the current cell and the value at `N` and store the result in the current
          cell.
* `&*N` - Bitwise AND the current cell and the value at `N` and store the result in the current
          cell.
* `^*N` - Bitwise XOR the current cell and the value at `N` and store the result in the current
          cell.
* `~*N` - Bitwise NOT the value at `N` and store the result in the current cell.
* `\*N` - Bitwise left shift the current cell by the value in `N` and store the result in the
          current cell.
* `/*N` - Bitwise right shift the current cell by the value in `N` and store the result in the
          current cell.

#### Relative Address Instructions

Relative address instructions interpret the `N` parameter as an offset from the current `DP`. That
address is dereferenced and the value at that cell is used to perform the given instruction. For
example, `+:0x100` reads the value at cell `DP + 256` and adds that value to the current cell.

Below is a list of all of the relative address instructions:

* `>:N` - Increment data pointer by the value at `DP+N`.
* `<:N` - Decrement data pointer by the value at `DP+N`.
* `+:N` - Increment current cell value by the value at `DP+N`.
* `-:N` - Decrement current cell value by the value at `DP+N`.
* `.:N` - Write the value at `DP+N` to `stdout`.
* `,:N` - Read a value from `stdin` and store it in cell `DP+N`.
* `[:N` - If the value at `(DP+N)` is zero, jump forward to one after the matching `]`.
* `|:N` - Bitwise OR the current cell and the value at `(DP+N)` and store the result in the current
          cell.
* `&:N` - Bitwise AND the current cell and the value at `(DP+N)` and store the result in the current
          cell.
* `^:N` - Bitwise XOR the current cell and the value at `(DP+N)` and store the result in the current
          cell.
* `~:N` - Bitwise NOT the value at `(DP+N)` and store the result in the current cell.
* `\:N` - Bitwise left shift the current cell by the value in `(DP+N)` and store the result in the
          current cell.
* `/:N` - Bitwise right shift the current cell by the value in `(DP+N)` and store the result in the
          current cell.

#### Literal Instructions

Literal instructions interpret `N` parameter as a literal value. Similarly to absolute and relative,
that value is used to perform the given instruction. For example, `+#0x1234` adds `0x1234` to the
current cell.

Below is a list of all of the literal instructions:

* `>#N` - Increment data pointer by the value `N`.
* `<#N` - Decrement data pointer by the value `N`.
* `+#N` - Increment current cell value by the value `N`.
* `-#N` - Decrement current cell value by the value `N`.
* `.#N` - Write the value `N` to `stdout`.
* `,#N` - Store the value `N` to the current cell.
* `[#N` - If the value `N` is zero, jump forward to one after the matching `]`.
* `|#N` - Bitwise OR the current cell and the value at `N` and store the result in the current cell.
* `&#N` - Bitwise AND the current cell and the value at `N` and store the result in the current
          cell.
* `^#N` - Bitwise XOR the current cell and the value at `N` and store the result in the current
          cell.
* `~#N` - Bitwise NOT the value at `N` and store the result in the current cell.
* `\#N` - Bitwise left shift the current cell by the value in `N` and store the result in the
          current cell.
* `/#N` - Bitwise right shift the current cell by the value in `N` and store the result in the
          current cell.

### Jump Instructions

Jump instructions allow the programmer to jump the instruction pointer to another location in the
program. These instructions work the same as C labels and `goto`. Note, once a jump occurs there is
no built-in concept of a return location.

* `@text` - Mark a label named `text`. This location may later be jumped to. Labels must begin with
            an alphabetical character, but may contain alphanumeric and `_` characters.
* `!text` - Jump to label `text`. If the label is not defined in the application it is considered a
            syntax error. A jump may precede a label definition in the application.
* `!(text)` - This is a special form of a jump that translates to a C function call. This allows the
              programmer to call external functions. The function signature must be
              `void text(void)`.

### Comments

Comments in the code may be made using two methods, a line comment or non-instruction characters.
Non-instruction characters are ignored, therefore, any characters that are not interpreted as an
instruction are considered a comment.

A line comment is used to mark an entire line as a comment, thus allowing instruction characters
and syntax to be used in a comment. Any line beginning with `#` is considered a line comment (unless
it is a configuration block, which is treated specially).

# Appendix

## Cheat Sheet

<table cellspacing="0" cellpadding="0">
    <tr style='height:20px; font-weight:bold; background-color:#4d79ff; text-align:center'>
        <td rowspan="2">Expression</td>
        <td colspan="2">Default</td>
        <td colspan="2">Absolute Address</td>
        <td colspan="2">Relative Address</td>
        <td colspan="2">Literal</td>
    </tr>
    <tr style='height:20px; text-align:center'>
        <td style='background-color:#ccd9ff'>Syntax</td>
        <td style='background-color:#ccd9ff'>C Equivalent</td>
        <td style='background-color:#ccd9ff'>Syntax</td>
        <td style='background-color:#ccd9ff'>C Equivalent</td>
        <td style='background-color:#ccd9ff'>Syntax</td>
        <td style='background-color:#ccd9ff'>C Equivalent</td>
        <td style='background-color:#ccd9ff'>Syntax</td>
        <td style='background-color:#ccd9ff'>C Equivalent</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>&gt;</td>
        <td>&gt;</td>
        <td>DP++</td>
        <td>&gt;*N</td>
        <td>DP+=*N</td>
        <td>&gt;:N</td>
        <td>DP+=*(DP+N)</td>
        <td>&gt;#N</td>
        <td>DP+=N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>&lt;</td>
        <td>&lt;</td>
        <td>DP--</td>
        <td>&lt;*N</td>
        <td>DP-=*N</td>
        <td>&lt;:N</td>
        <td>DP-=*(DP+N)</td>
        <td>&lt;#N</td>
        <td>DP-=N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>+</td>
        <td>+</td>
        <td>(*DP)++</td>
        <td>+*N</td>
        <td>*DP+=*N</td>
        <td>+:N</td>
        <td>*DP+=*(DP+N)</td>
        <td>+#N</td>
        <td>*DP+=N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>-</td>
        <td>-</td>
        <td>(*DP)--</td>
        <td>-*N</td>
        <td>*DP-=*N</td>
        <td>-:N</td>
        <td>*DP-=*(DP+N)</td>
        <td>-#N</td>
        <td>*DP-=N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>[</td>
        <td>[</td>
        <td>while(*DP!=0) {</td>
        <td>[*N</td>
        <td>while(*N!=0) {</td>
        <td>[:N</td>
        <td>while(*(DP+N)!=0) {</td>
        <td>[#N</td>
        <td>while(N!=0) {</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>]</td>
        <td>]</td>
        <td>} // end while</td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>.</td>
        <td>.</td>
        <td>putchar(*DP)</td>
        <td>.*N</td>
        <td>putchar(*N)</td>
        <td>.:N</td>
        <td>putchar(*(DP+N))</td>
        <td>.#N</td>
        <td>putchar(N)</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>,</td>
        <td>,</td>
        <td>*DP=getchar()</td>
        <td>,*N</td>
        <td>*N=getchar()</td>
        <td>,:N</td>
        <td>*(DP+N)=getchar()</td>
        <td>,#N</td>
        <td>*DP=N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>&amp;</td>
        <td>&amp;</td>
        <td>*DP=*DP&amp;*(DP+1)</td>
        <td>&amp;*N</td>
        <td>*DP=*DP&amp;*N</td>
        <td>&amp;:N</td>
        <td>*DP=*DP&amp;*(DP+N)</td>
        <td>&amp;#N</td>
        <td>*DP=*DP&amp;N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>|</td>
        <td>|</td>
        <td>*DP=*DP|*(DP+1)</td>
        <td>|*N</td>
        <td>*DP=*DP|*N</td>
        <td>|:N</td>
        <td>*DP=*DP|*(DP+N)</td>
        <td>|#N</td>
        <td>*DP=*DP|N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>^</td>
        <td>^</td>
        <td>*DP=*DP^*(DP+1)</td>
        <td>^*N</td>
        <td>*DP=*DP^*N</td>
        <td>^:N</td>
        <td>*DP=*DP^*(DP+N)</td>
        <td>^#N</td>
        <td>*DP=*DP^N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>~</td>
        <td>~</td>
        <td>*DP=~*DP</td>
        <td>~*N</td>
        <td>*DP=~*N</td>
        <td>~:N</td>
        <td>*DP=~*(DP+N)</td>
        <td>~#N</td>
        <td>*DP=~N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>\</td>
        <td>\</td>
        <td>*DP=*DP&lt;&lt;1</td>
        <td>\*N</td>
        <td>*DP=*DP&lt;&lt;*N</td>
        <td>\:N</td>
        <td>*DP=*DP&lt;&lt;*(DP+N)</td>
        <td>\#N</td>
        <td>*DP=*DP&lt;&lt;N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>/</td>
        <td>/</td>
        <td>*DP=*DP&gt;&gt;1</td>
        <td>/*N</td>
        <td>*DP=*DP&gt;&gt;*N</td>
        <td>/:N</td>
        <td>*DP=*DP&gt;&gt;*(DP+N)</td>
        <td>/#N</td>
        <td>*DP=*DP&gt;&gt;N</td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>@</td>
        <td>@text</td>
        <td>text:</td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>!</td>
        <td>!text</td>
        <td>goto text;</td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>!()</td>
        <td>!(text)</td>
        <td>text();</td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>#</td>
        <td># comment</td>
        <td>/* comment */</td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
    </tr>
    <tr style='height:20px; font-family:monospace;'>
        <td>#%()</td>
        <td>#%(config)</td>
        <td>N/A</td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
        <td style='background-color:#8c8c8c;'></td>
    </tr>
</table>
