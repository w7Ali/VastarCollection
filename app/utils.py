from PIL import Image


def resize_image(image_path, target_width, target_height):
    img = Image.open(image_path)
    img = img.resize((target_width, target_height), Image.ANTIALIAS)
    img.save(image_path, quality=90)
