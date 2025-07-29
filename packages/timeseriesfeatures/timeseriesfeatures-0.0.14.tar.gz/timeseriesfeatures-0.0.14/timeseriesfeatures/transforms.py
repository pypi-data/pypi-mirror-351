"""A list of transforms."""

from .transform import Transform
from .transform_acceleration import acceleration_transform
from .transform_jerk import jerk_transform
from .transform_log import log_transform
from .transform_snap import snap_transform
from .transform_velocity import velocity_transform

TRANSFORMS = {
    str(Transform.NONE): lambda x: x,
    str(Transform.VELOCITY): velocity_transform,
    str(Transform.LOG): log_transform,
    str(Transform.ACCELERATION): acceleration_transform,
    str(Transform.JERK): jerk_transform,
    str(Transform.SNAP): snap_transform,
}
