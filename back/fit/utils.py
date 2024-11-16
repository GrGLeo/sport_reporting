import os
from fit_tool.profile.profile_type import Intensity


def get_intensity(name):
    match name:
        case "active":
            return Intensity.ACTIVE
        case "rest":
            return Intensity.REST
        case "warmup":
            return Intensity.WARMUP
        case "cooldown":
            return Intensity.COOLDOWN


def get_path(user_id):
    current_path = os.path.abspath(__file__)
    path = os.path.dirname(os.path.dirname(current_path))
    path = os.path.join(path, 'workout', str(user_id))
    if not os.path.exists(path):
        os.mkdir(path)
    return path
