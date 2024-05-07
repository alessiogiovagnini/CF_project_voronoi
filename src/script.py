import utils
from pathlib import Path
import bpy
import sys
import mathutils


# density is the number of point per 1 unit of volume
def script_start(source: Path, output: Path, density: int = 100, radius: float = 1):
    utils.clear_scene()  # in case we have the default cube, camera and light

    utils.import_file(file=source)

    # TODO for now the imported file should contain only one object/mesh
    objects_in_scene = len(bpy.data.objects)
    if objects_in_scene > 1 or objects_in_scene == 0:
        print("imported file should contain 1 mesh only (for now)")
        sys.exit(1)

    b_box_min, b_box_max = utils.get_bounding_box(obj=bpy.data.objects[0])

    x_size, y_size, z_size = utils.bounding_box_size(corner_min=b_box_min, corner_max=b_box_max)

    volume = x_size * y_size * z_size

    total_num_points: int = int(density * volume)




