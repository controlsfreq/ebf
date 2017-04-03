
#include "ebf.h"

#include "hooks.h"

cell_t cells[CELLS_SIZE] = {0};

void init_hook(void)
{
    DP = cells;
}
