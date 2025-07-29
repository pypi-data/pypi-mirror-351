// ---------------------------------------------------------------------------------------------------------------------
// Copyright 2025 David Briant, https://github.com/coppertop-bones. All rights reserved.
//
// PYOM - PYTHON INTERFACE TO OBJECT MANAGER
// ---------------------------------------------------------------------------------------------------------------------

#ifndef SRC_JONES_PYOM_C
#define SRC_JONES_PYOM_C "jones/pyom.c"


#include <stdlib.h>
#include "lib/pyutils.h"
#include "mod_jones_wip.h"
#include "../bk/mm.c"
#include "../bk/om.c"


#define ProgrammerError PyExc_Exception



// ---------------------------------------------------------------------------------------------------------------------
// PyOM
// ---------------------------------------------------------------------------------------------------------------------

// ---------------------------------------------------------------------------------------------------------------------
// alloc: (szInSlots, btypeid, rc) -> PyObj + PyException

pvt PyObject * PyOM_alloc(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    // answers a proxy for a newly created object of the given btype
    return 0;
//    if (nargs != 1) return jErrWrongNumberOfArgs(FN_NAME, 1, nargs);
//    if (!PyObject_IsInstance(args[0], (PyObject *) &PyBTypeCls)) return PyErr_Format(PyExc_TypeError, "btype is not a BType");
//    // OPEN: what to do if there is no name (use t123?) - 0 means invalid type?
//    long bmtid = (long) tm_bmetatypeid(self->tm, ((PyBType *) args[0])->btypeid);
//    return PyLong_FromLong(bmtid);
}

// ---------------------------------------------------------------------------------------------------------------------
// count: (pObj) -> PyLong + PyException

pvt PyObject * PyOM_count(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    // answer the ref count of the given obj
    if (nargs != 1) return jErrWrongNumberOfArgs(FN_NAME, 1, nargs);
//    if (!PyObject_IsInstance(args[0], (PyObject *) &PyBTypeCls)) return PyErr_Format(PyExc_TypeError, "btype is not a BType");
//    // OPEN: what to do if there is no name (use t123?) - 0 means invalid type?
//    long bmtid = (long) tm_bmetatypeid(self->tm, ((PyBType *) args[0])->btypeid);
//    return PyLong_FromLong(bmtid);
    return 0;
}

// ---------------------------------------------------------------------------------------------------------------------
// drop: (pObj) -> PyLong + PyException

pvt PyObject * PyOM_drop(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    return 0;
}

// ---------------------------------------------------------------------------------------------------------------------
// dup: (pObj) -> PyLong + PyException

pvt PyObject * PyOM_dup(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    return 0;
}

// ---------------------------------------------------------------------------------------------------------------------
// free: (pObj) -> PyLong + PyException

pvt PyObject * PyOM_free(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    return 0;
}

// ---------------------------------------------------------------------------------------------------------------------
// linemap: (gen) -> PyLong + PyException

pvt PyObject * PyOM_linemap(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    return 0;
}

// ---------------------------------------------------------------------------------------------------------------------
// objmap: () -> PyLong + PyException

pvt PyObject * PyOM_objmap(PyOM *self, PyObject **args, Py_ssize_t nargs) {
    return 0;
}


// ---------------------------------------------------------------------------------------------------------------------
// PyOMCls
// ---------------------------------------------------------------------------------------------------------------------

pvt PyObject * PyOM_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    if (PyTuple_GET_SIZE(args) != 1) return PyErr_Format(ProgrammerError, "Must be created as OM(k)");
    return type->tp_alloc(type, 0);
}

pvt int PyOM_init(PyOM *self, PyObject *args, PyObject *kwds) {
    PyKernel *pyK;
    if (!PyArg_ParseTuple(args, "O:", &pyK)) return -1;
    // OPEN: check type of k
    self->pyK = Py_NewRef(pyK);
    self->om = OM_create(pyK->kernel->mm, pyK->kernel->tm);
    return 0;
}

pvt void PyOM_dealloc(PyOM *self) {
    i32 res = OM_trash(self->om);
    if (res) PP(error, "%s: OM_trash failed", FN_NAME);
    Py_XDECREF(self->pyK);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

pvt PyMemberDef PyOM_members[] = {
    {"k", Py_T_OBJECT_EX, offsetof(PyOM, pyK), Py_READONLY, "kernel"},
    {0}
};

pvt PyMethodDef PyOM_methods[] = {
    {"alloc",  (PyCFunction) PyOM_alloc,  METH_FASTCALL,
        "alloc(szInSlots, btypeid, rc)\n\n"
        "Answers a pointer to a newly allocated obj or throws an error."
    },
    {"count", (PyCFunction) PyOM_count, METH_FASTCALL,
        "count(pObj)\n\n"
        "Answers the ref count of pObj, or throws an error."
    },
    {"dup", (PyCFunction) PyOM_dup, METH_FASTCALL,
        "dup(pObj)\n\n"
        "Answers the incremented ref count of pObj, or throws an error."
    },
    {"drop", (PyCFunction) PyOM_drop, METH_FASTCALL,
        "drop(pObj)\n\n"
        "Answers the decremented ref count of pObj, or throws an error."
    },
    {"free", (PyCFunction) PyOM_free, METH_FASTCALL,
        "free(pObj)\n\n"
        "Frees pObj, or throws an error."
    },
    {"objmap", (PyCFunction) PyOM_objmap, METH_FASTCALL,
        "objmap()\n\n"
        "Answers the OMs object map, or throws an error."
    },
    {"linemap", (PyCFunction) PyOM_objmap, METH_FASTCALL,
        "linemap(gen)\n\n"
        "Answers the OMs line map for the given generation, or throws an error."
    },
};

pvt PyTypeObject PyOMCls = {
    PyVarObject_HEAD_INIT(0, 0)
    .tp_name = "jones_pvt.OM",
    .tp_doc = PyDoc_STR("TBC"),
    .tp_basicsize = sizeof(PyOM),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyOM_new,
    .tp_init = (initproc) PyOM_init,
    .tp_dealloc = (destructor) PyOM_dealloc,
    .tp_members = PyOM_members,
    .tp_methods = PyOM_methods,
};



#endif  // SRC_JONES_PYOM_C