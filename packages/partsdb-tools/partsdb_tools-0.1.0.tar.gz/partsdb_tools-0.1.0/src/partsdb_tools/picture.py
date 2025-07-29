import argparse
import cv2 as cv
import numpy as np

from pathlib import Path
from .common import load_manufacturers

min_size_x = 640*2
min_size_y = 480*2
small_object_size_x=640*2
small_object_size_y=480*2

class OutputImageParameters:
    def __init__(self, width: int, height: int, border: int):
        assert width > 0 and height > 0
        assert border >= 0
        assert width - 2*border > 0
        assert height - 2*border > 0
        self.width = width
        self.height = height
        self.border = border
        self.ratio = width/height
        self.object_width = width - 2*border
        self.object_height = height - 2*border

class BoundingBox:
    def __init__(self, xmin, xmax, ymin, ymax, image_width, image_height):
        assert xmin < xmax
        assert ymin < ymax
        assert xmax <= image_width, f"{xmax} > {image_width}"
        assert ymax <= image_height, f"{ymax} > {image_height}"
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.size_x = xmax - xmin
        self.size_y = ymax - ymin
        self.ratio = self.size_x/self.size_y
        self.image_width = image_width
        self.image_height = image_height

    def center(self):
        return self.xmin + (self.xmax - self.xmin) / 2, self.ymin + (self.ymax - self.ymin) / 2

    def __str__(self):
        return f"Bounding box {self.xmin}-{self.xmax}-{self.ymin}-{self.ymax}"


def main():
    parser = argparse.ArgumentParser(description="Picture tool")
    parser.add_argument('-b', '--background_image', type=Path, help="Background image")
    parser.add_argument('-i', '--input_dir', type=Path, required=True, help="Input image directory")
    parser.add_argument('-o', '--output_dir', type=Path, required=True, help="Output image directory")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('-m', '--manufacturers', type=Path, help="Manufacturers definition file")
    parser.add_argument('--output_image_size_x', type=int, default=640, help="Output image size")
    parser.add_argument('--output_image_size_y', type=int, default=480, help="Output image size")
    args = parser.parse_args()

    out_img_params = OutputImageParameters(args.output_image_size_x, args.output_image_size_y, 20)
    if args.manufacturers is not None:
        manufacturers = load_manufacturers(args.manufacturers.resolve())
    else:
        manufacturers = None

    image_collections = load_images(args.input_dir, args.background_image)
    for collection in image_collections:
        try:
            print("Processing", collection)
            processed_images = process_images(
                image_collections[collection]["background"],
                image_collections[collection]["images"],
                out_img_params,
                debug=args.debug
            )
            for processed_image_name in processed_images:
                save_image(processed_images[processed_image_name], args.output_dir, processed_image_name, manufacturers)
        except Exception as e:
            print(f"Exception while processing {collection}: ", e)


def process_images(background, images, out_image_params, debug=False):
    back_sub = cv.createBackgroundSubtractorMOG2(history=10, varThreshold=200, detectShadows=False)
    for i in range(4):
        back_sub.apply(background)

    fg_masks = []
    for image_name in images:
        fg_masks.append(back_sub.apply(images[image_name]))
        if debug:
            cv.imshow('FG Mask', cv.resize(fg_masks[-1], (640, 480), interpolation=cv.INTER_AREA))
            cv.waitKey(300)

    fg_mask = cv.bitwise_or(filterout_small_elements(fg_masks[-2]), filterout_small_elements(fg_masks[-1]))
    if debug:
        cv.imshow('FG Mask sum', cv.resize(fg_mask, (640, 480), interpolation=cv.INTER_AREA))
        cv.waitKey(300)
    bounding_box = get_bounding_box(fg_mask)

    processed_images = {}
    if is_small_object(bounding_box):
        dims = inside_min_image(bounding_box)
        x1, x2, y1, y2 = dims
        for image_name in images:
            final_bounding_box = BoundingBox(x1 - out_image_params.border,
                                             x2 + out_image_params.border,
                                             y1 - out_image_params.border,
                                             y2 + out_image_params.border,
                                             images[image_name].shape[1],
                                             images[image_name].shape[0])
            output_image = crop_image(images[image_name], final_bounding_box)
            resized_img = cv.resize(
                output_image,
                (out_image_params.width, out_image_params.height),
                interpolation=cv.INTER_AREA)
            processed_images[image_name] = resized_img
    else:
        for image_name in images:
            final_bounding_box = bounding_box_to_proportion(bounding_box, out_image_params)
            cropped_image=crop_image(images[image_name], final_bounding_box)
            resized_img = cv.resize(
                cropped_image,
                (out_image_params.width, out_image_params.height),
                interpolation=cv.INTER_AREA)
            processed_images[image_name] = resized_img
    return processed_images


def load_images(input_dir: Path, background_image: Path):
    image_collection = {}
    for file in input_dir.glob('**/*'):
        if file.is_file():
            filename = file.stem
            basename_end = filename.rfind("__")
            if basename_end != -1:
                collection = filename[:basename_end]
                if collection not in image_collection:
                    image_collection[collection] = {"background": None, "images": {}}
                if filename.endswith("background"):
                    image_collection[collection]["background"] = cv.imread(file.resolve())
                else:
                    image_collection[collection]["images"][filename] = cv.imread(file.resolve())

    if background_image is not None and background_image.is_file():
        background_img = cv.imread(background_image.resolve())
        for collection in image_collection:
            if image_collection[collection]["background"] is None:
                image_collection[collection]["background"] = background_img
    return image_collection


def save_image(image, output_dir, filename, manufacturers):
    manufacturer_name = filename.split("__")[0]
    if manufacturer_name in manufacturers or manufacturers is None:
        write_path = output_dir.joinpath(manufacturer_name).joinpath(filename).with_suffix(".jpg")
        write_path.parent.mkdir(parents=True, exist_ok=True)
        status = cv.imwrite(write_path.resolve(), image)
        if not status:
            print("Error writing image:", write_path.resolve())


def is_small_object(bounding_box):
    if bounding_box.size_x <= small_object_size_x and bounding_box.size_y <= small_object_size_y:
        return True
    else:
        return False


def filterout_small_elements(fg_mask):
    nb_blobs, im_with_separated_blobs, stats, _ = cv.connectedComponentsWithStats(fg_mask)
    sizes = stats[:, cv.CC_STAT_AREA]
    min_size = 1000

    im_result = np.zeros_like(im_with_separated_blobs, dtype=np.uint8)
    for index_blob in range(1, nb_blobs):
        if sizes[index_blob] >= min_size:
            im_result[im_with_separated_blobs == index_blob] = 255
    return im_result


def bounding_box_to_proportion(bounding_box, image_parameters: OutputImageParameters):
    if bounding_box.ratio > image_parameters.ratio:
        # add borders and adjust heigh
        scaling_ratio = bounding_box.size_x / image_parameters.object_width
        width_border = image_parameters.border * scaling_ratio
        if bounding_box.xmin - width_border < 0:
            width_border = bounding_box.xmin
            scaling_ratio = (bounding_box.size_x + 2*width_border) / image_parameters.width
        height = image_parameters.height * scaling_ratio
        if height > bounding_box.image_height:
            if bounding_box.image_width / bounding_box.image_height == image_parameters.ratio:
                return BoundingBox(0, bounding_box.image_width, 0, bounding_box.image_height, bounding_box.image_width, bounding_box.image_height)
            else:
                print(f"Original image ratio {bounding_box.image_width/bounding_box.image_height}, "
                      f"requested ratio {image_parameters.ratio}, scaling factor: {scaling_ratio}, scaled height: {height}")
                raise ValueError("Unable to fit bounding box with requested image ratio")
        center_y = bounding_box.center()[1]
        y_min = int(center_y - height / 2)
        return BoundingBox(int(bounding_box.xmin - width_border),
                           int(bounding_box.xmax + width_border),
                           y_min,
                           int(y_min + height),
                           bounding_box.image_width,
                           bounding_box.image_height)
    else:
        print("Adjusting width")
        # add borders and adjust width
        scaling_ratio = bounding_box.size_y / image_parameters.object_height
        height_border = image_parameters.border * scaling_ratio
        if bounding_box.ymin - height_border < 0:
            height_border = bounding_box.ymin
            scaling_ratio = (bounding_box.size_y + 2*height_border) / image_parameters.height
        width_border = image_parameters.border * scaling_ratio

    return BoundingBox(int(bounding_box.xmin - width_border),
                       int(bounding_box.xmax + width_border),
                       int(bounding_box.ymin * scaling_ratio - height_border),
                       int(bounding_box.ymax * scaling_ratio + height_border),
                       bounding_box.image_width,
                       bounding_box.image_height)


def get_bounding_box(elements):
    pts = np.argwhere(elements>0)
    y1, x1 = pts.min(axis=0)
    y2, x2 = pts.max(axis=0)
    return BoundingBox(x1, x2, y1, y2, elements.shape[1], elements.shape[0])


def crop_image(image, bounding_box):
    return image[
           bounding_box.ymin:bounding_box.ymax,
           bounding_box.xmin:bounding_box.xmax]


def inside_min_image(bounding_box):
    if bounding_box.size_x <= min_size_x and bounding_box.size_y <= min_size_y:
        middle_x = int(bounding_box.xmin + bounding_box.size_x / 2)
        middle_y = int(bounding_box.ymin + bounding_box.size_y / 2)
        return middle_x - min_size_x, middle_x + min_size_x, middle_y - min_size_y, middle_y + min_size_y
    return None
