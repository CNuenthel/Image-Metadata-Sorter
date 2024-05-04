from PIL import Image
import os
import shutil
import re
from moviepy.editor import VideoFileClip



# Set branching directory path
branching_root = ""

# Set target flattened directory path
flattened_directory = "flattened_images"

SORTED = 0
QUARANTINED = 0

month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}


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


def sort_by_filename(image_file_path):
    filename_base = os.path.basename(image_file_path)
    filename = os.path.splitext(filename_base)[0]
    date_dict = {}

    if re.match(r"\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}.*", filename):  # For files with "2016-12-25 09.56.00" format
        date_list = filename[:7].split("-")
        date_dict = {key: value for key, value in zip(["year", "month"], date_list)}

    elif re.match(r"\d{8}_\d{6}.*", filename):  # For files with "20130101_001300" format
        date_dict = {
            "year": filename[:4],
            "month": filename[4:6]
        }

    elif re.match(r"\d{14}_IMG_\d{4}.*", filename):  # For files with "20210205112757_IMG_3337" format
        date_dict = {
            "year": filename[:4],
            "month": filename[4:6]
        }

    elif re.match(r"\d{14}.*", filename):  # For files with "20220204090015" format
        date_dict = {
            "year": filename[:4],
            "month": filename[4:6]
        }

    elif re.match(r"IMG_\d{8}_\d{6}.*", filename):  # For files with "IMG_20140807_222851" format
        date_dict = {
            "year": filename[4:8],
            "month": filename[8:10]
        }

    elif re.match(r"Screenshot_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}.*",
                  filename):  # For files with "Screenshot_YYYY-MM-DD..." format
        date_list = filename.split("_")[1].split("-")
        date_dict = {
            "year": date_list[0],
            "month": date_list[1]
        }
        # Screenshot_\d{8}[-_]\d{6}\
    elif re.match(r"Screenshot_\d{8}[-_]\d{6}.*", filename):  # For files with "Screenshot_YYYYMMDD..." format
        date_string = filename.split("_")[1].split("-")[0]
        date_dict = {
            "year": date_string[:4],
            "month": date_string[4:6]
        }

    elif re.match(r"VideoCapture_\d{8}-\d{6}.*", filename):  # For files with "VideoCapture_YYYYMMDD..." format
        date_string = filename.split("_")[1].split("-")[0]
        date_dict = {
            "year": date_string[:4],
            "month": date_string[4:6]
        }

    elif re.match(r"\d{4}-\d{2}-\d{2}_\d{2}\.\d{2}\.\d{2}.*", filename):  # For files with "YYYY-MM-DD..." format
        date_list = filename.split("-")
        date_dict = {
            "year": date_list[0],
            "month": date_list[1]
        }

    # Move files
    if date_dict:
        save_directory_path = f"sorted_images/{date_dict["year"]}/{date_dict["month"]}"
        os.makedirs(save_directory_path, exist_ok=True)  # Make new month directory if missing from target directory
        shutil.move(image_file_path, save_directory_path)

        global SORTED
        SORTED += 1

        return True

    return False


def sort_by_metadata(image_file_path):
    image_data = Image.open(image_file_path)
    exifdata = image_data.getexif()  # exifdata tag 306 is datetime
    date_string = exifdata.get(306)
    image_data.close()

    if date_string:
        date_list = date_string.split(":")

        date_dict = {
            "year": date_list[0],
            "month": date_list[1]
        }

        save_directory_path = f"sorted_images/{date_dict["year"]}/{date_dict["month"]}"
        os.makedirs(save_directory_path, exist_ok=True)  # Make new month directory if missing from target directory
        shutil.move(image_file_path, save_directory_path)

        global SORTED
        SORTED += 1

        return True

    return False


def sort_by_mp4_creation_date(file_path):
    try:
        video = VideoFileClip(file_path)
        # creation_date = video.reader.info['creation_time']
        return video
    except Exception as e:
        print("Error:", e)
        return None


def scan_directory(directory):
    dir_items = os.listdir(directory)
    dir_size = len(dir_items)

    print(f"Sorting {dir_size} files in {directory} directory...")

    for image in os.listdir(directory):
        image_path = f"{directory}/{image}"

        try:
            if sort_by_filename(image_path):
                continue
            elif sort_by_metadata(image_path):
                continue
            else:
                global QUARANTINED
                QUARANTINED += 1

                save_directory_path = f"quarantine"
                os.makedirs(save_directory_path, exist_ok=True)
                shutil.move(image_path, save_directory_path)

        except Exception as e:
            print(f"Unable to sort a file...\n{e}")

    print(f"Sorting complete, {SORTED} files sorted, {QUARANTINED} files quarantined.")
