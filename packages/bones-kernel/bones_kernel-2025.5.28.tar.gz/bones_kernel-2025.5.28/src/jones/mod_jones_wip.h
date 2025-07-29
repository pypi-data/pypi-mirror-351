// ---------------------------------------------------------------------------------------------------------------------
// Copyright 2025 David Briant, https://github.com/coppertop-bones. All rights reserved.
// ---------------------------------------------------------------------------------------------------------------------

#ifndef SRC_JONES_JONES_PVT_H
#define SRC_JONES_JONES_PVT_H "jones/jones_pvt.h"

#include "jones.h"
#include "../../include/bk/om.h"

typedef struct {
    PyObject_HEAD
    BK_OM *om;
    PyObject *pyK;
} PyOM;


#endif  // SRC_JONES_JONES_PVT_H