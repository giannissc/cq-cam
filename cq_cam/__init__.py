from cq_cam.common import Unit
from cq_cam.job import Job
from cq_cam.operations.drill import Drill
from cq_cam.operations.pocket import Pocket
from cq_cam.operations.profile import Profile
from cq_cam.operations.strategy import ZigZagStrategy, ContourStrategy
from cq_cam.operations.tabs import EdgeTabs, WireTabs

_extra = []
try:
    from cq_cam.operations.op3d import Surface3D
    _extra.append('Surface3D')
except ModuleNotFoundError:
    pass

METRIC = Unit.METRIC
IMPERIAL = Unit.IMPERIAL

__all__ = [
    'Job',
    'Profile',
    'Pocket',
    'Drill',
    'Unit',
    'ZigZagStrategy',
    'ContourStrategy',
    'EdgeTabs',
    'WireTabs',
    'METRIC',
    'IMPERIAL',
] + _extra
