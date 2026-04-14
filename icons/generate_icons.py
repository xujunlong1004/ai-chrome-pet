from PIL import Image, ImageDraw

# 创建图标函数
def create_icon(size, output_path):
    # 创建空白图像
    image = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # 绘制宠物图标
    pet_size = int(size * 0.875)  # 宠物大小为图标大小的87.5%
    pet_x = (size - pet_size) // 2
    pet_y = (size - pet_size) // 2
    
    # 绘制宠物头部（圆形）
    draw.ellipse([(pet_x, pet_y), (pet_x + pet_size, pet_y + pet_size)], fill='#A8DADC')
    
    # 计算眼睛和嘴巴的大小
    eye_size = int(size * 0.08)
    mouth_width = int(size * 0.16)
    mouth_height = int(size * 0.08)
    
    # 绘制眼睛
    eye_distance = int(size * 0.16)
    eye_y = pet_y + int(pet_size * 0.4)
    left_eye_x = pet_x + (pet_size - eye_distance) // 2
    right_eye_x = left_eye_x + eye_distance
    
    draw.ellipse([(left_eye_x, eye_y), (left_eye_x + eye_size, eye_y + eye_size)], fill='#333333')
    draw.ellipse([(right_eye_x, eye_y), (right_eye_x + eye_size, eye_y + eye_size)], fill='#333333')
    
    # 绘制嘴巴
    mouth_x = pet_x + (pet_size - mouth_width) // 2
    mouth_y = pet_y + int(pet_size * 0.6)
    draw.ellipse([(mouth_x, mouth_y), (mouth_x + mouth_width, mouth_y + mouth_height)], fill='#333333')
    
    # 保存图像
    image.save(output_path, 'PNG')
    print(f"Created icon: {output_path}")

# 生成不同大小的图标
create_icon(16, 'icon16.png')
create_icon(48, 'icon48.png')
create_icon(128, 'icon128.png')
