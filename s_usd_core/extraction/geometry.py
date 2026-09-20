from pxr import UsdGeom


class GeometryExtractor:
    def extract(self, stage):
        from s_usd_core.contexts import GeometryStatistics, MeshGeometry

        geometry = GeometryStatistics()

        for prim in stage.TraverseAll():
            if prim.GetTypeName() != "Mesh":
                continue

            mesh = UsdGeom.Mesh(prim)
            points = mesh.GetPointsAttr().Get()
            counts = mesh.GetFaceVertexCountsAttr().Get()
            indices = mesh.GetFaceVertexIndicesAttr().Get()
            points_count = len(points) if points else 0
            face_count = len(counts) if counts else 0
            item = MeshGeometry(
                path=str(prim.GetPath()),
                points_count=points_count,
                face_count=face_count,
                polygon_count=face_count,
                points_valid=self._points_are_valid(points),
                face_vertex_counts_valid=self._face_counts_are_valid(
                    counts, points_count
                ),
                topology_valid=self._topology_is_valid(
                    counts, indices, points_count
                ),
                extent_authored=mesh.GetExtentAttr().HasAuthoredValueOpinion(),
                subdivision_scheme=mesh.GetSubdivisionSchemeAttr().Get() or "none",
                orientation=mesh.GetOrientationAttr().Get() or "rightHanded",
            )
            geometry.meshes.append(item)
            geometry.mesh_count += 1
            geometry.total_points += points_count
            geometry.total_faces += face_count
            geometry.total_polygons += face_count

        return geometry

    @staticmethod
    def _points_are_valid(points):
        return bool(points) and all(len(point) == 3 for point in points)

    @staticmethod
    def _face_counts_are_valid(counts, points_count):
        return bool(counts) and all(3 <= count <= points_count for count in counts)

    @staticmethod
    def _topology_is_valid(counts, indices, points_count):
        if not counts or not indices or sum(counts) != len(indices):
            return False

        return all(0 <= index < points_count for index in indices)
