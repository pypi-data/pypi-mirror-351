// Author: Radost Waszkiewicz
// Descr:  Genrate self avoiding random walks (SARW) for spheres of given sizes
//
// Compile with (linux):
// $ g++ mymodule.cpp -o mymodule.so -g -std=c++1z -fPIC -shared -I/usr/include/python3.8/
//-------------------------------------------------------

#include <cstdio> // Debugging
#include <iostream> // Debugging
#include <vector>

#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>

//#include "cpp_sources/Generator.cc"
#include "Generator.cc"


/** ==== Numpy helpers ==== **/

PyArrayObject* RectangularArrayFromDoubles(double *data, int XSIZE, int YSIZE)
{
    npy_intp dims[2]{XSIZE, YSIZE};
    const int ND = 2;

    double *c_arr = new double[XSIZE*YSIZE];

    for (int i = 0; i < XSIZE; i++)
        for (int j = 0; j < YSIZE; j++)
            c_arr[YSIZE*i+j] = data[YSIZE*i+j];

    // Convert it to a NumPy array.
    PyObject *pArray = PyArray_SimpleNewFromData(
        ND, dims, NPY_DOUBLE, reinterpret_cast<void*>(c_arr)
        );
    if (!pArray)
    {
        std::cerr << "Could not create np.array." << std::endl;
        //return -1;
    }
    PyArrayObject *np_arr = reinterpret_cast<PyArrayObject*>(pArray);    
    PyArray_ENABLEFLAGS(np_arr, NPY_ARRAY_OWNDATA);
    
    return np_arr;
}



/** ======== List of functions exposed to Python =========== */
PyObject* generateChain(PyObject* self, PyObject* args);

static PyMethodDef ModuleFunctions [] =
{
    {"generateChain", &generateChain, METH_VARARGS,
        "generateChain(sizes)"
      "\n"
      "\nGenerate self avoiding random walk of touching spheres of given radii"
      "\n"
      "\nParameters"
      "\n----------"
      "\nsizes : list"
      "\n    Sizes of spheres in the random walk"
      "\n"
      "\nReturns"
      "\n-------"
      "\nlist"
      "\n    A `3*len(sizes)` list of locations of centres of the spheres"
    }
    // Sentinel value used to indicate the end of function listing.
    // All function listing must end with this value.
    ,{nullptr, nullptr, 0, nullptr}
};

/* Module definition */
static struct PyModuleDef ModuleDefinitions {
    PyModuleDef_HEAD_INIT,
    // Module name as string
    "sarw_spheres",
    // Module documentation (docstring)
    "Genrate self avoiding random walks (SARW) for spheres of given sizes.",
    -1,
    // Functions exposed to the module
    ModuleFunctions
};

/** Module Initialization function: must have this name schema
 *  PyInit_<ModuleName> where ModuleName is the same base name of the
 *  shared library ModuleName.so (on Linux) or ModuleName.pyd (on Windows)
 */
PyMODINIT_FUNC PyInit_sarw_spheres(void)
{
    import_array(); // Required for numpy functionality

    Py_Initialize();
    PyObject* pModule = PyModule_Create(&ModuleDefinitions);
    PyModule_AddObject(pModule, "version", Py_BuildValue("s", "version 0.0.6"));
    return pModule;
}


// =========  Functions of the Python Module ======== //
PyObject* generateChain(PyObject* self, PyObject* args)
{
    /*
    Boilerplate thanks to Joel Vroom
    https://stackoverflow.com/questions/18789824/
    */
    
    
    PyArrayObject *X;
    int ndX;
    npy_intp *shapeX;
    PyArray_Descr *dtype;
    NpyIter *iter;
    NpyIter_IterNextFunc *iternext;
    

    PyArg_ParseTuple(args, "O!", &PyArray_Type, &X);
    ndX = PyArray_NDIM(X);
    shapeX = PyArray_SHAPE(X);
    dtype = PyArray_DescrFromType(NPY_DOUBLE);

    iter = NpyIter_New(X, NPY_ITER_READONLY, NPY_KEEPORDER, NPY_NO_CASTING, dtype);
    if (iter==NULL) {
        return NULL;
    }
    iternext = NpyIter_GetIterNext(iter, NULL);
    auto dataptr = (double **) NpyIter_GetDataPtrArray(iter);

    std::vector<double> sizes;

    do {
        sizes.push_back(**dataptr);
    } while (iternext(iter));

    NpyIter_Deallocate(iter);

    /*
    Call generateChain from the C-extension
    */
    
    int n_beads = sizes.size(); // number of beads
    
    Point locations[n_beads];
    Generator::GetChain(&sizes[0],sizes.size(),locations);
    
    /*
    Return Numpy array from generated chain
    */
    
    int n_dims = 3;
    double data[n_beads*n_dims];
    for(int i=0;i<n_beads;i++)
    {
        data[n_dims * i + 0] = locations[i].X;
        data[n_dims * i + 1] = locations[i].Y;
        data[n_dims * i + 2] = locations[i].Z;
    }
    auto np_arr = RectangularArrayFromDoubles(data,n_beads,n_dims);
    
    return reinterpret_cast<PyObject*>(np_arr);
}
