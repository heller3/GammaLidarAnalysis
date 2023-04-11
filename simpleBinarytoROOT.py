import struct  #struct unpack result - tuple
import numpy as np
from ROOT import *
import time
import optparse
import argparse
import os

# nevents = 20
nchan=24
ntrig=3
nchan_tot=nchan+ntrig
samples_per_frame = 1024
sampling_rate = 5 #GSa/s
samples_per_header = 6 ## e.g. number of 4 byte chunks in header
sample_length = 4 #bytes
data_path = "/Users/heller/Google Drive/Shared drives/Gamma-Ray LIDAR/Data/Backscatter Day 2/8-31-22/Run2 BeamMonitor OUT/"
# data_path = "/Users/heller/Google Drive/Shared drives/Gamma-Ray LIDAR/Data/Backscatter Day 2/8-31-22/Run 3 Beam Monitor OUT/"
output_file = "Aug31_Run2.root"
time_calibration_file = "V1742_tcal_v2"
time_calibration_file_triggers = "V1742_trigger_tcal_v1"

def dump_header_info(input_file,event_number,ch):
    my_file = open(input_file, 'rb')
    my_file.seek((event_number)*sample_length*samples_per_header + event_number*sample_length*samples_per_frame)
    header = my_file.read(sample_length*samples_per_header)
    header_unpack = struct.unpack("<"+str(samples_per_header*2)+"h", header)### testing short instead of int
    print("Header from event %i ch %i is: "%(event_number,ch), header_unpack)
   # if(header_unpack[4]!=event_number): print("[WARNING] Event number mismatch with binary data, ${}".format(input_file))
    #return header_unpack[3]

def get_trigger_cell(input_file,event_number,ch):
    my_file = open(input_file, 'rb')
    my_file.seek((event_number)*sample_length*samples_per_header + event_number*sample_length*samples_per_frame)
    header = my_file.read(sample_length*samples_per_header)
    header_unpack = struct.unpack("<"+str(samples_per_header)+"i", header)
  #  print("Header from event %i ch %i is: "%(event_number,ch), header_unpack)
    if(header_unpack[4]!=event_number): print("[WARNING] Event number mismatch with binary data, ${}".format(input_file))
    return header_unpack[3]

def get_y_values(input_file,event_number):
    my_file = open(input_file, 'rb')
    my_file.seek((event_number+1)*sample_length*samples_per_header + event_number*sample_length*samples_per_frame)
    raw_event = my_file.read(sample_length*samples_per_frame)
    y_axis_raw = struct.unpack("<"+str(samples_per_frame)+"f", raw_event)
    y_axis_in_V = [y * 0.001 for y in y_axis_raw] ### mV to V conversion
    return y_axis_in_V

def load_time_calibrations():
    global cell_dt_array
    cell_dt_array = np.zeros([nchan_tot,samples_per_frame],dtype=np.float32)
    my_file = open(time_calibration_file,"r")
    # print("length of calibration file"%len(my_file))
    for il,line in enumerate(my_file):
        calibrations_this_cell_number = line.split(",")[0:nchan]
        for ic in range(nchan):
            cell_dt_array[ic][il] = calibrations_this_cell_number[ic]
    
    my_file = open(time_calibration_file_triggers,"r")
    for il,line in enumerate(my_file):
        calibrations_this_cell_number = line.split(",")[0:ntrig]
        for ic in range(ntrig):
            cell_dt_array[ic+nchan][il] = calibrations_this_cell_number[ic]

    
def get_calibrated_x_axis(input_file,event_number,channel_number,trigger_cell):
    ### find zero time of zeroth channel in this chip
    if channel_number < 24: 
        chip_number = int(channel_number / 8)
    else: ## triggers
        chip_number = channel_number-24

    zeroth_channel_in_chip = chip_number * 8
    t0_ch0_this_chip = 0
    for i in range((1024 - trigger_cell) % 1024):
        t0_ch0_this_chip += cell_dt_array[zeroth_channel_in_chip][(i+trigger_cell)%1024]

    ### find zero time of this channel
    t0_this_ch = 0
    for i in range((1024 - trigger_cell) % 1024):
       t0_this_ch += cell_dt_array[channel_number][(i+trigger_cell)%1024]    

    adjustment = t0_this_ch - t0_ch0_this_chip
    
    x_axis = np.zeros([samples_per_frame],dtype=np.float32)
    ### define time axis starting from 0, given trigger_cell for this chip
    this_time = 0 - adjustment
    for i in range(1024):
        x_axis[i] = this_time*1.0e-9
        this_time += cell_dt_array[channel_number][(i+trigger_cell) % 1024]
        
    return x_axis

def compare_adjustments(input_file,event_number,channel_number,trigger_cell):
    time_array = np.zeros([nchan,samples_per_frame],dtype=np.float32)
    for chan in range(nchan):
        for i in range(1024):
            for j in range(i):
                time_array[chan][i] += cell_dt_array[chan][(j+trigger_cell) % 1024]

    t1 = time_array[0][(1024-trigger_cell) % 1024]
    t2 = time_array[1][(1024-trigger_cell) % 1024]

    adjustment_jinr = t2-t1

     ### find zero time of zeroth channel in this chip
    chip_number = int(channel_number / 8)
    zeroth_channel_in_chip = chip_number * 8
    t0_ch0_this_chip = 0
    for i in range((1024 - trigger_cell) % 1024):
        t0_ch0_this_chip += cell_dt_array[zeroth_channel_in_chip][(i+trigger_cell)%1024]

    ### find zero time of this channel
    t0_this_ch = 0
    for i in range((1024 - trigger_cell) % 1024):
       t0_this_ch += cell_dt_array[channel_number][(i+trigger_cell)%1024]    

    adjustment = t0_this_ch - t0_ch0_this_chip

    x_axis =[]
    ### define time axis starting from 0, given trigger_cell for this chip
    this_time = 0 - adjustment
    this_time=0
    for i in range(1024):
        x_axis.append(this_time*1.0e-9)
        this_time += cell_dt_array[channel_number][(i+trigger_cell) % 1024]
        
    if channel_number==1:
        print("Adjustment JINR vs Me: {} vs {}".format(adjustment_jinr,adjustment))
        for i in range(6): print("{} vs {}".format(time_array[1][i],x_axis[i]))


def test_end_of_file(input_file):
    size_of_file = os.path.getsize(input_file)
    print("opening %s, %i bytes" %(input_file,size_of_file))

    my_file = open(input_file, 'rb')

    my_file.seek(int(size_of_file) - 32)
    raw_event = my_file.read(4*4)
    y_axis_raw = struct.unpack("<"+str(4)+"f", raw_event)
    print("last 4 floats: ")
    print(y_axis_raw)
    print("attempt to keep going")
    raw_event = my_file.read(4*4)
    y_axis_raw = struct.unpack("<"+str(4)+"f", raw_event)
    print("after last 4 floats: ")
    print(y_axis_raw)

    number_of_events = int(size_of_file / (sample_length*samples_per_header + sample_length*samples_per_frame))
    print("total number of events", number_of_events)
    event_nm1 = get_y_values(input_file,number_of_events-1)
    print("event n-1",event_nm1)
    event_n = get_y_values(input_file,number_of_events)
    print("event n",event_n) ##crashes

def find_number_of_events(input_file):
    size_of_file = os.path.getsize(input_file)
    number_of_events = int(size_of_file / (sample_length*samples_per_header + sample_length*samples_per_frame))
    return number_of_events

start = time.time()

outRoot = TFile(output_file, "RECREATE")
outTree = TTree("pulse","pulse")

i_evt = np.zeros(1,dtype=np.dtype("u4"))
channel = np.zeros([nchan_tot,samples_per_frame],dtype=np.float32)
trigger_cell = np.zeros([nchan_tot],dtype=np.dtype("u4"))
time_array = np.zeros([nchan_tot,samples_per_frame],dtype=np.float32)

outTree.Branch('i_evt',i_evt,'i_evt/i')
outTree.Branch('trigger_cell',trigger_cell,'trigger_cell[%i]/i'%nchan_tot)
outTree.Branch('channel', channel, 'channel[%i][%i]/F' %(nchan_tot,samples_per_frame) )
outTree.Branch('time', time_array, 'time[%i][%i]/F' %(nchan_tot,samples_per_frame) )

horizontal_interval = 1. / (sampling_rate * 1e9) ## in seconds per point
uncalibrated_time_axis = horizontal_interval * np.linspace(0, samples_per_frame-1, samples_per_frame)

file_list =[]
for i in range(nchan):
    file_list.append("%s/wave_%i.dat" %(data_path,i))
for i in range(ntrig):
    file_list.append("%s/TR%i_%i.dat" %(data_path,i/2,i))

nevents = find_number_of_events(file_list[0])
load_time_calibrations()
# print(cell_dt_array)
# for i in range(50):
#     for ic in range(nchan):
#         dump_header_info(file_list[ic],i,ic)
# exit()

for i in range(nevents):
    if (i%100==0): print("Processing event %i." % i)
    # if i>2: exit()
    for ic in range(nchan_tot):
        this_chan_y = get_y_values(file_list[ic],i)
        this_trigger_cell = get_trigger_cell(file_list[ic],i,ic)
        this_chan_x = get_calibrated_x_axis(file_list[ic],i,ic,this_trigger_cell)
        # if(ic==1): compare_adjustments(file_list[ic],i,ic,this_trigger_cell)
        #print(this_chan_y)
        channel[ic] = this_chan_y
        time_array[ic] = this_chan_x
        trigger_cell[ic] = this_trigger_cell
    
    
    i_evt[0] = i
    #time_array[0] = uncalibrated_time_axis
    outTree.Fill()

print("done filling the tree")
outRoot.cd()
outTree.Write()
outRoot.Close()
final = time.time()
print("\nFilling tree took %i seconds." %(final-start))

# def get_channel(input_file):   
#     my_file = open(input_file, 'rb')
#     #header = struct.unpack("<"+str(6)+"f",my_file.read(4*6)) 
#     #print(header)
#     my_file.seek(samples_per_header*sample_length)
#     my_file.seek(6*4*3 + 2*sample_length*samples_per_frame)

#     raw_event = my_file.read(sample_length*samples_per_frame)
#     y_axis_raw = struct.unpack("<"+str(samples_per_frame)+"f", raw_event)
#     print(y_axis_raw)

#     # data = struct.unpack('f',my_file.read(1024))
#     # print(data)
#         # [header] = fread(fidt{tr},6, 'int');
#         # tct(tr,event+1)=header(4);
#         # headereventt{tr}(event+1)=header(5);
#         # headereventpost{tr}(event+1)=ftell(fidt{tr});
#         # datat{tr} = fread(fidt{tr},1024, 'single');

# get_channel(input_file)
