# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 02:00:56 2021

@author: boillat
"""

def skew(src_img, sx=None, sy=None, order=1, **kwargs):
    """
    Perform an affine transforn consisting in skewing the image in
    x and/or in y directions. The transform is set so that the image center
    does not move.

    Parameters
    ----------
    src_img : 2D numpy array
        Source image.
    sx : Double, optional
        Skew in x direction. The default is None.
    sy : Double, optional
        Skew in y direction. The default is None.
    order : Integer, optional
        Order of the interpolation. The default is 1.
    **kwargs : dictionnary
        Collects all unused named parameters.

    Returns
    -------
    Destination image.

    """
    
    from scipy.ndimage import affine_transform
    import numpy as np
    
        # get the image dimensions
    szx = src_img.shape[0]
    szy = src_img.shape[0]
    
        # compute the affine transform matrix
    a11 = 1.0
    a21 = sx if sx is not None else 0.0
    a12 = sy if sy is not None else 0.0
    a22 = 1.0
    t1 = -a12*szy/2.0
    t2 = -a21*szx/2.0
    matrix = [[a11, a12, t1], [a21, a22, t2]]
    
        # perform the transformation
    dst_img = affine_transform(src_img, matrix, order=order)
    
        # return the result
    return dst_img

#-----------------------------------------------------------------------------

def img_get_shifts(src_img, ref_roi, max_shift=20.0, subpix=10, direction='v',
                   c_threshold=0.95):
    """
    Measure by how much each pixel line or column of an elongated object
    has to be shifted in order to straighten this object. The optimal shift
    is obtained based on correlation with a reference ROI. The object needs
    to have a reasonably constant profile across it.
    
    The obtained values can be used to strighten the object using the
    img_straighten() function
    
    The shifts are measured at intervals defined by the width of the reference
    ROI. Subsequently, a smoothed spline interpolation is used to obtain a shift
    value for each pixel.

    Parameters
    ----------
    src_img : 2D numpy array
        Source image.
    ref_roi : list
        Definition of the reference ROI region [x,y,width,height].
    max_shift : float, optional
        Maximum shift allowed (in pixels). The default is 20.
    subpix : integer, optional
        Number of pixel subdivisions for the shift measurements. The default is 10.
    direction : string, optional
        'horizontal', 'horiz' or 'h' for measuring horizontal shifts (vertical object) /
        'vertical', 'vert' or 'v' for measuring vertical shifts (horizontal object).
        The default is 'v'.
    c_threshold : float, optional
        Threshold in the normalized correlation factor for considering a shift
        measurement acceptable. The default is 0.95.

    Raises
    ------
    ValueError
        - Raised if the 'direction' parameter as an invalid value.
        - Raised if none of the measured correlations reached the threshold

    Returns
    -------
    Pair of 2D numpy arrays
        1st array: coordinates.
        2nd array: shift values.

    """
    
    from neured.framework.img_utils import crop_img
    import numpy as np
    from scipy.interpolate import interp1d
    from tqdm import tqdm
    from scipy.interpolate import UnivariateSpline
    
    # ----- definition of the normalized correlation between two vectors
    
    def norm_corr(a,b):
        
            # normalize vector a
        norm_a = np.linalg.norm(a)
        a = a / norm_a
        
            # normalize vector b
        norm_b = np.linalg.norm(b)
        b = b / norm_b
        
            # compute and return the correlation
        c = np.correlate(a, b, mode = 'valid')
        return c[0]
    
    # ----------------------------------------------
    
        # if the direction of the shifts is horizontal, transpose the image
        # and proceed as if the direction was vertical
    if direction in ['horizontal','horiz','h']:
        img = np.swapaxes(src_img, 0, 1)
        
        # otherwise just use the source image
    elif direction in ['vertical','vert','v']:
        img = src_img
        
        # if the direction parameter has an invalid value, raise an error
    else:
        raise ValueError('Direction value not allowed (should be \'horizontal\' or \'vertical\'')
        
        # get the shape of the image
    szy, szx = img.shape
    
        # get the reference profile from the reference ROI region
    refprof = np.mean(crop_img(img, ref_roi),1)
    
        # get the shape of the reference ROI region
    szxr = ref_roi[2]
    szyr = ref_roi[3]
    
        # compute the base for the shift values
    sbase = np.arange(-max_shift, max_shift, 1.0/subpix)
    
        # get the vertical coordinate of the beginning of the reference ROI
    y0 = ref_roi[1]
    
        # compute the base for the horizontal coordinates at which the vertical
        # shift will be measured
    xbase = range(0, szx-szxr, szxr)
    
        # create empty arrays from the correlation coefficients and for the
        # measured shifts
    c_vals = []
    s_vals = []
    
        # loop for each coordinate in the x base:
    for x in tqdm(xbase, desc='Measuring shifts'):
        
            # get the vertical profile for a band starting at this coordinate
        prof = np.mean(crop_img(img, [x,0,szxr,szy]), 1)
        
            # create a linear interpolation function
        intp = interp1d(range(szy),prof)
        
            # for each shift value, measure the correlation of a fraction of the
            # profile corresponding to the shifted ROI vertical coordinated
        carr = [norm_corr(intp(np.arange(szyr)+y0+s), refprof) for s in sbase]
        
            # find the index of the maximum correlation in the resulting array
        imax = np.argmax(carr)
        
            # get the maximum correlation value
        cmax = carr[imax]
        
            # get the shift correponding to the maximum correlation
        sval = imax/subpix-max_shift
        
            # if the maximum correlation is above the threshold, add the values
            # to the corresponding arrays
        if cmax >= c_threshold:
            s_vals.append(sval)
            c_vals.append(cmax)
    
        # if none of the measurements reached the correlation threshold, 
        # raise an error
    if len(c_vals) == 0:
        raise ValueError('All measurement resulted in a correlation below the threshold')
    
        # create a univariate spline interpolation function of the measured shifts
    spl = UnivariateSpline(np.array(xbase) + szxr/2, np.array(s_vals))
    
        # compute the interpolated shift value for each coordinate
    shifts = np.array(spl(range(szx)))
        
        # return the results
    return np.array(range(szx)), shifts
       
#-----------------------------------------------------------------------------

def img_straighten(src_img, shifts, direction='v'):
    """
    Straightens the image of an elongated object based on a shift array
    previously measured using img_get_shifts().

    Parameters
    ----------
    src_img : 2D numpy array
        Source image.
    shifts : 1D array
        Array of shifts to be applied to straighten the object. The length of
        the array must be the same as the image dimension in the direction
        along the object
    direction : string, optional
        'horizontal', 'horiz' or 'h' for applying horizontal shifts (vertical object) /
        'vertical', 'vert' or 'v' for applying vertical shifts (horizontal object).
        The default is 'v'.

    Raises
    ------
    
    ValueError
        - If the direction string is invalid
        - If the length of the shifts array does not correspond to the image dimension

    Returns
    -------
    dst_img : 2D numpy array
        Image with the object straightened.

    """
    
    import numpy as np
    from scipy.ndimage import shift
    
        # if the direction of the shifts is horizontal, transpose the image
        # before and after the processing
    if direction in ['horizontal','horiz','h']:
        transpose = True
        
        # otherwise the axes are the opposite
    elif direction in ['vertical','vert','v']:
        transpose = False
        
        # if the direction parameter has an invalid value, raise an error
    else:
        raise ValueError('Direction value not allowed (should be \'horizontal\' or \'vertical\'')
        
        # transpose the image if necessary
    img = np.swapaxes(src_img, 0, 1) if transpose else src_img
        
        # if the array length does not coeespond to the image size, raise an error
    if len(shifts) != img.shape[1]:
        raise ValueError('The number of elements in the shifts array is not consistent with the image size')
        
        # create the destination image
    dst_img = np.zeros(img.shape, dtype=img.dtype)
    
        # for each x coordinate, copy the pixel column shifted by the desired value
    for i in range(src_img.shape[1]):
        dst_img[:,i] = shift(img[:,i], -shifts[i])
                           
        # transpose the image if necessary  
    dst_img = np.swapaxes(dst_img, 0, 1) if transpose else dst_img
   
        # return the result
    return dst_img
       
#-----------------------------------------------------------------------------
    
    
        
        
        
    
    
    
    
    
    
    
    
    