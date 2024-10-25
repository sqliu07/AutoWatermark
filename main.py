from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLabel, QHBoxLayout, QScrollArea, QTableWidget, QTableWidgetItem
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QFont, QImage

import subprocess
import piexif
import os

EDGE_WIDTH = 300
EDGE_WIDTH_SIDE = 150
FONT_SIZE = 90

IMAGE_SIZE = 6000 * 5000
class ImageWatermarkApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('Image Watermark App')
        self.setGeometry(100, 100, 1200, 800)
        self.setFixedSize(1500, 1000)

        # 创建布局
        main_layout = QtWidgets.QHBoxLayout()

        # 左侧布局
        left_layout = QtWidgets.QVBoxLayout()

        # 创建按钮和标签
        self.images_path_label = QtWidgets.QLabel('Images Path:')
        self.images_path_edit = QtWidgets.QLineEdit()
        self.images_browse_button = QtWidgets.QPushButton('Browse')

        self.logo_path_label = QtWidgets.QLabel('Logo Path:')
        self.logo_path_edit = QtWidgets.QLineEdit()
        self.logo_browse_button = QtWidgets.QPushButton('Browse')

        self.output_dir_label = QtWidgets.QLabel('Output Directory:')
        self.output_dir_edit = QtWidgets.QLineEdit()
        self.output_browse_button = QtWidgets.QPushButton('Browse')

        self.run_button = QtWidgets.QPushButton('Run')
        self.preview_button = QtWidgets.QPushButton('Preview')

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.preview_button)

        self.exif_info_table = QTableWidget(1, 4)
        self.exif_info_table.setHorizontalHeaderLabels(['Focal Length', 'Aperture', 'Exposure Time', 'ISO'])
        self.exif_info_table.setFixedSize(600, 100)
        self.exif_info_table.horizontalHeader().setStretchLastSection(True)
        self.exif_info_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.exif_info_table.setStyleSheet("QHeaderView::section { background-color:lightgray }")

        font = QFont("Arial", 10, QFont.Bold)
        self.exif_info_table.setFont(font)

        for i in range(4):
            self.exif_info_table.horizontalHeaderItem(i).setFont(font)

        self.exif_info_table.setAlternatingRowColors(True)
        self.exif_info_table.setStyleSheet("""
                   QTableWidget {
                       background-color: #F5F5F5;
                       alternate-background-color: #E0E0E0;
                       selection-background-color: #4CAF50;
                       selection-color: white;
                   }
                   QTableWidget::item {
                       border: 1px solid #d9d9d9;
                       padding: 5px;
                   }
               """)

        # 添加控件到左侧布局
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.images_path_label, self.images_path_edit)
        form_layout.addRow(self.images_browse_button)
        form_layout.addRow(self.logo_path_label, self.logo_path_edit)
        form_layout.addRow(self.logo_browse_button)
        form_layout.addRow(self.output_dir_label, self.output_dir_edit)
        form_layout.addRow(self.output_browse_button)

        left_layout.addLayout(form_layout)
        left_layout.addWidget(self.exif_info_table)
        # left_layout.addWidget(self.selected_image_label)  # 添加选定图片展示区域
        left_layout.addLayout(button_layout)

        # 设置布局间距
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)

        # 右侧布局
        right_layout = QtWidgets.QVBoxLayout()

        # 创建预览区域
        self.preview_area = QLabel()
        self.preview_area.setFixedSize(800, 600)
        self.preview_area.setAlignment(QtCore.Qt.AlignCenter)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.preview_area)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedSize(800, 600)

        self.selected_image_label = QLabel()
        self.selected_image_label.setFixedSize(600, 400)
        self.selected_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.selected_image_label.setStyleSheet("border: 1px solid #ccc;")  # 可选的样式设置
        self.scroll_area_selected = QScrollArea()
        self.scroll_area_selected .setWidget(self.selected_image_label)
        self.scroll_area_selected .setWidgetResizable(True)
        self.scroll_area_selected .setFixedSize(600, 400)

        left_layout.addWidget(self.scroll_area_selected, stretch = 3)
        right_layout.addWidget(self.scroll_area, stretch = 3)

        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout, stretch = 1)
        main_layout.addLayout(right_layout, stretch = 1)

        self.setLayout(main_layout)

        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-weight: bold;
                font-size: 16px;
            }
        """)

        # 连接信号和槽
        self.images_browse_button.clicked.connect(self.browse_images)
        self.logo_browse_button.clicked.connect(self.browse_logo)
        self.output_browse_button.clicked.connect(self.browse_output_dir)
        self.run_button.clicked.connect(self.run)
        self.preview_button.clicked.connect(self.preview)

    def browse_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Images', '', 'Image Files (*.jpg *.jpeg *.png)')
        if files:
            try:
                self.images_path_edit.setText(';'.join(files))
                self.display_exif_info(files[0])
                self.display_selected_image(files[0])  # 显示选定的图片
                manufacturer = self.get_manufacturer(files[0])
                logo_path = self.find_logo(manufacturer)
                if logo_path:
                    self.logo_path_edit.setText(logo_path)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def display_selected_image(self, image_path):
        image = Image.open(image_path)
        image = reset_image_orientation(image)  # Reset orientation
        qt_image = pil_image_to_qimage(image)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        self.selected_image_label.setPixmap(
            pixmap.scaled(self.selected_image_label.size(), QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation))

    def browse_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Logo', '', 'Image Files (*.png *.jpg *.jpeg)')
        if file_path:
            self.logo_path_edit.setText(file_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if dir_path:
            self.output_dir_edit.setText(dir_path)

    def run(self):
        images_paths = self.images_path_edit.text().split(';')
        logo_path = self.logo_path_edit.text()
        output_dir = self.output_dir_edit.text()

        if not images_paths or not logo_path or not output_dir:
            QMessageBox.warning(self, 'Input Error', 'Please provide all paths.')
            return

        logo_folder_path = "./logos"
        try:
            for image_path in images_paths:
                base_name = os.path.basename(image_path)
                name, ext = os.path.splitext(base_name)
                output_path = os.path.join(output_dir, f"{name}_watermark{ext}")
                manufacturer = self.get_manufacturer(image_path)
                logo_path = self.find_logo(manufacturer)
                add_borders_logo_and_text(image_path, logo_path, output_path)
            QMessageBox.information(self, 'Success', 'Images processed successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def preview(self):
        images_paths = self.images_path_edit.text().split(';')
        logo_path = self.logo_path_edit.text()

        if not images_paths or not logo_path:
            QMessageBox.warning(self, 'Input Error', 'Please provide images and logo path for preview.')
            return

        try:
            preview_image_path = images_paths[0]
            preview_image = add_borders_logo_and_text(preview_image_path, logo_path, preview=True)
            # preview_image.show()
            self.display_preview(preview_image)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')

    def get_manufacturer(self, image_path):
        try:
            image = Image.open(image_path)
            image = reset_image_orientation(image)
            exif_dict = piexif.load(image.info['exif'])
            manufacturer = exif_dict['0th'].get(piexif.ImageIFD.Make, b"").decode().strip()
            for letter in manufacturer:
                if letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    continue
                else:
                    manufacturer = manufacturer.replace(letter, '')
            return manufacturer
        except Exception as e:
            print(f"Error getting manufacturer: {e}")
            return ""

    def find_logo(self, manufacturer):
        logo_dir = "./logos"
        if not os.path.isdir(logo_dir):
            logo_dir = "D:/摄影/tool/auto_watermark/logos"  # 替换为你的logo文件夹路径
        for root, dirs, files in os.walk(logo_dir):
            for file in files:
                if file.lower().startswith(manufacturer.lower().split()[0]) \
                        or manufacturer.lower().startswith(file.lower().split('.')[0]):
                    return os.path.join(root, file)
        return None

    def display_preview(self, image):
        qt_image = pil_image_to_qimage(image)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        self.preview_area.setPixmap(pixmap.scaled(self.preview_area.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def display_exif_info(self, image_path):
        try:
            focal_length, aperture, exposure_time, iso = get_exif_table(image_path)
            self.exif_info_table.setItem(0, 0, QTableWidgetItem(f"{focal_length:.1f} mm"))
            self.exif_info_table.setItem(0, 1, QTableWidgetItem(f"f/{aperture:.1f}"))
            self.exif_info_table.setItem(0, 2, QTableWidgetItem(f"1/{int(1 / exposure_time)} s"))
            self.exif_info_table.setItem(0, 3, QTableWidgetItem(f"ISO {iso}"))

            for i in range(4):
                item = self.exif_info_table.item(0, i)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                item.setTextAlignment(QtCore.Qt.AlignCenter)  # 设置单元格内容居中

        except Exception as e:
            self.exif_info_table.setItem(0, 0, QTableWidgetItem(f"Error: {e}"))
            self.exif_info_table.setItem(0, 1, QTableWidgetItem(""))
            self.exif_info_table.setItem(0, 2, QTableWidgetItem(""))
            self.exif_info_table.setItem(0, 3, QTableWidgetItem(""))

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

def get_exif_table(image_path):
    image = Image.open(image_path)
    image = reset_image_orientation(image)  # Reset orientation

    exif_dict = piexif.load(image.info['exif'])
    exif_data = exif_dict['Exif']

    focal_length_35 = exif_data.get(piexif.ExifIFD.FocalLengthIn35mmFilm, (0, 1))
    focal_length = exif_data.get(piexif.ExifIFD.FocalLength, (0, 1))
    f_number = exif_data.get(piexif.ExifIFD.FNumber, (0, 1))
    exposure_time = exif_data.get(piexif.ExifIFD.ExposureTime, (0, 1))
    iso_speed = exif_data.get(piexif.ExifIFD.ISOSpeedRatings, 0)

    # focal_length_value = focal_length[0] / focal_length[1] if focal_length[1] != 0 else 0 # 实际焦距

    focal_length_value = focal_length_35 # 35mm 焦距
    f_number_value = f_number[0] / f_number[1] if f_number[1] != 0 else 0
    exposure_time_value = exposure_time[0] / exposure_time[1] if exposure_time[1] != 0 else 0

    return focal_length_value, f_number_value, exposure_time_value, iso_speed

def get_exif_data(image_path):
    dji_models = {
        'FC8482': 'DJI Mini 4 Pro',
        'FC7703': 'DJI Mini 2 SE'
    }

    image = Image.open(image_path)
    image = reset_image_orientation(image)  # Reset orientation

    exif_dict = piexif.load(image.info['exif'])
    exif_data = exif_dict['Exif']


    lens_info = exif_data.get(piexif.ExifIFD.LensModel, b"Unknown Lens").decode()
    camera_make = exif_dict['0th'].get(piexif.ImageIFD.Make, b"Unknown Make").decode()
    camera_model_code = exif_dict['0th'].get(piexif.ImageIFD.Model, b"Unknown Model").decode()

    for letter in camera_make:
        if letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            continue
        else:
            camera_make = camera_make.replace(letter, '')

    for letter in camera_model_code:
        if letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ':
            continue
        else:
            camera_model_code = camera_model_code.replace(letter, '')

    focal_length = exif_data.get(piexif.ExifIFD.FocalLength, (0, 1))
    focal_length_35 = exif_data.get(piexif.ExifIFD.FocalLengthIn35mmFilm, (0, 1))
    f_number = exif_data.get(piexif.ExifIFD.FNumber, (0, 1))
    exposure_time = exif_data.get(piexif.ExifIFD.ExposureTime, (0, 1))
    iso_speed = exif_data.get(piexif.ExifIFD.ISOSpeedRatings, 0)
    datetime = exif_data.get(piexif.ExifIFD.DateTimeOriginal, b"Unknown Date").decode()

    if camera_make.lower() == "dji":  # DJI 相机
        lens_info = "DJI"
        camera_model = dji_models.get(camera_model_code)
        print("camera_model get = " + str(camera_model))
    else:
        camera_model = camera_model_code
    if ' ' in datetime:
        index = datetime.index(' ')  # 找到空格的索引位置
        substring = datetime[:index]  # 提取空格前的部分
        if ":" in substring:
            new_substring = substring.replace(':', '-')  # 替换冒号为连字符
            datetime = datetime[:index].replace(substring, new_substring) + datetime[index:]

    if "T" in datetime:
        print("t in datetime")
        datetime = datetime.replace("T", " ")
        print(datetime)
        index = datetime.index(" ")  # 找到空格的索引位置
        substring = datetime[:index]  # 提取空格前的部分
        if ":" in substring:
            new_substring = substring.replace(':', '-')  # 替换冒号为连字符
            datetime = datetime[:index].replace(substring, new_substring) + datetime[index:]

    if str(lens_info) == "Unknown Lens":
        # 定义要尝试的ID列表
        exif_ids = ["-LensModel", "-Lens", "-LensType"]
        # 初始化镜头信息为空
        lens_info = "Unknown Lens"
        exif_tool_path = "./exiftool/exiftool.exe"
        for exif_id in exif_ids:
            output = subprocess.check_output([exif_tool_path, exif_id, image_path])
            output = output.decode().strip().split(":")
            if len(output) > 1:
                lens_info = output[1].strip()
                break
        if "Asph" in lens_info:
            index = lens_info.find("Asph")

            if index != -1:
                # 删除 "Asph" 开头的固定长度部分
                lens_info = lens_info[:index].strip()

        print("Modified Lens Info:", lens_info)

        print("Lens Info:", lens_info)

    # focal_length_value = focal_length[0] / focal_length[1] # 实际焦距
    focal_length_value = focal_length_35 # 35mm焦距
    f_number_value = f_number[0] / f_number[1]
    exposure_time_value = exposure_time[0] / exposure_time[1]

    camera_info = f"{lens_info}\n{camera_model}"
    shooting_info = f"{focal_length_value}mm f/{f_number_value} 1/{int(1 / exposure_time_value)}s ISO{iso_speed}\n{datetime}"

    return camera_info, shooting_info

def add_borders_logo_and_text(image_path, logo_path, output_path = None, preview = False):
    # Todo: Add more selections
    image = Image.open(image_path)
    image = reset_image_orientation(image)  # Reset orientation

    camera_info, shooting_info = get_exif_data(image_path)

    border_size = EDGE_WIDTH
    border_size_side = EDGE_WIDTH_SIDE
    new_width = image.width + border_size_side * 2
    new_height = image.height + border_size * 2

    new_image = Image.new("RGB", (new_width, new_height), (255, 255, 255))
    new_image.paste(image, (border_size_side, int(border_size / 2)))

    logo = Image.open(logo_path).convert("RGBA")
    logo_width, logo_height = logo.size
    logo_resize_factor = 200 / logo_height
    logo = logo.resize((int(logo_width * logo_resize_factor), int(logo_height * logo_resize_factor)), Image.LANCZOS)

    draw = ImageDraw.Draw(new_image)

    font_path_1 = "./fonts/AlibabaPuHuiTi-2-85-Bold.otf"
    font_path_2 = "./fonts/AlibabaPuHuiTi-2-45-Light.otf"
    font1 = ImageFont.truetype(font_path_1, 90)
    font2 = ImageFont.truetype(font_path_2, 90)

    camera_info_lines = camera_info.split('\n')
    shooting_info_lines = shooting_info.split('\n')

    shooting_info_bbox = draw.textbbox((0, 0), shooting_info, font=font1)

    text_y = new_height - 1.5 * border_size + 40
    draw.text((border_size, text_y), camera_info_lines[0], font=font1, fill=(0, 0, 0))
    draw.text((border_size, text_y + 120), camera_info_lines[1], font=font2, fill=(0, 0, 0))

    shooting_info_width = shooting_info_bbox[2] - shooting_info_bbox[0]
    draw.text((new_width - border_size - shooting_info_width, text_y), shooting_info_lines[0], font=font1, fill=(0, 0, 0))
    draw.text((new_width - border_size - shooting_info_width, text_y + 120), shooting_info_lines[1], font=font2, fill=(0, 0, 0))

    new_image.paste(logo,
                    (new_width - border_size - shooting_info_width - logo.size[0] - 200,
                     int(new_height - 1.5 * border_size + int(logo.size[1] / 4))),
                    logo)

    draw.line((new_width - border_size - shooting_info_width - 100,
               int(new_height - 1.5 * border_size + int(logo.size[1] / 4) - 10),
               new_width - border_size - shooting_info_width - 100,
               int(new_height - 1.5 * border_size + int(logo.size[1] / 4) + 10 + logo.size[1])),
              fill=(0, 0, 0),
              width=2)

    if preview:
        return new_image
    else:
        new_image.save(output_path)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = ImageWatermarkApp()
    ex.show()
    sys.exit(app.exec_())
