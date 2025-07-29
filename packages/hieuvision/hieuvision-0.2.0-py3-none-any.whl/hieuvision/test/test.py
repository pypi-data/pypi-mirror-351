
from core import HieuVision
from tools.augmenter import ImageAugmenter


augmenter = ImageAugmenter(
    input_dir="dataset",
    output_dir="dataset_augment"
)

hv = HieuVision()
hv.add_tool("augment", augmenter)
hv.run_tool("augment")