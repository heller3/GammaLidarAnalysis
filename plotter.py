import os, sys, re
import ROOT
from array import array
# import langaus as lg
import copy
import argparse
import utils

utils.set_style()


parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, required=True)
args = parser.parse_args()
input_filename = args.input_file

input_file = ROOT.TChain("pulse")
input_file.Add(input_filename)

tag = input_filename.replace(".root","").replace("_out","")
base_plot_dir = "plots/{}/".format(tag)
utils.prep_dirs(base_plot_dir)
total_events = input_file.GetEntries()

ADC_to_mV = 1000./4096.
mV_to_keV = [1.975,2.212,2.212,2.212]

cable_velocity = 0.659 * 299792458 #m/s
start_detector_delay = 2.89 / cable_velocity #289 cm
plastic_detector_delay = 0.914 / cable_velocity #3 ft = 91.4 cm

plastics = [
    {"ch_E":20,"ch_t":4},
    {"ch_E":21,"ch_t":5},
    {"ch_E":22,"ch_t":6},
    {"ch_E":23,"ch_t":11}
]
# Channel 21: Plastic energy channel 1
# Channel 22: Plastic energy channel 2
# Channel 23: Plastic energy channel 3
# Channel 24: Plastic energy channel 4

# Channel 5: Plastic channel 1 timing signal
# Channel 6: Plastic channel 2 timing signal
# Channel 7: Plastic channel 3 timing signal


plot_definitions = [
{
    "name":"start_det_dt",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"#DeltaT, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[50,-150e-12,150e-12],
    "draw_opt":"",
    "hist_list":[
        {
        "variable":"LP2_20[0]-LP2_20[7]",
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0",
        "legend":"Start detectors",
        "color_index":2,
        "input_file":input_file,
        "fit":"gaus"
        }
    ]
},
{
    "name":"start_det_dt_firstlast",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"#DeltaT, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[30,-150e-12,150e-12],
    "draw_opt":"",
    "hist_list":[
        {
        "variable":"LP2_20[0]-LP2_20[7]",
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0 && i_evt<600",
        "legend":"Start detectors, first 10 min",
        "color_index":2,
        "input_file":input_file,
        "fit":"gaus"
        },
        {
        "variable":"LP2_20[0]-LP2_20[7]",
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0 && i_evt>({}-600)".format(total_events),
        "legend":"Start detectors, last 10 min",
        "color_index":3,
        "input_file":input_file,
        "fit":"gaus"
        }
    ]
},

{
    "name":"start_det_dt_vs_event",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"Event number",
    "y_axis":"#DeltaT, start detectors [s]",
    "z_axis":"Entries",
    "xbins":[20,0,total_events],
    "ybins":[30,-300e-12,300e-12],
    "draw_opt":"colz",
    "hist_list":[
        {
        "variable":"LP2_20[0]-LP2_20[7]:i_evt",
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0",
        "legend":"Start detectors",
        "color_index":2,
        "input_file":input_file,
        "fit":""
        }
    ]
},
{
    "name":"start_det_dt_RMS_vs_event",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"Event number",
    "y_axis":"RMS of #DeltaT start detectors [s]",
    "z_axis":"Entries",
    "xbins":[20,0,total_events],
    "ybins":[30,-300e-12,300e-12],
    "draw_opt":"RMS",
    "hist_list":[
        {
        "variable":"LP2_20[0]-LP2_20[7]:i_evt",
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0",
        "legend":"Start detectors",
        "color_index":2,
        "input_file":input_file,
        "fit":""
        }
    ]
},
{
    "name":"plastic_energy_mV",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [mV]",
    "y_axis":"Entries",
    "xbins":[30,0,300],
    "draw_opt":"",
    "log":"True",
    "hist_list":[
        
        {
            "variable":"{}*amp[{}]".format(ADC_to_mV, plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},

{
    "name":"plastic_energy_keV",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [keV]",
    "y_axis":"Entries",
    "xbins":[30,0,250],
    "draw_opt":"",
    "log":"True",
    "hist_list":[
        
        {
            "variable":"{}*amp[{}]".format(ADC_to_mV*mV_to_keV[ip], plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
{
    "name":"plastic_dt",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"#DeltaT, plastic - start [s]",
    "y_axis":"Entries",
    "xbins":[100,-1000e-12,20000e-12],
    "draw_opt":"",
    "log":"True",
    "hist_list":[
        
        {
            "variable":"(LP2_20[{ch}] - {p_dly}) - ( 0.5*(LP2_20[0]+LP2_20[7])-{s_dly}  )".format(ch = plastics[ip]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
{
    "name":"plastic_energy_keV_vs_event",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Event number",
    "y_axis":"Mean energy [keV]",
    "z_axis":"Entries",
    "xbins":[20,0,total_events],
    "ybins":[30,0,250],
    "draw_opt":"prof",
    "hist_list":[
        {
            "variable":"{}*amp[{}]:i_evt".format(ADC_to_mV*mV_to_keV[ip], plastics[ip]["ch_E"]),
            "selection":"{}*amp[{}] <  100".format(ADC_to_mV*mV_to_keV[ip], plastics[ip]["ch_E"]),
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
]

for plot_def in plot_definitions: utils.make_plot(plot_def)