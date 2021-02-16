from micromagnet_simulator.magnet_creator import umag_creator

def example_MM_design(d_magnet_magnet, h_slant, w_slant, h_2deg=70, h_magnet=200):
	w_magnet = 5000
	h_magnet = 2000


	umag = umag_creator()
	umag.set_magnetisation(1,0,0)

	umag.add_electron_position(0, -200, -30)
	umag.add_electron_position(0, -120, -30)
	umag.add_electron_position(0,  -40, -30)
	umag.add_electron_position(0,   40, -30)
	umag.add_electron_position(0,  120, -30)
	umag.add_electron_position(0,  200, -30)


	# the big slabs
	umag.add_cube(-w_magnet/2-d_magnet_magnet/2-w_slant/2, 0, h_2deg+h_magnet/2,
		w_magnet,h_magnet,h_magnet)
	umag.add_cube( w_magnet/2+d_magnet_magnet/2+w_slant/2, 0, h_2deg+h_magnet/2,
		w_magnet,h_magnet,h_magnet)

	# the small pieces above the rectangle
	umag.add_cube(-d_magnet_magnet/2, h_magnet/4+h_slant/4, h_2deg+h_magnet/2,
		w_slant,h_magnet/2-h_slant/2,h_magnet)
	umag.add_cube( d_magnet_magnet/2, h_magnet/4+h_slant/4, h_2deg+h_magnet/2,
		w_slant,h_magnet/2-h_slant/2,h_magnet)

	# the rectangular pieces.
	p_2 = (-d_magnet_magnet/2-w_slant/2, -h_slant/2, h_2deg+h_magnet/2)
	p_1 = (-d_magnet_magnet/2-w_slant/2,  h_slant/2, h_2deg+h_magnet/2)
	p_3 = (-d_magnet_magnet/2+w_slant/2,  h_slant/2, h_2deg+h_magnet/2)
	umag.add_triangle(*p_1, *p_2, *p_3, 'z',200, n_magnets=10)

	p_2 = (d_magnet_magnet/2+w_slant/2, -h_slant/2, h_2deg+h_magnet/2)
	p_1 = (d_magnet_magnet/2+w_slant/2,  h_slant/2, h_2deg+h_magnet/2)
	p_3 = (d_magnet_magnet/2-w_slant/2,  h_slant/2, h_2deg+h_magnet/2)
	umag.add_triangle(*p_1, *p_2, *p_3, 'z',200, n_magnets=10)

	return umag


from micromagnet_simulator.loop_control.looping import linspace

w_slant =  linspace(20, 80,20, axis=0, name='w_slant', unit='nm')

# umag = example_MM_design(250, 200, w_slant)
# view = umag.generate_qubit_prop()

# view.unit = 'mT'
# f=view.plot_fields('xyz')
# f.savefig(f'/home/stephan/Desktop/1D_sweep_total_field.png')

# view.unit = 'mT'
# f=view.plot_derivative('x', movement_direction='xy')
# f.savefig(f'/home/stephan/Desktop/1D_sweep_dec_field.png')
# f=view.plot_derivative('yz', movement_direction='x')
# f.savefig(f'/home/stephan/Desktop/1D_sweep_driving_field.png')
# view.show()


w_slant =  linspace(20, 80,20, axis=0, name='w_slant', unit='nm')
h_slant =  linspace(100, 300,20, axis=1, name='h_slant', unit='nm')

umag = example_MM_design(250, h_slant, w_slant)
view = umag.generate_qubit_prop()

# view.unit = 'GHz'
# f=view.plot_fields('xyz')

# view.unit = 'mT'
# f=view.plot_derivative('x', movement_direction='xy')
# f=view.plot_derivative('yz', movement_direction='x')

# view.show()
