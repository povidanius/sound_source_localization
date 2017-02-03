from pylab import *
import time 
from pylab import *
import numpy as np
import scipy
import array
import random
from sklearn.neighbors import NearestNeighbors 
from scipy import spatial
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
import pickle

class LocationCalculator(object):
    """  Sound source location calculation
    """    
    def __init__(self):
	self.spacing = 0.217
	self.range = 3.0
	self.step = 0.1

	self.speed_of_sound_default = self.speed_of_sound = 343.0
	self.tdoa_dim = 6 # 6
	self.tree = []
	self.mics = [
	  	      (0,0),
		      (self.spacing, 0),
	              (self.spacing,-self.spacing),
		      (0, -self.spacing)    
		    ]
	self.points = []
	
	
	#self.net = buildNetwork(6,7,2)
	#fileObject = open('./trained.net', 'w')
	#pickle.dump(self.net, fileObject)
	#fileObject.close()


    def tdoa(self, point):
	toa = self.toa_from_point(point)
	tdoa = [0]*6 
	k = 0
	for i in range(4):
		for j in range(4):
		   if j < i:
			tdoa[k] = toa[i] - toa[j]
			k = k + 1
	return tdoa[0:self.tdoa_dim]

	

    def simulate(self):
	tdoa = []	

	x, y = np.mgrid[-self.range:self.range:self.step, -self.range:self.range:self.step]
	self.points = zip(x.ravel(), y.ravel())
	#ds = SupervisedDataSet(6,2)

	for point in self.points:
		#if (point[0] >
		tdoa.append(self.tdoa(point))
		#ds.addSample(self.tdoa(point), point)

	self.tree = spatial.KDTree(tdoa)

    def simple_test(self, pt):	
	z = self.tdoa(pt)
	distance_tdoa, index = self.tree.query(np.array(z))
	distance = math.hypot(pt[0] - self.points[index][0], pt[1] - self.points[index][1])
	
	print("\n\n----------simple test-----------");
	print("point = {}".format(pt))
	#print("toa = {}".format(self.toa_from_point(pt)))
	pt_ret = self.point_from_tdoa(z)
	print("corresponding tdoa = {}".format(z))
	print("point from tdoa = {}".format(pt_ret))
	print("dist {}, index = {}, numpts = {} \n\n".format(distance, index, len(self.points)))
	
	#print("Creating trainger")
	#trainer = BackpropTrainer( self.net, ds )
	#print("Training NN")
	#trainer.trainUntilConvergence( verbose = True, validationProportion = 0.25, maxEpochs = 100, continueEpochs=10)
	
    def toa_from_point(self, point):
	toa = [0]*4
	for i in range(4):
		dist = math.hypot(point[0] - self.mics[i][0], point[1] - self.mics[i][1])
		toa[i] = 1000.0 * dist/self.speed_of_sound # milliseconds
	return toa
		
		
    def point_from_tdoa(self, tdoa):
	distance_tdoa, index = self.tree.query(np.array(tdoa))
	return self.points[index]	

    def points_from_tdoa(self, tdoa, r):
	indices = self.tree.query_ball_point(np.array(tdoa),r)
	T = [self.points[i] for i in indices]
	print("size = {}".format(len(indices)))
	return T


    def get_tdoa_vector(self, tdoa):
	measured_tdoa = [0]*6;
	k = 0
	for i in range(4):
		for j in range(4):
			if (j < i):
				measured_tdoa[k] = tdoa[i,j]
				k = k + 1
	return measured_tdoa
	

    def set_sound_speed(self, s):
	old_s = self.speed_of_sound
	self.speed_of_sound = s
	if (abs(old_s - s) > 1.0):
		self.simulate()
	
   

# Main
if __name__ == '__main__':
    c = LocationCalculator()
    z = c.simulate()

