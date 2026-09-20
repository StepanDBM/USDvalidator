from __future__ import annotations

import argparse
import random
from pathlib import Path


HEADER = '''#usda 1.0
(
    defaultPrim = "World"
    documentation = "Generated deterministic USD validator fixture"
    endTimeCode = 240
    framesPerSecond = 24
    metersPerUnit = 1
    startTimeCode = 1
    timeCodesPerSecond = 24
    upAxis = "Y"
)

'''


def vec3(rng, scale=10.0):
    return tuple(round(rng.uniform(-scale, scale), 4) for _ in range(3))


def mesh_block(index, rng, bad=None):
    name = f"Mesh_{index:04d}"
    tx, ty, tz = vec3(rng, 100.0)
    size = round(rng.uniform(0.25, 4.0), 3)
    points = [
        (-size, -size, 0), (size, -size, 0), (size, size, 0), (-size, size, 0),
        (-size, -size, size * 2), (size, -size, size * 2),
        (size, size, size * 2), (-size, size, size * 2),
    ]
    point_text = ", ".join(f"({x}, {y}, {z})" for x, y, z in points)
    counts = "[4, 4, 4, 4, 4, 4]"
    indices = "[0,1,2,3, 4,7,6,5, 0,4,5,1, 1,5,6,2, 2,6,7,3, 4,0,3,7]"
    normals = "[(0,0,-1), (0,0,1), (0,-1,0), (1,0,0), (0,1,0), (-1,0,0)]"
    uv_indices = "[0,1,2,3, 0,3,2,1, 0,1,2,3, 0,1,2,3, 0,1,2,3, 0,1,2,3]"
    orientation = "rightHanded"
    subdivision = "none"
    extent = f"[({-size}, {-size}, 0), ({size}, {size}, {size * 2})]"
    material = f"/World/Looks/Material_{index % 12:02d}"
    visibility = "inherited"
    scale = "(1, 1, 1)"

    if bad == "topology":
        counts = "[4, 4, 4, 4, 4, 99]"
    elif bad == "indices":
        indices = "[0,1,2,999, 4,7,6,5]"
    elif bad == "normals":
        normals = "[(0,0,0), (1e30,0,0)]"
    elif bad == "uv_indices":
        uv_indices = "[0,1,2,99]"
    elif bad == "negative_scale":
        scale = "(-1, 1, 1)"
    elif bad == "orientation":
        orientation = "insideOut"
    elif bad == "subdivision":
        subdivision = "unsupportedScheme"
    elif bad == "extent":
        extent = "[(10,10,10), (-10,-10,-10)]"
    elif bad == "missing_material":
        material = "/World/Looks/DoesNotExist"
    elif bad == "invisible":
        visibility = "invisible"

    return f'''    def Mesh "{name}" (
        prepend apiSchemas = ["MaterialBindingAPI"]
    )
    {{
        float3[] extent = {extent}
        int[] faceVertexCounts = {counts}
        int[] faceVertexIndices = {indices}
        normal3f[] normals = {normals} (
            interpolation = "uniform"
        )
        point3f[] points = [{point_text}]
        texCoord2f[] primvars:st = [(0,0), (1,0), (1,1), (0,1)] (
            interpolation = "faceVarying"
        )
        int[] primvars:st:indices = {uv_indices}
        uniform token orientation = "{orientation}"
        uniform token subdivisionScheme = "{subdivision}"
        token visibility = "{visibility}"
        rel material:binding = <{material}>
        double3 xformOp:scale = {scale}
        double3 xformOp:translate = ({tx}, {ty}, {tz})
        uniform token[] xformOpOrder = ["xformOp:translate", "xformOp:scale"]
    }}

'''


def material_blocks(bad=False):
    blocks = ['    def Scope "Looks"\n    {\n']
    for index in range(12):
        shader_id = "BrokenShader" if bad and index == 1 else "UsdPreviewSurface"
        texture = "C:/temporary/absolute_texture.png" if bad and index == 2 else f"textures/texture_{index:02d}.png"
        connection = "" if bad and index == 3 else f'\n            token outputs:surface.connect = </World/Looks/Shader_{index:02d}.outputs:surface>'
        blocks.append(f'''        def Material "Material_{index:02d}"
        {{{connection}
        }}

        def Shader "Shader_{index:02d}"
        {{
            uniform token info:id = "{shader_id}"
            color3f inputs:diffuseColor = ({index / 12:.4f}, {1 - index / 12:.4f}, 0.5)
            float inputs:metallic = {0.1 * (index % 5):.2f}
            float inputs:roughness = {0.2 + 0.05 * index:.2f}
            asset inputs:file = @{texture}@
            token outputs:surface
        }}

''')
    blocks.append("    }\n\n")
    return "".join(blocks)


def scene_domains(bad=False):
    intensity = -20 if bad else 1500
    near, far = ((100, 1) if bad else (0.1, 10000))
    focal = -35 if bad else 50
    selection = "missingChoice" if bad else "high"
    reference = "C:/missing/asset.usda" if bad else "assets/referenced_asset.usda"
    output = "C:/temp/beauty.exr" if bad else "renders/beauty.exr"
    return f'''    def Scope "Lights"
    {{
        def SphereLight "KeyLight"
        {{
            float inputs:intensity = {intensity}
            float inputs:exposure = 2
            color3f inputs:color = (1, 0.92, 0.8)
            float inputs:radius = 2
            rel collection:lightLink:includes = [</World/Geometry/Mesh_0000>, </World/Geometry/Mesh_0001>]
        }}
        def DomeLight "Environment"
        {{
            asset inputs:texture:file = @textures/studio.exr@
            float inputs:intensity = 0.8
        }}
    }}

    def Scope "Render"
    {{
        def RenderSettings "Settings"
        {{
            rel camera = </World/Cameras/MainCamera>
            rel products = </World/Render/Beauty>
            token[] includedPurposes = ["default", "render"]
        }}
        def RenderProduct "Beauty"
        {{
            token productType = "raster"
            asset productName = @{output}@
            int2 resolution = (1920, 1080)
            float pixelAspectRatio = 1
            rel camera = </World/Cameras/MainCamera>
            rel orderedVars = [</World/Render/Color>, </World/Render/Depth>]
        }}
        def RenderVar "Color"
        {{
            token dataType = "color3f"
            string sourceName = "Ci"
            token sourceType = "raw"
        }}
        def RenderVar "Depth"
        {{
            token dataType = "float"
            string sourceName = "depth"
            token sourceType = "raw"
        }}
    }}

    def Scope "Cameras"
    {{
        def Camera "MainCamera"
        {{
            float focalLength = {focal}
            float2 clippingRange = ({near}, {far})
            token projection = "perspective"
            double3 xformOp:translate = (0, 15, 40)
            uniform token[] xformOpOrder = ["xformOp:translate"]
        }}
    }}

    def Xform "VariantAsset" (
        variants = {{ string lod = "{selection}" }}
        prepend variantSets = "lod"
    )
    {{
        variantSet "lod" = {{
            "low" {{
                int userProperties:resolution = 1
            }}
            "high" {{
                int userProperties:resolution = 4
            }}
        }}
    }}

    def Xform "ReferencedAsset" (
        prepend references = @{reference}@</Asset>
    )
    {{
    }}

    def Scope "Sets" (
        prepend apiSchemas = ["CollectionAPI:renderable"]
    )
    {{
        rel collection:renderable:includes = [</World/Geometry>]
        rel collection:renderable:excludes = [</World/Geometry/Mesh_0007>]
        uniform token collection:renderable:expansionRule = "expandPrims"
        bool collection:renderable:includeRoot = false
        rel userProperties:importantTargets = [</World/Geometry/Mesh_0000>, </World/Lights/KeyLight>]
    }}

'''


def rig_block(bad=False):
    indices = "[(0,1,2,3), (0,1,2,3), (0,1,2,3), (99,1,2,3)]" if bad else "[(0,1,2,3), (0,1,2,3), (0,1,2,3), (0,1,2,3)]"
    return f'''    def Scope "Rig"
    {{
        def Skeleton "Skeleton"
        {{
            uniform token[] joints = ["Root", "Root/Spine", "Root/Spine/Head", "Root/Arm"]
            matrix4d[] bindTransforms = [
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)),
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,1,0,1)),
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,2,0,1)),
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(1,1,0,1))
            ]
            matrix4d[] restTransforms = [
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)),
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,1,0,1)),
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,1,0,1)),
                ((1,0,0,0),(0,1,0,0),(0,0,1,0),(1,0,0,1))
            ]
        }}
        def Mesh "SkinnedMesh" (
            prepend apiSchemas = ["SkelBindingAPI"]
        )
        {{
            point3f[] points = [(-1,0,0), (1,0,0), (1,2,0), (-1,2,0)]
            int[] faceVertexCounts = [4]
            int[] faceVertexIndices = [0,1,2,3]
            int4[] primvars:skel:jointIndices = {indices} (
                elementSize = 4
                interpolation = "vertex"
            )
            float4[] primvars:skel:jointWeights = [(1,0,0,0), (0.5,0.5,0,0), (0,1,0,0), (0,0.5,0.5,0)] (
                elementSize = 4
                interpolation = "vertex"
            )
            rel skel:skeleton = </World/Rig/Skeleton>
        }}
        def BlendShape "Smile"
        {{
            vector3f[] offsets = [(0,0.1,0), (0,0.2,0)]
            int[] pointIndices = [2,3]
        }}
    }}

    def Xform "AnimatedProp"
    {{
        double3 xformOp:translate.timeSamples = {{
            1: (0,0,0), 24: (2,0,0), 48: (4,0,0), 72: (6,0,0), 96: (8,0,0)
        }}
        uniform token[] xformOpOrder = ["xformOp:translate"]
    }}

'''


def geometry_scope(rng, bad=False, mesh_count=72):
    mistakes = {
        3: "topology", 7: "indices", 11: "normals", 15: "uv_indices",
        19: "negative_scale", 23: "orientation", 27: "subdivision",
        31: "extent", 35: "missing_material", 39: "invisible",
    }
    blocks = ['    def Scope "Geometry"\n    {\n']
    for index in range(mesh_count):
        blocks.append(mesh_block(index, rng, mistakes.get(index) if bad else None))
    blocks.append("    }\n\n")
    return "".join(blocks)


def filler_scope(rng, count=160):
    departments = ("model", "lookdev", "layout", "animation")
    blocks = ['    def Scope "MetadataFixtures"\n    {\n']
    for index in range(count):
        x, y, z = vec3(rng, 1.0)
        blocks.append(f'''        def Xform "Item_{index:04d}"
        {{
            string userProperties:department = "{rng.choice(departments)}"
            int userProperties:revision = {rng.randint(1, 25)}
            bool userProperties:approved = {str(rng.random() > 0.15).lower()}
            color3f userProperties:displayColor = ({abs(x):.4f}, {abs(y):.4f}, {abs(z):.4f})
        }}

''')
    blocks.append("    }\n")
    return "".join(blocks)


def build_fixture(seed, bad=False):
    rng = random.Random(seed)
    return "".join([
        HEADER,
        'def Xform "World"\n{\n',
        material_blocks(bad),
        scene_domains(bad),
        rig_block(bad),
        geometry_scope(rng, bad),
        filler_scope(rng),
        "}\n",
    ])


def support_asset():
    return '''#usda 1.0
(
    defaultPrim = "Asset"
    upAxis = "Y"
)

def Xform "Asset"
{
    def Cube "Proxy"
    {
        double size = 2
    }
}
'''


def write_suite(output_dir, seed):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "assets").mkdir(exist_ok=True)
    (output_dir / "textures").mkdir(exist_ok=True)
    (output_dir / "renders").mkdir(exist_ok=True)
    (output_dir / "assets" / "referenced_asset.usda").write_text(support_asset(), encoding="utf-8")

    files = {
        "fixture_validish.usda": build_fixture(seed),
        "fixture_kitchen_sink_invalid.usda": build_fixture(seed + 1, bad=True),
        "fixture_variant_a.usda": build_fixture(seed + 2),
        "fixture_variant_b.usda": build_fixture(seed + 3, bad=True),
    }
    for name, content in files.items():
        path = output_dir / name
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path} ({content.count(chr(10)):,} lines)")

    (output_dir / "README.txt").write_text(
        "Generated deterministic USD validator fixtures.\n\n"
        "fixture_validish.usda: broad mostly-valid coverage.\n"
        "fixture_kitchen_sink_invalid.usda: curated parseable semantic mistakes.\n"
        "fixture_variant_a.usda and fixture_variant_b.usda: comparison pair.\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description="Generate large deterministic USDA validator fixtures.")
    parser.add_argument("--output", type=Path, default=Path.home() / "Documents" / "USDvalidator_fixtures")
    parser.add_argument("--seed", type=int, default=8675309)
    args = parser.parse_args()
    write_suite(args.output.expanduser().resolve(), args.seed)


if __name__ == "__main__":
    main()
