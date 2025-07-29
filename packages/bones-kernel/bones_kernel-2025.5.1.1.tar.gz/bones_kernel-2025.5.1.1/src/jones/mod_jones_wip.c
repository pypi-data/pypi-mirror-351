// ---------------------------------------------------------------------------------------------------------------------
// Copyright 2025 David Briant, https://github.com/coppertop-bones. All rights reserved.
// ---------------------------------------------------------------------------------------------------------------------

#ifndef SRC_JONES_MOD_JONES_WIP_C
#define SRC_JONES_MOD_JONES_WIP_C "jones/mod_jones_wip.c"


#include "mod_jones_wip.h"
#include "../bk/lib/os.c"
#include "pyom.c"
//#include "pyfs.c"
//#include "pyplay.c"



// ---------------------------------------------------------------------------------------------------------------------
// low level hacks - functions to hack memory from Python
// ---------------------------------------------------------------------------------------------------------------------

pvt PyObject * _toAddress(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    if (nargs != 1) return jErrWrongNumberOfArgs(FN_NAME, 1, nargs);
    return PyTuple_Pack(2, PyLong_FromVoidPtr(args[0]), PyLong_FromSize_t(args[0] -> ob_refcnt));
}

pvt PyObject * _toPtr(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    if (nargs != 1) return jErrWrongNumberOfArgs(FN_NAME, 1, nargs);
    return PyLong_FromVoidPtr(args[0]);
}

pvt PyObject * _pageSize(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    if (nargs != 0) return jErrWrongNumberOfArgs(FN_NAME, 0, nargs);
    return PyLong_FromLong(os_page_size());
}

pvt PyObject * _getCacheLineSize(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    if (nargs != 0) return jErrWrongNumberOfArgs(FN_NAME, 0, nargs);
    return PyLong_FromLong((long) os_cache_line_size());
}

pvt PyObject * _toObj(PyObject *mod, PyObject *args) {
    // could check that address is PyObject aligned
    PyObject *object;
    if (!PyArg_ParseTuple(args, "K", &object)) return 0;
    Py_INCREF(object);
    return PyTuple_Pack(2, object, PyLong_FromSize_t(object -> ob_refcnt));
}

pvt PyObject * _ob_refcnt(PyObject *mod, PyObject *args) {
    PyObject *object;  size_t address;
    if (!PyArg_ParseTuple(args, "K", &address)) return 0;
    object = (PyObject*) address;
    return PyLong_FromSize_t(object -> ob_refcnt);
}

pvt PyObject * _malloc(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    if (nargs != 1) return jErrWrongNumberOfArgs(FN_NAME, 1, nargs);
    // TODO raise a type error
    if (!PyLong_Check(args[0])) return 0;        // size_t
    size_t size = (size_t) PyLong_AsSize_t(args[0]);
    void *p = malloc(size);
    return PyLong_FromVoidPtr(p);
}

pvt PyObject * _atU16(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    // for the given pointer to an array of u16 and the index get a u16

    if (nargs != 2) return jErrWrongNumberOfArgs(FN_NAME, 2, nargs);
    // TODO raise a type error & check within bounds of u16
    if (!PyLong_Check(args[0])) return 0;        // ptr
    if (!PyLong_Check(args[1])) return 0;        // size_t index

    size_t index = PyLong_AsSize_t(args[1]);
    unsigned short *pItem = ((unsigned short*) (PyLong_AsSize_t(args[0]) & PTR_MASK)) + index - 1;

    return PyLong_FromLong(*pItem);
}

pvt PyObject * _atU16Put(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    // for the given pointer to an array of u16, the index, set the bits given by the mask and value

    if (nargs != 4) return jErrWrongNumberOfArgs(FN_NAME, 4, nargs);
    // TODO raise a type error & check within bounds of u16
    if (!PyLong_Check(args[0])) return 0;        // ptr
    if (!PyLong_Check(args[1])) return 0;        // size_t index
    if (!PyLong_Check(args[2])) return 0;        // u16 bit mask
    if (!PyLong_Check(args[3])) return 0;        // u16

    size_t index = PyLong_AsSize_t(args[1]);
    unsigned short *pItem = ((unsigned short*) (PyLong_AsSize_t(args[0]) & PTR_MASK)) + index - 1;
    unsigned short mask = (unsigned short) PyLong_AsLong(args[2]);           // OPEN check range before converting
    unsigned short v = (unsigned short) PyLong_AsLong(args[3]);

    *pItem = (*pItem & (mask ^ 0xFFFF)) | (v & mask);
    return PyBool_FromLong(*pItem);
}

pvt PyObject * _atU8(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    // for the given pointer to an array of u8 and the index get a U8

    if (nargs != 2) return jErrWrongNumberOfArgs(FN_NAME, 2, nargs);
    // TODO raise a type error & check within bounds of u16
    if (!PyLong_Check(args[0])) return 0;        // ptr
    if (!PyLong_Check(args[1])) return 0;        // size_t index

    size_t index = PyLong_AsSize_t(args[1]);
    m8 *pItem = ((mem) (PyLong_AsSize_t(args[0]) & PTR_MASK)) + index - 1;

    return PyLong_FromLong(*pItem);
}

pvt PyObject * _atU8Put(PyObject *mod, PyObject **args, Py_ssize_t nargs) {
    // for the given pointer to an array of u8 and the index, set the bits given by the mask and value

    if (nargs != 4) return jErrWrongNumberOfArgs(FN_NAME, 4, nargs);
    // TODO raise a type error & check within bounds of u8
    if (!PyLong_Check(args[0])) return 0;        // ptr
    if (!PyLong_Check(args[1])) return 0;        // size_t index
    if (!PyLong_Check(args[2])) return 0;        // u8 bit mask
    if (!PyLong_Check(args[3])) return 0;        // u8

    size_t index = (size_t) PyLong_AsSize_t(args[1]);
    m8 *pItem = ((mem) (PyLong_AsSize_t(args[0]) & PTR_MASK)) + index - 1;
    unsigned char mask = (unsigned char) PyLong_AsLong(args[2]);
    unsigned char v = (unsigned char) PyLong_AsLong(args[3]);

    *pItem = (*pItem & (mask ^ 0xFF)) | (v & mask);
    return PyBool_FromLong(*pItem);
}



// ---------------------------------------------------------------------------------------------------------------------
// jones_wip module
// ---------------------------------------------------------------------------------------------------------------------

pvt PyMethodDef jones_wip_fns[] = {
    {"_toAddress", (PyCFunction)                 _toAddress, METH_FASTCALL, "toAddress(object)\n\nanswer the address of object and it's refcount"},
    {"_toPtr", (PyCFunction)                     _toPtr, METH_FASTCALL, "toPtr(object)\n\nanswer the address of object"},
    {"_toObj",                                   _toObj, METH_VARARGS, "toObj(address)\n\nreturn the ptr as an object"},
    {"_ob_refcnt",                               _ob_refcnt, METH_VARARGS, "ob_refcnt(address)\n\nreturn the ref count for the object at the address"},
    {"_atU16", (PyCFunction)                     _atU16, METH_FASTCALL, "atU16(pBuf, index"},
    {"_atU16Put", (PyCFunction)                  _atU16Put, METH_FASTCALL, "atU16Put(pBuf, index, mask, value"},
    {"_atU8", (PyCFunction)                      _atU8, METH_FASTCALL, "atU8(pBuf, index"},
    {"_atU8Put", (PyCFunction)                   _atU8Put, METH_FASTCALL, "atU8Put(pBuf, index, mask, value"},
    {"_malloc", (PyCFunction)                    _malloc, METH_FASTCALL, ""},
    {"getPageSize", (PyCFunction)               _pageSize, METH_FASTCALL, "system page size"},
    {"getCacheLineSize", (PyCFunction)          _getCacheLineSize, METH_FASTCALL, "system cache line size"},

    {0}
};


pvt PyModuleDef jones_module_wip = {
    PyModuleDef_HEAD_INIT,
    .m_name = "jones_wip",
    .m_doc = "work in progress",
    .m_size = -1,
    jones_wip_fns
};


pub PyMODINIT_FUNC PyInit_jones_wip(void) {
    // https://docs.python.org/3/c-api/module.html#c.PyModule_AddObject
    PyObject *m;

    m = PyModule_Create(&jones_module_wip);
    if (m == 0) return 0;

//    // PyPlayCls
//    if (PyType_Ready(&PyPlayCls) < 0) return 0;
//    if (PyModule_AddObject(m, "Play", (PyObject *) &PyPlayCls) < 0) {
//        Py_DECREF(&PyPlayCls);
//        Py_DECREF(m);
//        return 0;
//    }

    // PyOMCls
    if (PyType_Ready(&PyOMCls) < 0) return 0;
    if (PyModule_AddObject(m, "OM", (PyObject *) &PyOMCls) < 0) {
        Py_DECREF(&PyOMCls);
        Py_DECREF(m);
        return 0;
    }

    return m;
}

pvt void die_(char *preamble, char *msg, va_list args) {
    fprintf(stderr, "%s", preamble);
    vfprintf(stderr, msg, args);
    exit(1);
}

#endif  // SRC_JONES_MOD_JONES_WIP_C