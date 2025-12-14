import math
import numpy as np
import cv2

def meters_per_pixel(lat, zoom):
    return 156543.03392 * math.cos(math.radians(lat)) / (2 ** zoom)

def sqft_to_m2(sqft):
    return sqft * 0.092903

def area_to_radius_px(area_m2, mpp):
    return math.sqrt(area_m2 / math.pi) / mpp

def circular_mask(h, w, r):
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (w // 2, h // 2), int(r), 1, -1)
    return mask
