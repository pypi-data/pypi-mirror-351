"""
List of all available instruments loaded from the <data> folder.

@author: rfetick
"""

import sys
import os
from configparser import ConfigParser
from astropy.io import fits
import numpy as np
from scipy.interpolate import interp2d

from maoppy.utils import circarr as _circarr
from maoppy.utils import RAD2ARCSEC as _RAD2ARCSEC
from maoppy.utils import binning as _binning

#%% INSTRUMENT CLASS
class Instrument:
    """Represents an optical system (telescope to detector)
    
    Attributes
    ----------
    D : float
        Entrance aperture diameter [meter]
    occ : float
        Aperture occultation ratio
    resolution_rad : float
        Resolution [rad]
    filters : dict
        Dictionary of available filters as tuples (central wvl, width) [meter]
    Nact : int
        Linear number of AO actuators
    gainADU : float
        Detector gain [e-/ADU]
    RON : float
        Detector read out noise [e-]
    binning : int
        Pixel binning factor (default=1)
    """

    def __init__(self, D=None, occ=0., res=None, Nact=0, gain=1., ron=1.):
        
        if D is None:
            raise ValueError("Please enter keyword `D` to set Instrument's aperture diameter")
        if res is None:
            raise ValueError("Please enter keyword `res` to set instrument resolution in rad")
        if D <= 0:
            raise ValueError("Keyword `D` must be strictly positive")
        if res <= 0:
            raise ValueError("Keyword `res` must be strictly positive")
        
        self.D = D
        self.occ = occ # occultation diameter ratio
        self.filters = {}
        self.Nact = Nact
        self.aliasing = 0
        self.correction_shape = 'circle' # or 'square'
        
        self._resolution_rad = res
        self.gain = gain
        self.ron = ron
        self.binning = 1
        
        self.name = "default" # unique identifier name
        self.fullname = "MAOPPY Instrument" # human readable name
        
        # phasemask (not tested yet)
        self.phasemask_enable = False
        self.phasemask_path = None
        self.phasemask_shift = (0.0,0.0)
        self._phasemask = None
        
    def __str__(self):
        s  = "---------------------------------\n" 
        s += self.fullname+"\n"
        s += "---------------------------------\n" 
        s += "Diameter   : %.2f m   (occ=%u%%)\n" % (self.D,self.occ*100)
        s += "Pixel scale: %.1f mas (binning=%u)\n" % (self.resolution_mas,self.binning)
        s += "Nb act     : %u\n" % self.Nact
        keys = tuple(self.filters.keys())
        s += "Filters    : "
        for k in keys:
            s += "%s " % k
        s += "\n"
        s += "Detector   : gain=%.1f e-/ADU\n"%self.gain
        s += "             RON =%.1f e-\n"%self.ron
        s += "Phasemask  : %s\n"%self.phasemask_enable
        s += "---------------------------------\n" 
        return s
    
    @property
    def resolution_rad(self):
        """Pixel resolution in radians"""
        return self._resolution_rad * self.binning
    
    @property
    def resolution_mas(self):
        """Pixel resolution in milli-arcsec"""
        return self.resolution_rad * _RAD2ARCSEC * 1e3
    
    def pupil(self,shape,wvl=None,samp=None):
        """Returns the 2D array of the pupil transmission function (complex data)"""
        Dpix = min(shape)/2
        pup = _circarr(shape)
        if self.phasemask_enable:
            if self._phasemask is None:
                if self.phasemask_path is None:
                    raise ValueError('phasemask_path must be defined')
                p = fits.open(self.phasemask_path)[0].data * 1e-9 # fits data in nm, converted here to meter
                x = np.arange(p.shape[0])/p.shape[0]
                y = np.arange(p.shape[1])/p.shape[1]
                self._phasemask = interp2d(x,y,p)
            cx,cy = self.phasemask_shift
            x = np.arange(shape[0])/shape[0] - cx/shape[0]
            y = np.arange(shape[1])/shape[1] - cy/shape[1]
            if wvl is None:
                wvl = self.wvl(samp) # samp must be defined if wvl is None
            wf = np.exp(2j*np.pi/wvl*self._phasemask(x,y))
        else:
            wf = 1.0 + 0j # complex type for output array, even if real data
        return (pup < Dpix) * (pup >= Dpix*self.occ) * wf
    
    def samp(self,wvl):
        """Returns sampling value for the given wavelength"""
        return wvl/(self.resolution_rad*self.D)
    
    def wvl(self,samp):
        """Returns wavelength for the given sampling"""
        return samp*(self.resolution_rad*self.D)


def pupil(shape, occ=0):
    """
    Returns a circular pupil, possibly obstructed in the center
    """
    sx = shape[0]
    sy = shape[1]
    xx,yy = np.mgrid[0:sx,0:sy]
    cx = (sx-1) / 2 # same convention as 'circarr'
    cy = (sy-1) / 2
    xx = xx - cx
    yy = yy - cy
    rr = np.sqrt(xx**2 + yy**2)
    Rpix = min([sx,sy])/2 # same convention as 'Instrument.pupil'
    return (rr < Rpix) * (rr >= (Rpix*occ))


def pupil_vlt(shape, angle=0, oversamp=1):
    """
    Returns the VLT pupil, rotated by <angle> (rad).
    The keyword <oversamp> allows better sampling for smoother spiders
    """
    ### VLT PARAMETERS
    occ = 0.14
    D = 8
    spider_width_m = 0.05
    ### NUMERICAL VALUES
    sx = shape[0] * oversamp
    sy = shape[1] * oversamp
    Rpix = min([sx,sy])/2 # same convention as 'Instrument.pupil'
    pix_size_m = D/(2*Rpix)
    spider_width_pix = spider_width_m / pix_size_m
    ### CENTERED and ROTATED ARRAYS
    xx0,yy0 = np.mgrid[0:sx,0:sy]
    cx = (sx-1) / 2 # same convention as 'circarr'
    cy = (sy-1) / 2
    xx0 = xx0 - cx
    yy0 = yy0 - cy
    xx = np.cos(angle)*xx0 + np.sin(angle)*yy0
    yy = np.cos(angle)*yy0 - np.sin(angle)*xx0
    ### CIRCULAR PUPIL (with central occultation)
    rr = np.sqrt(xx**2 + yy**2)
    pup = (rr < Rpix) * (rr >= (Rpix*occ))
    ### SPIDER 1
    a = np.tan(5.5*np.pi/180)
    x0 = - Rpix
    y0 = 0
    spider1 = np.abs(yy-(a*(xx-x0)+y0)) <= (spider_width_pix/2)
    spider1 *= (xx<0)
    ### SPIDER 2
    x0 = 0
    y0 = Rpix
    spider2 = np.abs(xx-(a*(yy-y0)+x0)) <= (spider_width_pix/2)
    spider2 *= (yy>0)
    ### SPIDER 3
    x0 = Rpix
    y0 = 0
    spider3 = np.abs(yy-(a*(xx-x0)+y0)) <= (spider_width_pix/2)
    spider3 *= (xx>0)
    ### SPIDER 4
    x0 = 0
    y0 = - Rpix
    spider4 = np.abs(xx-(a*(yy-y0)+x0)) <= (spider_width_pix/2)
    spider4 *= (yy<0)
    ### FINALIZE
    pup_total = pup*(1-spider1)*(1-spider2)*(1-spider3)*(1-spider4)
    if oversamp>1:
        return _binning(pup_total, oversamp) / oversamp**2
    return pup_total


def petal_vlt(shape, angle=0, oversamp=1):
    """
    Returns the four VLT petals, rotated by <angle> (rad).
    The keyword <oversamp> allows better sampling for smoother spiders
    """
    ### VLT PARAMETERS
    occ = 0.14
    D = 8
    spider_width_m = 0.05
    ### NUMERICAL VALUES
    sx = shape[0] * oversamp
    sy = shape[1] * oversamp
    Rpix = min([sx,sy])/2 # same convention as 'Instrument.pupil'
    pix_size_m = D/(2*Rpix)
    spider_width_pix = spider_width_m / pix_size_m
    ### CENTERED and ROTATED ARRAYS
    xx0,yy0 = np.mgrid[0:sx,0:sy]
    cx = (sx-1) / 2 # same convention as 'circarr'
    cy = (sy-1) / 2
    xx0 = xx0 - cx
    yy0 = yy0 - cy
    xx = np.cos(angle)*xx0 + np.sin(angle)*yy0
    yy = np.cos(angle)*yy0 - np.sin(angle)*xx0
    ### CIRCULAR PUPIL (with central occultation)
    rr = np.sqrt(xx**2 + yy**2)
    pup = (rr < Rpix) * (rr >= (Rpix*occ))
    ### SPIDER 1
    a = np.tan(5.5*np.pi/180)
    x0 = - Rpix
    y0 = 0
    spider1_top = (yy-(a*(xx-x0)+y0)) >= (spider_width_pix/2)
    spider1_bot = (yy-(a*(xx-x0)+y0)) <= (-spider_width_pix/2)
    ### SPIDER 2
    x0 = 0
    y0 = Rpix
    spider2_top = (xx-(a*(yy-y0)+x0)) >= (spider_width_pix/2)
    spider2_bot = (xx-(a*(yy-y0)+x0)) <= (-spider_width_pix/2)
    ### SPIDER 3
    x0 = Rpix
    y0 = 0
    spider3_top = (yy-(a*(xx-x0)+y0)) >= (spider_width_pix/2)
    spider3_bot = (yy-(a*(xx-x0)+y0)) <= (-spider_width_pix/2)
    ### SPIDER 4
    x0 = 0
    y0 = - Rpix
    spider4_top = (xx-(a*(yy-y0)+x0)) >= (spider_width_pix/2)
    spider4_bot = (xx-(a*(yy-y0)+x0)) <= (-spider_width_pix/2)
    ### PETALS
    petal1 = pup * spider1_top * spider2_bot
    petal2 = pup * spider1_bot * spider4_bot
    petal3 = pup * spider4_top * spider3_bot
    petal4 = pup * spider3_top * spider2_top
    if oversamp>1:
        petal1 = _binning(petal1, oversamp) / oversamp**2
        petal2 = _binning(petal2, oversamp) / oversamp**2
        petal3 = _binning(petal3, oversamp) / oversamp**2
        petal4 = _binning(petal4, oversamp) / oversamp**2
    all_petals = np.zeros((4,shape[0],shape[1]))
    all_petals[0,...] = petal1
    all_petals[1,...] = petal2
    all_petals[2,...] = petal3
    all_petals[3,...] = petal4
    return all_petals


def petal_mode_vlt(shape, angle=0, oversamp=1):
    """
    Return the 12 petal modes of VLT pupil for differential piston and tiptilt.
    These canonical modes are not orthonormalized.
    """
    petals = petal_vlt(shape, angle=angle, oversamp=oversamp)
    sx,sy = shape
    modes = np.zeros((12,sx,sy))
    ### CENTERED and ROTATED ARRAYS
    xx0,yy0 = np.mgrid[0:sx,0:sy]
    cx = (sx-1) / 2 # same convention as 'circarr'
    cy = (sy-1) / 2
    xx0 = (xx0 - cx)/(sx/2)
    yy0 = (yy0 - cy)/(sx/2)
    xx = np.cos(angle+np.pi/4)*xx0 + np.sin(angle+np.pi/4)*yy0
    yy = np.cos(angle+np.pi/4)*yy0 - np.sin(angle+np.pi/4)*xx0
    ### MODES
    for i in range(4):
        modes[i,...] = petals[i,...]
        modes[i+4,...] = petals[i,...]*xx
        modes[i+8,...] = petals[i,...]*yy
    return modes


#%% LOAD INSTRUMENT INSTANCES (make them attributes of this module)
# this might be clumsy, should I make something like this:
# from maoppy.instrument import load_instrument
# zimpol = load_instrument("zimpol")

def _get_data_folder():
    folder = os.path.abspath(__file__)
    folder = os.sep.join(folder.split(os.sep)[0:-1])+os.sep+'data'+os.sep
    return folder


def _get_all_ini(pth):
    return [f for f in os.listdir(pth) if f.endswith('.ini')]


def load_ini(pth):
    """Create an Instrument instance from a path to a .ini file"""
    config = ConfigParser()
    config.optionxform = str
    try:
        config.read(pth)
    except:
        raise FileNotFoundError("The instrument file has not been found")
    # [metadata]
    tag = config['metadata']['tag']
    name = config['metadata']['name']
    # [telescope]
    d = float(config['telescope']['d'])
    occ = float(config['telescope']['occ'])
    # [ao]
    nact = int(config['ao']['nact'])
    aliasing = float(config['ao']['aliasing'])
    try:
        correction_shape = config['ao']['correction_shape']
    except:
        correction_shape = 'circle'
    # [camera]
    res_mas = float(config['camera']['res_mas'])
    try:
        gain = float(config['camera']['gain'])
    except:
        gain = 1.0
    try:
        ron = float(config['camera']['ron'])
    except:
        ron = 1.0
    # [filters]
    filters = {}
    if 'filters' in config.keys():
        for filt in config['filters']:
            s = config['filters'][filt]
            wvl_central,width = s[1:-1].split(',')
            filters[filt] = (float(wvl_central)*1e-9,float(width)*1e-9)
    # Make instrument
    res_rad = res_mas*1e-3 / _RAD2ARCSEC
    instru = Instrument(D=d, occ=occ, res=res_rad, Nact=nact, gain=gain, ron=ron)
    instru.name = tag
    instru.fullname = name
    instru.filters = filters
    instru.aliasing = aliasing
    instru.correction_shape = correction_shape
    return instru
    


_this_module = sys.modules[__name__]
_d = _get_data_folder()
for _f in _get_all_ini(_d):
    _instru = load_ini(_d+_f)
    _n = _instru.name.lower().replace(" ","_") # format name
    setattr(_this_module, _n, _instru)
    
del _this_module, _d, _f, _instru, _n

