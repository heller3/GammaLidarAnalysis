import os, sys, re
import ROOT
from array import array
import utils
import argparse


utils.set_style()

parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, required=True)
parser.add_argument('--event_number', type=int, required=True)
parser.add_argument('--zoom_center', type=int, default=-1,required=False)



args = parser.parse_args()
input_filename = args.input_file
event_number = args.event_number
center_in_ns = args.zoom_center

tag = input_filename.replace(".root","").replace("_out","")
cosmetic_tag = tag.replace("calibrated_final","").replace("calibrated_mV","").replace("_"," ")

chain = ROOT.TChain("pulse")
chain.Add(input_filename)
print("Found {} entries".format(chain.GetEntries()))

base_plot_dir = "plots/{}/".format(tag)
display_dir = "{}/display/".format(base_plot_dir)
utils.prep_dirs(base_plot_dir)
if not os.path.exists(display_dir):
    os.makedirs(display_dir)	



if center_in_ns == -1: ## full range
    h_frame = ROOT.TH2F("h_frame","",3,0,205,3,-1200,1000)
else:
    h_frame = ROOT.TH2F("h_frame","",3,center_in_ns-15,center_in_ns+15,3,-1200,1000)

h_frame.SetTitle(";Time [ns];Amplitude [mV]")
c = ROOT.TCanvas("c1","",1000,600)
h_frame.Draw()

chain.SetLineWidth(2)
chain.SetMarkerStyle(20)
chain.SetMarkerSize(0.5)

chain.SetLineColor(utils.colors[4])
chain.SetMarkerColor(utils.colors[4])
chain.Draw("20*channel[20]:1e9*time[20]>>h_plastic_energy","i_evt=={}".format(event_number),"lp same")

chain.SetLineColor(utils.colors[2])
chain.SetMarkerColor(utils.colors[2])
chain.Draw("channel[0]:1e9*time[0]>>h_start","i_evt=={}".format(event_number),"lp same")

chain.SetLineColor(utils.colors[1])
chain.SetMarkerColor(utils.colors[1])
chain.Draw("channel[7]:1e9*time[0]>>h_start2","i_evt=={}".format(event_number),"lp same")

chain.SetLineColor(utils.colors[3])
chain.SetMarkerColor(utils.colors[3])
chain.Draw("channel[4]:1e9*time[4]>>h_plastic_time","i_evt=={}".format(event_number),"lp same")
h_start=ROOT.h_start
h_start2=ROOT.h_start2
h_plastic_time=ROOT.h_plastic_time
h_plastic_energy=ROOT.h_plastic_energy
latex= ROOT.TLatex()
latex.SetTextFont(62)
latex.SetTextSize(0.04)
latex.DrawLatexNDC(0.11,0.91,cosmetic_tag)
latex.DrawLatexNDC(0.8,0.91,"Event %i"%event_number)

input_file = ROOT.TFile.Open(input_filename)
tree = input_file.Get("pulse")
tree.GetEntry(int(event_number))
timestamp_start = tree.LP2_50[0]*1e9
timestamp_start_200mV = tree.LP2_200mV[0]*1e9 
timestamp_start2 = tree.LP2_50[7]*1e9
timestamp_start2_200mV = tree.LP2_200mV[7]*1e9 
timestamp_plastic = tree.LP2_50[4]*1e9
timestamp_plastic_100mV = tree.LP2_100mV[4]*1e9
timestamp_plastic_700mV = tree.LP2_700mV[4]*1e9
energy_plastic = tree.amp[20]*1.975 ##mV to keV

if center_in_ns != -1: ### draw line at timestamp for zoomed plot

    line_start = ROOT.TLine()
    line_start.SetLineColor(utils.colors[2])
    line_start.SetLineStyle(7)
    line_start.SetLineWidth(2)
    # line_start.DrawLine(timestamp_start,-1200,timestamp_start,200)
    line_start.DrawLine(timestamp_start_200mV,-1200,timestamp_start_200mV,200)
    
    
    line_start2 = ROOT.TLine()
    line_start2.SetLineColor(utils.colors[1])
    line_start2.SetLineStyle(7)
    line_start2.SetLineWidth(2)
    # line_start.DrawLine(timestamp_start,-1200,timestamp_start,200)
    line_start2.DrawLine(timestamp_start2_200mV,-1200,timestamp_start2_200mV,200)


    line_plastic = ROOT.TLine()
    line_plastic.SetLineColor(utils.colors[3])
    line_plastic.SetLineStyle(7)
    line_plastic.SetLineWidth(2)
    line_plastic.DrawLine(timestamp_plastic,-1200,timestamp_plastic,200)
    

# if center_in_ns != -1:
leg = ROOT.TLegend(0.15,0.68,0.85,0.87)
leg.AddEntry(h_plastic_energy,"Plastic energy (x20), {:.1f} keV".format(energy_plastic),"lp")
leg.AddEntry(h_plastic_time,"Plastic time, 50% CFD: {:.1f} ns".format(timestamp_plastic),"lp")
# leg.AddEntry(h_plastic_time,"Plastic time, 50% CFD: {:.1f} ns, #DeltaT(100, 700 mV): {:.1f} ns)".format(timestamp_plastic,-timestamp_plastic_100mV+timestamp_plastic_700mV),"lp")
leg.AddEntry(h_start,"Start #1, LE at 200 mV: {:.2f} ns".format(timestamp_start_200mV),"lp")
leg.AddEntry(h_start2,"Start #2, LE at 200 mV: {:.2f} ns".format(timestamp_start2_200mV),"lp")
# else:
#     leg = ROOT.TLegend(0.17,0.68,0.48,0.87)
#     leg.AddEntry(h_plastic,"Plastic scintillator","lp")
#     leg.AddEntry(h_start,"Start detector","lp")    
leg.Draw()

if center_in_ns == -1:
    c.Print("{}/event{}.pdf".format(display_dir,event_number))
else:
    c.Print("{}/event{}_zoom.pdf".format(display_dir,event_number))