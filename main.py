from utils.exif_utils import *
from utils.image_utils import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QLabel, QHBoxLayout, QScrollArea, QTableWidget, QTableWidgetItem
from PIL import Image, ImageDraw, ImageFont
from PyQt5.QtGui import QFont, QFontDatabase

import os
import json

EDGE_WIDTH = 400
EDGE_WIDTH_SIDE = 150
FONT_SIZE = 90

IMAGE_SIZE = 6000 * 5000

GLOBAL_FONT_PATH_BOLD = "./fonts/AlibabaPuHuiTi-2-85-Bold.otf"
GLOBAL_FONT_PATH_LIGHT = "./fonts/Roboto-Regular.ttf"


class ImageWatermarkApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        with open('configs/language.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

            self.current_language = config.get('language', 'zh')  # 默认语言为 'en'
        
        with open('configs/i18n.json', 'r', encoding='utf-8') as f:
            self.translations = json.load(f)
        
        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle(self.translations[self.current_language]['window_title'])
        self.setGeometry(100, 100, 1200, 800)
        self.setFixedSize(1500, 1000)
    

        # 创建布局
        main_layout = QtWidgets.QHBoxLayout()

        # 左侧布局
        left_layout = QtWidgets.QVBoxLayout()
        
        bold_font_id = QFontDatabase.addApplicationFont(GLOBAL_FONT_PATH_BOLD)
        light_font_id = QFontDatabase.addApplicationFont(GLOBAL_FONT_PATH_LIGHT)
        bold_font_families = QFontDatabase.applicationFontFamilies(bold_font_id)
        light_font_families = QFontDatabase.applicationFontFamilies(light_font_id)
        bold_qfont = QFont(bold_font_families[0])
        light_qfont = QFont(light_font_families[0]) 
        bold_font = QFont(bold_qfont)
        light_font  = QFont(light_qfont)

        # 创建按钮和标签
        self.images_path_label = QtWidgets.QLabel(self.translations[self.current_language]['images_path'])
        self.images_path_edit = QtWidgets.QLineEdit()
        self.images_browse_button = QtWidgets.QPushButton(self.translations[self.current_language]['browse'])
        
        self.images_path_label.setFont(bold_font)
        self.images_path_edit.setFont(light_font)
        self.images_browse_button.setFont(light_font)
        
        self.logo_path_label = QtWidgets.QLabel(self.translations[self.current_language]['logo_path'])
        self.logo_path_edit = QtWidgets.QLineEdit()
        self.logo_browse_button = QtWidgets.QPushButton(self.translations[self.current_language]['browse'])
        
        self.logo_path_label.setFont(bold_font)
        self.logo_path_edit.setFont(light_font)
        self.logo_browse_button.setFont(light_font)

        self.output_dir_label = QtWidgets.QLabel(self.translations[self.current_language]['output_directory'])
        self.output_dir_edit = QtWidgets.QLineEdit()
        self.output_browse_button = QtWidgets.QPushButton(self.translations[self.current_language]['browse'])
        
        self.output_dir_label.setFont(bold_font)
        self.output_dir_edit.setFont(light_font)
        self.output_browse_button.setFont(light_font)

        self.run_button = QtWidgets.QPushButton(self.translations[self.current_language]['run'])
        self.preview_button = QtWidgets.QPushButton(self.translations[self.current_language]['preview'])
        
        self.run_button.setFont(bold_font)
        self.preview_button.setFont(bold_font)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.preview_button)

        self.exif_info_table = QTableWidget(1, 4)
        self.exif_info_table.setHorizontalHeaderLabels([
            self.translations[self.current_language]['focal_length'],
            self.translations[self.current_language]['aperture'],
            self.translations[self.current_language]['exposure_time'],
            self.translations[self.current_language]['iso']
        ])
        self.exif_info_table.setFixedSize(600, 100)
        self.exif_info_table.horizontalHeader().setStretchLastSection(True)
        self.exif_info_table.verticalHeader().setVisible(False)
        self.exif_info_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.exif_info_table.setStyleSheet("QHeaderView::section { background-color:lightgray }")
        self.exif_info_table.setFont(bold_font)
        
        for i in range(self.exif_info_table.columnCount()):
            self.exif_info_table.horizontalHeaderItem(i).setFont(bold_font)

        # self.set_font(bold_font, self.images_path_label, self.images_path_edit, self.images_browse_button,
        #       self.logo_path_label, self.logo_path_edit, self.logo_browse_button,
        #       self.output_dir_label, self.output_dir_edit, self.output_browse_button,
        #       self.run_button, self.preview_button, self.exif_info_table)



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
        self.scroll_area_selected.setWidget(self.selected_image_label)
        self.scroll_area_selected.setWidgetResizable(True)
        self.scroll_area_selected.setFixedSize(600, 400)

        left_layout.addWidget(self.scroll_area_selected, stretch = 3)
        right_layout.addWidget(self.scroll_area, stretch = 3)

        # 将左右布局添加到主布局
        main_layout.addLayout(left_layout, stretch = 1)
        main_layout.addLayout(right_layout, stretch = 1)

        self.setLayout(main_layout)

        # 设置样式表
        self.setStyleSheet("""
            QWidget {
                font-size: 16px;
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
                font-weight: light;
                background-color: #45a049;
            }
            QLabel {
                font-size: 18px;
            }
        """)

        # 连接信号和槽
        self.images_browse_button.clicked.connect(self.browse_images)
        self.logo_browse_button.clicked.connect(self.browse_logo)
        self.output_browse_button.clicked.connect(self.browse_output_dir)
        self.run_button.clicked.connect(self.run)
        self.preview_button.clicked.connect(self.preview)

    def set_font(self, font, *widgets):
        """设置多个控件的字体"""
        for widget in widgets:
            widget.setFont(font)
    
    def show_message_box(self, title, text, msg_type='information'):
        bold_font_id = QFontDatabase.addApplicationFont(GLOBAL_FONT_PATH_BOLD)
        bold_font_families = QFontDatabase.applicationFontFamilies(bold_font_id)
        bold_qfont = QFont(bold_font_families[0])
        bold_font = QFont(bold_qfont)
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setFont(bold_font)
        if msg_type == 'information':
            msg_box.setIcon(QMessageBox.Information)
        elif msg_type == 'warning':
            msg_box.setIcon(QMessageBox.Warning)
        elif msg_type == 'critical':
            msg_box.setIcon(QMessageBox.Critical)
        elif msg_type == 'question':
            msg_box.setIcon(QMessageBox.Question)
        
        msg_box.exec_()

    def browse_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Images', '', 'Image Files (*.jpg *.jpeg *.png)')
        if files:
            self.images_path_edit.setText(';'.join(files))
            if get_manufacturer(files[0]) is not None:
                manufacturer = get_manufacturer(files[0])
                logo_path = find_logo(manufacturer)
                if logo_path:
                    self.logo_path_edit.setText(logo_path)
            else :
                self.show_message_box(self.translations[self.current_language]['no_device_title'], 
                                      self.translations[self.current_language]['no_device'], 
                                      'critical')
                # return
            
            self.display_exif_info(files[0])
            self.display_selected_image(files[0])  # 显示选定的图片


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
            self.show_message_box(self.translations[self.current_language]['input_error'], 
                                  self.translations[self.current_language]['invalid_path'], 
                                  'critical')
            return

        for image_path in images_paths:
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(output_dir, f"{name}_watermark{ext}")
            
            manufacturer = get_manufacturer(image_path)
            if manufacturer is not None:
                logo_path = find_logo(manufacturer)
            res = add_borders_logo_and_text(image_path, logo_path, output_path)
            if res is None:
                return
        self.show_message_box(self.translations[self.current_language]['success_title'], 
                              self.translations[self.current_language]['success'], 
                              'information')

    def preview(self):
        images_paths = self.images_path_edit.text().split(';')
        logo_path = self.logo_path_edit.text()

        if not images_paths or not logo_path:
            self.show_message_box(self.translations[self.current_language]['error_title'], 
                                  self.translations[self.current_language]['logo_error'], 
                                  'critical')
            return

        preview_image_path = images_paths[0]
        preview_image = add_borders_logo_and_text(preview_image_path, logo_path, preview=True)
        if preview_image is not None:
            self.display_preview(preview_image)

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
            self.show_message_box(self.translations[self.current_language]['error_title'], 
                                  self.translations[self.current_language]['exif_error'],
                                  'critical')
            return None

def add_borders_logo_and_text(image_path, logo_path, output_path = None, preview = False):
    # Todo: Add more selections
    image = Image.open(image_path)
    image = reset_image_orientation(image)  # Reset orientation
    exif_dict = None
    exif_bytes = None
    app_instance = ImageWatermarkApp()
    
    try:
        exif_dict = piexif.load(image.info.get('exif', b''))
        exif_bytes = piexif.dump(exif_dict)
    except Exception as e:
        app_instance.show_message_box(
                              app_instance.translations[app_instance.current_language]['error_title'], 
                              app_instance.translations[app_instance.current_language]['exif_error'],
                              'critical')
        return None

    result = get_exif_data(image_path)
    if result is not None:
        camera_info, shooting_info = result

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

    font_bold = ImageFont.truetype(GLOBAL_FONT_PATH_BOLD, 100)
    font_light = ImageFont.truetype(GLOBAL_FONT_PATH_LIGHT, 100)

    camera_info_lines = camera_info.split('\n')
    shooting_info_lines = shooting_info.split('\n')

    shooting_info_bbox = draw.textbbox((0, 0), shooting_info, font=font_bold)

    text_y = new_height - 1.5 * border_size + 120
    draw.text((border_size, text_y), camera_info_lines[0], font=font_bold, fill=(0, 0, 0))
    draw.text((border_size, text_y + 120), camera_info_lines[1], font=font_light, fill=(0, 0, 0))

    shooting_info_width = shooting_info_bbox[2] - shooting_info_bbox[0]
    draw.text((new_width - border_size - shooting_info_width, text_y), shooting_info_lines[0], font=font_bold, fill=(0, 0, 0))
    draw.text((new_width - border_size - shooting_info_width, text_y + 120), shooting_info_lines[1], font=font_light, fill=(0, 0, 0))

    new_image.paste(logo,
                    (new_width - border_size - shooting_info_width - logo.size[0] - 200,
                     int(new_height - 1.5 * border_size + 80 + int(logo.size[1] / 4))),
                    logo)

    draw.line((new_width - border_size - shooting_info_width - 100,
               int(new_height - 1.5 * border_size + 80 + int(logo.size[1] / 4) - 10),
               new_width - border_size - shooting_info_width - 100,
               int(new_height - 1.5 * border_size + 80 + int(logo.size[1] / 4) + 10 + logo.size[1])),
              fill=(0, 0, 0),
              width=2)

    if preview:
        return new_image
    else:
        new_image.save(output_path, exif=exif_bytes)  # 保留exif数据

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ex = ImageWatermarkApp()
    ex.show()
    sys.exit(app.exec_())
