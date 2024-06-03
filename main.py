from scipy.spatial import Voronoi
import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
from src.script import script_from_points, script_from_json


def plot_points(points_arr, points_arr2=None):
    fig = plt.figure()
    ax = plt.axes(projection="3d")
    x_p = [p[0] for p in points_arr]
    y_p = [p[1] for p in points_arr]
    z_p = [p[2] for p in points_arr]
    ax.scatter3D(x_p, y_p, z_p, color="green")
    if points_arr2 is not None:
        x_p2 = [p[0] for p in points_arr2]
        y_p2 = [p[1] for p in points_arr2]
        z_p2 = [p[2] for p in points_arr2]
        ax.scatter(x_p2, y_p2, z_p2, color="red")
    plt.show()


def generate_random_points(min_x: int, max_x: int, min_y: int, max_y: int, min_z: int, max_z: int):
    return [
        np.random.uniform(low=min_x, high=max_x),
        np.random.uniform(low=min_y, high=max_y),
        np.random.uniform(low=min_z, high=max_z)
    ]


def generate_points(max_size: int = 10):
    to_return = []
    for x in range(max_size+1):
        for y in range(max_size+1):
            for z in range(max_size+1):
                to_return.append(np.array([x, y, z]))
    return to_return


# Generate a list of tuples where each tuple represent the starting and ending index of the segment
# the
def make_segments(ridge_vertices: np.array) -> list[tuple]:
    segment_list: list = []
    for ridge in ridge_vertices:
        filtered_ridge = [r for r in ridge if r >= 0]  # filter out element that are -1, since they are virtual vertices
        if len(filtered_ridge) <= 1:
            continue    # if the array is empty or has only one vertex then we can skip
        elif len(filtered_ridge) == 2:
            segment = (filtered_ridge[0], filtered_ridge[1])
            segment_list.append(segment)
        else:  # len is most likely 3 or 4
            for i in range(len(filtered_ridge) -1):
                segment = (filtered_ridge[i], filtered_ridge[i+1])
                segment_list.append(segment)
            last_segment = (filtered_ridge[0], filtered_ridge[len(filtered_ridge)-1])
            segment_list.append(last_segment)
    without_repetition = list(set([tuple(sorted(t)) for t in segment_list]))  # remove repetition like (a, b) and (b, a)
    return without_repetition


def main():
    max_limit: int = 100
    p = [generate_random_points(0, max_limit, 0, max_limit, 0, max_limit) for _ in range(30)]

    points: np.array = np.array(p)

    points2 = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2],
                       [0, 1, 0], [0, 1, 1], [0, 1, 2],
                       [0, 2, 0], [0, 2, 1], [0, 2, 2],
                       [1, 0, 0], [1, 0, 1], [1, 0, 2],
                       [1, 1, 0], [1, 1, 1], [1, 1, 2],
                       [1, 2, 0], [1, 2, 1], [1, 2, 2]])

    vor2 = Voronoi(points=points2)

    vor = Voronoi(points=points)
    vertices = vor.vertices
    ridge_points = vor.ridge_points

    print(len(vor2.vertices))
    # plot_points(points2, vor2.vertices)
    plot_points(p, vertices)
    # plot_points(vertices)

    import sys
    sys.exit(0)


def plot_segments(segments_index, vertices):

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    for segment in segments_index:
        start = segment[0]
        end = segment[1]
        start_vertex = vertices[start]
        end_vertex = vertices[end]
        ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], zs=[start_vertex[2], end_vertex[2]])
    plt.show()


def main_2():
    p = generate_points(5)
    v = Voronoi(p)
    plot_points(p, v.vertices)

    all_segments = make_segments(v.ridge_vertices)

    plot_segments(all_segments, v.vertices)


if __name__ == '__main__':
    # main()
    # main_2()

    # parser = argparse.ArgumentParser(description="Process mesh with voronoi")
    # parser.add_argument("--source", type=Path, help="path to source file", required=True)
    # parser.add_argument("--output", type=Path, help="path to output file",
    # required=False, default="./output_mesh.stl")
    #
    # args = parser.parse_args()
    #
    # script_start(source=Path(args.source), output=Path(args.output))

    # source: Path = Path("./test_mesh/monkey_mesh.stl")
    # source_points: Path = Path("./test_mesh/small_monkey_points.obj")
    # output: Path = Path("./test_mesh/monkey_output.stl")
    # script_from_points(source=source, output=output, point_file=source_points)

    json_source: Path = Path("./data/example.json")

    out_path: Path = Path("./data/tmp2.blend").resolve()
    script_from_json(json_path=json_source, out=out_path)




