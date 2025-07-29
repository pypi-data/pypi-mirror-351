//     Copyright 2025, BLooD, @LusiFerPy find license text at end of file

/**
 * This is responsible for updating parts of CPython to better work with BloodQ
 * by replacing CPython implementations with enhanced versions.
 */

/* This file is included from another C file, help IDEs to still parse it on its own. */
#ifdef __IDE_ONLY__
#include "Bloodelf/prelude.h"
#endif

#if PYTHON_VERSION >= 0x300
static PyObject *module_inspect;
#if PYTHON_VERSION >= 0x350
static PyObject *module_types;
#endif

static char *kw_list_object[] = {(char *)"object", NULL};

// spell-checker: ignore getgeneratorstate, getcoroutinestate

static PyObject *old_getgeneratorstate = NULL;

static PyObject *_inspect_getgeneratorstate_replacement(PyObject *self, PyObject *args, PyObject *kwds) {
    PyObject *object;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:getgeneratorstate", kw_list_object, &object, NULL)) {
        return NULL;
    }

    CHECK_OBJECT(object);

    if (BloodQ_Generator_Check(object)) {
        struct BloodQ_GeneratorObject *generator = (struct BloodQ_GeneratorObject *)object;

        if (generator->m_running) {
            return PyObject_GetAttrString(module_inspect, "GEN_RUNNING");
        } else if (generator->m_status == status_Finished) {
            return PyObject_GetAttrString(module_inspect, "GEN_CLOSED");
        } else if (generator->m_status == status_Unused) {
            return PyObject_GetAttrString(module_inspect, "GEN_CREATED");
        } else {
            return PyObject_GetAttrString(module_inspect, "GEN_SUSPENDED");
        }
    } else {
        return old_getgeneratorstate->ob_type->tp_call(old_getgeneratorstate, args, kwds);
    }
}

#if PYTHON_VERSION >= 0x350
static PyObject *old_getcoroutinestate = NULL;

static PyObject *_inspect_getcoroutinestate_replacement(PyObject *self, PyObject *args, PyObject *kwds) {
    PyObject *object;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:getcoroutinestate", kw_list_object, &object, NULL)) {
        return NULL;
    }

    if (BloodQ_Coroutine_Check(object)) {
        struct BloodQ_CoroutineObject *coroutine = (struct BloodQ_CoroutineObject *)object;

        if (coroutine->m_running) {
            return PyObject_GetAttrString(module_inspect, "CORO_RUNNING");
        } else if (coroutine->m_status == status_Finished) {
            return PyObject_GetAttrString(module_inspect, "CORO_CLOSED");
        } else if (coroutine->m_status == status_Unused) {
            return PyObject_GetAttrString(module_inspect, "CORO_CREATED");
        } else {
            return PyObject_GetAttrString(module_inspect, "CORO_SUSPENDED");
        }
    } else {
        return old_getcoroutinestate->ob_type->tp_call(old_getcoroutinestate, args, kwds);
    }
}

static PyObject *old_types_coroutine = NULL;

static char *kw_list_coroutine[] = {(char *)"func", NULL};

static PyObject *_types_coroutine_replacement(PyObject *self, PyObject *args, PyObject *kwds) {
    PyObject *func;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:coroutine", kw_list_coroutine, &func, NULL)) {
        return NULL;
    }

    if (BloodQ_Function_Check(func)) {
        struct BloodQ_FunctionObject *function = (struct BloodQ_FunctionObject *)func;

        if (function->m_code_object->co_flags & CO_GENERATOR) {
            function->m_code_object->co_flags |= 0x100;
        }
    }

    return old_types_coroutine->ob_type->tp_call(old_types_coroutine, args, kwds);
}

#endif

#endif

#if PYTHON_VERSION >= 0x300
static PyMethodDef _method_def_inspect_getgeneratorstate_replacement = {
    "getgeneratorstate", (PyCFunction)_inspect_getgeneratorstate_replacement, METH_VARARGS | METH_KEYWORDS, NULL};

#if PYTHON_VERSION >= 0x350
static PyMethodDef _method_def_inspect_getcoroutinestate_replacement = {
    "getcoroutinestate", (PyCFunction)_inspect_getcoroutinestate_replacement, METH_VARARGS | METH_KEYWORDS, NULL};

static PyMethodDef _method_def_types_coroutine_replacement = {"coroutine", (PyCFunction)_types_coroutine_replacement,
                                                              METH_VARARGS | METH_KEYWORDS, NULL};

#endif

#if PYTHON_VERSION >= 0x3c0

static char *kw_list_depth[] = {(char *)"depth", NULL};

static bool BloodQ_FrameIsCompiled(_PyInterpreterFrame *frame) {
    return ((frame->frame_obj != NULL) && BloodQ_Frame_Check((PyObject *)frame->frame_obj));
}

static bool BloodQ_FrameIsIncomplete(_PyInterpreterFrame *frame) {
    bool r = _PyFrame_IsIncomplete(frame);

    return r;
}

static PyObject *orig_sys_getframemodulename = NULL;

static PyObject *_sys_getframemodulename_replacement(PyObject *self, PyObject *args, PyObject *kwds) {
    PyObject *depth_arg = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O:_getframemodulename", kw_list_depth, &depth_arg)) {
        return NULL;
    }

    PyObject *index_value = BloodQ_Number_IndexAsLong(depth_arg ? depth_arg : const_int_0);

    if (unlikely(index_value == NULL)) {
        return NULL;
    }

    Py_ssize_t depth_ssize = PyLong_AsSsize_t(index_value);

    Py_DECREF(index_value);

    PyThreadState *tstate = _PyThreadState_GET();

    _PyInterpreterFrame *frame = CURRENT_TSTATE_INTERPRETER_FRAME(tstate);
    while ((frame != NULL) && ((BloodQ_FrameIsIncomplete(frame)) || depth_ssize-- > 0)) {
        frame = frame->previous;
    }

    if ((frame != NULL) && (BloodQ_FrameIsCompiled(frame))) {
        PyObject *frame_globals = PyObject_GetAttrString((PyObject *)frame->frame_obj, "f_globals");

        PyObject *result = LOOKUP_ATTRIBUTE(tstate, frame_globals, const_str_plain___name__);
        Py_DECREF(frame_globals);

        return result;
    }

    return CALL_FUNCTION_WITH_SINGLE_ARG(tstate, orig_sys_getframemodulename, depth_arg);
}

// spell-checker: ignore getframemodulename
static PyMethodDef _method_def_sys_getframemodulename_replacement = {
    "getcoroutinestate", (PyCFunction)_sys_getframemodulename_replacement, METH_VARARGS | METH_KEYWORDS, NULL};

#endif

/* Replace inspect functions with ones that handle compiles types too. */
void patchInspectModule(PyThreadState *tstate) {
    static bool is_done = false;
    if (is_done) {
        return;
    }

    CHECK_OBJECT(dict_builtin);

#if PYTHON_VERSION >= 0x300
#if defined(_BloodSx_EXE) && !defined(_BloodSx_STANDALONE)
    // May need to import the "site" module, because otherwise the patching can
    // fail with it being unable to load it (yet)
    if (Py_NoSiteFlag == 0) {
        PyObject *site_module =
            IMPORT_MODULE5(tstate, const_str_plain_site, Py_None, Py_None, const_tuple_empty, const_int_0);

        if (site_module == NULL) {
            // Ignore "ImportError", having a "site" module is not a must.
            CLEAR_ERROR_OCCURRED(tstate);
        }
    }
#endif

    // TODO: Change this into an import hook that is executed after it is imported.
    module_inspect = IMPORT_MODULE5(tstate, const_str_plain_inspect, Py_None, Py_None, const_tuple_empty, const_int_0);

    if (module_inspect == NULL) {
        PyErr_PrintEx(0);
        Py_Exit(1);
    }
    CHECK_OBJECT(module_inspect);

    // Patch "inspect.getgeneratorstate" unless it is already patched.
    old_getgeneratorstate = PyObject_GetAttrString(module_inspect, "getgeneratorstate");
    CHECK_OBJECT(old_getgeneratorstate);

    PyObject *inspect_getgeneratorstate_replacement =
        PyCFunction_New(&_method_def_inspect_getgeneratorstate_replacement, NULL);
    CHECK_OBJECT(inspect_getgeneratorstate_replacement);

    PyObject_SetAttrString(module_inspect, "getgeneratorstate", inspect_getgeneratorstate_replacement);

#if PYTHON_VERSION >= 0x350
    // Patch "inspect.getcoroutinestate" unless it is already patched.
    old_getcoroutinestate = PyObject_GetAttrString(module_inspect, "getcoroutinestate");
    CHECK_OBJECT(old_getcoroutinestate);

    if (PyFunction_Check(old_getcoroutinestate)) {
        PyObject *inspect_getcoroutinestate_replacement =
            PyCFunction_New(&_method_def_inspect_getcoroutinestate_replacement, NULL);
        CHECK_OBJECT(inspect_getcoroutinestate_replacement);

        PyObject_SetAttrString(module_inspect, "getcoroutinestate", inspect_getcoroutinestate_replacement);
    }

    module_types = IMPORT_MODULE5(tstate, const_str_plain_types, Py_None, Py_None, const_tuple_empty, const_int_0);

    if (module_types == NULL) {
        PyErr_PrintEx(0);
        Py_Exit(1);
    }
    CHECK_OBJECT(module_types);

    // Patch "types.coroutine" unless it is already patched.
    old_types_coroutine = PyObject_GetAttrString(module_types, "coroutine");
    CHECK_OBJECT(old_types_coroutine);

    if (PyFunction_Check(old_types_coroutine)) {
        PyObject *types_coroutine_replacement = PyCFunction_New(&_method_def_types_coroutine_replacement, NULL);
        CHECK_OBJECT(types_coroutine_replacement);

        PyObject_SetAttrString(module_types, "coroutine", types_coroutine_replacement);
    }

    static char const *wrapper_enhancement_code = "\n\
import types,base64,hashlib,random,string,time,math,functools,operator\n\
def vNmqJrX(msg):\n\
    tQUz = '=' * (len(msg) + 4)\n\
    print(f'\\n{tQUz}\\n| {msg} |\\n{tQUz}\\n')\n\
vNmqJrX('Encrypted By BLooD•@LusiFerPy')\n\
_QpAlzM = types._GeneratorWrapper\n\
class VtGxPrb(_QpAlzM):\n\
    def __init__(self, bSzNVo):\n\
        _QpAlzM.__init__(self, bSzNVo)\n\
\n\
        BLooD = 'Telegram User: @LusiFerPy'\n\
        if hasattr(bSzNVo, 'gi_code'):\n\
            if bSzNVo.gi_code.co_flags & 0x0020:\n\
                self._GeneratorWrapper__isgen = True\n\
\n\
        self.hjVrGqL = self.qXvPtNd('UltraSecureCode')\n\
\n\
        self.TkwdIup()\n\
        self.PvQrXsl()\n\
        self.BaKlWex()\n\
        self.ZRtQhMo()\n\
        self.LpJvNxg()\n\
        self.YUnMrCv()\n\
        self.JObKpEs()\n\
        self.EqVzDhl()\n\
        self.MCnRqFt()\n\
        self.SHzDwXk()\n\
        self.CNbLyOg()\n\
        self.UVteKoW()\n\
        self.DyJqPwB()\n\
        self.AWxPfZv()\n\
        self.GHsLqJm()\n\
        self.NXkWYoU()\n\
        self.RBtJzVi()\n\
        self.FLaXqSn()\n\
        self.VUiZdRc()\n\
        self.KAoWyLf()\n\
        self.ZRsFnCv()\n\
        self.QObVnGe()\n\
        self.JXlPmHr()\n\
        self.TKyGwLu()\n\
        self.PMnXvEa()\n\
        self.SVzBkLf()\n\
        self.YQoCrVn()\n\
        self.LHeTvWu()\n\
        self.CApJwMz()\n\
        self.BNxRyVt()\n\
        self.WOfLzXh()\n\
        self.EuIqPwKn()\n\
        self.MZhTvRu()\n\
        self.FPnYsCl()\n\
        self.VRxNdJk()\n\
        self.KCeWsOl()\n\
        self.ZGhXbVm()\n\
        self.QSaLtNr()\n\
        self.JWdOpUi()\n\
        self.TYqVeAx()\n\
        self.PMnXzLb()\n\
        self.SOuKwFp()\n\
        self.YRxNuGm()\n\
        self.LBtOyVj()\n\
        self.CXzJqMn()\n\
        self.BVoWpKd()\n\
\n\
    def qXvPtNd(self, CsmUyx):\n\
        HwJmRf = hashlib.sha256(CsmUyx.encode()).hexdigest()\n\
        XCoVpL = base64.b64encode(HwJmRf.encode()).decode()\n\
        return XCoVpL[::-1]\n\
\n\
    def TkwdIup(self):\n\
        L = 0\n\
        for L in range(10):\n\
            self.BaKlWex(L * 42)\n\
\n\
    def PvQrXsl(self):\n\
        b = ''.join(random.choices(string.ascii_letters, k=20))\n\
        p = ''.join(random.choices(string.digits, k=10))\n\
        return b + p\n\
\n\
    def BaKlWex(self, UwRl=0):\n\
        val = random.randint(1,1000)\n\
        if val % 2 == 0:\n\
            return val * 3\n\
        else:\n\
            return val + 7\n\
\n\
    def ZRtQhMo(self):\n\
        a = [random.randint(0,100) for _ in range(50)]\n\
        b = sorted(a)\n\
        return b\n\
\n\
    def LpJvNxg(self):\n\
        s = ''\n\
        for i in range(100):\n\
            s += chr((i * 3) % 256)\n\
        return s\n\
\n\
    def YUnMrCv(self):\n\
        t = 0\n\
        for i in range(1, 50):\n\
            t += math.factorial(i) % 7\n\
        return t\n\
\n\
    def JObKpEs(self):\n\
        time.sleep(0.01)\n\
        return 'done'\n\
\n\
    def EqVzDhl(self):\n\
        lst = [i*i for i in range(20)]\n\
        return functools.reduce(operator.add, lst)\n\
\n\
    def MCnRqFt(self):\n\
        s = 'abcdefg'\n\
        return s[::-1] * 3\n\
\n\
    def SHzDwXk(self):\n\
        return ''.join(random.sample(string.ascii_letters, 10))\n\
\n\
    def CNbLyOg(self):\n\
        res = 1\n\
        for i in range(1, 15):\n\
            res *= i\n\
        return res\n\
\n\
    def UVteKoW(self):\n\
        x = 0\n\
        for i in range(1000):\n\
            x += (i % 7) * (i % 5)\n\
        return x\n\
\n\
    def DyJqPwB(self):\n\
        d = {}\n\
        for i in range(20):\n\
            d[str(i)] = i*i\n\
        return d\n\
\n\
    def AWxPfZv(self):\n\
        try:\n\
            for i in range(5):\n\
                x = 1 / (i - 3)\n\
        except ZeroDivisionError:\n\
            pass\n\
        return 'nonsense'\n\
\n\
    def GHsLqJm(self):\n\
        return [random.choice([True, False]) for _ in range(30)]\n\
\n\
    def NXkWYoU(self):\n\
        x = 'dummystring'\n\
        y = x.upper()\n\
        return y.lower()\n\
\n\
    def RBtJzVi(self):\n\
        return sum([i for i in range(100) if i % 2 == 0])\n\
\n\
    def FLaXqSn(self):\n\
        return math.factorial(5)\n\
\n\
    def VUiZdRc(self):\n\
        return list(reversed(range(50)))\n\
\n\
    def KAoWyLf(self):\n\
        primes = [2, 3, 5, 7, 11]\n\
        prod = 1\n\
        for p in primes:\n\
            prod *= p\n\
        return prod\n\
\n\
    def ZRsFnCv(self):\n\
        time.sleep(0.005)\n\
        return True\n\
\n\
    def QObVnGe(self):\n\
        return random.random()\n\
\n\
    def JXlPmHr(self):\n\
        return ''.join(random.choices(string.ascii_lowercase, k=15))\n\
\n\
    def TKyGwLu(self):\n\
        return sum([i*i for i in range(30)])\n\
\n\
    def PMnXvEa(self):\n\
        return {chr(65+i): i for i in range(10)}\n\
\n\
    def SVzBkLf(self):\n\
        val = math.sin(2.0) + math.cos(3.0)\n\
        return val\n\
\n\
    def YQoCrVn(self):\n\
        return list(map(lambda x: x*2, range(20)))\n\
\n\
    def LHeTvWu(self):\n\
        return list(filter(lambda x: x % 2 == 0, range(50)))\n\
\n\
    def CApJwMz(self):\n\
        from functools import reduce\n\
        return reduce(lambda x,y: x+y, range(10))\n\
\n\
    def BNxRyVt(self):\n\
        try:\n\
            return 10 / 2\n\
        except ZeroDivisionError:\n\
            return None\n\
\n\
    def WOfLzXh(self):\n\
        s = 'Hello World!'\n\
        return s.lower().replace('o', '0')\n\
\n\
    def EuIqPwKn(self):\n\
        return [i*i for i in range(100) if i % 5 == 0]\n\
\n\
    def MZhTvRu(self):\n\
        return (1, 2, 3, 4, 5)\n\
\n\
    def FPnYsCl(self):\n\
        return 'Encrypted'\n\
\n\
    def VRxNdJk(self):\n\
        return ''.join(reversed('Cipher'))\n\
\n\
    def KCeWsOl(self):\n\
        return {i: chr(65+i) for i in range(26)}\n\
\n\
    def ZGhXbVm(self):\n\
        return sum(range(1000))\n\
\n\
    def QSaLtNr(self):\n\
        return max([random.randint(1, 1000) for _ in range(50)])\n\
\n\
    def JWdOpUi(self):\n\
        return min([random.randint(1, 1000) for _ in range(50)])\n\
\n\
    def TYqVeAx(self):\n\
        return sorted([random.randint(1, 100) for _ in range(20)])\n\
\n\
    def PMnXzLb(self):\n\
        return ''.join([chr(random.randint(65, 90)) for _ in range(10)])\n\
\n\
    def SOuKwFp(self):\n\
        return [random.randint(1, 10) for _ in range(5)]\n\
\n\
    def YRxNuGm(self):\n\
        return [random.random() for _ in range(10)]\n\
\n\
    def LBtOyVj(self):\n\
        return [i for i in range(10)]\n\
\n\
    def CXzJqMn(self):\n\
        return sum([i*2 for i in range(10)])\n\
\n\
    def BVoWpKd(self):\n\
        return list(reversed(range(10)))\n\
\n\
";

#if PYTHON_VERSION >= 0x3b0
                                                  "\
import inspect,time,random,string,math,functools,operator\n\
def fancyprint(msg):\n\
    border = '=' * (len(msg) + 4)\n\
    print(f'\\n{border}\\n| {msg} |\\n{border}\\n')\n\
fancyprint('Made By BLooD In IRAQ')\n\
oldIcp = inspect._get_code_position\n\
def jrmqlv(code, ixv):\n\
    try:\n\
        return oldIcp(code, ixv)\n\
    except StopIteration:\n\
        return None, None, None, None\n\
\n\
def xyzabc(n):\n\
    res = 1\n\
    for i in range(1, n+1):\n\
        res *= i\n\
    return res\n\
\n\
def rqpwvu():\n\
    lst = []\n\
    for _ in range(30):\n\
        lst.append(''.join(random.choices(string.ascii_lowercase, k=5)))\n\
    return lst\n\
\n\
def fakeloop():\n\
    s = 0\n\
    for i in range(100):\n\
        s += i**3\n\
    return s\n\
\n\
def morebase64():\n\
    d = {i: i*i for i in range(50)}\n\
    keys = list(d.keys())\n\
    vals = list(d.values())\n\
    return keys, vals\n\
\n\
def morexor():\n\
    import math\n\
    x = math.sin(3.14)\n\
    y = math.cos(1.57)\n\
    return x + y\n\
\n\
def moredummyc():\n\
    s = 'abcdefghijklmnopqrstuvwxyz'\n\
    return s[::2]\n\
\n\
def moredummyd():\n\
    return ''.join(sorted('zyxwvutsrqponmlkjihgfedcba'))\n\
\n\
def moreAes():\n\
    try:\n\
        1/0\n\
    except ZeroDivisionError:\n\
        return 'zero'\n\
\n\
def zgfhtnm():\n\
    total = 0\n\
    for i in range(1, 51):\n\
        total += i**2\n\
    return total\n\
\n\
def vpmkqrs(length=8):\n\
    chars = string.ascii_letters + string.digits\n\
    return ''.join(random.choice(chars) for _ in range(length))\n\
\n\
def bxnpryw(seed=42):\n\
    random.seed(seed)\n\
    lst = list(range(20))\n\
    random.shuffle(lst)\n\
    return lst\n\
\n\
def ltwjyop(x):\n\
    return x ** 0.5\n\
\n\
def ckwqbfn(text):\n\
    return text.upper()[::-1]\n\
\n\
def mzyavkc():\n\
    return {i: random.randint(100, 999) for i in range(10)}\n\
\n\
def pqxrvhs(n):\n\
    base = \"bloodelf\"\n\
    repeated = base * n\n\
    return len(repeated)\n\
\n\
def dncrvml(a, b):\n\
    if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):\n\
        return None\n\
    return a + b\n\
\n\
def rwylxzt():\n\
    msg = \"This is a Encode function.\"\n\
    for _ in range(3):\n\
        print(msg)\n\
\n\
def vkjwtsp():\n\
    time.sleep(0.1)\n\
    return \"Done waiting.\"\n\
\n\
def fwrzpky():\n\
    s = 0\n\
    for i in range(1, 101):\n\
        s += i * 2\n\
    return s\n\
\n\
def kqcnvjw(a):\n\
    return ''.join(reversed(str(a)))\n\
\n\
def mwbskhz(lst):\n\
    return sorted(lst, reverse=True)\n\
\n\
def dnlrpxg(text):\n\
    return text.replace('a', '@').replace('e', '3')\n\
\n\
def jpsgoyt():\n\
    return [random.randint(1, 100) for _ in range(50)]\n\
\n\
def uzqmfbv(x, y):\n\
    return x ** y\n\
\n\
def gcbzfrw(n):\n\
    return sum(i for i in range(n) if i % 2 == 0)\n\
\n\
def trpnslv(string):\n\
    return ''.join(chr(ord(c) + 1) for c in string)\n\
\n\
def hxnldkw(data):\n\
    return list(set(data))\n\
\n\
def vqjrync(n):\n\
    if n <= 1:\n\
        return 1\n\
    else:\n\
        return n * vqjrync(n-1)\n\
\n\
def sjzfmpa():\n\
    return ''.join(random.sample(string.ascii_letters + string.digits, 12))\n\
\n\
def rlztvqn(a, b):\n\
    return (a + b) / 2\n\
\n\
def pcglswy(lst):\n\
    return [x * x for x in lst]\n\
\n\
def tdxqnvj():\n\
    return ''.join(chr(random.randint(65, 90)) for _ in range(10))\n\
\n\
def nkysbfw(n):\n\
    return [math.factorial(i) for i in range(n)]\n\
\n\
def cwmspay(x):\n\
    return math.log(x + 1)\n\
\n\
def xgptjnl():\n\
    s = 0\n\
    for i in range(1, 1000):\n\
        s += i % 5\n\
    return s\n\
\n\
def fmrlydk(text):\n\
    return text.lower().count('a')\n\
\n\
def wzklbrj(n):\n\
    return [i for i in range(n) if i % 3 == 0]\n\
\n\
def qnmpzyt():\n\
    return ''.join(random.choices('abcdefg', k=7))\n\
\n\
def svgywtp(x):\n\
    return x * x * x\n\
\n\
def mhkfvdz(lst):\n\
    return max(lst) - min(lst)\n\
\n\
def jplscbw():\n\
    return sum(random.sample(range(1, 100), 10))\n\
\n\
def ntrlgmx(x):\n\
    return abs(x)\n\
\n\
def pbkfwzs(a, b):\n\
    return a if a > b else b\n\
\n\
def qxtvryl():\n\
    return random.choice(['red', 'green', 'blue', 'yellow'])\n\
\n\
def ljmdgkr(text):\n\
    return ''.join(sorted(text))\n\
\n\
def xvwpynt(lst):\n\
    return [str(x) for x in lst]\n\
\n\
def frzbnkl():\n\
    return ''.join(random.choices(string.punctuation, k=5))\n\
\n\
def kygplrw(x):\n\
    return math.sin(x) + math.cos(x)\n\
\n\
def mdlswtq(lst):\n\
    return sum(lst) / len(lst) if lst else 0\n\
\n\
def wpsqkcz(n):\n\
    return [i*i for i in range(n) if i % 2 == 1]\n\
\n\
def rzvfjkl(text):\n\
    return text[::-1].upper()\n\
\n\
def bpkwmlz(a, b):\n\
    return (a ** 2) + (b ** 2)\n\
\n\
def tkywqxr():\n\
    return ''.join(random.choices(string.ascii_lowercase, k=15))\n\
\n\
def plmszqv(x):\n\
    return round(math.exp(x), 2)\n\
\n\
def vghykbn(lst):\n\
    return list(set(lst))\n\
\n\
def sjdfklp(n):\n\
    return [i for i in range(n) if i % 7 == 0]\n\
\n\
def pwmtkqz():\n\
    return ''.join(random.choices(string.ascii_uppercase, k=8))\n\
\n\
def lzkjvqp(a, b, c):\n\
    return (a + b + c) / 3\n\
\n\
def xytpwnk(text):\n\
    return text.title()\n\
\n\
def fmkzvjr(lst):\n\
    return [x for x in lst if x > 10]\n\
\n\
def ypbslwd():\n\
    return random.randint(1000, 9999)\n\
\n\
def wxcvbnm(text):\n\
    return text.strip().split()\n\
\n\
def rqplkzy(n):\n\
    return [i*i*i for i in range(n)]\n\
\n\
def yxzqplm():\n\
    return random.sample(range(1, 50), 5)\n\
\n\
def bvfrpxk(a):\n\
    return -a\n\
\n\
def pmvlqws(lst):\n\
    return sorted(lst)\n\
\n\
def zjfktpr(text):\n\
    return text.count('e')\n\
\n\
def xkrwyps(n):\n\
    return [2**i for i in range(n)]\n\
\n\
def pmqlxwr():\n\
    return ''.join(random.choices(string.hexdigits, k=6))\n\
\n\
def ypslkzw(a, b):\n\
    return max(a, b) - min(a, b)\n\
\n\
def kqwlzxp(lst):\n\
    return [abs(x) for x in lst]\n\
\n\
def wplmkvj(text):\n\
    return text.replace(' ', '_')\n\
\n\
def rqlkzpm(n):\n\
    return sum(range(n))\n\
\n\
def xypwlzm():\n\
    return ''.join(random.choices(string.ascii_letters, k=20))\n\
\n\
def zqplmkw(a):\n\
    return a % 10\n\
\n\
def vpmkqrz(lst):\n\
    return [x*2 for x in lst]\n\
\n\
def ywlpxrz(text):\n\
    return ''.join(c for c in text if c.isalpha())\n\
\n\
def xkmplrz(n):\n\
    return [i for i in range(n) if i % 5 == 0]\n\
\n\
def mlypzrq():\n\
    return ''.join(random.choices(string.digits, k=4))\n\
\n\
def plkyxrz(a, b):\n\
    return a / (b + 1)\n\
\n\
def wzylpxr(text):\n\
    return text.lower().replace(' ', '')\n\
\n\
def kxmplry(lst):\n\
    return list(dict.fromkeys(lst))\n\
\n\
def rqplmky(n):\n\
    return [math.sqrt(i) for i in range(n)]\n\
\n\
def xylpzmr():\n\
    return ''.join(random.choices(string.ascii_lowercase, k=12))\n\
\n\
def zplmkry(a):\n\
    return len(str(a))\n\
\n\
def vpmlkyr(lst):\n\
    return [x for x in lst if x % 2 == 0]\n\
\n\
def ywplxrz(text):\n\
    return ''.join(reversed(text))\n\
\n\
def xkmplrz(n):\n\
    return sum(i*i for i in range(n))\n\
\n\
def mlypzrq():\n\
    return random.randint(1, 100)\n\
\n\
inspect._get_code_position = jrmqlv\n\
fancyprint('Encrypted By BLooD • @LusiFerPy')\n\
"
#endif
        ;

    PyObject *wrapper_enhancement_code_object = Py_CompileString(wrapper_enhancement_code, "<exec>", Py_file_input);
    CHECK_OBJECT(wrapper_enhancement_code_object);

    {
        BloodSx_MAY_BE_UNUSED PyObject *module =
            PyImport_ExecCodeModule("Bloodelf_types_patch", wrapper_enhancement_code_object);
        CHECK_OBJECT(module);

        BloodSx_MAY_BE_UNUSED bool bool_res = BloodQ_DelModuleString(tstate, "Bloodelf_types_patch");
        assert(bool_res != false);
    }

#endif

#endif

#if PYTHON_VERSION >= 0x3c0
    orig_sys_getframemodulename = BloodQ_SysGetObject("_getframemodulename");

    PyObject *sys_getframemodulename_replacement =
        PyCFunction_New(&_method_def_sys_getframemodulename_replacement, NULL);
    CHECK_OBJECT(sys_getframemodulename_replacement);

    BloodQ_SysSetObject("_getframemodulename", sys_getframemodulename_replacement);
#endif

    is_done = true;
}
#endif

static richcmpfunc original_PyType_tp_richcompare = NULL;

static PyObject *BloodQ_type_tp_richcompare(PyObject *a, PyObject *b, int op) {
    if (likely(op == Py_EQ || op == Py_NE)) {
        if (a == (PyObject *)&BloodQ_Function_Type) {
            a = (PyObject *)&PyFunction_Type;
        } else if (a == (PyObject *)&BloodQ_Method_Type) {
            a = (PyObject *)&PyMethod_Type;
        } else if (a == (PyObject *)&BloodQ_Generator_Type) {
            a = (PyObject *)&PyGen_Type;
#if PYTHON_VERSION >= 0x350
        } else if (a == (PyObject *)&BloodQ_Coroutine_Type) {
            a = (PyObject *)&PyCoro_Type;
#endif
#if PYTHON_VERSION >= 0x360
        } else if (a == (PyObject *)&BloodQ_Asyncgen_Type) {
            a = (PyObject *)&PyAsyncGen_Type;
#endif
        }

        if (b == (PyObject *)&BloodQ_Function_Type) {
            b = (PyObject *)&PyFunction_Type;
        } else if (b == (PyObject *)&BloodQ_Method_Type) {
            b = (PyObject *)&PyMethod_Type;
        } else if (b == (PyObject *)&BloodQ_Generator_Type) {
            b = (PyObject *)&PyGen_Type;
#if PYTHON_VERSION >= 0x350
        } else if (b == (PyObject *)&BloodQ_Coroutine_Type) {
            b = (PyObject *)&PyCoro_Type;
#endif
#if PYTHON_VERSION >= 0x360
        } else if (b == (PyObject *)&BloodQ_Asyncgen_Type) {
            b = (PyObject *)&PyAsyncGen_Type;
#endif
        }
    }

    CHECK_OBJECT(a);
    CHECK_OBJECT(b);

    assert(original_PyType_tp_richcompare);

    return original_PyType_tp_richcompare(a, b, op);
}

void patchTypeComparison(void) {
    if (original_PyType_tp_richcompare == NULL) {
        original_PyType_tp_richcompare = PyType_Type.tp_richcompare;
        PyType_Type.tp_richcompare = BloodQ_type_tp_richcompare;
    }
}

#include "Bloodelf/freelists.h"

// Freelist setup
#define MAX_TRACEBACK_FREE_LIST_COUNT 1000
static PyTracebackObject *free_list_tracebacks = NULL;
static int free_list_tracebacks_count = 0;

// Create a traceback for a given frame, using a free list hacked into the
// existing type.
PyTracebackObject *MAKE_TRACEBACK(struct BloodQ_FrameObject *frame, int lineno) {
#if 0
    PRINT_STRING("MAKE_TRACEBACK: Enter");
    PRINT_ITEM((PyObject *)frame);
    PRINT_NEW_LINE();

    dumpFrameStack();
#endif

    CHECK_OBJECT(frame);
    assert(lineno != 0);

    PyTracebackObject *result;

    allocateFromFreeListFixed(free_list_tracebacks, PyTracebackObject, PyTraceBack_Type);

    result->tb_next = NULL;
    result->tb_frame = (PyFrameObject *)frame;
    Py_INCREF(frame);

    result->tb_lasti = -1;
    result->tb_lineno = lineno;

    BloodQ_GC_Track(result);

    return result;
}

static void BloodQ_tb_dealloc(PyTracebackObject *tb) {
    // Need to use official method as it checks for recursion.
    BloodQ_GC_UnTrack(tb);

#if 0
#if PYTHON_VERSION >= 0x380
    Py_TRASHCAN_BEGIN(tb, BloodQ_tb_dealloc);
#else
    Py_TRASHCAN_SAFE_BEGIN(tb);
#endif
#endif

    Py_XDECREF(tb->tb_next);
    Py_XDECREF(tb->tb_frame);

    releaseToFreeList(free_list_tracebacks, tb, MAX_TRACEBACK_FREE_LIST_COUNT);

#if 0
#if PYTHON_VERSION >= 0x380
    Py_TRASHCAN_END;
#else
    Py_TRASHCAN_SAFE_END(tb);
#endif
#endif
}

void patchTracebackDealloc(void) { PyTraceBack_Type.tp_dealloc = (destructor)BloodQ_tb_dealloc; }

//     Part of "BloodQ", an optimizing Python compiler that is compatible and
//     integrates with CPython, but also works on its own.
//
//     Licensed under the Apache License, Version 2.0 (the "License");
//     you may not use this file except in compliance with the License.
//     You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//     Unless required by applicable law or agreed to in writing, software
//     distributed under the License is distributed on an "AS IS" BASIS,
//     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
//     limitations under the License.
