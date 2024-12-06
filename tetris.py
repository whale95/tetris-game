import pygame
import random

# 初始化pygame
pygame.init()

# 在pygame.init()后添加以下代码来设置中文字体
try:
    # Windows系统默认中文字体
    FONT_PATH = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
except:
    try:
        # Linux/Mac系统可能的中文字体路径
        FONT_PATH = "/System/Library/Fonts/PingFang.ttc"  # 苹方字体
    except:
        FONT_PATH = None

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
RETRO_GREEN = (155, 188, 115)
RETRO_DARK = (50, 50, 50)
RETRO_LIGHT = (200, 210, 185)

# 游戏设置
BLOCK_SIZE = 20  # 每个方块的大小
GRID_WIDTH = 10  # 游戏区域宽度（以方块数计）
GRID_HEIGHT = 20  # 游戏区域高度（以方块数计）
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)  # 屏幕宽度
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT  # 屏幕高度

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("俄罗斯方块")

# 定义方块形状
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# 定义方块颜色
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Menu:
    def __init__(self):
        if FONT_PATH:
            self.font_big = pygame.font.Font(FONT_PATH, 36)
            self.font_small = pygame.font.Font(FONT_PATH, 24)
        else:
            self.font_big = pygame.font.Font(None, 48)
            self.font_small = pygame.font.Font(None, 28)
        self.difficulty_options = ["简单", "普通", "困难"]  # 添加难度选项
        self.difficulty = 1  # 0: 简单, 1: 普通, 2: 困难
        self.music_on = False  # 默认关闭音乐
        try:
            pygame.mixer.init()
            pygame.mixer.music.load('assets/music/background.mp3')
            pygame.mixer.music.play(-1)  # 加载音乐但立即暂停
            pygame.mixer.music.pause()  # 默认暂停音乐
        except:
            print("无法初始化音乐系统")
        self.selected = 0
        
    def draw(self, screen):
        screen.fill(RETRO_GREEN)
        
        # 调整标题位置和大小
        title = self.font_big.render("俄罗斯方块", True, BLACK)
        subtitle = self.font_small.render("GAME", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 40))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 90))
        
        button_width = 140
        button_height = 32
        button_spacing = 40
        
        options = [
            "开始游戏",
            f"难度: {self.difficulty_options[self.difficulty]}",
            f"音乐: {'开' if self.music_on else '关'}"
        ]
        
        start_y = 140
        
        for i, option in enumerate(options):
            x = SCREEN_WIDTH//2 - button_width//2
            y = start_y + i * button_spacing
            
            rect = pygame.Rect(x, y, button_width, button_height)
            pygame.draw.rect(screen, RETRO_LIGHT, rect, border_radius=5)
            pygame.draw.rect(screen, BLACK, rect, 2, border_radius=5)
            
            color = WHITE if i == self.selected else BLACK
            text = self.font_small.render(option, True, color)
            text_x = x + (button_width - text.get_width())//2
            text_y = y + (button_height - text.get_height())//2
            screen.blit(text, (text_x, text_y))
        
        pygame.display.flip()
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % 3
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % 3
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:
                    return True  # 开始游戏
            elif event.key == pygame.K_LEFT:
                if self.selected == 1:  # 难度设置
                    self.difficulty = (self.difficulty - 1) % 3  # 在0、1、2之间循环
            elif event.key == pygame.K_RIGHT:
                if self.selected == 1:  # 难度设置
                    self.difficulty = (self.difficulty + 1) % 3  # 在0、1、2之间循环
                elif self.selected == 2:  # 音乐设置
                    self.music_on = not self.music_on
                    try:
                        if self.music_on:
                            pygame.mixer.music.rewind()  # 重置音乐到开始位置
                            pygame.mixer.music.play(-1)  # 重新开始播放
                        else:
                            pygame.mixer.music.pause()
                    except:
                        print("无法控制音乐")
        return False

class Tetris:
    def __init__(self, difficulty=1):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.leaderboard = Leaderboard()  # 先初始化排行榜
        # 从排行榜中获取最高分
        self.high_score = max(self.leaderboard.scores[0], self.load_high_score())  # 取排行榜第一名和历史最高分的较大值
        self.level = 1
        self.difficulty = difficulty
        # 根据难度设置初始速度
        self.fall_speed = self.get_initial_fall_speed()
        self.fall_time = 0
        self.clock = pygame.time.Clock()
        self.preview_block_size = 12
        self.pause_menu = PauseMenu()
        self.showing_leaderboard = False
        self.game_over_screen = GameOverScreen(self.leaderboard)
        try:
            # 初始化音效
            self.score_sound = pygame.mixer.Sound('assets/sound/score.wav')
            self.score_sound.set_volume(0.3)  # 设置音效音量为30%
        except:
            print("无法加载音效文件")

    def load_high_score(self):
        try:
            with open('high_score.txt', 'r') as f:
                high_score = int(f.read())
                # 确保最高分也在排行榜中
                if high_score > 0:
                    self.leaderboard.add_score(high_score)
                return high_score
        except:
            return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open('high_score.txt', 'w') as f:
                f.write(str(self.high_score))
            # 当更新最高分时，也更新排行榜
            self.leaderboard.add_score(self.score)

    def new_piece(self):
        # 随机选择一个新方块
        shape = random.choice(SHAPES)
        return {
            'shape': shape,
            'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
            'y': 0
        }

    def draw_piece(self, piece, x, y):
        for i in range(len(piece['shape'])):
            for j in range(len(piece['shape'][0])):
                if piece['shape'][i][j]:
                    pygame.draw.rect(screen, RETRO_DARK,
                                   [x + j * BLOCK_SIZE + 1,
                                    y + i * BLOCK_SIZE + 1,
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2])

    def draw_preview_piece(self, piece, x, y):
        # 专门用于绘制预览方块的方法，使用较小的方块尺寸
        for i in range(len(piece['shape'])):
            for j in range(len(piece['shape'][0])):
                if piece['shape'][i][j]:
                    pygame.draw.rect(screen, RETRO_DARK,
                                   [x + j * self.preview_block_size + 1,
                                    y + i * self.preview_block_size + 1,
                                    self.preview_block_size - 2,
                                    self.preview_block_size - 2])

    def draw(self):
        # 设置背景色
        screen.fill(RETRO_GREEN)
        
        # 绘制游戏区域背景
        game_area = pygame.Rect(0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE)
        pygame.draw.rect(screen, RETRO_LIGHT, game_area)
        
        # 绘制网格线
        for i in range(GRID_WIDTH + 1):
            pygame.draw.line(screen, RETRO_GREEN, 
                            (i * BLOCK_SIZE, 0), 
                            (i * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE))
        for i in range(GRID_HEIGHT + 1):
            pygame.draw.line(screen, RETRO_GREEN,
                            (0, i * BLOCK_SIZE),
                            (GRID_WIDTH * BLOCK_SIZE, i * BLOCK_SIZE))
        
        # 绘制已放置的方块和当前方块（移除暂停条件）
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.grid[i][j]:
                    pygame.draw.rect(screen, RETRO_DARK,
                                   [j * BLOCK_SIZE + 1, i * BLOCK_SIZE + 1, 
                                    BLOCK_SIZE - 2, BLOCK_SIZE - 2])
        
        if self.current_piece:
            self.draw_piece(self.current_piece, 
                          self.current_piece['x'] * BLOCK_SIZE,
                          self.current_piece['y'] * BLOCK_SIZE)

        # 绘制右侧信息区域
        info_x = GRID_WIDTH * BLOCK_SIZE + 10
        
        # 绘制暂停按钮
        pause_rect = pygame.Rect(info_x, 10, 50, 50)
        pygame.draw.rect(screen, RETRO_LIGHT, pause_rect, border_radius=8)
        pygame.draw.rect(screen, RETRO_DARK, pause_rect, 2, border_radius=8)
        
        # 绘制暂停图标
        if not self.paused:
            pygame.draw.rect(screen, RETRO_DARK, (info_x + 17, 22, 5, 25))
            pygame.draw.rect(screen, RETRO_DARK, (info_x + 28, 22, 5, 25))
        else:
            points = [(info_x + 17, 22), (info_x + 17, 47), (info_x + 37, 35)]
            pygame.draw.polygon(screen, RETRO_DARK, points)
        
        # 绘制"下一个"文字
        if FONT_PATH:
            font = pygame.font.Font(FONT_PATH, 20)
        else:
            font = pygame.font.Font(None, 24)
        next_text = font.render("下一个", True, RETRO_DARK)
        screen.blit(next_text, (info_x + 5, 80))
        
        # 修改预览框和预览方块的绘制部分
        preview_size = 60
        preview_rect = pygame.Rect(info_x, 110, preview_size, preview_size)
        pygame.draw.rect(screen, RETRO_LIGHT, preview_rect, border_radius=5)
        pygame.draw.rect(screen, RETRO_DARK, preview_rect, 2, border_radius=5)
        
        # 调整预览方块的位置和大小
        if self.next_piece and not self.paused:
            shape_width = len(self.next_piece['shape'][0]) * self.preview_block_size
            shape_height = len(self.next_piece['shape']) * self.preview_block_size
            next_piece_x = info_x + (preview_size - shape_width) // 2
            next_piece_y = 110 + (preview_size - shape_height) // 2
            self.draw_preview_piece(self.next_piece, next_piece_x, next_piece_y)
        
        # 绘制分数区域（调整位置）
        score_y = 190
        score_text = font.render("得分", True, RETRO_DARK)
        score_value = font.render(str(self.score), True, RETRO_DARK)
        high_score_text = font.render("最高分", True, RETRO_DARK)
        high_score_value = font.render(str(self.high_score), True, RETRO_DARK)
        
        screen.blit(score_text, (info_x + 5, score_y))
        screen.blit(score_value, (info_x + 5, score_y + 30))
        screen.blit(high_score_text, (info_x + 5, score_y + 70))
        screen.blit(high_score_value, (info_x + 5, score_y + 100))
        
        # 添加难度显示
        difficulty_names = ["简单", "普通", "困难"]
        difficulty_text = font.render("难度", True, RETRO_DARK)
        difficulty_value = font.render(difficulty_names[self.difficulty], True, RETRO_DARK)
        screen.blit(difficulty_text, (info_x + 5, score_y + 140))
        screen.blit(difficulty_value, (info_x + 5, score_y + 170))
        
        # 如果正在显示排行榜，绘制排行榜
        if self.showing_leaderboard or (self.paused and self.pause_menu.show_leaderboard):
            self.leaderboard.draw(screen)
        elif self.paused:
            self.pause_menu.draw(screen)

        if self.game_over:
            self.game_over_screen.draw(screen, self.score)

        pygame.display.flip()

    def drop_piece(self):
        if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
        else:
            # 固定方块到网格
            for i in range(len(self.current_piece['shape'])):
                for j in range(len(self.current_piece['shape'][0])):
                    if self.current_piece['shape'][i][j]:
                        if self.current_piece['y'] + i < 0:
                            self.game_over = True
                            if self.score > 0:  # 只保存大于0的分数
                                self.save_high_score()  # 先保存最高分
                                self.leaderboard.add_score(self.score)  # 再更新排行榜
                            return
                        self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = 1
            
            # 清除完成的行并更新分数
            self.clear_lines()  # 移除分数更新，由 clear_lines 处理
            
            # 更新当前方块和下一个方块
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            
            # 检查游戏是否结束
            if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
                self.game_over = True
                if self.score > 0:  # 只保存大于0的分数
                    self.save_high_score()  # 先保存最高分
                    self.leaderboard.add_score(self.score)  # 再更新排行榜

    def valid_move(self, piece, x, y):
        # 检查移动是否有效
        for i in range(len(piece['shape'])):
            for j in range(len(piece['shape'][0])):
                if piece['shape'][i][j]:
                    if (x + j < 0 or x + j >= GRID_WIDTH or
                        y + i >= GRID_HEIGHT or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True

    def rotate_piece(self, piece):
        # 旋转方块
        new_shape = list(zip(*piece['shape'][::-1]))
        if self.valid_move({'shape': new_shape, 'x': piece['x'], 'y': piece['y']}, piece['x'], piece['y']):
            piece['shape'] = new_shape

    def clear_lines(self):
        # 清除已完成的行
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                lines_cleared += 1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        # 更新分数，加入难度系数
        if lines_cleared > 0:
            score_multiplier = self.get_score_multiplier()
            self.score += int(lines_cleared * 100 * score_multiplier)
            # 播放得分音效
            try:
                self.score_sound.play()
            except:
                pass
            # 检查是否超过最高分
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
        
        return lines_cleared

    def handle_pause_menu(self, action, menu):
        if action == 0:  # 继续
            self.paused = False
        elif action == 1:  # 重玩
            self.__init__(difficulty=self.difficulty)
        elif action == 2:  # 排行榜
            self.pause_menu.show_leaderboard = True
        elif action == "toggle_music":  # 音乐控制
            menu.music_on = not menu.music_on
            try:
                if menu.music_on:
                    pygame.mixer.music.rewind()  # 重置音乐到开始位置
                    pygame.mixer.music.play(-1)  # 重新开始播放
                else:
                    pygame.mixer.music.pause()
            except:
                print("无法控制音乐")
            return None  # 返回 None 表示不关闭暂停菜单
        elif action == 4:  # 返回首页
            return True
        return False

    def get_initial_fall_speed(self):
        # 根据难度回不同的初始速度
        speeds = {
            0: 0.8,  # 简单
            1: 0.5,  # 普通
            2: 0.3   # 困难
        }
        return speeds[self.difficulty]
    
    def get_score_multiplier(self):
        # 根据难度返回不同的得分倍数
        multipliers = {
            0: 1,    # 简单
            1: 1.5,  # 普通
            2: 2     # 困难
        }
        return multipliers[self.difficulty]

class PauseMenu:
    def __init__(self):
        if FONT_PATH:
            self.font = pygame.font.Font(FONT_PATH, 20)
        else:
            self.font = pygame.font.Font(None, 24)
        self.selected = 0
        self.options = [
            ("继续", "►"),
            ("重玩", "⟲"),
            ("排行榜", "▌"),
            ("音乐", "♪"),
            ("首页", "⌂")
        ]
        self.show_leaderboard = False
    
    def draw(self, screen):
        # 创建半透明的背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(RETRO_GREEN)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        if self.show_leaderboard:
            # 显示排行榜界面
            self.draw_leaderboard(screen)
            return
        
        # 调整菜单尺寸
        menu_width = 160
        menu_height = 240  # 增加高度到240
        menu_x = SCREEN_WIDTH // 2 - menu_width // 2
        menu_y = SCREEN_HEIGHT // 2 - menu_height // 2
        
        # 绘制菜单背景
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(screen, RETRO_LIGHT, menu_rect, border_radius=8)
        pygame.draw.rect(screen, RETRO_DARK, menu_rect, 2, border_radius=8)
        
        # 调整按钮参数
        button_height = 35  # 增加按钮高度
        button_spacing = 38  # 调整按钮间距
        start_y = menu_y + 30  # 从更高的位置开始
        
        for i, (text, icon) in enumerate(self.options):
            button_rect = pygame.Rect(
                menu_x + 15,
                start_y + i * button_spacing,
                menu_width - 30,
                button_height
            )
            
            # 如果是选中的选项，绘制深色背景
            if i == self.selected:
                pygame.draw.rect(screen, RETRO_DARK, button_rect, border_radius=5)
            
            # 绘制按钮边框
            pygame.draw.rect(screen, RETRO_DARK, button_rect, 2, border_radius=5)
            
            # 绘制文字和图标
            color = WHITE if i == self.selected else RETRO_DARK
            text_surface = self.font.render(text, True, color)
            icon_surface = self.font.render(icon, True, color)
            
            # 调整文字和图标位置
            text_x = button_rect.left + 30
            text_y = button_rect.centery - text_surface.get_height() // 2
            
            icon_x = button_rect.left + 8
            icon_y = button_rect.centery - icon_surface.get_height() // 2
            
            screen.blit(icon_surface, (icon_x, icon_y))
            screen.blit(text_surface, (text_x, text_y))
    
    def draw_leaderboard(self, screen):
        # 使用现有的 Leaderboard 类的绘制方法
        self.leaderboard.draw(screen)
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected == 3:  # 音乐选项
                    return "toggle_music"  # 返回特殊值表示切换音乐
                return self.selected
        return None

class Leaderboard:
    def __init__(self):
        if FONT_PATH:
            self.font = pygame.font.Font(FONT_PATH, 20)
        else:
            self.font = pygame.font.Font(None, 24)
        self.scores = self.load_scores()
    
    def load_scores(self):
        try:
            with open('scores.txt', 'r') as f:
                scores = [int(line.strip()) for line in f.readlines() if line.strip()]
                # 确保至少有5个分数
                while len(scores) < 5:
                    scores.append(0)
                return sorted(scores, reverse=True)[:5]  # 只保留前5个最高分
        except FileNotFoundError:
            # 如果文件不存在，创建文件并返回初始分数列表
            with open('scores.txt', 'w') as f:
                f.write('0\n' * 5)
            return [0] * 5
    
    def save_scores(self):
        try:
            with open('scores.txt', 'w') as f:
                # 确保只保存非零分数
                scores_to_save = [score for score in self.scores if score > 0]
                # 如果没有非零分数，至少保存一个0
                if not scores_to_save:
                    scores_to_save = [0]
                for score in scores_to_save:
                    f.write(f"{score}\n")
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, score):
        if score > 0:  # 只添加大于0的分数
            # 检查是否已经存在相同的数
            if score not in self.scores:
                self.scores.append(score)
                self.scores = sorted(self.scores, reverse=True)[:5]  # 保持前5个最高分
                self.save_scores()  # 立即保存分数
    
    def draw(self, screen):
        # 创建半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(RETRO_GREEN)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        # 调整排行榜面板尺寸
        panel_width = 140  # 保持宽度
        panel_height = 260  # 增加高度，给间距留更多空间
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        # 绘制面板背景
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, RETRO_LIGHT, panel_rect, border_radius=8)
        pygame.draw.rect(screen, RETRO_DARK, panel_rect, 2, border_radius=8)
        
        # 绘制标题
        title = self.font.render("排行榜", True, RETRO_DARK)
        title_x = panel_x + (panel_width - title.get_width()) // 2
        screen.blit(title, (title_x, panel_y + 25))
        
        # 绘制分数列表
        button_height = 25  # 保持按钮高度
        button_spacing = 34  # 增加间距
        start_y = panel_y + 55  # 第一个按钮的起始位置
        
        for i, score in enumerate(self.scores[:5]):
            # 绘制排名背景
            button_rect = pygame.Rect(
                panel_x + 10,
                start_y + i * button_spacing,
                panel_width - 20,
                button_height
            )
            pygame.draw.rect(screen, RETRO_LIGHT, button_rect, border_radius=5)
            pygame.draw.rect(screen, RETRO_DARK, button_rect, 2, border_radius=5)
            
            # 绘制排名和分数
            rank_text = f"#{i + 1}"
            rank = self.font.render(rank_text, True, RETRO_DARK)
            score_text = self.font.render(str(score), True, RETRO_DARK)
            
            # 调整排名和分数的位置
            rank_x = button_rect.left + 10
            score_x = button_rect.right - score_text.get_width() - 10
            text_y = button_rect.centery - rank.get_height() // 2
            
            screen.blit(rank, (rank_x, text_y))
            screen.blit(score_text, (score_x, text_y))
        
        # 计算底部文字的位置
        # 确保与最后一个按钮的距离和与底部的距离相等
        last_button_bottom = start_y + 4 * button_spacing + button_height
        remaining_space = panel_height - (last_button_bottom - panel_y)
        bottom_margin = remaining_space // 2
        
        # 绘制"按任意键返回"文字
        hint_font = pygame.font.Font(FONT_PATH, 14) if FONT_PATH else pygame.font.Font(None, 16)
        hint = hint_font.render("按任意键返回", True, RETRO_DARK)
        hint_x = panel_x + (panel_width - hint.get_width()) // 2
        hint_y = last_button_bottom + bottom_margin - hint.get_height() // 2
        screen.blit(hint, (hint_x, hint_y))

class GameOverScreen:
    def __init__(self, leaderboard):
        if FONT_PATH:
            self.font_title = pygame.font.Font(FONT_PATH, 24)
            self.font = pygame.font.Font(FONT_PATH, 20)  # 用于按钮文字
        else:
            self.font_title = pygame.font.Font(None, 32)
            self.font = pygame.font.Font(None, 24)
        self.leaderboard = leaderboard
        self.selected = 0
        self.options = [
            ("重玩", "⟲"),
            ("排行榜", "▌"),
            ("首页", "⌂")
        ]
        self.show_leaderboard = False
    
    def draw(self, screen, current_score):
        # 创建半透明背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(RETRO_GREEN)
        overlay.set_alpha(180)
        screen.blit(overlay, (0, 0))
        
        if self.show_leaderboard:
            # 显示排行榜界面
            self.leaderboard.draw(screen)
            return
        
        # 设置对话框尺寸
        dialog_width = 200
        dialog_height = 240  # 增加高度以容纳新按钮
        dialog_x = SCREEN_WIDTH // 2 - dialog_width // 2
        dialog_y = SCREEN_HEIGHT // 2 - dialog_height // 2
        
        # 绘制对话框背景
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        pygame.draw.rect(screen, RETRO_LIGHT, dialog_rect, border_radius=8)
        pygame.draw.rect(screen, RETRO_DARK, dialog_rect, 2, border_radius=8)
        
        # 绘制标题
        title = self.font_title.render("游戏结束", True, RETRO_DARK)
        title_x = dialog_x + (dialog_width - title.get_width()) // 2
        screen.blit(title, (title_x, dialog_y + 20))
        
        # 绘制分数
        score_text = self.font.render(f"最终得分: {current_score}", True, RETRO_DARK)
        score_x = dialog_x + (dialog_width - score_text.get_width()) // 2
        screen.blit(score_text, (score_x, dialog_y + 60))
        
        # 绘制按钮
        button_height = 30
        button_spacing = 40
        start_y = dialog_y + 100
        
        for i, (text, icon) in enumerate(self.options):
            button_rect = pygame.Rect(
                dialog_x + 20,
                start_y + i * button_spacing,
                dialog_width - 40,
                button_height
            )
            
            # 如果是选中的选项，绘制深色背景
            if i == self.selected:
                pygame.draw.rect(screen, RETRO_DARK, button_rect, border_radius=5)
            
            # 绘制按钮边框
            pygame.draw.rect(screen, RETRO_DARK, button_rect, 2, border_radius=5)
            
            # 绘制文字和图标
            color = WHITE if i == self.selected else RETRO_DARK
            text_surface = self.font.render(text, True, color)
            icon_surface = self.font.render(icon, True, color)
            
            # 调整文字和图标位置
            text_x = button_rect.left + 30
            text_y = button_rect.centery - text_surface.get_height() // 2
            
            icon_x = button_rect.left + 8
            icon_y = button_rect.centery - icon_surface.get_height() // 2
            
            screen.blit(icon_surface, (icon_x, icon_y))
            screen.blit(text_surface, (text_x, text_y))
    
    def handle_input(self, event):
        if self.show_leaderboard:
            if event.type == pygame.KEYDOWN:
                self.show_leaderboard = False
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.selected == 0:  # 重玩
                    return "restart"
                elif self.selected == 1:  # 排行榜
                    self.show_leaderboard = True
                elif self.selected == 2:  # 首页
                    return "menu"
            elif event.key == pygame.K_ESCAPE:
                return "menu"
        return None

def main():
    menu = Menu()
    game = None
    in_menu = True
    
    while True:
        if in_menu:
            menu.draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if menu.handle_input(event):
                    in_menu = False
                    game = Tetris(difficulty=menu.difficulty)  # 传入难度参数
        else:
            # 只在非暂停且游戏未结束时更新方块位置
            if not game.game_over and not game.paused:
                current_time = pygame.time.get_ticks()
                if current_time - game.fall_time > game.fall_speed * 1000:
                    game.drop_piece()
                    game.fall_time = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if game.game_over:
                        action = game.game_over_screen.handle_input(event)
                        if action == "restart":
                            game = Tetris(difficulty=menu.difficulty)
                            game.fall_speed = 0.5 / menu.difficulty
                        elif action == "menu":  # 只在明确返回菜单时返回
                            in_menu = True
                            game = None
                    elif game.showing_leaderboard:
                        game.showing_leaderboard = False
                        game.paused = False
                    elif event.key == pygame.K_ESCAPE:
                        in_menu = True
                        game.leaderboard.add_score(game.score)  # 保存当前分数
                    elif event.key == pygame.K_p:
                        game.paused = not game.paused
                        if game.paused:
                            game.fall_time = pygame.time.get_ticks()
                    elif game.paused:
                        if game.pause_menu.show_leaderboard:
                            game.pause_menu.show_leaderboard = False
                        else:
                            action = game.pause_menu.handle_input(event)
                            if action is not None:
                                if game.handle_pause_menu(action, menu):  # 如果返回 True，表示需要返回首页
                                    in_menu = True
                                    game = None
                    # 只在非暂停且游戏未结束时响应游戏控制
                    elif not game.game_over and not game.paused:
                        if event.key == pygame.K_LEFT:
                            if game.valid_move(game.current_piece, game.current_piece['x'] - 1, game.current_piece['y']):
                                game.current_piece['x'] -= 1
                        elif event.key == pygame.K_RIGHT:
                            if game.valid_move(game.current_piece, game.current_piece['x'] + 1, game.current_piece['y']):
                                game.current_piece['x'] += 1
                        elif event.key == pygame.K_DOWN:
                            game.drop_piece()
                        elif event.key == pygame.K_UP:
                            game.rotate_piece(game.current_piece)
                        elif event.key == pygame.K_SPACE:
                            while game.valid_move(game.current_piece, game.current_piece['x'], game.current_piece['y'] + 1):
                                game.current_piece['y'] += 1
                            game.drop_piece()

            # 无论是否暂停都需要绘制画面
            if not in_menu:
                game.draw()
                game.clock.tick(60)

if __name__ == '__main__':
    main()
