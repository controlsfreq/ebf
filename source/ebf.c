/* -*- mode: C; tab-width: 4; -*- */
/**
 * @file ebf.c
 *
 * @brief This file contains the implementation code for the Embedded Brainfuck (EBF) interpreter.
 *
 * @date 9/25/2014
 * @author Liam Bucci
 * @version 0.1.0
 *
 * @details Nothing here yet.
 *
 * @private
 */

/**
 * @addtogroup ebf
 *
 * @{
 */

// Include standard libraries
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Include EBF headers
#include <ebf.h>

// Private function declarations
static ebf_error_t init_(ebf_attr_t *attr, uint8_t *data_array, uint32_t data_array_length);
static ebf_error_t process_(ebf_chunk_t *chunk);
static ebf_error_t pause_(void);
static ebf_error_t unpause_(void);
static ebf_error_t reset_(void);
static uint32_t get_program_counter_(void);
static bool is_valid_(void);
static bool is_processing_(void);
static ebf_error_t clean_up_(void);

// Private member declaration
struct ebf_private_s
{
    ebf_attr_t attr_;
    uint8_t *data_array_;
    uint32_t data_array_length_;
    uint8_t *data_array_pointer_;
    uint32_t *loop_stack_;
    uint8_t loop_stack_height_;
    uint32_t program_counter_;
    ebf_chunk_t current_chunk_;
    bool processing_;
    volatile bool pause_requested_;
};
typedef struct ebf_private_s ebf_private_t;

// Global ebf object definition
ebf_t ebf = {
    .init = init_,
    .process = process_,
    .pause = pause_,
    .unpause = pause_,
    .reset = reset_,
    .get_program_counter = get_program_counter_,
    .is_valid = is_valid_,
    .is_processing = is_processing_,
    .clean_up = clean_up_
};

// Private function definitions
static ebf_error_t init_(ebf_attr_t *attr, uint8_t *data_array, uint32_t data_array_length)
{
    // Allocate private struct
    ebf.private = malloc(sizeof(ebf_private_t));
    if( ebf.private == NULL )
    {// Allocation failed
        // Clean up and return unsuccessfully
        ebf.clean_up();
        return EBF_E_ALLOC;
    }
    
    // Store attribute struct
    ((ebf_private_t *)(ebf.private))->attr_ = *attr;

    // Allocate loop stack
    ((ebf_private_t *)(ebf.private))->loop_stack_ = \
        malloc( (((ebf_private_t *)(ebf.private))->attr_.memory.max_loop_depth+1) * sizeof(uint32_t) );
    if( ((ebf_private_t *)(ebf.private))->loop_stack_ == NULL )
    {// Allocation failed
        // Clean up and return unsuccessfully
        ebf.clean_up();
        return EBF_E_ALLOC;
    }

    // Check data array length
    if( data_array_length == 0 )
    {// Invalid input
        // Clean up and return unsuccessfully
        ebf.clean_up();
        return EBF_E_INPUT;
    }

    // Determine whether to use users array or dynamically allocate one
    if( data_array == NULL )
    {// Dynamically allocate data array
        // Dynamically allocate and zero data array
        ((ebf_private_t *)(ebf.private))->data_array_ = \
            calloc( data_array_length, sizeof(uint8_t) );
        if( ((ebf_private_t *)(ebf.private))->data_array_ == NULL )
        {// Allocation failed
            // Clean up and return unsuccessfully
            ebf.clean_up();
            return EBF_E_ALLOC;
        }

        ((ebf_private_t *)(ebf.private))->data_array_length_ = data_array_length;
    }
    else
    {// Copy users array to private struct
        ((ebf_private_t *)(ebf.private))->data_array_ = data_array;
        ((ebf_private_t *)(ebf.private))->data_array_length_ = data_array_length;
    }

    // Initialize program counter
    ((ebf_private_t *)(ebf.private))->program_counter_ = 0;
    
    // Initialize chunk information
    ((ebf_private_t *)(ebf.private))->current_chunk_ = (ebf_chunk_t){NULL,0,0};

    // Initialize flags
    ((ebf_private_t *)(ebf.private))->processing_ = false;
    ((ebf_private_t *)(ebf.private))->pause_requested_ = false;

    return EBF_E_NONE;
}

static ebf_error_t process_(ebf_chunk_t *chunk)
{
    int8_t *cursor;
    ebf_chunk_t temp_chunk;
    
    // Check for a valid ebf object
    if( !ebf.is_valid() )
    {// Invalid ebf object
        // Return unsuccessfully
        return EBF_E_INVALID;
    }

    // Check if currently processing (don't allow two instantiations)
    if( ebf.is_processing() )
    {// Currently processing
        // Return unsuccessfully
        return EBF_E_WOULDBLOCK;
    }

    // Check for valid chunk
    if( chunk->instruction_array == NULL \
        || chunk->instruction_array_length == 0 )
    {// Chunk is invalid
        // Return unsuccessfully
        return EBF_E_INPUT;
    }

    // Copy valid chunk to private struct
    ((ebf_private_t *)(ebf.private))->current_chunk_ = *chunk;
    
    // Mark ebf object as processing
    ((ebf_private_t *)(ebf.private))->processing_ = true;
    
    // Start the next instruction if no pause has been requested
    while( !((ebf_private_t *)(ebf.private))->pause_requested_ )
    {
        // Check if the current instruction is outside of this chunk
        if( ((ebf_private_t *)(ebf.private))->program_counter_         \
            < ((ebf_private_t *)(ebf.private))->current_chunk_.starting_instruction \
            || ((ebf_private_t *)(ebf.private))->program_counter_       \
            > (((ebf_private_t *)(ebf.private))->current_chunk_.starting_instruction \
               + ((ebf_private_t *)(ebf.private))->current_chunk_.instruction_array_length) )
        {// Current instruction is not in this chunk
            // Check if continuous processing is configured
            if( ((ebf_private_t *)(ebf.private))->attr_.processing.continuous )
            {// Continuous processing is configured
                // Check for valid next() pointer
                if( ebf.next == NULL )
                {// Invalid pointer
                    //! @todo Handle error
                    ((ebf_private_t *)(ebf.private))->processing_ = false;
                    return EBF_E_UNKNOWN;
                }
                
                // Request next chunk
                temp_chunk = ebf.next( ((ebf_private_t *)(ebf.private))->program_counter_ );

                // Check for valid chunk
                if( temp_chunk.instruction_array == NULL \
                    || temp_chunk.instruction_array_length == 0 )
                {// Chunk is invalid
                    //! @todo handle error
                    ((ebf_private_t *)(ebf.private))->processing_ = false;
                    return EBF_E_UNKNOWN;
                }

                // Copy new chunk to current chunk
                ((ebf_private_t *)(ebf.private))->current_chunk_ = temp_chunk;
                
                // Continue looping
                continue;
            }
            else
            {// Continuous processing is not configured
                // Return successfully
                ((ebf_private_t *)(ebf.private))->processing_ = false;
                return EBF_E_NONE;
            }
        }
        else
        {// Current instruction is inside this chunk
            // Update the cursor
            cursor = ((ebf_private_t *)(ebf.private))->current_chunk_.instruction_array \
                + ( ((ebf_private_t *)(ebf.private))->program_counter_  \
                    - ((ebf_private_t *)(ebf.private))->current_chunk_.starting_instruction );

            // Parse current instruction
            switch( *cursor )
            {
            case '>':
                // Increment data pointer

                // Check if incrementing would go out of bounds
                if( ((ebf_private_t *)(ebf.private))->data_array_pointer_ \
                    >= ( ((ebf_private_t *)(ebf.private))->data_array_  \
                         + ((ebf_private_t *)(ebf.private))->data_array_length_ - 1 ) )
                {// Incrementing would go out of bounds
                    // Check if wrapping is configured
                    if( ((ebf_private_t *)(ebf.private))->attr_.interpreter.wrap_data_pointer )
                    {// Wrapping is configured
                        // Set data pointer to first item in array
                        ((ebf_private_t *)(ebf.private))->data_array_pointer_ \
                            = ((ebf_private_t *)(ebf.private))->data_array_;
                    }
                    else
                    {// Wrapping is not configured
                        // Data pointer remains at the end of the array
                    }
                }
                else
                {// Incrementing would not go out of bounds
                    // Increment data pointer
                    ((ebf_private_t *)(ebf.private))->data_array_pointer_++;
                }

                break;
            case '<':
                // Decrement data pointer

                // Check if decrementing would go out of bounds
                if( ((ebf_private_t *)(ebf.private))->data_array_pointer_ \
                    <= ((ebf_private_t *)(ebf.private))->data_array_ )
                {// Decrementing would go out of bounds
                    // Check if wrapping is configured
                    if( ((ebf_private_t *)(ebf.private))->attr_.interpreter.wrap_data_pointer )
                    {// Wrapping is configured
                        // Set data pointer to last item in array
                        ((ebf_private_t *)(ebf.private))->data_array_pointer_ \
                            = ( ((ebf_private_t *)(ebf.private))->data_array_ \
                                + ((ebf_private_t *)(ebf.private))->data_array_length_ - 1 );
                    }
                    else
                    {// Wrapping is not configured
                        // Data pointer remains at the beginning of the array
                    }
                }
                else
                {// Decrementing would not go out of bounds
                    // Decrement data pointer
                    ((ebf_private_t *)(ebf.private))->data_array_pointer_--;
                }

                break;
            case '+':
                // Increment data value

                ( *((ebf_private_t *)(ebf.private))->data_array_pointer_ )++;

                break;
            case '-':
                // Decrement data value

                ( *((ebf_private_t *)(ebf.private))->data_array_pointer_ )--;

                break;
            case '.':
                // Output current data value

                // Check for valid output function
                if( ebf.output != NULL )
                {// Assume output function is valid
                    ebf.output( *((ebf_private_t *)(ebf.private))->data_array_pointer_ );
                }
                else
                {// Output function is not valid
                    // Ignore the output instruction
                }

                break;
            case ',':
                // Input to current data pointer

                // Check for valid input function
                if( ebf.input != NULL )
                {// Assume input function is valid
                    *((ebf_private_t *)(ebf.private))->data_array_pointer_ = ebf.input();
                }
                else
                {// Input function is not valid
                    // Ignore the input instruction
                }

                break;
            case '[':
                // Start loop/jump instruction

                //! @todo Finish start loop/jump instruction

                break;
            case ']':
                // End loop/jump instruction

                //! @todo Finish end loop/jump instruction

                break;
            default:
                // Ignore any other characters
                break;
            }

            // Increment program counter
            ((ebf_private_t *)(ebf.private))->program_counter_++;
        }
    }

    // Pause was requested

    // Unset processing flag
    ((ebf_private_t *)(ebf.private))->processing_ = false;

    return EBF_E_NONE;
}

static ebf_error_t pause_(void)
{

}

static ebf_error_t unpause_(void)
{

}

static ebf_error_t reset_(void)
{

}

static uint32_t get_program_counter_(void)
{

    return 0;
}

static bool is_valid_(void)
{

    return false;
}

static bool is_processing_(void)
{

    return false;
}

static ebf_error_t clean_up_(void)
{

}

/**
 * @}
 */ // End group ebf
