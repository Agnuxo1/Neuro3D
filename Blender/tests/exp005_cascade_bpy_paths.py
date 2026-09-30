"""Bounded v2 traversal: real bpy hits, normal-scale-invariant reflection.

Does not query the triangle oracle or infer a desired object/axis from IDs.
"""
import json
from exp005_reflection import reflect_direction


def raycast_paths(scene):
    import bpy
    from mathutils import Vector
    bpy.context.view_layer.update()
    graph=bpy.context.evaluated_depsgraph_get()
    paths=[]; rays=0
    for source in json.loads(scene['optical_sources']):
        initial=complex(*source['field_reim'])
        if initial==0: continue
        stack=[(Vector(source['position_BU']),Vector(source['direction']).normalized(),[])]
        while stack:
            origin,direction,history=stack.pop(); rays+=1
            if rays>4096 or len(history)>=64: raise ValueError('bounded cascade exceeded')
            found,point,normal,face,obj,_=scene.ray_cast(graph,origin+direction*1e-6,direction)
            if not found: raise ValueError('lost Blender ray')
            hit={'object_id':obj.name,'distance_BU':(point-origin).length,'face_index':face,
                 'point_BU':list(point),'incoming_direction':list(direction),'normal':list(normal)}
            kind=obj['kind']
            if kind in ('det','escape'):
                axis=Vector(obj['mode_direction']).normalized()
                if direction.dot(axis)<1-1e-6: raise ValueError('terminal mode mismatch')
                hit['event']='detect' if kind=='det' else 'escape'
                paths.append({'source_id':source['id'],'initial_field':initial,'hits':history+[hit],
                              'reference_offset_BU':direction.dot(Vector(obj['mode_origin_BU'])-point)})
                continue
            if kind not in ('bs','mirror'): raise ValueError('unknown optical kind')
            reflected=Vector(reflect_direction(direction,normal))
            events=[('mirror',reflected)] if kind=='mirror' else [('t',direction),('r',reflected)]
            for event,ray in events: stack.append((point,ray,history+[dict(hit,event=event)]))
    return paths,rays
