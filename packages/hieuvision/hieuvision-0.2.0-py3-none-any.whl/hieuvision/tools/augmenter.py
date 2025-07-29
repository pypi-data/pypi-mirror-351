import os
import cv2
import shutil
import albumentations as A
from tqdm import tqdm

class ImageAugmenter:
    def __init__(self, root_input_dir, root_output_dir, brightness_limit=0.3, contrast_limit=0.3):
        self.root_input_dir = root_input_dir
        self.root_output_dir = root_output_dir
        self.transform = A.Compose([
            A.RandomBrightnessContrast(brightness_limit=brightness_limit,
                                       contrast_limit=contrast_limit, p=1.0)
        ])
        os.makedirs(self.root_output_dir, exist_ok=True)

    def run(self):
        for dirpath, _, filenames in os.walk(self.root_input_dir):
            rel_path = os.path.relpath(dirpath, self.root_input_dir)
            output_dir = os.path.join(self.root_output_dir, rel_path)
            os.makedirs(output_dir, exist_ok=True)

            for filename in tqdm(filenames, desc=f"Augmenting images {rel_path}"):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(dirpath, filename)
                    label_name = filename.rsplit('.', 1)[0] + '.txt'
                    label_path = os.path.join(dirpath, label_name)

                    image = cv2.imread(image_path)
                    if image is None:
                        print(f"⚠️ Cannot read image: {filename}")
                        continue

                    augmented = self.transform(image=image)
                    aug_image = augmented['image']

                    aug_img_path = os.path.join(output_dir, filename)
                    cv2.imwrite(aug_img_path, aug_image)

                    if os.path.exists(label_path):
                        aug_label_path = os.path.join(output_dir, os.path.basename(label_name))
                        shutil.copy(label_path, aug_label_path)
                    else:
                        print(f"⚠️ Label not found for: {image_path}")

        print("Image augmentation complete.")
