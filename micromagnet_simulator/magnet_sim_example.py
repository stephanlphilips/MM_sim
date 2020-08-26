import sys

from micromagnet_simulator.magnet_sim_class import micromagnet_simulator
from shapely.geometry import Polygon

import matplotlib.pyplot as plt
import os
import inspect

import numpy as np
import math

def mk_triangle(point_1, point_2,point_3, n_magnets):
	# define in which area the triangle is located
	y_pos = [point_1[1], point_2[1], point_3[1]]
	y_min = np.min(y_pos)
	y_max = np.max(y_pos)

	z_pos = [point_1[0], point_2[0], point_3[0]]
	z_min = np.min(z_pos)
	z_max = np.max(z_pos)

	n_pt_z = 500
	y_points = np.linspace(y_min, y_max, n_magnets + 1)
	z_points = np.linspace(z_min, z_max, n_pt_z+1)
	z_points_inv = z_points[::-1]

	# constuct slabs for the triangle (contains rectangles that approximate the triangle)
	micromagnet_slabs = []

	triangle = Polygon([point_1, point_2, point_3])
	for n in range(n_magnets):
		z_0 = 0
		z_1 = 0

		y_0 = y_points[n]
		y_1 = y_points[n+1]

		for z in range(n_pt_z):
			pol1 = Polygon([[z_points[z], y_0], [z_points[z],  y_1], [z_points[z+1], y_1], [z_points[z+1], y_0]])
			overlap = triangle.intersection(pol1)

			if overlap.area > pol1.area/2:	
				z_0 = z_points[z]
				break

		
		for z in range(n_pt_z):
			pol1 = Polygon([[z_points_inv[z], y_0], [z_points_inv[z], y_1], [z_points_inv[z+1], y_1] ,[z_points_inv[z+1], y_0]])
			overlap = triangle.intersection(pol1)

			if overlap.area > pol1.area/2:
				z_1 = z_points_inv[z]
				break

		micromagnet_slabs.append(((z_0,y_0),(z_1, y_1)))


	return micromagnet_slabs

def add_triangle(sim,points, h_magnet, h_2deg, n_slabs):
	point_1, point_2, point_3 = points

	magnets = mk_triangle(point_1, point_2, point_3, n_slabs)
	for i in magnets:
		sim.add_micromagnet( i[0], i[1], h_magnet, h_2deg)

def micromagnet_design(h, w, d, alpha, d_magnet_magnet, y_offset, z_offset, h_magnet = 150e-9, h_2deg = 120e-9, h_2deg2 = 120e-9):

	h_triangle = math.tan(math.radians(alpha))*d
	sign = np.sign(alpha)
	w = w/2
	d=d/2

	m = micromagnet_simulator(200)

	# start with top magnet
	m.add_micromagnet( (-h + z_offset,-w + y_offset), (-d_magnet_magnet/2 + z_offset - h_triangle/2*sign,w + y_offset), h_magnet, h_2deg)
	m.add_micromagnet( (-d_magnet_magnet/2 + z_offset - h_triangle/2,-w*sign + y_offset), (-d_magnet_magnet/2 + z_offset + h_triangle/2,-d*sign + y_offset), h_magnet, h_2deg)

	points = [(-d_magnet_magnet/2 + z_offset + h_triangle/2,-d*sign + y_offset),
				(-d_magnet_magnet/2 + z_offset- h_triangle/2,-d*sign + y_offset),
				(-d_magnet_magnet/2 + z_offset- sign*h_triangle/2,d*sign + y_offset)]
	add_triangle(m, points, h_magnet,h_2deg, 10)

	# bottom magnet
	m.add_micromagnet( (h + z_offset,-w + y_offset), (d_magnet_magnet/2 + z_offset + h_triangle/2*sign,w + y_offset), h_magnet, h_2deg)
	m.add_micromagnet( (d_magnet_magnet/2 + z_offset + h_triangle/2, -w*sign + y_offset), (d_magnet_magnet/2 + z_offset - h_triangle/2,-d*sign + y_offset), h_magnet, h_2deg)

	points = [(d_magnet_magnet/2 + z_offset - h_triangle/2, -d*sign + y_offset),
				(d_magnet_magnet/2 + z_offset + h_triangle/2,-d*sign + y_offset),
				(d_magnet_magnet/2 + z_offset + sign*h_triangle/2, d*sign + y_offset)]
	add_triangle(m, points, h_magnet,h_2deg, 10)

	# m.plot_micromagnets()
	m.set_electron_pos([-250e-9,-150e-9,-50e-9,50e-9,150e-9,250e-9], axis='y')
	m.set_external_field(0.2)
	m.set_magnetisation(1.0)
	m.calculate([(-400e-9,-800e-9),(400e-9,800e-9)])
    
	m.plot_field_abs(unit='GHz')
	m.plot_field_abs('dots', unit='GHz')
	m.plot_diff('dots', 'z', 'zy')
	m.plot_diff('all', 'xy', 'z')
	m.plot_fields()
	m.show()
	# m.mk_gds('wisconsin_micromagnet_design_6dot_100nm', True)
	print(m.generate_dot_report(verbose=False))
	return m.generate_dot_report(verbose=True)

h = 3000e-9
w = 2000e-9
d = 250e-9

alpha = 15.
d_magnet_magnet = 280e-9
y_offset = 350e-9
z_offset = 0e-9
h_magnet = 200e-9
h_2deg = 140e-9
h_2deg2 =  140e-9

micromagnet_design(h, w, d, alpha, d_magnet_magnet, y_offset, z_offset, h_magnet, h_2deg, h_2deg2)
