from SceneObjects import Triangle, Sphere, CheckeredSphere, PointLight
from BHV_BBox import BoundingBox
from vector import Vec3
from random import uniform

class Ray:
    def __init__(self, ray_origin, ray_direction, nearest_hit_distance=1e20):
        """Ray( Origin (vec3), Direction (vec3) )"""
        self.origin = ray_origin
        self.direction = ray_direction.normalize()
        self.nearest_hit_distance = nearest_hit_distance  # really far away by default
        self.initial_offset = 0.0001  # small distance started to prevent hitting same thing after bouncing

    def __str__(self):
        o = f"Origin = {self.origin}\t"
        d = f"Direction = {self.direction}"
        return o + d

    def __repr__(self):
        o = f"Origin = {self.origin}\t"
        d = f"Direction = {self.direction}"
        return o + d

    def reflect(self, point, normal):
        """Reflect( PointInSpace (vec3), VectorToReflectAround (vec3) )"""
        dir_dot_n = self.direction.dot(normal)

        # Check if is actually reflecting the correct way
        if dir_dot_n > 0:
            return False
        # From book
        new_direction = self.direction + normal * (2 * -dir_dot_n)
        return Ray(point, new_direction)


class ShadowRay(Ray):
    """Used for rays from points to lights; Ignores the Ray super class"""
    def __init__(self, start_pos, light):
        shadow_dir = light.position - start_pos
        super(ShadowRay, self).__init__(ray_origin=start_pos, ray_direction=shadow_dir, nearest_hit_distance=abs(shadow_dir))


def ray_trace(objects_list, num_bounces, max_bounces=1, ray_origin=None, ray_look_at_point=None,
              background_color=Vec3(0, 0, 0), list_of_lights=None,
              multiple=False, ray_given=None, cel_shaded=False):
    """Recursively casting rays for reflections
        (casted ray, list of objects, current number of bounces, max bounces)"""


    # Really don't need bounces after first few
    if multiple and num_bounces > 3:
        multiple = False

    if ray_given is None:
        assert ray_origin is not None and ray_look_at_point is not None

    color_rays_list = []
    silhouette_rays_list, silhouette_objects_hit_list = [], []
    silh_thickness = 4

    if multiple:
        ray_offsets = [(0.25, 0.25), (-0.25, 0.25), (0.25, -0.25), (-0.25, -0.25)]
        jitter = 0.2
        for (x_off, y_off) in ray_offsets:

            # Don't jitter silhouette rays, gives dotty appearance
            sil_offset_vec = Vec3(x_off, y_off, 0)

            # Jitter direction of ray already given
            color_offset_vector = sil_offset_vec + Vec3(uniform(-jitter, jitter), uniform(-jitter, jitter), 0)

            if ray_given is not None:
                # New rays based off given ray ( offset vector scaled down because already normalized)
                new_color_ray = Ray(ray_given.origin, ray_given.direction + color_offset_vector / 500)

                # extend range of silhouette ray
                new_silhouette_ray = Ray(ray_given.origin, ray_given.direction + sil_offset_vec / 500 * silh_thickness)

            else:
                # Extra rays based off given origin and look at point (offset not scaled down)
                new_color_ray = Ray(ray_origin, ray_look_at_point + color_offset_vector - ray_origin)
                new_silhouette_ray = Ray(ray_origin, ray_look_at_point + sil_offset_vec * silh_thickness - ray_origin)

            color_rays_list.append(new_color_ray)
            silhouette_rays_list.append(new_silhouette_ray)

    elif not multiple:
        # Will not have silhouette rays since only firing one anyway
        if ray_given is not None:
            color_rays_list.append(ray_given)
            silhouette_rays_list.append(ray_given)
        else:
            color_rays_list.append(Ray(ray_origin, ray_look_at_point - ray_origin))
            silhouette_rays_list.append(Ray(ray_origin, ray_look_at_point - ray_origin))

    for ray in silhouette_rays_list:
        silhouette_objects_hit_list.append(ray_intersection(ray, objects_list) )

    if len(silhouette_rays_list) > 1:
        pass

    is_background = True
    for hit_obj in silhouette_objects_hit_list:
        if hit_obj is not False:
            is_background = False
            break
    if is_background:
        return background_color


    # determining if is edge silhouette
    first_hit_obj = silhouette_objects_hit_list[0]
    if multiple:
        if not first_hit_obj:
            return Vec3(0, 0, 0)
        for hit_obj in silhouette_objects_hit_list[1:]:
            if not hit_obj:
                return Vec3(0, 0, 0)
            if hit_obj.parent is not first_hit_obj.parent:
                return Vec3(0, 0, 0)

    # since we know we hit the same object, we can just send in a "list" of that one object to check the rays against
    #    Still have to do the intersection to set the nearest hit distance of each ray, but should be much faster
    for ray in color_rays_list:
        ray_did_hit = ray_intersection(ray, silhouette_objects_hit_list)

    object_hit = first_hit_obj
    # Is not edge silhouette
    obj_type = type(object_hit)
    if obj_type == Triangle or obj_type == Sphere or obj_type == CheckeredSphere:

        sum_color = Vec3()

        for ray_to_trace in color_rays_list:
            reflected_ray = False
            # only reflect off of things "reasonably" close; this came from some debugging I was doing
            if ray_to_trace.nearest_hit_distance < 1e18:
                point_hit = ray_to_trace.origin + ray_to_trace.nearest_hit_distance * ray_to_trace.direction
                reflected_ray = ray_to_trace.reflect(point_hit, object_hit.get_normal(point_hit))

            # Make sure can actually reflect; if cannot, triangle is facing away from ray origin
            # This would be the same for every ray that hit this object, so is safe to return now
            # This may not be the case in refraction, so may have to look at that part
            if reflected_ray is False:
                return background_color

            shaded_color = shade(reflected_ray.origin, object_hit, list_of_lights=list_of_lights,
                                 list_of_objects=objects_list, ray_to_point=ray_to_trace,
                                 amb_intensity=abs(background_color)/abs(Vec3(255,255,255)) + 0.1, cel_shaded=cel_shaded)

            if object_hit.reflectiveness == 0 or num_bounces + 1 > max_bounces:
                return shaded_color

            reflected_color = ray_trace(objects_list=objects_list,
                                        num_bounces=num_bounces + 1, max_bounces=max_bounces,
                                        background_color=background_color, list_of_lights=list_of_lights,
                                        multiple=multiple, ray_given=reflected_ray)

            sum_color += (1 - object_hit.reflectiveness) * shaded_color + object_hit.reflectiveness * reflected_color

        return sum_color/len(color_rays_list)

    else:
        # reflected_ray = None
        print("Not a Triangle or Sphere")
        return background_color


def ray_intersection(ray, objects):
    obj_hit = None
    for obj in objects:
        if type(obj) == BoundingBox:
            new_obj_hit = obj.intersect(ray)
            if new_obj_hit:
                obj_hit = new_obj_hit
        else:
            b_obj_hit = obj.intersect(ray)
            if b_obj_hit:
                obj_hit = obj
    if obj_hit is not None:
        return obj_hit
    else:
        return False


def shade(point_shaded, object_shaded, list_of_lights, list_of_objects, ray_to_point,
          ambient_color=Vec3(0, 0, 0), amb_intensity=None, cel_shaded=False):
    if len(list_of_lights) == 0:
        print("No lights for shading")
        return object_shaded.get_color(point_hit=point_shaded)

    diffuse_color, specular_color = Vec3(), Vec3()

    for light in list_of_lights:
        shadow_ray = ShadowRay(point_shaded, light)
        in_shadow = False
        for obj in list_of_objects:
            if obj.intersect(shadow_ray): #and obj is not object_shaded:
                in_shadow = True
                break

        if abs(ambient_color) < 0.1:
            assert amb_intensity is not None
            ambient_color = object_shaded.get_color(point_hit=point_shaded) * amb_intensity

        if in_shadow is False:

            l_vec = shadow_ray.direction.normalize()
            norm_at_point = object_shaded.get_normal(point_shaded)
            # Dot product of point to light with point to ray
            l_dot_n = l_vec.dot(norm_at_point)
            diffuse_color += light.intensity * object_shaded.get_color(point_hit=point_shaded) * max(l_dot_n, 0)

            # Reflected Light (Negative because shadow ray pointing away from surface) Shirley & Marschner pg.238
            # Check if is actually reflecting the correct way
            r_vec = 2 * l_vec.dot(norm_at_point) * norm_at_point - l_vec
            e_vec = -1 * ray_to_point.direction  # negative so facing correct way
            e_dot_r = max(e_vec.dot(r_vec), 0)
            specular_color += light.intensity * light.color * pow(e_dot_r, object_shaded.shininess)
        else:
            return ambient_color / 2
            # is in shadow

    total_color = ambient_color + diffuse_color + specular_color

    if cel_shaded:
        color_magnitude = abs(total_color)
        color_shaded = object_shaded.get_color(point_hit=point_shaded)
        if color_magnitude > abs(Vec3(1, 1, 1) * 255):
            return Vec3(1, 1, 1) * 255
        elif color_magnitude > abs(Vec3(0.4, 0.4, 0.4) * 255):
            return color_shaded * 0.8
        elif color_magnitude > abs(Vec3(0.2, 0.2, 0.2) * 255):
            return color_shaded * 0.5
        elif color_magnitude > abs(Vec3(0.05, 0.05, 0.05) * 255):
            return color_shaded * 0.3
        else:
            return Vec3(0, 0, 0)
    else:

        if total_color.x > 255: total_color.x = 255
        if total_color.y > 255: total_color.y = 255
        if total_color.z > 255: total_color.z = 255

        return total_color  # diffuse_color +

