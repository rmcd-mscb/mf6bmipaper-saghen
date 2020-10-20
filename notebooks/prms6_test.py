import numpy as np
from pymt.models import PRMSSurface, PRMSSoil, PRMSGroundwater, PRMSStreamflow
from pathlib import Path
import geopandas as gpd
import pandas as pd
import helper

run_dir = '../sagehen_prms6/prms6'
config_surf= 'prms6_surf.control'
config_soil = 'prms6_soil.control'
config_gw = 'prms6_gw.control'
config_sf = 'prms6_strm.control'
print(Path(run_dir).exists())
print((Path(run_dir) / config_surf).exists())
print((Path(run_dir) / config_soil).exists())
print((Path(run_dir) / config_gw).exists())
print((Path(run_dir) / config_sf).exists())
msurf = PRMSSurface()
msoil = PRMSSoil()
mgw = PRMSGroundwater()
msf = PRMSStreamflow()

msurf.initialize(config_surf, run_dir)
msoil.initialize(config_soil, run_dir)
mgw.initialize(config_gw, run_dir)
msf.initialize(config_sf, run_dir)



# surf2soil_vars = ['hru_ppt', 'hru_area_perv', 'hru_frac_perv', 'dprst_evap_hru',
#                   'dprst_seep_hru', 'infil', 'sroff', 'potet', 'hru_intcpevap',
#                   'snow_evap', 'snowcov_area', 'soil_rechr', 'soil_rechr_max',
#                   'soil_moist', 'soil_moist_max', 'hru_impervevap',
#                   'srunoff_updated_soil', 'transp_on']

surf2soil_vars = ['hru_ppt', 'hru_area_perv', 'hru_frac_perv',
                  'infil', 'sroff', 'potet', 'hru_intcpevap',
                  'snow_evap', 'snowcov_area', 'soil_rechr', 'soil_rechr_max',
                  'soil_moist', 'soil_moist_max', 'hru_impervevap',
                  'srunoff_updated_soil', 'transp_on']

surf2soil_cond_vars = ['dprst_evap_hru', 'dprst_seep_hru']

soil_cond_vars = ['soil_rechr_chg', 'soil_moist_chg']

soil2surf_vars = ['infil', 'sroff', 'soil_rechr', 'soil_moist']

# surf2gw_vars = ['pkwater_equiv', 'dprst_seep_hru', 'dprst_stor_hru', 'hru_intcpstor',
#                 'hru_impervstor', 'sroff']

surf2gw_vars = ['pkwater_equiv', 'hru_intcpstor', 'hru_impervstor', 'sroff']

surf2gw_cond_vars = ['dprst_seep_hru', 'dprst_stor_hru']

soil2gw_vars = ['soil_moist_tot', 'soil_to_gw', 'ssr_to_gw', 'ssres_flow']

surf2sf_vars = ['potet', 'swrad', 'sroff']

soil2sf_vars = ['ssres_flow']

gw2sf_vars = ['gwres_flow']


def soilinput(msurf, msoil, exch_vars, surf_cond_vars, soil_cond_vars,
              dprst_flag, dyn_dprst_flag, imperv_flag):
    for var in exch_vars:
        msoil.set_value(var, msurf.get_value(var))
    if dprst_flag == 1:
        for var in surf_cond_vars:
            msoil.set_value(var, msurf.get_value(var))
    if dyn_dprst_flag in [1, 3] or imperv_flag in [1, 3]:
        for var in soil_cond_vars:
            msoil.set_value(var, msurf.get_value(var))

def soil2surface(msoil, msurf, exch_vars):
    for var in exch_vars:
        msurf.set_value(var, msoil.get_value(var))


def gwinput(msurf, msoil, mgw, surf_vars, soil_vars, cond_flag, cond_vars):
    for var in surf_vars:
        mgw.set_value(var, msurf.get_value(var))
    for var in soil_vars:
        mgw.set_value(var, msoil.get_value(var))
    if cond_flag == 1:
        for var in cond_vars:
            mgw.set_value(msurf.get_value(var))


def sfinput(msurf, msoil, mgw, msf, surf_vars, soil_vars, gw_vars):
    for var in surf_vars:
        msf.set_value(var, msurf.get_value(var))
    for var in soil_vars:
        msf.set_value(var, msoil.get_value(var))
    for var in gw_vars:
        msf.set_value(var, mgw.get_value(var))

dprst_flag = msurf.get_value('dprst_flag')
dyn_dprst_flag = msoil.get_value('dyn_dprst_flag')
dyn_imperv_flag = msoil.get_value('dyn_imperv_flag')
print(dprst_flag, dyn_dprst_flag, dyn_imperv_flag)


def update_coupled(msurf, surf2soil_vars, surf2soil_cond_vars, soil_cond_vars,
                   msoil, soil2surf_vars,
                   mgw, surf2gw_vars, soil2gw_vars, surf2gw_cond_vars,
                   msf, surf2sf_vars, soil2sf_vars, gw2sf_vars,
                   dprst_flag, dyn_dprst_flag, dyn_imperv_flag):
    msurf.update()
    soilinput(msurf, msoil, surf2soil_vars, surf2soil_cond_vars, soil_cond_vars,
              dprst_flag, dyn_dprst_flag, dyn_imperv_flag)
    msoil.update()
    soil2surface(msoil, msurf, soil2surf_vars)
    gwinput(msurf, msoil, mgw, surf2gw_vars, soil2gw_vars, dprst_flag, surf2gw_cond_vars )
    mgw.update()
    sfinput(msurf, msoil, mgw, msf, surf2sf_vars, soil2sf_vars, gw2sf_vars)
    msf.update()

# Get time information from the model.
print(f'Start time Surface/Soil: {msurf.start_time}/{msoil.start_time}')
print(f'End time Surface/Soil: {msurf.end_time}/{msoil.end_time}')
print(f'Current time Surface/Soil: {msurf.end_time}/{msoil.end_time}')
print('Nowtime Surface/Soil:', msoil.var['nowtime'].data)#, msoil.var['nowtime'].data)

for i in range(int(msurf.start_time),int(msurf.end_time)):
    update_coupled(msurf, surf2soil_vars, surf2soil_cond_vars, soil_cond_vars,
                   msoil, soil2surf_vars,
                   mgw, surf2gw_vars, soil2gw_vars, surf2gw_cond_vars,
                   msf, surf2sf_vars, soil2sf_vars, gw2sf_vars,
                   dprst_flag, dyn_dprst_flag, dyn_imperv_flag)
    if i%250 == 0:
        print(i)

msurf.finalize()
msoil.finalize()
mgw.finalize()
msf.finalize()

print("finished")