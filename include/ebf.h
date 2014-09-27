/* -*- mode: C; tab-width: 4; -*- */
/**
 * @file ebf.h
 *
 * @brief This file contains the interface declarations for the Embedded Brainfuck (EBF)
 * interpreter.
 *
 * @date 8/20/2014
 * @author Liam Bucci
 * @version 0.1.0
 *
 * @details Nothing here yet.
 *
 * @public
 */

/**
 * @addtogroup ebf
 *
 * @{
 */

// Include guard
#ifndef EBF_H_
#define EBF_H_

// Include standard libraries
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>


/**
 * @brief This object contains a chunk of Brainfuck instructions.
 *
 * @details The ebf object assumes that not all Brainfuck instructions may be available at once.
 * Therefore, it allows the user to feed it chunks of instructions at a time. In the worst case a
 * user may feed a single instruction at a time. This object represents a chunk of instructions.
 *
 * @public
 */
struct ebf_chunk_s
{
    int8_t *instruction_array;
    uint32_t starting_instruction;
    uint32_t instruction_array_length;
};
typedef struct ebf_chunk_s ebf_chunk_t;

/**
 * @brief The attribute object contains settings and configurations for the ebf object.
 *
 * @details The ebf object's workings may be modified by changing different settings during
 * initialization. The attribute object contains those settings.
 *
 * EOF: End of file character; marks the end of the instructions and stops the interpreter.
 * Processing: Settings related to how the interpreter processes instructions.
 * - Continuous:
 * -- Enabled: When the end of a chunk is reached the next() function will be called and the user is
 * expected to supply the next chunk.
 * -- Disabled: When the end of a chunk is reached the interpreter will stop and return control to
 * the calling function. The start() function may be called with the next chunk to resume
 * processing.
 * Memory: Settings related to memory usage.
 * - Max Loop Depth: The maximum number minus 1 of simultaneous loops that may be ongoing. Whenever
 * a Brainfuck open bracket is encountered a loop starts. This value equates to the size of the
 * stack which stores the locations of all the loops. May be any number from 0-255. A value of 0
 * means a maximum loop depth of one and a value of 255 is a maximum loop depth of 256. Keep in mind
 * each location is stored as a 32-bit integer.
 *
 * @public
 */
struct ebf_attr_s
{
    struct
    {
        int8_t eof;
        bool wrap_data_pointer;
    } interpreter;
    
    struct
    {
        bool continuous; 
    } processing;
    
    struct
    {
        uint8_t max_loops;
    } memory;
};
typedef struct ebf_attr_s ebf_attr_t;


/**
 * @brief This enumeration defines all the valid error codes that may be returned by an EBF
 * function.
 *
 * @details Nothing here yet.
 *
 * @public
 */
enum ebf_error_e
{
    EBF_E_NONE       = 0,
    EBF_E_INVALID    = -1,
    EBF_E_ALLOC      = -2,
    EBF_E_INPUT      = -3,
    EBF_E_WOULDBLOCK = -4,
    EBF_E_LOOPMEM    = -5,
    EBF_E_PARSING    = -6,
    EBF_E_UNKNOWN    = INT8_MIN
};
typedef enum ebf_error_e ebf_error_t;


// Pre-declaration of ebf typedef
struct ebf_s;
typedef struct ebf_s ebf_t;

/**
 * @brief The ebf object represents the interpreter and stores it's state and pointers to all of
 * it's public functions.
 *
 * @details There may only be one ebf object within each project. The object is declared as public
 * and defined in the ebf.c file. This object is the assumed target of all ebf functions.
 *
 * @public
 */
struct ebf_s
{
    // Public members

    // Public user functions
    /**
     * @brief The user supplied function called when an output instruction is reached.
     *
     * @details This function must be supplied by the user. It must take a char as input and
     * generally will output that character by some visible means (e.g. UART, LCD, etc). The
     * function will be called whenever the interpreter reaches an output instruction in the
     * Brainfuck code. The output character will be the current data value under the data
     * pointer.
     *
     * @public
     */
    void (* output)(int8_t output);

    /**
     * @brief The user supplied function called when an input instruction is reached.
     *
     * @details This function must be supplied by the user. It must return a char which is
     * generally taken from some user input (i.e. UART, keypad, etc). The function will be called
     * whenever the interpreter reaches an input instruction in the Brainfuck code. The character
     * returned by this function will be stored in the currently pointed to data position.
     *
     * @public
     */
    int8_t (* input)(void);

    /**
     * @brief The user supplied function called when more instructions are needed.
     *
     * @details The ebf object assumes that not all Brainfuck instructions may be available at once.
     * Therefore, it allows the user to feed it chunks of instructions at a time. In the worst case
     * a user may feed a single instruction at a time. This function is called when the interpreter
     * needs the next chunk of instructions. It provides the program counter (i.e. a "pointer" to
     * the instruction which it needs next) and expects a chunk of instructions starting with the
     * instruction specified by that program counter.
     *
     * @public
     */
    ebf_chunk_t (* next)(uint32_t program_counter);
    
    // Public EBF functions
    /**
     * @brief The init function initializes the ebf object to a known starting state.
     *
     * @details The init function sets up all the state variables for the ebf interpreter. The
     * attribute parameter contains settings and configurations for the ebf object. The function
     * also takes as a parameter a pointer to the data array where all the Brainfuck data will be
     * stored.
     *
     * @public
     */
    ebf_error_t (* const init)(ebf_attr_t *attr, uint8_t *data_array, uint32_t data_array_length);

    /**
     * @brief Starts processing of the given chunk of instructions.
     *
     * User may call this function to start the next chunk if continuous processing is not enabled.
     */
    ebf_error_t (* const process)(ebf_chunk_t *chunk);
    ebf_error_t (* const pause)(void);
    ebf_error_t (* const unpause)(void);
    // Zeros out data array, user may reinitialize the data_array pointer outside of ebf
    ebf_error_t (* const reset)(void);
    uint32_t (* const get_program_counter)(void);
    bool (* const is_valid)(void);
    bool (* const is_processing)(void);
    ebf_error_t (* const clean_up)(void);
    
    // Private members
    void *private;
};

// Declaration of global ebf object
extern ebf_t ebf;


// End include guard
#endif

/**
 * @}
 */ // End group ebf
