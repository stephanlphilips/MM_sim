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