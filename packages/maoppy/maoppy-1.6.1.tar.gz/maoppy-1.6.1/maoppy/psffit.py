"""
Methods to fit a PSF model on data.

@author: rfetick
"""

import numpy as np
from scipy.optimize import least_squares


__all__ = ["lsq_flux_bck", "psffit"]


def lsq_flux_bck(model, data, weights, background=True, positive_bck=False):
    """Compute the analytical least-square solution for flux and background
    LS = SUM_pixels { weights*(flux*model + bck - data)² }
    
    Parameters
    ----------
    model: numpy.ndarray
    data: numpy.ndarray
    weights: numpy.ndarray
    
    Keywords
    --------
    background: bool
        Activate/inactivate background (activated by default:True)
    positive_bck : bool
        Makes background positive (default:False)
    """
    ws = np.sum(weights)
    mws = np.sum(model * weights)
    mwds = np.sum(model * weights * data)
    m2ws = np.sum(weights * (model ** 2))
    wds = np.sum(weights * data)

    if background:
        delta = mws ** 2 - ws * m2ws
        amp = 1. / delta * (mws * wds - ws * mwds)
        bck = 1. / delta * (-m2ws * wds + mws * mwds)
    else:
        amp = mwds / m2ws
        bck = 0.0
        
    if bck<0 and positive_bck: #re-implement above equation
        amp = mwds / m2ws
        bck = 0.0

    return amp, bck


def psffit(psf, model, x0, weights=None, dxdy=(0.,0.), flux_bck=(True,True),
           positive_bck=False, fixed=None, npixfit=None, max_nfev=None, **kwargs):
    """Fit a PSF with a parametric model solving the least-square problem
       epsilon(x) = SUM_pixel { weights * (amp * Model(x) + bck - psf)² }
    
    Parameters
    ----------
    psf : numpy.ndarray
        The experimental image to be fitted
    model : instance of ParametricPSF (or its subclasses)
        The model to fit
    x0 : tuple, list, numpy.ndarray
        Initial guess for parameters
    weights : numpy.ndarray
        Least-square weighting matrix (same size as `psf`)
        Inverse of the noise's variance
        Default: uniform weighting
    dxdy : tuple of two floats
        Eventual guess on PSF shifting
    flux_bck : tuple of two bool
        Only background can be activate/inactivated
        Flux is always activated (sorry!)
    positive_bck : bool
        Force background to be positive or null
    fixed : numpy.ndarray
        Fix some parameters to their initial value (default: None)
    npixfit : int (default=None)
        Increased pixel size for improved fitting accuracy
    max_nfev : int or None
        Maximum number of evaluation of the cost function
    **kwargs :
        All keywords used to call your `model`
    
    Returns
    -------
    out.x : numpy.array
            Parameters at optimum
       .dxdy : tuple of 2 floats
           PSF shift at optimum
       .flux_bck : tuple of two floats
           Estimated image flux and background
       .psf : numpy.ndarray (dim=2)
           Image of the PSF model at optimum
       .success : bool
           Minimization success
       .status : int
           Minimization status (see scipy doc)
       .message : string
           Human readable minimization status
       .active_mask : numpy.array
           Saturated bounds
       .nfev : int
           Number of function evaluations
       .cost : float
           Value of cost function at optimum
    """
    
    if weights is None:
        weights = np.ones_like(psf)
    elif len(psf)!=len(weights):
        raise ValueError("Keyword `weights` must have same number of elements as `psf`")
    
    if np.min(weights)<0:
        raise ValueError("Keyword `weights` cannot contain negative values.")
    
    # Increase array size for improved fitting accuracy
    if npixfit is not None:
        sx,sy = np.shape(psf)
        if (sx>npixfit) or (sy>npixfit):
            raise ValueError('npixfit must be greater or equal to both psf dimensions')
        psfbig = np.zeros((npixfit,npixfit))
        wbig = np.zeros((npixfit,npixfit))
        psfbig[npixfit//2-sx//2:npixfit//2+sx//2,npixfit//2-sy//2:npixfit//2+sy//2] = psf
        wbig[npixfit//2-sx//2:npixfit//2+sx//2,npixfit//2-sy//2:npixfit//2+sy//2] = weights
        psf = psfbig
        weights = wbig
    
    sqw = np.sqrt(weights)
    
    class CostClass:
        """A cost function that can print iterations"""
        def __init__(self):
            self.iter = 0
        def __call__(self,y):
            if (self.iter%5)==0:
                print("\rPSFFIT iteration %3u "%self.iter,end="")
            self.iter += 1
            x, dxdy = mini2input(y)
            mm = model(x, dx=dxdy[0], dy=dxdy[1], **kwargs)
            amp, bck = lsq_flux_bck(mm, psf, weights, background=flux_bck[1], positive_bck=positive_bck)
            return 0.5*np.reshape(sqw * (amp*mm + bck - psf), np.size(psf))
    
    cost = CostClass()
    
    if fixed is not None:
        if len(fixed)!=len(x0):
            raise ValueError("When defined, `fixed` must be same size as `x0`")
        free = [not fixed[i] for i in range(len(fixed))]
        idxfree = np.where(free)[0]
    
    def input2mini(x,dxdy):
        # Transform user parameters to minimizer parameters
        if fixed is None:
            xfree = x
        else: xfree = np.take(x,idxfree)
        return np.concatenate((xfree,dxdy))
    
    def mini2input(y):
        # Transform minimizer parameters to user parameters
        if fixed is None:
            xall = y[0:-2]
        else:
            xall = np.copy(x0)
            for i in range(len(y)-2):
                xall[idxfree[i]] = y[i]
        return (xall,y[-2:])
    
    def get_bound(inst):
        b_low = inst.bounds[0]
        if fixed is not None:
            b_low = np.take(b_low,idxfree)
        b_low = np.concatenate((b_low,[-np.inf,-np.inf]))
        b_up = inst.bounds[1]
        if fixed is not None:
            b_up = np.take(b_up,idxfree)
        b_up = np.concatenate((b_up,[np.inf,np.inf]))
        return (b_low,b_up)
    
    result = least_squares(cost, input2mini(x0,dxdy), bounds=get_bound(model), max_nfev=max_nfev)
    
    print("\rPSFFIT finished in %u iter : %s"%(cost.iter,result.message))
    
    result.x, result.dxdy = mini2input(result.x) #split output between x and dxdy
    
    std = 1/np.sqrt(np.diag(result.jac.T @ result.jac))
    result.x_std, result.dxdy_std = mini2input(std)
    if fixed is not None:
        result.x_std[fixed] = 0

    m = model(result.x,dx=result.dxdy[0],dy=result.dxdy[1])
    amp, bck = lsq_flux_bck(m, psf, weights, background=flux_bck[1], positive_bck=positive_bck)
    
    result.flux_bck = (amp,bck)
    result.psf = m    
    return result