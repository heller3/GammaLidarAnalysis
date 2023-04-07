import struct  #struct unpack result - tuple
import numpy as np
from ROOT import *
import time
import optparse
import argparse
import os

# nevents = 20
nchan=24
samples_per_frame = 1024
sampling_rate = 5 #GSa/s
samples_per_header = 6
sample_length = 4 #bits
#data_path = "/Users/heller/Google Drive/Shared drives/Gamma-Ray LIDAR/Data/Backscatter Day 2/8-31-22/Run2 BeamMonitor OUT/"
data_path = "/Users/heller/Google Drive/Shared drives/Gamma-Ray LIDAR/Data/Backscatter Day 2/8-31-22/Run 3 Beam Monitor OUT/"
output_file = "Aug31_Run3.root"


def get_y_values(input_file,event_number):
    my_file = open(input_file, 'rb')
    my_file.seek((event_number+1)*sample_length*samples_per_header + event_number*sample_length*samples_per_frame)
    raw_event = my_file.read(sample_length*samples_per_frame)
    y_axis_raw = struct.unpack("<"+str(samples_per_frame)+"f", raw_event)
    y_axis_in_V = [y * 0.001 for y in y_axis_raw] ### mV to V conversion
    return y_axis_in_V

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
channel = np.zeros([nchan,samples_per_frame],dtype=np.float32)
time_array = np.zeros([1,samples_per_frame],dtype=np.float32)

outTree.Branch('i_evt',i_evt,'i_evt/i')
outTree.Branch('channel', channel, 'channel[%i][%i]/F' %(nchan,samples_per_frame) )
outTree.Branch('time', time_array, 'time[1]['+str(samples_per_frame)+']/F' )

horizontal_interval = 1. / (sampling_rate * 1e9) ## in seconds per point
default_time_axis = horizontal_interval * np.linspace(0, samples_per_frame-1, samples_per_frame)

file_list =[]
for i in range(nchan):
    file_list.append("%s/wave_%i.dat" %(data_path,i))

nevents = find_number_of_events(file_list[0])

for i in range(nevents):
    if (i%500==0): print("Processing event %i." % i)
    for ic in range(nchan):
        this_chan_y = get_y_values(file_list[ic],i)
        #print(this_chan_y)
        channel[ic] = this_chan_y
    
    i_evt[0] = i
    time_array[0] = default_time_axis
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
