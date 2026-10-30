# Licensed and private content check

Complete this for every `<tool>-job` repo before its first image is pushed, and again
when the method, its dependencies or its model weights change. Record the answers in the
tool's PR. Repos and ghcr packages are public unless this check says otherwise.

- [x] **Method code license.** MIT ([le-yuan/EZKinetics](https://github.com/le-yuan/EZKinetics),
      public). Redistribution in a public image is permitted. SPDX: `MIT`.
- [x] **Model weights and data.** EZKinetics' trained XGBoost models and scalers are in the
      public upstream repo (MIT) and in the base image. ESM2-3B and ESM2-650M (MIT, via
      fair-esm) and DeepChem/ChemBERTa-77M-MTR (Hugging Face, not gated, no license
      declared) download at runtime and are not in the image.
- [x] **Commercial toolkits.** None.
- [x] **Secrets.** None in the repo or the image.
- [x] **Unpublished work.** The paper is under consideration, but the code, models and
      training data are already public upstream, so nothing here is under embargo.

If every answer is clear: the repo and package stay public.

If anything is restricted: make the repo and/or ghcr package private, keep the
restricted content out of the image where possible (download at runtime with a mounted
secret), and note that the backend needs an image pull secret for this tool.
