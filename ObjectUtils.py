import math
from typing import Tuple


def point_3d(v):
    return [v[0], v[1], v[2]]


def magnitude(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def cross_product(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def vector(a, b):
    return [b[0] - a[0], b[1] - a[1], b[2] - a[2]]


BEFORE_SEGMENT = 0
ON_SEGMENT = 1
AFTER_SEGMENT = 2


def distance(line_a, line_b, point) -> Tuple[float, int]:
    """
    :param line_a: first point on the line segment
    :param line_b: second point on the line segment
    :param point: point to calculate distance to line from
    :return: (distance, where on line segment distance calculated to (before, on, after))
    """
    distance_a_to_point = magnitude(vector(line_a, point))
    distance_b_to_point = magnitude(vector(line_b, point))
    segment_length = magnitude(vector(line_a, line_b))

    # Angles <line_b, line_a, point> and <line_a, line_b, point> both must be < 90 degrees if the closest point
    # on the line segment is not one of the ends. Therefore the cosine of both angles needs to be greater than 0.
    # By using the cosine rule, the closest point on the line segment is point a if
    # distance_b_to_point ^ 2 > segment_length ^ 2 + distance_a_to_point ^ 2,
    # and point b if
    # distance_a_to_point ^ 2 > segment_length ^ 2 + distance_b_to_point ^ 2
    if segment_length == 0:
        return distance_a_to_point, ON_SEGMENT
    elif distance_b_to_point ** 2 > segment_length ** 2 + distance_a_to_point ** 2:
        return distance_a_to_point, BEFORE_SEGMENT
    elif distance_a_to_point ** 2 > segment_length ** 2 + distance_b_to_point ** 2:
        return distance_b_to_point, AFTER_SEGMENT
    else:
        return magnitude(cross_product(vector(line_b, line_a), vector(line_b, point))) / segment_length, ON_SEGMENT


def closest_segment(obj, segments) -> Tuple[int, int]:
    """
    :param obj:
    :param segments: map number to (line_a, line_b)
    :return: (closest segment number, relative position (before, on, after))
    """
    object_point = point_3d(obj.location)
    segment_number: int = 0

    distance_to_nearest_segment = (float("inf"), ON_SEGMENT)
    for i in range(len(segments)):
        distance_to_segment = distance(segments[i][0], segments[i][1], object_point)
        if distance_to_segment[0] < distance_to_nearest_segment[0]:
            distance_to_nearest_segment = distance_to_segment
            segment_number = i
    return segment_number, distance_to_nearest_segment[1]


def objects_sorted_by_path(objects, path):
    """
    :param objects: objects to sort
    :param path: path to sort by
    :return: objects sorted along path (does not include the path, even if the path is one of the objects)
    """
    spline = path.data.splines.active
    if spline.bezier_points is not None and len(spline.bezier_points) > 0:
        path_points = [path.matrix_world @ point.co for point in spline.bezier_points]
    else:
        path_points = [path.matrix_world @ point.co for point in spline.points]
    segment_count = len(path_points) - 1
    path_segments = {i: (point_3d(path_points[i]), point_3d(path_points[i + 1]), [])
                     for i in range(segment_count)}
    objects_before_path = []
    objects_after_path = []

    for obj in objects:
        if obj != path:
            nearest = closest_segment(obj, path_segments)
            if nearest[0] == 0 and nearest[1] == BEFORE_SEGMENT:
                objects_before_path.append(obj)
            elif nearest[0] == segment_count - 1 and nearest[1] == AFTER_SEGMENT:
                objects_after_path.append(obj)
            else:
                path_segments[nearest[0]][2].append(obj)

    # sort objects before the path in reverse order (farthest from path is first)
    objects_before_path.sort(key=lambda x: magnitude(vector(path_segments[0][0], point_3d(x.location))), reverse=True)
    sorted_objects = objects_before_path

    for segment in path_segments.values():
        segment_objects = segment[2]
        if len(segment_objects) > 0:
            # for each segment, sort objects by distance to the first point on the segment
            segment_objects.sort(key=lambda x: magnitude(vector(segment[0], point_3d(x.location))))
            sorted_objects.extend(segment_objects)

    # add objects after the path after objects that are on the path
    objects_after_path.sort(key=lambda x: magnitude(vector(path_segments[segment_count - 1][0], point_3d(x.location))))
    sorted_objects.extend(objects_after_path)

    return sorted_objects
