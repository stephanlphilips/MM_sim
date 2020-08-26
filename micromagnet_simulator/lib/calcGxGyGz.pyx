from libc.math cimport asinh, atan,sqrt, M_PI
from libcpp.vector cimport vector
from threading import Thread

import numpy as np
cimport numpy as np

import cython
cimport cython


@cython.wraparound(False)
@cython.boundscheck(False)
@cython.nonecheck(False)
cdef vector[double] calcG(double x,double y,double z, double x_,double y_,double z_) nogil:
	
	cdef vector[double] G
	G.push_back(0)
	G.push_back(0)
	G.push_back(0)

	cdef double r = sqrt( (x-x_)*(x-x_) + (y-y_)*(y-y_) + (z-z_)*(z-z_) )
	
	G[0] = - asinh((y-y_)/sqrt( (x-x_)*(x-x_) + (z-z_)*(z-z_) ))
	G[1] = - asinh((x-x_)/sqrt( (y-y_)*(y-y_) + (z-z_)*(z-z_) ))
	G[2] = 0.5 * atan((2*(z-z_)*(y-y_)*(x-x_)*r)/((z-z_)*(z-z_)*r*r - (x-x_)*(x-x_)*(y-y_)*(y-y_)))

	return G


@cython.wraparound(False)
@cython.boundscheck(False)
@cython.nonecheck(False)
cdef vector[double] calcB(double Ms, double x,double y,double z, double W,double D,double L, double[:,:,:] z_cache, double[:,:,:] z_offset) nogil:

	cdef vector[double] B
	B.push_back(0)
	B.push_back(0)
	B.push_back(0)


	# cache
	cdef vector[double] G
	cdef double prefactor
	cdef double Gz_prev

	cdef int i = 0
	cdef int j = 0
	cdef int k = 0
	for i in range(2):
		for j in range(2):
			for k in range(2):
				prefactor = Ms/(M_PI*4)*(-1)**(i+j+k)
				
				G = calcG(x,y,z, (-1)**i*W/2, (-1)**j*D/2, (-1)**k*L/2)
				Gz_prev = z_cache[i,j,k]
				# if jump
				if Gz_prev - G[2] > 0.5:
					z_offset[i,j,k] += M_PI/2
				elif G[2] - Gz_prev > 0.5:
					z_offset[i,j,k] -= M_PI/2

				z_cache[i,j,k] = G[2]
				G[2] += z_offset[i,j,k]


				B[0] += prefactor*G[0]
				B[1] += prefactor*G[1]
				B[2] += prefactor*G[2]


	return B



@cython.wraparound(False)
@cython.boundscheck(False)
@cython.nonecheck(False)
@cython.cdivision(True)
cdef c_calcGxGyGz(double Ms, double x_pos, np.ndarray[double, ndim=1] y_pos, np.ndarray[double, ndim=1] z_pos,
	double W,double D,double L,double magnetx,double magnety,double magnetz):
	"""
	calculation of magnetic field of unifrom magnetisation, taken from Goldman et al. 2000, Appl. Phys. A
	
	Args:
		Ms : magnetisation in tesla
		x_pos : x positions you want to calculate for.
		y_pos : y positions you want to calculate for.
		z_pos : z postion of the the plane where you want to calcualte in.
		W : size of magnet along x
		D : size of magnet along y
		L : size of magnet along z
		magnetx : center of magnet along x
		magnety : center of magnet along y
		magnetz : center of magnet along z

	Note : change axis coordinates appriatelay. Magnet assumed here to be magnetized in Z!
	"""

	cdef double[:,:,:] B_view
	B_view = np.empty([len(y_pos), len(z_pos),3])

	# make memoryviews of input variables.
	cdef double[:] c_y_pos = y_pos
	cdef double[:] c_z_pos = z_pos
	cdef int size_y = c_y_pos.size
	cdef int size_z = c_z_pos.size

	cdef vector[double] B_single

	cdef int y_idx
	cdef int z_idx
		
	# z_cache
	cdef double[:,:,:] z_cache = np.zeros([2,2,2])
	cdef double[:,:,:] z_offset = np.zeros([2,2,2])

	with nogil:
		for y_idx in xrange(size_y):
			for z_idx in xrange(size_z):

				if y_idx%2 != 0:
					z_idx = size_z-z_idx -1

				B_single = calcB(Ms,  x_pos-magnetx, c_y_pos[y_idx]-magnety, c_z_pos[z_idx]-magnetz,W,D,L, z_cache, z_offset)
				B_view[y_idx, z_idx, 0] = B_single[0]
				B_view[y_idx, z_idx, 1] = B_single[1]
				B_view[y_idx, z_idx, 2] = B_single[2]

	return B_view


# dataclass
class B_field_results(object):
	def __init__(self, Bx, By, Bz):
		self.Bx = np.asarray(Bx)
		self.By = np.asarray(By)
		self.Bz = np.asarray(Bz)

def _calcGxGyGz(Br, x_pos, y_pos, z_pos, Dx,Dy,Dz,magnetx,magnety,magnetz):
	return c_calcGxGyGz(Br, x_pos, y_pos, z_pos, Dx,Dy,Dz,magnetx,magnety,magnetz)

class calcGxGyGz(Thread):
	# calculate the field of the micromagnet defined by the spec.
	def __init__(self, micromagnet_specification):
		'''
		Args:
			micromagnet_specification (micromagnet_spec) : spec of the magnet
		'''
		super().__init__()
		self.micromagnet_specification = micromagnet_specification
		self.result = None

		self.start()

	def run(self):
		B = _calcGxGyGz(*self.micromagnet_specification)
		self.result = B_field_results(B[:,:,0], B[:,:,1], B[:,:,2])