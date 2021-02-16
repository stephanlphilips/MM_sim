from micromagnet_simulator.magnet_creator import umag_creator

def generate_slanted_xy_MM(magnet_to_magnet_distance, l_skew, w_skew, h_2deg=70, h_magnet=200):
	umag = umag_creator()

	length_magnet = 5000
	width_magnet = 2000

	# the big slabs
	umag.add_cube(-length_magnet/2-magnet_to_magnet_distance/2-w_skew/2, 0, h_2deg+h_magnet/2,
		length_magnet,width_magnet,h_magnet)
	umag.add_cube( length_magnet/2+magnet_to_magnet_distance/2+w_skew/2, 0, h_2deg+h_magnet/2,
		length_magnet,width_magnet,h_magnet)

	umag.add_cube(-magnet_to_magnet_distance/2, width_magnet/4+l_skew/4, h_2deg+h_magnet/2,
		w_skew,width_magnet/2-l_skew/2,h_magnet)
	umag.add_cube( magnet_to_magnet_distance/2, width_magnet/4+l_skew/4, h_2deg+h_magnet/2,
		w_skew,width_magnet/2-l_skew/2,h_magnet)

	p_2 = (-magnet_to_magnet_distance/2-w_skew/2, -l_skew/2, h_2deg+h_magnet/2)
	p_1 = (-magnet_to_magnet_distance/2-w_skew/2,  l_skew/2, h_2deg+h_magnet/2)
	p_3 = (-magnet_to_magnet_distance/2+w_skew/2,  l_skew/2, h_2deg+h_magnet/2)
	umag.add_triangle(*p_1, *p_2, *p_3, 'z',200, n_magnets=10)

	p_2 = (magnet_to_magnet_distance/2+w_skew/2, -l_skew/2, h_2deg+h_magnet/2)
	p_1 = (magnet_to_magnet_distance/2+w_skew/2,  l_skew/2, h_2deg+h_magnet/2)
	p_3 = (magnet_to_magnet_distance/2-w_skew/2,  l_skew/2, h_2deg+h_magnet/2)
	umag.add_triangle(*p_1, *p_2, *p_3, 'z',200, n_magnets=10)

	view = umag.generate_view(False)

	return view

view = generate_slanted_xy_MM(200, 500, 80)

# a 1D slice of the field at the locations of the qubits
# view.set_slice('y', -500, 500, 100, 0, -30) # plot y-axis, -500nm to 500nm (100pt), x=0, z=-30


# view.unit = 'GHz'
# fig_abs_field = view.plot_fields('xyz') #specified which field direction, for Bx, specify 'x'

# view.unit = 'mT'
# fig_driving_gradient = view.plot_derivative(field_direction='yz', movement_direction='x' )
# fig_dec_gradient     = view.plot_derivative(field_direction='x' , movement_direction='xy')

# view.show()

view.set_image('xz', -200,200,100,-50,0,100, 0)

view.unit = 'T'
fig_abs_field = view.plot_fields('xyz') #specified which field direction, for Bx, specify 'x'
fig_vec       = view.plot_fields('xz', plot_type='vect') #make a vector plot

view.unit = 'mT'
fig_driving_gradient = view.plot_derivative(field_direction='yz', movement_direction='x' )
fig_dec_gradient     = view.plot_derivative(field_direction='x' , movement_direction='xy')

view.show()