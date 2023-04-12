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

ADC_to_mV = 1000./4096.

chain = ROOT.TChain("pulse")
chain.Add(input_filename)
print("Found {} entries".format(chain.GetEntries()))

tag = input_filename.replace(".root","").replace("_out","")
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
# chain.SetLineColor(utils.colors[3])
# chain.SetMarkerColor(colors[3])
#chain.Draw("channel[2]:1e9*time[0]>>h_lgad","i_evt==%i"%event_number,"lp same")
print(utils.colors)
chain.SetLineColor(utils.colors[2])
chain.SetMarkerColor(utils.colors[2])
chain.Draw("{}*channel[0]:1e9*time[0]>>h_start".format(ADC_to_mV),"i_evt=={}".format(event_number),"lp same")
h_start=ROOT.h_start
chain.SetLineColor(utils.colors[3])
chain.SetMarkerColor(utils.colors[3])
chain.Draw("{}*channel[4]:1e9*time[4]>>h_plastic".format(ADC_to_mV),"i_evt=={}".format(event_number),"lp same")
h_plastic=ROOT.h_plastic
latex= ROOT.TLatex()
latex.SetTextFont(62)
latex.SetTextSize(0.045)
# if not beta: latex.DrawLatexNDC(0.15,0.91,"FNAL 120 GeV proton beam")
# else: latex.DrawLatexNDC(0.15,0.91,"^{106}Ru #beta^{-} source")
# latex.DrawLatexNDC(0.61,0.91,"HPK type 3.1, 170V, -20 C")

if center_in_ns != -1: ### draw line at timestamp for zoomed plot
    input_file = ROOT.TFile.Open(input_filename)
    tree = input_file.Get("pulse")
    tree.GetEntry(int(event_number))
    timestamp_start = tree.LP2_50[0]*1e9
    timestamp_plastic = tree.LP2_50[4]*1e9
    line_start = ROOT.TLine()
    line_start.SetLineColor(utils.colors[2])
    line_start.SetLineStyle(7)
    line_start.SetLineWidth(2)
    line_start.DrawLine(timestamp_start,-1200,timestamp_start,200)
    line_plastic = ROOT.TLine()
    line_plastic.SetLineColor(utils.colors[3])
    line_plastic.SetLineStyle(7)
    line_plastic.SetLineWidth(2)
    line_plastic.DrawLine(timestamp_plastic,-1200,timestamp_plastic,200)


if center_in_ns != -1:
    leg = ROOT.TLegend(0.17,0.68,0.68,0.87)
    leg.AddEntry(h_plastic,"Plastic scintillator, 50% CFD: {:.2f} ns".format(timestamp_plastic),"lp")
    leg.AddEntry(h_start,"Start detector, 50% CFD: {:.2f} ns".format(timestamp_start),"lp")
else:
    leg = ROOT.TLegend(0.17,0.68,0.48,0.87)
    leg.AddEntry(h_plastic,"Plastic scintillator","lp")
    leg.AddEntry(h_start,"Start detector","lp")    
leg.Draw()


# h_lgad.SetLineWidth(2)
# h_lgad.SetLineColor(utils.colors[3])
# h_lgad.SetMarkerColor(utils.colors[3])

# h_ptk.SetLineWidth(2)
# h_ptk.SetLineColor(utils.colors[2])
# h_ptk.SetMarkerColor(utils.colors[2])

#h_ptk.Draw("lp")
#h_lgad.Draw("lp same")

if center_in_ns == -1:
    c.Print("{}/event{}.pdf".format(display_dir,event_number))
else:
    c.Print("{}/event{}_zoom.pdf".format(display_dir,event_number))
# c.Print("displays/run%i_event%i.root"%(run_number,event_number))