"""Installed Cycles OptiX closest-surface candidates, never optical intensities.

One tiny orthographic pixel samples an approximate ray through captured meshes.
Object/face IDs and projected position are encoded by an emission material and
read from a lossless float32 EXR. Every candidate needs independent exact
represented-ray admission before it can enter coherent optical computation.
"""
import math,time
from pathlib import Path
from Blender.blender_lab.native_graphics_geometry_v1 import pack_queries

class NativeCyclesOptixCandidates:
    execution_kind='GPU_OPTIX'

    def __init__(self,scene,*,out,pixel_BU,far_BU):
        import bpy
        start=time.perf_counter();self.out=Path(out);self.out.mkdir(exist_ok=False)
        self.names=list(scene['objects']);self.objects={};self.query_index=0
        self.pixel_BU=pixel_BU;self.far_BU=far_BU
        preferences=bpy.context.preferences.addons['cycles'].preferences
        preferences.compute_device_type='OPTIX';preferences.get_devices()
        devices=[{'name':d.name,'type':d.type,'id':d.id} for d in preferences.devices]
        selected=[d for d in preferences.devices if d.type=='OPTIX' and d.name=='NVIDIA GeForce RTX 3090']
        if len(selected)!=1:raise ValueError('Actual single RTX3090 OptiX device required; no CPU fallback')
        for d in preferences.devices:d.use=d==selected[0]
        self.device_inventory=devices;self.selected_device={'name':selected[0].name,'type':selected[0].type,'id':selected[0].id}
        self.render_scene=bpy.data.scenes.new('OpticNeuroBlender_owned_OptiX_candidates')
        s=self.render_scene;s.render.engine='CYCLES';s.cycles.device='GPU';s.cycles.samples=1
        s.cycles.use_adaptive_sampling=False;s.cycles.use_denoising=False
        s.cycles.max_bounces=0;s.cycles.use_light_tree=False;s.cycles.seed=0
        s.render.resolution_x=1;s.render.resolution_y=1;s.render.resolution_percentage=100
        s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='32';s.render.image_settings.exr_codec='ZIP'
        s.render.film_transparent=True;s.render.use_persistent_data=True
        s.view_settings.view_transform='Raw';s.view_settings.exposure=0.;s.view_settings.gamma=1.
        world=bpy.data.worlds.new('OpticNeuroBlender_owned_black');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(0,0,0,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=0;s.world=world
        camera=bpy.data.cameras.new('OpticNeuroBlender_owned_probe_camera');camera.type='ORTHO';camera.ortho_scale=pixel_BU;camera.clip_start=1e-6;camera.clip_end=far_BU
        self.camera=bpy.data.objects.new(camera.name,camera);s.collection.objects.link(self.camera);s.camera=self.camera
        self.origin_nodes=[];self.direction_nodes=[];offset=0
        for index,name in enumerate(self.names):
            geometry=scene['objects'][name];vertices=[tuple(float(v) for v in p) for p in geometry['vertices_world_BU']];faces=geometry['faces']
            if not faces or not all(len(f)==3 and len(set(f))==3 for f in faces) or not all(math.isfinite(v) for p in vertices for v in p):raise ValueError('Finite explicit captured triangles required')
            mesh=bpy.data.meshes.new('OptiX_payload_'+name);mesh.from_pydata(vertices,[],faces);mesh.update()
            primitive=mesh.attributes.new('optic_global_primitive','FLOAT','FACE')
            for j,value in enumerate(primitive.data):value.value=float(offset+j+1)
            offset+=len(faces)
            obj=bpy.data.objects.new('OptiX_payload_'+name,mesh);s.collection.objects.link(obj);self.objects[name]=obj
            material=bpy.data.materials.new('OptiX_payload_ids_'+name);material.use_nodes=True
            nodes=material.node_tree.nodes;links=material.node_tree.links;nodes.clear()
            output=nodes.new('ShaderNodeOutputMaterial');emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1.
            combine=nodes.new('ShaderNodeCombineXYZ');combine.inputs['X'].default_value=float(index+1)
            attribute=nodes.new('ShaderNodeAttribute');attribute.attribute_name='optic_global_primitive';links.new(attribute.outputs['Fac'],combine.inputs['Y'])
            geometry_node=nodes.new('ShaderNodeNewGeometry');subtract=nodes.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT'
            projection=nodes.new('ShaderNodeVectorMath');projection.operation='DOT_PRODUCT'
            links.new(geometry_node.outputs['Position'],subtract.inputs[0]);links.new(subtract.outputs['Vector'],projection.inputs[0]);links.new(projection.outputs['Value'],combine.inputs['Z'])
            links.new(combine.outputs['Vector'],emission.inputs['Color']);links.new(emission.outputs['Emission'],output.inputs['Surface'])
            self.origin_nodes.append(subtract);self.direction_nodes.append(projection);mesh.materials.append(material)
        if not 1<=offset<=100000:raise ValueError('Bounded captured triangle count required')
        self.triangle_count=offset;self.compile_pack_upload_seconds=time.perf_counter()-start

    def query(self,queries):
        import bpy
        from mathutils import Vector
        start=time.perf_counter();pack_queries(queries,self.names);rows=[];times=[]
        for q in queries:
            origin=tuple(float(v) for v in q['origin']);direction=Vector(tuple(float(v) for v in q['direction']));direction.normalize()
            self.camera.location=origin;self.camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
            for name,obj in self.objects.items():obj.hide_render=name==q['previous_name']
            for node in self.origin_nodes:node.inputs[1].default_value=origin
            for node in self.direction_nodes:node.inputs[1].default_value=direction
            path=self.out/('candidate_'+str(self.query_index)+'.exr');self.query_index+=1
            self.render_scene.render.filepath=str(path);t=time.perf_counter()
            bpy.ops.render.render(write_still=True,scene=self.render_scene.name)
            image=bpy.data.images.load(str(path),check_existing=False)
            try:
                image.colorspace_settings.name='Non-Color';rgba=list(image.pixels[:])
            finally:bpy.data.images.remove(image)
            elapsed=time.perf_counter()-t;times.append(elapsed)
            if len(rgba)!=4 or not all(math.isfinite(v) for v in rgba):raise ValueError('Complete finite lossless EXR pixel required')
            obj,primitive,distance,alpha=rgba
            if alpha==0:rows.append({'status':'MISS','raw_rgba':rgba});continue
            if alpha!=1 or obj!=int(obj) or primitive!=int(primitive) or not 1<=obj<=len(self.names) or not 1<=primitive<=self.triangle_count or not 0<distance<self.far_BU:raise ValueError('Malformed native OptiX candidate pixel')
            rows.append({'status':'GRAPHICS_SURFACE_CANDIDATE','object':self.names[int(obj)-1],'primitive_id':int(primitive)-1,'distance_BU':distance,'raw_rgba':rgba})
        return {'rows':rows,'query_seconds':time.perf_counter()-start,'individual_render_seconds':times,'execution_kind':self.execution_kind,'pixel_aperture_BU':self.pixel_BU,'candidate_only':True}
