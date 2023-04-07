import os, sys, re
import ROOT
from array import array
# import langaus as lg
import copy
import argparse
import utils

utils.set_style()
utils.prep_dirs()

parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, required=True)
args = parser.parse_args()
input_filename = args.input_file

input_file = ROOT.TChain("pulse")
input_file.Add(input_filename)

ADC_to_mV = 1000./4096.

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
    "name":"start_time_res",
    "output_folder":"plots/",
    "x_axis":"#Delta T, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[30,-60e-12,100e-12],
    "draw_opt":"",
    "hist_list":[
        {
        "variable":"LP2_20[0]-LP2_20[7]",
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0",
        "legend":"Start detectors",
        "color_index":1,
        "input_file":input_file,
        "fit":"gaus"
        }
    ]
    # "legend_list":["Start detectors"],
    # "selection_list":["LP2_20[0]!=0 && LP2_20[7]!=0"],
    # "variable_list":["LP2_20[0]-LP2_20[7]"],
    # "color_list":[2],
    # "inputs_list":[input_file],
    # "fit_list":["gaus"]
},
{
    "name":"plastic_energy",
    "output_folder":"plots/plastic/",
    "x_axis":"Energy [mV]",
    "y_axis":"Entries",
    "xbins":[30,0,300],
    "draw_opt":"",
    "hist_list":[
        
        {
            "variable":"{}*amp[{}]".format(ADC_to_mV, plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
        # {
        #     "variable":"amp[7]",
        #     "selection":"",
        #     "legend":"Start detectors 7",
        #     "color_index":2,
        #     "input_file":input_file,
        #     "fit":""
        # },
        # {
        #     "variable":"amp[18]",
        #     "selection":"",
        #     "legend":"Other detector 18",
        #     "color_index":3,
        #     "input_file":input_file,
        #     "fit":""
        # },       
    # ]
}
]

for plot_def in plot_definitions: utils.make_plot(plot_def)