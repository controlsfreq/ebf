# -*- mode: Makefile; tab-width: 4; -*- #

### Commands ###
MKDIR = mkdir -p
RM    = rm -f
CC    = gcc
AR    = ar

### Flags ###
CC_FLAGS = -D EBF_MAJOR_VERSION=$(MAJOR_VERSION) -D EBF_MINOR_VERSION=$(MINOR_VERSION) -D EBF_PATCH_VERSION=$(PATCH_VERSION)
AR_FLAGS = rcs

### Directories ###
BUILD_DIR   = ./build
DIST_DIR    = ./dist
SOURCE_DIR  = ./source
INCLUDE_DIR = ./include

### Files ###
SRC_FILES = ebf.c
TARGET = ebf.a

all: build

build: $(BUILD_DIR)/ebf.o
	@$(MKDIR) $(DIST_DIR)
	$(AR) $(AR_FLAGS) $(DIST_DIR)/$(TARGET) $(BUILD_DIR)/ebf.o

clean:
	@$(RM) $(BUILD_DIR)/*.o

$(BUILD_DIR)/ebf.o: $(SOURCE_DIR)/ebf.c $(INCLUDE_DIR)/ebf.h
	@$(MKDIR) $(BUILD_DIR)
	$(CC) $(CC_FLAGS) -I$(INCLUDE_DIR) -c $(SOURCE_DIR)/ebf.c -o $(BUILD_DIR)/ebf.o

include version.mk

.PHONY: clean