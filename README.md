# anatomix-t1w-dwi-registration

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Registers a DWI series to a T1-weighted image by aligning its mean b0 with anatomix deep features and FireANTs deformable registration, outputting the registered b0 and an ANTs-convention warp.**

Averages the DWI volumes at or below b0_max_bval into a b0 image, registers it onto the T1w with anatomix-register.py (modality-agnostic anatomix features driving FireANTs, affine then deformable by default) and writes the resampled b0 plus the forward and optional inverse displacement fields in ITK/ANTs convention. Use the warp to bring FA/MD or other DWI-space maps into T1w space, or the inverse to bring T1w-space parcellations into DWI space. A GPU is strongly recommended; the transform must end in a deformable stage.

| | |
|---|---|
| 📥 **Inputs** | `neuro/anat/t1w` · `neuro/dwi` |
| 📤 **Outputs** | `neuro/dwi/b0` · `neuro/transform/nifti` |
| 🐳 **Container** | `gamorosino/anatomix-fireants:latest` |
| ⚙️ **Resources** | 32 GB memory · 4 h walltime · GPU |
| 🔗 **Run it** | [doi.org/10.25663/brainlife.app.972](https://doi.org/10.25663/brainlife.app.972) |

#### 📥 Inputs

| Input | Datatype | Required | Description |
|---|---|---|---|
| `t1` | `neuro/anat/t1w` | yes | T1-weighted anatomical image used as the fixed image. |
| `dwi` | `neuro/dwi` | yes | DWI series with bvals and bvecs; its mean b0 is the moving image. At least one volume with b-value at or below b0_max_bval. |

#### 📤 Outputs

| Output | Datatype | Description |
|---|---|---|
| `b0_reg` | `neuro/dwi/b0` | Mean b0 volume extracted from the DWI series, registered (resampled) onto the T1w grid. |
| `warp` | `neuro/transform/nifti` | FireANTs transform (ITK/ANTs LPS-mm displacement field convention, not FSL) that resamples the DWI/b0 (moving) image onto T1w (fixed) space -- apply it to other DWI-space volumes (e.g. FA, MD maps) to bring them into T1w space. With save_inverse enabled, inverse-warp.nii.gz does the reverse (T1w -> native DWI space). |

<details>
<summary><b>⚙️ Parameters</b> (4)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `b0_max_bval` | number | `50` | b-value (s/mm^2) at or below which a DWI volume is treated as a b0 and averaged to build the moving image. |
| `transform` | string | `affine,deformable` | Comma-separated registration stages, in order, from rigid/affine/deformable (see anatomix-register.py --help). Must end in a deformable stage: this app's warp output is a NIfTI displacement field, which anatomix-register.py only writes when the last stage is deformable. affine,deformable handles gross T1w/DWI misalignment plus local distortion; use deformable alone if the images are already roughly aligned. |
| `save_inverse` | boolean | `true` | Also compute the moving-to-fixed (DWI/b0 -> T1w) inverse transform, e.g. to bring a T1w-space parcellation into native DWI space for tractography ROIs. |
| `device` | string | `auto` | Compute device for FireANTs: auto, cpu, cuda, or cuda:N. |

</details>

<!-- brainlife-app:end -->

Registers a DWI series onto a T1w anatomical image with anatomix (modality-agnostic deep features) + FireANTs (GPU-accelerated diffeomorphic registration). The b0 volume is extracted internally from the DWI series (mean of low-b volumes) and used as the moving image; the T1w image is the fixed/reference space.

## Inputs

- `t1` (neuro/anat/t1w)
- `dwi` (neuro/dwi)

## Outputs

- `b0_reg` (neuro/dwi/b0) -- Mean b0 volume extracted from the DWI series, registered (resampled) onto the T1w grid.
- `warp` (neuro/transform/nifti) -- FireANTs transform (ITK/ANTs LPS-mm displacement field convention, not FSL) that resamples the DWI/b0 (moving) image onto T1w (fixed) space -- apply it to other DWI-space volumes (e.g. FA, MD maps) to bring them into T1w space. With save_inverse enabled, inverse-warp.nii.gz does the reverse (T1w -> native DWI space).

## Usage

Brainlife.io: run via `braise-app-run`/`braise-app-pipeline` (once registered
with `braise-app-create`), or the web UI.

Locally (outside brainlife): copy `config.json.example` to `config.json`,
fill in real file paths, then run `./main` from this directory. `main` pulls
its own container (`singularity exec docker://...`) -- no local install of
the underlying tool needed, only Singularity itself.

**GPU strongly recommended.** The container has no fused CUDA kernels built,
so FireANTs runs its pure-PyTorch path everywhere -- correct on CPU, but
registration is slow without a GPU. `main` requests one Slurm GPU and passes
`--nv` to singularity; adjust for other schedulers.

Entrypoint: `main.py`

## Credits

Registration is performed by
[anatomix](https://github.com/neel-dey/anatomix) +
[FireANTs](https://github.com/rohitrango/FireANTs) (via
[this fork](https://github.com/neel-dey/FireANTs)). See anatomix's own
[registration README](https://github.com/neel-dey/anatomix/blob/main/anatomix/registration/README.md)
for the underlying method and citations.

## Authors

- Gabriele Amorosino <ga24643@eid.utexas.edu>

## License

MIT, see `LICENSE`. anatomix and FireANTs have their own separate licenses.
