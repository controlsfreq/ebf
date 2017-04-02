/**
 * @file      ebf.c
 * @brief     Common EBF definitions and declarations.
 * @author    Liam Bucci <liam.bucci@gmail.com>
 * @date      2017-04-02
 * @copyright @parblock
 *            Copyright (c) 2017, Liam Bucci.
 *
 *            This file is part of Embedded Brain Fuck (EBF).
 *
 *            EBF is free software: you can redistribute it and/or modify it under the terms of
 *            the GNU General Public License as published by the Free Software Foundation, either
 *            version 3 of the License, or (at your option) any later version.
 *
 *            EBF is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 *            without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 *            PURPOSE.  See the GNU General Public License for more details.
 *
 *            You should have received a copy of the GNU General Public License along with EBF.
 *            If not, see <http://www.gnu.org/licenses/>.
 *            @endparblock
 */

#include <stdint.h>
#include <stddef.h>

#include "ebf.h"

cell_t* DP;
