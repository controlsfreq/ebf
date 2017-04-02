/**
 * @file main.c
 * @brief ${brief}
 * @author ${author}
 * @date ${date}
 * @copyright ${copyright_blurb}
 */

#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

#include "ebf.h"

% if includes is not None:
% for i in includes:
#include "${i}"
% endfor
% endif

int main(void) {
    % if en_init_hook:
    init_hook();

    % endif
    /* Start User Application ============================================ */
    ${application}
    /* End User Application ============================================== */
    % if en_cleanup_hook:

    cleanup_hook();
    % endif
}
