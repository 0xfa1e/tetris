import pygame
import random
from pygame import Rect, Surface, SRCALPHA
import math
import os
import pygame.mixer

# 游戏设置
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600
BLOCK_SIZE = 30
FIELD_WIDTH = 10
FIELD_HEIGHT = 20
GAME_SPEED = 50
FIELD_X = (WINDOW_WIDTH - FIELD_WIDTH * BLOCK_SIZE) // 2
FIELD_Y = WINDOW_HEIGHT - (FIELD_HEIGHT * BLOCK_SIZE)   # 调整底部间距为10
GAME_WIDTH = FIELD_WIDTH * BLOCK_SIZE + 10
GAME_HEIGHT = FIELD_HEIGHT * BLOCK_SIZE + 10

# 音效常量
VOLUME_BACKGROUND = 0.3
VOLUME_EFFECTS = 0.5

# 颜色定义 - 明亮温暖的扁平化配色
COLORS = [
    (245, 245, 245),    # 背景色 - 浅灰
    (255, 88, 88),      # 暖红色
    (255, 165, 0),      # 橙色
    (255, 223, 0),      # 金黄色
    (255, 182, 193),    # 粉色
    (255, 140, 0),      # 深橙色
    (255, 127, 80),     # 珊瑚色
]

# 方块形状定义
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
    [[1, 2, 5, 6]],  # O
    [[6, 7, 9, 10], [1, 5, 6, 10]],  # S
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # T
    [[4, 5, 9, 10], [2, 6, 5, 9]]  # Z
]

# 初始化Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# 设置中文字体 (Mac系统)
try:
    FONT_NAME = "/System/Library/Fonts/PingFang.ttc"  # Mac系统中文字体
except:
    FONT_NAME = pygame.font.get_default_font()

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('俄罗斯方块')
clock = pygame.time.Clock()

class Button:
    def __init__(self, x, y, width, height, text, font_size=32, 
                 text_color=(255, 255, 255),  # 白色文字
                 button_color=(255, 88, 88),  # 暖红色按钮
                 hover_color=(255, 120, 120)):  # 浅一点的红色悬停
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.button_color = button_color
        self.hover_color = hover_color
        self.font = pygame.font.Font(FONT_NAME, font_size)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.button_color
        
        # 绘制圆角按钮
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        
        # 渲染文字
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_clicked(event.pos):
                return True
        return False

class SoundManager:
    """管理游戏音效"""
    def __init__(self):
        # 背景音乐
        self.game_over_sound_played = False
        try:
            # 尝试使用绝对路径
            background_music_path = os.path.join(os.path.dirname(__file__), 'assets', 'sounds', 'background_music.mp3')
            pygame.mixer.music.load(background_music_path)
            pygame.mixer.music.set_volume(VOLUME_BACKGROUND)
            pygame.mixer.music.play(-1)  # 循环播放
        except pygame.error as e:
            print(f"背景音乐加载失败: {e}")
        
        # 音效
        try:
            # 使用绝对路径加载音效
            base_path = os.path.join(os.path.dirname(__file__), 'assets', 'sounds')
            self.move_sound = pygame.mixer.Sound(os.path.join(base_path, 'move_sound.wav'))
            self.move_sound.set_volume(VOLUME_EFFECTS)
            
            self.clear_sound = pygame.mixer.Sound(os.path.join(base_path, 'clear_sound.wav'))
            self.clear_sound.set_volume(VOLUME_EFFECTS)
            
            self.game_over_sound = pygame.mixer.Sound(os.path.join(base_path, 'game_over_sound.wav'))
            self.game_over_sound.set_volume(VOLUME_EFFECTS)
        except pygame.error as e:
            print(f"音效加载失败: {e}")
            self.move_sound = None
            self.clear_sound = None
            self.game_over_sound = None
    
    def play_move(self):
        """播放移动音效"""
        if self.move_sound:
            self.move_sound.play()
    
    def play_clear(self):
        """播放消除音效"""
        if self.clear_sound:
            self.clear_sound.play()
    
    def play_game_over(self):
        """播放游戏结束音效，确保只播放一次"""
        if not self.game_over_sound_played:
            if self.game_over_sound:
                self.game_over_sound.play()
                self.game_over_sound_played = True
            pygame.mixer.music.stop()

class Figure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(SHAPES) - 1)
        self.color = random.randint(1, len(COLORS) - 1)
        self.rotation = 0

    def image(self):
        return SHAPES[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.type])

class Tetris:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """完全重置游戏状态"""
        # 重置游戏区域
        self.field = [[0 for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
        
        # 重置游戏状态
        self.state = "start"
        self.score = 0
        
        # 清除当前方块
        self.figure = None
        self.next_figure = None

    def new_figure(self):
        if not self.next_figure:
            self.next_figure = Figure(3, 0)
        self.figure = self.next_figure
        self.next_figure = Figure(3, 0)

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if (i + self.figure.y > FIELD_HEIGHT - 1 or
                        j + self.figure.x > FIELD_WIDTH - 1 or
                        j + self.figure.x < 0 or
                        self.field[i + self.figure.y][j + self.figure.x] > 0):
                        intersection = True
        return intersection

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def break_lines(self):
        """消除已完成的行并计算得分"""
        lines = 0
        cleared_lines = []  # 记录被清除的行
        for i in range(FIELD_HEIGHT - 1, -1, -1):
            zeros = 0
            for j in range(FIELD_WIDTH):
                if self.field[i][j] == 0:
                    zeros += 1
        
            # 如果这一行已满
            if zeros == 0:
                # 记录被清除的行
                cleared_lines.append(i)
                # 删除这一行
                del self.field[i]
                # 在顶部添加一个新的空行
                self.field.insert(0, [0 for _ in range(FIELD_WIDTH)])
                lines += 1
    
        # 根据消除的行数计算得分
        if lines > 0:
            # 计分规则：消除1行1分，2行3分，3行5分，4行8分
            if lines == 1:
                self.score += 100
            elif lines == 2:
                self.score += 300
            elif lines == 3:
                self.score += 500
            elif lines == 4:
                self.score += 800
        
        return cleared_lines

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def go_side(self, dx):
        """移动方块"""
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

def create_gradient_background():
    try:
        # Use absolute path to background image
        background_path = os.path.join(os.path.dirname(__file__), 'assets', 'background.jpeg')
        background = pygame.image.load(background_path)
        # Resize background to match window dimensions
        background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except pygame.error as e:
        print(f"Error loading background image: {e}")
        # Fallback to original gradient background if image loading fails
        background = Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        background.fill((252, 252, 252))  # Pure white background
    return background

def draw_game_area(screen):
    # 使用灰色边框
    pygame.draw.rect(screen, (150, 150, 150), (FIELD_X - 1, FIELD_Y - 1, FIELD_WIDTH * BLOCK_SIZE + 2, FIELD_HEIGHT * BLOCK_SIZE + 2), 1)

def draw_block(screen, x, y, color):
    # 减小方块间隙
    block_rect = pygame.Rect(x + 1, y + 1, BLOCK_SIZE - 1, BLOCK_SIZE - 1)
    pygame.draw.rect(screen, color, block_rect)
    # 添加轻微的边框
    pygame.draw.rect(screen, (100, 100, 100), block_rect, 1)

def draw_explosion_effect(screen, cleared_lines):
    for line in cleared_lines:
        for i in range(FIELD_WIDTH):
            pygame.draw.rect(screen, (255, 0, 0), (FIELD_X + i * BLOCK_SIZE, FIELD_Y + line * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_text(screen, text, size, x, y, color=(0, 0, 0)):
    font = pygame.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main():
    # 创建背景
    background = create_gradient_background()
    
    # 初始化游戏状态
    game = Tetris()
    sound_manager = SoundManager()
    
    # 初始化第一个方块
    game.new_figure()
    
    # 游戏主循环相关变量
    counter = 0
    pressing_down = False
    fast_down = False  # 快速下落标志
    
    # 左右移动相关变量
    moving_left = False
    moving_right = False
    move_delay_counter = 0
    initial_move_delay = 15  # 初始移动延迟
    repeat_move_delay = 4    # 重复移动间隔
    
    # 游戏状态相关按钮
    restart_button = Button(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 50, 300, 50, "重新开始", 
                            button_color=(76, 175, 80),    # 绿色
                            hover_color=(129, 199, 132),   # 浅绿色
                            text_color=(255, 255, 255))    # 白色文字
    quit_button = Button(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 120, 300, 50, "退出游戏", 
                         button_color=(244, 67, 54),       # 红色
                         hover_color=(229, 115, 115),      # 浅红色
                         text_color=(255, 255, 255))       # 白色文字
    
    # 特效相关
    cleared_lines = []
    
    # 主游戏循环
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 游戏中状态的按键处理
            if game.state == "start":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        game.rotate()
                        sound_manager.play_move()
                    if event.key == pygame.K_DOWN:
                        pressing_down = True
                        fast_down = True  # 启用快速下落
                    if event.key == pygame.K_LEFT:
                        moving_left = True
                        move_delay_counter = 0
                        game.go_side(-1)
                        sound_manager.play_move()
                    if event.key == pygame.K_RIGHT:
                        moving_right = True
                        move_delay_counter = 0
                        game.go_side(1)
                        sound_manager.play_move()
                    if event.key == pygame.K_SPACE:
                        game.go_space()
                        sound_manager.play_move()
            
            # 游戏结束状态的按钮处理
            if game.state == "gameover":
                if restart_button.handle_event(event):
                    game.reset_game()
                    game.new_figure()
                    sound_manager.game_over_sound_played = False  # 重置游戏结束音效标志
                    sound_manager.play_move()
                if quit_button.handle_event(event):
                    running = False
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False
                    fast_down = False
                if event.key == pygame.K_LEFT:
                    moving_left = False
                    move_delay_counter = 0
                if event.key == pygame.K_RIGHT:
                    moving_right = False
                    move_delay_counter = 0
        
        # 处理持续移动
        if game.state == "start" and (moving_left or moving_right):
            move_delay_counter += 1
            if move_delay_counter >= initial_move_delay:
                if move_delay_counter >= initial_move_delay + repeat_move_delay:
                    if moving_left:
                        game.go_side(-1)
                        sound_manager.play_move()
                    if moving_right:
                        game.go_side(1)
                        sound_manager.play_move()
                    move_delay_counter = initial_move_delay
        
        # 绘制背景
        screen.blit(background, (0, 0))
        
        # 游戏进行中
        if game.state == "start":
            # 控制下落速度
            counter += 1
            if counter > (GAME_SPEED // (10 if fast_down else 1)):  # 大幅加快下落速度
                counter = 0
                game.go_down()
            
            # 绘制游戏区域
            draw_game_area(screen)
            
            # 绘制已经固定的方块
            for y, row in enumerate(game.field):
                for x, cell in enumerate(row):
                    if cell > 0:
                        draw_block(screen, FIELD_X + x * BLOCK_SIZE, FIELD_Y + y * BLOCK_SIZE, COLORS[cell])
            
            # 绘制当前下落方块
            if game.figure:
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j
                        if p in game.figure.image():
                            draw_block(screen, 
                                       FIELD_X + (game.figure.x + j) * BLOCK_SIZE, 
                                       FIELD_Y + (game.figure.y + i) * BLOCK_SIZE, 
                                       COLORS[game.figure.color])
            
            # 绘制分数
            draw_text(screen, f"分数: {game.score}", 24, 10, 10)
        
        # 游戏结束状态
        elif game.state == "gameover":
            # 播放游戏结束音效
            sound_manager.play_game_over()
            
            # 创建半透明遮罩
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # 半透明黑色
            screen.blit(overlay, (0, 0))
            
            # 绘制游戏结束文字
            draw_text(screen, "游戏结束", 64, WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 200, (244, 67, 54))  # 红色
            draw_text(screen, f"最终得分: {game.score}", 32, WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 100, (255, 255, 255))  # 白色
            
            # 绘制按钮
            restart_button.draw(screen)
            quit_button.draw(screen)
        
        # 消除特效
        if game.break_lines():
            sound_manager.play_clear()
            cleared_lines = game.break_lines()
            draw_explosion_effect(screen, cleared_lines)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
