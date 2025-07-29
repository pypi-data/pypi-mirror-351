# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 16:30:27 2021

@author: rfetick
"""

import pytest
import numpy as np
import copy
from maoppy.psfutils import reduced_coord, moffat, gauss
from maoppy.psfmodel import ParametricPSFfromPSD, Psfao
from maoppy.psffit import lsq_flux_bck
from maoppy.instrument import muse_nfm, zimpol

#%% DEFINITIONS
def errL1(a,b):
    """L1-norm error between two arrays"""
    avg = np.sum(np.abs(a)+np.abs(b))/2
    diff = np.sum(np.abs(a-b))
    if avg==0: return 0 # if the norms of a and b are both null!
    return diff/avg

#%% TEST FUNCTIONS
def test_reduced_coord_grad():
    ax = 3
    ay = 4
    theta = 1.3
    npix = 256
    XY = np.mgrid[0:npix,0:npix]
    cx = npix//2 - 3
    cy = npix//2 - 5
    u,g = reduced_coord(XY, ax, ay, theta, cx, cy, grad=True)
    # numerical gradient
    gnum = 0*g
    eps = 1e-8
    u2 = reduced_coord(XY, ax+eps, ay, theta, cx, cy)
    gnum[0,...] = (u2-u)/eps
    u2 = reduced_coord(XY, ax, ay+eps, theta, cx, cy)
    gnum[1,...] = (u2-u)/eps
    u2 = reduced_coord(XY, ax, ay, theta+eps, cx, cy)
    gnum[2,...] = (u2-u)/eps
    assert errL1(g,gnum) == pytest.approx(0,abs=1e-7)
    
def test_fluxbck():
    bck = -5.0
    flux = 8.0
    model = np.zeros((10,10))
    model[3:5,3:5] = 1.0/4 # dummy PSF with unit sum
    image = flux*model+bck
    w = np.ones_like(image)
    f,b = lsq_flux_bck(model,image,w)
    assert f==pytest.approx(flux,rel=1e-8)
    assert b==pytest.approx(bck,rel=1e-8)
    
def test_fluxbck_positive():
    bck = -2.0
    flux = 8.0
    model = np.zeros((10,10))
    model[3,3] = 1.0
    image = flux*model+bck
    w = np.ones_like(image)
    f,b = lsq_flux_bck(model,image,w,positive_bck=True)
    assert b==0

def test_moffat_energy():
    npix = 512
    XY = np.mgrid[0:npix,0:npix] - npix/2.0
    param = [5.0,6.0,np.pi/4,1.6,0,0]
    m = moffat(XY,param,norm=np.inf)
    assert np.sum(m)==pytest.approx(1.0,abs=1e-2)
    m = moffat(XY,param,norm=None)
    assert np.max(m)==pytest.approx(1.0,abs=1e-8)
    
def test_gauss_energy():
    npix = 512
    XY = np.mgrid[0:npix,0:npix] - npix/2.0
    param = [5.0,6.0,np.pi/4,0,0]
    g = gauss(XY,param)
    assert np.sum(g)==pytest.approx(1.0,abs=1e-2)
    
def test_moffat_grad():
    npix = 512
    XY = np.mgrid[0:npix,0:npix]-npix//2
    param = [35,25,1.3,1.5,0,0]
    for norm in [None,np.inf,50]: # test the different normalization
        for rm in [0,4]: # test different removeInside
            m,g = moffat(XY, param, norm=norm, removeInside=rm, grad=True)
            gnum = g*0
            eps = 1e-7
            for i in range(gnum.shape[0]):
                dp = copy.copy(param)
                dp[i] += eps
                m2 = moffat(XY, dp, norm=norm, removeInside=rm)
                gnum[i,...] = (m2-m)/eps
            assert errL1(g,gnum)==pytest.approx(0,abs=1e-6)
    
    
#%% TEST PSFfromPSD and PSFAO MODELS
def test_psffrompsd_oversampling():
    npix = 100
    samp = 0.3
    nparam = 8 # whatever
    P = ParametricPSFfromPSD(nparam,(npix,npix),system=muse_nfm,samp=samp)
    assert samp==P.samp
    assert P._samp_over>=2.0
    assert (P._k%1)==0
    
def test_psfao_bounds():
    npix = 100
    samp = 0.3
    P = Psfao((npix,npix),system=muse_nfm,samp=samp)
    assert len(P.bounds[0])==7
    assert len(P.bounds[1])==7
    
def test_psfao_psd_integral():
    npix = 1024
    samp = 2.0
    P = Psfao((npix,npix),system=zimpol,samp=samp)
    fao = P.system.Nact/(2.0*P.system.D)
    df = 1.0/(P.system.D*P._samp_over)
    
    r0 = 0.15
    C = 0
    A = 0
    alpha = 0.5
    ellip = 1.0
    theta = 0
    beta = 1.5
    # Integral of the halo
    psd,_ = P.psd([r0,C,A,alpha,ellip,theta,beta])
    int_num = np.sum(psd)*df*df
    int_ana = 0.0229 * 6*np.pi/5 * (fao*r0)**(-5.0/3.0)
    assert int_num==pytest.approx(int_ana,abs=1e-2)
    # Integral of the constant
    r0 = np.inf
    C = 1e-2
    psd,_ = P.psd([r0,C,A,alpha,ellip,theta,beta])
    int_num = np.sum(psd)*df*df
    int_ana = C*np.pi*fao**2.0 - df*df # remove central pixel
    assert int_num==pytest.approx(int_ana,abs=1e-2)
    # Integral of the Moffat
    C = 0.0
    A = 1.0
    psd,_ = P.psd([r0,C,A,alpha,ellip,theta,beta])
    int_num = np.sum(psd)*df*df
    int_ana = A
    assert int_num==pytest.approx(int_ana,abs=1e-2)
    
def test_psfao_otf_max():
    npix = 1024
    samp = 2.0
    P = Psfao((npix,npix),system=zimpol,samp=samp)
    r0 = 0.25
    C = 1e-4
    A = 1.0
    ax = 0.05
    ay = 0.08
    theta = np.pi/4
    beta = 1.5
    otf = P.otf([r0,C,A,ax,ay,theta,beta])
    mtf = np.max(np.abs(otf))
    assert mtf==pytest.approx(1.0,abs=1e-2)
    assert mtf<=1.0
    
#%% RUN FILE
if __name__=="__main__":
    pytest.main()