# Sorts images from a branching directory to a flattened single folder and then sorts them by metadata

from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import os
import shutil


# Set branching directory path
branching_root = ""

# Set target flattened directory path
flattened_directory = "flattened_images"


def flatten_images_directory(src_dir, dest_dir):
    # Traverse the source directory
    for root, _, files in os.walk(src_dir):
        for file in files:
            # Check if the file is an image (you can customize this check as needed)
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, file)

                # Check if the destination file already exists (avoid overwriting)
                if not os.path.exists(dest_path):
                    shutil.move(src_path, dest_path)
                    print(f"Moved: {src_path} -> {dest_path}")
                else:
                    print(f"Skipped (file already exists): {src_path}")


# Traverse directory of images and read metadata
def sort_images(src_dir):
    for image in os.listdir(src_dir):
        image_path = f"{src_dir}/{image}"
        img_data = Image.open(image_path)
        exifdata = img_data.getexif()

        info_dict = {}

        for tag_id in exifdata:
            # get the tag name, instead of human unreadable tag id
            tag = TAGS.get(tag_id, tag_id)
            data = exifdata.get(tag_id)
            info_dict[tag] = data

        img_data.close()
        # Image data has been granted, now traverse folders as necessary, or create directory if needed

        # If no image data, quarantine image:
        if not info_dict:
            shutil.move(image_path, "Quarantine")
        else:
            try:
                dt = datetime.strptime(info_dict["DateTime"][:10], "%Y:%m:%d")
                save_directory_path = f"sorted_images/{dt.year}/{dt.month}"

                os.makedirs(save_directory_path, exist_ok=True)
                shutil.move(image_path, save_directory_path)
            except KeyError:
                shutil.move(image_path, "Quarantine")
