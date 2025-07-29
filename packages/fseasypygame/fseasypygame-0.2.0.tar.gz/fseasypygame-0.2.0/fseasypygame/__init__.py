import math  # 导入数学模块，用于执行数学运算
import os  # 导入操作系统模块，用于处理文件和目录
import sys  # 导入系统模块，用于访问与 Python 解释器紧密相关的变量和函数
import time  # 导入时间模块，用于处理时间相关的任务
import inspect  # 确保模块顶部引入 inspect
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from fseasypygame import GameObject

import pygame  # 导入 pygame 模块，用于游戏开发

game_instance = None  # 初始化游戏实例变量为 None


# 定义 Animation 类，用于处理动画
class Animation:
    # 初始化函数，设置动画的各种属性
    def __init__(self, frame_image_names, frame_rate, destroy=False, revert=True, width=None, height=None,
                 repeat_count=1):
        self.frames = [pygame.image.load(name) for name in frame_image_names]  # 加载每一帧的图像
        self.frame_rate = frame_rate  # 设置帧率
        self.current_frame = 0  # 当前帧的索引
        self.frame_count = 0  # 总帧数
        self.destroy = destroy  # 是否在播放完毕后销毁动画
        self.revert = revert  # 是否在播放完毕后恢复到初始状态
        self.width = width  # 动画的宽度
        self.height = height  # 动画的高度
        self.repeat_count = repeat_count  # 重复播放次数


# 定义 GameText 类，用于在游戏中显示文本
class GameText:
    # 初始化函数，设置文本的各种属性
    def __init__(self, text, x=0, y=0, font_size=24, font_color=(0, 0, 0)):
        self.text = text  # 文本内容
        self.x = x  # 文本在屏幕上的 x 坐标
        self.y = y  # 文本在屏幕上的 y 坐标
        self.font_size = font_size  # 字体大小
        self.font_color = font_color  # 字体颜色
        self.visible = True  # 文本是否可见
        self.font = pygame.font.Font(None, self.font_size)  # 创建字体对象
        game_instance.add_game_text(self)  # 将文本对象添加到游戏实例中

    # 设置文本内容的方法
    def set_text(self, text):
        self.text = text

    # 设置字体大小的方法
    def set_font_size(self, font_size):
        self.font_size = font_size  # 更新字体大小
        self.font = pygame.font.Font(None, self.font_size)  # 重新创建字体对象以应用新的大小

    # 设置字体颜色的方法
    def set_font_color(self, font_color):
        self.font_color = font_color  # 更新字体颜色

    # 切换文本可见性的方法
    def toggle_visibility(self):
        self.visible = not self.visible  # 切换文本的可见性状态

    # 销毁文本对象的方法
    def destroy(self):
        game_instance.remove_game_text(self)  # 从游戏实例中移除该文本对象

    # 在屏幕上绘制文本的方法
    def draw(self, surface):
        if self.visible:
            text_surface = self.font.render(self.text, True, self.font_color)  # 创建文本的表面对象
            surface.blit(text_surface, (self.x, self.y))  # 在指定位置绘制文本


# 定义 GroupManager 类，用于管理游戏中的精灵组
class GroupManager:
    # 初始化函数
    def __init__(self):
        self.groups = {}  # 存储所有精灵组的字典

    # 获取指定名称的精灵组
    def get_group(self, group_name):
        return self.groups.get(group_name, None)  # 如果存在则返回组，否则返回 None

    # 将精灵添加到指定的组中
    def add_to_group(self, sprite, group_name):
        if group_name not in self.groups:  # 如果组不存在，则创建新组
            self.groups[group_name] = pygame.sprite.Group()  # 创建新的精灵组
        self.groups[group_name].add(sprite)  # 将精灵添加到组中
        sprite.group = self.groups[group_name]  # 更新精灵的组属性

    # 从组中移除精灵的方法
    def remove_from_group(self, sprite, group_name):
        group = self.groups.get(group_name, None)  # 获取指定名称的组
        if group is not None and sprite in group:  # 如果组存在且精灵在组中
            group.remove(sprite)  # 从组中移除精灵
            sprite.group = None  # 清除精灵的组属性


# 定义 KeyStatus 类，用于处理键盘按键的状态
class KeyStatus:
    # 初始化函数
    def __init__(self):
        self.pressed = False  # 按键是否被按下
        self.triggered_time = time.time()  # 最后一次触发的时间
        self.interval = 0.2  # 触发间隔时间
        self.released = False  # 按键是否被释放

    # 设置触发间隔时间的方法
    def set_interval(self, interval):
        self.interval = interval  # 更新间隔时间

    # 检查按键是否被触发的方法
    def is_triggered(self):
        return self.pressed  # 返回按键是否被按下

    # 带间隔时间检查的触发方法
    def is_triggered_with_interval(self):
        if self.pressed and time.time() - self.triggered_time > self.interval:  # 如果按键被按下且超过了间隔时间
            self.triggered_time = time.time()  # 重置触发时间
            return True  # 返回 True 表示触发
        return False  # 否则返回 False

    # 处理按键释放的方法
    def handle_keyup(self):
        self.pressed = False  # 更新按键状态为未按下
        self.released = True  # 更新按键状态为已释放

    # 重置按键释放状态的方法
    def reset_released(self):
        self.released = False  # 重置释放状态


# 定义 Keys 类，用于映射和处理键盘按键
class Keys:
    key_mapping = {
        'LEFT': pygame.K_LEFT,  # 左键
        'RIGHT': pygame.K_RIGHT,  # 右键
        'UP': pygame.K_UP,  # 上键
        'DOWN': pygame.K_DOWN,  # 下键
        'SPACE': pygame.K_SPACE,  # 空格键
        'A': pygame.K_a,  # 字母 A 键
        'B': pygame.K_b,  # 字母 B 键
        'C': pygame.K_c,  # 字母 C 键
        'D': pygame.K_d,  # 字母 D 键
        'E': pygame.K_e,  # 字母 E 键
        'F': pygame.K_f,  # 字母 F 键
        'G': pygame.K_g,  # 字母 G 键
        'H': pygame.K_h,  # 字母 H 键
        'I': pygame.K_i,  # 字母 I 键
        'J': pygame.K_j,  # 字母 J 键
        'K': pygame.K_k,  # 字母 K 键
        'L': pygame.K_l,  # 字母 L 键
        'M': pygame.K_m,  # 字母 M 键
        'N': pygame.K_n,  # 字母 N 键
        'O': pygame.K_o,  # 字母 O 键
        'P': pygame.K_p,  # 字母 P 键
        'Q': pygame.K_q,  # 字母 Q 键
        'R': pygame.K_r,  # 字母 R 键
        'S': pygame.K_s,  # 字母 S 键
        'T': pygame.K_t,  # 字母 T 键
        'U': pygame.K_u,  # 字母 U 键
        'V': pygame.K_v,  # 字母 V 键
        'W': pygame.K_w,  # 字母 W 键
        'X': pygame.K_x,  # 字母 X 键
        'Y': pygame.K_y,  # 字母 Y 键
        'Z': pygame.K_z,  # 字母 Z 键
    }


# 继承自 pygame.sprite.Sprite，用于表示游戏中的对象
class GameObject(pygame.sprite.Sprite):
    def __init__(self, img_path, x=0, y=0, width=None, height=None, name=None, group_name=None, rotation_angle=0):
        super().__init__()  # 调用父类构造函数
        image = pygame.image.load(img_path)  # 加载图片
        # 设置图片大小
        if width and height:
            self.image = pygame.transform.scale(image, (width, height))
            self._width = width
            self._height = height
        else:
            self.image = image
            self._width = image.get_width()
            self._height = image.get_height()
        # 图片旋转
        if rotation_angle != 0:
            self.image = pygame.transform.rotate(self.image, rotation_angle)
        self.name = name  # 对象名称
        self.center_x = x  # 对象中心x坐标
        self.center_y = y  # 对象中心y坐标
        self.collided_callback = None  # 碰撞回调函数
        self.rect = self.image.get_rect()  # 图片的矩形区域
        self.angle = 90  # 初始角度
        self.original_image = self.image.copy()  # 原始图片
        self.destroyCallback = None  # 销毁时的回调函数
        self.rect.topleft = (self.x, self.y)  # 矩形的左上角位置
        self.original_rect = self.image.get_rect().copy()  # 原始矩形区域
        self.collision_scale_factor = 1.0  # 碰撞区域缩放因子
        self.scaled_size = self.rect.size  # 缩放后的尺寸
        self.drawRect = False  # 是否绘制矩形
        # 添加到指定组或默认组
        if group_name:
            group_manager.add_to_group(self, group_name)
        else:
            default_group_name = os.path.splitext(os.path.basename(img_path))[0]
            group_manager.add_to_group(self, default_group_name)
        self.animations = {}  # 动画字典
        self.current_animation = None  # 当前动画
        self.destroy_after_animation = False  # 动画后是否销毁
        self.revert_to_original_after_animation = True  # 动画后是否恢复原始状态
        self.alive = True  # 对象是否存活
        self.animation_repeat_counts = {}  # 动画重复次数
        self.current_animation_repeat = 0  # 当前动画重复次数
        self.current_animation_name = None  # 当前动画名称

    def set_image_size(self, width, height):
        # 缩放原始图片到新的尺寸
        self.original_image = pygame.transform.scale(self.original_image, (width, height))
        if self.current_animation:
            # 如果当前有动画，更新每一帧的大小
            self.current_animation.frames = [pygame.transform.scale(frame, (width, height)) for frame in
                                             self.current_animation.frames]
        # 更新当前显示的图片
        self.image = self.original_image.copy()
        # 更新缩放后的尺寸和矩形区域
        self.scaled_size = (width, height)
        self.rect = self.image.get_rect()
        self.original_rect = self.image.get_rect().copy()
        # 更新矩形区域的中心位置
        self.rect.center = (self.center_x, self.center_y)

    def changeImage(self, image):
        # 加载新的图片
        image = pygame.image.load(image)
        # 将新图片缩放到指定大小
        self.image = pygame.transform.scale(image, (self._width, self._height))

    def rotate(self, angle):
        if not self.alive:
            return
        # 选择当前动画帧或原始图片进行旋转
        image_to_rotate = self.current_animation.frames[
            self.current_animation.current_frame] if self.current_animation else self.original_image
        # 应用旋转
        self.angle += angle
        self.image = pygame.transform.rotate(image_to_rotate, self.angle - 90)
        # 保持图片的中心位置不变
        original_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = original_center
        # 应用碰撞区域调整
        self.apply_collision_adjustment()

    @property
    def x(self):
        # 获取对象的x坐标（中心点向左偏移半个宽度）
        return self.center_x - self.width // 2

    @x.setter
    def x(self, x):
        # 设置对象的x坐标（实际上设置的是中心点的位置）
        self.center_x = x + self.width // 2

    @property
    def y(self):
        # 获取对象的y坐标（中心点向上偏移半个高度）
        return self.center_y - self.height // 2

    @y.setter
    def y(self, y):
        # 设置对象的y坐标（实际上设置的是中心点的位置）
        self.center_y = y + self.height // 2

    @property
    def width(self):
        # 返回对象的宽度，如果没有设置则返回图片的宽度
        return self._width if self._width else self.image.get_width()

    @property
    def height(self):
        # 返回对象的高度，如果没有设置则返回图片的高度
        return self._height if self._height else self.image.get_height()

    def set_collided_callback(self, callback):
        # 设置当发生碰撞时调用的回调函数
        self.collided_callback = callback

    def move(self, dx, dy):
        if not self.alive:
            return
        # 按指定的偏移量移动对象
        self.center_x += dx
        self.center_y += dy
        # 更新对象的矩形位置
        self.rect.topleft = (self.x, self.y)
        # 应用碰撞区域调整
        self.apply_collision_adjustment()

    def up(self, speed):
        if not self.alive:
            return
        # 向上移动对象
        self.center_y -= speed
        self.rect.center = (self.center_x, self.center_y)
        self.apply_collision_adjustment()

    def down(self, speed):
        if not self.alive:
            return
        # 向下移动对象
        self.center_y += speed
        self.rect.center = (self.center_x, self.center_y)
        self.apply_collision_adjustment()

    def left(self, speed):
        if not self.alive:
            return
        # 向左移动对象
        self.center_x -= speed
        self.rect.center = (self.center_x, self.center_y)
        self.apply_collision_adjustment()

    def right(self, speed):
        if not self.alive:
            return
        # 向右移动对象
        self.center_x += speed
        self.rect.center = (self.center_x, self.center_y)
        self.apply_collision_adjustment()

    def goto(self, x, y):
        if not self.alive:
            return
        # 设置对象的中心坐标
        self.center_x = x
        self.center_y = y
        # 更新对象的矩形位置
        self.rect.topleft = (self.x, self.y)
        # 应用碰撞区域调整
        self.apply_collision_adjustment()

    def face_towards(self, target):
        if not self.alive or not target.alive:
            return
        # 计算与目标对象的x和y坐标差
        dx = target.getX() - self.getX()
        dy = target.getY() - self.getY()
        # 计算角度并设置对象朝向
        angle = math.degrees(math.atan2(-dy, dx))
        self.setAngel(angle)

    def destroy(self):
        # 设置对象为不活动状态
        self.set_alive(False)
        if self.destroyCallback != None:
            # 如果设置了销毁回调，则调用
            self.destroyCallback()
        # 从所有群组中移除此对象
        self.kill()

    def draw(self, surface):
        # 在指定的表面上绘制游戏对象的图像
        surface.blit(self.image, (self.x, self.y))
        if game_instance.get_draw_rect_flag():
            # 如果设置了绘制矩形标志，绘制对象的边框
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)

    def adjust_collision_area(self, scale_factor):
        # 设置碰撞区域的缩放因子
        self.collision_scale_factor = scale_factor
        self.apply_collision_adjustment()

    def apply_collision_adjustment(self):
        # 根据缩放因子调整碰撞区域的大小
        center = self.rect.center
        self.rect.width = int(self.original_rect.width * self.collision_scale_factor)
        self.rect.height = int(self.original_rect.height * self.collision_scale_factor)
        self.rect.center = center

    def setAngel(self, angle):
        if not self.alive:
            return
        # 更新角度
        self.angle = angle
        # 选择当前动画帧或原始图片进行旋转
        image_to_rotate = self.current_animation.frames[
            self.current_animation.current_frame] if self.current_animation else self.original_image
        # 应用旋转
        self.image = pygame.transform.rotate(image_to_rotate, self.angle - 90)
        # 保持图片的中心位置不变
        original_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = original_center
        # 更新对象的矩形位置
        self.rect.topleft = (self.x, self.y)
        # 应用碰撞区域调整
        self.apply_collision_adjustment()

    def move_forward(self, speed):
        if not self.alive:
            return
        # 根据当前角度计算前进方向
        dx = math.cos(math.radians(self.angle)) * speed
        dy = -math.sin(math.radians(self.angle)) * speed
        # 更新位置
        self.x += dx
        self.y += dy
        self.rect.center = (self.center_x, self.center_y)
        # 应用碰撞区域调整
        self.apply_collision_adjustment()

    def getX(self):
        return self.center_x

    def getY(self):
        return self.center_y

    def getAngel(self):
        return self.angle

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getRect(self):
        return self.rect

    def getImage(self):
        return self.image

    def getCenter(self):
        return self.rect.center

    def getCenterX(self):
        return self.rect.centerx

    def getCenterY(self):
        return self.rect.centery

    def is_outof_border(self):
        # 检查对象是否超出游戏屏幕的边界
        return self.x > game_instance.screen_width + self.width or self.x < 0 - self.width or self.y > game_instance.screen_height + self.height or self.y < 0 - self.height

    def set_group(self, new_group_name):
        # 从当前组移除并添加到新的组
        if self.group:
            old_group_name = [name for name, group in group_manager.groups.items() if self.group == group][0]
            group_manager.remove_from_group(self, old_group_name)
        group_manager.add_to_group(self, new_group_name)

    def check_collision(self, target_group_name, dokill=False, target_animation_name=None):
        if not self.alive:
            return
        # 获取目标组
        target_group = group_manager.get_group(target_group_name)
        if not target_group:
            return False
        # 检测碰撞
        collision_sprite = pygame.sprite.spritecollideany(self, target_group)
        if collision_sprite:
            if not collision_sprite.alive:
                return False
            if dokill:
                # 如果设置了dokill，销毁碰撞的对象
                collision_sprite.set_alive(False)
                if target_animation_name:
                    # 如果指定了动画，启动动画
                    collision_sprite.startAnimation(target_animation_name)
                else:
                    # 否则直接销毁对象
                    collision_sprite.destroy()
            elif target_animation_name:
                # 如果指定了动画但没有设置dokill，只启动动画
                collision_sprite.startAnimation(target_animation_name)
            return True
        return False

    def onDestroy(self, fun):
        # 设置销毁回调函数
        self.destroyCallback = fun

    def addAnimation(self, animation_name, animation):
        # 添加动画到对象的动画字典
        self.animations[animation_name] = animation
        # 设置动画的重复次数
        self.animation_repeat_counts[animation_name] = animation.repeat_count
        if animation.width and animation.height:
            # 调整动画帧的大小
            resized_frames = [pygame.transform.scale(frame, (animation.width, animation.height)) for frame in
                              animation.frames]
            animation.frames = resized_frames

    def startAnimation(self, animation_name):
        # 启动指定名称的动画
        if animation_name in self.animations:
            self.current_animation = self.animations[animation_name]
            self.current_animation.current_frame = 0
            self.current_animation_name = animation_name
            self.current_animation_repeat = 0
            if self.current_animation.destroy:
                # 如果动画设置了结束时销毁对象，则标记对象为不活动
                self.alive = False

    def stopAnimation(self):
        # 停止当前动画
        self.current_animation = None
        self.current_animation_name = None

    def removeAnimation(self, animation_name):
        # 从对象中移除指定名称的动画
        if animation_name in self.animations:
            del self.animations[animation_name]

    def update(self):
        animation_completed = False
        if self.current_animation:
            # 处理当前动画的帧
            destroy = self.current_animation.destroy
            revert = self.current_animation.revert
            repeat_count = self.current_animation.repeat_count
            self.current_animation.frame_count += 1
            if self.current_animation.frame_count % self.current_animation.frame_rate == 0:
                self.current_animation.current_frame += 1
                if self.current_animation.current_frame >= len(self.current_animation.frames):
                    self.current_animation_repeat += 1
                    if repeat_count != -1 and self.current_animation_repeat >= repeat_count:
                        # 动画播放完成
                        animation_completed = True
                        if destroy:
                            # 销毁对象
                            revert = False
                            self.destroy()
                        if revert:
                            # 恢复到原始图像
                            self.image = self.original_image
                        self.stopAnimation()
                    else:
                        self.current_animation.current_frame = 0
                if not animation_completed:
                    # 更新当前显示的图像
                    self.image = self.current_animation.frames[self.current_animation.current_frame]

    def set_alive(self, alive_status):
        # 设置对象的活动状态
        self.alive = alive_status
        if not self.alive:
            # 如果对象不活动，则清空矩形区域
            self.rect = pygame.Rect(0, 0, 0, 0)

    def __hash__(self):
        # 使用对象的ID作为哈希值
        return id(self)

    def __eq__(self, other):
        # 判断两个对象是否相同，基于它们的ID
        return id(self) == id(other)

    # 获取中心点横坐标
    def get_center_x(self):
        return self.center_x

    # 获取中心点纵坐标
    def get_center_y(self):
        return self.center_y


# 用于创建和管理游戏环境的类
class Game:
    def __init__(self, width, height):
        global game_instance
        pygame.init()  # 初始化pygame库
        self.screen_width = width  # 设置游戏屏幕宽度
        self.screen_height = height  # 设置游戏屏幕高度
        # 创建一个窗口或屏幕用于显示
        self.surface = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()  # 创建一个时钟对象，用于控制游戏帧率
        self.update_func = None  # 设置一个可选的更新函数，可以在游戏循环中被调用
        game_instance = self  # 将当前实例赋值给全局变量，方便其他地方引用
        # 创建一个字典来存储键盘的按键状态
        self.key_status = {key: KeyStatus() for key in Keys.key_mapping.keys()}
        self.drawRect = False  # 用于控制是否绘制矩形（可能用于调试或其他目的）
        self.game_texts = []  # 存储游戏中的文本对象
        self.background = None  # 游戏背景，默认为None
        self.background_image = None  # 背景图像的Surface对象（静态或滚动通用）
        self.scroll_enabled = False  # 是否启用滚动背景模式
        self.scroll_direction = 'up'  # 背景滚动方向，默认向上
        self.scroll_speed = 0  # 滚动速度（像素/帧）
        # 用于记录两张背景图像的当前位置（实现无缝衔接滚动）
        self.bg_x1 = 0
        self.bg_y1 = 0
        self.bg_x2 = 0
        self.bg_y2 = 0

    def set_scrolling_background(self, image_path, direction='up', speed=1):
        """设置可滚动的背景图像。
        参数:
            image_path: 背景图像文件的路径
            direction: 滚动方向，可选 'up'（向上）, 'down'（向下）, 'left'（向左）, 'right'（向右）
            speed: 滚动速度，单位为像素/帧
        """
        # 加载背景图像并转换为Surface对象（convert可以提高渲染效率）
        bg_image = pygame.image.load(image_path).convert()
        self.background_image = pygame.transform.scale(bg_image, (self.screen_width, self.screen_height))
        # self.background_image = bg_image
        # 设置滚动方向和速度
        self.scroll_direction = direction
        self.scroll_speed = speed
        # 获取背景图像的宽度和高度，用于计算循环滚动的位置
        bg_rect = self.background_image.get_rect()
        bg_width, bg_height = bg_rect.width, bg_rect.height
        # 根据滚动方向，初始化两张背景图片的起始坐标，以实现无缝滚动衔接
        if direction == 'up':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = 0, bg_height  # 第二张背景在第一张的正下方
        elif direction == 'down':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = 0, -bg_height  # 第二张背景在第一张的正上方
        elif direction == 'left':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = bg_width, 0  # 第二张背景在第一张的正右方
        elif direction == 'right':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = -bg_width, 0  # 第二张背景在第一张的正左方
        else:
            # 如传入无效的方向参数，默认改为向上滚动
            self.scroll_direction = 'up'
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = 0, bg_height
        # 启用滚动背景模式（将通过游戏循环自动滚动背景）
        self.scroll_enabled = True

    def set_scroll_direction(self, direction):
        """动态设置背景滚动方向"""
        self.scroll_direction = direction
        w, h = self.background_image.get_width(), self.background_image.get_height()
        if direction == 'up':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = 0, h
        elif direction == 'down':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = 0, -h
        elif direction == 'left':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = w, 0
        elif direction == 'right':
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = -w, 0
        else:
            self.scroll_direction = 'up'
            self.bg_x1, self.bg_y1 = 0, 0
            self.bg_x2, self.bg_y2 = 0, h

    def set_scroll_speed(self, speed):
        """动态设置滚动速度"""
        self.scroll_speed = speed

    def add_game_text(self, game_text):
        self.game_texts.append(game_text)  # 将一个新的游戏文本对象添加到列表中

    def remove_game_text(self, game_text):
        self.game_texts.remove(game_text)  # 从列表中移除指定的游戏文本对象

    def set_draw_rect_flag(self, flag):
        self.drawRect = flag  # 设置drawRect标志

    def get_draw_rect_flag(self):
        return self.drawRect  # 获取drawRect标志的当前状态

    def setUpdateFunction(self, fun):
        self.update_func = fun  # 设置更新函数

    def set_background(self, bg_path):
        image = pygame.image.load(bg_path)  # 加载背景图像
        # 将图像缩放到和屏幕一样的大小
        self.background = pygame.transform.scale(image, (self.screen_width, self.screen_height))

    def mark_game_object_for_removal(self, game_object):
        self.objects_marked_for_removal.append(game_object)  # 添加要移除的游戏对象到列表

    def is_key_pressed(self, keyname):
        keyname = keyname.upper()  # 将键名转换为大写
        return self.key_status[keyname].is_triggered()  # 返回键是否被触发

    def is_pressed_withinterval(self, keyname):
        keyname = keyname.upper()  # 将键名转换为大写
        return self.key_status[keyname].is_triggered_with_interval()  # 返回键是否在特定间隔内被触发

    def setkey_interval(self, keyname, interval):
        keyname = keyname.upper()  # 将键名转换为大写
        self.key_status[keyname].set_interval(interval)  # 设置检测间隔

    def get_active_objects_in_group(self, group_name) -> List['GameObject']:
        group = group_manager.get_group(group_name)  # 获取指定组
        if not group:
            return []
        # 返回组内存活的对象
        active_objects = [sprite for sprite in group if sprite.alive]
        return active_objects

    def get_count_in_group(self, group_name):
        group = group_manager.get_group(group_name)  # 获取指定组
        if not group:
            return 0
        return len(group)  # 返回组内对象的数量

    def is_key_released(self, keyname):
        keyname = keyname.upper()  # 将键名转换为大写
        if keyname in self.key_status:
            return self.key_status[keyname].released
        return False

    def get_scroll_speed(self):
        """获取当前背景滚动速度"""
        return self.scroll_speed

    def run(self, FPS=60):

        # 自动查找调用者作用域中的 update 函数
        if self.update_func is None:
            caller_globals = inspect.stack()[1].frame.f_globals
            if 'update' in caller_globals and callable(caller_globals['update']):
                self.update_func = caller_globals['update']

        while True:  # 无限循环，直到游戏结束
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # 检测到退出事件
                    pygame.quit()  # 退出pygame
                    sys.exit()  # 退出程序
                elif event.type == pygame.KEYUP:  # 键被释放
                    keyname = pygame.key.name(event.key).upper()
                    if keyname in self.key_status:
                        self.key_status[keyname].handle_keyup()
            keys = pygame.key.get_pressed()
            for key, status in self.key_status.items():
                status.pressed = keys[Keys.key_mapping[key]]
            if self.background != None:
                self.surface.blit(self.background, (0, 0))
            if self.update_func != None:
                self.update_func()  # 调用更新函数
            self.objects_marked_for_removal = []  # 重置要移除的对象列表

            # **更新滚动背景的位置**
            if self.scroll_enabled:
                if self.scroll_direction == 'up':
                    # 背景向上滚动，纵坐标递减
                    self.bg_y1 -= self.scroll_speed
                    self.bg_y2 -= self.scroll_speed
                    # 如果第一张背景滚出屏幕上方，则将其移到第二张背景下方
                    if self.bg_y1 <= -self.background_image.get_height():
                        self.bg_y1 = self.bg_y2 + self.background_image.get_height()
                    # 如果第二张背景也滚出屏幕上方，则将其移到第一张背景下方
                    if self.bg_y2 <= -self.background_image.get_height():
                        self.bg_y2 = self.bg_y1 + self.background_image.get_height()
                elif self.scroll_direction == 'down':
                    # 背景向下滚动，纵坐标递增
                    self.bg_y1 += self.scroll_speed
                    self.bg_y2 += self.scroll_speed
                    if self.bg_y1 >= self.background_image.get_height():
                        self.bg_y1 = self.bg_y2 - self.background_image.get_height()
                    if self.bg_y2 >= self.background_image.get_height():
                        self.bg_y2 = self.bg_y1 - self.background_image.get_height()
                elif self.scroll_direction == 'left':
                    # 背景向左滚动，横坐标递减
                    self.bg_x1 -= self.scroll_speed
                    self.bg_x2 -= self.scroll_speed
                    if self.bg_x1 <= -self.background_image.get_width():
                        self.bg_x1 = self.bg_x2 + self.background_image.get_width()
                    if self.bg_x2 <= -self.background_image.get_width():
                        self.bg_x2 = self.bg_x1 + self.background_image.get_width()
                elif self.scroll_direction == 'right':
                    # 背景向右滚动，横坐标递增
                    self.bg_x1 += self.scroll_speed
                    self.bg_x2 += self.scroll_speed
                    if self.bg_x1 >= self.background_image.get_width():
                        self.bg_x1 = self.bg_x2 - self.background_image.get_width()
                    if self.bg_x2 >= self.background_image.get_width():
                        self.bg_x2 = self.bg_x1 - self.background_image.get_width()

            # **绘制背景**（在其他游戏元素绘制之前）
            if self.scroll_enabled:
                # 绘制两张背景图像到屏幕，实现无缝衔接的滚动效果
                self.surface.blit(self.background_image, (self.bg_x1, self.bg_y1))
                self.surface.blit(self.background_image, (self.bg_x2, self.bg_y2))
            else:
                # 静态背景的绘制（保留原有 set_background 功能）
                if self.background_image:
                    self.surface.blit(self.background_image, (0, 0))

            for group_name, group in group_manager.groups.items():
                for sprite in group:
                    sprite.update()  # 更新精灵
                    sprite.draw(self.surface)  # 绘制精灵
            for game_text in self.game_texts:
                game_text.draw(self.surface)  # 绘制游戏文本
            pygame.display.update()  # 更新显示
            for key_status in self.key_status.values():
                key_status.reset_released()  # 重置键的释放状态
            self.clock.tick(FPS)  # 控制游戏帧率


# 创建组管理器的实例
group_manager = GroupManager()  # 实例化组管理器，用于管理游戏中的精灵组
