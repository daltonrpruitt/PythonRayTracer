from SceneObjects import *


class BoundingBox:
    """Holds a min and max position vector of an Axis-Aligned Bounding Box (AABB)"""

    def __init__(self, objects_list, axis=0):
        """Recursively defines contained bounding volumes"""
        self.left_box = None
        self.right_box = None
        self.object_contained = None
        self.min_point = None
        self.max_point = None
        self.object_count = 0
        if len(objects_list) == 1:
            if type(objects_list[0]) == Triangle:
                tri = objects_list[0]
                self.min_point = Vec3(min(tri.A.x, tri.B.x, tri.C.x) - 0.1,
                                      min(tri.A.y, tri.B.y, tri.C.y) - 0.1,
                                      min(tri.A.z, tri.B.z, tri.C.z) - 0.1)
                self.max_point = Vec3(max(tri.A.x, tri.B.x, tri.C.x) + 0.1,
                                      max(tri.A.y, tri.B.y, tri.C.y) + 0.1,
                                      max(tri.A.z, tri.B.z, tri.C.z) + 0.1)
                self.object_contained = tri
                # print(f"Bounding box for {self.object_contained}")
                self.object_count = 1
            else:
                print("Warning: BoundingBox not usable with non-Triangles yet")
        elif len(objects_list) > 1:
            """Based on Shirley and Marschner Hierarchical Bounding Volumes"""
            if axis == 0:
                new_list = sorted(objects_list, key=lambda t: (t.A.x + t.B.x + t.C.x) / 3, reverse=False)
            elif axis == 1:
                new_list = sorted(objects_list, key=lambda t: (t.A.y + t.B.y + t.C.y) / 3, reverse=False)
            elif axis == 2:
                new_list = sorted(objects_list, key=lambda t: (t.A.z + t.B.z + t.C.z) / 3, reverse=False)
            else:
                print(f"Error in Bounding box for {objects_list}")
                new_list = objects_list

            first = new_list[0].A
            xmin, xmax, ymin, ymax, zmin, zmax = first.x, first.x, first.y, first.y, first.z, first.z
            for tri in new_list:
                for pt in (tri.A, tri.B, tri.C):
                    if pt.x < xmin: xmin = pt.x
                    if pt.x > xmax: xmax = pt.x
                    if pt.y < ymin: ymin = pt.y
                    if pt.y > ymax: ymax = pt.y
                    if pt.z < zmin: zmin = pt.z
                    if pt.x > xmax: zmax = pt.z

            self.min_point = Vec3(xmin - 0.1, ymin - 0.1, zmin - 0.1)
            self.max_point = Vec3(xmax + 0.1, ymax + 0.1, zmax + 0.1)

            mid_point = len(new_list)//2
            self.left_box = BoundingBox(new_list[:mid_point], axis=(axis + 1) % 3)
            self.right_box = BoundingBox(new_list[mid_point:], axis=(axis + 1) % 3)
            self.object_count = self.left_box.object_count + self.right_box.object_count
        else:
            print(f"Warning: BoundingBox not programmed to deal with {len(objects_list)} items. ")

    def intersect(self, ray_to_test):
        """Based on https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-box-intersection
        Returns either False or the object_hit (Triangle)"""
        r_dir = ray_to_test.direction
        r_ori = ray_to_test.origin

        if r_dir.x == 0:
            print(f"Warning: Ray {ray_to_test} has no x component in direction.")
            return False

        t_x_min = ((self.max_point.x if r_dir.x < 0 else self.min_point.x) - r_ori.x) / r_dir.x
        t_x_max = ((self.min_point.x if r_dir.x < 0 else self.max_point.x) - r_ori.x) / r_dir.x
        if t_x_min > t_x_max:
            t_x_min, t_x_max = t_x_max, t_x_min

        t_min, t_max = t_x_min, t_x_max

        t_y_min = ((self.max_point.y if r_dir.y < 0 else self.min_point.y) - r_ori.y) / r_dir.y
        t_y_max = ((self.min_point.y if r_dir.y < 0 else self.max_point.y) - r_ori.y) / r_dir.y
        if t_y_min > t_y_max:
            t_y_min, t_y_max = t_y_max, t_y_min

        if t_min > t_y_max or t_max < t_y_min:
            return False

        if t_y_min > t_min:
            t_min = t_y_min
        if t_y_max < t_max:
            t_max = t_y_max

        t_z_min = ((self.max_point.z if r_dir.z < 0 else self.min_point.z) - r_ori.z) / r_dir.z
        t_z_max = ((self.min_point.z if r_dir.z < 0 else self.max_point.z) - r_ori.z) / r_dir.z
        if t_z_min > t_z_max:
            t_z_min, t_z_max = t_z_max, t_z_min

        if t_min > t_z_max or t_max < t_z_min:
            return False

        # Don't do anything with the updated t's, so why keep this?
        # if t_z_min > t_min:
        #     t_min = t_z_min
        # if t_z_max < t_max:
        #     t_max = t_z_max

        # Return some form of True statement now
        if self.object_contained is not None:
            if self.object_contained.intersect(ray_to_test):
                return self.object_contained
            else:
                return False
        else:
            obj_hit, left_hit, right_hit = None, None, None
            # Ray's nearest hit distance will update, so can check in succession
            if self.left_box is not None:
                left_hit = self.left_box.intersect(ray_to_test)
            if self.right_box is not None:
                right_hit = self.right_box.intersect(ray_to_test)
            if left_hit:
                obj_hit = left_hit
            if right_hit:
                obj_hit = right_hit
            if obj_hit is not None:
                return obj_hit
            else:
                return False


    def __repr__(self):
        return f"BoundingBox obj: Vmin={self.min_point}, Vmax={self.max_point}"

    def get_depth(self):
        level = max(DFS_count(self.left_box), DFS_count(self.right_box))
        print(f"{self} is {level} levels deep")


def DFS_count(box):
    left, right = 0, 0
    if box is None:
        return 0
    if box.object_contained is not None:
        # Base Case
        return 1
    if box.left_box is not None:
        left = DFS_count(box.left_box) + 1
    if box.right_box is not None:
        right = DFS_count(box.right_box) + 1
    curr_level = max(left, right)
    return curr_level

