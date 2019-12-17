import numpy as np
from SceneObjects import Triangle
from vector import Vec3
'''
For loading cube geometry/color
Unscaled, all in unit length from -1,-1,-1 to +1,+1,+1
'''


def cube_load(reflectiveness=0.0):
    """ Returns an array of Triangles representing a simple cube.
        Based off cube_regl.js example.
        Z values reversed because my orientation is +'ve in z away from camera. """
    # Interleaved position/color data
    cube_vertex_data = np.array([
    -1, -1, -1,     1, 0, 0,
    +1, -1, -1,     1, 0, 0,
    +1, +1, -1,     1, 0, 0,
    -1, +1, -1,     1, 0, 0,

    -1, -1, +1,     0, 1, 0,
    -1, +1, +1,     0, 1, 0,
    +1, +1, +1,     0, 1, 0,
    +1, -1, +1,     0, 1, 0,

    -1, +1, +1,     0, 0, 1,
    -1, +1, -1,     0, 0, 1,
    +1, +1, -1,     0, 0, 1,
    +1, +1, +1,     0, 0, 1,

    -1, -1, +1,     1, 0, 1,
    +1, -1, +1,     1, 0, 1,
    +1, -1, -1,     1, 0, 1,
    -1, -1, -1,     1, 0, 1,

    +1, -1, +1,     0, 1, 1,
    +1, +1, +1,     0, 1, 1,
    +1, +1, -1,     0, 1, 1,
    +1, -1, -1,     0, 1, 1,

    -1, -1, +1,     1, 1, 0,
    -1, -1, -1,     1, 1, 0,
    -1, +1, -1,     1, 1, 0,
    -1, +1, +1,     1, 1, 0], dtype=np.int8)
    cube_vertex_data.shape = (24, 2, 3)

    cube_vertex_indices = np.array([
        [[0, 1, 2], [0, 2, 3]],        # Front
        [[4, 5, 6], [4, 6, 7]],        # Bottom
        [[8, 9, 10], [8, 10, 11]],     # Top
        [[12, 13, 14], [12, 14, 15]],  # Bottom
        [[16, 17, 18], [16, 18, 19]],  # Right
        [[20, 21, 22], [20, 22, 23]]   # Left
        ], dtype=np.int8)
    # cube_vertex_indices.shape = (6, 4, 2, 3)

    # Construct Triangle list
    cube_tris_list = []
    for face_index in range(6):
        vd = cube_vertex_data
        for tri_index in range(2):
            vi = cube_vertex_indices[face_index, tri_index]
            ptA, ptB, ptC, color = Vec3(vd[vi][0][0]), Vec3(vd[vi][1][0]), Vec3(vd[vi][2][0]), Vec3(vd[vi][0][1]) * 255
            
            cube_tris_list.append(Triangle(ptA, ptB, ptC,
                                           input_color=color,
                                           parent="Cube1",
                                           reflectiveness=reflectiveness))

    # cube_tris_array = np.array(cube_tris_list, dtype=Triangle)
    return cube_tris_list
