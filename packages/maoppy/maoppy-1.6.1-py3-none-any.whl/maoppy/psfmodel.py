"""
All PSF models available in this library.

@author: rfetick
"""

import sys
import numpy as np
from scipy.fft import fft2, ifft2, fftshift, ifftshift
from astropy.io import fits
from maoppy.utils import binning, random_sample
from maoppy.psfutils import moffat, gauss, oversample, moffat_center
from maoppy.zernike import zernike, ansi2nm
import warnings

__all__ = ["ParametricPSF", "ConstantPSF", "Moffat", "Gaussian",
           "ParametricPSFfromPSD", "Turbulent", "Psfao"]


_EPSILON = np.sqrt(sys.float_info.epsilon)

#%% CLASS PARAMETRIC PSF AND ITS SUBCLASSES
class ParametricPSF:
    """Super-class defining parametric PSFs
    Not to be instantiated, only serves as a referent for subclasses
    """
    
    def __init__(self, nparam, npix):
        """
        Parameters
        ----------
        npix : tuple of two elements
            Model X and Y pixel size when called
        """
        if not isinstance(nparam, int):
            raise TypeError("Argument `nparam` must be an integer")
        if not isinstance(npix, tuple):
            raise TypeError("Argument `npix` must be a tuple")
        self.npix = npix
        self._nparam = nparam
        self.bounds = ((-np.inf,)*nparam, (np.inf,)*nparam)
    
    def __str__(self):
        s  = self.__class__.__name__ + "\n"
        s += "-"*20 + "\n"
        s += "pixels  : (%u,%u)\n"%self.npix
        s += "nb param: %u"%self._nparam
        return s
    
    @property
    def param_name(self):
        """Ordered list of the parameters names"""
        return ["param_%u"%i for i in range(self._nparam)]
    
    @property
    def param_comment(self):
        """Comment on the parameters (self.param_name)"""
        return ["default name" for i in range(self._nparam)]
    
    def dict2list(self, dctnry):
        """Transform a dictionary of parameters into a list"""
        return [dctnry[k] for k in self.param_name]
    
    def list2dict(self, lst):
        """Transform a list of parameters into a dictionary"""
        return dict(zip(self.param_name,lst))
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("ParametricPSF is not made to be instantiated. Better use its subclasses")
    
    def otf(self, *args, **kwargs):
        """Return the Optical Transfer Function (OTF)"""
        psf = self.__call__(args,kwargs)
        return fftshift(fft2(psf))
    
    def mtf(self, *args, **kwargs):
        """Return the Modulation Transfer Function (MTF)"""
        return np.abs(self.otf(args,kwargs))
    
    def fits_header_read(self, hdr):
        """Read a FITS header and return PSF parameters.
        Also accepts a path to the FITS file."""
        if type(hdr)==str:
            fts = fits.open(hdr)
            hdr = fts[0].header
            fts.close()
        param = [0]*len(self.param_name)
        for i in range(len(self.param_name)):
            param[i] = float(hdr[self.param_name[i]])
        return param
    
    def fits_header_make(self, param):
        """Generate a FITS header and fill it with the given PSF parameters"""
        hdr = fits.Header()
        hdr['ORIGIN'] = 'MAOPPY automatic header'
        for i in range(len(param)):
            hdr[self.param_name[i]] = (param[i], self.param_comment[i])
        return hdr
    
    def fits_psf_write(self, param, filename, *args, **kwargs):
        """Write PSF into a FITS file"""
        psf = self.__call__(param, *args, **kwargs)
        hdr = self.fits_header_make(param)
        hdu = fits.PrimaryHDU(psf, hdr)
        hdu.writeto(filename)


class ConstantPSF(ParametricPSF):
    """Create a constant PSF, given as a 2D image, using ParametricPSF formalism
    With such a formalism, a constant PSF is just a particular case of a parametric PSF
    """
    def __init__(self,image_psf):
        super().__init__(0, np.shape(image_psf))
        self.image_psf = image_psf
        
    def __call__(self,*args,**kwargs):
        return self.image_psf


class Moffat(ParametricPSF):
    """Moffat PSF model"""
    def __init__(self, npix, norm=np.inf):
        super().__init__(4, npix)
        self.norm = norm
        bounds_down = [_EPSILON,_EPSILON,-np.inf,1+_EPSILON]
        bounds_up = [np.inf for i in range(4)]
        self.bounds = (bounds_down,bounds_up)
        
        self._xxyy = np.mgrid[0:npix[0],0:npix[1]]
        self._xxyy[0] -= npix[0]//2
        self._xxyy[1] -= npix[1]//2
    
    @property
    def param_name(self):
        """Ordered list of the parameters names"""
        return ["alpha_x","alpha_y","theta","beta"]
    
    def __call__(self, param, dx=0, dy=0):
        """
        Parameters
        ----------
        param : list, tuple, numpy.ndarray (len=4)
            param[0] - Alpha X
            param[1] - Alpha Y
            param[2] - Theta
            param[3] - Beta
        """
        paramdxdy = np.concatenate((param,[dx,dy]))
        return moffat(self._xxyy, paramdxdy, norm=self.norm)


class Gaussian(ParametricPSF):
    """Gaussian PSF model"""
    def __init__(self, npix):
        super().__init__(3, npix)
        bounds_down = [_EPSILON,_EPSILON,-np.inf]
        bounds_up = [np.inf for i in range(3)]
        self.bounds = (bounds_down,bounds_up)
        
        self._xxyy = np.mgrid[0:npix[0],0:npix[1]]
        self._xxyy[1] -= npix[0]/2
        self._xxyy[0] -= npix[1]/2
    
    @property
    def param_name(self):
        """Ordered list of the parameters names"""
        return ["sigma_x","sigma_y","theta"]
    
    def __call__(self, param, dx=0, dy=0):
        """
        Parameters
        ----------
        param : list, tuple, numpy.ndarray (len=4)
            param[0] - Sigma X
            param[1] - Sigma Y
            param[2] - Theta
        """
        paramdxdy = np.concatenate((param,[dx,dy]))
        return gauss(self._xxyy, paramdxdy)


#%% MASTER CLASS
class ParametricPSFfromPSD(ParametricPSF):
    """
    This class is NOT to be instantiated
    
    Attributes
    ----------
    system : maoppy.Instrument
        Do not modify `system` after __init__.
    samp : float
        Required sampling (samp=2 for Shannon).
    npix : (float,float)
        Number of desired pixels for output arrays.
    otfDiffraction: np.array
        Beware that the array is numerically oversampled when samp<2.
        Do not use this method when samp<2 or be sure of what you do.
    
    Methods
    -------
    strehlOTF : compute Strehl ratio from OTF ratio (recommanded).
    strehlMarechal : compute Strehl ratio using Marechal approximation (only in high Strehl case).
    psd : return the phase PSD.
    otf : return the OTF.
    __call__ : return the PSF.
    tofits : write a FITS file of the PSF.
    """
    
    def __init__(self, nparam, npix, system=None, samp=None, fixed_k=None):
        if not (type(npix) in [tuple,list,np.ndarray]):
            raise ValueError("npix must be a tuple, list or numpy.ndarray")
        if len(npix)!=2:
            raise ValueError("npix must be of length = 2")
        if (npix[0]%2) or (npix[1]%2):
            raise ValueError("Each npix component must be even")
        if system is None:
            raise ValueError("Keyword `system` must be defined")
        if samp is None:
            raise ValueError("Keyword `samp` must be defined")
        
        self._fx_fy = None
        self._xx = None
        self._yy = None
        self._fx2 = None
        self._fy2 = None
        self._fxy = None
        self._f2 = None
        self._otfStatic = None
        self._otfDiffraction = None
        self._jitter_mas = 0
        self._otfJitter = 1
        
        self.fixed_k = fixed_k
        self.system = system
        self._npix = npix # "_" to bypass the _computeXYarray update, that will be made with samp setter
        self._zernike = None # list of Zernike coefficients for static PSF
        self.samp = samp # also init _computeXYarray and _otfDiffraction
        self._nparam = nparam
        self.bounds = ((-np.inf,)*nparam, (np.inf,)*nparam)
        
      
    def __str__(self):
        s  = super().__str__() + '\n'
        s += "system  : %s\n"%self.system.name
        s += "jitter  : %.2f mas\n"%self.jitter_mas
        if self.zernike is None:
            znorm = 0
        else:
            znorm = np.sqrt(np.sum(np.array(self.zernike)**2))
        s += "zernike : %.2f rad"%znorm
        return s  
      
        
    @property
    def npix(self):
        """Number of required pixels for arrays"""
        return self._npix
    
    
    @npix.setter
    def npix(self, value):
        self._npix = value
        self._computeXYarray()
        self._computeOtfDiffraction()
        
        
    @property
    def npixOver(self):
        """
        Return the number of pixels for the correctly sampled array
        (at least at Shannon-Nyquist)
        """
        return self.npix[0]*self._k, self.npix[1]*self._k
    
        
    @property
    def samp(self):
        """Sampling of the output PSF"""
        return self._samp_over/self._k
    
    
    @samp.setter
    def samp(self, value):
        # Manage cases of undersampling
        self._samp_over, self._k = oversample(value, fixed_k = self.fixed_k)
        self._computeXYarray()
        self._computeOtfDiffraction()
        
    @property
    def zernike(self):
        return self._zernike
    
    @zernike.setter
    def zernike(self, value):
        self._zernike = value
        self._computeOtfDiffraction()
        
    def _computeXYarray(self):
        nx,ny = self.npixOver
        xyarray = np.mgrid[0:nx, 0:ny].astype(float)
        xyarray[0] -= nx//2
        xyarray[1] -= ny//2
        self._fx_fy = xyarray * self.pix2freq
        self._xx = xyarray[1]/ny
        self._yy = xyarray[0]/nx
        self._fx2 = self._fx_fy[0]**2.
        self._fy2 = self._fx_fy[1]**2.
        self._fxy = self._fx_fy[0]*self._fx_fy[1]
        self._f2 = self._fx2 + self._fy2
    
    
    @property
    def pix2freq(self):
        """Pixel to frequency conversion in the PSD plane"""
        return 1.0/(self.system.D*self._samp_over)
    
    
    @property
    def _nullFreqIndex(self):
        nx,ny = self.npixOver
        return nx//2, ny//2
    
    
    @property
    def otfDiffraction(self):
        """Return the diffraction OTF"""
        if self._k > 1:
            raise ValueError("Cannot call `otfDiffraction(...)` when undersampled")
        return fftshift(self._otfDiffraction)
    
    
    @property
    def psfDiffraction(self):
        psf = fftshift(np.real(ifft2(self._otfDiffraction)))
        k = int(self._k)
        if k==1:
            return psf
        return binning(psf,k) # undersample PSF if needed (if it was oversampled for computations)
    
    
    @property
    def jitter_mas(self):
        return self._jitter_mas
    
    
    @jitter_mas.setter
    def jitter_mas(self,val):
        self._jitter_mas = val
        xx,yy = np.mgrid[0:self.npix[0],0:self.npix[1]]
        dfx = 1/(self.npix[0]*self.system.resolution_mas)
        dfy = 1/(self.npix[1]*self.system.resolution_mas)
        xx = (xx - self.npix[0]//2)*dfx
        yy = (yy - self.npix[1]//2)*dfy
        # sigma = 1/val, but the writing below allows for val = 0
        g = np.exp(-0.5*((xx*val)**2 + (yy*val)**2))
        self._otfJitter = fftshift(g)
    
    
    def strehlOTF(self, parampsd, **kwargs):
        """Compute the Strehl ratio based on the sum of the OTF"""
        return np.real(np.sum(self._otf(parampsd, **kwargs))/np.sum(self._otfDiffraction))
    
    
    def strehlMarechal(self, parampsd, **kwargs):
        """
        Compute the Strehl ratio based on the Maréchal approximation.
        Note that `strehlOTF` might provide more accurate results.
        """
        _,sig2 = self.psd(parampsd, **kwargs)
        return np.exp(-sig2)
    
    
    def psd(self, parampsd, grad=False):
        """
        Compute the PSD.
        This method should be overriden in the subclasses.
        """
        raise NotImplementedError("ParametricPSFfromPSD is not to be instantiated. the `psd` method must be override in the subclasses")
    
    
    def check_parameters(self, parampsd):
        """Check whether input parameters comply with bounds"""
        bdn, bup = self.bounds
        parampsd = np.array(parampsd)
        bdn = np.array(bdn)
        bup = np.array(bup)
        if len(parampsd)!=self._nparam:
            raise ValueError('len(parampsd) is different from length of bounds')
        if np.any(parampsd<bdn):
            raise ValueError('Lower bounds are not respected')
        if np.any(parampsd>bup):
            raise ValueError('Upper bounds are not respected')
      
        
    def otf(self, parampsd, dx=0, dy=0, grad=False, **kwargs):
        """
        Public implemetation of the OTF.
        Only available if samp>=2.
        Null frequency is at the center of the array.
        
        Parameters
        ----------
        parampsd : list
            See the parameters of the `psd` method
            
        Keywords
        --------
        dx : float (default=0)
            Pixel shift of the PSF on X
        dy : float (default=0)
            Pixel shift of the PSF on Y
        grad : bool (default=False)
            Return OTF and its gradients if set to True
        **kwargs
            Extra keywords to be provided to the `psd` method
        """
        if self._k > 1:
            raise ValueError("Cannot call `otf(...)` when undersampled")
        if grad:
            otf, gg = self._otf(parampsd, dx=dx, dy=dy, grad=True, **kwargs)
            return fftshift(otf), fftshift(gg,axes=(1,2))
        
        otf = self._otf(parampsd, dx=dx, dy=dy, grad=False, **kwargs)
        return fftshift(otf)
    
    
    def _otf(self, parampsd, dx=0, dy=0, grad=False, **kwargs):
        """
        Private implementation of the OTF.
        It is correctly oversampled.
        Null frequency is at position [0,0].
        Computation should be slighly quicker than self.otf(...)
        """
        if (dx==0) and (dy==0):
            otfShift = 1.0
        else:
            otfShift = self._otfShift(dx,dy)
            
        if grad:
            otfTurb, gg = self._otfTurbulent(parampsd, grad=True, **kwargs)
            for i in range(gg.shape[0]):
                gg[i,:] *= self._otfStatic * otfShift
        else:
            otfTurb = self._otfTurbulent(parampsd, grad=False, **kwargs)
        
        otf = otfTurb * self._otfStatic * otfShift * self._otfJitter

        if grad:
            return otf, gg
        return otf
    
    
    def _otfTurbulent(self, parampsd, grad=False, **kwargs):
        """Atmospheric part of the OTF"""
        df2 = self.pix2freq**2
        if grad:
            psd, integral, gg, integral_g = self.psd(parampsd, grad=True, **kwargs)
        else:
            psd, integral = self.psd(parampsd, grad=False, **kwargs)
            
        Bphi = np.real(fft2(fftshift(psd))) * df2
        #Bphi = Bphi[0, 0] - Bphi # normalized on the numerical FoV 
        Bphi = integral - Bphi # normalized up to infinity
        otf = np.exp(-Bphi)
        
        if grad:
            gg2 = np.zeros(gg.shape,dtype=complex) # I cannot override 'g' here due to float to complex type
            for i in range(len(parampsd)):
                Bphi = np.real(fft2(fftshift(gg[i,...]))) * df2
                #Bphi = Bphi[0, 0] - Bphi # normalized on the numerical FoV
                Bphi = integral_g[i] - Bphi # normalized up to infinity
                gg2[i,...] = -Bphi*otf
            return otf, gg2
        return otf
    
    
    def _computeOtfDiffraction(self):
        """Precompute the diffraction part of the OTF"""
        nx, ny = self.npixOver
        npupx = int(np.ceil(nx/self._samp_over))
        npupy = int(np.ceil(ny/self._samp_over))
        pupil = self.system.pupil((npupx,npupy), samp=self._samp_over)
        phase = 0
        if self.zernike is not None:
            if npupx != npupy:
                raise ValueError('Zernike has not been implemented on rectangular arrays')
            phase = np.zeros((npupx,npupy))
            for i in range(len(self.zernike)):
                amp = self.zernike[i]
                phase += amp*zernike(*ansi2nm(i+3), npupx, samp=1)
        tab = np.zeros((nx, ny), dtype=complex)
        tab[0:npupx, 0:npupy] = pupil * np.exp(1j*phase)
        self._otfDiffraction = ifft2(np.abs(fft2(np.abs(tab)))**2) / np.sum(pupil)
        self._otfStatic = ifft2(np.abs(fft2(tab))**2) / np.sum(pupil)
    
    
    def _otfShift(self, dx, dy):
        """Shifting part of the OTF"""
        # Compensate oversampling shift
        dx += (self._k-1)/(2*self._k)
        dy += (self._k-1)/(2*self._k)
        # Compensate odd pixel shift
        dx -= (self.npix[1]%2)/2
        dy -= (self.npix[0]%2)/2
        return ifftshift(np.exp(-2j*np.pi*self._k*(dx*self._xx + dy*self._yy)))
    
    
    def short_exposure(self, parampsd):
        """
        Draw one random short exposure PSF.
        Exposures are temporally uncorrelated one from another.
        """
        psd, psd_integral = self.psd(parampsd)
        df = self.pix2freq
        L = 1/df
        random_phase = random_sample(psd, L)
        # copied from _otfDiffraction, I should make a unique function
        nx, ny = self.npixOver
        npupx = int(np.ceil(nx/self._samp_over))
        npupy = int(np.ceil(ny/self._samp_over))
        pup = np.zeros((nx, ny), dtype=complex)
        pup[0:npupx, 0:npupy] = self.system.pupil((npupx,npupy), samp=self._samp_over)
        em_field = pup * np.exp(1j*random_phase)
        return fftshift(np.abs(fft2(em_field)) ** 2) / np.abs(np.sum(pup)) / (nx*ny)
    
    
    def __call__(self, parampsd, dx=0, dy=0, grad=False, **kwargs):
        """
        Parameters
        ----------
        parampsd : numpy.array (dim=1), tuple, list
            Array of parameters for the PSD (see __doc__)
            
        Keywords
        --------
        dx : float (default = 0)
            PSF X shifting [pix].
        dy : float (default = 0)
            PSF Y shifting [pix].
        grad : boolean (default = False)
            Also compute gradients.
        """
        
        if grad:
            otf, gg = self._otf(parampsd, dx=dx, dy=dy, grad=True, **kwargs)
            for i in range(len(parampsd)):
                gg[i,...] = fftshift(np.real(ifft2(gg[i,...])))
        else:
            otf = self._otf(parampsd, dx=dx, dy=dy, grad=False, **kwargs)
        
        psf = fftshift(np.real(ifft2(otf)))
            
        k = int(self._k)
        if k==1:
            if grad: return psf, gg
            return psf
        
        if grad:
            gg2 = np.zeros((len(parampsd),psf.shape[0]//k,psf.shape[1]//k))
            for i in range(len(parampsd)):
                gg2[i,...] = binning(gg[i,...].astype(float),k)
            return binning(psf,k), gg2
        
        return binning(psf,k) # undersample PSF if needed (if it was oversampled for computations)


#%% TURBULENT PSF
class Turbulent(ParametricPSFfromPSD):
    """
    Summary
    -------
    PSF model dedicated to long-exposure imaging with turbulence
    p = Turbulent((npix,npix),system=system,samp=samp)
    
    Description
    -----------
    the PSF is parametrised through the PSD of the electromagnetic phase
        x[0] - Fried parameter r0 [m]
        x[1] - Von Karman external length [m]
    """
    def __init__(self, npix, system=None, samp=None):
        """
        Parameters
        ----------
        npix : tuple
            Size of output PSF
        system : OpticalSystem
            Optical system for this PSF
        samp : float
            Sampling at the observation wavelength
        """
        super().__init__(2,npix,system=system,samp=samp)
        
        # r0,L0
        bounds_down = [_EPSILON, _EPSILON]
        bounds_up = [np.inf, np.inf]
        self.bounds = (bounds_down,bounds_up)
    
    @property
    def param_name(self):
        """Ordered list of the parameters names"""
        return ["r0","lext"]
    
    def psd(self, parampsd, grad=False):
        """Compute the PSD model from parameters
        PSD is given in [rad²/f²] = [rad² m²]
        
        Parameters
        ----------
        parampsd : numpy.array (dim=1), tuple, list
            See __doc__ for more details
            
        Returns
        -------
        psd : numpy.array (dim=2)
        integral : float : the integral of the `psd` up to infinity
            
        """
        self.check_parameters(parampsd)
        nx0,ny0 = self._nullFreqIndex
        
        r0,lext = parampsd
        psd = 0.0229* r0**(-5./3.) * ((1./lext**2.) + self._f2)**(-11./6.)

        # Set PSD = 0 at null frequency
        psd[nx0,ny0] = 0.0
        
        # Compute PSD integral up to infinity
        fmax = np.min([nx0,ny0])*self.pix2freq
        integral_in = np.sum(psd*(self._f2<(fmax**2))) * self.pix2freq**2 # numerical sum (in the array's tangent circle)
        integral_out = 0.0229*6*np.pi/5 * (r0*fmax)**(-5./3.) # analytical sum (outside the array's tangent circle)
        integral = integral_in + integral_out
        
        if grad:
            gg = np.zeros((len(parampsd),)+self._f2.shape)
            gg[0,...] = psd*(-5./3)/r0
            gg[1,...] = psd*(-11./6)/((1./lext**2.) + self._f2)*(-2/lext**3)
            
            # compute integral gradient
            integral_g = [0,0]
            for i in range(2):
                integral_g[i] = np.sum(gg[i,...]*(self._f2<(fmax**2))) * self.pix2freq**2 # numerical sum (in the array's tangent circle)
            integral_g[0] += integral_out*(-5./3)/r0
        
        if grad:
            return psd, integral, gg, integral_g
        return psd, integral


#%% PSFAO MODEL        
class Psfao(ParametricPSFfromPSD):
    """
    Summary
    -------
    PSF model dedicated to long-exposure imaging with adaptive optics
    p = Psfao((npix,npix),system=system,samp=samp)
    
    Description
    -----------
    the PSF is parametrised through the PSD of the electromagnetic phase
        x[0] - Fried parameter           : r0 [m]
        x[1] - Corrected area background : C [rad² m²]
        x[2] - Moffat phase variance     : A [rad²]
        x[3] - Moffat width              : alpha [1/m]
        x[4] - Moffat elongation ratio   : sqrt(ax/ay)
        x[5] - Moffat angle              : theta [rad]
        x[6] - Moffat power law          : beta
        
    Reference
    ---------
    Fétick et al., August 2019, A&A, Vol.628
    """
    
    def __init__(self, npix, system=None, lext=10., samp=None, fixed_k=None):
        """
        Parameters
        ----------
        npix : tuple
            Size of output PSF
            
        Keywords
        --------
        system : Instrument
            Optical system for this PSF
        samp : float
            Sampling at the observation wavelength
        lext : float
            Von-Karman external scale (default = 10 m)
            Useless if Fao >> 1/lext
        fixed_k : int
            Define a fixed oversampling factor
        """
        self.lext = lext
        self._maskin = None
        self._vk = None
        super().__init__(7,npix,system=system,samp=samp,fixed_k=fixed_k)
        
        # r0,C,A,alpha,ratio,theta,beta
        ### Mathematical bounds
        #bounds_down = [_EPSILON,0,0,_EPSILON,_EPSILON,-np.inf,1+_EPSILON]
        #bounds_up = [np.inf for i in range(7)]
        ### Physical bounds
        bounds_down = [1e-3, 0, 0, 1e-5, 1e-2, -np.inf, 1.01]
        bounds_up = [np.inf]*4 + [1e2, np.inf, 5]
        self.bounds = (bounds_down,bounds_up)
    
    
    @property
    def cutoffAOfreq(self):
        """AO cutoff frequency due to limited number of corrected modes"""
        return self.system.Nact/(2.0*self.system.D)
    
    
    def _computeXYarray(self):
        super()._computeXYarray()
        if self.system.correction_shape=='circle':
            self._maskin = (self._f2 < self.cutoffAOfreq**2.)
        elif self.system.correction_shape=='square':
            fx,fy = self._fx_fy
            self._maskin = (np.abs(fx)<self.cutoffAOfreq)*(np.abs(fy)<self.cutoffAOfreq)
        else:
            raise ValueError('Instrument.correction_shape must be the string `circle` or `square`.')
        self._vk = (1-self._maskin) * 0.0229 * ((1. / self.lext**2.) + self._f2)**(-11./6.)
    
    
    @property
    def param_name(self):
        """Ordered list of the parameters names"""
        return ["r0","bck","amp","alpha","ratio","theta","beta"]
    
    @property
    def param_comment(self):
        """Comment on the parameters (self.param_name)"""
        comments = ["Fried parameter [m]",
                    "AO background [rad2 m2]",
                    "AO Moffat variance [rad2]",
                    "AO Moffat alpha [1/m]",
                    "AO Moffat sqrt(ax/ay) ratio",
                    "AO Moffat theta [rad]",
                    "AO Moffat beta"]
        return comments
    
    def var_corr(self, parampsd):
        """Return the numerical variance on the corrected area"""
        psd,_ = self.psd(parampsd)
        return np.sum(psd*self._maskin) * self.pix2freq**2
    
    
    def var_halo(self, parampsd, fovnorm=False):
        """Return the numerical variance on the halo (fitting error)"""
        psd,var_tot = self.psd(parampsd, fovnorm=fovnorm)
        var_corr = np.sum(psd*self._maskin) * self.pix2freq**2
        return var_tot - var_corr
        
    
    def var_total(self, parampsd, fovnorm=False):
        """Return total variance halo + corrected area"""
        _,var_tot = self.psd(parampsd, fovnorm=fovnorm)
        return var_tot
    
    
    def psd(self, parampsd, grad=False, fovnorm=False, nocheck=False):
        """Compute the PSD of the electromagnetic phase
        PSD is given in [rad²/f²] = [rad² m²]
        
        Parameters
        ----------
        parampsd : numpy.array (dim=1), tuple, list
            See __doc__ for more details
        grad : bool (default=False)
            Return both (psd,integral,gradient) if set to True
        fovnorm : bool (default=False)
            PSF normalized to unity on the numerical FoV (True) or to infinity (False)
        nocheck : bool (default=False)
            Do not check bounds
            
        Returns
        -------
        psd : numpy.array (dim=2)
        integral : float : the integral of the `psd` (according to `fovnorm`)
            
        """
        # parampsd can be called with a dictionary
        if isinstance(parampsd,dict):
            parampsd = self.dict2list(parampsd)
            
        if not nocheck:
            self.check_parameters(parampsd)
        nx0,ny0 = self._nullFreqIndex
        pix = self.pix2freq
        
        r0, bck, amp, alpha, ratio, theta, beta = parampsd
        
        if alpha < (2*pix):
            # well, the factor 2 is really empirical...
            warnings.warn("`alpha < 2*df`. Everything works fine but the value of `amp` might not correspond exactly to the PSD integral.")
        
        # Von-Karman
        psd = (r0**(-5./3.)) * self._vk
        
        # Moffat
        ax = alpha*ratio
        ay = alpha/ratio
        param = (ax,ay,theta,beta)
        
        remove_inside = (1+np.sqrt(2))/2 * pix/2 # remove central pixel in energy computation
        if grad:
            moff,dm = moffat_center(self._fx2, self._fxy, self._fy2, param,
                                    norm=self.cutoffAOfreq, removeInside=remove_inside, grad=True)
        else:
            moff = moffat_center(self._fx2, self._fxy, self._fy2, param,
                                 norm=self.cutoffAOfreq, removeInside=remove_inside, grad=False)
        moff *= self._maskin
        
        numerical_norm = False # set to true in order to activate code below
        if numerical_norm:
            moff[nx0,ny0] = 0.0 # Set Moffat PSD = 0 at null frequency
            moff = moff / (np.sum(moff)*pix**2)  # normalize moffat numerically to get correct A=sigma² in the AO zone
            if grad:
                raise ValueError("PSFAO analytical gradient computation is not compatible with numerical Moffat normalization")
            # Warning: Moffat numerical normalization generates strehlOTF jump when "_k" is changed
        
        psd += self._maskin * (bck + amp*moff)
        psd[nx0,ny0] = 0.0 # Set PSD = 0 at null frequency
        
        # Compute PSD integral up to infinity
        if fovnorm:
            integral = np.sum(psd) * pix**2
        else:
            fmax = np.min([nx0,ny0])*pix
            integral_in = np.sum(psd*(self._f2<(fmax**2))) * pix**2 # numerical sum on the array
            integral_out = 0.0229*6*np.pi/5 * (r0*fmax)**(-5./3.) # analytical sum outside
            integral = integral_in + integral_out
        
        if grad:
            gg = np.zeros((len(parampsd),)+self._f2.shape)
            # derivative towards r0
            gg[0,...] = psd*(1-self._maskin)*(-5./3)/r0
            # derivative towards bck
            gg[1,...] = self._maskin
            # derivative towards amp
            gg[2,...] = self._maskin*moff
            # derivative towards alpha
            gg[3,...] = amp*self._maskin*(dm[0,...]*ratio + dm[1,...]/ratio)
            # derivative towards ratio
            gg[4,...] = amp*self._maskin*(dm[0,...]*alpha - dm[1,...]*ay/ratio)
            # derivative towards theta
            gg[5,...] = amp*self._maskin*dm[2,...]
            # derivative towards beta
            gg[6,...] = amp*self._maskin*dm[3,...]
            # Remove central freq from all derivative
            gg[:,nx0,ny0] = 0
        
            # Compute integral gradient
            integral_g = np.zeros(len(parampsd))
            if fovnorm:
                for i in range(len(parampsd)):
                    integral_g[i] = np.sum(gg[i,...]) * pix**2 # numerical sum
            else:
                for i in range(len(parampsd)):
                    integral_g[i] = np.sum(gg[i,...]*(self._f2<(fmax**2))) * pix**2 # numerical sum
                integral_g[0] += integral_out*(-5./3)/r0
            
        if grad:
            return psd, integral, gg, integral_g
        return psd, integral
        
    
    def fits_header_make(self, param):
        """Generate a FITS header and fill it with the given PSF parameters"""
        hdr = super().fits_header_make(param)
        # hdr['CDELT1'] = (self.system.resolution_mas,"pixel size")
        # hdr['CUNIT1'] = ("mas","pixel size unit unit")
        # hdr['CDELT2'] = (self.system.resolution_mas,"pixel size")
        # hdr['CUNIT2'] = ("mas","pixel size unit unit")
        hdr["SYSTEM"] = (self.system.name,"System name")
        hdr["SAMP"] = (self.samp,"Sampling (eg. 2 for Shannon)")
        hdr["LEXT"] = (self.lext,"Von-Karman outer scale")
        return hdr



class PsfaoAliasing(Psfao):
    """
    Same as Psfao but without background parameter.
    The background is automatically set using `r0` and `system.aliasing`.
    """
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nparam = 6
        bd,bu = self.bounds
        self.bounds = ([bd[0]]+bd[2:],[bu[0]]+bu[2:])
    
    @property
    def param_name(self):
        pn = super().param_name
        return [pn[0]] + pn[2:]
    
    @property
    def param_comment(self):
        pc = super().param_comment
        return [pc[0]] + pc[2:]
    
    def psd(self, parampsd, *args, grad=False, **kwargs):
        """
        Same function as `Psfao.psd(...)`.
        `parampsd` only holds 6 parameters, the background one being removed.
        """
        # parampsd can be called with a dictionary (6 parameters)
        if isinstance(parampsd,dict):
            parampsd = self.dict2list(parampsd)
        
        self.check_parameters(parampsd)
        
        r0 = parampsd[0]
        var_fitting = 0.023*6*np.pi/5 * (r0*self.cutoffAOfreq)**(-5./3.)
        var_alias = self.system.aliasing * var_fitting # [rad²]
        surf_corr = np.pi * self.cutoffAOfreq**2 # [1/m²]
        bck = var_alias / surf_corr
        parampsd_seven = np.concatenate(([r0,bck],parampsd[1:]))
        
        out = super().psd(parampsd_seven, *args, grad=grad, nocheck=True, **kwargs)
        
        if grad:
            # I need to update the gradient and its integral!
            psd, integral, gg, integral_g = out
            dbck_dr0 = -5/3 * bck/r0
            newbckmsk = dbck_dr0*self._maskin
            gg[0,...] += newbckmsk
            integral_g[0] += np.sum(newbckmsk) * self.pix2freq**2
            gg = np.delete(gg, (1), axis=0)
            integral_g = np.delete(integral_g, (1), axis=0)
            return psd, integral, gg, integral_g
                
        return out
        