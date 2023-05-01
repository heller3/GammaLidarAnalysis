# GammaLidarAnalysis

### First, convert from binary to ROOT waveform file
Modify input directory (directory with all .dat files) and output name first, then do:
```
python simpleBinarytoROOT.py
```


Example command to view waveforms in ROOT file:
```
root -l <filename>
pulse->Draw("channel[0]:time[0]","i_evt == 12","l")
```


### Second step: waveform analysis using TimingDAQ
To get the code:
```
git clone git@github.com:heller3/TimingDAQ
cd TimingDAQ
make -j4
```
Then modify path to TimingDAQ in TimingDAQ_wrapper.sh, and run:
```
./TimingDAQ_wrapper.sh <input root file>  <output root file>
./TimingDAQ_wrapper.sh Aug31_Run3_May1.root Aug31_Run3_May1_out.root
```
### Third step: looking at the data

Event displays:
```
 python eventDisplay.py --input_file Aug31_Run3_May1_out.root --event_number 31  
```
Histograms:
```
python plastic_analysis.py  --input_file Aug31_Run3_May1_out.root
```
