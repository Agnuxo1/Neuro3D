# Point 4 preregistered integration plan
Date: 2026-10-06. Parent revision: 8f9a54cb118043ff47d1b09b64e214fa2a676a6f.

## Claim to test

A saved and reopened Blender scene can supply a typed, exact hi/lo32 geometry and source-query packet to a native GPU consumer. The consumer must preserve its integer words and identities and use the limbs in compensated coordinate differences and direction interval widths.

This is a diagnostic integration of real scene data with a new native consumer. The legacy full optical propagator, first-hit predicates and physical phase bounds are not upgraded by this test. Frozen CPU receipts keep their original scope and zero native joins.

## Data and arithmetic contract

Use the existing evaluated-scene exporter and pure rational scalar codec without changing frozen implementations. Fix a little-endian uint32 ABI with bounded header, scalar, source, vertex and triangle tables. Keep original object, face, triangle and source identities. Initial sources have the explicit previous-primitive sentinel 0xffffffff.

The arithmetic domain comprises observed geometric coordinates, source origins, raw directions and declared direction endpoints. Source amplitudes and wavelength may be transported if admitted exactly, but this pilot does not calculate optical propagation from them. Preserve the complete unmodified optical snapshot in the trusted manifest. Phase and material propagation require their own representation and error contract.

This scope matters for the existing K3/K4 scenes: their phase parameters include 0.2, whose observed binary64 value leaves the exact residual 1/2^54 after the two binary32 limbs. Do not round those parameters to claim exact admission, and do not mistake a geometry/query transport result for a phase transport result.

For every admitted hi/lo32 scalar, retain the exact input rational, the two words and exact residual. Nonzero residual, unsupported subnormal, nonfinite value, prohibited negative zero, malformed metadata, identity or layout must stop admission before upload.

Record the actual blend hash, scene and view layer, evaluated snapshot, extraction code, source properties, table order and complete wire bytes. No CPU-generated hits, paths or solved intersection parameters enter the native input.

## Experiments and rejection criteria

1. Reopen the actual retained K3/K4 scenes and preserve their complete snapshots and identities.
2. Save and reopen a separately identified controlled scene with source values such as 1 + 2^-30 and 2^-60 and explicit non-singleton direction endpoints. These are declared test inputs, not recovered mesh precision.
3. Upload through integer GPU storage and verify all returned input words bit for bit.
4. Compute source-to-vertex differences, triangle edges and direction endpoint widths from the native limbs. Return explicitly typed pair64 values instead of one collapsed double.
5. Compare every admitted result with an independent exact Fraction calculation. A derived result such as 1 - 2^-60 must retain the small term.
6. Discard input low words deliberately and collapse compensated outputs deliberately. Both controls must expose the expected numerical differences.
7. Reject truncated or extended buffers, invalid counts/strides/offsets, swapped endpoints/identities, changed endianness and coherent metadata/hash mutations against a separately fixed trusted manifest.
8. Verify memory visibility and synchronized readback. Preserve setup/upload, combined dispatch/synchronization/readback and CPU audit timings with their actual scope.
9. Preserve failing receipts. No tolerance may be widened in response to a failed result.

## Execution dependency

Use a new launcher with a real gpuq lease and a UUID-bound fresh resource snapshot. Create the owned Blender child suspended, assign it to a private Windows Job Object before resuming, and verify closure.

Default budgets are 2 GiB RAM and 2 GiB GPU memory. Admission requires at least 4 GiB host free memory after the budget, global GPU use plus budget no greater than 18 GiB, and temperature no greater than 80 C. Bound work to 100 s and closure to 10 s. Failed telemetry, lost lease, resource excess, stale output, invalid report, nonzero exit or unconfirmed cleanup prevents PASS.

Validate the guard's failure behavior with bounded CPU processes before starting GPU work. The owned Blender process uses factory settings, one CPU thread, disabled auto-execution, OpenGL and a timer-based private shutdown. It does not save user preferences.

## Primary references and implications

- Blender 4.5 GPU API: https://docs.blender.org/api/4.5/gpu.types.html
  The documented integer texture formats support an explicit word-oriented transport. Actual runtime capabilities and the synchronization implementation must still be checked.
- Khronos GLSL 4.60, sections 4.7.1 and 4.9: https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html
  The precise qualifier controls operation ordering and consistency; it does not establish a universal IEEE round-to-nearest proof. Subnormal behavior and the language's allowed arithmetic accuracy prevent extrapolating one device result to all backends.
- Khronos memory model: https://wikis.khronos.org/opengl/Incoherent_Memory_Access
  Shader image writes need the appropriate visibility barrier before texture readback. Verify the Blender implementation or use a documented explicit barrier.
- Ogita, Rump and Oishi, Accurate Sum and Dot Product, SIAM J. Sci. Comput. 26(6), 1955-1988, DOI 10.1137/030601818: https://ogilab.w.waseda.jp/ogita/math/doc/2005_OgRuOi.pdf
  Sections 2-3 state the arithmetic assumptions and describe TwoSum and error-free transformations. The pilot checks exact finite cases under its observed native implementation; it does not claim that the paper's assumptions hold universally for GLSL.

## Closure

Require a pinned source revision, retained CPU and native reports, all declared gates passing, cleanup confirmed, an independent internal review and an updated project status. First-hit robustness, full phase/error bounds, full trained-network execution and general GPU supervision remain separate roadmap work.

Pre-execution adversarial case: the controlled source named low has a declared y-direction interval [2^-60 + 2^-100, 1 + 2^-30], containing its raw direction 1. Its width tests preservation of four terms in a pair64 result. This deliberately broad numerical box is not a physical uncertainty estimate. The other controlled source retains the narrow x-direction interval around 1 + 2^-30 with half-width 2^-50.

## Native storage correction before the first GPU execution
The first texture-based draft was rejected by source inspection, without any native execution. In the installed Blender build 62c1db4208e8, GPUTexture construction with initial data accepts only a FLOAT buffer, and the RGBA32UI texture read path selects FLOAT. Neither path supplies the required bit-preserving word transport.

The admitted candidate instead uses the public GPUUniformBuf byte-buffer constructor and a std140 array of uvec4, with a fixed 32768-byte allocation. The original little-endian packet bytes are followed by zero padding; all inputs must fit 8192 uint32 words. Query GL_MAX_UNIFORM_BLOCK_SIZE and reject a device below 32768 bytes before compilation.

Outputs use R32UI textures because this exact Blender source selects GPU_DATA_UINT for their readback. Each texel stores one uint32; rows have 64 texels. New output storage is initialized to poison 0x5A5A5A5A, every logical word must be written, and physical padding must remain poison. A unique dispatch nonce and complement identify each result. Logical packet/row ABIs and exact arithmetic gates remain unchanged.

The explicit TEXTURE_UPDATE and SHADER_IMAGE_ACCESS barrier, same-context completion fence and bounded wait remain required. Allocation/upload/binding and combined dispatch/synchronization/readback/host validation are recorded with their actual scopes.

Primary implementation sources at the installed build:
- https://raw.githubusercontent.com/blender/blender/62c1db4208e8/source/blender/python/gpu/gpu_py_uniformbuffer.cc
  SHA256 933575ea46765869a9f119c8b69b2dd89d7429aa9a4693d281f53fa1c4dad2b7.
- https://raw.githubusercontent.com/blender/blender/62c1db4208e8/source/blender/python/gpu/gpu_py_texture.cc
  SHA256 2291243286b6b386e3aaad7984a1aa9b5a91c52e1516aeb8fae7a1d97532cf81.

The original rejected draft and its rationale are retained separately. It is a pre-execution compatibility finding, not a failed GPU experiment.
