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
    "name":"start_det_ToA",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"#DeltaT, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[103,0,206],
    "draw_opt":"",
    "hist_list":[
        {
        "variable":"1e9*LP2_50[0]",
        "selection":"LP2_50[0]!=0",
        "legend":"Start detector 1",
        "color_index":2,
        "input_file":input_file,
        "fit":""
        },
                {
        "variable":"1e9*LP2_50[7]",
        "selection":"LP2_50[7]!=0",
        "legend":"Start detector 2",
        "color_index":3,
        "input_file":input_file,
        "fit":""
        }
    ]
},
{
    "name":"start_det_dt_firstlast",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"#DeltaT, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[30,-200e-12,200e-12],
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
    "name":"start_det_dt_firstlast_200mV",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"#DeltaT, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[30,-200e-12,200e-12],
    "draw_opt":"",
    "hist_list":[
        {
        "variable":"LP2_200mV[0]-LP2_200mV[7]",
        "selection":"LP2_200mV[0]!=0 && LP2_200mV[7]!=0 && i_evt<600",
        "legend":"Start detectors, first 10 min",
        "color_index":2,
        "input_file":input_file,
        "fit":"gaus"
        },
        {
        "variable":"LP2_200mV[0]-LP2_200mV[7]",
        "selection":"LP2_200mV[0]!=0 && LP2_200mV[7]!=0 && i_evt>({}-600)".format(total_events),
        "legend":"Start detectors, last 10 min",
        "color_index":3,
        "input_file":input_file,
        "fit":"gaus"
        }
    ]
},
{
    "name":"start_det_dt_firstlast_100mV",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"#DeltaT, start detectors [s]",
    "y_axis":"Entries",
    "xbins":[30,-200e-12,200e-12],
    "draw_opt":"",
    "hist_list":[
        {
        "variable":"LP2_100mV[0]-LP2_100mV[7]",
        "selection":"LP2_100mV[0]!=0 && LP2_100mV[7]!=0 && i_evt<600",
        "legend":"Start detectors, first 10 min",
        "color_index":2,
        "input_file":input_file,
        "fit":"gaus"
        },
        {
        "variable":"LP2_100mV[0]-LP2_100mV[7]",
        "selection":"LP2_100mV[0]!=0 && LP2_100mV[7]!=0 && i_evt>({}-600)".format(total_events),
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
    "name":"start_det_expected_jitter_vs_event",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"Event number",
    "y_axis":"Expected jitter, start detector [ps]",
    "z_axis":"Entries",
    "xbins":[20,0,total_events],
    "ybins":[30,0,20],
    "draw_opt":"colz",
    "hist_list":[
        {
        "variable":"-1e12*baseline_RMS[0]/risetime[0]:i_evt",
        "selection":"",
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
    "name":"start_det_dt_res_vs_x",
    "tag":tag,
    "output_folder":"{}".format(base_plot_dir),
    "x_axis":"Event number",
    "y_axis":"Start detector resolution, FWHM / #sqrt{2} [ps]",
    "z_axis":"Entries",
    "xbins":[12,0,total_events],
    "ybins":[30,-300e-12,300e-12],
    "draw_opt":"res_vs_x",
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
    "log":True,
    "hist_list":[
        
        {
            "variable":"amp[{}]".format(plastics[ip]["ch_E"]),
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
    "log":True,
    "hist_list":[
        
        {
            "variable":"{}*amp[{}]".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
{
    "name":"plastic_energy_keV_unzoom",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [keV]",
    "y_axis":"Entries",
    "xbins":[40,0,2000],
    "draw_opt":"",
    "log":True,
    "hist_list":[
        
        {
            "variable":"{}*amp[{}]".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
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
    "log":True,
    "hist_list":[
        
        {
            "variable":"{}*amp[{}]".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
{
    "name":"plastic_energy_vs_amp_time",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [keV]",
    "y_axis":"Fast readout amplitude [mV]",
    "z_axis":"Entries",
    "xbins":[40,0,200],
    "ybins":[40,0,1000],
    "draw_opt":"colz",
    "log":False,
    "hist_list":[
        {
            "variable":"amp[{}]:{}*amp[{}]".format(plastics[ip]["ch_t"],mV_to_keV[ip], plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(1)]
},
{
    "name":"plastic_time_slew_200mV",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [keV]",
    "y_axis":"LE time 200 mV, w.r.t. start [ns]",
    "z_axis":"Entries",
    "xbins":[40,0,200],
    "ybins":[100,-1000e-12,20000e-12],
    "draw_opt":"colz",
    "log":False,
    "hist_list":[
        {
            "variable":"(LP2_200mV[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  ):{conv}*amp[{chE}]".format(ch = plastics[ip]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay,conv=mV_to_keV[ip], chE=plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(1)]
},
{
    "name":"plastic_time_slew_CFD",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [keV]",
    "y_axis":"LE time 20%, w.r.t. start [ns]",
    "z_axis":"Entries",
    "xbins":[40,0,200],
    "ybins":[100,-1000e-12,20000e-12],
    "draw_opt":"colz",
    "log":False,
    "hist_list":[
        {
            "variable":"(LP2_20[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  ):{conv}*amp[{chE}]".format(ch = plastics[ip]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay,conv=mV_to_keV[ip], chE=plastics[ip]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(1)]
},
{
    "name":"plastic_time_slew_prof",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy [keV]",
    "y_axis":"LE time w.r.t. start [ns]",
    "z_axis":"Entries",
    "xbins":[40,0,200],
    "ybins":[100,-1000e-12,20000e-12],
    "draw_opt":"prof",
    "hist_list":[
        {
            "variable":"(LP2_20[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  ):{conv}*amp[{chE}]".format(ch = plastics[0]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay,conv=mV_to_keV[0], chE=plastics[0]["ch_E"]),
            "selection":"",
            "legend":"CFD 20%",
            "color_index":1,
            "input_file":input_file,
            "fit":""
        }, 
             {
            "variable":"(LP2_200mV[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  ):{conv}*amp[{chE}]".format(ch = plastics[0]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay,conv=mV_to_keV[0], chE=plastics[0]["ch_E"]),
            "selection":"",
            "legend":"LE 200 mV",
            "color_index":2,
            "input_file":input_file,
            "fit":""
        } ,
                     {
            "variable":"(LP2_200mV[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  ):{conv}*amp[{chE}]".format(ch = plastics[0]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay,conv=mV_to_keV[0], chE=plastics[2]["ch_E"]),
            "selection":"",
            "legend":"LE 200 mV vs wrong channel",
            "color_index":3,
            "input_file":input_file,
            "fit":""
        } ,
    ]
},
{
    "name":"plastic_energy_corr",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy 0 [keV]",
    "y_axis":"Energy 2 [keV]",
    "z_axis":"Entries",
    "xbins":[40,0,100],
    "ybins":[40,0,100],
    "draw_opt":"colz",
    "log":False,
    "hist_list":[
        {
            "variable":"{conv}*amp[{chEy}]:{conv}*amp[{chEx}]".format(conv=mV_to_keV[ip], chEy=plastics[2]["ch_E"],chEx=plastics[0]["ch_E"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(1)]
},
{
    "name":"plastic_energy_corr_prof",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Energy 0 [keV]",
    "y_axis":"Energy X [keV]",
    "z_axis":"Entries",
    "xbins":[40,0,100],
    "ybins":[40,0,100],
    "draw_opt":"prof",
    "log":False,
    "hist_list":[
        {
            "variable":"{conv}*amp[{chEy}]:{conv}*amp[{chEx}]".format(conv=mV_to_keV[ip], chEy=plastics[ip]["ch_E"],chEx=plastics[0]["ch_E"]),
            "selection":"",
            "legend":"Energy {} vs Energy 0".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(1,4)]
},
{
    "name":"plastic_dt_100to700mV",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Risetime, 100 to 700 mV [ns]",
    "y_axis":"Entries",
    "xbins":[50,-3e-9,7e-9],
    "draw_opt":"hist",
    "hist_list":[
        {
            "variable":"LP2_700mV[{ch}] - LP2_100mV[{ch}]".format(ch = plastics[ip]["ch_t"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
{
    "name":"plastic_time_amp",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Amplitude [mV]",
    "y_axis":"Entries",
    "xbins":[50,0,1000],
    "draw_opt":"hist",
    "hist_list":[
        {
            "variable":"amp[{ch}]".format(ch = plastics[ip]["ch_t"]),
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
    "log":True,
    "hist_list":[
        
        {
            "variable":"(LP2_50[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  )".format(ch = plastics[ip]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay),
            "selection":"{0}*amp[{1}] <  100".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
        # } for ip in range(1)]
},
{
    "name":"plastic_dt_clean",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"#DeltaT, plastic - start [s]",
    "y_axis":"Entries",
    "xbins":[100,-1000e-12,20000e-12],
    "draw_opt":"",
    "log":True,
    "hist_list":[
        
        {
            "variable":"(LP2_50[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  )".format(ch = plastics[ip]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay),
            "selection":"{0}*amp[{1}] <  100 && (LP2_700mV[{2}] - LP2_100mV[{2}])<1.2e-9".format(mV_to_keV[ip], plastics[ip]["ch_E"],plastics[ip]["ch_t"]),
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
        # } for ip in range(1)]
},
{
    "name":"plastic_dt_clean_vs_not",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"#DeltaT, plastic - start [s]",
    "y_axis":"Entries",
    "xbins":[100,-1000e-12,20000e-12],
    "draw_opt":"norm",
    "log":True,
    "hist_list":[
        
        {
            "variable":"(LP2_200mV[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  )".format(ch = plastics[0]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay),
            "selection":"{0}*amp[{1}] <  60 && (LP2_700mV[{2}] - LP2_100mV[{2}])<1.2e-9".format(mV_to_keV[0], plastics[0]["ch_E"],plastics[0]["ch_t"]),
            "legend":"Plastic, {0} cleaned".format(0),
            "color_index":0,
            "input_file":input_file,
            "fit":""
        },
                {
            "variable":"(LP2_200mV[{ch}] - {p_dly}) - ( 0.5*(LP2_50[0]+LP2_50[7])-{s_dly}  )".format(ch = plastics[0]["ch_t"],p_dly=plastic_detector_delay,s_dly=start_detector_delay),
            "selection":"{0}*amp[{1}] <  60 ".format(mV_to_keV[0], plastics[0]["ch_E"],plastics[0]["ch_t"]),
            "legend":"Plastic {}, all".format(0),
            "color_index":1,
            "input_file":input_file,
            "fit":""
        }  
    ]
},
{
    "name":"plastic_dt_raw",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"#DeltaT, plastic - start [s]",
    "y_axis":"Entries",
    "xbins":[100,-40000e-12,40000e-12],
    "draw_opt":"",
    "log":True,
    "hist_list":[
        
        {
            "variable":"(LP2_50[{ch}]) - ( 0.5*(LP2_50[0]+LP2_50[7])  )".format(ch = plastics[ip]["ch_t"]),
            "selection":"{0}*amp[{1}] <  100".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
        # } for ip in range(1)]
},
{
    "name":"plastic_ToA",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Plastic ToA [ns]",
    "y_axis":"Entries",
    "xbins":[103,0,206],
    "draw_opt":"",
    "log":True,
    "hist_list":[
        
        {
            "variable":"1e9*LP2_50[{ch}]".format(ch = plastics[ip]["ch_t"]),
            "selection":"{0}*amp[{1}] <  100".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
        # } for ip in range(1)]
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
            "variable":"{}*amp[{}]:i_evt".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "selection":"{}*amp[{}] <  100".format(mV_to_keV[ip], plastics[ip]["ch_E"]),
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},

{
    "name":"plastic_expected_jitter",
    "tag":tag,
    "output_folder":"{}/plastic/".format(base_plot_dir),
    "x_axis":"Expected rising edge jitter [ps]",
    "y_axis":"Entries",
    "xbins":[100,-5,50],
    "draw_opt":"",
    "log":True,
    "hist_list":[
        
        {
            "variable":"-1e12*baseline_RMS[{}]/risetime[{}]".format(plastics[ip]["ch_t"],plastics[ip]["ch_t"]),
            "selection":"",
            "legend":"Plastic {}".format(ip),
            "color_index":ip,
            "input_file":input_file,
            "fit":""
        } for ip in range(len(plastics))]
},
]

for plot_def in plot_definitions: utils.make_plot(plot_def)