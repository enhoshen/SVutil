import os
import sys
sys.path.append(os.environ.get('SVutil'))
from SVparse import *
from SVgen import * 
from SVclass import *
import itertools
import numpy as np
class TestGen(SVgen):
    def __init__(self, ind=Ind(0)):
        super().__init__()
    def TbSVGen(self): 
        ind = self.cur_ind.Copy() 
        yield ''
        s = '\n'
        s += '`timescale 1ns/1ns\n'
        s += '`include ' + f'"{self.incfile}.sv"\n' 
        s += f'`define {self.endcyclemacro} 100\n'  
        s += f'`define {self.hclkmacro} 5\n'  
        s += 'module ' + TOPMODULE + ';\n'
        s = s.replace('\n',f'\n{ind.b}')
        yield s
        s = f'\nlogic {self.clkstr}, {self.rststr};\n`Pos(rst_out, {self.rststr})\n' +f'`PosIf(ck_ev , {self.clkstr}, {self.rststr})\n' + '`WithFinish\n\n' 
        s += f'always #`{self.hclkmacro} {self.clkstr}= ~{self.clkstr};\n\n'
        s += f'initial begin'
        s = s.replace('\n',f'\n{ind[1]}')
        _s =  f'\n$fsdbDumpfile("{self.fsdbname}.fsdb");\n' 
        _s +=  f'$fsdbDumpvars(0,{TEST},"+all");\n'
        _s +=  f'{self.clkstr} = 0;\n' + f'{self.rststr} = 1;\n'
        _s +=  '#1 `NicotbInit\n' 
        _s +=  '#10 rst = 0;\n' +  '#10 rst = 1;\n'
        _s +=  f'#(2*`{self.hclkmacro+"*`"+self.endcyclemacro}) $display("timeout");\n'
        _s +=  '`NicotbFinal\n' +  '$finish;'
        _s = _s.replace('\n',f'\n{ind[2]}')
        _s += f'\n{ind[1]}end\n\n'
        yield s+_s
        s = '\n' + ind.b +'endmodule'
        yield s
    def DeclareBlkGen(self ):
        pass
    def TopBlkGen(self , tpname ):
        ind = self.cur_ind.Copy()
        yield ''
        yield 
    def ModBlkGen(self):
        pass
    def LogicGen(self , module , **conf):
        ind = self.cur_ind.Copy()
        yield ''
        s = self.CommentBlkStr ( 'Logics' , ind)
        pfield = SVhier.portfield 
        for p in module.ports:
            if p[pfield.tp] == 'logic' or p[pfield.tp] == 'signed logic':
                s += f'{ind.b}{p[pfield.tp]} {p[pfield.bwstr]} {p[pfield.name]} {p[pfield.dimstr]};\n'
            else:
                s += f'{ind.b}{p[pfield.tp]} {p[pfield.name]} {p[pfield.dimstr]};\n' 
        yield s
    def ParamGen(self , module , **conf):
        ind = self.cur_ind.Copy()
        yield ''
        s = self.CommentBlkStr(  'Parameters' , ind )
        for pkg,param  in module.scope.imported.items():
            s += f'{ind.b}import {pkg}::{param};\n'
        pmfield = SVhier.paramfield
        for param,v in module.paramports.items():
            detail = module.paramsdetail[param]
            tpstr = detail[pmfield.tp] + ' ' if detail[pmfield.tp] != '' else ''
            bwstr = detail[pmfield.bwstr] + ' ' if detail[pmfield.bwstr] != '' else ''
            pmtp  = detail[pmfield.paramtype]
            s += f'{ind.b}{pmtp} {tpstr}{bwstr}{param} = {detail[pmfield.numstr]};\n'
        yield s
    def CommentBlkGen(self , s  ,width=35):
        ind = self.cur_ind.Copy()
        yield ''
        yield f'{ind.b}//{"":=<{width}}\n{ind.b}//{s:^{width}}\n{ind.b}//{"":=<{width}}\n'
    def CommentBlkStr(self, s , ind , width=35):
        return f'{ind.b}//{"":=<{width}}\n{ind.b}//{s:^{width}}\n{ind.b}//{"":=<{width}}\n'
    def InsGen(self , module , name='dut' ,  **conf):
        ind = self.cur_ind.Copy() 
        yield ''
        s = '\n'
        s += ind.base + module.hier + ' #(\n'
        s_param = ''
        for param,v in module.paramports.items():
            if module.paramsdetail[param][SVhier.paramfield.paramtype] == 'parameter':
                s_param += f'{ind[1]},.{param}({param})\n'
        s_param = s_param.replace(f'{ind[1]},' , ind[1]+' ', 1)
        sb = f'{ind.b}) {name} (\n'
        s_port =''
        for io , n , dim , *_ in module.ports:
            if 'clk' in n:
                s_port += ind[1] + ',.' + n + f'({self.clkstr})\n'
            elif 'rst' in n:
                s_port += ind[1] + ',.' + n + f'({self.rststr})\n'
            else:
                s_port += ind[1] + ',.' + n + (  (f'({n})\n') if dim ==() else (f'({{ >>{{{n}}} }})\n'))
                
        s_port = s_port.replace(f'{ind[1]},' , ind[1]+' ' , 1)
        s += s_param + sb + s_port + ind.base + ');\n' 
        yield s

    def TbPYGen(self):
        ind = self.cur_ind.Copy()
        yield ''
        s = '\n'
        s += f'{ind.b}from nicotb import *\n'
        s += f'{ind.b}import numpy as np \n'
        yield s
        s =  f'{ind.b}rst_out, ck_ev = CreateEvents(["rst_out" , "ck_ev"])\n\n'
        s += f'{ind.b}RegisterCoroutines([\n'
        s += f'{ind[1]}main()\n'
        s += f'{ind.b}])'
        yield s
    def NicoutilImportGen(self):
        ind = self.cur_ind.Copy()
        yield ''
        s = '\n'
        s +='import sys\n'
        s +='import os\n'
        s +='sys.path.append(os.environ.get(\'SVutil\'))\n'
        s +='from itertools import repeat\n'
        s +='from nicotb.primitives import JoinableFork\n'
        s +='from SVparse import SVparse,EAdict\n'
        s +='from sim.NicoUtil import *\n'
        s = s.replace('\n',f'\n{ind.b}') 
        yield s
    def PYbusinitGen(self,module):
        ind = self.cur_ind.Copy()
        yield ''
        s = '\n'
        s += f'{ind.b}def BusInit():\n'
        s += f'{ind[1]}SBC = StructBusCreator\n'
        s += f'{ind[1]}SBC.TopTypes()\n'
        s += f'{ind[1]}dic = {{}}\n'
        for p in module.ports:
            pfield = SVhier.portfield
            tp = p[pfield.tp]
            if tp == 'logic' or tp == 'signed logic':
                s += f'{ind[1]}dic[\'{p[pfield.name]}\'] = '
                s += f'CreateBus(( (\'\', \'{p[pfield.name]}\', {p[pfield.dim]},),  ))\n'
            else:
                s += f'{ind[1]}dic[\'{p[1]}\'] = SBC.Get(\'{p[3]}\' , \'{p[1]}\')\n'     
        s += f'{ind[1]}return Busdict(dic) # access by name without quotes\n'
        yield s
            
    def PYmainGen(self):
        ind = self.cur_ind.Copy()
        yield '' 
        s = '\n'
        s += f'{ind.b}def main():\n'
        s += f'{ind[1]}buses = BusInit()\n'
        s += f'{ind[1]}buses.SetToN()\n'
        s += f'{ind[1]}buses.Write() #don\' use this afterward if you\'re not sure what you\'re doing\n'
        s += f'{ind[1]}yield rst_out\n'
        s += f'{ind[1]}#j = []\n' 
        s += f'{ind[1]}#for jj in j:\n'
        s += f'{ind[1]}#    yield from jj.Join()\n'
        s += f'{ind[1]}#[jj.Destroy() for jj in j]\n'
        s += f'{ind[1]}FinishSim()\n' 
        yield s
 
    def ModuleTestSV(self , module=None , **conf):
        module = self.dut if not module else module
        ins = self.InsGen(module)
        pm = self.ParamGen(module)
        lg = self.LogicGen(module)
        tb = self.TbSVGen()
        ind = self.IndBlk()
        s = self.Genlist( [ (tb,) , tb , [ind,pm] , [ind,lg] , [ind,ins] , tb , tb]) 
        if (conf.get('copy')==True):
            ToClip(s)
        return s
        
    def ModuleTestPY(self , module=None , **conf):
        module = self.dut if not module else module
        tb = self.TbPYGen()
        nicoutil = self.NicoutilImportGen() 
        businit = self.PYbusinitGen(module)
        main = self.PYmainGen()
        s = self.Genlist( [(tb,nicoutil,businit,main), tb ] )
        if (conf.get('copy')==True):
            ToClip(s)
        return s
    def WriteModuleTestALL(self, module=None , **conf):
        module = self.dut if not module else module
        conf['copy']=False
        self.SVWrite(self.ModuleTestSV(module,**conf))
        self.PYWrite(self.ModuleTestPY(module,**conf)) 
    def ShowIns(self, module=None):
        module = self.dut if not module else module
        ins = self.InsGen(module)
        s =  self.Genlist( [(ins,)]) 
        ToClip(s)
        print(s)
    def SVWrite(self , text ):
        p = self.TbWrite(text,'sv') 
        print ( "SV testbench written to " , p )
    def PYWrite(self , text ):
        p = self.TbWrite(text,'py')
        print ( "PY testbench written to " , p )
    def TbWrite(self , text , suf): 
        fpath = self.genpath + self.test + '.' + suf
        if os.path.isfile(fpath):
            print( "file exists, make a copy, rename the file right away")
            import time
            fpath = self.genpath + self.test +'_'+ time.strftime('%m%d%H') +'.'+ suf 
        else:
            pass
        f = open( fpath,'w')
        f.write(text)
        return fpath
if __name__ == '__main__':
    g = TestGen()

