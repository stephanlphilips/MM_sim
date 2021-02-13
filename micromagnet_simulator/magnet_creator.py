import matplotlib.pyplot as plt
import magpylib as magpy
import numpy as np
import copy

from dataclasses import dataclass
from collections import Counter

from micromagnet_simulator.loop_control.data_container import data_container, loop_ctrl
from micromagnet_simulator.loop_control.setpoint_mgr import setpoint_mgr
from micromagnet_simulator.magnet_viewer import qubit_view, plot_view

@dataclass
class mag_sim_data:
	u_mag_positions= list()
	magnetisation = tuple()
	ext_field = tuple()
	dot_positions= list()
	magnet_collection : any = None

	def __copy__(self):
		m = mag_sim_data()
		m.u_mag_positions = copy.copy(self.u_mag_positions)
		m.magnetisation = copy.copy(self.magnetisation) 
		m.ext_field = copy.copy(self.ext_field)
		m.dot_positions = copy.copy(self.dot_positions)

		return m

	def make_collection(self):
		self.magnet_collection = magnet_collection()
		for magnet in self.u_mag_positions:
			magnet.set_magnetisation(self.magnetisation)
			self.magnet_collection += magnet
		self.magnet_collection.set_positions(self.dot_positions)

	def move(self, displacement):
		self.magnet_collection.move(displacement)

@dataclass
class magnet():
	x: float
	y: float
	z: float
	delta_x : float
	delta_y : float
	delta_z : float
	magnetisation : tuple = (1000,0,0)

	def set_magnetisation(self, magnetisation):
		self.magnetisation = magnetisation

	def return_magnet(self):
		return magpy.source.magnet.Box(mag=self.magnetisation, 
			dim=(self.delta_x, self.delta_y, self.delta_z),
			pos=(self.x, self.y, self.z))

	@property
	def shade(self):
		return [(self.x-self.delta_x/2, self.x+self.delta_x/2),
		        (self.y-self.delta_y/2, self.y+self.delta_y/2),
		        (self.z-self.delta_z/2, self.z+self.delta_z/2)]

class magnet_collection():
	def __init__(self):
		self.coll = magpy.Collection()
		self.magnets = list()
		self.qubit_positions = list()

	def __add__(self, magnet, electron =[]):
		self.coll.addSources(magnet.return_magnet())
		self.magnets.append(magnet)
		return self

	def set_positions(self, pos):
		self.qubit_positions = np.asarray(pos)

	def move(self, displacement):
		self.coll.move(displacement)


class umag_creator():
	def __init__(self):
		'''
		generate object to create magnets with

		mode (int) : what needs to be simulated (e.g. 2D pictures of the fiels, or just properties at the dot locations)
		'''
		self.data = data_container(mag_sim_data())
		self._setpoints = setpoint_mgr()
	@loop_ctrl
	def set_magnetisation(self, Mx, My, Mz):
		'''
		set's the magnetisation of the magnet (x,y,z) (unit in tesla)
		'''
		self.data_tmp.magnetisation = (Mx*1e3, My*1e3, Mz*1e3)
		return self.data_tmp

	@loop_ctrl
	def set_external_field(self, Bx, By, Bz):
		'''
		set's the external field where the magnet is in (x,y,z) (unit in tesla)
		'''
		self.data_tmp.ext_field = (Bx, By, Bz)
		return self.data_tmp

	@loop_ctrl
	def add_electron_position(self, x ,y ,z):
		self.data_tmp.dot_positions.append((x*1e-6,y*1e-6,z*1e-6))
		return self.data_tmp

	@loop_ctrl
	def add_cube(self, x,y,z, delta_x, delta_y, delta_z):
		'''
		add's a block of your favourite magnet material

		Args:
			x,y,z (double) : center coordinates of the magnet (unit in nm)
			delta_x, delta_y, delta_z (double) : widht, length and hight of the magnet (unit in nm)
		'''
		self.data_tmp.u_mag_positions.append(magnet(x*1e-6, y*1e-6, z*1e-6, delta_x*1e-6, delta_y*1e-6, delta_z*1e-6))
		return self.data_tmp

	@loop_ctrl
	def add_triangle(self, p1_x, p1_y, p1_z, p2_x, p2_y, p2_z,p3_x, p3_y, p3_z, static_axis, delta, n_magnets=20):
		'''
		adds a triangular piece of micromagnet, h_magnet defines the height of that piece
		'''
		point_1 = (p1_x, p1_y, p1_z)
		point_2 = (p2_x, p2_y, p2_z)
		point_3 = (p3_x, p3_y, p3_z)

		moving_axes = [0,1,2]
		moving_axes.pop(list('xyz').index(static_axis))
		# define in which area the triangle is located

		x_pos = [point_1[moving_axes[0]], point_2[moving_axes[0]], point_3[moving_axes[0]]]
		cnt = dict((v,k) for k,v in Counter(x_pos).items())
		x_min = cnt[1]
		x_max = cnt[2]

		y_pos = [point_1[moving_axes[1]], point_2[moving_axes[1]], point_3[moving_axes[1]]]
		cnt = dict((v,k) for k,v in Counter(y_pos).items())
		y_min = cnt[1]
		y_max = cnt[2]
		
		x_seg = np.linspace(x_min, x_max, n_magnets+1)
		for i in range(n_magnets):
			x_0, x_1 = x_seg[i], x_seg[i+1]
			y_0 = y_max
			y_1 = y_max - (y_max - y_min)*(i+.5)/n_magnets

			properties = [0]*3
			properties[moving_axes[0]] = ((x_1+x_0)/2,  x_1-x_0)
			properties[moving_axes[1]] = ((y_1+y_0)/2,  y_1-y_0)
			properties[list('xyz').index(static_axis)] = (point_1[list('xyz').index(static_axis)],  delta)
			x,y,z, delta_x, delta_y, delta_z = (properties[0][0], properties[1][0], properties[2][0],
				np.abs(properties[0][1]), np.abs(properties[1][1]), np.abs(properties[2][1]))
			self.data_tmp.u_mag_positions.append(magnet(x*1e-6, y*1e-6, z*1e-6, delta_x*1e-6, delta_y*1e-6, delta_z*1e-6))

		return self.data_tmp

	def generate_view(self, show_geom = False):
		if self.data.size == 1:
			m_coll = magnet_collection()

			for m in self.data[0].u_mag_positions:
				m_coll += m

			if show_geom == True:
				fig = plt.figure(figsize=(9,5))
				ax1 = fig.add_subplot(121, projection='3d')
				magpy.displaySystem(m_coll.coll, subplotAx=ax1, suppress=True)

			return plot_view(m_coll, view=None)
		else:
			raise ValueError('no support for multidimensional views.')

	def generate_qubit_prop(self):
		for data_item in self.data.flatten():
			data_item.make_collection()

		return qubit_view(self.data, self._setpoints)
