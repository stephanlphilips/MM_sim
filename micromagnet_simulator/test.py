from micromagnet_simulator.magnet_sim_class_v2 import umag_creator
import math
import numpy as np

def micromagnet_design(length, width, lenght_skew, width_skew, d_magnet_magnet, h_magnet = 150, h_to_MM = 120, h_2deg2 = 120):

	m = umag_creator()
	m.set_magnetisation(1, 0, 0)

	m.add_electron_position(0, -200, -30)
	m.add_electron_position(0, -120, -30)
	m.add_electron_position(0,  -40, -30)
	m.add_electron_position(0,   40, -30)
	m.add_electron_position(0,  120, -30)
	m.add_electron_position(0,  200, -30)

	m.add_cube(-length/2-d_magnet_magnet/2, 0, h_to_MM+h_magnet/2, length, width, h_magnet)
	m.add_cube( length/2+d_magnet_magnet/2, 0, h_to_MM+h_magnet/2, length, width, h_magnet)

	m.add_cube(-d_magnet_magnet/2+width_skew/2, width/4 + lenght_skew/4, h_to_MM+h_magnet/2, width_skew, width/2 - lenght_skew/2, h_magnet)
	m.add_cube( d_magnet_magnet/2-width_skew/2, width/4 + lenght_skew/4, h_to_MM+h_magnet/2, width_skew, width/2 - lenght_skew/2, h_magnet)

	p_1 = (-d_magnet_magnet/2 			  ,-lenght_skew/2, h_to_MM + h_magnet/2)
	p_2 = (-d_magnet_magnet/2 			  , lenght_skew/2, h_to_MM + h_magnet/2)
	p_3 = (-d_magnet_magnet/2 + width_skew, lenght_skew/2, h_to_MM + h_magnet/2)
	m.add_triangle(p_1, p_2, p_3, 'z',h_magnet,5)

	p_1 = ( d_magnet_magnet/2 - width_skew, lenght_skew/2, h_to_MM + h_magnet/2)
	p_2 = ( d_magnet_magnet/2 			  ,-lenght_skew/2, h_to_MM + h_magnet/2)
	p_3 = ( d_magnet_magnet/2 			  , lenght_skew/2, h_to_MM + h_magnet/2)
	m.add_triangle(p_1, p_2, p_3, 'z',h_magnet,5)
	return m


m = micromagnet_design(3e3, 1500, lenght_skew=275, width_skew=50, d_magnet_magnet=225)

v = m.generate_view()
v.set_image('yz', -500,500,100,-50,0,100, 0)

# v.set_image('xy', -200,200,100,-800,800,100, 0)

# v.set_slice('z', -80, 50, 100,0, 40 )
v.set_unit('GHz')
v.plot_fields('xyz', plot_type='norm')
# v.plot_fields('yz', plot_type='vect')
# v.plot_derivative('x', movement_direction='x')
# v.set_unit('mT')
v.plot_derivative('x', movement_direction='xy')
v.plot_derivative('yz', movement_direction='x')
v.plot_derivative('y', movement_direction='xy')

v.show()
