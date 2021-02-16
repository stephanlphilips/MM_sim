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

	view = umag.generate_view(True)
	view.show()

generate_slanted_xy_MM(200, 500, 80)