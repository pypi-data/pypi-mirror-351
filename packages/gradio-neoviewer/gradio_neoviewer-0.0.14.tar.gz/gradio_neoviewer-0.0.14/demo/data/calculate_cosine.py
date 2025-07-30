
import math

def calculate_cosine(angle_radians):
    """
    Calculate the cosine of a given angle in radians.

    Parameters:
    angle_radians (float): The angle in radians for which to calculate the cosine.

    Returns:
    float: The cosine of the given angle.
    """
    return math.cos(angle_radians)

if __name__ == "__main__":
    # Example usage
    angle = float(input("Enter the angle in radians: "))
    cosine_value = calculate_cosine(angle)
    print(f"The cosine of {angle} radians is {cosine_value}")
