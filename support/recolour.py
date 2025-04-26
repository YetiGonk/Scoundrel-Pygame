from PIL import Image
import glob
import sys

def replace_colour(image_path, old_colour, new_colour):
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        new_data = []
        for item in data:
            # print the colour code if it is within 20 of the old_colour
            if abs(item[0] - old_colour[0]) < 20 and abs(item[1] - old_colour[1]) < 20 and abs(item[2] - old_colour[2]) < 20:
                print(item)
            if item == old_colour:
                print(item)
                new_data.append(new_colour)
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        img.save(image_path)
        print(f"Replaced {old_colour} with {new_colour} in {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

if __name__ == "__main__":
    replace_colour("assets/weapons/weapons1.png", (233, 157, 32, 255), (206, 45, 11, 255))


