#!/usr/bin/env python3 -i
if __name__ == "__main__":
    from SVutil.SVparse import *
    import sys
    import SVutil.SVutilCompleter
    from SVutil.gen.SrcGen import *
    from SVutil.gen.TestGen import TestGen
    from SVutil.gen.srcgen.RegbkGen import RegbkGen 
    from SVutil.gen.srcgen.ConnectGen import ConnectGen
    from SVutil.gen.drawiogen.InterfaceDiagramGen import InterfaceDiagramGen 
    from SVutil.gen.drawiogen.BlockDiagramGen import BlockDiagramGen 
    from SVutil.gen.LatexGen import LatexGen
    from SVutil.gen.BannerGen import GanzinBanner
    from SVutil.gen.xlgen.MemmapGen import MemmapGen
    session = SVparseSession(V_(VERBOSE))
    session.FileParse(paths=None)
    hiers = EAdict(session.hiers)
    try:
        gTest = TestGen(session=session)
    except:
        SVutil().print('TestGen initialization failed') 
    try:
        gRegbk = RegbkGen(session=session)
    except:
        SVutil().print('RegbkGen initialization failed') 
    try:
        gConnect= ConnectGen(session=session)
    except:
        SVutil().print('ConnectGen initialization failed') 
    try:
        gIFgen = InterfaceDiagramGen(session=session)
    except:
        SVutil().print('InterfaceGen initialization failed') 
    try:
        gBLgen = BlockDiagramGen(session=session)
    except:
        SVutil().print('BlockGen initialization failed') 
    try:
        gLatex = LatexGen(session=session)
    except:
        SVutil().print('LatexGen initialization failed') 
    gBanner = GanzinBanner()
    try:
        gmemmapxl = MemmapGen(session=session)
    except:
        SVutil().print('MemmapGen initialization failed') 
