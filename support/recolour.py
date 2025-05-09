from PIL import Image
import glob
import sys

def replace_colour(image_path, old_colour, new_colour):
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        new_data = []
        for item in data:
            if item == old_colour:
                new_data.append(new_colour)
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        img.save(image_path)
        print(f"Replaced {old_colour} with {new_colour} in {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    replace_colour("assets/weapons/scythe.png", (239, 172, 40, 255), (155, 26, 10, 255))
    replace_colour("assets/weapons/scythe.png", (236, 196, 105, 255), (206, 45, 11, 255))
    replace_colour("assets/weapons/scythe.png", (239, 216, 161, 255), (239, 58, 12, 255))


