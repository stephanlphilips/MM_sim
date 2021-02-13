import copy
import numpy as np
import magpylib as magpy

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

matplotlib.rcParams.update({'font.size': 16})
matplotlib.rcParams.update({"figure.figsize" : [10, 6]})

from dataclasses import dataclass
from collections import Counter

from micromagnet_simulator.fields import field, field_qubits

class view():
	def __init__(self):
		self._unit = 'T'
	
	@property
	def unit(self):
		return self._unit

	@unit.setter
	def unit(self, value):
		if value in ['T', 'mT', 'GHz', 'MHz']:
			self._unit = value
			self.field.unit = value
		else:
			raise ValueError("invalid unit selected, options : 'T', 'mT', 'GHz', 'MHz'")

	def show(self):
		plt.show()

class qubit_view(view):
	def __init__(self, data_items, setpoints):
		super().__init__()
		self.field = field_qubits(data_items, setpoints)

	def plot_fields(self, direction):
		if self.field.ndim == 2:
			return self.__plot_1D('B{}'.format(direction), self.field.B(direction))

		if self.field.ndim == 3:
			return self.__plot_2D('B{}'.format(direction), self.field.B(direction))

	def plot_derivative(self, field_direction='x', movement_direction='x'):
		if self.field.ndim == 2:
			return self.__plot_1D("dB{}/d{}".format(field_direction, movement_direction, '/nm'),
				self.field.dB(field_direction, movement_direction))
		if self.field.ndim == 3:
			return self.__plot_2D("dB{}/d{}".format(field_direction, movement_direction, '/nm'),
				self.field.dB(field_direction, movement_direction))

	def __plot_1D(self, y_axis_name, raw_data, append_unit = ''):
		idx = self.field.active_idx

		fig = plt.figure()
		plt.title('{} plot of the MM'.format(y_axis_name))

		for i in range(raw_data.shape[1]):
			plt.plot(self.field.setpoints.setpoints[0], raw_data[:,i], label='qubit {}'.format(i+1))
		plt.xlabel('{} ({})'.format(self.field.setpoints.labels[0], self.field.setpoints.units[0]))
		plt.ylabel('{} ({})'.format(y_axis_name, self.field.unit+ append_unit))
		plt.legend()
		return fig

	def __plot_2D(self, y_axis_name, raw_data, append_unit = ''):

		fig,axes = plt.subplots(1,raw_data.shape[2])
		title ='{}'.format(y_axis_name)
		plt.title(title)
		if not isinstance(axes, np.ndarray):
			axes = [axes]
		for i in range(raw_data.shape[2]):
			ax = axes[i]
			ax.set_xlabel('{} ({})'.format(self.field.setpoints.labels[0], self.field.setpoints.units[0]))
			ax.set_ylabel('{} ({})'.format(self.field.setpoints.labels[1], self.field.setpoints.units[1]))
			c = ax.pcolor(self.field.setpoints.setpoints[0],self.field.setpoints.setpoints[1],raw_data[:,:,i])
			cbar = fig.colorbar(c, ax=ax)
			cbar.ax.set_ylabel('{} ({})'.format(y_axis_name, self.field.unit+ append_unit))

		return fig

class plot_view(view):
	def __init__(self, collection, view):
		'''
		add collection of magnet pieces to be plotted.
		'''
		super().__init__()
		self.collection = collection
		self.views = ((-1000,1000,100),(-1000,1000,80), (-30,-30,1))
		self.field = field(collection, self.views, self.unit)	

	def set_slice(self, axis, start, stop, n, level1, level2):
		self.views = [(level1,level1,1),(level2,level2,1)]
		self.views.insert(list('xyz').index(axis), (start, stop, n))

		self.field = field(self.collection, self.views, self.unit)

	def set_image(self,axis, start_1, stop_1, n_1, start_2, stop_2, n_2, level):
		self.views = [(level,level,1)]*3
		
		self.views[list('xyz').index(axis[0])] = (start_1, stop_1, n_1)
		self.views[list('xyz').index(axis[1])] = (start_2, stop_2, n_2)

		self.field = field(self.collection, self.views, self.unit)

	def plot_fields(self, direction='xyz', unit='T', plot_type='norm'):

		if self.field.dim == 1:
			return self.__plot_1D("B{}".format(direction), self.field.B(direction))

		if plot_type == 'vect' and self.field.dim == 2:
			return self.__plot_2D_vec()
		
		if plot_type == 'norm' and self.field.dim == 2:
			return self.__plot_2D_norm('B' + direction, self.field.B(direction))

	def plot_derivative(self, field_direction='x', movement_direction='x'):
		if self.field.dim == 1:
			return self.__plot_1D("dB{}/d{}".format(field_direction, movement_direction, '/nm'),
				self.field.dB(field_direction, movement_direction))

		if self.field.dim == 2:
			return self.__plot_2D_norm("dB{}/d{}".format(field_direction, movement_direction),
				self.field.dB(field_direction, movement_direction),'/nm')

	def __plot_1D(self, y_axis_name, raw_data, append_unit = ''):

		xyz = [self.field.x,self.field.y,self.field.z]
		idx = self.field.active_idx

		fig = plt.figure()
		plt.title('{} plot of the MM'.format(y_axis_name))
		plt.plot(xyz[idx[0]], raw_data)
		plt.xlabel('{} (nm)'.format('xyz'[idx[0]]))
		plt.ylabel('{} ({})'.format(y_axis_name, self.field.unit+ append_unit))

		# for electron_position in self.electron_pos['pos']:
		# 	plt.axvline(electron_position*1e9, color='r')
		return fig

	def __plot_2D_vec(self, append_unit = ''):
		fig = plt.figure()
		ax = fig.subplots(1)
		
		idx = self.field.active_idx
		plt.xlabel('{} direction (nm)'.format('xyz'[idx[0]]))
		plt.ylabel('{} direction (nm)'.format('xyz'[idx[1]]))
		
		title ='Vector plot (B{}{}) field of the MM'.format('xyz'[idx[0]], 'xyz'[idx[1]])
		plt.title(title)

		plt.xlim(self.views[idx[0]][0], self.views[idx[0]][1])
		plt.ylim(self.views[idx[1]][0], self.views[idx[1]][1])
		
		xyz = [self.field.x,self.field.y,self.field.z]
		X,Y = np.meshgrid(xyz[idx[0]],xyz[idx[1]])
		U = getattr(self.field, 'B{}'.format('xyz'[idx[0]])).T
		V = getattr(self.field, 'B{}'.format('xyz'[idx[1]])).T

		b_amp = self.field.Btot.T

		c = ax.pcolor(xyz[idx[0]],xyz[idx[1]],b_amp)
		ax.streamplot(X, Y, U, V, color=np.log(U**2+V**2))
		k = fig.colorbar(c, ax=ax)
		k.ax.set_ylabel('B{}{} ({})'.format('xyz'[idx[0]], 'xyz'[idx[1]], self.field.unit+ append_unit))

		self.__add_micromagnet_overlay(ax, idx)

		return fig

	def __plot_2D_norm(self, y_axis_name, raw_data, append_unit = ''):
		fig = plt.figure()
		ax = fig.subplots(1)

		idx = self.field.active_idx
		
		plt.xlabel('{} direction (nm)'.format('xyz'[idx[0]]))
		plt.ylabel('{} direction (nm)'.format('xyz'[idx[1]]))
		title ='{}'.format(y_axis_name)
		plt.title(title)

		plt.xlim(self.views[idx[0]][0], self.views[idx[0]][1])
		plt.ylim(self.views[idx[1]][0], self.views[idx[1]][1])
		
		self.__add_micromagnet_overlay(ax, idx)

		# im = plt.imshow(raw_data.T[::-1,:], extent=[self.views[idx[0]][0], self.views[idx[0]][1], self.views[idx[1]][0], self.views[idx[1]][1]])
		# cbar = plt.colorbar(im, ax=ax)
		xyz = [self.field.x,self.field.y,self.field.z]
		c = ax.pcolor(xyz[idx[0]],xyz[idx[1]],raw_data.T)
		cbar = fig.colorbar(c, ax=ax)
		cbar.ax.set_ylabel('{} ({})'.format(y_axis_name, self.field.unit+ append_unit))

		return fig

	def __add_micromagnet_overlay(self, ax, idx):
		for magnet in self.collection.magnets:
			x_min = magnet.shade[idx[0]][0]*1e6
			y_min = magnet.shade[idx[1]][0]*1e6
			x_max = magnet.shade[idx[0]][1]*1e6
			y_max = magnet.shade[idx[1]][1]*1e6

			patch = patches.Rectangle((x_min,y_min),x_max-x_min,y_max-y_min, linewidth=1, facecolor='none', edgecolor='w')
			ax.add_patch(patch)

