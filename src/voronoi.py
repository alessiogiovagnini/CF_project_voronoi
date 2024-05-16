import numpy as np


def generate_random_point(min_x: int, max_x: int, min_y: int, max_y: int, min_z: int, max_z: int) -> list:
    return [
        np.random.uniform(low=min_x, high=max_x),
        np.random.uniform(low=min_y, high=max_y),
        np.random.uniform(low=min_z, high=max_z)
    ]


def generate_n_random_points(n: int, min_x: int, max_x: int, min_y: int, max_y: int, min_z: int, max_z: int) -> list:
    points: list = []
    for i in range(n+1):
        p = generate_random_point(min_x=min_x, max_x= max_x, min_y=min_y, max_y=max_y, min_z=min_z, max_z=max_z)
        points.append(p)
    return points


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


