# Uni-Mol Tools

<img src = "https://bohrium.oss-cn-zhangjiakou.aliyuncs.com/article/16664/d50607556c5c4076bf3df363a7f1aedf/4feaf601-09b6-4bcb-85a0-70890c36c444.png" width = 40%>

[![GitHub release](https://img.shields.io/github/release/deepmodeling/unimol_tools.svg)](https://github.com/deepmodeling/unimol_tools/releases/)
[![PyPI version](https://img.shields.io/pypi/v/unimol-tools.svg)](https://pypi.org/project/unimol-tools/)
![Python versions](https://img.shields.io/pypi/pyversions/unimol-tools.svg)
[![License](https://img.shields.io/github/license/deepmodeling/unimol_tools.svg)](https://github.com/deepmodeling/unimol_tools/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/deepmodeling/unimol_tools.svg)](https://github.com/deepmodeling/unimol_tools/issues)
[![GitHub contributors](https://img.shields.io/github/contributors/deepmodeling/unimol_tools.svg)](https://github.com/deepmodeling/unimol_tools/graphs/contributors)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-blue.svg)
[![Documentation Status](https://readthedocs.org/projects/unimol/badge/?version=latest)](https://unimol.readthedocs.io/en/latest/?badge=latest)

Unimol_tools is a easy-use wrappers for property prediction,representation and downstreams with Uni-Mol.

# Uni-Mol tools for various prediction and downstreams.

📖 Documentation: [unimol-tools.readthedocs.io](https://unimol-tools.readthedocs.io/en/latest/)

## Install
- pytorch is required, please install pytorch according to your environment. if you are using cuda, please install pytorch with cuda. More details can be found at https://pytorch.org/get-started/locally/
- currently, rdkit needs with numpy<2.0.0, please install rdkit with numpy<2.0.0.

### Option 1: Installing from PyPi (Recommended, for stable version)

```bash
pip install unimol_tools --upgrade
```

We recommend installing ```huggingface_hub``` so that the required unimol models can be automatically downloaded at runtime! It can be install by

```bash
pip install huggingface_hub
```

`huggingface_hub` allows you to easily download and manage models from the Hugging Face Hub, which is key for using Uni-Mol models.

### Option 2: Installing from source (for latest version)

```python
## Dependencies installation
pip install -r requirements.txt

## Clone repository
git clone https://github.com/deepmodeling/unimol_tools.git
cd unimol_tools

## Install
python setup.py install
```

### Models in Huggingface

The UniMol pretrained models can be found at [dptech/Uni-Mol-Models](https://huggingface.co/dptech/Uni-Mol-Models/tree/main).

If the download is slow, you can use other mirrors, such as:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Setting the `HF_ENDPOINT` environment variable specifies the mirror address for the Hugging Face Hub to use when downloading models.

### Modify the default directory for weights

Setting the `UNIMOL_WEIGHT_DIR` environment variable specifies the directory for pre-trained weights if the weights have been downloaded from another source.

```bash
export UNIMOL_WEIGHT_DIR=/path/to/your/weights/dir/
```

## News
- 2025-05-26: Unimol_tools is now independent from the Uni-Mol repository!
- 2025-03-28: Unimol_tools now support Distributed Data Parallel (DDP)!
- 2024-11-22: Unimol V2 has been added to Unimol_tools!
- 2024-07-23: User experience improvements: Add `UNIMOL_WEIGHT_DIR`.
- 2024-06-25: unimol_tools has been publish to pypi! Huggingface has been used to manage the pretrain models.
- 2024-06-20: unimol_tools v0.1.0 released, we remove the dependency of Uni-Core. And we will publish to pypi soon.
- 2024-03-20: unimol_tools documents is available at https://unimol-tools.readthedocs.io/en/latest/

## Examples
### Molecule property prediction
```python
from unimol_tools import MolTrain, MolPredict
clf = MolTrain(task='classification', 
                data_type='molecule', 
                epochs=10, 
                batch_size=16, 
                metrics='auc',
                )
pred = clf.fit(data = data)
# currently support data with smiles based csv/txt file, and
# custom dict of {'atoms':[['C','C],['C','H','O']], 'coordinates':[coordinates_1,coordinates_2]}

clf = MolPredict(load_model='../exp')
res = clf.predict(data = data)
```
### Molecule representation
```python
import numpy as np
from unimol_tools import UniMolRepr
# single smiles unimol representation
clf = UniMolRepr(data_type='molecule', remove_hs=False)
smiles = 'c1ccc(cc1)C2=NCC(=O)Nc3c2cc(cc3)[N+](=O)[O]'
smiles_list = [smiles]
unimol_repr = clf.get_repr(smiles_list, return_atomic_reprs=True)
# CLS token repr
print(np.array(unimol_repr['cls_repr']).shape)
# atomic level repr, align with rdkit mol.GetAtoms()
print(np.array(unimol_repr['atomic_reprs']).shape)
```

## Credits
We thanks all contributors from the community for their suggestions, bug reports and chemistry advices. Currently unimol-tools is maintained by Yaning Cui, Xiaohong Ji, Zhifeng Gao from DP Technology and AI for Science Insitution, Beijing.

Please kindly cite our papers if you use this tools.
```

@article{gao2023uni,
  title={Uni-qsar: an auto-ml tool for molecular property prediction},
  author={Gao, Zhifeng and Ji, Xiaohong and Zhao, Guojiang and Wang, Hongshuai and Zheng, Hang and Ke, Guolin and Zhang, Linfeng},
  journal={arXiv preprint arXiv:2304.12239},
  year={2023}
}
```

License
-------

This project is licensed under the terms of the MIT license. See LICENSE for additional details.
