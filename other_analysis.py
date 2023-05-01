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

mV_to_keV = [1.975,2.212,2.212,2.212]

cable_velocity = 0.659 * 299792458 #m/s
cable_velocity = 1.0 * 299792458 #m/s
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
        "variable":"LP2_20[0]-LP2_20[7]", ###LP2_20[0] is the CFD 20% on channel 0
        "selection":"LP2_20[0]!=0 && LP2_20[7]!=0",
        "legend":"Start detectors",
        "color_index":2,
        "input_file":input_file,
        "fit":"gaus"
        }
    ]
}
]

for plot_def in plot_definitions: utils.make_plot(plot_def)