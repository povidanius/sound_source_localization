from pylab import *
import matplotlib.animation as animation
import serial
import time 
import binascii
import matplotlib.pyplot as plt
from matplotlib import gridspec
from pylab import *
import numpy as np
import scipy
import dtw
import array
from numpy.fft import fft, ifft, fft2, ifft2, fftshift
import random
from location_calculator import *


class Monitor(object):
    """  This is supposed to be the class that will capture the data from
        whatever you are doing.
    """    
    def __init__(self,N):

	self.time = 0
	self.samplesPerUSec = 0
	self.data = []
	self.corr = np.zeros((4,4))
	self.shifts = np.zeros((4,4), dtype=np.int)
	self.tdoa = np.zeros((4,4))
	self.event_index = -1
	spacing = 0.217
	self.speed_of_sound = 343.0
	self.ser = serial.Serial(
		    port='/dev/ttyACM0',\
		    baudrate=9600,\
		    parity=serial.PARITY_NONE,\
		    stopbits=serial.STOPBITS_ONE,\
		    bytesize=serial.EIGHTBITS,\
		    timeout=None)
	self.ser.flushInput()
        self.ser.flushOutput()

	self.locator = LocationCalculator()
	self.locator.simulate()
	time.sleep(5)

	

    def waitForData(self):	
	"""
		Main loop.
	"""	        
	line = ""
	i = 0
	self.data = []
	while (True): 
		print("Waiting for data packet")
		line = self.ser.readline()
		line = line[0:len(line)-2]
		#print (line)
		#print("{} {}".format(line, len(line)))

		if (len(line) == 6144):
			#line = line[0:6144]				
			#print(line)
			byte_array = bytearray.fromhex(line)
			self.data.append(array.array('f', byte_array))
			#print("i = {}".format(i))
			#print binascii.hexlify(self.data[i])
			#print("{}".format(self.data[0]))
			i = i + 1
		if (line[0] == 'T'):
			self.time = float(line.split(" ")[1])
			print("Time : {}".format(self.time))
		if (line[0] == 'V'):
			self.speed_of_sound = float(line.split(" ")[1])
			self.locator.set_sound_speed(self.speed_of_sound)			
			print("Speed of sound: {}".format(self.speed_of_sound))
		if (line[0] == 'S'):
			self.samplesPerUSec = float(line.split(" ")[1])
			print("Samples per sec.: {}".format(self.samplesPerUSec))
		if (line[0] == 'I'):
			self.event_index = int(line.split(" ")[1])
			print("Event index: {}".format(self.event_index))
		if (line == "END" and len(self.data) < 4):
			print("Invalid packet. {}".format(len(self.data)));				
			#self.plotSingleData()
			i = 0			
			self.data = []					
		elif (line == "END" and len(self.data) == 4):
			print("Packet received, analysing. {}".format(len(self.data)))
			for j in range(4):
				print("Normalizing data {}".format(j))
				self.normalize(self.data[j])
			
			self.analyse()
			self.plotData()
			i = 0
			self.data = []		

    def plotSingleData(self):
		f, axarr = plt.subplots(1, 1)
		axarr[0,0].plot(self.data[0], 'r-') 
		plt.show()

    def plotData(self):
        """
            Plot data.
        """
	colors = ['g','b','r','k']

	measured_tdoa = self.locator.get_tdoa_vector(self.tdoa)
	print("measured tdoa {}".format(measured_tdoa))
	estimated_location = self.locator.point_from_tdoa(measured_tdoa)
	print("locator::estimated_location = {}".format(estimated_location))
	estimated_locations = self.locator.points_from_tdoa(measured_tdoa, 0.2)


	fig = plt.figure() 
	gs = gridspec.GridSpec(4, 3) 


	# Location data cell
	ax_location = plt.subplot(gs[0:2,2])
	ax_location.axis([-self.locator.range, self.locator.range, -self.locator.range, self.locator.range])
	#ax_location.plot([0, estimated_location[0]], [0, estimated_location[1]], 'ro')
	ax_location.arrow(0, 0, estimated_location[0], estimated_location[1], head_width=0.05, head_length=0.1, fc='k', ec='k')

	for loc in estimated_locations:
		ax_location.plot([0, loc[0]], [0, loc[1]], 'b.')

	for j in range(4):
		ax_location.plot([self.locator.mics[j][0]], [self.locator.mics[j][1]], colors[j]+'o')


	# Text data cell
	ax = plt.subplot(gs[2:4,2])
	ax.axis([0.0, 1.0, 0.0, 1.0])
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
	#ax.text(0.1, 0.8 , r'an equation: $E=mc^2$', fontsize=10)	
	ax.text(0.1, 0.9, r'Location: ({},{})'.format(estimated_location[0], estimated_location[1]), fontsize=10)
	ax.text(0.1, 0.85 , r'Speed of sound: ${0:.2f}m/s$'.format(self.speed_of_sound), fontsize=10)
	ax.text(0.1, 0.80, r'Samples/ms: {}'.format(self.samplesPerUSec), fontsize=10)


	ax = plt.subplot(gs[0,0])
	ax.plot([self.event_index], [self.data[0][self.event_index]], 'ro') #bug?
	
        for j in range(4):
	    ax = plt.subplot(gs[j,0])
	    ax.plot(self.data[j], colors[j]+'-')     	       
            i_match = 0 #np.argmax(self.corr[j,:])       
            shift = -self.shifts[j, i_match]
            #print("Data {}, matched {}, corr {}, shift {}, delta_t {} millis.".format(j, i_match,self.corr[j, i_match], shift, self.tdoa[j,i_match]))
	  
            data1 = self.data[j]
            data2 = self.data[i_match]
	
	    if (shift > 0):
		    data1 = np.roll(data1, shift)	
		    data1[0:shift] = 0
	    else:
		    data2 = np.roll(data2, -shift)	
		    data2[0:-shift] = 0
       
	    ax1 = plt.subplot(gs[j,1])
	    ax1.plot(data1, colors[j]) 
	    if (self.corr[j,i_match] > 0.65):	
		    ax1.plot(data2, colors[i_match]+'-.') 
	
	    ax1.set_title("{}, {}".format(i_match, shift))

	figure = plt.gcf()
	figure.set_size_inches(18, 16)
	plt.savefig('./localization.pdf', dpi=600)
        plt.show()




    def normalize(self, data):
	self.demean(data)
	return

	data /= np.max(np.abs(data),axis=0)
	data *= 255
	data -= 128

	N = len(data)
	a_mean = np.mean(data)
    	a_max = max(np.abs(data))   
	a_mean = np.mean(data)
	t_max = 128
	max_r = 1 - t_max/a_max
	f_max = -1

	for i in range(N):
		x_abs = abs(data[i])
		factor = max_r * x_abs / a_max
		dat = (1 - factor) * data[i]
		absdat = abs(dat)
		if (absdat <= t_max):
		    data[i] = dat
		# noise reduction
		if (absdat < t_max / 2):
		    zz = data[i] * absdat *2 / t_max;	
		    data[i] = data[i] * absdat * 2 / t_max;
		# weighting
		if (absdat >= t_max*0.75 and f_max == -1):
		    f_max = i
		if (f_max >= 0):		  
		    data[i] = data[i] * (1 - min(1, ((i - f_max))/(N/2)))	

    def demean(self, data):
	N = len(data)
	a_mean = np.mean(data)
	#print("len {}, mean {}".format(N, a_mean))
	for i in range( N):
		data[i] = data[i] - a_mean
	return
		
    def analyse(self):	
	n = len(self.data[0])
	for i in range(len(self.data)):
		for j in range(len(self.data)):		
		  if j > i: 		 
			sig1 = self.data[i]
			sig2 = self.data[j]
						
			c = self.cross_correlation_using_fft(sig1, sig2)
			self.shifts[i,j] = -self.compute_shift(sig1, sig2, c)
			self.tdoa[i,j] = self.shifts[i,j]/self.samplesPerUSec
			self.corr[i,j] = max(c)/(np.std(sig1)*np.std(sig2)*n)

			self.shifts[j,i] = -self.shifts[i,j]
			self.tdoa[j,i] = -self.tdoa[i,j]
			self.corr[j,i] = self.corr[i,j]
			print("c({},{}) = {}, shift = {}, time_shift {}".format(i,j,self.corr[i,j], self.shifts[i,j], self.tdoa[i,j]))


    def compute_shift(self, x, y, c):
	    assert len(x) == len(y)
	    assert len(c) == len(x)
	    zero_index = int(len(x) / 2) - 1
	    shift = zero_index - np.argmax(c)
	    return shift

    def cross_correlation_using_fft(self, x, y):
	f1 = fft(x)
	f2 = fft(np.flipud(y))
    	cc = np.real(ifft(f1 * f2))
	return fftshift(cc)
	


    # clean up
   # def close(self):
      # close serial
   #   self.ser.flush()
   #   self.ser.close() 



# Main
if __name__ == '__main__':
    m = Monitor(2048)
    m.waitForData()
