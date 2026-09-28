"""Write expected_values.json for EXP-001 T0-T6 (OPT-006). CPU only, deterministic."""
import json, math
from mz_oracle import (single_path_baseline, mz_closed_form, destructive_by_single_mirror,
                       delay_line_shift, gaussian_overlap, cross_term_average)

def r(x): return {k: getattr(x, k) for k in ("port_a", "port_b", "loss_arm1", "loss_arm2", "residual", "visibility")}
alpha, L = 0.05, 2.0  # proposed arm length 2 BU each, alpha as EXP-000
T = math.exp(-alpha * L)
out = {
  "convention": "U(tau)=[[sqrt(tau), i sqrt(1-tau)],[i sqrt(1-tau), sqrt(tau)]]; arm1=transmitted; port B bright when phases equal",
  "T0_baseline_single_path": single_path_baseline(),
  "T1_constructive_ideal": r(mz_closed_form()),
  "T1_constructive_lossy_alpha0.05_L2": r(mz_closed_form(t_arm1=T, t_arm2=T)),
  "T2_destructive_ideal": r(mz_closed_form(phi1=math.pi)),
  "T3_sweep_tau1_0.8_portB": [mz_closed_form(tau1=0.8, phi1=2*math.pi*k/32).port_b for k in range(32)],
  "T3_expected_visibility_tau1_0.8": 2*math.sqrt(0.8*0.2),
  "T4_incoherent_any_phase": r(mz_closed_form(gamma=0.0, phi1=1.0)),
  "T4_freq_mismatch_crossfactor_df1_Tint100": cross_term_average(0.0, 1.0, 100.0),
  "T5_broken_arm2": r(mz_closed_form(t_arm2=0.0)),
  "geometry_single_mirror_lambda1_w0.2": destructive_by_single_mirror(1.0, 45.0, 0.2),
  "geometry_single_mirror_lambda0.05_w0.2": destructive_by_single_mirror(0.05, 45.0, 0.2),
  "geometry_delay_line_lambda1": delay_line_shift(0.5),
  "max_lambda_single_mirror_overlap_0.99_w0.2": 2*0.2*math.sqrt(-2*math.log(0.99)),
}
json.dump(out, open("expected_values.json", "w"), indent=2)
print(json.dumps({k: out[k] for k in ("T1_constructive_lossy_alpha0.05_L2","geometry_single_mirror_lambda1_w0.2","geometry_single_mirror_lambda0.05_w0.2","max_lambda_single_mirror_overlap_0.99_w0.2")}, indent=1))
