from SVparse import * 
import os
class Ind():
    def __init__(self , n):
        self.n = n
        self.base = '' if n==0 else f'{" ":{4*n}}'
        self.b = self.base
    def __getitem__(self, n):
        return  self.base if n==0 else f'{" ":{4*(int(n)+self.n)}}' 
    def __iadd__ (self, n):
        self.n += n
        self.base = f'{" ":{4*self.n}}'
        return self
    def __isub__ (self,n):
        self.n -= n
        self.base = '' if self.n==0 else f'{" ":{4*self.n}}'
        return self 
    def __add__ (self, n):
        return Ind(self.n+n)
    def Copy(self):
        return Ind(self.n)
class SVgen():
    def __init__(self , paths=[(True,INC)] ):
        FileParse(paths)
        self.genlist = {}    
        self.hclkmacro = 'HCYCLE'
        self.endcyclemacro = 'TIMEOUTCYCLE'
        self.clkstr = 'clk'
        self.rststr = 'rst'
        self.test = TEST
        self.testname = TEST.rsplit('_tb')[0]
        self.fsdbname = self.testname + '_tb' #TODO
        self.topfile  = SV.rstrip('.sv')
        self.incfile  = INC
        self.dutname = TESTMODULE 
        self.dut = hiers.dic[self.dutname]
        self.dutfile = hiers.dic[self.dutname+'_sv']
        self.hier = hiers.dic[HIER] if HIER != '' else None
        self.regbkstr= hiers.dic[REGBK] if REGBK != '' else None
        self.genpath = './'
        self.endcycle = 10000
        self.cond = {} # syn 2ns test name etc.
        self.cur_ind = Ind(0)
    def IndBlk(self):
        ind = self.cur_ind.Copy() 
        yield ''
        while 1:
            yield ind.b + '\n' 
    def Genlist(self , structure):
        o = ''
        for strt in structure:
            if type(strt) == list:
                for v in strt:
                    next(v) # initialize
                    o += self.Nextblk(v)
                    self.cur_ind+=1
                strt.reverse()
                for v in strt:
                    o += self.Nextblk(v)
                    self.cur_ind-=1
            elif  type(strt) == tuple:
                for i in strt:
                    next(i)
                    o += self.Nextblk(i)
            else :
                o += self.Nextblk(strt)
        return o
    def Str2Blk(self, strcallback, *arg):
        ind = self.cur_ind.Copy()
        yield ''
        yield strcallback( *arg , ind=ind)
    def BlkGroup (self, *arg):
        ind = self.cur_ind.Copy()
        yield ''
        s = self.Genlist( [ tuple(arg) ])
        yield s 
    def GenStr( self , gen):
        s = ''
        for _s in gen:
            s += _s
        return s
    def Blkprint( self , gen):
        s = ''
        print ( self.GenStr(gen) )
    def Nextblk(self, blk):
        s = next(blk,None)
        return s if s != None else ''
if __name__ == "__main__":
    g = SVgen()
    pass
    #dut = hiers.Ahb2ToReqAckWrap
    #ins = g.InsGen(dut, 'u1' )  
    #lg = g.LogicGen(dut)
    #tb = g.TbSVGen()                                    
    #ind = g.IndBlk()                                     
    #g.Genlist( [ (tb,), tb , (lg,) , [ins] , tb , tb])
    #print(o)
