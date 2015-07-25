/* -*- mode: C; tab-width: 4; -*- */
/**
 * @file   ebf.c
 * @brief  This file contains the implementation code for the Embedded Brainfuck (EBF) interpreter.
 * @date   2014-09-25
 * @author Liam Bucci
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

/* Internal Variables =============================================================================================== */

static const char* EBF_VERSION_STRING = "EBF_MAJOR_VERSION.EBF_MINOR_VERSION.EBF_PATCH_VERSION";


// Public function implementation declarations
static ebf_error_t init_(ebf_attr_t *attr, uint8_t *data_array, uint32_t data_array_length);
static ebf_error_t process_(ebf_chunk_t *chunk);
static ebf_error_t pause_(void);
static ebf_error_t unpause_(void);
static ebf_error_t reset_(void);
static uint32_t get_program_counter_(void);
static bool is_valid_(void);
static bool is_processing_(void);
static ebf_error_t clean_up_(void);

// Private function declarations
static ebf_error_t build_loop_hash_table_(void);

// Private member declaration
struct ebf_private_s
{
    ebf_attr_t attr_;
    uint8_t *data_array_;
    uint32_t data_array_length_;
    uint8_t *data_pointer_;
    uint32_t *loop_hash_table_start_;
    uint32_t *loop_hash_table_end_;
    uint32_t *current_loop_;
    uint32_t *next_loop_start_entry_;
    uint32_t *next_loop_end_entry_;
    uint8_t loop_stack_height_;
    uint32_t program_counter_;
    ebf_chunk_t current_chunk_;
    bool is_processing_;
    volatile bool is_pause_requested_;
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

    // Set up loop hash table
    // Treat special case of max_loop_depth = 0
    if( ((ebf_private_t *)(ebf.private))->attr_.memory.max_loops == 0 )
    {// No loops allowed
        // Set loop hash table pointers to NULL
        ((ebf_private_t *)(ebf.private))->loop_hash_table_start_ = NULL;
        ((ebf_private_t *)(ebf.private))->loop_hash_table_end_ = NULL;
        ((ebf_private_t *)(ebf.private))->current_loop_ = NULL;
        ((ebf_private_t *)(ebf.private))->next_loop_start_entry_ = NULL;
        ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ = NULL;
    }
    else
    {// Loops are allowed
        // Allocate loop hash table
        ((ebf_private_t *)(ebf.private))->loop_hash_table_start_ =      \
            calloc( (((ebf_private_t *)(ebf.private))->attr_.memory.max_loops) * 2, sizeof(uint32_t) );
        if( ((ebf_private_t *)(ebf.private))->loop_hash_table_start_ == NULL )
        {// Allocation failed
            // Clean up and return unsuccessfully
            ebf.clean_up();
            return EBF_E_ALLOC;
        }

        // Set up loop hash table pointers
        // Assign pointer to end of hash table
        ((ebf_private_t *)(ebf.private))->loop_hash_table_end_ \
            = ((ebf_private_t *)(ebf.private))->loop_hash_table_start_ \
            + ( ((ebf_private_t *)(ebf.private))->attr_.memory.max_loops * 2 );
        
        // Set current loop pointer to NULL (no current loop)
        ((ebf_private_t *)(ebf.private))->current_loop_ = NULL;
        // Set next loop start entry to first entry (first loop start)
        ((ebf_private_t *)(ebf.private))->next_loop_start_entry_ \
            = ((ebf_private_t *)(ebf.private))->loop_hash_table_start_;
        // Set next loop end entry to NULL (no loops started)
        ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ = NULL;
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
    ((ebf_private_t *)(ebf.private))->is_processing_ = false;
    ((ebf_private_t *)(ebf.private))->is_pause_requested_ = false;

    // Build the loop hash table (or return any errors)
    return build_loop_hash_table();
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
    ((ebf_private_t *)(ebf.private))->is_processing_ = true;
    
    // Start the next instruction if no pause has been requested
    while( !((ebf_private_t *)(ebf.private))->is_pause_requested_ )
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
                    ((ebf_private_t *)(ebf.private))->is_processing_ = false;
                    return EBF_E_UNKNOWN;
                }
                
                // Request next chunk
                temp_chunk = ebf.next( ((ebf_private_t *)(ebf.private))->program_counter_ );

                // Check for valid chunk
                if( temp_chunk.instruction_array == NULL \
                    || temp_chunk.instruction_array_length == 0 )
                {// Chunk is invalid
                    //! @todo handle error
                    ((ebf_private_t *)(ebf.private))->is_processing_ = false;
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
                ((ebf_private_t *)(ebf.private))->is_processing_ = false;
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
                if( ((ebf_private_t *)(ebf.private))->data_pointer_ \
                    >= ( ((ebf_private_t *)(ebf.private))->data_array_  \
                         + ((ebf_private_t *)(ebf.private))->data_array_length_ - 1 ) )
                {// Incrementing would go out of bounds
                    // Check if wrapping is configured
                    if( ((ebf_private_t *)(ebf.private))->attr_.interpreter.wrap_data_pointer )
                    {// Wrapping is configured
                        // Set data pointer to first item in array
                        ((ebf_private_t *)(ebf.private))->data_pointer_ \
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
                    ((ebf_private_t *)(ebf.private))->data_pointer_++;
                }

                break;
            case '<':
                // Decrement data pointer

                // Check if decrementing would go out of bounds
                if( ((ebf_private_t *)(ebf.private))->data_pointer_ \
                    <= ((ebf_private_t *)(ebf.private))->data_array_ )
                {// Decrementing would go out of bounds
                    // Check if wrapping is configured
                    if( ((ebf_private_t *)(ebf.private))->attr_.interpreter.wrap_data_pointer )
                    {// Wrapping is configured
                        // Set data pointer to last item in array
                        ((ebf_private_t *)(ebf.private))->data_pointer_ \
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
                    ((ebf_private_t *)(ebf.private))->data_pointer_--;
                }

                break;
            case '+':
                // Increment data value

                ( *((ebf_private_t *)(ebf.private))->data_pointer_ )++;

                break;
            case '-':
                // Decrement data value

                ( *((ebf_private_t *)(ebf.private))->data_pointer_ )--;

                break;
            case '.':
                // Output current data value

                // Check for valid output function
                if( ebf.output != NULL )
                {// Assume output function is valid
                    ebf.output( *((ebf_private_t *)(ebf.private))->data_pointer_ );
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
                    *((ebf_private_t *)(ebf.private))->data_pointer_ = ebf.input();
                }
                else
                {// Input function is not valid
                    // Ignore the input instruction
                }

                break;
            case '[':
                // Start loop/jump instruction

                // Check if looping is enabled
                if( ((ebf_private_t *)(ebf.private))->attr_.memory.max_loops == 0 )
                {// Looping is disabled
                    //! @todo Return to known state
                    return EBF_E_LOOPMEM;
                }

                // Move to next entry in loop hash table
                // Check if we are currently looping
                if( ((ebf_private_t *)(ebf.private))->current_loop_ == NULL )
                {// No current loop
                    // Set the current loop to the first entry in the hash table
                    ((ebf_private_t *)(ebf.private))->current_loop_     \
                        = ((ebf_private_t *)(ebf.private))->loop_hash_table_start_;
                }
                else
                {// Currently in a loop
                    // Move to the next loop in the hash table
                    ((ebf_private_t *)(ebf.private))->current_loop_ += 2;
                }
                
                // Check if current loop exists in hash table
                if( ((ebf_private_t *)(ebf.private))->current_loop_     \
                    > ((ebf_private_t *)(ebf.private))->loop_hash_table_end_ )
                {// Current loop doesn't exist in hash table
                    // @todo Return to known state
                    return EBF_E_LOOPMEM;
                }
                
                // Check if we should start a loop or jump
                if( *((ebf_private_t *)(ebf.private))->data_pointer_ == 0 )
                {// Jump to matching end brace
                    ((ebf_private_t *)(ebf.private))->program_counter_ \
                        = *(((ebf_private_t *)(ebf.private))->current_loop_ + 1);

                    // Move backwards one loop
                    ((ebf_private_t *)(ebf.private))->current_loop_ -= 2;

                    // Check if the loop doesn't exist in the hash table
                    if( ((ebf_private_t *)(ebf.private))->current_loop_ \
                        < ((ebf_private_t *)(ebf.private))->loop_hash_table_start_ )
                    {// Loop doesn't exist in hash table, no more current loops
                        ((ebf_private_t *)(ebf.private))->current_loop_ = NULL;
                    }
                }
                else
                {// Start a new loop
                    // Do nothing
                    // Chances are higher that when encountering a loop start it will begin a new
                    // loop as opposed to jumping, so this branch should have the least amount
                    // to do.
                }

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
    ((ebf_private_t *)(ebf.private))->is_processing_ = false;

    return EBF_E_NONE;
}

static ebf_error_t pause_(void)
{
    return EBF_E_NONE;
}

static ebf_error_t unpause_(void)
{
    return EBF_E_NONE;
}

static ebf_error_t reset_(void)
{
    return EBF_E_NONE;
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
    return EBF_E_NONE;
}

// This function may only be called from within the init_ function, after all initialization is
// complete. It will request all chunks in order and build the loop hash table before any
// processing occurs.
static ebf_error_t build_loop_hash_table_(void)
{
    uint32_t program_counter = 0;
    ebf_chunk_t chunk;
    int8_t *cursor;
    
    // Check for a valid ebf object
    if( !ebf.is_valid() )
    {// Invalid ebf object
        // Return unsuccessfully
        return EBF_E_INVALID;
    }

    // Check if looping is enabled
    if( ((ebf_private_t *)(ebf.private))->attr_.memory.max_loops == 0 )
    {// Looping is disabled
        return EBF_E_NONE;
    }
    
    // Check if next() is valid
    if( ebf.next == NULL )
    {// next() is invalid
        return EBF_E_INVALID;
    }

    // Get first chunk
    chunk = ebf.next(0);

    // Check if chunk is valid
    if( chunk.instruction_array == NULL \
        || chunk.instruction_array_length == 0 )
    {// Chunk is invalid
        return EBF_E_INVALID;
    }

    // Start building loop hash table
    // Continue building while the given chunks are valid (a NULL chunk will end building)
    while( chunk.instruction_array != NULL \
           && chunk.instruction_array_length != 0 )
    {
        // Check if current chunk contains current instruction (program counter)
        if( program_counter < chunk.starting_instruction                \
            || program_counter > (chunk.starting_instruction + chunk.instruction_array_length) )
        {// Current chunk does not contain needed instruction
            // Request next chunk
            chunk = ebf.next(program_counter);
            continue;
        }

        // Update cursor
        cursor = chunk.instruction_array + (program_counter - chunk.starting_instruction);

        // Parse cursor
        switch( *cursor )
        {
        case '[':
            // Start of loop/jump

            // Check if there is room in the hash table
            if( ((ebf_private_t *)(ebf.private))->next_loop_start_entry_ == NULL )
            {// No more room in hash table
                // Stop building and return with an error
                //! @todo Return to known state
                return EBF_E_LOOPMEM;
            }

            // Write new entry (program_counter + 1 because we begin one past the loop start)
            *((ebf_private_t *)(ebf.private))->next_loop_start_entry_ = program_counter + 1;
            
            // Move next loop end entry to current entry
            ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ \
                = ((ebf_private_t *)(ebf.private))->next_loop_start_entry_;
            
            // Check if there is room for another entry
            if( (((ebf_private_t *)(ebf.private))->next_loop_start_entry_ + 2) \
                > ((ebf_private_t *)(ebf.private))->loop_hash_table_end_ )
            {// No more room in hash table
                // Set next loop start entry to NULL so any more loop starts will fail
                ((ebf_private_t *)(ebf.private))->next_loop_start_entry_ = NULL;
            }
            else
            {// More room available in hash table
                // Move next loop start entry to next entry
                ((ebf_private_t *)(ebf.private))->next_loop_start_entry_ += 2;
            }

            break;

        case ']':
            // End of loop/jump

            // Check if there are no loops started
            if( ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ == NULL )
            {// No loops are started
                // Throw an error and stop building (unmatched end brace)
                //! @todo Return to known state
                return EBF_E_PARSING;
            }

            // Write new entry (program_counter + 1 because we jump one past the loop start)
            *((ebf_private_t *)(ebf.private))->next_loop_end_entry_ = program_counter + 1;

            // Move backwards until we hit an empty entry or the beginning of the hash table
            while( *((ebf_private_t *)(ebf.private))->next_loop_end_entry_ \
                   != 0 )
            {
                // Move backwards one entry
                ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ -= 2;

                // Check if we are out of bounds of the hash table
                if( ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ \
                   < ((ebf_private_t *)(ebf.private))->loop_hash_table_start_ )
                {// Out of bounds
                    // All braces are matched, set next loop end entry to NULL to show this
                    ((ebf_private_t *)(ebf.private))->next_loop_end_entry_ = NULL;
                    // Break out of the loop
                    break;
                }
            }

            break;
            
        default:
            // Ignore any other characters
            break;
        }

        // Increment program counter
        program_counter++;
    }
}


/**
 * @}
 */ // End group ebf
