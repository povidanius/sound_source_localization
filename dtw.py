"""
Created on Fri Jun 13 19:11:28 2014

Copyright (C) 2014 Eric Wilkinson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import matplotlib.pyplot as plt

class DTW(object):
    def __init__(self, template, dist_func=None):
        """
        Creates a class for calculating Dynamic Time Warping distance, 
        finding a warping path, and warping signals. Currently only for 
        1 dimentional signals
        
        Parameters
        -------------
        template (t,y) array-like: template independent variable and signal
        dist_func function: (optional) Distance function. Defaults to euclidean
        """
        self.set_template(template)
        
        if dist_func is not None:
            self.dist_func = dist_func
        else:
            self.dist_func = lambda x,y: (x-y)**2
            
            
    def set_template(self, template):
        """
        Set the template signal. Resets all parameters
        
        Parameters
        -------------
        template (t,y) array-like: template independent variable and signal
        """
        self.template = template
        self.t = template[:,0] # Template independent variable
        self.Q = template[:,1] # Template signal
        self.N = template.shape[0] # max number of sequence points
        self.R = int(self.N * 0.1) # Bounding warping window to 10%
        self.Rs = np.arange(-self.R,self.R+1,1,dtype='int32') # Warping window bounds
        self._reset()
    
    def _reset(self):
        self.dist_matrix = np.empty((self.N,self.N), dtype='float64')
        self.dist_matrix.fill(np.inf)
        self.gamma_map = {(-1, -1): 0.0}
        self.C = None
    
    def _calc_dist_matrix(self, C):
        """
        Computes the distance matrix for every sample in the template
        Q with every sample within a bounding distance in C
        """
        for i in range(self.N):
            ks = self.Rs + i
            ks = ks[(ks<self.N) & (ks>=0)]
            l = len(ks)
            self.dist_matrix[i,ks] = map(self.dist_func, self.Q[i].repeat(l), C[ks])
            self.dist_matrix[ks,i] = map(self.dist_func, self.Q[ks], C[i].repeat(l))
            
    def _get_gamma_val(self, i, j):
        """ Special getter that handles no key found issues """
        if not self.gamma_map.has_key((i,j)):
            return np.inf
        return self.gamma_map[(i,j)]
 
    def _calc_gamma_forward(self, C):
        """
        Calculates the gamma map forwards which is significanly cheaper than doing
        recursive calculation from endpoint when using bounding window size.
        
        Parameters
        ------------
        C array-like: 
        """
        (s_is, s_js) = np.where(self.dist_matrix < np.inf)
        for i in range(self.N):
            js = s_js[np.where(s_is == i)]
            for j in js:
                min_i, min_j = min((i - 1, j), (i, j - 1), (i - 1, j - 1),
                                key=lambda x: self._get_gamma_val(*x))
                self.gamma_map[(i,j)] = self.dist_matrix[i,j] + self.gamma_map[(min_i,min_j)]
                
    def _calc_path(self):
        '''
        Calculate the warping path mapping.
        '''
        i, j = (self.N - 1, self.N - 1)
        path = []
        while (i, j) != (-1, -1):
            path.append((i, j))
            min_i, min_j = min((i - 1, j), (i, j - 1), (i - 1, j - 1),
                                 key=lambda x: self._get_gamma_val(*x))
            i, j = min_i, min_j
        return np.array(path)[::-1]
    
    def calculate(self, C):
        """
        Calculates the DTW distance, the warping path, and warps both the
        input signal and the template signal. 
        
        Returns
        --------------
        dtw_distance, warping_path, C_warped, Q_warped
        """
        if not isinstance(C, np.ndarray):
            C = np.array(C)
        
        if not C.shape[0] == self.N:
            c_prime = np.interp(self.t,C[:,0],C[:,1])
            C = np.column_stack((t,c_prime))
            
        
        self._reset()
        
        self._calc_dist_matrix( C[:,1])
        self._calc_gamma_forward(C[:,1]) 
        path = self._calc_path()
        C_warped = C[path[:,1],1]
        Q_warped= self.Q[path[:,0]]
        dtw_dist = self.gamma_map[(self.N-1,self.N-1)]

        return dtw_dist, path, C_warped, Q_warped
        
    
    def plot_warped_signals(self, C_warped, Q_warped):       
        plt.figure()
        plt.plot(range(len(C_warped)), C_warped, label='C-warped')
        plt.plot(range(len(Q_warped)), Q_warped, label='Q-warped')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.show()
    
    def plot_signals(self, C):
	print "Plotting"        
        plt.figure()
        plt.plot(C[:,0], C[:,1], label='C')
        plt.plot(self.t, self.Q, label='Q')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
	plt.show()
        
        
            
if __name__ == '__main__':
    
    print "Testing %s" % __name__
    t = np.arange(0,10,0.1)
    t2 = np.arange(0,10,0.2)
    t_prime = t2 + 0.3
    y = np.cos(t)
    z = np.cos(t_prime)
    
    template = np.column_stack((t,y))
    C = np.column_stack((t2,z))
    
    dtw = DTW(template)
    dist, path, C_warped, Q_warped = dtw.calculate(C)

    print "Distance %f" % dist	
    
    dtw.plot_signals(C)
    dtw.plot_warped_signals(C_warped, Q_warped)
    
