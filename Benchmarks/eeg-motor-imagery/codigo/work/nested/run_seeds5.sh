#!/bin/bash
cd "$(dirname "$0")"
GPUQ="${GPUQ:-}"
for s in S001 S002 S003 S004 S005 S006 S007 S009 S010 S011 S012 S014 S016 S017 S018 S019 S020; do
  ${GPUQ:+python "$GPUQ" run --name "neuro3d:mi-seeds5-$s" --vram 2 --ram 3 --} python "$(pwd)/nested_bench.py" --grid finalists --tag seeds5 --seeds 5 --no-inner --dev cuda --subjects $s >> logs/seeds5.log 2>&1
done
echo FIN_SEEDS5 >> logs/seeds5.log
