from pxr import UsdGeom


class GeometryExtractor:
    def extract(self, stage):
        from contexts import GeometryStatistics, MeshGeometry

        geometry = GeometryStatistics()

        for prim in stage.TraverseAll():
            if prim.GetTypeName() != "Mesh":
                continue

            mesh = UsdGeom.Mesh(prim)

            points = mesh.GetPointsAttr().Get()
            face_vertex_counts = mesh.GetFaceVertexCountsAttr().Get()
            face_vertex_indices = mesh.GetFaceVertexIndicesAttr().Get()

            points_count = len(points) if points else 0
            face_count = len(face_vertex_counts) if face_vertex_counts else 0
            polygon_count = face_count

            points_valid = self._points_are_valid(points)
            face_vertex_counts_valid = self._face_vertex_counts_are_valid(
                face_vertex_counts,
                points_count,
            )
            topology_valid = self._topology_is_valid(
                face_vertex_counts,
                face_vertex_indices,
                points_count,
            )

            mesh_geometry = MeshGeometry(
                path=str(prim.GetPath()),
                points_count=points_count,
                face_count=face_count,
                polygon_count=polygon_count,
                points_valid=points_valid,
                face_vertex_counts_valid=face_vertex_counts_valid,
                topology_valid=topology_valid,
            )

            geometry.meshes.append(mesh_geometry)

            geometry.mesh_count += 1
            geometry.total_points += points_count
            geometry.total_faces += face_count
            geometry.total_polygons += polygon_count

        return geometry

    @staticmethod
    def _points_are_valid(points):
        if not points:
            return False

        return all(
            len(point) == 3
            for point in points
        )

    @staticmethod
    def _face_vertex_counts_are_valid(
        face_vertex_counts,
        points_count,
    ):
        if not face_vertex_counts:
            return False

        return all(
            count >= 3 and count <= points_count
            for count in face_vertex_counts
        )

    @staticmethod
    def _topology_is_valid(
        face_vertex_counts,
        face_vertex_indices,
        points_count,
    ):
        if not face_vertex_counts or not face_vertex_indices:
            return False

        if sum(face_vertex_counts) != len(face_vertex_indices):
            return False

        return all(
            0 <= index < points_count
            for index in face_vertex_indices
        )