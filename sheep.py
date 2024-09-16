import pygame
import random
import sys

# 定义游戏相关属性
TITLE = '羊了个羊小游戏'
WIDTH = 600
HEIGHT = 720
FPS = 60

# 自定义游戏常量
T_WIDTH = 60
T_HEIGHT = 66

# 下方牌堆的位置
DOCK = pygame.Rect((90, 564), (T_WIDTH * 7, T_HEIGHT))

# 上方的所有牌
tiles = []
# 牌堆里的牌
docks = []

# 难度设置
DIFFICULTY = ''

# 清空道具的属性
CLEAR_ITEM_IMAGE = pygame.image.load('images/clear_item.png')  # 假设你有一个清空道具的图片
CLEAR_ITEM_RECT = pygame.Rect((WIDTH - 200, 10), (100, 100))  # 道具在屏幕上的位置和大小
has_clear_item = True  # 玩家是否拥有清空道具的标志

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# 加载背景和遮罩图像
background = pygame.image.load('images/back.png')
mask = pygame.image.load('images/mask.png')
end = pygame.image.load('images/end.png')
win = pygame.image.load('images/win.png')

# 加载按钮图片
easy_button = pygame.image.load('images/easy_button.png')
normal_button = pygame.image.load('images/normal_button.png')
hard_button = pygame.image.load('images/hard_button.png')

# 播放背景音乐
pygame.mixer.music.load('music/bgm.mp3')
pygame.mixer.music.play(-1)

# 自定义牌类
class CustomTile:
    def __init__(self, image, rect, tag, layer, status):
        self.image = image
        self.rect = rect
        self.tag = tag
        self.layer = layer
        self.status = status

# 难度选择界面
def difficulty_select():
    global DIFFICULTY
    easy_rect = easy_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    normal_rect = normal_button.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    hard_rect = hard_button.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    DIFFICULTY = ''  # 初始化难度为空字符串
    while DIFFICULTY not in ['easy', 'normal', 'hard']:
        screen.fill((0, 0, 0))  # 用黑色填充屏幕
        screen.blit(background, (0, 0))  # 绘制背景图像
        screen.blit(easy_button, easy_rect)  # 绘制简单模式按钮
        screen.blit(normal_button, normal_rect)  # 绘制普通模式按钮
        screen.blit(hard_button, hard_rect)  # 绘制困难模式按钮
        pygame.display.update()  # 更新屏幕显示

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    DIFFICULTY = 'easy'
                elif normal_rect.collidepoint(event.pos):
                    DIFFICULTY = 'normal'
                elif hard_rect.collidepoint(event.pos):
                    DIFFICULTY = 'hard'

    return DIFFICULTY

# 初始化牌组，12*12张牌随机打乱
def init_tile_group():
    ts = list(range(1, 7)) * 6
    random.shuffle(ts)
    n = 0
    for k in range(4):  # 4层
        for i in range(4-k):  # 每层减1行
            for j in range(4-k):
                t = ts[n]  # 获取排种类
                n += 1
                tile_image = pygame.image.load(f'images/tile{t}.png')  # 加载图片
                tile_image = pygame.transform.scale(tile_image, (T_WIDTH, T_HEIGHT))
                tile_rect = tile_image.get_rect()
                tile_rect.topleft = (120 + (k * 0.5 + j) * T_WIDTH, 100 + (k * 0.5 + i) * T_HEIGHT * 0.9)
                tile = CustomTile(tile_image, tile_rect, t, k, 1 if k == 3 else 0)
                tiles.append(tile)
    for i in range(6):  # 剩余的6张牌放下面（为了凑整能通关）
        t = ts[n]
        n += 1
        tile_image = pygame.image.load(f'images/tile{t}.png')
        tile_image = pygame.transform.scale(tile_image, (T_WIDTH, T_HEIGHT))
        tile_rect = tile_image.get_rect()
        tile_rect.topleft = (210 + i * T_WIDTH, 516)
        tile = CustomTile(tile_image, tile_rect, t, 0, 1)
        tiles.append(tile)

# 游戏帧绘制函数
def draw():
    screen.blit(background, (0, 0))
    for tile in tiles:
        screen.blit(tile.image, tile.rect)
        if tile.status == 0:
            screen.blit(mask, tile.rect)
    for i, tile in enumerate(docks):
        tile.rect.left = DOCK.x + i * T_WIDTH
        tile.rect.top = DOCK.y
        screen.blit(tile.image, tile.rect)
    if len(docks) >= 7:
        screen.blit(end, (0, 0))
    if not tiles:
        screen.blit(win, (0, 0))
    if has_clear_item:
        screen.blit(CLEAR_ITEM_IMAGE, CLEAR_ITEM_RECT)
    pygame.display.flip()

# 鼠标点击响应
def on_mouse_down(pos):
    global docks, has_clear_item
    if len(docks) >= 7 or not tiles:
        return
    if has_clear_item and CLEAR_ITEM_RECT.collidepoint(pos):
        has_clear_item = False  # 消耗道具
        # 将卡槽里的牌放到底部牌堆的上方
        bottom_deck_start_y = 516 - T_HEIGHT  # 底部牌堆的上方起始y坐标
        for i, tile in enumerate(docks):
            tile.status = 1  # 重置状态为可点击
            # 计算应该放置的位置（底部牌堆的上方）
            new_x = 210 + i * T_WIDTH
            new_y = bottom_deck_start_y + (i // 7) * T_HEIGHT
            tile.rect.topleft = (new_x, new_y)
            tiles.append(tile)  # 加入到tiles列表
        docks.clear()  # 清空卡槽
        return
    for tile in reversed(tiles):  # 逆序循环是为了先判断上方的牌
        if tile.status == 1 and tile.rect.collidepoint(pos):
            tile.status = 2
            tiles.remove(tile)
            docks.append(tile)
            # 根据难度检查是否可以消除
            if DIFFICULTY == 'easy':
                # 简单模式下，一张相同的卡片就可以消除
                if len([t for t in docks if t.tag == tile.tag]) >= 1:
                    docks = [t for t in docks if t.tag != tile.tag]
            elif DIFFICULTY == 'normal':
                # 普通模式下，需要两张相同的卡片
                if len([t for t in docks if t.tag == tile.tag]) >= 2:
                    docks = [t for t in docks if t.tag != tile.tag]
            elif DIFFICULTY == 'hard':
                # 困难模式下，需要三张相同的卡片
                if len([t for t in docks if t.tag == tile.tag]) >= 3:
                    docks = [t for t in docks if t.tag != tile.tag]
            for down in tiles:
                if down.layer == tile.layer - 1 and down.rect.colliderect(tile.rect):
                    for up in tiles:
                        if up.layer == down.layer + 1 and up.rect.colliderect(down.rect):
                            break
                    else:
                        down.status = 1
            return

# 游戏主循环
def main():
    difficulty_select()  # 调用难度选择界面
    init_tile_group()  # 初始化牌组
    has_clear_item = True  # 玩家开始时拥有清空道具
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                on_mouse_down(event.pos)
        draw()
        clock.tick(FPS)
    pygame.quit()

# 启动游戏
main()