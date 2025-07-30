# Setup
```shell
conda create -n uois-datasets python=3.10
conda activate uois-datasets
export CUDA_HOME=/usr/local/cuda-12.6 # (use your cuda version)
pip install torch torchvision opencv-python numpy scipy pycocotools
pip install git+https://github.com/facebookresearch/detectron2@65184fc057d4fab080a98564f6b60fae0b94edc4
```

# To test locally
```shell
rm -rf build dist *egg* && pip install -e .
```

<details>
<summary><strong>Note:</strong> Click to show more 💡 (For PyPI)</summary>
Execute the following commands with each new PyPI build:

```bash
python -m pip install build twine
rm -rf build/ dist/ # Also remove the corresponding .egg-info directory
python -m build
python setup.py sdist bdist_wheel # Make sure to change the version in setup.py before running this
twine upload dist/* # Ensure you have the pypi-token
```
</details>

# Use
```python
python test/test_datasets.py
# If sample output is as follows then everything works fine
# INFO:uois_toolkit.core.datasets.iteach_humanplay:2859 images for dataset iteach_humanplay_object_train
# INFO:uois_toolkit.core.datasets.iteach_humanplay:11796 images for dataset iteach_humanplay_object_train
# INFO:uois_toolkit.core.datasets.iteach_humanplay:902 images for dataset iteach_humanplay_object_test
# INFO:uois_toolkit.core.datasets.ocid:2390 images for dataset ocid_object_train
# INFO:uois_toolkit.core.datasets.ocid:2390 images for dataset ocid_object_test
# INFO:uois_toolkit.core.datasets.tabletop:280000 images for dataset tabletop_object_train
# INFO:uois_toolkit.core.datasets.tabletop:28000 images for dataset tabletop_object_test
# INFO:uois_toolkit.core.datasets.robot_pushing:321 images for dataset robot_pushing_object_train
# INFO:uois_toolkit.core.datasets.robot_pushing:107 images for dataset robot_pushing_object_test
# INFO:uois_toolkit.core.datasets.osd:111 images for dataset osd_object_train
# INFO:uois_toolkit.core.datasets.osd:111 images for dataset osd_object_test
```

# Add download links for all the datasets
# Add metrics utils as well