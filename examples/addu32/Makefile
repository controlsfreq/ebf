##
# Makefile for EBF examples.
#
# Author:    Liam Bucci
# Date:      4/2/2017
# Copyright: Copyright (c) 2017, Liam Bucci.
#
#            This file is part of Embedded Brain Fuck (EBF).
#
#            EBF is free software: you can redistribute it and/or modify it under the terms of
#            the GNU General Public License as published by the Free Software Foundation, either
#            version 3 of the License, or (at your option) any later version.
#
#            EBF is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#            without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#            PURPOSE.  See the GNU General Public License for more details.
#
#            You should have received a copy of the GNU General Public License along with EBF.
#            If not, see <http://www.gnu.org/licenses/>.
##

# Target
TARGET=helloworld

# EBF File
EBF_SOURCE=$(TARGET).ebf

# Directories
EBF_ROOT=../..

# C Compiler
CC=gcc

# C Flags
CFLAGS=-Wall -Werror

# Sources
SOURCES=hooks.c
HEADERS=hooks.h
GEN_SOURCES=main.c
GEN_HEADERS=ebf.h

# Objects
OBJECTS=$(GEN_SOURCES:.c=.o) $(SOURCES:.c=.o)

# Recipes ====================================================================

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET)

$(GEN_SOURCES) $(GEN_HEADERS): $(EBF_SOURCE)
	python3 $(EBF_ROOT)/ebf/ebf.py $<

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

run: $(TARGET)
	./$(TARGET)

.PHONY: clean
clean:
	rm -rf $(OBJECTS)
	rm -rf $(GEN_SOURCES) $(GEN_HEADERS)
	rm -rf $(TARGET)
