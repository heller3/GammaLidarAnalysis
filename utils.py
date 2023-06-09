import os, sys, re
import ROOT

def prep_dirs(base_dir):
    if not os.path.exists("plots"):
        os.makedirs("plots")	
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)	
    if not os.path.exists("{}/plastic".format(base_dir)):
        os.makedirs("{}/plastic".format(base_dir))	

def set_style():
    ROOT.gROOT.SetBatch(ROOT.kTRUE)
    ROOT.gStyle.SetLabelFont(42,"xyz")
    ROOT.gStyle.SetLabelSize(0.05,"xyz")
    #ROOT.gStyle.SetTitleFont(42)
    ROOT.gStyle.SetTitleFont(42,"xyz")
    ROOT.gStyle.SetTitleFont(42,"t")
    #ROOT.gStyle.SetTitleSize(0.05)
    ROOT.gStyle.SetTitleSize(0.05,"xyz")
    ROOT.gStyle.SetTitleSize(0.05,"t") 
    ROOT.gStyle.SetPadBottomMargin(0.14)
    #ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetTitleOffset(1,'y')
    ROOT.gStyle.SetLegendTextSize(0.035)
    ROOT.gStyle.SetGridStyle(3)
    ROOT.gStyle.SetGridColor(14)
    ROOT.gStyle.SetOptFit(1111)
    ROOT.gStyle.SetOptStat(0)

ROOT.TColor.SetColorThreshold(0.)
##short color palette
one = ROOT.TColor.GetColor(0.906,0.153,0.094)
two = ROOT.TColor.GetColor(0.906,0.533,0.094)
three = ROOT.TColor.GetColor(0.086,0.404,0.576)
four =ROOT.TColor.GetColor(0.071,0.694,0.18)
five =ROOT.TColor.GetColor(0.388,0.098,0.608)
six=ROOT.TColor.GetColor(0.906,0.878,0.094)
colors = [ROOT.kBlack,one,two,three,four,five,six]

### long color palette
red =    ROOT.TColor.GetColor(230./255, 25./255, 75./255)
green =  ROOT.TColor.GetColor(60./255, 180./255, 75./255)
yellow = ROOT.TColor.GetColor(255./255, 225./255, 25./255)
blue =   ROOT.TColor.GetColor(0./255, 130./255, 200./255)
orange = ROOT.TColor.GetColor(245./255, 130./255, 48./255)
purple = ROOT.TColor.GetColor(145./255, 30./255, 180./255)
cyan =   ROOT.TColor.GetColor(70./255, 240./255, 240./255)
magenta =ROOT.TColor.GetColor(240./255, 50./255, 230./255)
lime =   ROOT.TColor.GetColor(210./255, 245./255, 60./255)
pink =   ROOT.TColor.GetColor(250./255, 190./255, 212./255)
teal =   ROOT.TColor.GetColor(0./255, 128./255, 128./255)
lavender=ROOT.TColor.GetColor(220./255, 190./255, 255./255)
brown =  ROOT.TColor.GetColor(170./255, 110./255, 40./255)
beige =  ROOT.TColor.GetColor(255./255, 250./255, 200./255)
maroon = ROOT.TColor.GetColor(128./255, 0./255, 0./255)
mint =   ROOT.TColor.GetColor(170./255, 255./255, 195./255)
olive =  ROOT.TColor.GetColor(128./255, 128./255, 0./255)
apricot =ROOT.TColor.GetColor(255./255, 215./255, 180./255)
navy =   ROOT.TColor.GetColor(0./255, 0./255, 128./255)
grey =   ROOT.TColor.GetColor(128./255, 128./255, 128./255)
black =  ROOT.TColor.GetColor(0./255, 0./255, 0./255)
many_colors = [black,red,green,yellow,blue,orange,purple,cyan,teal,lavender,lime,maroon,navy,grey]


def make_plot(plot_definition):
    c = ROOT.TCanvas()
    c.SetGridy()
    c.SetGridx()
    leg = ROOT.TLegend(0.15,0.68,0.89,0.89)
    leg.SetMargin(0.15)
    if len(plot_definition["hist_list"])>2: leg.SetNColumns(2)
    stack = ROOT.THStack()
    hists=[]
    two_dim_plot = "ybins" in plot_definition
    for ih in range(len((plot_definition["hist_list"]))):
        histname = "h{}".format(ih)
        hist_dict = plot_definition["hist_list"][ih]
        if not two_dim_plot:
            hist = ROOT.TH1D(histname,"",plot_definition["xbins"][0],plot_definition["xbins"][1],plot_definition["xbins"][2])
        else:
            hist = ROOT.TH2D(histname,"",plot_definition["xbins"][0],plot_definition["xbins"][1],plot_definition["xbins"][2],plot_definition["ybins"][0],plot_definition["ybins"][1],plot_definition["ybins"][2])
        hist_dict["input_file"].Project(histname,hist_dict["variable"],hist_dict["selection"])
       
        if not two_dim_plot:
            ### add overflow to last bin
            hist.SetBinContent(plot_definition["xbins"][0],hist.GetBinContent(plot_definition["xbins"][0]+1)+hist.GetBinContent(plot_definition["xbins"][0]))

        ##Hack to achieve in-line profile behavior as in interactive root.
        if "prof" in plot_definition["draw_opt"]: hist = hist.ProfileX()

        if "norm" in plot_definition["draw_opt"]: 
            hist.Scale(1./hist.Integral())
        if "res_vs_x" in plot_definition["draw_opt"]:
            ##replace y values with FWHM/sqrt(2) from gaus fit of y values in each bin of x.
            sigma_hist = ROOT.TH1D("{}_RMS".format(histname),"",plot_definition["xbins"][0],plot_definition["xbins"][1],plot_definition["xbins"][2])
            for ibin in range(plot_definition["xbins"][0]+1):
                this_slice = hist.ProjectionY("project_{}".format(ibin),ibin,ibin)
                fitfunc = ROOT.TF1("f{}".format(ibin),"gaus",plot_definition["ybins"][1],plot_definition["ybins"][2])
                this_slice.Fit(fitfunc,"")
                sigma_hist.SetBinContent(ibin,2.355*(1./1.4142)*1e12*fitfunc.GetParameter(2))
                sigma_hist.SetBinError(ibin,2.355*(1./1.4142)*1e12*fitfunc.GetParError(2))
            hist=sigma_hist
            hist.SetMarkerStyle(20)
            plot_definition["draw_opt"] = "ep"


        if "RMS" in plot_definition["draw_opt"]:
            ### replace y values with RMS of y values in each bin of X
            profile = hist.ProfileX()
            RMS_hist = ROOT.TH1D("{}_RMS".format(histname),"",plot_definition["xbins"][0],plot_definition["xbins"][1],plot_definition["xbins"][2])
            for ibin in range(plot_definition["xbins"][0]+1):
                RMS_hist.SetBinContent(ibin,profile.GetBinError(ibin)*pow(profile.GetBinEntries(ibin),0.5))
            hist=RMS_hist
            plot_definition["draw_opt"] = "hist"
            
        hist.SetLineColor(colors[hist_dict["color_index"]])
        hist.SetLineWidth(2)
        hist.SetMarkerColor(colors[hist_dict["color_index"]])
        stack.Add(hist)
        hists.append(hist)
        if "fit" in hist_dict and hist_dict["fit"]!="":
            fitfunc = ROOT.TF1("f{}".format(ih),hist_dict["fit"],plot_definition["xbins"][1],plot_definition["xbins"][2])
            fitfunc.SetLineColor(colors[hist_dict["color_index"]])
            hist.Fit(fitfunc,"")

            ## restrict fit range within +- 2 sigma and fit again.
            if hist_dict["fit"] == "gaus": 
                fit_lo_x = fitfunc.GetParameter(1) - 2*fitfunc.GetParameter(2)
                fit_hi_x = fitfunc.GetParameter(1) + 2*fitfunc.GetParameter(2)
                fitfunc.SetRange(fit_lo_x,fit_hi_x)
                hist.Fit(fitfunc,"","",fit_lo_x,fit_hi_x)


            if hist_dict["fit"] == "gaus": 
                # leg.AddEntry(hist, "{}, #sigma = {:.1f} #pm {:.1f} ps, FWHM / sqrt(2) = {:.1f}".format(hist_dict["legend"],1e12*fitfunc.GetParameter(2),1e12*fitfunc.GetParError(2),2.355*(1./1.4142)*1e12*fitfunc.GetParameter(2)),"l")
                leg.AddEntry(hist, "{}. FWHM / sqrt(2) = {:.1f} #pm {:.1f} ps".format(hist_dict["legend"],2.355*(1./1.4142)*1e12*fitfunc.GetParameter(2),2.355*(1./1.4142)*1e12*fitfunc.GetParError(2)),"l")
        
        else:
            leg.AddEntry(hist, hist_dict["legend"],"l")

    stackmax = stack.GetMaximum("nostack")
    stack.SetMaximum(1.5*stackmax)
    if not two_dim_plot or "z_axis" not in plot_definition: stack.SetTitle(";{0};{1}".format(plot_definition["x_axis"],plot_definition["y_axis"]))
    else: stack.SetTitle(";{0};{1};{2}".format(plot_definition["x_axis"],plot_definition["y_axis"],plot_definition["z_axis"]))

    stack.Draw("nostack {}".format(plot_definition["draw_opt"]))
    if "colz" not in plot_definition["draw_opt"]: leg.Draw("same")
    output_filename = "{0}/{1}_{2}.pdf".format(plot_definition["output_folder"],plot_definition["tag"],plot_definition["name"])
    latex= ROOT.TLatex()
    latex.SetTextFont(62)
    latex.SetTextSize(0.04)
    latex.DrawLatexNDC(0.73,0.91,plot_definition["tag"].replace("_"," "))


    c.Print(output_filename)
    if "log" in plot_definition and plot_definition["log"]: 
        c.SetLogy()
        stack.SetMaximum(20*stackmax)
        stack.Draw("nostack")
        leg.Draw("same")
        output_filename = "{0}/{1}_{2}_log.pdf".format(plot_definition["output_folder"],plot_definition["tag"],plot_definition["name"])
        latex.DrawLatexNDC(0.73,0.91,plot_definition["tag"].replace("_"," "))

        c.Print(output_filename)

    for hist in hists: hist.Delete()
