from micromagnet_simulator.magnet_creator import umag_creator

umag = umag_creator()
umag.set_magnetisation(1,0,0)

umag.add_cube(-2000, 0, 200, 3800,1000,200)
umag.add_cube( 2000, 0, 200, 3800,1000,200)

view = umag.generate_view()

# a 1D slice of the field at the locations of the qubits
view.set_slice('y', -500, 500, 100, 0, -30) # plot y-axis, -500nm to 500nm (100pt), x=0, z=-30


view.unit = 'GHz'
fig_abs_field = view.plot_fields('xyz') #specified which field direction, for Bx, specify 'x'

view.unit = 'mT'
fig_driving_gradient = view.plot_derivative(field_direction='yz', movement_direction='x' )
fig_dec_gradient     = view.plot_derivative(field_direction='x' , movement_direction='xy')

view.show()

view.set_image('xz', -200,200,100,-50,0,100, 0)

view.unit = 'T'
fig_abs_field = view.plot_fields('xyz') #specified which field direction, for Bx, specify 'x'
fig_vec       = view.plot_fields('xz', plot_type='vect') #make a vector plot

view.unit = 'mT'
fig_driving_gradient = view.plot_derivative(field_direction='yz', movement_direction='x' )
fig_dec_gradient     = view.plot_derivative(field_direction='x' , movement_direction='xy')

view.show()