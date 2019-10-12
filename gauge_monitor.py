from PIL import Image, ImageDraw
from io import BytesIO
import json
import base64
import math
import numpy as np
import os
import time
from sklearn.linear_model import LinearRegression
import statistics



"""
    Note: Throughout this module, in order to simplify variable names,
    'squared residuals' will simply be referred to as 'residuals'.
"""



def default_values():
    return {
            "sensitivity": 70,
            "r_factor": 1,
            "sm_r_factor": 0.2,
            "pxls_detected_min": 5,
            "r_sq_min": 0.4,
            "residual_cutoff": 5,
            "ref_angle": 227,
            "calib": 0.35,
            }




def read( image_string, comp_ratio, radius, sensitivity, r_factor, sm_r_factor, pxls_detected_min,
          r_sq_min, residual_cutoff, ref_angle, calib):
    """
    The darker pixels on the image likely represent the gauge needle. Obtain the slope of the needle
    via linear regression, and convert to the angle. By comparing to the reference angle and calibration,
    the angle can be converted to a psig reading.
    """

    # Initialize
    psig, x_unit, y_unit, points_x, points_y, slope, angle, r_sq, pxls_detected = (999,)*9 # Inspired by analog sensors that read 999 when disconnected.

    # Prep image
    image = base64string2image(image_string)
    width, height = image.size
    center_point = (width/2, height/2)


    points_x, points_y = get_dark_pixels_in_area(image, center_point, radius*(1/comp_ratio)*r_factor, radius*(1/comp_ratio)*sm_r_factor, sensitivity)

    if len(points_x) >= pxls_detected_min:
        slope, intercept, r_sq = linear_regression(points_x, points_y)

        if r_sq >= r_sq_min:  # Prevent excessively noisy data from giving false readings
            points_with_residuals = linear_regression_residuals(points_x, points_y, slope, intercept)  # Further controls noise
            psig, angle = get_psig(slope, points_with_residuals, residual_cutoff, ref_angle, calib, center_point)
            x_unit, y_unit = get_unit_circle_cartesian_coords(angle)


    return {
             "psig": psig,
             "x_unit": x_unit, "y_unit": y_unit,
             "points_x": json.dumps(points_x), "points_y": json.dumps(points_y),
             "slope": slope,
             "angle": angle,
             "r_sq": r_sq,
             "pxls_detected": len(points_x)
            }





def get_dark_pixels_in_area(img, center_point, big_radius, small_radius, sensitivity):
    """
    Find all pixels that are sufficiently dark (grayscale_pixel < sensitivity)
    and that also fall within the relevant area defined as the area between
    the small circle and the large circle.
    """

    pixelMap = img.load()
    width, height = img.size
    dark_x, dark_y = [], []

    for col in range(width):
        for row in range(height):
            if is_inside_area((col, row), center_point, big_radius, small_radius):
                pixel = pixelMap[col, row]
                grayscale_pixel = 0.2989 * pixel[0] + 0.5870 * pixel[1] + 0.1140 * pixel[2]   # grayscale_pixel value range: 0-255
                if grayscale_pixel < sensitivity:
                    dark_x.append(col)
                    dark_y.append(row)
    return dark_x, dark_y




def linear_regression(datapoints_x, datapoints_y):
    """
    Given some datapoints, determine the slope, intercept, and R squared.
    """
    slope, b, r_sq = (999,)*3  # Intialize

    try:
        x_arr = np.array(datapoints_x).reshape((-1, 1))
        y_arr = np.array(datapoints_y)

        model = LinearRegression()
        model.fit(x_arr, y_arr)
        slope = round(model.coef_[0],4)
        intercept = round(model.intercept_,4)
        r_sq = model.score(x_arr, y_arr)  # A measure of goodness of fit

    except Exception as e:
        print("ERROR in linear regression", e)

    return slope, intercept, r_sq




def linear_regression_residuals(datapoints_x, datapoints_y, slope, intercept):
    """
    Return a list of tuples containing x, y, and the square of the difference between actual and predicted y values.
    """
    y_predict = lambda x : slope * x + intercept
    residuals = [ round((y_predict(x) - y) ** 2, 2) for x, y in zip(datapoints_x, datapoints_y) ]
    return list(zip(datapoints_x, datapoints_y, residuals))





def get_psig(slope, points_with_residuals, residual_cutoff, ref_angle, calib, center_point):
    """
    Any slope is associated with two angles. The needle angle corresponds to one of these angles.
    By knowing whether the needle is pointing up or down, the corresponding angle can be determined.

    If the needle is pointing down, the chosen angle is the LARGER of the two angles.
    Otherwise, the smaller is chosen.

    Compare the chosen angle to the reference angle entered by user. Convert to PSIG using the calibration.
    """

    # Calculate both angles
    slope_adj = -slope # flip the sign because the image y-axis increases top to bottom
    angle1 = math.degrees(math.atan(slope_adj))
    angle2 = angle1 + 180

    if angle1 < 0: # If initial angle was negative, converted angle = 360 - abs(theta) ...or 360 + theta
        angle1 = 360 + angle1

    if angle1 > angle2:
        large_angle, small_angle = angle1, angle2
    else:
        large_angle, small_angle = angle2, angle1


    direction = is_needle_pointing_up_or_down(points_with_residuals, center_point, residual_cutoff)

    if direction == 999:
        return 999, 999
    elif "down" in direction:
        angle = large_angle
    else:
        angle = small_angle

    # Find the angular distance between the angle and the reference angle
    if angle < ref_angle:
        ang_dist = ref_angle - angle
    else:
        ang_dist = 360 - angle + ref_angle

    psig = round(ang_dist * calib, 0) # Accuracy depends greatly on the user-entered calib
    return psig, angle





def base64string2image(image_string):
    """
    convert base64 string to PIL Image
    """
    imgdata = base64.b64decode(image_string)
    return Image.open(BytesIO(imgdata))




def is_inside_area(point, center_point, big_radius, small_radius):
    """
    Is a pixel found within a radial range?
    """
    distance = get_distance(point, center_point)
    if distance >= small_radius and distance <= big_radius:
        return True
    return False




def get_distance(point1, point2):
    """
    point1, point2 are (x,y) tuples
    Pythagorean theorem to find the distance between two points
    """
    return math.sqrt(pow(point1[0]-point2[0],2) + pow(point1[1]-point2[1],2))




def get_unit_circle_cartesian_coords(angle):
    """
    From the angle, find x_unit and y_unit coordinates of the unit circle.
    The output can be multiplied with the radius to determine the scaled-up cartesian coordinates.
    """
    y_unit = -round(math.sin(math.radians(angle)),3)
    x_unit = round(math.cos(math.radians(angle)),3)
    return x_unit, y_unit




def is_needle_pointing_up_or_down(points_with_residuals, center_point, residual_cutoff):
    """
    The most distant point from the center indicates which way the needle is pointing.
    To prevent noise from interfering, points with a residual above the residual_cutoff are neglected.
    """
    point_distances = []
    relevant_points = []

    for point_with_residual in points_with_residuals:
        x,y,residual = point_with_residual
        if residual < residual_cutoff:
            point_distances.append(get_distance((x,y), center_point))  # get distance from center
            relevant_points.append((x,y))

    if len(point_distances) == 0:
        return 999

    farthest_point = relevant_points[point_distances.index(max(point_distances))]   # get point with max distance to center

    if farthest_point[1] >= center_point[1]:
        return "down"
    else:
        return "up"
