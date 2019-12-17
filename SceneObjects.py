from vector import Vec3
from copy import deepcopy
from math import sqrt, trunc, pi


class Triangle:
    """Tuple of 3 points (Vec3's)"""
    # TODO Add bounding box stuff
    def __init__(self, pt_a, pt_b, pt_c, input_normal=None, input_color=Vec3(255, 255, 255),
                 reflectiveness=0, shininess=8.0, parent=None):
        self.A = pt_a
        self.B = pt_b
        self.C = pt_c
        self.reflectiveness = reflectiveness
        self.shininess = shininess
        self.parent = parent

        if input_normal is not None:
            self.normal = input_normal
        else:
            self.calc_normal()

        if input_color is not None:
            self.diffuse = input_color

    def get_color(self, point_hit=None):
        return self.diffuse

    def calc_normal(self):
        vec_ab = self.B - self.A
        vec_ac = self.C - self.A

        # Reversed from normal implementations due to reversed coordinate system
        cross_vec = vec_ab.cross(vec_ac)

        self.normal = cross_vec.normalize()
        # print(vec_ab, vec_ac, cross_vec, self.normal)

    def get_normal(self, pos=None):
        return self.normal

    def __str__(self):
        pts = f"Tri Pts = {self.A},{self.B},{self.C}\t"
        norm = f"Tri Normal = {self.normal}\t"
        info = f"Color = {self.diffuse}, Reflectiveness = {self.reflectiveness}"
        return pts + norm + info

    def __repr__(self):
        pts = f"Tri Pts = {self.A},{self.B},{self.C}\t"
        norm = f"Tri Normal = {self.normal}\t"
        info = f"Color = {self.diffuse}, Reflectiveness = {self.reflectiveness}"
        return pts + norm + info

    def intersect(self, ray_to_test):
        """Based on Ray-Triangle Intersection algorithm in Shirley and Marschner, pg 77-81"""
        direction = ray_to_test.direction

        # Pre-check for normal pointed towards ray's origin
        if self.normal.dot(direction) > 0:
            return False

        # Saving to variables to prevent coding too much
        a_ = self.A.x - self.B.x
        b_ = self.A.y - self.B.y
        c_ = self.A.z - self.B.z
        d_ = self.A.x - self.C.x
        e_ = self.A.y - self.C.y
        f_ = self.A.z - self.C.z
        g_, h_, i_ = ray_to_test.direction.x, ray_to_test.direction.y, ray_to_test.direction.z
        j_, k_, l_ = self.A.x - ray_to_test.origin.x, \
                     self.A.y - ray_to_test.origin.y, \
                     self.A.z - ray_to_test.origin.z

        # Saving More variables
        ei_min_hf = e_ * i_ - h_ * f_
        gf_min_di = g_ * f_ - d_ * i_
        dh_min_eg = d_ * h_ - e_ * g_
        ak_min_jb = a_ * k_ - j_ * b_
        jc_min_al = j_ * c_ - a_ * l_
        bl_min_kc = b_ * l_ - k_ * c_

        m_denominator = a_ * ei_min_hf + b_ * gf_min_di + c_ * dh_min_eg

        if m_denominator == 0.0:
            return False
        # First, compute t
        t_of_hit = -(f_ * ak_min_jb + e_ * jc_min_al + d_ * bl_min_kc) / m_denominator
        if t_of_hit < ray_to_test.initial_offset or t_of_hit > ray_to_test.nearest_hit_distance:
            return False

        # Next, try gamma
        gamma = (i_ * ak_min_jb + h_ * jc_min_al + g_ * bl_min_kc) / m_denominator
        if gamma < 0 or gamma > 1:
            return False

        # Then, try beta
        beta = (j_ * ei_min_hf + k_ * gf_min_di + l_ * dh_min_eg) / m_denominator
        if beta < 0 or beta > 1:
            return False

        # Finally, calculate alpha (1 - gamma - beta)
        alpha = 1 - gamma - beta
        if alpha < 0 or alpha > 1:
            return False

        ray_to_test.nearest_hit_distance = t_of_hit
        return True


class Sphere:
    def __init__(self, pos, radius, color=Vec3(255, 255, 255), reflectiveness=0, shininess=8.0, parent=None):
        self.pos = pos
        self.radius = radius
        self.diffuse = color
        self.reflectiveness = reflectiveness
        self.shininess = shininess
        self.parent = parent

    def get_color(self, point_hit):
        return self.diffuse

    def get_normal(self, pos):
        return (pos - self.pos)/self.radius

    def __repr__(self):
        return f"Sphere: Pos = {self.pos}\t info = Color = {self.diffuse}, Reflectiveness = {self.reflectiveness}"

    def intersect(self, ray_to_test):
        """Based on Ray-Sphere Intersection algorithm in Shirley and Marschner, pg 76-77"""
        # Put in terms like the book uses
        e = ray_to_test.origin  # Vec 3
        d = ray_to_test.direction  #  Vec3
        c = self.pos  # Vec3
        r = self.radius # Float
        e_min_c = e - c # Vec3

        discriminant = pow((d.dot(e_min_c)),2) - d.dot(d)*((e_min_c).dot(e_min_c) - pow(r, 2))
        if discriminant < 0:
            return False  # no real solution
        elif -0.0000001 < discriminant < 0.0000001:
            t_of_hit = -d.dot(e_min_c)/d.dot(d)
            if t_of_hit < ray_to_test.nearest_hit_distance:
                ray_to_test.nearest_hit_distance = t_of_hit
                return True
        else:
            rest_of_equ = -d.dot(e_min_c) / d.dot(d)
            sqrt_disc = sqrt(discriminant)
            smaller_t = rest_of_equ - sqrt_disc
            larger_t = rest_of_equ + sqrt_disc
            if ray_to_test.initial_offset < smaller_t < ray_to_test.nearest_hit_distance:
                ray_to_test.nearest_hit_distance = smaller_t
                return True
            elif ray_to_test.initial_offset < larger_t < ray_to_test.nearest_hit_distance:
                ray_to_test.nearest_hit_distance = larger_t
                return True
            else:
                return False


class CheckeredSphere(Sphere):
    def get_color(self, point_hit):
        """Based off of James Bowman's ray tracer at https://github.com/jamesbowman/raytrace/blob/master/rt3.py"""
        checker = trunc(point_hit.x /(self.radius / 9999) * 10) % 2 == trunc(point_hit.z / (self.radius / 9999) * 10) % 2
        return checker * self.diffuse + (1 - checker) * (Vec3(255, 255, 255) - self.diffuse)


class PointLight:
    """ Holds pos, color, and intensity of a "light" """
    def __init__(self, position, color, intensity):
        self.position = position
        self.color = color
        self.intensity = intensity


