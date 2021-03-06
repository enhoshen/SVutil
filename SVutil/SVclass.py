from SVutil.SVutil import *
import re

VERBOSE = os.environ.get("VERBOSE", 0)


class EAdict:  # easy access
    def __init__(self, items):
        if type(items) == dict:
            self.dic = items
        elif type(items) == list:
            self.dic = {v: i for i, v in enumerate(items)}
        else:
            print("un-supported type for EAdict")
            raise TypeError

    def __getattr__(self, n):
        return self.dic[n]

    # completer
    def __svcompleterattr__(self):
        x = set(self.dic.keys())
        return x

    def __svcompleterfmt__(self, attr, match):
        if attr in self.dic.keys():
            return f"{SVutil.ccyan}{match}{SVutil.creset}"
        else:
            return f"{match}"


paramfield = EAdict(
    [
        "name",
        "dim",
        "tp",
        "bw",
        "num",
        "bwstr",
        "dimstr",
        "numstr",
        "paramtype",
        "numstrlst",
    ]
)
typefield = EAdict(["name", "bw", "dim", "tp", "enumliteral", "cmts"])
portfield = EAdict(
    [
        "direction",
        "name",
        "dim",
        "tp",
        "bw",
        "bwstr",
        "dimstr",
        "dimstrtuple",
        "cmts",
        "group",
    ]
)
enumfield = EAdict(["name", "bw", "dim", "tp", "enumliterals", "cmts"])
enumsfield = EAdict(["names", "nums", "cmts", "idxs", "sizes", "name_bases", "groups"])
enumlfield = EAdict(["name", "num", "cmt", "idx", "size", "name_base", "group"])
macrofield = EAdict(["args", "macrostr", "lambda"])


class SVclass(SVutil):
    def __init__(self):
        self.w = 20
        self.V_(VERBOSE)
        pass

    def __getattr__(self, n):
        return self.data[self.field.dic[n]]

    @property
    def ShowData(self):
        s = ""
        for f in self.field.dic:
            try:
                s += f"{self.data[self.field.dic[f]].__repr__():<{self.w}}"
            except:
                s += f'{"":<{self.w}}'
        return s + "\n"

    @property
    def ShowLine(self):
        return f'{"":{self.linechar}<{len(self.field.dic)*self.w}}\n'

    @property
    def ShowField(self):
        s = ""
        for f in self.field.dic:
            s += f"{f:<{self.w}}"
        return s + "\n"

    @property
    def Show(self):
        s = ""
        s += self.ShowField
        s += self.ShowLine
        s += self.ShowData
        return s

    def ShowDataCb(self, cblst):
        """
        cblst:callback list; applied to each field
        Ex: ShowDataCb([hex,bin]) would print hex(field0), bin(field1)
        """
        s = ""
        for f, cb in zip(self.field.dic, cblst):
            _s = (
                cb(self.data[self.field.dic[f]]) if cb else self.data[self.field.dic[f]]
            )
            _s = _s.__repr__() if type(_s) != str else _s
            s += f"{_s:<{self.w}}"
        return s + "\n"

    # completer
    def __svcompleterattr__(self):
        x = set(self.field.dic.keys())
        return x

    def __svcompleterfmt__(self, attr, match):
        if attr in self.field.dic.keys():
            return f"{SVutil.ccyan}{match}{SVutil.creset}"
        else:
            return f"{match}"


class SVParam(SVclass):
    field = paramfield

    def __init__(self, param=None):
        self.w = 20
        self.linechar = "="
        self.data = param


class SVStruct(SVclass):
    """ bugged """

    field = typefield

    def __init__(self, tp=None):
        self.w = 15
        self.linechar = "="
        self.datas = [SVType(t) for t in tp]

    def IsAlias(self):
        pass

    @property
    def ShowData(self):
        for d in self.datas:
            d.ShowData


class SVType(SVclass):
    field = typefield

    def __init__(self, tp=None):
        self.w = 15
        self.linechar = "="
        self.data = tp

    def __repr__(self):
        type_ = type(self)
        module = type_.__module__
        qualname = type_.__qualname__
        return f"<{module}.{qualname} {self.name} at {hex(id(self))}>"

    @property
    def ShowData(self):
        s = ""
        for d in self.data:
            s += d.ShowData
        return s


class SVPort(SVclass):
    field = portfield

    def __init__(self, port=None):
        self.w = 20
        self.linechar = "="
        self.data = port


class SVEnums(SVclass):
    field = enumsfield

    def __init__(self, enums=None):
        self.w = 30
        self.linechar = "="
        self.data = enums
        # self.enumls = [ SVEnuml((name, num, cmt, idx, size, name_base)) \
        #                for name, num, cmt, idx, size, name_base in \
        #                zip( self.names, self.nums, self.cmts, self.idxs, self.sizes, self.name_bases) ]
        self.enumls = [SVEnuml(d) for d in zip(*self.data)]

    def __str__(self):
        slst = [str(i) + ":" + x.__str__() for i, x in enumerate(self.enumls)]
        return "[ " + " , ".join(slst) + " ]"


class SVEnuml(SVclass):
    """ enum literal """

    field = enumlfield

    def __init__(self, enuml=None):
        self.w = 20
        self.linechar = "="
        self.data = enuml

    def __repr__(self):
        type_ = type(self)
        module = type_.__module__
        qualname = type_.__qualname__
        return f"<{module}.{qualname} {self.name} at {hex(id(self))}>"

    def __str__(self):
        return f"<SVEnuml: {self.name}>"


class SVRegbk(SVutil):
    """
    Register bank information parsed from a *Regbk package
        regfields: SVEnums
    """

    def __init__(self, pkg):
        self.customlst = [
            "regfield_suf",
            "default_suf",
            "bw_suf",
            "arr_num_suf",
            "reserved_name",
            "regaddr_name",
            "regaddr_arr_name",
            "regbw_name",
            "regaddrbw_name",
            "regbsize_name",
            "regbsizebw_name",
            "regintr_name",
        ]
        self.userfunclst = ["ShowAddr"]
        self.regfield_suf = "_regfield"
        self.default_suf = "_DEFAULT"
        self.bw_suf = "_BW"
        self.arr_num_suf = "_NUM"
        self.reserved_name = "RESERVED"
        self.regaddr_name = "regaddr"
        self.regaddr_arr_name = "regaddr_arr"
        self.regbw_name = "REG_BW"
        self.regaddrbw_name = "REG_ADDR_BW"
        self.regbsize_name = "REG_BSIZE"
        self.regbsizebw_name = "REG_BSIZE_BW"
        self.regintr_name = "raw_intr_stat"

        self.name = pkg.name
        self.verbose = V_(VERBOSE)
        self.w = 20
        self.pkg = pkg
        self.addrs = pkg.enums.get(self.regaddr_name)
        self.addrs = SVEnums(self.addrs) if self.addrs else None
        self.addrsdict = {x.name: x for x in self.addrs.enumls} if self.addrs else None
        self.regaddrs = self.addrs
        self.regaddrsdict = self.addrsdict
        self.regaddrsreversedict = (
            {v: k for k, v in self.addrsdict.items()} if self.addrsdict else None
        )
        self.regaddrs_arr = pkg.enums.get(self.regaddr_arr_name)
        self.regaddrs_arr = SVEnums(self.regaddrs_arr) if self.regaddrs_arr else None
        self.regaddrs_arrdict = (
            {x.name: x for x in self.regaddrs_arr.enumls} if self.regaddrs_arr else None
        )
        self.regbw = pkg.params.get(self.regbw_name)
        self.regaddrbw = pkg.params.get(self.regaddrbw_name)
        self.regbsize = pkg.params.get(self.regbsize_name)
        self.regbsizebw = pkg.params.get(self.regbsizebw_name)
        self.regtypes = {}
        self.regmembtypes = {}
        self.regfields = {}
        self.regslices = {}
        self.regdefaults = {}
        self.regbws = {}
        self.params = {}
        self.raw_intr_stat = self.GetType(self.regintr_name)
        for i, v in pkg.paramsdetail.items():
            _v = SVParam(v)
            self.params[i] = _v
            _s = i.split(self.default_suf)
            if len(_s) == 2:
                self.regdefaults[_s[0]] = _v
            _s = i.split(self.bw_suf)
            if len(_s) == 2:
                self.regbws[_s[0]] = _v
        for i, v in pkg.enums.items():
            self.EnumToRegfield(i, v)
        for i, v in pkg.types.items():
            while True:
                _v = v[0]
                subt = pkg.types.get(SVType(_v).tp)
                if len(v) == 1 and subt:
                    v = subt
                else:
                    break
            _v = [SVType(vv) for vv in v]
            tt = [self.GetType(vv.tp) for vv in _v]
            self.regtypes[i.upper()] = _v
            self.regmembtypes[i.upper()] = tt
        if self.addrsdict:
            for k in self.addrsdict.keys():
                tp = self.regtypes.get(k)
                if type(tp) == list and k not in self.regslices:
                    self.StructToRegfield(k, tp)
        # self.regfields = pkg. TODO reg fields, defaults etc...

    def GetDefaultsStr(self, name, lst=False):
        reg = self.regaddrsdict.get(name)
        d = self.regdefaults.get(name)
        if not d:
            d = self.regdefaults.get(reg.name_base)
        if not d:
            return None
        if lst:
            _s = d.numstrlst
        else:
            _s = d.numstr
        return _s

    def GetBWStr(self, name, lst=False):
        reg = self.regaddrsdict.get(name)
        bw = self.regbws.get(name)
        if not bw:
            bw = self.regbws.get(reg.name_base)
        if not bw:
            return None
        try:
            if lst:
                _s = bw.numstrlst
            else:
                _s = bw.numstr
        except:
            _s = str(bw)
        return _s

    def GetType(self, tp):
        tp = self.pkg.AllType.get(tp)
        return [SVType(t) for t in tp] if tp else None

    def EnumToRegfield(self, name, enum):
        _v = SVEnums(enum)
        _s = name.split(self.regfield_suf)
        if len(_s) == 2:
            self.regfields[_s[0]] = _v
            pre_slice = 0
            self.regslices[_s[0]] = []
            _regslices = [
                (name, [(start, end - 1)])
                for name, start, end in zip(
                    _v.names, _v.nums, _v.nums[1:] + [self.regbw]
                )
            ]
            reserved = []
            for ii in _regslices:
                if self.reserved_name in ii[0]:
                    reserved.append(ii[1][0])
                else:
                    self.regslices[_s[0]].append(ii)
            if len(reserved) != 0:
                self.regslices[_s[0]] += [(self.reserved_name, reserved)]

    def StructToRegfield(self, name, struct):
        """struct is list of SVType"""
        regfield = SVEnums([[] for i in enumsfield.dic])
        regslice = []
        rev = [i for i in struct]
        rev.reverse()
        num = 0
        for i in rev:
            regfield.cmts.append(i.cmts)
            regfield.nums += [num]
            regfield.names += [f"{name}_{i.name}".upper()]
            regslice += [(i.name.upper(), [(num, num + i.bw - 1)])]
            num += i.bw
        if num < self.regbw - 1:
            regfield.nums += [num]
            regfield.names += [f"{name.upper()}_RESERVED"]
            regslice += [("RESERVED", [(num, self.regbw - 1)])]
            regfield.cmts.append([""])
        self.regslices[name] = regslice
        import itertools

        regfield.enumls = [SVEnuml(d) for d in itertools.zip_longest(*regfield.data)]
        self.regfields[name] = regfield
        self.regbws[name] = num

    def GetAddrCmt(self, reg):
        cmt = self.addrsdict[reg].cmt
        return self.GetCmt(cmt)

    def GetCmt(self, cmt):
        width = ""
        rw = ""
        arr = ""
        omit = ""
        comb = ""
        _ = ""
        for c in cmt:
            if type(c) != str:
                continue
            if re.search(r"RW|R/W|RO|WO|RC|W1C", c):
                rw = c.lstrip().rstrip()
                continue
            if re.search(r"\d", c):
                width = c.lstrip().rstrip()
                continue
            if re.search(r"arr|ARR", c):
                arr = c.lstrip().rstrip()
                continue
            if re.search(r"omit|OMIT", c):
                omit = c.lstrip().rstrip()
                continue
            if re.search(r"comb|COMB", c):
                comb = c.lstrip().rstrip()
                continue
        return width, rw, arr, omit, comb, _

    def GetAddrNField(self, reg):
        """
        Return the address and regfield given the register name
        the address is multiplied by regaddrbw
        """
        # TODO  multi-dimensional register
        if type(reg) == int:
            addr = reg
        else:
            addr = self.regaddrsdict[reg].num * self.regbsize
        regfield = self.regfields.get(reg)
        nums = regfield.nums if regfield else [0]
        names = regfield.names if regfield else None
        return addr, nums, names

    def GetAddr(self, reg):
        if type(reg) == int:
            addr = reg
        elif type(reg) == tuple:
            addr = self.GetAddrNField(reg[0])[0]
            offset = reg[1] * self.regbsize
            addr += offset
        elif type(reg) == str:
            addr = self.GetAddrNField(reg)[0]
        else:
            raise TypeError("un-recognized register sequence type")
        return addr

    def RegWrite(self, reg, datalst):
        """
        Return the address ,packed data and register fields names given register name
        and list of data of each register fields.
        """
        addr, regnums, regnames = self.GetAddrNField(reg)
        data = self.RegfieldPack(regnums, datalst)
        return addr, data, regnames

    def RegRead(self, reg, data):
        """
        Return the address ,extracted data fields and register fields names given register name
        and read data.
        """
        addr, regnums, regnames = self.GetAddrNField(reg)
        datalst = self.RegfieldExtract(regnums, data)
        return datalst, regnames

    def ShowAddr(self, valuecb=hex):
        print(f"{self.pkg.name:-^{3*self.w}}")
        SVEnuml().ShowField
        SVEnuml().ShowLine
        for i in self.regaddrs.enumls:
            print(
                i.ShowDataCb(
                    [
                        None,
                        lambda x: str(x) + " " + hex(x * self.regbsize).upper(),
                        None,
                    ]
                )
            )

    def ShowRegfield(self, name):
        pass

    def RegfieldPack(self, regfieldlst, datalst):
        """
        The function packs the provided data list
        based on each fields to a data of bandwidth self.regbw.
        regfieldlst consists of a list
        Ex: [0,6,31]; the first data will be packed to data[5:0], then data[30:6] and data[31]
        this list corresponds to self.regfield['reg name'].nums
        If the last field reaches the MSB of the register, don't specify the end.
        Ex: [0,16] indicates two 16bit field on a 32b register
        """
        data = 0
        try:
            iterator = iter(datalst)
        except TypeError:
            datalst = [datalst]
        else:
            pass
        for f, d in zip(regfieldlst, datalst):
            data = data + (d << f)
        msk = (1 << self.regbw) - 1
        data = data & msk
        return data

    def RegfieldExtract(self, regfieldlst, data):
        """
        Given the regfield list and a data, extract each fields' bit slice
        Co-test with RegfieldPack by:
            datalst == g.regbk.RegfieldExtract( regfieldlst, g.regbk.RegfieldPack( regfieldlst, datalst))
            Ex:g.regbk.RegfieldExtract( [0,5,17,30,31], g.regbk.RegfieldPack( [0, 5, 17, 30, 31], [31, 1033, 2033, 0, 1]))
        """
        datalst = []
        for s, e in zip(regfieldlst, regfieldlst[1:] + [self.regbw]):
            msk = (1 << e) - 1
            datalst.append((data & msk) >> s)
        return datalst[0] if len(datalst) == 1 else datalst

    def RegfieldUnitTest(self):
        field = [[0, 5, 17, 30, 31], [0, 8, 15]]
        datalst = [[31, 1033, 2033, 0, 1], [56, 22, 55]]
        err = []
        for f, d in zip(field, datalst):
            _d = self.RegfieldExtract(f, self.RegfieldPack(f, d))
            self.print(_d)
            err += [_d == d]
        return err
