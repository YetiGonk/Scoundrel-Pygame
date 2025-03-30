from PIL import Image
import sys

def replace_color(image_path, old_color, new_color):
    try:
        img = Image.open(image_path).convert("RGBA")
        data = img.getdata()
        
        new_data = [new_color + (pixel[3],) if pixel[:3] == old_color else pixel for pixel in data]
        
        img.putdata(new_data)
        img.save(image_path, "PNG")
        print(f"Image saved successfully to {image_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    replace_color("../assets/cards/joker_red_15.png", (0,0,0), (171, 82, 54))
    replace_color("../assets/cards/joker_red_16.png", (0,0,0), (171, 82, 54))
    replace_color("../assets/cards/joker_red_17.png", (0,0,0), (171, 82, 54))
