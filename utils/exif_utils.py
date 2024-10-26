from PIL import Image
import piexif
import subprocess
import os

def convert_to_int(value):
    if isinstance(value, tuple):
        print("isTuple")
        return int(value[0])
    elif isinstance(value, int):
        # 如果已经是整数，直接返回
        return value
    elif isinstance(value, str):
        # 如果是字符串，尝试将其转换为整数
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Cannot convert string to int: '{value}'")
    else:
        # 其他类型可以选择抛出异常或处理
        raise ValueError("Unsupported type")
    
def get_manufacturer(image_path):
    try:
        image = Image.open(image_path)
        exif_dict = piexif.load(image.info['exif'])
        manufacturer = exif_dict['0th'].get(piexif.ImageIFD.Make, b"").decode().strip()
        for letter in manufacturer:
            if letter in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                continue
            else:
                manufacturer = manufacturer.replace(letter, '')
        return manufacturer
    except KeyError:
        return None
    except Exception as e:
        print(f"Error getting manufacturer: {e}")
        return None

def find_logo(manufacturer):
    logo_dir = "./logos"
    if not os.path.isdir(logo_dir):
        logo_dir = "D:/摄影/tool/auto_watermark/logos"  # 替换为你的logo文件夹路径
    for root, dirs, files in os.walk(logo_dir):
        for file in files:
            if file.lower().startswith(manufacturer.lower().split()[0]) \
                    or manufacturer.lower().startswith(file.lower().split('.')[0]):
                return os.path.join(root, file)
    return None

def get_exif_table(image_path):
    try:
        image = Image.open(image_path)
        exif_dict = piexif.load(image.info['exif'])
        exif_data = exif_dict['Exif']

        focal_length_35 = exif_data.get(piexif.ExifIFD.FocalLengthIn35mmFilm, (0, 1))
        #Some photos don't have focal length in 35mm film
        if focal_length_35 == (0, 1):
            focal_length = exif_data.get(piexif.ExifIFD.FocalLength, (0, 1))
            focal_length_35 = convert_to_int(focal_length)
        
        f_number = exif_data.get(piexif.ExifIFD.FNumber, (0, 1))
        exposure_time = exif_data.get(piexif.ExifIFD.ExposureTime, (0, 1))
        iso_speed = exif_data.get(piexif.ExifIFD.ISOSpeedRatings, 0)
        
        print(focal_length_35)

        focal_length_value = focal_length_35  # 35mm 焦距
        f_number_value = f_number[0] / f_number[1] if f_number[1] != 0 else 0
        exposure_time_value = exposure_time[0] / exposure_time[1] if exposure_time[1] != 0 else 0

        return focal_length_value, f_number_value, exposure_time_value, iso_speed
    except KeyError:
        return None, None, None, None
    except Exception as e:
        print(f"Error getting EXIF table: {e}")
        return None, None, None, None

def get_exif_data(image_path):
    dji_models = {
        'FC8482': 'DJI Mini 4 Pro',
        'FC7703': 'DJI Mini 2 SE'
        # todo: need to add more dji models
    }

    try:
        image = Image.open(image_path)
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
    
        focal_length_value, f_number_value, exposure_time_value, iso_speed = get_exif_table(image_path)
        
        datetime = exif_data.get(piexif.ExifIFD.DateTimeOriginal, b"Unknown Date").decode()
        date_part, time_part = datetime.split(" ")
        formatted_date = date_part.replace(":", "-")
        datetime = f"{formatted_date} {time_part}"
        
        camera_model = dji_models.get(camera_model_code, camera_model_code) #In case dji has unknown model code

        # Format shooting_info only if values are valid
        if focal_length_value and f_number_value and exposure_time_value:
            shooting_info = f"{focal_length_value}mm f/{f_number_value} 1/{int(1 / exposure_time_value)}s ISO{iso_speed}\n{datetime}"
        else:
            shooting_info = "Invalid shooting info\n" + datetime

        camera_info = f"{lens_info}\n{camera_model}"

        return camera_info, shooting_info
    except KeyError:
        return None, None
    except Exception as e:
        print(f"Error getting EXIF data: {e}")
        return None, None

