from pathlib import Path

OUTPUT = Path("tests/fixtures/invalid_geometry_polygon_limit.usda")

POLYGON_COUNT = 100001

lines = [
    "#usda 1.0",
    "",
    "(",
    '    defaultPrim = "World"',
    ")",
    "",
    'def Xform "World"',
    "{",
    '    def Mesh "PolygonLimitMesh"',
    "    {",
]

points = []
indices = []
face_counts = []

for i in range(POLYGON_COUNT):
    base = i * 3

    points.extend([
        f"({i}, 0, 0)",
        f"({i}, 1, 0)",
        f"({i}, 0, 1)",
    ])

    indices.extend([
        str(base),
        str(base + 1),
        str(base + 2),
    ])

    face_counts.append("3")

lines.append("        point3f[] points = [")
for i, point in enumerate(points):
    comma = "," if i < len(points) - 1 else ""
    lines.append(f"            {point}{comma}")
lines.append("        ]")

lines.append("")
lines.append("        int[] faceVertexCounts = [")
for i, count in enumerate(face_counts):
    comma = "," if i < len(face_counts) - 1 else ""
    lines.append(f"            {count}{comma}")
lines.append("        ]")

lines.append("")
lines.append("        int[] faceVertexIndices = [")
for i, index in enumerate(indices):
    comma = "," if i < len(indices) - 1 else ""
    lines.append(f"            {index}{comma}")
lines.append("        ]")

lines.extend([
    "    }",
    "}",
])

OUTPUT.write_text("\n".join(lines), encoding="utf-8")

print(f"Created {OUTPUT}")