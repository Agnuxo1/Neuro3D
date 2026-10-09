#!/bin/bash
# Un job gpuq por sujeto (granularidad corta: la cola FIFO se intercala con otros chats). Reanudable.
cd "$(dirname "$0")"
GPUQ="${GPUQ:-}"
for s in "$@"; do
  ${GPUQ:+python "$GPUQ" run --name "neuro3d:mi-nested-$s" --vram 2 --ram 3 --} python "$(pwd)/nested_bench.py" --grid full --tag full --dev cuda --subjects $s >> logs/full_persubject.log 2>&1
done
echo FIN_PERSUBJECT >> logs/full_persubject.log
