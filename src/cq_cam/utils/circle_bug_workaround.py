import cadquery as cq


def circle_bug_workaround(source_wire: cq.Wire, target_wires: list[cq.Wire]):
    """
    FreeCAD style workaround for
    https://github.com/CadQuery/cadquery/issues/896

    :param source_wire:
    :param target_wires:
    :return:
    """

    for target_wire in target_wires:
        source_edges = source_wire.Edges()
        apply_fix = False
        for i, target_edge in enumerate(target_wire.Edges()):
            if target_edge.geomType() == "CIRCLE":
                if i < len(source_edges):
                    source_edge = source_edges[i]
                    # target_edge.wrapped.Location(source_edge.wrapped.Location().Inverted())
                    apply_fix = True
        if apply_fix:
            target_wire.wrapped.Location(
                source_wire.wrapped.Location().Inverted())

    # for edge in source_wire.Edges():
    #     geom_type = edge.geomType()
    #     # print(geom_type)

    #     if geom_type == "CIRCLE":
    #         print("bug fix")
    #         print(len(target_wires))
    #         for target_wire in target_wires:
    #             for target_edge in target_wire.Edges():
    #                 target.wrapped.Location(source_wire.wrapped.Location().Inverted())

