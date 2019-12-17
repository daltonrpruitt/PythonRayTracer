import numpy as np
from PIL import Image
from ray import *
import datetime
from SceneObjects import  PointLight
from geometry_loading import *
from cube import cube_load
from math import trunc, pi, ceil
from BHV_BBox import BoundingBox
from copy import deepcopy

"""Note: The coordinate system used dictates that clockwise triangles be used, not counterclockwise"""
if __name__ == "__main__":
    # Appearance
    size = 512
    depth = 5
    is_silhouetted = True
    is_cel_shaded = True

    # Objects
    is_link = True
    uses_BBox = True
    model_reflectiveness = 0.0
    is_cube = True
    is_spheres_for_link = True
    is_spheres = True
    is_test_tris = False

    # To save, or not to save?
    is_saved = True

    start_time = time.time()

    height, width = size, size
    background_color = Vec3(30, 30, 30)
    eye_distance = height * 1.5
    viewing_angle = 30
    image_data = np.zeros(shape=(height, width, 3), dtype=np.uint8)
    eye_location = Vec3(0, 0, -eye_distance)

    # Test Triangle
    tri_dist = width * 2

    objects_list = checkered_sph_only(size, viewing_angle=viewing_angle, reflectiveness=0.4)
    if is_link:
        tris_list = load_toon_link()  # from imported file

        trans_mat = transformations.compose_matrix(angles=(15*pi/180, 180*pi/180, 0))
        transform_objects(tris_list, transform_matrix=trans_mat)  # transformations.identity_matrix())

        # tris_list = np.asarray(tris_list, dtype=Triangle)
        # For multiple links
        second_link = deepcopy(tris_list)

        # Scale up and move ( and cull back-facing triangles)
        tri_offset = Vec3(0 * size/4, 1.2 * -size / 3,  0 * -size / 5)

        for tri in tris_list:
            tri.A = (tri.A * size / 35) + tri_offset
            tri.B = (tri.B * size / 35) + tri_offset
            tri.C = (tri.C * size / 35) + tri_offset
            tri.normal = -1 * tri.normal
            # tri.calc_normal()
            tri.diffuse = Vec3(67, 158, 78)*1.2 # make brighter
            tri.reflectiveness = model_reflectiveness
            tri.shininess = 8.0

        tri_offset = Vec3(1.5 * size / 4, -size / 10, size / 4)

        for tri in second_link:
            tri.A = (tri.A * size / 50) + tri_offset
            tri.B = (tri.B * size / 50) + tri_offset
            tri.C = (tri.C * size / 50) + tri_offset
            tri.normal = -1 * tri.normal
            # tri.calc_normal()
            tri.diffuse = Vec3(67, 79, 140)*1.4 # make brighter
            tri.reflectiveness = model_reflectiveness
            tri.shininess = 8.0

        print("Number of Tris = ", len(tris_list))
        if uses_BBox:
            bounding_start_time = time.time()
            BBox = BoundingBox(tris_list + second_link)
            print(f"Time to put tris in bounding box = {time.time()- bounding_start_time}")
            print("Link: ", end="")
            BBox.get_depth()
            print(f"Objects inside Link Box: {BBox.object_count}")
            objects_list += [BBox]
        else:
            objects_list += tris_list + second_link
    if is_cube:
        cube = cube_load(reflectiveness=0.5)
        # scale_mat = transformations.scale_matrix(size/5)
        rot_mat1 = transformations.compose_matrix(angles=(0, 0, -90 * pi / 180))
        rot_mat2 = transformations.compose_matrix(angles=(0, 65 * pi / 180, 0))
        # print(rot_mat)
        scale = size / 4
        transform_mat = transformations.compose_matrix(scale=(scale, scale, scale),
                                                       angles=(-viewing_angle * pi / 180, 0, 0),
                                                       translate=(-size/3, size / 3, size/2)).dot(rot_mat2.dot(rot_mat1))
        # print(transform_mat)
        transform_objects(cube, transform_matrix=transform_mat)
        # for tri in cube:
        #     print(tri)

        bounding_start_time = time.time()
        BBox = BoundingBox(cube)
        print(f"Time to put tris in bounding box = {time.time() - bounding_start_time}")
        print("Cube: ", end="")
        BBox.get_depth()
        objects_list += [BBox]
        # objects_list += cube  # after transformation
    if is_spheres_for_link:
        sphrs = spheres_for_link(size, viewing_angle=viewing_angle)
        objects_list += sphrs
    if is_spheres:
        # Testing Spheres
        objects_list += test_spheres(size, viewing_angle=viewing_angle)

    if is_test_tris:
        test_z = size / 2
        test_offset = 0#size/10
        forwardsTri  = Triangle(Vec3(-size/2+test_offset, size/2, test_z),
                                Vec3(size / 2 + test_offset, size / 2, test_z),
                                Vec3(0 + test_offset, -size / 2, test_z),
                                input_color=Vec3(30,30,180),
                                reflectiveness=0.7)

        backwardsTri = Triangle(Vec3(-size / 2 + test_offset*1.5, size / 2, -size/4),
                                Vec3(0 + test_offset * 1.5, -size / 2, - size / 4),
                                Vec3(size / 2 + test_offset*1.5, size / 2, - size / 4),
                                input_color=Vec3(150, 90, 30),
                                reflectiveness=0.7)
        print(forwardsTri)
        print(backwardsTri)
        objects_list += [BoundingBox([forwardsTri, backwardsTri])]

    lights_list = [PointLight(position=Vec3(size, size, -size * 1.5),
                              color=Vec3(255, 255, 255), intensity=1.0)]

    print(f"All object initialization took {time.time() - start_time} seconds")
    start_time = time.time()

    for i in range(height):
        for j in range(width):
            sample_point = Vec3(-width / 2 + j + 0.5, height / 2 - i + 0.5, 0)
            curr_ray = Ray(eye_location, Vec3(-width / 2 + j + 0.5, height / 2 - i + 0.5, 0) - eye_location)
            color = ray_trace(objects_list, num_bounces=0, max_bounces=depth,
                              background_color=background_color, list_of_lights=lights_list,
                              multiple=is_silhouetted, ray_given=curr_ray, cel_shaded=is_cel_shaded)

            image_data[i, j] = [color.x, color.y, color.z]
            if i == 31:
                if j == 31:
                    print(end="")
        # Show progress in console
        if i % 10 == 0:
            print("Finished with row", i, "after ", round(time.time() - start_time, 3), "seconds.")
    print("Finished with entire image after ", round(time.time() - start_time, 3), "seconds.")

    end_time = time.time()

    image = Image.fromarray(image_data, "RGB")
    print(end_time)
    time_taken = end_time - start_time
    print(f"Total Time: {time_taken}")
    image.show()

    if is_saved:
        img_name = "Final picture Funnnn"  # input("What do you want to save this image as? ")
        image.save(f"{img_name} - Bkgrnd = "
                   f"{size}x{size} - depth {depth} - " +
                   f"{datetime.datetime.now().strftime('%d-%m-%y__%H-%M-%S')} - {trunc(time_taken)}s.png")
                    # f"{trunc(background_color.x)}-{trunc(background_color.x)}-{trunc(background_color.x)} - "

