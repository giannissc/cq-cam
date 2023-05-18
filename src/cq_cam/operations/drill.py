from dataclasses import dataclass
from typing import Union

import cadquery as cq

from cq_cam.address import AddressVector
from cq_cam.command import PlungeCut, Rapid
from cq_cam.operations.base_operation import Operation, OperationError
from cq_cam.operations.strategy import Strategy
from cq_cam.utils.utils import flatten_list

_op_o_shapes = Union[cq.Wire, cq.Face, cq.Vector]


@dataclass
class Drill(Operation):
    wp: cq.Workplane = None
    """ The cadquery Workplane containing faces and/or
    wires that the profile will operate on. 
    """
    o: Union[cq.Workplane, list[_op_o_shapes], _op_o_shapes] = None
    depth: float = None
    previous_pos: AddressVector | None = None

    def __post_init__(self):
        # TODO max depth
        # TODO evacuate chips?
        transform_f = self.job.top.toWorldCoords
        drill_vectors: list[cq.Vector] = []
        if self.previous_pos is None:
            self.previous_pos = AddressVector()

        if self.o is None:
            raise OperationError("o must be defined")

        if self.depth is None:
            raise OperationError("depth must be defined")

        for obj in self._o_objects(self.o):
            if isinstance(obj, cq.Vector):
                drill_vectors.append(transform_f(obj))
            elif isinstance(obj, cq.Wire):
                drill_vectors.append(transform_f(cq.Face.makeFromWires(obj).Center()))
            elif isinstance(obj, cq.Face):
                if obj.innerWires():
                    for wire in obj.innerWires():
                        drill_vectors.append(
                            transform_f(cq.Face.makeFromWires(wire).Center())
                        )
                else:
                    drill_vectors.append(
                        transform_f(cq.Face.makeFromWires(obj.outerWire()).Center())
                    )
            else:
                raise OperationError(
                    f'Object type "{type(obj)}" not supported by Profile operation'
                )

        if not drill_vectors:
            raise OperationError("Given wp does not contain anything to do")

        drill_points = [(point.x, point.y) for point in drill_vectors]
        ordered_drill_points = []
        cut_sequences = []
        last = None
        while drill_points:
            drill_point = (
                Strategy._pick_nearest(last, drill_points) if last else drill_points[0]
            )
            ordered_drill_points.append(drill_point)
            drill_points.pop(drill_points.index(drill_point))
            last = drill_point

        depth = -abs(self.depth)
        for point in ordered_drill_points:
            ops = []
            ops.append(Rapid.abs(z=self.job.op_safe_height, start=self.previous_pos))
            self.previous_pos = ops[-1].end
            ops.append(Rapid.abs(x=point[0], y=point[1], start=self.previous_pos))
            self.previous_pos = ops[-1].end
            ops.append(Rapid.abs(z=0, start=self.previous_pos))
            self.previous_pos = ops[-1].end
            ops.append(
                PlungeCut.abs(z=depth, feed=self.job.feed, start=self.previous_pos)
            )
            self.previous_pos = ops[-1].end
            cut_sequences.append(ops)
        cut_sequences = flatten_list(cut_sequences)
        self.commands = cut_sequences
