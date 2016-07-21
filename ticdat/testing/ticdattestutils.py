import os
import unittest
from shutil import rmtree, copy
import itertools
import fnmatch
from ticdat.utils import dictish, containerish, verify
import unittest
from ticdat import TicDatFactory

__codeFile = []
def _codeFile() :
    if __codeFile:
        return __codeFile[0]
    import inspect
    __codeFile[:]=[os.path.abspath(inspect.getsourcefile(_codeFile))]
    return _codeFile()

def _codeDir():
    return os.path.dirname(_codeFile())

def configure_blank_accdb():
    verify(os.path.isfile("blank.accdb"),
           "You need a blank.accdb file in your current directory.")
    mdb_dir = os.path.abspath(os.path.join(".."))
    v_str = "Contact ticdat support at ticdat@opalytics.com"
    verify(os.path.isdir(mdb_dir), "%s is strangely not a directory. %s"%(mdb_dir, v_str))
    verify(os.path.isfile(os.path.join(mdb_dir, "mdb.py")), "mdb.py is missing. %s"%v_str)
    copy("blank.accdb", mdb_dir)

_debug = []
def _asserting() :
    _debug.append(())
    return _debug
assert _asserting()

def DEBUG() :
    return bool(_debug)

def firesException(f) :
    try:
        f()
    except Exception as e:
        return e

_memo = []
def memo(*args):
    rtn = list(_memo)
    _memo[:] = args
    return rtn[0] if len(rtn) == 1 else rtn

def clean_denormalization_errors(chk):
    return {k:{_k:set(_v) for _k,_v in v.items()} for k,v in chk.items()}

def fail_to_debugger(cls) :
    """
    decorator to allow a unittest class to enter the debugger if a unit test fails
    :param cls: a unittest class
    :return: cls decorated so as to fail to the ipdb debugger
    CAVEATS : Will side effect the unittest module by redirecting the main function!
              This routine is intended for **temporary** decorating of a unittest class
              for debugging/troubleshooting.
    """
    def _failToDebugger(x) :
        if not (x) :
            import ipdb; ipdb.set_trace()
            assert(x)
    cls.assertTrue = lambda s,x : _failToDebugger(x)
    cls.assertFalse = lambda s,x : _failToDebugger(not x)
    cls.failToDebugger = True
    unittest.main = lambda : _runSuite(cls)
    return cls

def flagged_as_run_alone(f):
    """
    a decorator to flag a unittest test function to be the sole test run for
    a fail_to_debugger decorated class
    :param f: a unittest test function
    :return: the same function decorated for fail_to_debugger
    """
    f.runAlone = True
    return f

def _runSuite(cls):
    _rtn = [getattr(cls, x) for x in dir(cls)
           if x.startswith("test")]
    assert all(callable(x) for x in _rtn)

    runalones = [x for x in _rtn if  hasattr(x, "runAlone")]
    assert len(runalones) <= 1, "you specified more than one to runAlone!"
    if runalones:
        _rtn = [runalones[0].__name__]
    else:
        _rtn = [x.__name__ for x in _rtn ]

    suite = unittest.TestSuite()
    for x in _rtn :
        suite.addTest(cls(x))
    if "failToDebugger" in dir(cls) and cls.failToDebugger :
        print("!!! Debugging suite for " + str(cls) + " !!!\n")
        suite.debug()
        print("!!! Debugged suite for " + str(cls) + " !!!\n")
    else :
        unittest.TextTestRunner().run(suite)

def unixWildCardDir(dirPath, unixStyleStr, fullPath = True, collapseSingleton = True, allowLinks = False) :
    assert os.path.isdir(dirPath)
    rtn = [x for x in os.listdir(dirPath) if fnmatch.fnmatch(x, unixStyleStr)]
    if (fullPath) :
        rtn = [os.path.abspath(os.path.join(dirPath, x)) for x in rtn]
    if (not allowLinks) :
        rtn = [x for x in rtn if not os.path.islink(x) ]
    if ( (len(rtn) == 1)  and collapseSingleton):
        return rtn[0]
    return rtn

def findAllUnixWildCard(directory, unixStyleStr, fullPath = True, recursive=True, allowLinks = False, skippedDirs = None):
    _skippedDirs = skippedDirs or [] # Py does scary stuff with mutable default arguments
    assert(os.path.isdir(directory))
    assert (not _skippedDirs)  or (recursive), "skipping directories makes sense only for recursive"
    rtn = unixWildCardDir(directory, unixStyleStr, fullPath = fullPath,
                          collapseSingleton = False, allowLinks = allowLinks)
    dirList=os.listdir(directory)

    for fname in dirList:
        fname = os.path.join(directory,  fname)
        if ( (os.path.isdir(fname)) and recursive and fname not in _skippedDirs) :
            rtn = rtn + findAllUnixWildCard(fname, unixStyleStr, recursive = True,
                                            allowLinks = allowLinks, skippedDirs = _skippedDirs)
    return rtn

def findAllFiles(path, extensions) :
    assert os.path.isdir(path)
    return list(itertools.chain(*[findAllUnixWildCard(path, "*" + x) for x in extensions]))

def makeCleanDir(path) :
    assert not os.path.exists(path) or os.path.isdir(path)
    rmtree(path, ignore_errors = True)
    os.mkdir(path)
    return path
def makeCleanPath(path) :
    if os.path.exists(path) :
        if os.path.isdir(path) :
            makeCleanDir(path)
        else :
            os.remove(path)
    return path

#assert is magic. It  can't be passed around directly. Lambda encapsulation lets us pass around a proxy. Yay lambda
def assertTrue(x) :
    assert (x)

def assertFalse(x) :
    assert (not x)

def spacesSchema() :
    return {"a_table" : [("a Field",),("a Data 1", "a Data 2", "a Data 3") ],
            "b_table" : [("b Field 1", "b Field 2", "b Field 3"), ["b Data"]],
            "c_table" : [[],("c Data 1", "c Data 2", "c Data 3", "c Data 4")]}

def spacesData() :
    return {
        "a_table" : {1 : {"a Data 3":3, "a Data 2":2, "a Data 1":1},
                     "b" : ("b", "d", 12), 0.23 : (11, 12, "thirt")},
        "b_table" : {(1, 2, 3) : 1, ("a", "b", "b") : 12},
        "c_table" : ((1, 2, 3, 4),
                      {"c Data 4":"d", "c Data 2":"b", "c Data 3":"c", "c Data 1":"a"},
                      ("a", "b", 12, 24) )
    }

def assertTicDatTablesSame(t1, t2, _goodTicDatTable,
                           _assertTrue = assertTrue, _assertFalse = assertFalse) :
    _assertTrue(set(t1) == set(t2))
    _assertTrue(_goodTicDatTable(t1) and _goodTicDatTable(t2))
    if not dictish(t1) and not dictish(t2) :
        return
    if dictish(t1) != dictish(t2) and dictish(t2) :
        t1,t2 = t2,t1
    if not dictish(t2) :
        _assertTrue(all(containerish(x) and len(x) == 0 for x in t1.values()))
        return
    for k1,v1 in t1.items() :
        v2 = t2[k1]
        if dictish(v1) != dictish(v2) and dictish(v2) :
            v2, v1 = v1, v2
        if dictish(v1) and dictish(v2) :
            _assertTrue(set(v1) == set(v2))
            for _k1 in v1 :
                _assertTrue(v1[_k1] == v2[_k1])
        elif dictish(v1) and containerish(v2) :
            _assertTrue(sorted(map(str, v1.values())) == sorted(map(str, v2)))
        elif dictish(v1) :
            _assertTrue(len(v1) == 1 and v1.values()[0] == v2)
        else :
            if containerish(v1) != containerish(v2) and containerish(v2) :
                v2, v1 = v1, v2
            if containerish(v1) and containerish(v2) :
                _assertTrue(len(v1) == len(v2))
                _assertTrue(all(v1[x] == v2[x] for x in range(len(v1))))
            elif containerish(v1) :
                _assertTrue(len(v1) == 1 and v1[0] == v2)
            else :
                _assertTrue(v1 == v2)

def deepFlatten(x) :
    # does a FULL recursive flatten.
    # this works for 2.7, will need to be replaced for 3
    # make sure replaced version works equally well with tuples as lists
    import compiler
    return tuple(compiler.ast.flatten(x))

def shallowFlatten(x) :
    return tuple(itertools.chain(*x))

# gurobi netflow problem - http://www.gurobi.com/documentation/6.0/example-tour/netflow_py
def netflowSchema():
    return {
        "commodities" : [["name"], []],
        "nodes": [["name"],[]],
        "arcs" : [("source", "destination"),["capacity"]],
        "cost" : [("commodity", "source", "destination"),["cost"]],
        "inflow" :[["commodity", "node"], ["quantity"]],
    }
def netflowData() :
    class _(object) :
        pass

    dat = _() # simplest object with a __dict__

    # simplest possible copy

    dat.commodities = ['Pencils', 'Pens']
    dat.nodes = ['Detroit', 'Denver', 'Boston', 'New York', 'Seattle']

    dat.arcs = {
('Detroit', 'Boston'):   100,
('Detroit', 'New York'):  80,
('Detroit', 'Seattle'):  120,
('Denver',  'Boston'):   120,
('Denver',  'New York'): 120,
('Denver',  'Seattle'):  120 }

    dat.cost = {
('Pencils', 'Detroit', 'Boston'):   10,
('Pencils', 'Detroit', 'New York'): 20,
('Pencils', 'Detroit', 'Seattle'):  60,
('Pencils', 'Denver',  'Boston'):   40,
('Pencils', 'Denver',  'New York'): 40,
('Pencils', 'Denver',  'Seattle'):  30,
('Pens',    'Detroit', 'Boston'):   20,
('Pens',    'Detroit', 'New York'): 20,
('Pens',    'Detroit', 'Seattle'):  80,
('Pens',    'Denver',  'Boston'):   60,
('Pens',    'Denver',  'New York'): 70,
('Pens',    'Denver',  'Seattle'):  30 }

    dat.inflow = {
('Pencils', 'Detroit'):   50,
('Pencils', 'Denver'):    60,
('Pencils', 'Boston'):   -50,
('Pencils', 'New York'): -50,
('Pencils', 'Seattle'):  -10,
('Pens',    'Detroit'):   60,
('Pens',    'Denver'):    40,
('Pens',    'Boston'):   -40,
('Pens',    'New York'): -30,
('Pens',    'Seattle'):  -30 }

    return dat

def addNetflowForeignKeys(tdf) :
    tdf.add_foreign_key("arcs", "nodes", [u'source', u'name'])
    tdf.add_foreign_key("arcs", "nodes", (u'destination', u'name'))
    tdf.add_foreign_key("cost", "nodes", (u'source', u'name'))
    tdf.add_foreign_key("cost", "nodes", [u'destination', u'name'])
    tdf.add_foreign_key("cost", "commodities", (u'commodity', u'name'))
    tdf.add_foreign_key("inflow", "commodities", (u'commodity', u'name'))
    tdf.add_foreign_key("inflow", "nodes", [u'node', u'name'])


# gurobi diet problem - http://www.gurobi.com/documentation/6.0/example-tour/diet_py
def dietSchema():
    return {
     "categories" : (("name",),["minNutrition", "maxNutrition"]),
     "foods" :[["name"],("cost",)],
     "nutritionQuantities" : (["food", "category"], ["qty"])
    }

def dietSchemaWeirdCase():
    return {
     "cateGories" : (("name",),["miNnutrition", "maXnutrition"]),
     "foodS" :[["name"],("COST",)],
     "nutritionquantities" : (["food", "category"], ["qtY"])
    }
def copyDataDietWeirdCase(dat):
    tdf = TicDatFactory(**dietSchemaWeirdCase())
    rtn = tdf.TicDat()
    for c,r in dat.categories.items():
        rtn.cateGories[c]["miNnutrition"] = r["minNutrition"]
        rtn.cateGories[c]["maXnutrition"] = r["maxNutrition"]
    for f,r in dat.foods.items():
        rtn.foodS[f] = r["cost"]
    for (f,c),r in dat.nutritionQuantities.items():
        rtn.nutritionquantities[f,c] = r["qty"]
    return rtn
def dietSchemaWeirdCase2():
    rtn = dietSchemaWeirdCase()
    rtn["nutrition_quantities"] = rtn["nutritionquantities"]
    del(rtn["nutritionquantities"])
    return rtn
def copyDataDietWeirdCase2(dat):
    tdf = TicDatFactory(**dietSchemaWeirdCase2())
    tmp = copyDataDietWeirdCase(dat)
    rtn = tdf.TicDat(cateGories = tmp.cateGories, foodS = tmp.foodS)
    for (f,c),r in tmp.nutritionquantities.items():
        rtn.nutrition_quantities[f,c] = r
    return rtn

def addDietForeignKeys(tdf) :
    tdf.add_foreign_key("nutritionQuantities", 'categories',[u'category', u'name'])
    tdf.add_foreign_key("nutritionQuantities", 'foods', (u'food', u'name'))

def dietData():
    # this is the gurobi diet data in ticDat format

    class _(object) :
        pass

    dat = _() # simplest object with a __dict__

    dat.categories = {
      'calories': {"minNutrition": 1800, "maxNutrition" : 2200},
      'protein':  {"minNutrition": 91,   "maxNutrition" : float("inf")},
      'fat':      {"minNutrition": 0,    "maxNutrition" : 65},
      'sodium':   {"minNutrition": 0,    "maxNutrition" : 1779}}

    # deliberately goofing on it a little bit
    dat.foods = {
      'hamburger': {"cost": 2.49},
      'chicken':   {"cost": 2.89},
      'hot dog':   {"cost": 1.50},
      'fries':     {"cost": 1.89},
      'macaroni':  2.09,
      'pizza':     {"cost": 1.99},
      'salad':     {"cost": 2.49},
      'milk':      (0.89,),
      'ice cream': {"cost": 1.59}}

    dat.nutritionQuantities = {
      ('hamburger', 'calories'): {"qty" : 410},
      ('hamburger', 'protein'):  {"qty" : 24},
      ('hamburger', 'fat'):      {"qty" : 26},
      ('hamburger', 'sodium'):   {"qty" : 730},
      ('chicken',   'calories'): {"qty" : 420},
      ('chicken',   'protein'):  {"qty" : 32},
      ('chicken',   'fat'):      {"qty" : 10},
      ('chicken',   'sodium'):   {"qty" : 1190},
      ('hot dog',   'calories'): {"qty" : 560},
      ('hot dog',   'protein'):  {"qty" : 20},
      ('hot dog',   'fat'):      {"qty" : 32},
      ('hot dog',   'sodium'):   {"qty" : 1800},
      ('fries',     'calories'): {"qty" : 380},
      ('fries',     'protein'):  {"qty" : 4},
      ('fries',     'fat'):      {"qty" : 19},
      ('fries',     'sodium'):   {"qty" : 270},
      ('macaroni',  'calories'): {"qty" : 320},
      ('macaroni',  'protein'):  {"qty" : 12},
      ('macaroni',  'fat'):      {"qty" : 10},
      ('macaroni',  'sodium'):   {"qty" : 930},
      ('pizza',     'calories'): {"qty" : 320},
      ('pizza',     'protein'):  {"qty" : 15},
      ('pizza',     'fat'):      {"qty" : 12},
      ('pizza',     'sodium'):   {"qty" : 820},
      ('salad',     'calories'): {"qty" : 320},
      ('salad',     'protein'):  {"qty" : 31},
      ('salad',     'fat'):      {"qty" : 12},
      ('salad',     'sodium'):   {"qty" : 1230},
      ('milk',      'calories'): {"qty" : 100},
      ('milk',      'protein'):  {"qty" : 8},
      ('milk',      'fat'):      {"qty" : 2.5},
      ('milk',      'sodium'):   {"qty" : 125},
      ('ice cream', 'calories'): {"qty" : 330},
      ('ice cream', 'protein'):  {"qty" : 8},
      ('ice cream', 'fat'):      {"qty" : 10},
      ('ice cream', 'sodium'):   {"qty" : 180} }

    return dat

def sillyMeSchema() :
    return {"a" : [("aField",),("aData1", "aData2", "aData3") ],
            "b" : [("bField1", "bField2", "bField3"), ["bData"]],
            "c" : [[],("cData1", "cData2", "cData3", "cData4")]}


def sillyMeData() :
    return {
        "a" : {1 : (1, 2, 3), "b" : ("b", "d", 12), 0.23 : (11, 12, "thirt")},
        "b" : {(1, 2, 3) : 1, ("a", "b", "b") : 12},
        "c" : ((1, 2, 3, 4), ("a", "b", "c", "d"), ("a", "b", 12, 24) )
    }
