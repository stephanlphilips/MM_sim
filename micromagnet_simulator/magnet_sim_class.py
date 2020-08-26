from micromagnet_simulator.lib.data_classes import micromagnet_spec
import micromagnet_simulator.lib.calcGxGyGz as mag_sim
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from dataclasses import dataclass


class micromagnet_simulator(object):
	"""docstring for micromagnet_simulator"""
	def __init__(self, n_steps):
		'''
		init class for magnet simulator

		Args:
			n_steps (int): number of steps in the z and y direction.
		'''

		self.steps = n_steps
		#defauld magnentisation for cobalt
		self.Br = 1.8
		self.B_ext = 0
		self.micromagnets = []
		self.electron_pos = {'axis':'y', 'pos':[]}

	def remove_micromagnets(self):
		'''
		removes all micromagnets in memory, while keeping all other settings.
		'''
		self.micromagnets = []

	def add_micromagnet(self,x1_y1, x2_y2, h_magnet, h_2deg):
		'''
		Add a micromagnet

		We suppose that the micromagnet lies in the y/z plane and the height goes in the x direction.

		Args:
			x1_y1 (tuple): specifiy x and y coordinates of the corner (down_left_corner)
			x2_y2 (tuple): specifiy x and y coordinates of the corner (upper_right_corner)
			h_magnet (double): specify the height of the magnet
			h_2deg (double): height difference between the bottom of the magnet and the 2def
		'''
		my_micromagnet = {'x1_y1': x1_y1, 'x2_y2': x2_y2, 'h_magnet': h_magnet, 'h_2deg': h_2deg}
		self.micromagnets.append(my_micromagnet)

	def set_magnetisation(self,Br):
		'''
		Set how much the magnet is magnetized
		Args:
			Br (double): magnetisation of the magnet
		'''
		self.Br = Br

	def set_external_field(self, B_ext):
		'''
		Apply a field (unit is T)
		Args:
			B_ext (double): value of the external field (along Z direction)
		'''
		self.B_ext =B_ext

	def calculate(self, canvas=None):
		'''
		calculates the fiels generated by the deposited micromagnets
		Args:
			canvas (list): define canvas as a list of two tuples.

		'''

		if canvas is None:
			self.pos_1	, self.pos_2 = self._get_canvas_size()
		else:
			self.pos_1	, self.pos_2 = canvas

		self.z_pos = np.linspace(self.pos_1	[0], self.pos_2[0], self.steps+1)
		self.y_pos = np.linspace(self.pos_1	[1], self.pos_2[1], self.steps+1)

		self.Bx= np.zeros([self.steps+1, self.steps+1])
		self.By= np.zeros([self.steps+1, self.steps+1])
		self.Bz= np.zeros([self.steps+1, self.steps+1])

		magnet_calc_specs = []

		for magnet in self.micromagnets:
			z_min = np.min([magnet['x1_y1'][0],magnet['x2_y2'][0]])
			z_max = np.max([magnet['x1_y1'][0],magnet['x2_y2'][0]])

			y_min = np.min([magnet['x1_y1'][1],magnet['x2_y2'][1]])
			y_max = np.max([magnet['x1_y1'][1],magnet['x2_y2'][1]])

			magnet_x0 = magnet['h_2deg'] + magnet['h_magnet']/2
			delta_x = magnet['h_magnet']

			delta_y = y_max - y_min
			magnet_y0 = (y_max + y_min)/2

			delta_z = z_max -z_min
			magnet_z0 = (z_max + z_min)/2

			spec = micromagnet_spec(0, self.y_pos, self.z_pos, magnet_x0, magnet_y0, magnet_z0, delta_x, delta_y, delta_z, self.Br)
			magnet_calc_specs.append(spec)

		uM_calculators = []
		# calculatiom object are classes as a thread. This works as the gil is releasued during the calculcation
		for spec in magnet_calc_specs:
			uM_calculators.append(mag_sim.calcGxGyGz(spec))

		for calculator in uM_calculators:
			calculator.join()

		for calculator in uM_calculators:
			# included in solver...
			self.Bx += calculator.result.Bx
			self.By += calculator.result.By
			self.Bz += calculator.result.Bz

		self.Bz += self.B_ext

	def set_electron_pos(self, pos, axis='z'):
		'''
		define the positions of the spin qubits. The qubits are assumed to be placed either on the z or y axis.

		Args:
			pos (list): list of positions (e.g. [-100e-9,100e-9])
			axis (char): y or z
		'''
		
		self.electron_pos['axis'] = axis
		self.electron_pos['pos'] = pos

	def plot_fields(self, mode='all', direction='xyz', unit='T'):
		'''
		plot the fields of the micromagnets in the canvas defined in the calculate section.
		
		for each direction a seperate plot will be made
		Args:
			mode (str): 'all', or 'dots' (plot all the calculated fields (2D plot) or only where the dots are (1D plot))
			direction (str): directions you want to plot.
			unit (str) : T'/mT/GHz/MHz
		'''

		mult = self._get_unit_conversion(unit)

		if mode =='all':
			if 'x' in direction:
				self._mk_2D_plot(self.Bx*mult, 'B_x component of micromagnet field.', 'Field ({})'.format(unit))
			if 'y' in direction:
				self._mk_2D_plot(self.By*mult, 'B_y component of micromagnet field.', 'Field ({})'.format(unit))
			if 'z' in direction:
				self._mk_2D_plot(self.Bz*mult, 'B_z component of micromagnet field.', 'Field ({})'.format(unit))

		if mode == 'dots':
			if self.electron_pos['axis'] == 'z':
				y0 = np.argmin(np.abs(self.y_pos))

				z_range = [np.min(self.electron_pos['pos'])-100e-9, np.max(self.electron_pos['pos'])+100e-9]
				z0 = np.argmin(np.abs(self.z_pos - z_range[0]))
				z1 = np.argmin(np.abs(self.z_pos - z_range[1]))

				data_x = self.Bx[y0, z0:z1]*mult
				data_y = self.By[y0, z0:z1]*mult
				data_z = self.Bz[y0, z0:z1]*mult

				if 'x' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, data_x, 'z-axis (nm)', 'Bx ({})'.format(unit), 'Bx field of the micromagnet.')
				if 'y' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, data_y, 'z-axis (nm)', 'By ({})'.format(unit), 'By field of the micromagnet.')
				if 'z' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, data_z, 'z-axis (nm)', 'Bz ({})'.format(unit), 'Bz field of the micromagnet.')
			if self.electron_pos['axis'] == 'y':
				# TODO
				raise NotImplemented

		plt.show()

	def plot_field_abs(self, mode='all', direction='xyz', unit='T'):
		'''
		plot the total field of the micromagnets in the canvas defined in the calculate section.
		the direction defined with part of the vector need to be counted up.

		Args:
			mode (str): 'all', or 'dots' (plot all the calculated fields (2D plot) or only where the dots are (1D plot))
			direction (str): directions you want to plot.
			unit (str) : T'/mT/GHz/MHz
		'''

		mult = self._get_unit_conversion(unit)

		if mode =='all':
			if 'x' in direction and 'y' in direction and 'z' in direction:
				self._mk_2D_plot(np.sqrt(self.Bx**2+ self.By**2+self.Bz**2)*mult, 'sum (B_abs) of B_x + B_y + B_z component of micromagnet field.', 'Field ({})'.format(unit))
			elif 'x' in direction and 'y' in direction:
				self._mk_2D_plot(np.sqrt(self.Bx**2+ self.By**2)*mult, 'sum (B_abs) of B_x + B_y component of micromagnet field.', 'Field ({})'.format(unit))
			elif 'x' in direction and 'z' in direction:
				self._mk_2D_plot(np.sqrt(self.Bx**2+ self.By**2)*mult, 'sum (B_abs) of B_x + B_z component of micromagnet field.', 'Field ({})'.format(unit))
			elif 'z' in direction and 'y' in direction:
				self._mk_2D_plot(np.sqrt(self.Bx**2+ self.By**2)*mult, 'sum (B_abs) of B_y + B_z component of micromagnet field.', 'Field ({})'.format(unit))

		if mode == 'dots':
			if self.electron_pos['axis'] == 'z':
				y0 = np.argmin(np.abs(self.y_pos))

				z_range = [np.min(self.electron_pos['pos'])-100e-9, np.max(self.electron_pos['pos'])+100e-9]
				z0 = np.argmin(np.abs(self.z_pos - z_range[0]))
				z1 = np.argmin(np.abs(self.z_pos - z_range[1]))

				data_x = self.Bx[y0, z0:z1]
				data_y = self.By[y0, z0:z1]
				data_z = self.Bz[y0, z0:z1]

				if 'x' in direction and 'y' in direction and 'z' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, np.sqrt(data_x**2+ data_y**2 + data_z**2)*mult, 'z-axis (nm)', 'Field ({})'.format(unit), 'sum (B_abs) of B_x + B_y + B_z component of micromagnet field.')
				elif 'x' in direction and 'y' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, np.sqrt(data_x**2 + data_y**2)*mult, 'z-axis (nm)', 'Field ({})'.format(unit) , 'sum (B_abs) of B_x + B_y component of micromagnet field.')
				elif 'x' in direction and 'z' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, np.sqrt(data_x**2 + data_z**2)*mult, 'z-axis (nm)', 'Field ({})'.format(unit) , 'sum (B_abs) of B_x + B_z component of micromagnet field.')
				elif 'z' in direction and 'y' in direction:
					self._plot_1D(self.z_pos[z0:z1]*1e9, np.sqrt(data_y**2 + data_z**2)*mult, 'z-axis (nm)', 'Field ({})'.format(unit) , 'sum (B_abs) of B_y + B_z component of micromagnet field.')

			if self.electron_pos['axis'] == 'y':
				z0 = np.argmin(np.abs(self.z_pos))

				y_range = [np.min(self.electron_pos['pos'])-100e-9, np.max(self.electron_pos['pos'])+100e-9]
				y0 = np.argmin(np.abs(self.y_pos - y_range[0]))
				y1 = np.argmin(np.abs(self.y_pos - y_range[1]))

				data_x = self.Bx[y0:y1, z0]
				data_y = self.By[y0:y1, z0]
				data_z = self.Bz[y0:y1, z0]

				if 'x' in direction and 'y' in direction and 'z' in direction:
					self._plot_1D(self.y_pos[y0:y1]*1e9, np.sqrt(data_x**2+ data_y**2 + data_z**2)*mult, 'y-axis (nm)', 'Field ({})'.format(unit), 'sum (B_abs) of B_x + B_y + B_z component of micromagnet field.')
				elif 'x' in direction and 'y' in direction:
					self._plot_1D(self.y_pos[y0:y1]*1e9, np.sqrt(data_x**2 + data_y**2)*mult, 'y-axis (nm)', 'Field ({})'.format(unit) , 'sum (B_abs) of B_x + B_y component of micromagnet field.')
				elif 'x' in direction and 'z' in direction:
					self._plot_1D(self.y_pos[y0:y1]*1e9, np.sqrt(data_x**2 + data_z**2)*mult, 'y-axis (nm)', 'Field ({})'.format(unit) , 'sum (B_abs) of B_x + B_z component of micromagnet field.')
				elif 'z' in direction and 'y' in direction:
					self._plot_1D(self.y_pos[y0:y1]*1e9, np.sqrt(data_y**2 + data_z**2)*mult, 'y-axis (nm)', 'Field ({})'.format(unit) , 'sum (B_abs) of B_y + B_z component of micromagnet field.')

		# plt.show()

	def plot_diff(self, mode, field, axis, plot = True):
		'''
		plot differential plot 

		Args:
			mode (str): 'all' or 'dots'
			field (str): select which fields to differentiate (e.g. 'xy' which would be Bx and By)
			axis (str): select axis to which to differentiate (e.g. 'y', so you get Bx/dy + By/dy)
		'''

		my_diff_field = np.zeros([self.steps, self.steps])
		for field_direction in field:
			for ax in axis:
				matrix_direction = 0
				dx = (self.y_pos[1]-self.y_pos[0])*1e6
				if ax == 'z':
					matrix_direction = 1
					dx = (self.z_pos[1]-self.z_pos[0])*1e6
				
				if field_direction == 'x':
					my_diff_field += np.power(np.diff(self.Bx, axis=matrix_direction)/dx,2)[:self.steps, :self.steps]
				elif field_direction == 'y':
					my_diff_field += np.power(np.diff(self.By, axis=matrix_direction)/dx,2)[:self.steps, :self.steps]
				elif field_direction == 'z':
					my_diff_field += np.power(np.diff(self.Bz, axis=matrix_direction)/dx,2)[:self.steps, :self.steps]
		
		my_diff_field = np.sqrt(my_diff_field)


		if plot==True:
			self._mk_2D_plot(my_diff_field, "diff_plot B{}/d{}".format(field, axis), 'Field Gradient (mT/nm)')


		return my_diff_field

	def plot_diff_abs(self, mode, axis):
		'''
		plot differential plot 

		Args:
			mode (str): 'all' or 'dots'
			axis (str): select axis to which to differentiate (e.g. 'y', so you get Bx/dy + By/dy)
		'''

		my_diff_field = np.zeros([self.steps, self.steps])
		for ax in axis:
			matrix_direction = 0
			dx = (self.y_pos[1]-self.y_pos[0])*1e6
			if ax == 'z':
				matrix_direction = 1
				dx = (self.z_pos[1]-self.z_pos[0])*1e6
			
			my_diff_field += np.power(np.diff(np.sqrt(self.Bx**2 + self.By**2 + self.Bz**2), axis=matrix_direction)/dx,2)[:self.steps, :self.steps]

		my_diff_field = np.sqrt(my_diff_field)


		self._mk_2D_plot(my_diff_field, "title todo", 'Field Gradient (mT/nm)')

	def generate_dot_report(self, verbose = False):
		local_field = []
		gradient = []
		decoherence_gradient = []
		# get relevant gradients.
		gradient_data = self.plot_diff('all', 'xy', 'z', plot =False)
		decoherence_gradient_data = self.plot_diff('all', 'z', 'yz', plot =False) # x not possible to calulate here.

		coordinates = []
		is_y = 0
		# get local field
		if self.electron_pos['axis'] == 'z':
			y0 = np.argmin(np.abs(self.y_pos))

			for dot_pos in self.electron_pos['pos']:
				coordinates.append((y0,np.argmin(np.abs(self.z_pos - dot_pos))))
		
		if self.electron_pos['axis'] == 'y':
			z0 = np.argmin(np.abs(self.z_pos))

			for dot_pos in self.electron_pos['pos']:
				coordinates.append((np.argmin(np.abs(self.y_pos - dot_pos)),z0))
			is_y = 0

		mult = self._get_unit_conversion('GHz')

		for i in range(len(coordinates)):
			field = np.sqrt(self.Bx[coordinates[i]]**2 + self.By[coordinates[i]]**2 + self.Bz[coordinates[i]]**2)
			local_field.append(field*mult)
			gradient.append(gradient_data[coordinates[i]])
			decoherence_gradient.append(decoherence_gradient_data[coordinates[i]])
			if verbose == True:
				print("dot {}:\t {:.3f} GHz at {:.3f} nm".format(i+1,field*mult, self.y_pos[coordinates[i][0+is_y]]*1e9))
				print("\t\t\t Gradient {:.3f} (mT/nm) || decoherence gradient {:.3f} (mT/nm)".format(gradient_data[coordinates[i]],decoherence_gradient_data[coordinates[i]]))
				if i >= 1:
					print("\t\t\t freq_diff {:.3f} (MHz)".format(local_field[i]*1e3- local_field[i-1]*1e3))

		return np.array(local_field), np.array(gradient), np.array(decoherence_gradient)

	def return_fields(self):
		'''
		Return calaculated field data

		Returns:
			Bx
			By
			Bz
			pos_y
			pos_z
		'''
		return self.Bx, self.By, self.Bz, self.y_pos, self.z_pos
	
	def plot_micromagnets(self, canvas_size=None):
		if canvas_size is None:
			self.pos_1	, self.pos_2 = self._get_canvas_size()
		else:
			self.pos_1	, self.pos_2 = canvas_size

		y_loc = np.linspace(self.pos_1	[0], self.pos_2[0], 1000)
		z_loc = np.linspace(self.pos_1	[1], self.pos_2[1], 1000)
		canvas = np.zeros([1000,1000])

		fig = plt.figure()
		ax = fig.subplots(1)


		plt.xlim(self.pos_1[0]*1e9, self.pos_2[0]*1e9)
		plt.ylim(self.pos_1[1]*1e9, self.pos_2[1]*1e9)

		for magnet in self.micromagnets:
			z_min = np.min([magnet['x1_y1'][0],magnet['x2_y2'][0]])*1e9
			y_min = np.min([magnet['x1_y1'][1],magnet['x2_y2'][1]])*1e9
			z_max = np.max([magnet['x1_y1'][0],magnet['x2_y2'][0]])*1e9
			y_max = np.max([magnet['x1_y1'][1],magnet['x2_y2'][1]])*1e9

			patch = patches.Rectangle((z_min,y_min),z_max-z_min,y_max-y_min,linewidth=1,edgecolor='r',facecolor='r', alpha=0.4)
			ax.add_patch(patch)
		plt.xlabel('z direction (nm)')
		plt.ylabel('y direction (nm)')
	
	def _plot_1D(self, x_data, y_data, x_label,y_label, title):
		plt.figure()
		plt.title(title)
		plt.plot(x_data, y_data)
		plt.xlabel(x_label)
		plt.ylabel(y_label)

		for electron_position in self.electron_pos['pos']:
			plt.axvline(electron_position*1e9, color='r')

	def _mk_2D_plot(self, data, title, cb_label):
		
		fig = plt.figure()
		ax = fig.subplots(1)
		plt.xlabel('z direction (nm)')
		plt.ylabel('y direction (nm)')
		plt.title(title)

		plt.xlim(self.pos_1[0]*1e9, self.pos_2[0]*1e9)
		plt.ylim(self.pos_1[1]*1e9, self.pos_2[1]*1e9)
		
		self.add_micromagnet_overlay(ax)
		im =plt.imshow(data[::-1,:], extent=[self.pos_1[0]*1e9, self.pos_2[0]*1e9, self.pos_1[1]*1e9, self.pos_2[1]*1e9])
		cbar = plt.colorbar(im, ax=ax)
		cbar.ax.set_ylabel(cb_label)

	def add_micromagnet_overlay(self, ax):
		for magnet in self.micromagnets:
			z_min = np.min([magnet['x1_y1'][0],magnet['x2_y2'][0]])*1e9
			y_min = np.min([magnet['x1_y1'][1],magnet['x2_y2'][1]])*1e9
			z_max = np.max([magnet['x1_y1'][0],magnet['x2_y2'][0]])*1e9
			y_max = np.max([magnet['x1_y1'][1],magnet['x2_y2'][1]])*1e9

			patch = patches.Rectangle((z_min,y_min),z_max-z_min,y_max-y_min, linewidth=1, facecolor='none', edgecolor='w')
			ax.add_patch(patch)


	def show(self):
		plt.show()
	
	def mk_gds(self, location, show=True):
		'''
		make a rendering of the micromagnet design in a gds file
		location + filename = where to save.
		'''
		import gdspy

		micromagnet_gds = gdspy.Cell('MICROMAGNET')

		for magnet_pos in self.micromagnets:
			micromagnet_gds.add(gdspy.Rectangle(magnet_pos['x1_y1'], magnet_pos['x2_y2'], layer=0))

		electron_coor = self._get_electron_coordinates()
		for coor in electron_coor:
			micromagnet_gds.add(gdspy.Round(coor,20e-9, number_of_points=10, layer=2))

		if show == True:
			gdspy.LayoutViewer()

		gdspy.write_gds(location + '.gds', unit=1.0, precision=1.0e-10)

	def _get_canvas_size(self):
		'''
		Get size of the area where we are putting micromagets in
		Return
			canvas_size (2 tuples): two corners of the canvas to span
		'''
		min_y = 0
		max_y = 0
		min_z = 0
		max_z = 0

		for magnet in self.micromagnets:
			if magnet['x1_y1'][0] < min_y: 
				min_y = magnet['x1_y1'][0]
			if magnet['x2_y2'][0] < min_y: 
				min_y = magnet['x2_y2'][0]
			if magnet['x1_y1'][0] > max_y: 
				max_y = magnet['x1_y1'][0]
			if magnet['x2_y2'][0] > max_y: 
				max_y = magnet['x2_y2'][0]

			if magnet['x1_y1'][1] < min_z:
				min_z = magnet['x1_y1'][1]
			if magnet['x2_y2'][1] < min_z: 
				min_z = magnet['x2_y2'][1]
			if magnet['x1_y1'][1] > max_z: 
				max_z = magnet['x1_y1'][1]
			if magnet['x2_y2'][1] > max_z: 
				max_z = magnet['x2_y2'][1]

		# Lets add a margin of 200 nm
		min_y -= 200e-9
		min_z -= 200e-9
		max_y += 200e-9
		max_z += 200e-9

		return (min_y, min_z), (max_y, max_z)

	def _get_unit_conversion(self, unit):
		mult = 1
		if unit == 'mT':
			mult = 1e3
		elif unit == 'GHz':
			mult = 28.5714
		elif unit == 'MHz':
			mult = 28.5714*1e3

		return mult

	def _get_electron_coordinates(self):
		coordinates = []
		# get local field
		if self.electron_pos['axis'] == 'y':
			for dot_pos in self.electron_pos['pos']:
				coordinates.append((0,dot_pos))
		
		if self.electron_pos['axis'] == 'z':
			for dot_pos in self.electron_pos['pos']:
				coordinates.append((dot_pos,0))

		return coordinates


if __name__ == '__main__':
	s = micromagnet_simulator(100)
	s.add_micromagnet( (-400e-9, -500e-9), (100e-9,100e-9), 100e-9,200e-9)
	s.calculate()
	s.plot_fields()