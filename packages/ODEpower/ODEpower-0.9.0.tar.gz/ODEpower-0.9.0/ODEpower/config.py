from dataclasses import dataclass

@dataclass
class settings:
    """ODEpower Settings"""
    DEBUG: bool = False
    LOG: bool = False 
    pySolver: str = 'LSODA' # ...
    casadiEnable: bool = True
    casadiPath: str = ''
    matlab_engine = None
    matlab_enable: bool = True 
    matlab_model_path: str = ''