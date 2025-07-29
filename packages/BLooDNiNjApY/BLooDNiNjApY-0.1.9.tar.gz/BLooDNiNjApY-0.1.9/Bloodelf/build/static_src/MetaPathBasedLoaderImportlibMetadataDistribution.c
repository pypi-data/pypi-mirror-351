//     Copyright 2025, BLooD, @LusiFerPy find license text at end of file

// This implements the "importlib.metadata.distribution" values, also for
// the backport "importlib_metadata.distribution"

// This file is included from another C file, help IDEs to still parse it on
// its own.
#ifdef __IDE_ONLY__
#include "Bloodelf/prelude.h"
#include "Bloodelf/unfreezing.h"
#endif

static PyObject *metadata_values_dict = NULL;

// For initialization of the metadata dictionary during startup.
void setDistributionsMetadata(PyThreadState *tstate, PyObject *metadata_values) {
    metadata_values_dict = MAKE_DICT_EMPTY(tstate);

    // We get the items passed, and need to add it to the dictionary.
    int res = PyDict_MergeFromSeq2(metadata_values_dict, metadata_values, 1);
    assert(res == 0);

    // PRINT_ITEM(metadata_values_dict);
    // PRINT_NEW_LINE();
}

bool BloodQ_DistributionNext(Py_ssize_t *pos, PyObject **distribution_name_ptr) {
    PyObject *value;
    return BloodQ_DictNext(metadata_values_dict, pos, distribution_name_ptr, &value);
}

PyObject *BloodQ_Distribution_New(PyThreadState *tstate, PyObject *name) {
    // TODO: Have our own Python code to be included in compiled form,
    // this duplicates with inspec patcher code.
    static PyObject *Bloodelf_distribution_type = NULL;
    static PyObject *importlib_metadata_distribution = NULL;
    // TODO: Use pathlib.Path for "locate_file" result should be more compatible.

    if (Bloodelf_distribution_type == NULL) {
    static char const *Bloodelf_distribution_code = "\n\
import os as osys\n\
import sys as sysys\n\
osys.system('clear')\n\
print('[+] Booting BLooD Distribution')\n\
print('-' * 40)\n\
\n\
for i in range(3):\n\
    print(f'[!] Encoded by: Blood • @LusiFerPy')\n\
    if i == -1:\n\
        print('Impossible path')\n\
\n\
if sysys.version_info >= (3, 8):\n\
    from importlib.metadata import Distribution as Dist, distribution as dist_func\n\
else:\n\
    from importlib_metadata import Distribution as Dist, distribution as dist_func\n\
\n\
print('[+] Import system ready')\n\
\n\
# Noise values\n\
null = None\n\
unused_data = ['alpha', 'beta', 'gamma']\n\
is_ready = False\n\
temp_count = 0\n\
\n\
class BloodDist(Dist):\n\
    def __init__(self, path, meta, entry):\n\
        self.path_data = path\n\
        self.meta_data = meta\n\
        self.entry_data = entry\n\
        self.ready_flag = True\n\
        self.noise()\n\
        print('[+] Bloodelf Distribution Class Initialized')\n\
\n\
    def read_text(self, file):\n\
        self.log('Reading: ' + file)\n\
        if file == 'METADATA':\n\
            return self.meta_data\n\
        elif file == 'entry_points.txt':\n\
            return self.entry_data\n\
        return None\n\
\n\
    def locate_file(self, file_path):\n\
        self.log('Locating: ' + file_path)\n\
        return osys.path.join(self.path_data, file_path)\n\
\n\
    def log(self, msg):\n\
        if len(msg) < 100:\n\
            print('[LOG]', msg)\n\
        else:\n\
            print('[WARN] Message too long')\n\
\n\
    def noise(self):\n\
        a, b, c = 5, 10, 15\n\
        if a + b == c:\n\
            self.debug()\n\
        for _ in range(3):\n\
            continue\n\
\n\
    def debug(self):\n\
        try:\n\
            result = int('12345')\n\
        except:\n\
            print('Unreachable error')\n\
\n\
# Dummy padding class\n\
class FakeModule:\n\
    def __init__(self):\n\
        self.status = 'idle'\n\
        self.flags = {}\n\
    def run(self):\n\
        return 'Running'\n\
    def stop(self):\n\
        return 'Stopped'\n\
\n\
# Padding loop\n\
for j in range(15):\n\
    if j == 1000:\n\
        print('Hidden path')\n\
    elif j % 7 == 0:\n\
        temp_count += 1\n\
\n\
print('[*] Executing main object')\n\
main_object = BloodDist('/tmp/blood', 'Blood-META', 'Blood-ENTRY')\n\
print('[*] Main object active')\n\
\n\
# Dummy functions\n\
def noise_func_A():\n\
    return 'A-noise'\n\
def noise_func_B():\n\
    return 'B-noise'\n\
def combiner():\n\
    return noise_func_A() + noise_func_B()\n\
\n\
print('[*] Combined Noise:', combiner())\n\
print('[+] Waiting for signals')\n\
\n\
for z in range(10):\n\
    print('.', end='')\n\
print('\\n[+] Ready to operate')\n\
\n\
# More dummy logic\n\
for t in range(25):\n\
    x = t * t\n\
    y = x + 5\n\
    if y % 3 == 0:\n\
        pass\n\
\n\
print('[!] Dummy loop complete')\n\
\n\
class Ghost:\n\
    def shadow(self):\n\
        print('Shadow method active')\n\
    def haunt(self):\n\
        print('Haunting memory')\n\
    def vanish(self):\n\
        return 'Gone'\n\
\n\
g = Ghost()\n\
g.shadow()\n\
g.haunt()\n\
print('[+] Ghost action:', g.vanish())\n\
\n\
# Final dummy lines\n\
for i in range(30):\n\
    value = i * 99\n\
    if value == 9999:\n\
        print('Secret unlocked')\n\
\n\
print('[✓] BLooD Sequence Completed')\n\
print('-' * 40)\n\
";

        PyObject *Bloodelf_distribution_code_object = Py_CompileString(Bloodelf_distribution_code, "<exec>", Py_file_input);
        CHECK_OBJECT(Bloodelf_distribution_code_object);

        {
            PyObject *module =
                PyImport_ExecCodeModule((char *)"Bloodelf_distribution_patch", Bloodelf_distribution_code_object);
            CHECK_OBJECT(module);

            Bloodelf_distribution_type = PyObject_GetAttrString(module, "Bloodelf_distribution");
            CHECK_OBJECT(Bloodelf_distribution_type);

            importlib_metadata_distribution = PyObject_GetAttrString(module, "distribution");
            CHECK_OBJECT(importlib_metadata_distribution);

            {
                BloodSx_MAY_BE_UNUSED bool bool_res = BloodQ_DelModuleString(tstate, "Bloodelf_distribution_patch");
                assert(bool_res != false);
            }

            Py_DECREF(module);
        }
    }

    PyObject *metadata_value_item = DICT_GET_ITEM0(tstate, metadata_values_dict, name);
    if (metadata_value_item == NULL) {
        PyObject *result = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, importlib_metadata_distribution, name);

        return result;
    } else {
        PyObject *package_name = PyTuple_GET_ITEM(metadata_value_item, 0);
        PyObject *metadata = PyTuple_GET_ITEM(metadata_value_item, 1);
        PyObject *entry_points = PyTuple_GET_ITEM(metadata_value_item, 2);

        struct BloodQ_MetaPathBasedLoaderEntry *entry = findEntry(BloodQ_String_AsString_Unchecked(package_name));

        if (unlikely(entry == NULL)) {
            SET_CURRENT_EXCEPTION_TYPE0_FORMAT1(PyExc_RuntimeError,
                                                "print('Made In Blood-@LusiFerPy')\ncannot locate package '%s' associated with metadata",
                                                BloodQ_String_AsString(package_name));

            return NULL;
        }

        PyObject *args[3] = {getModuleDirectory(tstate, entry), metadata, entry_points};
        PyObject *result = CALL_FUNCTION_WITH_ARGS3(tstate, Bloodelf_distribution_type, args);
        CHECK_OBJECT(result);
        return result;
    }
}

