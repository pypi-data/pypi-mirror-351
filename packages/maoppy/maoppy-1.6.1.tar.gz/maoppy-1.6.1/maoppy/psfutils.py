"""
List of useful functions to generate PSF.

@author: rfetick
"""

import numpy as np

__all__ = ["oversample", "reduced_coord", "reduced_center_coord", "moffat",
           "moffat_center", "gauss"]


def oversample(samp, fixed_k = None):
    """
        Find the minimal integer that allows oversampling

    Parameters
    ----------
    samp (float):
        input sampling
        
    Keywords
    --------
    fixed_k (int, optional):
        Oversampling factor to be fixed. Defaults to None.

    Returns
    -------
    (k*samp, k):
        the oversampling (>=2) and the corresponding oversampling factor
    """
    if fixed_k is None: 
        k = int(np.ceil(2.0/samp))
    else: 
        k = fixed_k
    return (k*samp,k)


def reduced_coord(xxyy, ax, ay, theta, cx, cy, grad=False):
    """Create an array of reduced coordinated with elongation and rotation"""
    uxx = (xxyy[0]-cx)**2
    uxy = (xxyy[0]-cx)*(xxyy[1]-cy)
    uyy = (xxyy[1]-cy)**2
    return reduced_center_coord(uxx, uxy, uyy, ax, ay, theta, grad=grad)


def reduced_center_coord(uxx, uxy, uyy, ax, ay, theta, grad=False):
    """Create an array of reduced coordinated with elongation and rotation"""
    c = np.cos(theta)
    s = np.sin(theta)
    s2 = np.sin(2.0 * theta)

    rxx = (c/ax)**2 + (s/ay)**2
    rxy =  s2/ay**2 -  s2/ax**2
    ryy = (c/ay)**2 + (s/ax)**2
    
    uu = rxx*uxx + rxy*uxy + ryy*uyy
    
    if grad:
        gg = np.zeros((3,)+uu.shape)
        # du/dax
        gg[0,...] = -2/ax * (uxx*(c/ax)**2 - uxy*s2/ax**2 + uyy*(s/ax)**2)
        # du/day
        gg[1,...] = -2/ay * (uxx*(s/ay)**2 + uxy*s2/ay**2 + uyy*(c/ay)**2)
        # du/dtheta
        drxx = -2*c*s/ax**2 + 2*s*c/ay**2
        drxy = 2*np.cos(2*theta)*(1/ay**2 - 1/ax**2)
        dryy = -2*c*s/ay**2 + 2*s*c/ax**2
        gg[2,...] = drxx*uxx + drxy*uxy + dryy*uyy
        return uu, gg
    
    return uu 


def moffat(xxyy, param, norm=None, removeInside=0, grad=False):
    """Compute a Moffat function on a meshgrid [xx,yy]
    ```moff = E * (1+u)^(-beta)```
    with `u` the reduced quadratic coordinates in the shifted and rotated frame
    and `E` the energy normalization factor
    
    Parameters
    ----------
    xxyy : numpy.ndarray (dim=2)
        The (xx,yy) meshgrid with xx = xxyy[0] and yy = xxyy[1]
    param : list, tuple, numpy.ndarray (len=6)
        param[0] - Alpha X
        param[1] - Alpha Y
        param[2] - Theta
        param[3] - Beta
        param[4] - Center X
        param[5] - Center Y
        
    Keywords
    --------
    norm : None, np.inf, float (>0), int (>0)
        Radius for energy normalization
        None      - No energy normalization (maximum=1.0)
                    E = 1.0
        np.inf    - Total energy normalization (on the whole X-Y plane)
                    E = (beta-1)/(pi*ax*ay)
        float,int - Energy normalization up to the radius defined by this value
                    E = (beta-1)/(pi*ax*ay)*(1-(1+(R**2)/(ax*ay))**(1-beta))    
    
    removeInside: float (default=0)
        Used to remove the central pixel in energy computation
    """
    if len(param)!=6:
        raise ValueError("Parameter `param` must contain exactly 6 elements")
    _,_,_,_,cx,cy = param
    
    uxx = (xxyy[0]-cx)**2
    uxy = (xxyy[0]-cx)*(xxyy[1]-cy)
    uyy = (xxyy[1]-cy)**2
    
    return moffat_center(uxx, uxy, uyy, param[:-2], norm=norm, removeInside=removeInside, grad=grad)


def moffat_center(uxx, uxy, uyy, param, norm=None, removeInside=0, grad=False):
    """Compute a Moffat function, given the quadratic coordinates
    ```moff = E * (1+u)^(-beta)```
    with `u` the reduced quadratic coordinates in the shifted and rotated frame
    and `E` the energy normalization factor
    
    Parameters
    ----------
    xxyy : numpy.ndarray (dim=2)
        The (xx,yy) meshgrid with xx = xxyy[0] and yy = xxyy[1]
    param : list, tuple, numpy.ndarray (len=6)
        param[0] - Alpha X
        param[1] - Alpha Y
        param[2] - Theta
        param[3] - Beta
        
    Keywords
    --------
    norm : None, np.inf, float (>0), int (>0)
        Radius for energy normalization
        None      - No energy normalization (maximum=1.0)
                    E = 1.0
        np.inf    - Total energy normalization (on the whole X-Y plane)
                    E = (beta-1)/(pi*ax*ay)
        float,int - Energy normalization up to the radius defined by this value
                    E = (beta-1)/(pi*ax*ay)*(1-(1+(R**2)/(ax*ay))**(1-beta))    
    
    removeInside: float (default=0)
        Used to remove the central pixel in energy computation
    """
    if len(param)!=4:
        raise ValueError("Parameter `param` must contain exactly 4 elements")
    ax,ay,theta,beta = param
    
    if grad:
        uu,du = reduced_center_coord(uxx, uxy, uyy, ax, ay, theta, grad=grad)
    else:
        uu = reduced_center_coord(uxx, uxy, uyy, ax, ay, theta, grad=grad)
    
    V = (1.0+uu)**(-beta) # Moffat shape
    E = 1.0 # normalization factor (eventually up to infinity)
    F = 1.0 # normalization factor (eventually up to a limited radius)
    
    if grad:
        dVdu = -beta*V/(1.0+uu)
        dV = np.zeros((4,)+uu.shape)
        for i in range(3):
            dV[i,...] = dVdu*du[i,...]
        dV[3,...] = -V*np.log(1.0+uu)
    
    if norm is None:
        if grad:
            return V,dV
    else: # norm can be float or np.inf
        if (beta<=1) and (norm==np.inf):
            raise ValueError("Cannot compute Moffat energy for beta<=1")
        if beta==1:
            raise ValueError("Energy computation for beta=1.0 not implemented yet. Sorry!")
        E = (beta-1) / (np.pi*ax*ay)
        Fout = (1 +         (norm**2)/(ax*ay))**(1-beta)
        Fin  = (1 + (removeInside**2)/(ax*ay))**(1-beta)
        F = 1/(Fin-Fout)
        if grad:
            dE = [-E/ax,-E/ay,0,E/(beta-1)]
            k = (1-beta)*Fout/(1 + (norm**2)/(ax*ay))*(norm**2)/(ax*ay)
            dFout = np.array([-k/ax,-k/ay,0,-Fout*np.log(1 + (norm**2)/(ax*ay))]) if norm<np.inf else np.zeros(4)
            k = (1-beta)*Fin/(1 + (removeInside**2)/(ax*ay))*(removeInside**2)/(ax*ay)
            dFin  = np.array([-k/ax,-k/ay,0,-Fin*np.log(1 + (removeInside**2)/(ax*ay))])
            dF = -(dFin-dFout)/(Fin-Fout)**2
            dm = 0*dV
            for i in range(4):
                dm[i,...] = V*E*dF[i] + V*dE[i]*F + dV[i,...]*E*F
            return V*E*F, dm
            
    return V*E*F


def gauss(xxyy,param):
    """
    Compute a Gaussian function on a meshgrid

    Parameters
    ----------
    xxyy : numpy.ndarray (dim=2)
        The (xx,yy) meshgrid with xx = xxyy[0] and yy = xxyy[1]
    param : list, tuple, numpy.ndarray (len=5)
        param[0] - Sigma X
        param[1] - Sigma Y
        param[2] - Theta
        param[3] - Center X
        param[4] - Center Y  
    """
    if len(param)!=5:
        raise ValueError("Parameter `param` must contain exactly 5 elements")
    ax = np.sqrt(2)*param[0]
    ay = np.sqrt(2)*param[1]
    uu = reduced_coord(xxyy,ax,ay,param[2],param[3],param[4])
    return np.exp(-uu) / (2*np.pi*param[0]*param[1])

