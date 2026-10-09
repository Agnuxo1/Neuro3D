"""Native Blender CPU BVHs: an equivalent 3D geometry candidate baseline.

Float32 BVH hits are candidates only. The shared independent exact verifier
must admit them before optical propagation. No expected hits enter this API.
"""
import math, time
from Blender.blender_lab.native_graphics_geometry_v1 import pack_queries


class NativeBVHCandidates:
    execution_kind = 'CPU_BVH'

    def __init__(self, scene, *, far_BU):
        from mathutils.bvhtree import BVHTree
        start = time.perf_counter()
        self.names = list(scene['objects']); self.far_BU = far_BU
        self.trees = []; offset = 0
        for name in self.names:
            obj = scene['objects'][name]
            vertices = [tuple(float(v) for v in p) for p in obj['vertices_world_BU']]
            faces = obj['faces']
            if not all(len(f)==3 and len(set(f))==3 for f in faces):
                raise ValueError('Explicit nondegenerate triangle indices required')
            if not all(math.isfinite(v) for p in vertices for v in p):
                raise ValueError('Finite evaluated vertices required')
            tree = BVHTree.FromPolygons(vertices, faces, all_triangles=True, epsilon=0.0)
            self.trees.append((name, tree, offset, len(faces)))
            offset += len(faces)
        if not 1 <= offset <= 100000:
            raise ValueError('Bounded explicit triangle count required')
        self.triangle_count = offset
        self.compile_pack_upload_seconds = time.perf_counter()-start

    def query(self, queries):
        from mathutils import Vector
        start = time.perf_counter(); pack_queries(queries, self.names)
        rows = []
        for q in queries:
            origin = Vector(tuple(float(v) for v in q['origin']))
            direction = Vector(tuple(float(v) for v in q['direction'])); direction.normalize()
            nearest = None
            for name, tree, offset, count in self.trees:
                # Same exact zero-plane precondition as the graphics builder.
                # No positive-distance epsilon or energy pruning.
                if name == q['previous_name']: continue
                location, normal, face, distance = tree.ray_cast(origin, direction, self.far_BU)
                if face is None: continue
                if not 0 <= face < count or not math.isfinite(distance):
                    raise ValueError('Malformed native BVH candidate')
                if nearest is None or distance < nearest['distance_BU']:
                    nearest = {'status':'GRAPHICS_SURFACE_CANDIDATE', 'object':name,
                               'primitive_id':offset+face, 'distance_BU':distance}
            rows.append(nearest if nearest is not None else {'status':'MISS'})
        return {'rows':rows, 'query_seconds':time.perf_counter()-start,
                'execution_kind':self.execution_kind}
