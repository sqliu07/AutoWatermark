from PyQt5.QtGui import QImage
def pil_image_to_qimage(pil_image):
    """
    将PIL Image转换为QImage
    :param pil_image: PIL Image对象
    :return: QImage对象
    """
    # 将PIL图像转换为RGB格式，如果已经是RGB，这步骤不会改变图像
    pil_image = pil_image.convert("RGB")

    # 将PIL图像数据转换为字节串
    image_data = pil_image.tobytes()

    # 创建QImage对象
    qimage = QImage(image_data, pil_image.width, pil_image.height, QImage.Format_RGB888)

    # 返回转换后的QImage对象
    return qimage

def reset_image_orientation(image):
    try:
        exif = image._getexif()
        if exif:
            orientation = exif.get(274)
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except Exception as e:
        print(f"Error resetting orientation: {e}")
    return image
