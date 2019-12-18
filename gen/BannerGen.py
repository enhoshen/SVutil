import os
import sys
sys.path.append(os.environ.get('SVutil'))
from SVparse import *
from SVgen import * 
from SVclass import *
import itertools
import numpy as np
import time
class BannerGen(SVgen):
    def __init__(self, ind=Ind(0)):
        self.cur_ind = ind 
        self.genpath = './'
        _time = time.localtime()
        self.yyyy, self.mm, self.dd = _time.tm_year, _time.tm_mon, _time.tm_mday
    def UserReg (self, name, email):
        self.name = name
        self.email = f'<{email}>'
    def FileReg (self, f):
        self.filepath = f
        _f = f.split('/')[-1].rsplit('.',1)
        self.filename = _f[0]
        _f = _f[-1] if len(_f) != 1 else ''
        self.filesuf = _f
    def TimeReg (self, yyyy, mm, dd):
        self.yyyy, self.mm, self.dd = yyyy, mm, dd 
class GanzinBanner(BannerGen):
    def __init__(self, ind=Ind(0)):
        super().__init__()
        self.svcopyrightstr = f'// Copyright (C) Ganzin Technology - All Rights Reserved\n'
        self.svstatementstr = \
              f'// ---------------------------\n'\
            + f'// Unauthorized copying of this file, via any medium is strictly prohibited\n'\
            + f'// Proprietary and confidential\n'\
            + f'//\n'\
            + f'// Contributors\n'\
            + f'// ---------------------------\n'
        self.pycopyrightstr = self.svcopyrightstr.replace('//','#')
        self.pystatementstr= self.svstatementstr.replace('//','#')
    def IncGuardStr(self):
        return f'__{self.filename.upper()}_{self.filesuf.upper()}__'
    def BannerBlk(self, suf='sv'):
        ind = self.cur_ind.Copy()
        yield ''
        s =''
        if suf == 'sv':
            s =  f'{ind.b}' + self.svcopyrightstr 
            s += f'{ind.b}' + self.svstatementstr
            s.replace ('\n', f'{ind.b}')
            s += f'{ind.b}//'
            s += f' {self.name} {self.email}, {self.yyyy}\n\n'
        elif suf == 'py' or suf == 'Makefile':
            s =  f'{ind.b}' + self.pycopyrightstr 
            s += f'{ind.b}' + self.pystatementstr
            s.replace ('\n', f'{ind.b}')
            s += f'{ind.b}#'
            s += f' {self.name} {self.email}, {self.yyyy}\n\n'
        yield s
    def IncGuardBlk(self):
        ind = self.cur_ind.Copy()
        yield ''
        s  = f'{ind.b}`ifndef {self.IncGuardStr()}\n'
        s += f'{ind.b}`define {self.IncGuardStr()}\n\n'
        yield s 
        yield f'\n{ind.b}`endif // {self.IncGuardStr()}'
    def BannerStr(self, fr, suf='sv'):
        fr = open(fr, 'r')
        ban = self.BannerBlk(suf)
        try:
            fstr = fr.read()
        except:
            print('file read not supported')
            return None
        s = self.Genlist( [(ban,), fstr] )
        return s
    def BannerIncguardStr(self, fr, suf='sv'):
        fr = open(fr, 'r')
        ban = self.BannerBlk(suf)
        incg = self.IncGuardBlk()
        try:
            fstr = fr.read()
        except:
            print('file read not supported')
            return None
        s = self.Genlist( [(ban,), (incg,), fstr, incg] )
        return s
    def BanWrite(self, fr=None, overwrite=False):
        '''
            Write Banner at the start of the file
            Arguments:
                fr = file name
                overwrite = True to write to the file, False to generate a new one
        '''
        fpath = self.Write(self.BannerStr, fr, overwrite)
        if (os.path.isfile(fpath)):
            print ( "Banner attached to ", fpath)
    def BanIncWrite(self, fr=None, overwrite=False):
        fpath = self.Write(self.BannerIncguardStr, fr, overwrite)
        if (os.path.isfile(fpath)):
            print ( "Banner, include guard attached to ", fpath)
    def Write(self, strcallback=None, fr=None, overwrite=False):
        '''
            Utility to write strings to files
        '''
        if not strcallback:
            strcallback = self.BannerStr
        if not fr:
            print('specify a file')
            return
        else:
            self.FileReg(fr)
        if not overwrite and os.path.isfile(self.filepath):
            print( "file exists, make a copy, rename the file right away")
            fpath = self.genpath + self.filename +'_'+ time.strftime('%m%d%H')
            if self.filesuf:
                fpath += '.' + self.filesuf
        else:
            fpath = self.filepath
        _suf = 'Makefile' if self.filename == 'Makefile' else self.filesuf
        if (os.path.isfile(fpath)):
            s = strcallback(fr, _suf)
            if not s:
                print('un-supported files or something went wrong')
                return ''
            f = open( fpath, 'w')
            f.write(s)
        return fpath
    def FolderBanWrite(self, _dir='.', overwrite=False):
        '''
            Write Banner to every files of provided folder _dir
                Arguments:
                    _dir = folder path
                    overwrite = True to write to the file, False to generate a new one
        '''
        for f in os.listdir(_dir):
            self.BanWrite(_dir+'/'+f, overwrite)
    def FolderBanIncWrite(self, _dir='.', overwrite=False):
        '''
            Write Banner and include guard to every files of the provided folder _dir
            This is meant for .sv files.
                Arguments:
                    _dir = folder path
                    overwrite = True to write to the file, False to generate a new one
        '''
        for f in os.listdir(_dir):
            self.BanIncWrite(_dir+'/'+f, overwrite)
if __name__ == '__main__':
    g = GanzinBanner()
    g.UserReg('En-Ho Shen', 'enhoshen@ganzin.com.tw')
    pass
