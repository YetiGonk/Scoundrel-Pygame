""" Split a png into multiple pngs of the same size and same dimensions. """

import os
from PIL import Image
from glob import glob

def split_image(image_path, output_dir, rows, cols):
    """
    Split an image into smaller images.
    
    :param image_path: Path to the input image.
    :param output_dir: Directory to save the split images.
    :param rows: Number of rows to split the image into.
    :param cols: Number of columns to split the image into.
    """
    # Open the image
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Calculate the size of each split image
    split_width = img_width // cols
    split_height = img_height // rows

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Split the image
    for row in range(rows):
        for col in range(cols):
            left = col * split_width
            upper = row * split_height
            right = left + split_width
            lower = upper + split_height

            # Crop the image
            cropped_img = img.crop((left, upper, right, lower))

            # Save the cropped image
            output_path = os.path.join(output_dir, f"{os.path.basename(image_path).split('.')[0]}_{row}_{col}.png")
            cropped_img.save(output_path)
            print(f"Saved {output_path}")

if __name__ == "__main__":
    # Example usage
    pngs_dir = "assets/weapons/weapons1.png"
    pngs_list = glob(pngs_dir)
    output_dir = "assets/weapons"
    rows = 3
    cols = 3
    for img_path in pngs_list:
        split_image(img_path, output_dir, rows, cols)