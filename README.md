# ray_tracer
## Basic ray tracer for rendering spheres and triangles. *(With reflections)*

Final project for Computer Graphics at MSState

By Dalton R. Pruitt

Driven by main.py, where many of the different parameters are determined, such as image size and turning on/off cel-shading and edge silhouettes. (Sorry, no GUI yet.)

#### Current Issues:
	- Reflections of triangles do not work correctly (invisible from backside or something) when the Bounding Box acceleration strucutre is used; assumed that this is due to some box intersection issues. 
	- Current coordinate system has the +z direction facing away from the camera, not the conventional "towards the camera"; this is causes issues with the usual way that we define the normals of triangles (and models, if stored in the model)
	- The lighting has only been tested for a single PointLight; neither multiple lights nor other types of lights (Directional or Spotlight) have been tested/implemented (multiple point lights can be used easily, I just never made more than one)


#### All extraneous imports used:
	-PIL
	-numpy
	-datetime
	-time
	-transformations
	-os
	-math
	-copy
	-random
	-Numbers
	-builtins
