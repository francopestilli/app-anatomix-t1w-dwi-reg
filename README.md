# anatomix-t1w-dwi-registration

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
