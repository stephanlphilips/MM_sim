from micromagnet_simulator.magnet_creator import umag_creator

umag = umag_creator()


# set magnetization in the x,y,z direction with a field strength of 1,0,0 Tesla.
umag.set_magnetisation(1,0,0)
# set external field, 150mT along the x-direction
umag.set_external_field(0.150,0,0)


# specification of the locations : (x,y,z) axis, (0nm,-200nm, -30nm) 
umag.add_electron_position(0, -200, -30)
umag.add_electron_position(0, -120, -30)
umag.add_electron_position(0,  -40, -30)
umag.add_electron_position(0,   40, -30)
umag.add_electron_position(0,  120, -30)
umag.add_electron_position(0,  200, -30)


# syntax : center_x, center_y, center_z, span_x, span_y, span_z
umag.add_cube(-500, 0, 200, 400,500,200)
umag.add_cube( 500, 0, 200, 400,500,200)


view = umag.generate_view(True)
view.show()

