# ******************************************************************

#                           MAGIC_SELECTORS

# Collection of functions to be used in Jupyter notebook for interactive
# selection in combination with the '%load' magic.

# select_directory - choose a source or destination directory

# select_filesave_fits - select a file name for saving a FITS image

# select_fileopen_fits - select a file name for loading a fits image

# select_roi - choose a rectangular region in an image

# ******************************************************************

from neured.framework.file_utils import file_list
from neured.framework.processors import exec_proc, load_img_params
import numpy as np
from IPython.display import Javascript
from neured.framework.parameters import param, get_all_params

app = 0

# ----------------------------- %msel magic ------------------------

def par_str_to_dict(*args, **kwargs):
    return (args, kwargs)

# Register %msel magic only if inside IPython (e.g., Jupyter)
try:
    from IPython import get_ipython
    ipy = get_ipython()
    if ipy is not None:
        from IPython.core.magic import register_line_magic

        @register_line_magic
        def msel(arg, default=None):
            shell = get_ipython()
            base_dir = param('base_dir')
            if base_dir is not None:
                p = arg.rfind(')')
                if arg[:p][-1] == '(':
                    arg_exec = arg[:p] + f'base_dir=r"{base_dir}"' + arg[p:]
                else:
                    arg_exec = arg[:p] + f', base_dir=r"{base_dir}"' + arg[p:]
            else:
                arg_exec = arg

            sel_retval = shell.ev(arg_exec)

            if isinstance(sel_retval, tuple):
                code_exec = sel_retval[0]
                p = arg.rfind(')')
                if arg[:p][-1] == '(':
                    arg_cell = arg[:p] + 'default=' + sel_retval[1] + arg[p:]
                else:
                    pdef = arg.find('default')
                    if pdef == -1:
                        arg_cell = arg[:p] + ', default=' + sel_retval[1] + arg[p:]
                    else:
                        arg_cell = arg[:pdef] + 'default=' + sel_retval[1] + arg[p:]
            else:
                code_exec = sel_retval
                arg_cell = arg

            code_js = repr(code_exec + "\n# %msel {}".format(str(arg_cell)))
            shell.run_cell(code_exec)
            js = "Jupyter.notebook.get_cell(Jupyter.notebook.get_cell_elements()." + \
                 "index(this.element.parents('.cell'))).set_text(" + code_js + ")"
            return Javascript(js)

except Exception as e:
    # Skip magic registration if not inside IPython
    pass


"""-------------------------------------------------------------------------"""

def select_basedir(base_dir='', default=None):
    """
    Opens a dialog to select the base directory. All subsequent files and
    directories will be specified with a path relative to this base directory.

    Parameters
    ----------
    base_dir : string, optional
        Starting point for the base directory. The default is ''.

    Returns
    -------
    Absolute path of the selected base directory

    """
    
        # import necessary packages
    import os
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import QApplication
    
    global app
    
        # create the application if necessary
    if app == 0:
        app = QApplication([])
    
        # if the default directory is not set, use the base directory for this
    if default is None:
        default = base_dir
        
        # create the file dialog object
    dialog = QtWidgets.QFileDialog()
    
        # set the title
    dialog.setWindowTitle('Please select the base directory')
    
        # start in the default directory
    dialog.setDirectory(default)
    
        # use directory selection mode
    dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    
        # run the dialog and get the selected directory if accepted
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        new_dir = dialog.selectedFiles()[0]
        
        # if canceled, set the directory to default
    else:
        new_dir = default
    
        # cleanup the path so it will work on Linux
    dir_cleaned = os.path.normpath(new_dir).replace(os.path.sep, '/')
    
        # generate a statement to be inserted in the jupyter notebook
    retval = ('set_params(base_dir = r\"' + dir_cleaned + '\", general=True)',
              'r\"' + dir_cleaned + '\"')
    
        # return the statement
    return retval

# ------------------------------------------------------------------
#                           select_directory
# ------------------------------------------------------------------
# this function is meant to be used together with the '%load' magic in jupyter
# notebook to provide an interactive interface for directory selection.

# input parameters: var_name = string with the name of the variable which will 
#                               contain the resulting path in the notebook
#                   base_dir = directory relative to which the directory path
#                               is specified (absolute path is used if omitted)

# return value: statement to be inserted in the jupyter code cell to 
#               assign the selected path to this variable

# ------------------------------------------------------------------

def select_directory(var_name, base_dir='', default=''):
    
        # import necessary packages
    import os
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import QApplication
    
    global app
    
        # create the application if necessary
    if app == 0:
        app = QApplication([])
    
        # compute the prompt message
    title = 'Please select the "' + var_name + '" directory'
    
        # compute the absolute path of the initial directory
    init_dir = os.path.join(base_dir, default)
        
        # create the file dialog object
    dialog = QtWidgets.QFileDialog()
    
        # set the title
    dialog.setWindowTitle(title)
    
        # set the starting directory
    dialog.setDirectory(init_dir)
    
        # use directory selection mode
    dialog.setFileMode(QtWidgets.QFileDialog.Directory)
    
        # run the dialog and get the selected directory if accepted
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        sel_dir = dialog.selectedFiles()[0]
    
            # if a base path is not specified, select and return the absolute path
        if base_dir == '':
            new_dir = sel_dir
            
            # else return the path relative to the base dir
        else:
            new_dir = os.path.relpath(sel_dir, start=base_dir)
        
        # if canceled, set the directory to default
    else:
        new_dir = default
    
        # cleanup the path so it will work on Linux 
    dir_cleaned = os.path.normpath(new_dir).replace(os.path.sep, '/')
    
        # generate a statement to be inserted in the jupyter notebook
    retval = ('set_params(' + var_name + ' = r\"' + dir_cleaned + '\")',
              'r\"' + dir_cleaned + '\"')
    
        # return the statement
    return retval

# ------------------------------------------------------------------

def select_filesave(var_name, base_dir='', default='', ftype=None, ft_desc=None) -> str:
    
        # import necessary packages
    import os
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import QApplication
    
    global app
    
        # create the application if necessary
    if app == 0:
        app = QApplication([])
    
        # if a filetype is specified, update the default extension and file type description
    if ftype is not None:
        def_ext = '(*.' + ftype + ')'
        ft_desc_eff = ft_desc if ft_desc is not None else ftype.upper() + ' files'
        filters = [ft_desc_eff + ' ' + def_ext, 'All Files (*)']
        
        # otherwise just use a general description
    else:
        filters = ['All files (*)']
    
        # compute the prompt message
    title = 'Please select the "' + var_name + '" file for writing'
    
    init_dir, init_file = os.path.split(os.path.join(base_dir, default))
        
        # create the file dialog object
    dialog = QtWidgets.QFileDialog()
    
        # set the title
    dialog.setWindowTitle(title)
    
        # set the initial directory
    dialog.setDirectory(init_dir)
    
        # select the default file
    dialog.selectFile(init_file)
    
        # set the filters
    dialog.setNameFilters(filters)
    
        # set the overwrite confirmation
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    
        # use directory selection mode
    dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
    
        # run the dialog and get the selected directory if accepted
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        sel_fname = dialog.selectedFiles()[0]
        
            # if no base directory is defined, use the absolute path
        if base_dir == '':
            new_fname = sel_fname
            
            # otherwise compute the relative path to the base directory
        else:
            df = os.path.split(sel_fname)
            new_fname = os.path.join(os.path.relpath(df[0], base_dir), df[1])
        
        # if canceled, set the directory to default
    else:
        new_fname = default
    
        # cleanup the path so it will work on Linux 
    fname = new_fname.replace(os.path.sep, '/')
        
        # generate a statement to be inserted in the jupyter notebook
    return ('set_params(' + var_name + ' = r\"' + fname + '\")', 'r\"' + fname + '\"')
    
# ------------------------------------------------------------------
#                           select_filesave_fits
# ------------------------------------------------------------------
# this function is meant to be used together with the '%load' magic in jupyter
# notebook to provide an interactive interface for saving FITS files

# input parameters: var_name = string with the name of the variable which will 
#                               contain the resulting file name in the notebook
#                   base_dir = directory relative to which the file path
#                               is specified (absolute path is used if omitted)

# return value: statement to be inserted in the jupyter code cell to 
#               assign the selected file name to this variable

# ------------------------------------------------------------------
def select_filesave_fits(var_name, base_dir='', default='') -> str:
    
    return select_filesave(var_name, base_dir=base_dir, default=default, ftype='fits')

# ------------------------------------------------------------------
#                           select_fileopen_fits
# ------------------------------------------------------------------
# this function is meant to be used together with the '%load' magic in jupyter
# notebook to provide an interactive interface for opening FITS files

# input parameters: var_name = string with the name of the variable which will 
#                               contain the resulting file name in the notebook
#                   base_dir = directory relative to which the file path
#                               is specified (absolute path is used if omitted)

# return value: statement to be inserted in the jupyter code cell to 
#               assign the selected file name to this variable

# ------------------------------------------------------------------

def select_fileopen(var_name, base_dir='', default='', ftype=None, ft_desc=None) -> str:
    
        # import necessary packages
    import os
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import QApplication
    
    global app
    
        # create the application if necessary
    if app == 0:
        app = QApplication([])
    
        # if a filetype is specified, update the default extension and file type description
    if ftype is not None:
        def_ext = '(*.' + ftype + ')'
        ft_desc_eff = ft_desc if ft_desc is not None else ftype.upper() + ' files'
        filters = [ft_desc_eff + ' ' + def_ext, 'All Files (*)']
        
        # otherwise just use a general description
    else:
        filters = ['All files (*)']
    
        # compute the prompt message
    title = 'Please select the "' + var_name + '" file for reading'
    
        # compute the initial directory
    init_dir, init_file = os.path.split(os.path.join(base_dir, default))
        
        # create the file dialog object
    dialog = QtWidgets.QFileDialog()
    
        # set the title
    dialog.setWindowTitle(title)
    
        # set the initial directory
    dialog.setDirectory(init_dir)
    
        # select the default file
    dialog.selectFile(init_file)
    
        # set the filters
    dialog.setNameFilters(filters)
    
        # set the overwrite confirmation
    dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
    
        # use directory selection mode
    dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
    
        # run the dialog and get the selected directory if accepted
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        sel_fname = dialog.selectedFiles()[0]
        
            # if no base directory is defined, use the absolute path
        if base_dir == '':
            new_fname = sel_fname
            
            # otherwise compute the relative path to the base directory
        else:
            df = os.path.split(sel_fname)
            new_fname = os.path.join(os.path.relpath(df[0], base_dir), df[1])
        
        # if canceled, set the directory to default
    else:
        new_fname = default
    
        # cleanup the path so it will work on Linux 
    fname = new_fname.replace(os.path.sep, '/')
    
        # generate a statement to be inserted in the jupyter notebook
    return ('set_params(' + var_name + ' = r\"' + fname + '\")', 'r\"' + fname + '\"')

# ------------------------------------------------------------------

def select_fileopen_fits(var_name, base_dir='', default='') -> str:
    
    return select_fileopen(var_name, base_dir=base_dir, default=default, ftype='fits')

# ------------------------------------------------------------------
#                           msel_load_image
# ------------------------------------------------------------------

def msel_load_image(img, show_img='middle', seq=None, **kwargs):
    """
    Internal function used to load the image used for ROI selection or
    other selection functions. Depending on the type of the variable
    'img', different behaviors will occur:
        - if 'img' is a numpy array, it is simply returned by the function
        - if 'img' is a string representing a file path, the corresponding image
          will be loaded
        - if 'img' is a string representing a directory path, one image from
          this directory will be loaded (either the first, last or middle one
          depending on the parameter 'show_img')

    Parameters
    ----------
    img : 2D numpy array or string
        Specification of the image to display for selection
    show_img : string
        Specification of which image to load from a directory ('first', 'middle'
        or 'last')

    Returns
    -------
    2D numpy array containing the image to display

    """
    
    import os
    from neured.framework.img_utils import get_img
        
        # get all the general processing parameters and add them to kwargs
        # if the same name is present in both, kwargs has the priority
    params = get_all_params()
    kwargs_p = {**params, **kwargs}
    
    base_dir = kwargs_p['base_dir']
    
        # if 'img' is already a 2D numpy array, return it
    if isinstance(img, np.ndarray) and len(img.shape) == 2:
        return img, None
    
    if isinstance(img, str):
        imgpath = os.path.join(base_dir, img)
        
        if os.path.isfile(imgpath):
            isdir = False
            
        else:
            isdir = True
    
                # get a list of all FITS files in the specified source directory
            flist = file_list(imgpath, base_dir)
            
                # select the index of the image to be shown (default is the middle one)
            fcount = len(flist)
            if show_img == 'first':
                isel = 0
            elif show_img == 'last':
                isel = fcount-1
            elif show_img == 'middle':
                isel = int(fcount/2)
            else:
                isel = int(show_img)
                
                # load the selected image
            #return get_img(flist[isel], imgpath), os.path.relpath(os.path.join(imgpath, flist[isel]), base_dir)
        
        if seq is not None:
            
                # load the images which are used as parameters
                # (see detailed description of the 'load_img_params' function)
            kwargs_img = load_img_params(**kwargs_p)
            
            kwargs_img['header'] = {}
            
            if isdir:
                ok = False
                while not ok:
                    img = exec_proc(0, seq, allow_3D=True, src_fname=os.path.join(imgpath, flist[isel]), **kwargs_img)
                    if img.size > 0:
                        ok = True
                        rpath = os.path.relpath(os.path.join(imgpath, flist[isel]), base_dir)
                    else:
                        isel = isel+1
                    
            else:
                img = exec_proc(0, seq, allow_3D=True, src_fname=imgpath, **kwargs_img)
                rpath = os.path.relpath(imgpath, base_dir)
                
        else:
            if isdir:
                img = get_img(os.path.join(imgpath, flist[isel]))
                rpath = os.path.relpath(os.path.join(imgpath, flist[isel]), base_dir)
            else:
                img = get_img(imgpath)
                rpath = os.path.relpath(imgpath, base_dir)
                
        return img, rpath
    
    raise ValueError('"img" parameter has un invalid value (must be either an image, a path to an image, or a directory)')

# ------------------------------------------------------------------
#                           select_roi
# ------------------------------------------------------------------
# this function is meant to be used together with the '%load' magic in jupyter
# notebook to provide an interactive interface for selecting a rectangular
# region of interest in an image.
    
# A source directory for the image is specified, and the 'select_roi' function
# first loads and displays the first image in this folder, as a guide for the
# ROI selection.

# input parameters: var_name = string with the name of the variable which will 
#                               contain the resulting ROI definition in the notebook
#                   src_dir = directory containing the source images
#                   base_dir = directory relative to which the 'src_dir' variable
#                               is specified (absolute path is used if omitted)
#                   ftype = source file type (default is 'fits')

# return value: statement to be inserted in the jupyter code cell to 
#               assign the selected ROI definition to this variable

# ------------------------------------------------------------------

def select_roi(var_name, img_def, ftype='fits', seq=None, 
               show_img='middle', default=None, **kwargs) -> str:
    
        # import necessary packages
    from neured.framework.img_utils import prep_img_for_display, img_roi_selector
    import os
    
    import numpy as np
    
        # get the image to display
    img, fname = msel_load_image(img_def, show_img=show_img, seq=seq, **kwargs)
        
    """
        # if a pre-processing sequence is defined
    if seq is not None:
            
            # load the images which are used as parameters
            # (see detailed description of the 'load_img_params' function)
        kwargs_img = load_img_params(**kwargs_p)
        
        kwargs_img['header'] = {}
        
        if fname is None:
                # execute the pre-processing sequence on the loaded image
            img = exec_proc(img, seq=seq, **kwargs_img)
        else:
            img = exec_proc(0, seq, allow_3D=True, src_fname=os.path.join(base_dir, fname), **kwargs_img)
    """
    
        # generate the window title
    title = 'Please select the "' + var_name + '" region'

        # perform the interactive rectangular ROI selection
    roi_def = img_roi_selector(prep_img_for_display(img), title=title,
                               default=default)
    
        # if an empty ROI is returned, this means the input was canceled
    if sum(roi_def) == 0:
        raise ValueError('Interactive input canceled by the user')
    
        # generate a statement to be inserted in the jupyter notebook
    return ('set_params(' + var_name + ' = ' + str(roi_def) + ')', str(roi_def))

"""# ------------------------------------------------------------------
#                           select_roi_img
# ------------------------------------------------------------------
# this function is meant to be used together with the '%load' magic in jupyter
# notebook to provide an interactive interface for selecting a rectangular
# region of interest in an image.
    
# A source file for the image is specified, and the 'select_roi' function
# first loads and displays the corresponding image, as a guide for the
# ROI selection.

# input parameters: var_name = string with the name of the variable which will 
#                               contain the resulting ROI definition in the notebook
#                   src_img = source image file name
#                   base_dir = directory relative to which the 'src_dir' variable
#                               is specified (absolute path is used if omitted)

# return value: statement to be inserted in the jupyter code cell to 
#               assign the selected ROI definition to this variable

# ------------------------------------------------------------------

def select_roi_img(var_name, src_img, base_dir='', pre_proc=0, **kwargs) -> str:
    
        # import necessary packages
    import cv2
    import os
    from neured.framework.img_utils import get_img
    from neured.framework.img_utils import prep_img_for_display
        
        # load the first image of this list
    img = get_img(os.path.join(base_dir, src_img))
        
        # if a pre-processing sequence is defined
    if pre_proc != 0:
            
        # load the images which are used as parameters
            # (see detailed description of the 'load_img_params' function)
        kwargs_img = load_img_params(base_dir, **kwargs)
            
            # execute the pre-processing sequence on the image
        img = exec_proc(img, seq=pre_proc, **kwargs_img)
    
        # compute the zoom factor so that the image fits within a 1000x500 pixels rectangle
        # (to be able to display it on the screen)
    zf = min(1000.0/img.shape[1], 500.0/img.shape[0])

        # perform the interactive rectangular ROI selection
    r = cv2.selectROI(var_name, prep_img_for_display(img, zf))
    cv2.destroyAllWindows()
    
        # generate a statement to be inserted in the jupyter notebook
    return var_name + ' = [' + str(int(r[0]/zf)) + ',' + str(int(r[1]/zf)) + ',' + str(int(r[2]/zf)) + ',' + str(int(r[3]/zf)) + ']'

# ------------------------------------------------------------------
#                           select_roi_ij
# ------------------------------------------------------------------
# this function is meant to be used together with the '%load' magic in jupyter
# notebook to provide an interface for selecting a rectangular
# region of interest in an image. The ROI must be previously defined in the
# ROI Manager tool of ImageJ and saved as a single *.roi file. Only rectangular
# ROIs are supported.

# input parameters: var_name = string with the name of the variable which will 
#                               contain the resulting ROI definition in the notebook
#                   base_dir = start directory to look for the *.roi file

# return value: statement to be inserted in the jupyter code cell to 
#               assign the selected ROI definition to this variable

# ------------------------------------------------------------------

def select_roi_ij(var_name, base_dir='') -> str:
    
        # import necessary packages
    import tkinter
    from tkinter import filedialog
    from PymageJ.roi import ROIDecoder
    import sys
    
        # Create Tk root
    root = tkinter.Tk()
    
        # Hide the main window
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    
        # Select a file and return the path
    fname = filedialog.askopenfile(initialdir=base_dir, defaultextension='.roi', filetypes=(("ROI files", "*.roi"),("All Files", "*.*"))).name
    
    try:
            
            # get the ROI object from the file
        with ROIDecoder(fname) as roi:
            roi_obj = roi.get_roi()
            
            # extract the coordinates
        r = [roi_obj.left, roi_obj.top, roi_obj.width, roi_obj.height]
        
    except:
        print("Unexpected error:", sys.exc_info()[0])
        r = [0,0,0,0]
    
        # generate a statement to be inserted in the jupyter notebook
    return var_name + ' = [' + str(r[0]) + ',' + str(r[1]) + ',' + str(r[2]) + ',' + str(r[3]) + ']'
    
# ----------------------------------------------------------------------------"""


def select_multiple_rois(var_name, img_def, base_dir='', seq=None, 
                         show_img='middle', options=[], default=None, **kwargs):
    '''
    This function provides an interactive interface for selecting a rectangular region of interest in an image.
    This function is meant to be used with the `%load`  magic in jupyter.
    
    The difference with 'select_rois' is that this function assign all the ROIs selected to only one variable name

    Parameters
    ----------
    var_name : str
        strs or list with the names assigned that want to be assigned to the ROIs
    src_img : str
        image directory and name
    img : 2D numpy array
        source image
    base_dir : str, optional
        directory relative to which the 'src_dir' variable is specified (absolute path is used if omitted) 

    Returns
    -------
    variables
        Variable name = [[x,y,w,h], [x2,y2,w2,h2],...]

    '''
    
        # import necessary packages
    from neured.framework.img_utils import prep_img_for_display, img_roi_selector
    import os
        
    """     # get all the general processing parameters and add them to kwargs
        # if the same name is present in both, kwargs has the priority
    params = get_all_params()
    kwargs_p = {**params, **kwargs}
    
    base_dir = kwargs_p['base_dir']"""
    
        # get the image to display
    img, fname = msel_load_image(img_def, show_img=show_img, seq=seq, **kwargs)
    
    """    # read the image directory if a directory is given
    if type(img) == str:
            # load the first image of this list
        img = get_img(os.path.join(base_dir, img))
        
        # read the image received
    else:
        img = img"""
        
        # if a pre-processing sequence is defined
    """if seq is not None:
            
            # load the images which are used as parameters
            # (see detailed description of the 'load_img_params' function)
        kwargs_img = load_img_params(**kwargs_p)
        
        kwargs_img['header'] = {}
        
        if fname is None:
                # execute the pre-processing sequence on the loaded image
            img = exec_proc(img, seq=seq, **kwargs_img)
        else:
            img = exec_proc(0, seq, allow_3D=True, src_fname=os.path.join(base_dir, fname), **kwargs_img)"""
        
    """    # compute the zoom factor so that the image fits within a 1000x500 pixels rectangle
        # (to be able to display it on the screen)
    zf = min(1000.0/img.shape[1], 500.0/img.shape[0])"""
    
        # if one variable is given ie. string, it convert it into a list to enter the names and ROIs loop
    if type(var_name) == list:
        
            # generate the window title
        title = 'Please select following ROIs: ' + ','.join(var_name)
        
            # perform the interactive rectangular ROI selection
        roi_def = img_roi_selector(prep_img_for_display(img), title=title, 
                multiple=True, roi_names=var_name, options=options, default=default)
        
            # if an empty ROI is returned, this means the input was canceled
        if roi_def == None:
            raise ValueError('Interactive input canceled by the user')
        
            # generate a statement to be inserted in the jupyter notebook
        return ('\n'.join([var_name[i] + ' = ' + str(roi) for i, roi in enumerate(roi_def)]), str(roi_def))
        
    else:
        
            # generate the window title
        title = 'Please define one or more ROIs for ' + var_name
        
            # perform the interactive rectangular ROI selection
        roi_def = img_roi_selector(prep_img_for_display(img), title=title, 
                                   multiple=True, options=options, default=default)
        
            # if an empty ROI is returned, this means the input was canceled
        if roi_def == None:
            raise ValueError('Interactive input canceled by the user')
            
            # return the list of values in a legible format for %load magic
        return ('set_params(' + var_name + ' = ' + str(roi_def) + ')', str(roi_def))
    
    