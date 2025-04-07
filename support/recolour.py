from PIL import Image
import glob
import sys

def replace_color(image_path, old_color, new_color):
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        # remove all pixels with the old color and replace with new color
        new_data = [new_color if pixel[:len(old_color)] == old_color else pixel for pixel in data]
        # remove all pixel close to old color and replace with new color
        new_data = [new_color if all(abs(pixel[i] - old_color[i]) < 50 for i in range(4)) else pixel for pixel in new_data]
        
        img.putdata(new_data)
        img.save(image_path, "PNG")
        print(f"Image saved successfully to {image_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    replace_color("assets/ui/inv.png", (207,213,213,255), (255,255,255,0))


