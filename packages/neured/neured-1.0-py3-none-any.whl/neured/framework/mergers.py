# ******************************************************************

#                           MERGERS

# Collection of functions to perform merge operation between images

# ******************************************************************

    # import packages
from neured.framework.img_utils import get_img, write_img
from neured.framework.processors import exec_proc, load_img_params, load_imgdir_params, \
    load_dyn_params, exec_start, exec_end
from neured.framework.file_utils import file_index
from tqdm.notebook import tqdm
from astropy.time import Time
import numpy as np
from neured.framework.parameters import param, get_all_params

# ------------------------------------------------------------------
#                           mrg_medproj
# ------------------------------------------------------------------
# Performs a pixel-wise median projection of a stack of images

# input parameters: src_stack = stack of images as a 3D array
#                   **kwargs = collection of named parameters (unused here)

# return value: single image (2D array) containing the projection
# ------------------------------------------------------------------

def mrg_medproj(src_stack, **kwargs):
        
        # import package
    import numpy as np

        # perform pixel-wise median projection in the stack depth direction
        # and recast the image type to the original one
    return np.median(src_stack, axis=2).astype(src_stack.dtype)

# ------------------------------------------------------------------
#                           mrg_avgproj
# ------------------------------------------------------------------
# Performs a pixel-wise average projection of a stack of images

# input parameters: src_stack = stack of images as a 3D array
#                   **kwargs = collection of named parameters (unused here)

# return value: single image (2D array) containing the projection
# ------------------------------------------------------------------

def mrg_avgproj(src_stack, **kwargs):
    
        # import package
    import numpy as np

        # perform pixel-wise median projection in the stack depth direction
        # and recast the image type to the original one
    return np.average(src_stack, axis=2).astype(src_stack.dtype)


def mrg_avgproj_nan(src_stack, **kwargs):
    
        # import package
    import numpy as np

        # perform pixel-wise median projection in the stack depth direction
        # and recast the image type to the original one
    return np.nanmean(src_stack, axis=2).astype(src_stack.dtype)

# ------------------------------------------------------------------
#                           simple_merge
# ------------------------------------------------------------------
# Merges the images contained in a single directory and saves the resulting
# image. The 'merger' is defined as a function which casts a 3D stack of
# images of size (x,y,n) into a single image of size (x,y). Example of
# mergers are the pixel-wise median and average projections.
    
# Optionally, a sequence of pre-processing steps can be defined.

# input parameters: src_dir = src_dir = source directory (relative to 'base_dir')
#                   dst_file = name of the destination file
#                   merger = name of the merger function
#                   base_dir = base directory to define the relative paths
#                   pre_proc = optional sequence of processing steps to be
#                       applied to each image of the stack before merging.
#                   index_range = [min, max] array used to select only a given
#                       range of files to merge (base on their index)
#                       Default: empty array meaning all files are used
#                   tag_pos = position of the tag representing the index in the
#                       file name (tags are separated by '_'). Default: last one
#                   overwrite = if true, destination is overwritten if exists
#                       Default: False
#                   **kwargs = additional list of named parameters. **kwargs will
#                           be passed to different sub functions, but in particular:
#                   - All values defined in **kwargs are made available to
#                     the processing steps (if a pre-processing sequence is defined)
#                   - All parameters in **kwargs whose name ends with '_imgf'
#                     are assumed to be image file names. The corresponding images
#                     are loaded and made available to the processing steps
#                     as named parameters with the '_imgf' ending changed to 'img'
#                   - The 'start_before', 'start_after', 'stop_before' and
#                     'stop_after' parameters are passed to the 'exec_proc'
#                     function and can be used to define a subset of the
#                     pre-processing sequence to be applied.

# return value: none
# ------------------------------------------------------------------
    
def simple_merge(src, dst, merger, seq=None, merge_at=None, proc_from=None, proc_to=None,
                 index_range=[], tag_pos=-1, overwrite=False, silent=False, 
                 flist=None, log_level='standard', filt='*.fits', **kwargs):
    
        # import packages
    import os
    import numpy as np
    import warnings
    from neured.framework.img_utils import crop_img, get_img_exposure
    import glob
    
        # output start timing indication
    if not silent:
        start_time = exec_start()
        
        # get all the general processing parameters and add them to kwargs
        # if the same name is present in both, kwargs has the priority
    params = get_all_params()
    kwargs_img = {**params, **kwargs}
    
        # get the log level value
    log_level = 'standard' if param('log_level') is None else param('log_level')
    
        # if no base directory is specified, get it from the general processing parameters
    base_dir = param('base_dir')
    
        # get the exposure threshold
    exp_threshold = param('exp_threshold')
    
        # get the intensity ratio threshold
    ir_threshold = param('intratio_threshold')
    
        # bad exposure count variable
    bad_exp_count = 0
    
        # get the 'roi' parameter (if defined)
    if 'roi' in kwargs_img.keys():
        roi_val = kwargs_img['roi']
    else:
        roi_val = None
    
        # compute the absolute path of the source directory
    src_dir_abs = os.path.join(base_dir, src)
    
        # compute the absolute path of the destination file
    dst_name = os.path.join(base_dir, dst)
    dst_name_dir, _ = os.path.split(dst_name)
    
        # if the destination already exists, skip the computation of the
        # merged image
    if os.path.exists(dst_name) and not overwrite:
        print('Destination file "' + dst + '" already exists, skipping"')
        nfiles = 0
    
        # otherwise proceed to the calculation
    else:
        
            # if no file list is specified, get the list of files in the
            # source directory and the number of files
        if flist is None:
            if filt is None:
                file_list = os.listdir(src_dir_abs)
            else:
                file_list = glob.glob(os.path.join(src_dir_abs, filt))
            
            # otherwise use the specified file list
        else:
            file_list = flist
        
            # get the number of files
        nfiles = len(file_list)
        
            # first image indicator
        first_img = True
        
            # create the image buffer (for 3D processing)
        kwargs_img['img_buffer'] = {}
        
            # initialize empty list of headers
        headers = []
        
        first_fname = ''
        last_fname = ''
        
            # initialize file index and image index
        i = 0
        i_img = 0
           
        if seq is None:
            pre_proc = None
            post_proc = None
        else:
            
                          # find the index of the start milestone, if any
            if proc_from is not None:
               try:
                   first_step = seq.index(proc_from)
               except ValueError:
                   raise ValueError('Start milestone "'+ proc_from +'" not found in processing sequence')
            else:
                first_step = 0
                
                # find the index of the end milestone, if any
            if proc_to is not None:
               try:
                   last_step = seq.index(proc_to)
               except ValueError:
                   raise ValueError('End milestone "'+ proc_to +'" not found in processing sequence')
            else:
                last_step = len(seq)
                   
            sub_seq = seq[first_step:last_step]
            
            if merge_at is None:
                pre_proc = sub_seq
                post_proc = None
            else:
                i_mrg = sub_seq.index(merge_at) + 1
                pre_proc = sub_seq[:i_mrg]
                post_proc = sub_seq[i_mrg:]
        
            # loop for each source file in the list
        if silent:
            loop_list = file_list
        else:
            loop_list = tqdm(file_list, desc='Processing')
        for name in loop_list:
            
            if log_level == 'debug':
                print('Simple merge: processing "'+name+'"')
            
                # if an index range is defined, test whether the current file is in range
            do_proc = 1
            if index_range != []:
                fi = file_index(name, tag_pos)
                if fi < index_range[0] or fi > index_range[1]:
                    do_proc = 0
                
                # if an exposure threshold is set, check whether the exposure is sufficient
            if exp_threshold is not None:
                exp_val = get_img_exposure(os.path.join(base_dir, src, name))
                if exp_val < exp_threshold:
                    do_proc = 0
                    bad_exp_count += 1
                
                # if an intensity ratio threshold is set, check whether the intensity ratio is sufficient
            if ir_threshold is not None:
                ir_val = get_img_exposure(os.path.join(base_dir, src, name), exp_key='INTRATIO')
                if ir_val < ir_threshold:
                    do_proc = 0
                    bad_exp_count += 1
            
                # if the image is selected for processing
            if do_proc:
                
                    # load the image
                file_name = os.path.join(src, name)
                        
                if pre_proc is not None or post_proc is not None:
                    
                        # load the images which are used as parameters
                        # (see detailed description of the 'load_img_params' function)
                    kwargs_img = load_img_params(**kwargs_img)
                    
                        # load the images which are used as dynamic parameters
                        # (see detailed description of the 'load_img_params' function)
                    kwargs_img = load_dyn_params(name, **kwargs_img)
                
                    # if a pre-processing sequence is defined
                if pre_proc is not None:
                    
                    if log_level == 'debug':
                        print('Pre-processing "'+name+'"')
                
                        # disable the warnings occuring during the processing
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                
                            # execute the pre-processing sequence on the image
                        img, header = exec_proc(0, seq=pre_proc, allow_3D=True,
                                        src_fname = os.path.join(base_dir, file_name),
                                        get_header=True, **kwargs_img)
                    
                    # if there is no pre-processing sequence, just load the image
                else:
                    img, header = get_img(file_name, base_dir, get_header=True)
                    
                    # only include the image if it is valid
                if img.size > 0:
                
                        # if this is the first image, create the 3D image stack
                    if first_img:
                        stack = np.zeros([img.shape[0], img.shape[1], len(file_list)], img.dtype)
                        stack[:,:,0] = img
                        first_img = False
                        first_fname = name
                        # otherwise, add the image to the stack
                    else:
                        stack[:,:,i_img] = img
                        
                    last_fname = name
                        
                        # increase image index
                    i_img = i_img + 1
                    
                        # add the header to the list
                    headers.append(header)
                
                    # increase file index
                i = i+1
        
            # remove the empty images end the end of the stack
        nimg = i_img
        if nimg > 0:
            stack = stack[:,:,0:nimg]
            
                # apply the selected merge operation on the loaded stack
            mrg_img = merger(stack, **kwargs_img)
        
                # merge the headers
            mrg_header = merge_headers(headers)
            
        else:
            mrg_img, mrg_header = get_img(os.path.join(src, file_list[0]), base_dir, get_header=True)
            mrg_img = mrg_img*0
        
        head_string = 'Processing: Image merged from ' + str(nimg) + ' images'
        if exp_threshold is not None or ir_threshold is not None:
            head_string = head_string + ' / ' + str(bad_exp_count) + ' image(s) dropped'
        mrg_header['HISTORY'] = head_string
        mrg_header['HISTORY'] = 'First: ' + first_fname
        mrg_header['HISTORY'] = 'Last: ' + last_fname
        
        if post_proc is not None:
            dst_img, dst_header = exec_proc(mrg_img, post_proc, get_header=True,
                                            header=mrg_header, **kwargs_img)
        else:
            dst_img = mrg_img
            dst_header = mrg_header
        
            # if the destination directory does not exist, create it
        if not os.path.exists(dst_name_dir):
            os.makedirs(os.path.join(dst_name_dir,''))
                    
            # if a ROI is defined, crop the processed image
        if roi_val is not None:
            dst_img = crop_img(dst_img, roi_val)
        
            # write the merged image
        write_img(dst_img, dst_name, header=dst_header, overwrite=overwrite, log_level=log_level)  
        
        # output end timing indication
    if not silent:
        exec_end(start_time, nfiles)

    
# ------------------------------------------------------------------

def merge_headers(head_list):
    
    comment_fields = ['COMMENT', 'HISTORY']
    
    fields_list = []
    
        # get the list of all fields present in the headers, except comments
    for header in head_list:
        fields_list.extend([x for x in header.keys() if x not in fields_list \
                            and x not in comment_fields])
    
        # use the first of the headers to create the merged one
    head_mrg = head_list[0].copy()
    
        # loop for all fields
    for field in fields_list:
        
            # if all headers have the curent field:
        if all([field in header for header in head_list]):
        
                # get all values for this field
            val_list = [header[field] for header in head_list]
            
                # if all values are the same, keep the value from first header
            if all([x == val_list[0] for x in val_list]):            
                pass
            
                # if we have different values
            else:
            
                    # try to compute the average, assuming numerical values
                try:
                    head_mrg[field] = sum(val_list)/len(val_list)
                
                    # if not a numerical value
                except (ValueError, TypeError):
                    
                        # try to average the value as a time stamp
                    try:
                        ts_list = Time(val_list)
                        ts_mean = ts_list.min() + np.mean(ts_list - ts_list.min())
                        head_mrg[field] = str(ts_mean)
                    
                        # if not a time stamp
                    except (ValueError, TypeError):
                        
                            # write an empty value
                        head_mrg[field] = (None, 'Cannot merge values')
        
            # if any of the headers does not have the current field
        else:
                # write an empty value
            head_mrg[field] = (None, 'Field value missing')
    
    return head_mrg

    
# ------------------------------------------------------------------

def multi_merge(src_dir, dst_dir, merger, dst_name_rule=None, **kwargs):
    
    from neured.framework.file_utils import file_list
    import os
    
        # output start timing indication
    start_time = exec_start()
    
        # if no base directory is specified, get it from the general processing parameters
    base_dir = param('base_dir')
    
        # get the list of FITS files
    flist = file_list(src_dir, base_dir, 'fits')
    dirlist = []
    
        # get the number of files
    nfiles = len(flist)
    
        # get the list of directories containing FITS files
    for fname in flist:
        dirname = os.path.dirname(fname)
        if dirname not in dirlist:
            dirlist.append(dirname)
            
        # if no naming rule is defined, use the default one:
    if dst_name_rule is None:
        dst_names = [os.path.join(os.path.sep.join(x.split('\\')[:-1]), x.split('\\')[-1]+'.fits') for x in dirlist] 
        
        # else use the specified naming rule
    else:
        dst_names = [dst_name_rule(x) for x in dirlist]
        
        # loop for all directories to merge
    for i in tqdm(range(len(dirlist))):
        simple_merge(os.path.join(src_dir, dirlist[i]), os.path.join(dst_dir, dst_names[i]), 
                     merger=merger, silent=True, **kwargs)
        
        # output end timing indication
    exec_end(start_time, nfiles)
    
    
# ------------------------------------------------------------------

def ts_list_merge(src_dir, dst_dir, merger, ts_list, log_level='standard', **kwargs):
    
    from neured.framework.file_utils import file_list
    import pandas as pd
    import os
    from neured.framework.parameters import param
    
        # output start timing indication
    start_time = exec_start()
    
        # if no base directory is specified, get it from the general processing parameters
    base_dir = param('base_dir')

    print('Reading the time stamps list ...')
    
    ts_loaded = False
    
    if param('ts_list_merge_save_fname') is not None:
        tlist_fname = os.path.join(param('base_dir'), param('ts_list_merge_save_fname'))
        if os.path.exists(tlist_fname):
            df_times = pd.read_csv(tlist_fname, sep=';', parse_dates=['tstart','tend'], dayfirst=True)
            ts_loaded = True
        
        # if not given as parameter, get the list of FITS files
    if not ts_loaded:
        flist, tlist_start, tlist_end = file_list(src_dir, base_dir, 'fits', get_ts=True, silent=False)
        df_times = pd.DataFrame({'name':flist, 'tstart':tlist_start, 'tend':tlist_end})
        if param('ts_list_merge_save_fname') is not None:
            df_times.to_csv(tlist_fname, sep=';')
    
    if log_level == 'debug':
        print('df_times:')
        print(df_times)
    
    df_ts_list = pd.read_csv(os.path.join(base_dir, ts_list), sep=';', parse_dates=['tstart','tend'], dayfirst=True)
    
    nfiles = len(df_ts_list)

    print('Processing ...')
    
    for i in tqdm(range(nfiles)):
        
        dst_fname = os.path.join(base_dir, dst_dir, df_ts_list['name'][i]) + '.fits'
        tstart = df_ts_list['tstart'][i]
        tend = df_ts_list['tend'][i]
        
        dst_name_dir = os.path.dirname(dst_fname)
                    
            # and create this destination directory if it does not exist
        if not os.path.exists(dst_name_dir):
            os.makedirs(os.path.join(dst_name_dir,''))
            
            # output debug information
        if log_level == 'debug':
            print('name:', df_ts_list['name'][i])
            print('tstart:', tstart)
            print('tend:', tend)
            
            # get the list of files to merge
        flist_mrg = df_times.loc[(df_times['tstart'] >= tstart) & (df_times['tend'] <= tend)]['name']
        
            # output debug information
        if log_level == 'debug':
            print('flist_mrg:', flist_mrg)
        
            # if there are files in the list
        if len(flist_mrg) > 0:
            
                # perform the merge
            simple_merge(src_dir, dst_fname, merger, silent=True, flist=list(flist_mrg), **kwargs)
            
            # if there are no files in the list, output a message
        else:
            print('Merged image "' + df_ts_list['name'][i] + '": no source images')
            
        # output end timing indication
    exec_end(start_time, nfiles)
    
    
# ------------------------------------------------------------------

def load_tb_data(src_dir, sort_key='MS Time'):
    
    from datetime import datetime, timedelta
    import pandas as pd
    import os
    from neured.framework.file_utils import file_list
    
        # output start timing indication
    start_time = exec_start()
    
        # if no base directory is specified, get it from the general processing parameters
    base_dir = param('base_dir')
    
        # get the list of files with TAB extension
    flist = file_list(src_dir, base_dir, ftype='tab')
    
        # create a list for the laoded results
    df_list = []
    
        # loop for each file
    for file in tqdm(flist):
        
            # load the file contents into a pandas data frame
        df_list.append(pd.read_csv(os.path.join(param('base_dir'), src_dir, file), sep='\t', encoding='latin1'))
    
        # concatenate all data
    df = pd.concat(df_list, ignore_index=True)
    
        # sort the data in chronological order
    df.sort_values(sort_key, inplace=True)
    
        # add the time stamp in full format
    df['timestamp'] = df['MS Time']*timedelta(days=1) + datetime(1899,12,30,0,0,0)
        
        # output end timing indication
    exec_end(start_time, len(flist))
    
    return df
    
# ------------------------------------------------------------------

def tag_based_mrg_list(tb_data, list_def_fname, dst_fname):
    
    from datetime import datetime, timedelta
    import pandas as pd
    import os
    
        # output start timing indication
    start_time = exec_start()
    
        # if no base directory is specified, get it from the general processing parameters
    base_dir = param('base_dir')
    
        # get the mergin list definitions
    list_def = pd.read_csv(os.path.join(param('base_dir'), list_def_fname), sep=';')
    
        # create empty destination arrays
    dst_names = []
    dst_ts = []
    dst_te = []
    
        # loop for all list definitions
    for i in tqdm(range(len(list_def))):
        
            #get the list definition parameters
        name = list_def.iloc[i]['name']
        grp_field = list_def.iloc[i]['group']
        filters = list(eval(list_def.iloc[i]['filters']+','))
        tstart = list_def.iloc[i]['tstart']
        tend = list_def.iloc[i]['tend']
        
            # get the list of group names
        grp_list = tb_data.groupby(grp_field).groups.keys()
        
            # loop for all groups
        for grp in grp_list:
            
                # compute the destination name
            dst_name = os.path.join(name, 'cnd'+str(int(grp)))
        
                # make a copy of the testbench data
            tb_data_sub = tb_data.copy()
        
                # select the data corresponding to this group only                
            tb_data_sub = tb_data_sub.loc[tb_data_sub[grp_field] == grp]
            
                # loop for all filters
            for filt in filters:
            
                    # select the data subset according to the filter
                if filt[1] == '=':
                    tb_data_sub = tb_data_sub.loc[tb_data_sub[filt[0]] == filt[2]]
                elif filt[1] == '<>':
                    tb_data_sub = tb_data_sub.loc[tb_data_sub[filt[0]] != filt[2]]
                elif filt[1] == '>':
                    tb_data_sub = tb_data_sub.loc[tb_data_sub[filt[0]] > filt[2]]
                elif filt[1] == '<':
                    tb_data_sub = tb_data_sub.loc[tb_data_sub[filt[0]] < filt[2]]
                elif filt[1] == '>=':
                    tb_data_sub = tb_data_sub.loc[tb_data_sub[filt[0]] >= filt[2]]
                elif filt[1] == '<=':
                    tb_data_sub = tb_data_sub.loc[tb_data_sub[filt[0]] <= filt[2]]
                else:
                    raise ValueError('Filter operator "'+filt[1]+'" is not valid')
                    
            if len(tb_data_sub) > 0:
                    
                        # get the time stamps corresponding to the start and end of the selected data
                ts = tb_data_sub['MS Time'].min()*timedelta(days=1) + datetime(1899,12,30,0,0,0)
                te = tb_data_sub['MS Time'].max()*timedelta(days=1) + datetime(1899,12,30,0,0,0)
        
                    # if a tstart definition is included, apply it
                if tstart < 0:
                    ts_eff = te - timedelta(seconds=int(-tstart))
                elif tstart > 0:
                    ts_eff = ts + timedelta(seconds=int(tstart))
                else:
                    ts_eff = ts
        
                    # if a tend definition is included, apply it
                if tend < 0:
                    te_eff = te - timedelta(seconds=int(-tend))
                elif tend > 0:
                    te_eff = ts + timedelta(seconds=int(tend))
                else:
                    te_eff = te
                    
                    # add the computed output to the merge list
                dst_names.append(dst_name)
                dst_ts.append(ts_eff)
                dst_te.append(te_eff)
                
            else:
                print('Warning: no data found for "'+dst_name+'", skipped')
    
        # create a data frame for the merge list
    df_merge_list = pd.DataFrame({'name':dst_names, 'tstart':dst_ts, 'tend':dst_te})
    
        # write the merge list to the destination file
    df_merge_list.to_csv(os.path.join(base_dir, dst_fname), sep=';')
        
        # output end timing indication
    exec_end(start_time, len(list_def))
    
    