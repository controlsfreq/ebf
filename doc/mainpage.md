# Extended/Embedded Brain Fuck

## Introduction

Extended or Embedded Brain Fuck (or EBF) is an extension of the Brain Fuck language to allow easier
usage on embedded systems. EBF adds a number of extended commands that make writing to and from
registers and various places in memory simpler. It also provides mechanisms for single depth
function calls, literal writes into data memory, and the ability to override the `_stdin` and
`_stdout` operations defined in classic Brain Fuck.

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
* `.` - Copy value at data pointer to `_stdout`. **Note:** `_stdout` must be defined at
        compile-time.
* `,` - Copy value from `_stdin` to current data pointer. **Note:** `_stdin` must be defined at
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

<table>
    <tr>
        <th rowspan=2></th>
        <th colspan=2>Location</th>
        <th colspan=2>Value</th>
    </tr>
    <tr>
        <th>Direct</th>
        <th>Indirect</th>
        <th>Direct</th>
        <th>Indirect</th>
    </tr>
    <tr>
        <th>Absolute</th>
        <td><tt>(x@a)</tt></td>
        <td><tt>(x@*a)</tt></td>
        <td><tt>(x#n)</tt></td>
        <td><tt>(x#*n)</tt></td>
    </tr>
    <tr>
        <th>Relative</th>
        <td><tt>(x@:n)</tt></td>
        <td><tt>(x@:*n)</tt></td>
        <td><tt>(x#:n)</tt></td>
        <td><tt>(x#:*n)</tt></td>
    </tr>
</table>

<table>
    <tr>
        <th>Instruction</th>
        <th>Action Type</th>
        <th>Positioning</th>
        <th>Indirection</th>
        <th>Command</th>
        <th>Equivalent C++</th>
        <th>Behavior</th>
    </tr>

    <tr>
        <th rowspan=8>&gt;</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(&gt;@n)</tt></td>
        <td><tt>DP = n</tt></td>
        <td>Set data pointer to <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&gt;@*n)</tt></td>
        <td><tt>DP = *n</tt></td>
        <td>Set data pointer to address stored in cell <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(&gt;@:n)</tt></td>
        <td><tt>DP += n</tt></td>
        <td>Move data pointer right by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&gt;@:*n)</tt></td>
        <td><tt>DP += *(DP + n)</tt></td>
        <td>Move data pointer right by value stored in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(&gt;#n)</tt></td>
        <td><tt>DP = n</tt></td>
        <td>Set data pointer to <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&gt;#*n)</tt></td>
        <td><tt>DP = *n</tt></td>
        <td>Set data pointer to address stored in cell <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(&gt;#:n)</tt></td>
        <td><tt>DP += n</tt></td>
        <td>Move data pointer right by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&gt;#:*n)</tt></td>
        <td><tt>DP += *(DP + n)</tt></td>
        <td>Move data pointer right by value stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>&lt;</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(&lt;@n)</tt></td>
        <td><tt>DP = n</tt></td>
        <td>Set data pointer to <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&lt;@*n)</tt></td>
        <td><tt>DP = *n</tt></td>
        <td>Set data pointer to address stored in cell <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(&lt;@:n)</tt></td>
        <td><tt>DP -= n</tt></td>
        <td>Move data pointer left by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&lt;@:*n)</tt></td>
        <td><tt>DP -= *(DP + n)</tt></td>
        <td>Move data pointer left by value stored in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(&lt;#n)</tt></td>
        <td><tt>DP = n</tt></td>
        <td>Set data pointer to <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&lt;#*n)</tt></td>
        <td><tt>DP = *n</tt></td>
        <td>Set data pointer to address stored in cell <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(&lt;#:n)</tt></td>
        <td><tt>DP -= n</tt></td>
        <td>Move data pointer left by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&lt;#:*n)</tt></td>
        <td><tt>DP -= *(DP + n)</tt></td>
        <td>Move data pointer left by value stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>+</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(+@n)</tt></td>
        <td><tt>*n += 1</tt></td>
        <td>Increment value at cell <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(+@*n)</tt></td>
        <td><tt>**n += 1</tt></td>
        <td>Increment value at cell pointed to by address stored in <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(+@:n)</tt></td>
        <td><tt>*(DP + n) += 1</tt></td>
        <td>Increment value at cell in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(+@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) += 1</tt></td>
        <td>Increment value at cell pointed to by relative address stored in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(+#n)</tt></td>
        <td><tt>*DP += n</tt></td>
        <td>Increment value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(+#*n)</tt></td>
        <td><tt>*DP += *n</tt></td>
        <td>Increment value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(+#:n)</tt></td>
        <td><tt>*DP += *(DP + n)</tt></td>
        <td>Increment value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(+#:*n)</tt></td>
        <td><tt>*DP += *(DP + *(DP + n))</tt></td>
        <td>Increment value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>-</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(-@n)</tt></td>
        <td><tt>*n -= 1</tt></td>
        <td>Decrement value at cell <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(-@*n)</tt></td>
        <td><tt>**n -= 1</tt></td>
        <td>Decrement value at cell pointed to by address stored in <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(-@:n)</tt></td>
        <td><tt>*(DP + n) -= 1</tt></td>
        <td>Decrement value at cell in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(-@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) -= 1</tt></td>
        <td>Decrement value at cell pointed to by relative address stored in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(-#n)</tt></td>
        <td><tt>*DP -= n</tt></td>
        <td>Decrement value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(-#*n)</tt></td>
        <td><tt>*DP -= *n</tt></td>
        <td>Decrement value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(-#:n)</tt></td>
        <td><tt>*DP -= *(DP + n)</tt></td>
        <td>Decrement value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(-#:*n)</tt></td>
        <td><tt>*DP -= *(DP + *(DP + n))</tt></td>
        <td>Decrement value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>.</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(.@n)</tt></td>
        <td><tt>*n = *DP</tt></td>
        <td>Set value at cell <tt>n</tt> to current cell value</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(.@*n)</tt></td>
        <td><tt>**n = *DP</tt></td>
        <td>Set value at cell pointed to by address stored in <tt>n</tt> to current cell value</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(.@:n)</tt></td>
        <td><tt>*(DP + n) = *DP</tt></td>
        <td>Set value at cell in relative address <tt>n</tt> to current cell value</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(.@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) = *DP</tt></td>
        <td>Set value at cell pointed to by relative address stored in relative address <tt>n</tt> to current cell value</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(.#n)</tt></td>
        <td><tt>_stdout &lt;&lt; n</tt></td>
        <td>Write <tt>n</tt> to _stdout</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(.#*n)</tt></td>
        <td><tt>_stdout &lt;&lt; *n</tt></td>
        <td>Write value at address <tt>n</tt> to _stdout</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(.#:n)</tt></td>
        <td><tt>_stdout &lt;&lt; *(DP + n)</tt></td>
        <td>Write value at relative address <tt>n</tt> to _stdout</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(.#:*n)</tt></td>
        <td><tt>_stdout &lt;&lt; *(DP + *(DP + n))</tt></td>
        <td>Write value at relative address stored in relative address <tt>n</tt> to _stdout</td>
    </tr>

    <tr>
        <th rowspan=8>,</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(,@n)</tt></td>
        <td><tt>_stdin &gt;&gt; *n</tt></td>
        <td>Set value at cell <tt>n</tt> to next character in _stdin</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(,@*n)</tt></td>
        <td><tt>_stdin &gt;&gt; **n</tt></td>
        <td>Set value at cell pointed to by address stored in <tt>n</tt> to next character in _stdin</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(,@:n)</tt></td>
        <td><tt>_stdin &gt;&gt; *(DP + n)</tt></td>
        <td>Set value at cell in relative address <tt>n</tt> to next character in _stdin</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(,@:*n)</tt></td>
        <td><tt>_stdin &gt;&gt; *(DP + *(DP + n))</tt></td>
        <td>Set value at cell pointed to by relative address stored in relative address <tt>n</tt> to next character in _stdin</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(,#n)</tt></td>
        <td><tt>*DP = n</tt></td>
        <td>Write <tt>n</tt> to current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(,#*n)</tt></td>
        <td><tt>*DP = *n</tt></td>
        <td>Write value at address <tt>n</tt> to current cell</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(,#:n)</tt></td>
        <td><tt>*DP = *(DP + n)</tt></td>
        <td>Write value at relative address <tt>n</tt> to current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(,#:*n)</tt></td>
        <td><tt>*DP = *(DP + *(DP + n))</tt></td>
        <td>Write value at relative address stored in relative address <tt>n</tt> to current cell</td>
    </tr>

    <tr>
        <th rowspan=8>[</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>([@n)</tt></td>
        <td><tt>while( *n != 0 )</tt></td>
        <td>Continue while value at cell <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>([@*n)</tt></td>
        <td><tt>while( **n != 0 )</tt></td>
        <td>Continue while value at cell pointed to by address stored in <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>([@:n)</tt></td>
        <td><tt>while( *(DP + n) != 0 )</tt></td>
        <td>Continue while value at cell in relative address <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>([@:*n)</tt></td>
        <td><tt>while( *(DP + *(DP + n)) != 0 )</tt></td>
        <td>Continue while value at cell pointed to by relative address stored in relative address <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>([#n)</tt></td>
        <td><tt>while( *DP != n )</tt></td>
        <td>Continue while current cell is not equal to <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>([#*n)</tt></td>
        <td><tt>while( *DP != *n )</tt></td>
        <td>Continue while current cell is not equal to value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>([#:n)</tt></td>
        <td><tt>while( *DP != *(DP + n) )</tt></td>
        <td>Continue while current cell is not equal to value at relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>([#:*n)</tt></td>
        <td><tt>while( *DP != *(DP + *(DP + n)) )</tt></td>
        <td>Continue while current cell is not equal to value at relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>]</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(]@n)</tt></td>
        <td><tt>do { } while( *n != 0 )</tt></td>
        <td>Continue while value at cell <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(]@*n)</tt></td>
        <td><tt>do { } while( **n != 0 )</tt></td>
        <td>Continue while value at cell pointed to by address stored in <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(]@:n)</tt></td>
        <td><tt>do { } while( *(DP + n) != 0 )</tt></td>
        <td>Continue while value at cell in relative address <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(]@:*n)</tt></td>
        <td><tt>do { } while( *(DP + *(DP + n)) != 0 )</tt></td>
        <td>Continue while value at cell pointed to by relative address stored in relative address <tt>n</tt> is non-zero</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(]#n)</tt></td>
        <td><tt>do { } while( *DP != n )</tt></td>
        <td>Continue while current cell is not equal to <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(]#*n)</tt></td>
        <td><tt>do { } while( *DP != *n )</tt></td>
        <td>Continue while current cell is not equal to value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(]#:n)</tt></td>
        <td><tt>do { } while( *DP != *(DP + n) )</tt></td>
        <td>Continue while current cell is not equal to value at relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(]#:*n)</tt></td>
        <td><tt>do { } while( *DP != *(DP + *(DP + n)) )</tt></td>
        <td>Continue while current cell is not equal to value at relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>&amp;</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(&amp;@n)</tt></td>
        <td><tt>*n &amp;= *DP</tt></td>
        <td>Bitwise AND the value at cell <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&amp;@*n)</tt></td>
        <td><tt>**n &amp;= *DP</tt></td>
        <td>Bitwise AND the value at cell pointed to by address stored in <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(&amp;@:n)</tt></td>
        <td><tt>*(DP + n) &amp;= *DP</tt></td>
        <td>Bitwise AND the value at cell in relative address <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&amp;@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) &amp;= *DP</tt></td>
        <td>Bitwise AND the value at cell pointed to by relative address stored in relative address <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(&amp;#n)</tt></td>
        <td><tt>*DP &amp;= n</tt></td>
        <td>Bitwise AND the value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&amp;#*n)</tt></td>
        <td><tt>*DP &amp;= *n</tt></td>
        <td>Bitwise AND the value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(&amp;#:n)</tt></td>
        <td><tt>*DP &amp;= *(DP + n)</tt></td>
        <td>Bitwise AND the value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(&amp;#:*n)</tt></td>
        <td><tt>*DP &amp;= *(DP + *(DP + n))</tt></td>
        <td>Bitwise AND the value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>|</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(|@n)</tt></td>
        <td><tt>*n |= *DP</tt></td>
        <td>Bitwise OR the value at cell <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(|@*n)</tt></td>
        <td><tt>**n |= *DP</tt></td>
        <td>Bitwise OR the value at cell pointed to by address stored in <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(|@:n)</tt></td>
        <td><tt>*(DP + n) |= *DP</tt></td>
        <td>Bitwise OR the value at cell in relative address <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(|@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) |= *DP</tt></td>
        <td>Bitwise OR the value at cell pointed to by relative address stored in relative address <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(|#n)</tt></td>
        <td><tt>*DP |= n</tt></td>
        <td>Bitwise OR the value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(|#*n)</tt></td>
        <td><tt>*DP |= *n</tt></td>
        <td>Bitwise OR the value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(|#:n)</tt></td>
        <td><tt>*DP |= *(DP + n)</tt></td>
        <td>Bitwise OR the value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(|#:*n)</tt></td>
        <td><tt>*DP |= *(DP + *(DP + n))</tt></td>
        <td>Bitwise OR the value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>^</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(^@n)</tt></td>
        <td><tt>*n ^= *DP</tt></td>
        <td>Bitwise XOR the value at cell <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(^@*n)</tt></td>
        <td><tt>**n ^= *DP</tt></td>
        <td>Bitwise XOR the value at cell pointed to by address stored in <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(^@:n)</tt></td>
        <td><tt>*(DP + n) ^= *DP</tt></td>
        <td>Bitwise XOR the value at cell in relative address <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(^@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) ^= *DP</tt></td>
        <td>Bitwise XOR the value at cell pointed to by relative address stored in relative address <tt>n</tt> with the current cell</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(^#n)</tt></td>
        <td><tt>*DP ^= n</tt></td>
        <td>Bitwise XOR the value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(^#*n)</tt></td>
        <td><tt>*DP ^= *n</tt></td>
        <td>Bitwise XOR the value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(^#:n)</tt></td>
        <td><tt>*DP ^= *(DP + n)</tt></td>
        <td>Bitwise XOR the value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(^#:*n)</tt></td>
        <td><tt>*DP ^= *(DP + *(DP + n))</tt></td>
        <td>Bitwise XOR the value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>/</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(/@n)</tt></td>
        <td><tt>*n &gt;&gt;= *DP</tt></td>
        <td>Bitwise right shift the value at cell <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(/@*n)</tt></td>
        <td><tt>**n &gt;&gt;= *DP</tt></td>
        <td>Bitwise right shift the value at cell pointed to by address stored in <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(/@:n)</tt></td>
        <td><tt>*(DP + n) &gt;&gt;= *DP</tt></td>
        <td>Bitwise right shift the value at cell in relative address <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(/@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) &gt;&gt;= *DP</tt></td>
        <td>Bitwise right shift the value at cell pointed to by relative address stored in relative address <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(/#n)</tt></td>
        <td><tt>*DP &gt;&gt;= n</tt></td>
        <td>Bitwise right shift the value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(/#*n)</tt></td>
        <td><tt>*DP &gt;&gt;= *n</tt></td>
        <td>Bitwise right shift the value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(/#:n)</tt></td>
        <td><tt>*DP &gt;&gt;= *(DP + n)</tt></td>
        <td>Bitwise right shift the value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(/#:*n)</tt></td>
        <td><tt>*DP &gt;&gt;= *(DP + *(DP + n))</tt></td>
        <td>Bitwise right shift the value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th rowspan=8>\</th>
        <th rowspan=4>Location</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(\@n)</tt></td>
        <td><tt>*n &lt;&lt;= *DP</tt></td>
        <td>Bitwise left shift the value at cell <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(\@*n)</tt></td>
        <td><tt>**n &lt;&lt;= *DP</tt></td>
        <td>Bitwise left shift the value at cell pointed to by address stored in <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(\@:n)</tt></td>
        <td><tt>*(DP + n) &lt;&lt;= *DP</tt></td>
        <td>Bitwise left shift the value at cell in relative address <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(\@:*n)</tt></td>
        <td><tt>*(DP + *(DP + n)) &lt;&lt;= *DP</tt></td>
        <td>Bitwise left shift the value at cell pointed to by relative address stored in relative address <tt>n</tt> with the value in the current cell</td>
    </tr>
    <tr>
        <th rowspan=4>Value</th>
        <th rowspan=2>Absolute</th>
        <th>Direct</th>
        <td><tt>(\#n)</tt></td>
        <td><tt>*DP &lt;&lt;= n</tt></td>
        <td>Bitwise left shift the value at current cell by <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(\#*n)</tt></td>
        <td><tt>*DP &lt;&lt;= *n</tt></td>
        <td>Bitwise left shift the value at current cell by value at address <tt>n</tt></td>
    </tr>
    <tr>
        <th rowspan=2>Relative</th>
        <th>Direct</th>
        <td><tt>(\#:n)</tt></td>
        <td><tt>*DP &lt;&lt;= *(DP + n)</tt></td>
        <td>Bitwise left shift the value at current cell by value in relative address <tt>n</tt></td>
    </tr>
    <tr>
        <th>Indirect</th>
        <td><tt>(\#:*n)</tt></td>
        <td><tt>*DP &lt;&lt;= *(DP + *(DP + n))</tt></td>
        <td>Bitwise left shift the value at current cell by value in relative address stored in relative address <tt>n</tt></td>
    </tr>

    <tr>
        <th>Notes</th>
        <td colspan=6>
            <ul>
                <li>Data Pointer (DP) is a pointer to the current cell in the data array.</li>
                <li>Shadow Data Pointer (SDP) is a pointer that stores the address of another cell in the data array (may hold any addressable value).</li>
                <li>_stdout is either an address or a writable file. It must be defined at compile-time.</li>
                <li>_stdin is either an address or a readable file. It must be defined at compile-time.</li>
            </ul>
        </td>
    </tr>

</table>

<table>
    <tr>
        <th>Instruction</th>
        <th>Command</th>
        <th>Equivalent C++</th>
        <th>Behavior</th>
    </tr>

    <tr>
        <th>%</th>
        <td><tt>%</tt></td>
        <td><tt>size_t temp = DP; DP = SDP; SDP = temp</tt></td>
        <td>Swap the data pointer and the shadow data pointer</td>
    </tr>

    <tr>
        <th>@</th>
        <td><tt>(@id)</tt></td>
        <td><tt>id:</tt></td>
        <td>Define the next instruction using the identifier <tt>id</tt></td>
    </tr>

    <tr>
        <th rowspan=3>!</th>
        <td><tt>(!id)</tt></td>
        <td><tt>goto id</tt></td>
        <td>Jump (without return) to the instruction identified by <tt>id</tt></td>
    </tr>
    <tr>
        <td><tt>(!:id)</tt></td>
        <td><tt>goto id; return_point:</tt></td>
        <td>Jump (with return) to the instruction identified by <tt>id</tt></td>
    </tr>
    <tr>
        <td><tt>!</tt></td>
        <td><tt>goto return_point</tt></td>
        <td>Jump to most recent return point</td>
    </tr>

    <tr>
        <th>{{}}</th>
        <td><tt>{{comment}}</tt></td>
        <td><tt>/* comment */</tt></td>
        <td>Defines a block comment</td>
    </tr>
</table>

* `(@id)` - Define the next instruction as identifier symbol `id`. Instructions may only be
             identified by a single identifier and identifiers may only be defined once.
* `(*id)` - Jump the instruction pointer to the given identifier and store the previous
             instruction address in the shadow instruction register.
* `{{comment}}` - Anything wrapped in double curly braces is considered a comment and will
                  be ignored. This allows the use of command characters in comments. All
                  non-command characters outside of a comment are still ignored.