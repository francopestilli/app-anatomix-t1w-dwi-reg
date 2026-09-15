#!/usr/bin/env python3
"""brainlife.io entrypoint: register a DWI series onto a T1w image.

Reads config.json directly (brainlife's app-template-python convention). The
b0 volume is extracted from the DWI series (mean of all volumes at or below
`b0_max_bval`) and registered onto the T1w image with anatomix + FireANTs
(anatomix-register.py, baked into the container at
/opt/anatomix/anatomix/registration/anatomix-register.py).
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

import nibabel as nib
import numpy as np

ANATOMIX_REGISTER = "/opt/anatomix/anatomix/registration/anatomix-register.py"


def extract_b0(dwi_path, bvals_path, max_bval, out_path):
    bvals = np.loadtxt(bvals_path).reshape(-1)
    img = nib.load(dwi_path)
    data = img.get_fdata()
    b0_idx = np.where(bvals <= max_bval)[0]
    if b0_idx.size == 0:
        sys.exit(f"no volumes with b-value <= {max_bval} found in {bvals_path}")
    b0_mean = data[..., b0_idx].mean(axis=-1).astype(np.float32)
    nib.save(nib.Nifti1Image(b0_mean, img.affine, img.header), out_path)
    return b0_idx.size


def write_degenerate_bval_bvec(bvals_out, bvecs_out):
    # b0_reg is a single averaged volume, not a real diffusion series, but its
    # datatype (neuro/dwi/b0) still requires bvals/bvecs files to exist.
    with open(bvals_out, "w") as f:
        f.write("0\n")
    with open(bvecs_out, "w") as f:
        f.write("0\n0\n0\n")


def main():
    with open("config.json") as f:
        config = json.load(f)

    t1 = config["t1"]
    dwi = config["dwi"]
    bvals_path = config["bvals"]
    max_bval = float(config.get("b0_max_bval", 50))
    transform = config.get("transform", "affine,deformable")
    save_inverse = bool(config.get("save_inverse", True))
    device = config.get("device", "auto")

    os.makedirs("out_dir", exist_ok=True)
    os.makedirs("b0_reg", exist_ok=True)
    os.makedirs("warp", exist_ok=True)

    b0_path = os.path.join("out_dir", "b0.nii.gz")
    n_b0 = extract_b0(dwi, bvals_path, max_bval, b0_path)
    print(f"extracted b0 from {n_b0} volume(s) (b <= {max_bval})", flush=True)

    cmd = [
        "python3", ANATOMIX_REGISTER,
        "--fixed", t1,
        "--moving", b0_path,
        "--transform", transform,
        "--initialization", "center-of-mass",
        "--output-dir", "out_dir",
        "--exp-name", "reg",
        "--output-transformation-convention", "ants",
        "--device", device,
    ]
    if save_inverse:
        cmd.append("--save-inverse")

    print("+ " + " ".join(shlex.quote(c) for c in cmd), flush=True)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)

    moved = os.path.join("out_dir", "reg-moved-b0.nii.gz")
    if not os.path.isfile(moved):
        sys.exit(f"expected registered image not found: {moved}")
    shutil.copy(moved, os.path.join("b0_reg", "dwi.nii.gz"))
    write_degenerate_bval_bvec(
        os.path.join("b0_reg", "dwi.bvals"), os.path.join("b0_reg", "dwi.bvecs")
    )

    warp = os.path.join("out_dir", "reg-warp-b0.nii.gz")
    if not os.path.isfile(warp):
        sys.exit(
            f"expected warp not found: {warp} -- `transform` must end in a "
            "deformable stage (e.g. affine,deformable), otherwise "
            "anatomix-register.py writes a linear .mat instead of a NIfTI "
            "displacement field"
        )
    shutil.copy(warp, os.path.join("warp", "warp.nii.gz"))

    if save_inverse:
        inverse_warp = os.path.join("out_dir", "reg-inverse-warp-b0.nii.gz")
        if os.path.isfile(inverse_warp):
            shutil.copy(inverse_warp, os.path.join("warp", "inverse-warp.nii.gz"))

    with open("product.json", "w") as f:
        json.dump({"tags": ["anatomix", "fireants", "t1w-dwi-registration"]}, f)


if __name__ == "__main__":
    main()
