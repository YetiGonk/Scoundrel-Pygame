from PIL import Image
import os

def isolate_card_corners(image_path, output_path):
    """
    Keeps only the suit and rank in the top-left and bottom-right corners of a playing card image.
    Turns everything else white except for already transparent areas.
    
    :param image_path: Path to the input PNG file.
    :param output_path: Path to save the modified PNG file.
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        pixels = img.load()
        width, height = img.size
        
        # Define corner areas (adjust values if needed)
        corner_width = int(width / 4.6)
        corner_height = int(height / 3)
        
        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                
                # Keep pixels in the top-left or bottom-right corners, white out the rest
                if not ((x < corner_width and y < corner_height) or (x > width - corner_width - (5 if "10" in image_path else 0) and y > height - corner_height)):
                    if a > 0:  # Only change non-transparent pixels
                        pixels[x, y] = (255, 255, 255, 255)
        
        img.save(output_path, "PNG")
        print(f"Image saved successfully to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

def process_all_cards(input_folder):
    """
    Processes all card images in the given folder that start with clubs, hearts, diamonds, or spades.
    
    :param input_folder: Path to the folder containing card images.
    :param input_folder: Path to save processed images.
    """
    for filename in os.listdir(input_folder):
        if filename.startswith(("clubs", "hearts", "diamonds", "spades")) and filename.endswith(".png"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(input_folder, filename)
            print(f"Processing {filename}...")
            isolate_card_corners(input_path, output_path)

if __name__ == "__main__":
    input_folder = "../assets/cards"
    process_all_cards(input_folder)