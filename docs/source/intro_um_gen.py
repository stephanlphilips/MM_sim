from micromagnet_simulator.magnet_creator import umag_creator

# umag = umag_creator()


# # set magnetization in the x,y,z direction with a field strength of 1,0,0 Tesla.
# umag.set_magnetisation(1,0,0)
# # set external field, 150mT along the x-direction
# umag.set_external_field(0.150,0,0)


# # specification of the locations : (x,y,z) axis, (0nm,-200nm, -30nm) 
# umag.add_electron_position(0, -200, -30)
# umag.add_electron_position(0, -120, -30)
# umag.add_electron_position(0,  -40, -30)
# umag.add_electron_position(0,   40, -30)
# umag.add_electron_position(0,  120, -30)
# umag.add_electron_position(0,  200, -30)


# # syntax : center_x, center_y, center_z, span_x, span_y, span_z
# umag.add_cube(-500, 0, 200, 400,500,200)
# umag.add_cube( 500, 0, 200, 400,500,200)


# view = umag.generate_view(True)
# view.show()

umag = umag_creator()

umag.add_cube(-500, 0, 200, 400,500,200)

# in this case we specify the coordinates of a triangle in the xz plane
p_2 = (-250, 0, 100)
p_1 = (-300, 0, 100)
p_3 = (-300, 0, 300)
# now we can extend in the y plane around these coordinate (so in this case, -250nm, 250nm on the y axis)
umag.add_triangle(*p_1, *p_2, *p_3, 'y',500, n_magnets=20)
view = umag.generate_view(True)
view.show()