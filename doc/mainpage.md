# Extended/Embedded Brain Fuck

## Introduction

Extended or Embedded Brain Fuck (or EBF) is an extension of the Brain Fuck language to allow easier
usage on embedded systems. EBF adds a number of extended commands that make writing to and from
registers and various places in memory simpler. It also provides mechanisms for single depth
function calls, literal writes into data memory, and the ability to override the stdin and stdout
operations defined in classic Brain Fuck.

## Overview

EBF maps the data array from classic Brain Fuck to a specific area of memory depending on the
system it is being compiled for. This allows for architecture specific mapping. For example, on an
embedded microcontroller it could map to the entire RAM section of the microcontroller giving the
program access to everything in RAM, including hardware registers.

EBF programs are also (loosely) compiled instead of interpreted. This compilation removes some of
the more difficult features to implement on an embedded system and replaces them with faster
alternatives. For example, it removes the identifiers used for function calls and replaces them
with jump addresses wherever they are used.

## Memory Maps

Memory mapping in EBF is used to allow the program to access all important memory regions on an
embedded system.

## Compiling

### Stages

There are two stages to compiling an EBF program. The first stage is the EBF transcoding which
takes the `.ebf` file and converts it to a binary format which is readable by the EBF runner. This
binary blob is stored as a C variable in a `.c` file which may then be compiled by a C compiler.
After compilation, the instruction binary blob may be accessed by the Runner as any other C
variable would.

This two step method allows the EBF instructions to be stored wherever is most convenient on the
embedded system (determined at link-time). It also allows for new Runners to be written and
compiled without any modification to the EBF program.

### Runners

### Bootloaders

### Addresses

### Binary Format

The binary format of an EBF program after compilation begins with a magic number (given here in
hexadecimal): `23 45 42 46 MM mm pp`. Here, `MM` is the major version, `mm` is the minor version, and
`pp` is the patch version of the standard used during compilation. This version may or may not be
used to determine compatibility with the runner at run time.

After the magic number is a stream of byte instructions. All instructions are 1 byte wide, but some
instructions take a parameter which must be directly after the instruction. The parameter must be
aligned to the natural system boundary. This may require NOP padding before the instruction byte.
The alignment is required to ensure ease of reading the numbers stored in the parameter space.

Parameters are always the same width as the system's register width.

#### Byte Commands

All byte commands use the following format: `bmmRiiiii`, where `mm` is the instruction mode, `R` is
reserved, and `iiiii` is the instruction to execute.

Valid modes:

* `00` - Standard mode.
* `01` - Absolute addressing mode.
* `10` - Relative addressing mode.
* `11` - Literal mode.

Valid instructions:

* `00000` - No operation (NOP).
* `00001` - Jump data pointer right.
* `00010` - Jump data pointer left.
* `00011` - Increment data value.
* `00100` - Decrement data value.
* `00101` - Copy value from current cell.
* `00110` - Copy value to current cell.
* `00111` - Forward jump.
* `01000` - Backward jump.
* `01001` - Bitwise NOT.
* `01010` - Data pointer swap.
* `01011` - Instruction pointer swap.
* `01100` - Bitwise AND.
* `01101` - Bitwise OR.
* `01110` - Bitwise XOR.
* `01111` - Shift right.
* `10000` - Shift left.

Special instructions:

* `11111111` (`0xFF`) - No operation (NOP).

## Special Functions

Special functions are functions that aren't called in the normal flow of a program, for example
interrupt vectors. These functions are named using a special identifier (e.g. `(@:_interrupt)`)
that is defined by the architecture specific Runner. Special variables are inserted into the
transcoded C file that tell the Runner where to find these special functions.

All special functions must begin with an `(@:id)` definition and end with a `!`. They may not
define any other identifier symbols within that block.

## Commands

This section describes all of the valid commands available in EBF, including both the classic and
extended commands. The extended commands are a superset of the original commands and thus a classic
Brain Fuck program will run correctly in an EBF environment.

### Standard Commands

Standard commands are single character (unary) commands that are generally simple and have a single
operation.

* `>` - Increment data pointer.
* `<` - Decrement data pointer.
* `+` - Increment value at data pointer.
* `-` - Decrement value at data pointer.
* `.` - Copy value at data pointer to `stdout` (Note: `stdout` must be defined at compile-time).
* `,` - Copy value from `stdin` to current data pointer (Note: `stdin` must be defined at
        compile-time).
* `[` - If the current data value is zero, move the instruction pointer forward to one after the
        matching `]`.
* `]` - If the current data value is non-zero, move the instruction pointer back to one after the
        matching `[`.
* `~` - Bitwise NOT the current data value and store the result in the current cell.
* `%` - Swap the current data pointer and the shadow data register.
* `!` - Swap the instruction pointer and the shadow instruction register (i.e. return from the
        previous call/jump).

### Extended Commands

Extended commands are multi-character commands that generally perform multiple operations per
invocation (e.g. modifying the data pointer by multiple cells while also shadowing the previous
data pointer).

* `(x:n)` - An absolute addressed command, where `x` is the command and `n` is the address used for
            that command. The possible commands and their behaviors are shown below:

            * `>` - Move the data pointer to the given address and store the previous address in
                    the shadow data register. Note: Same behavior as `<`.
            * `<` - Move the data pointer to the given address and store the previous address in
                    the shadow data register. Note: Same behavior as `>`.
            * `+` - Increment the data value at the absolute address `n`.
            * `-` - Decrement the data value at the absolute address `n`.
            * `.` - Copy the current data value to the data address indicated.
            * `,` - Copy the data value from the address indicated to the current data value.
            * `[` - If the data value at the absolute address `n` is zero, move the instruction
                    pointer forward to one after the matching `]` (not necessarily absolutely
                    addressed).
            * `]` - If the data value at the absolute address `n` is non-zero, move the instruction
                    pointer backward to one after the matching `[` (not necessarily an absolutely
                    addressed).
            * `&` - Bitwise AND the current data value and the value stored in the absolute address
                    `n` and store the result in the current data cell.
            * `|` - Bitwise OR the current data value and the value stored in the absolute address
                    `n` and store the result in the current data cell.
            * `^` - Bitwise XOR the current data value and the value stored in the absolute address
                    `n` and store the result in the current data cell.
            * `/` - Shift right the current data value by the value stored in the absolute address
                    `n` and store the result in the current data cell.
            * `\` - Shift left the current data value by the value stored in the absolute address
                    `n` and store the result in the current data cell.

            Note: `n` must be within the range UINT_MIN to UINT_MAX unless otherwise specified.

* `[x:n]` - A relative addressed command, where `x` is the command and `n` is the offset used for
            that command. The possible commands and their behaviors are shown below:

            * `>` - Increment the data pointer by the offset given and store the previous address
                    in the shadow data register.
            * `<` - Decrement the data pointer by the offset given and store the previous address
                    in the shadow data register.
            * `+` - Increment the data value at the relative address `n`.
            * `-` - Decrement the data value at the relative address `n`.
            * `.` - Copy the current data value to the data address formed by the current address
                    offset by the given value. Note: May only offset in the positive direction.
            * `,` - Copy into the current data value the data value from the address formed by the
                    current address offset by the given value. Note: May only offset in the
                    positive direction.
            * `[` - If the data value at the relative address `n` is zero, move the instruction
                    pointer forward to one after the matching `]` (not necessarily relatively
                    addressed).
            * `]` - If the data value at the relative address `n` is non-zero, move the instruction
                    pointer backward to one after the matching `[` (not necessarily relatively
                    addressed).
            * `&` - Bitwise AND the current data value and the value stored in the relative address
                    `n` and store the result in the current data cell.
            * `|` - Bitwise OR the current data value and the value stored in the relative address
                    `n` and store the result in the current data cell.
            * `^` - Bitwise XOR the current data value and the value stored in the relative address
                    `n` and store the result in the current data cell.
            * `/` - Shift right the current data value by the value stored in the relative address
                    `n` and store the result in the current data cell.
            * `\` - Shift left the current data value by the value stored in the relative address
                    `n` and store the result in the current data cell.

            Note: `n` must be within the range INT_MIN to INT_MAX unless otherwise specified.

* `{x:n}` - A literal command, where `x` is the command and `n` is the literal value used for that
            command. The possible commands and their behaviors are shown below:

            * `>` - Increment the data pointer by the offset given (does NOT store the previous
                    address in the shadow data register).
            * `<` - Decrement the data pointer by the offset given (does NOT store the previous
                    address in the shadow data register).
            * `+` - Increment the data value by the literal value `n`.
            * `-` - Decrement the data value by the literal value `n`.
            * `.` - Write the literal value `n` to `stdout`. Note: `n` must be between DATA_MIN and
                    DATA_MAX.
            * `,` - Write the literal value `n` to the current data cell. Note: `n` must be between
                    DATA_MIN and DATA_MAX.
            * `[` - If the literal value `n` is zero, move the instruction pointer forward to one
                    after the matching `]` (not necessarily a literal instruction).
            * `]` - If the literal value `n` is non-zero, move the instruction pointer backward to
                    one after the matching `[` (not necessarily a literal instruction).
            * `&` - Bitwise AND the current data value and the literal value `n` and store the
                    result in the current data cell.
            * `|` - Bitwise OR the current data value and the literal value `n` and store the
                    result in the current data cell.
            * `^` - Bitwise XOR the current data value and the literal value `n` and store the
                    result in the current data cell.
            * `/` - Shift right the current data value by the literal value `n` and store the
                    result in the current data cell.
            * `\` - Shift left the current data value by the literal value `n` and store the
                    result in the current data cell.

            Note: `n` must be within the range UINT_MIN to UINT_MAX unless otherwise specified.

* `(@:id)` - Define the next instruction as identifier symbol `id`. Instructions may only be
             identified by a single identifier and identifiers may only be defined once.
* `(*:id)` - Jump the instruction pointer to the given identifier and store the previous
             instruction address in the shadow instruction register.
* `{{comment}}` - Anything wrapped in double curly braces (`{}`) is considered a comment and will
                  be ignored. This allows the use of command characters in comments. All
                  non-command characters outside of a comment are still ignored.