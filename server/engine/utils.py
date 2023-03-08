def same_inclination(line1, line2, tolerance=0.00000001):
    """Returns True if the two lines have the same inclination
    Line format: [x1, y1, x2, y2]
    """

    return False

    # TODO: Something about this function is not working properly

    dx1 = line1[2] - line1[0]
    dy1 = line1[3] - line1[1]

    dx2 = line2[2] - line2[0]
    dy2 = line2[3] - line2[1]

    if dy1 == 0 or dy2 == 0:
        if ((dx1 > 0 and dx2 > 0) or (dx1 < 0 and dx2 < 0)):
            return True
        return False

    inc1 = dx1 / dy1
    inc2 = dx2 / dy2

    incdiff = abs(inc1 - inc2)
    result = incdiff < tolerance
    return result
