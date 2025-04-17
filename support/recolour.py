from PIL import Image
import glob
import sys

def replace_colour(image_path, old_colour, new_colour):
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        # remove all pixels with the old colour and replace with new colour
        new_data = [new_colour if pixel[:len(old_colour)] == old_colour else pixel for pixel in data]
        # remove all pixel close to old colour and replace with new colour
        new_data = [new_colour if all(abs(pixel[i] - old_colour[i]) < 50 for i in range(4)) else pixel for pixel in new_data]
        
        img.putdata(new_data)
        img.save(image_path, "PNG")
        print(f"Image saved successfully to {image_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    replace_colour("assets/ui/inv.png", (207,213,213,255), (255,255,255,0))


