# import pywavefront as wf
import os
import numpy as np
from vector import Vec3
from SceneObjects import Triangle, Sphere, CheckeredSphere
from math import sin, cos, pi
import time
import transformations as transformations


def test_spheres(size, viewing_angle=30):
    spheres_list = []
    up_move, back_move = sin(viewing_angle / 180 * pi), cos(viewing_angle / 180 * pi)
    positions = [(1.25, up_move, back_move),
                 (-0.75, up_move, back_move),
                 (-1, -up_move, -back_move),
                 (1, -up_move, -back_move)]
    colors = [Vec3(0, 0, 255), Vec3(255, 255, 100), Vec3(200, 0, 0), Vec3(0, 200, 0)]
    scale = 1 / 5 * size
    for (i, j, k) in positions:
        spheres_list.append(Sphere(
            pos=Vec3(scale * i, scale * j, scale * k),
            radius=scale / 1.1,
            reflectiveness=0.4,
            shininess=8.0,
        ))
    for k in range(len(colors)):
        spheres_list[k].diffuse = colors[k]
        spheres_list[k].parent = f"Sphere {k}"

    # big_offset = 9999 * size
    # spheres_list.append(CheckeredSphere(
    #     pos=Vec3(0, -cos(viewing_angle / 180 * pi) * big_offset - scale, sin(viewing_angle / 180 * pi) * big_offset),
    #     radius=big_offset,
    #     color=Vec3(255, 255, 255),
    #     reflectiveness=0.1,
    #     shininess=32.0,
    #     parent="Big Sphere"
    # ))
    return spheres_list


def spheres_for_link(size, viewing_angle=30):
    spheres_list = []
    scale = size / 3
    up_move, back_move = sin(viewing_angle / 180 * pi), cos(viewing_angle / 180 * pi)
    for i in (1,):
        spheres_list.append(Sphere(
            pos=Vec3(size / 4 * i, 0 + up_move*scale*2+scale/2, 0 + back_move*scale*2),
            radius=scale,
            color=Vec3(200, 80, 80),
            reflectiveness=0.5,
            shininess=8.0
        ))
    return spheres_list


def checkered_sph_only(size, reflectiveness=0.5, viewing_angle=30):
    spheres_list = []
    scale =  size / 5
    big_offset = 9999 * size
    spheres_list.append(CheckeredSphere(
        pos=Vec3(0, -cos(viewing_angle / 180 * pi) * big_offset - scale, sin(viewing_angle / 180 * pi) * big_offset),
        radius=big_offset,
        color=Vec3(255, 255, 255),
        reflectiveness=reflectiveness,
        shininess=32.0,
        parent="Big Sphere"
    ))
    return spheres_list


def transform_objects(list_of_objects, transform_matrix=transformations.identity_matrix()):
    transformation_start_time = time.time()
    print("Beginning Transformation of Objects")
    for obj in list_of_objects:
        if isinstance(obj, Sphere):
            pass
        elif isinstance(obj, Triangle):
            if (transform_matrix - transformations.identity_matrix()).all():
                print("Warning: Transforming by Identity matrix only")
                return
            obj.A = Vec3(transform_matrix.dot(np.asarray([obj.A.x, obj.A.y, obj.A.z, 1]))[:3])
            obj.B = Vec3(transform_matrix.dot(np.asarray([obj.B.x, obj.B.y, obj.B.z, 1]))[:3])
            obj.C = Vec3(transform_matrix.dot(np.asarray([obj.C.x, obj.C.y, obj.C.z, 1]))[:3])
            obj.calc_normal()  # built in method
            obj.normal = -1 * obj.normal
    print(f"Transformation of objects took {time.time() - transformation_start_time}s ")


class ObjLoader:
    """Taken from https://github.com/totex/PyOpenGL_tutorials/blob/master/ObjLoader.py
        Accompanies YouTube video https://www.youtube.com/watch?v=VMsHs7ARv0U"""
    def __init__(self):
        self.vert_coords = []
        self.text_coords = []
        self.norm_coords = []

        self.vertex_index = []
        self.texture_index = []
        self.normal_index = []

        self.model = []

    def load_model(self, file):
        for line in open(file, 'r'):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue

            if values[0] == 'v':
                self.vert_coords.append(values[1:4])
            if values[0] == 'vt':
                self.text_coords.append(values[1:3])
            if values[0] == 'vn':
                self.norm_coords.append(values[1:4])

            if values[0] == 'f':
                face_i = []
                text_i = []
                norm_i = []
                for v in values[1:4]:
                    w = v.split('//')
                    face_i.append(int(w[0]) - 1)
                    norm_i.append(int(w[1]) - 1)
                    # Modified since I don't have texture coordinates
                self.vertex_index.append(face_i)
                self.texture_index.append(text_i)
                self.normal_index.append(norm_i)

        self.vertex_index = [y for x in self.vertex_index for y in x]
        self.texture_index = [y for x in self.texture_index for y in x]
        self.normal_index = [y for x in self.normal_index for y in x]

        for i in self.vertex_index:
            self.model.extend(self.vert_coords[i])

        for i in self.texture_index:
            self.model.extend(self.text_coords[i])

        for i in self.normal_index:
            self.model.extend(self.norm_coords[i])

        self.model = np.array(self.model, dtype='float32')


def load_toon_link():

    # obj file should now be in main directory
    # os.chdir(r'Toon_Link/ssbb-toon-link_obj/source')

    new_model = ObjLoader()
    model_name = 'DolToonlinkR1_fixed'
    new_model.load_model(f"{model_name}.obj")

    indices = new_model.vertex_index
    coords = new_model.vert_coords
    norm_inds = new_model.normal_index
    norm_coords = new_model.norm_coords

    model_triangles = []
    for i in range(len(new_model.vertex_index)//3):
        ptA, ptB, ptC = Vec3(coords[indices[i * 3]]), Vec3(coords[indices[i * 3 + 1]]), Vec3(coords[indices[i * 3 + 2]])
        norm = Vec3(norm_coords[norm_inds[i * 3]])
        new_tri = Triangle(ptA, ptB, ptC, input_normal=-1*norm, parent=f"{model_name}")
        model_triangles.append(new_tri)
        # print(new_model.vert_coords[i])
    print(f"Number of triangles in {model_name} file: {len(model_triangles)}")
    # os.chdir(r'../../../')
    return model_triangles
