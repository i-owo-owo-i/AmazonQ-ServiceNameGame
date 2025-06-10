import pygame
import random
import os
import sys
import time
import math  # 追加: 数学関数を使用するため

# 初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AWS アーキテクチャ名当てクイズ")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)

# レトロゲーム風のカラーパレット
RETRO_BLACK = (0, 0, 0)
RETRO_WHITE = (255, 255, 255)
RETRO_RED = (208, 70, 72)
RETRO_GREEN = (52, 101, 36)
RETRO_BLUE = (89, 125, 206)
RETRO_YELLOW = (218, 212, 94)
RETRO_ORANGE = (210, 125, 44)
RETRO_PURPLE = (133, 76, 158)
RETRO_CYAN = (78, 156, 149)
RETRO_PINK = (241, 129, 191)
RETRO_BROWN = (153, 101, 21)
RETRO_GRAY = (127, 127, 127)
RETRO_LIGHT_GRAY = (170, 170, 170)
RETRO_DARK_GRAY = (80, 80, 80)
RETRO_DARK_BLUE = (38, 58, 108)

# 日本語対応のフォント設定（複数のフォントを試して、利用可能なものを使用）
def get_font(size):
    # 試すフォントの順序（一般的なフォントから順に）
    font_names = ['Meiryo', 'MS Gothic', 'Yu Gothic', 'Noto Sans CJK JP', 'Arial', 'Sans']
    
    # 各フォントを試す
    for font_name in font_names:
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            continue
    
    # どのフォントも使えない場合はデフォルトフォントを使用
    return pygame.font.Font(None, size)

# フォントを設定
font_large = get_font(36)
font_medium = get_font(28)
font_small = get_font(20)

# 難易度設定
DIFFICULTY_PRACTITIONER = "プラクティショナー"
DIFFICULTY_ASSOCIATE = "アソシエイト"
DIFFICULTY_PROFESSIONAL = "プロフェッショナル"
DIFFICULTY_SPECIALIST = "スペシャリスト"

# 難易度ごとのヒント回数
HINTS_BY_DIFFICULTY = {
    DIFFICULTY_PRACTITIONER: 10,
    DIFFICULTY_ASSOCIATE: 5,
    DIFFICULTY_PROFESSIONAL: 3,
    DIFFICULTY_SPECIALIST: 0
}

# 有名なAWSサービス（プラクティショナーモード用）
FAMOUS_SERVICES = [
    "Amazon EC2", "Amazon S3", "Amazon RDS", "AWS Lambda",
    "Amazon DynamoDB", "Amazon VPC", "Amazon CloudFront",
    "AWS IAM", "Amazon SNS", "Amazon SQS", "Amazon CloudWatch",
    "AWS CloudFormation", "Amazon API Gateway", "Amazon ECS",
    "Amazon Route 53", "AWS Elastic Beanstalk", "Amazon EKS",
    "Amazon Aurora", "Amazon Redshift", "AWS Fargate"
]

# アイコンフォルダの準備
def get_icons_dir():
    # 同フォルダ内のiconディレクトリを使用
    icons_dir = "icon"
    
    # iconディレクトリが存在するか確認
    if os.path.exists(icons_dir) and os.path.isdir(icons_dir):
        return icons_dir
    else:
        print(f"エラー: {icons_dir} ディレクトリが見つかりません。")
        return None

# アイコンの読み込み
def load_icons(icons_dir):
    loaded_services = {}
    category_services = {}  # カテゴリごとのサービス
    
    # iconディレクトリ内のすべてのサブディレクトリを検索
    for category_dir in os.listdir(icons_dir):
        category_path = os.path.join(icons_dir, category_dir)
        
        # ディレクトリのみを処理
        if os.path.isdir(category_path):
            category_services[category_dir] = []
            
            # 各カテゴリディレクトリ内のPNGファイルを検索
            for file in os.listdir(category_path):
                if file.endswith('.png'):
                    try:
                        # ファイル名からサービス名を抽出（.pngを除去）
                        service_name = os.path.splitext(file)[0]
                        
                        # サービス名をフォーマット（ハイフンをスペースに置換）
                        formatted_name = service_name.replace('-', ' ')
                        
                        # アイコンを読み込む
                        icon_path = os.path.join(category_path, file)
                        icon = pygame.image.load(icon_path)
                        
                        # アイコンのサイズを調整
                        icon = pygame.transform.scale(icon, (100, 100))
                        
                        # サービス名とアイコンを登録
                        loaded_services[formatted_name] = icon
                        category_services[category_dir].append(formatted_name)
                    except Exception as e:
                        print(f"アイコンの読み込みエラー ({file}): {e}")
    
    # アイコンが見つからない場合は、ダミーアイコンを作成
    if not loaded_services:
        print("アイコンが見つかりませんでした。ダミーアイコンを使用します。")
        dummy_services = [
            "Amazon EC2", "Amazon S3", "Amazon RDS", "AWS Lambda", 
            "Amazon DynamoDB", "Amazon VPC", "Amazon CloudFront", 
            "AWS IAM", "Amazon SNS", "Amazon SQS"
        ]
        
        for service in dummy_services:
            # ダミーアイコンを作成
            dummy_icon = pygame.Surface((100, 100))
            dummy_icon.fill(WHITE)
            pygame.draw.rect(dummy_icon, BLACK, (0, 0, 100, 100), 2)
            
            # サービス名の頭文字を表示
            initials = ''.join([word[0] for word in service.split() if word[0].isupper()])
            text = font_large.render(initials, True, BLACK)
            text_rect = text.get_rect(center=(50, 50))
            dummy_icon.blit(text, text_rect)
            
            loaded_services[service] = dummy_icon
    
    print(f"読み込まれたサービス数: {len(loaded_services)}")
    return loaded_services, category_services

# 難易度に基づいてサービスをフィルタリング
def filter_services_by_difficulty(loaded_services, category_services, difficulty):
    if difficulty == DIFFICULTY_PRACTITIONER:
        # プラクティショナーモード: 有名なサービスのみ
        available_services = {}
        for service in FAMOUS_SERVICES:
            if service in loaded_services:
                available_services[service] = loaded_services[service]
        return available_services, None
    
    elif difficulty == DIFFICULTY_ASSOCIATE:
        # アソシエイトモード: 特定のフォルダからのみ出題（フォルダはランダムに選択）
        # サービスが9つ以上あるフォルダのみを対象とする
        eligible_categories = []
        for category, services in category_services.items():
            if len(services) >= 9:
                eligible_categories.append(category)
        
        if not eligible_categories:
            # 該当するフォルダがない場合は全サービスを対象とする
            return loaded_services, None
        
        # ランダムにフォルダを1つ選択
        selected_category = random.choice(eligible_categories)
        
        # 選択されたフォルダのサービスのみを抽出
        available_services = {}
        for service in category_services[selected_category]:
            available_services[service] = loaded_services[service]
        
        return available_services, selected_category
    
    elif difficulty == DIFFICULTY_PROFESSIONAL or difficulty == DIFFICULTY_SPECIALIST:
        # プロフェッショナル/スペシャリストモード: すべてのサービス
        return loaded_services, None
    
    # デフォルトはすべてのサービス
    return loaded_services, None

# クイズの問題を生成
def generate_quiz(services, num_questions=10):
    service_names = list(services.keys())
    questions = []
    
    for _ in range(num_questions):
        # 正解のサービスをランダムに選択
        correct_service = random.choice(service_names)
        
        # 選択肢を作成（正解を含む9つ）
        choices = [correct_service]
        remaining_services = [s for s in service_names if s != correct_service]
        choices.extend(random.sample(remaining_services, min(8, len(remaining_services))))
        random.shuffle(choices)
        
        questions.append({
            "correct_service": correct_service,
            "choices": choices
        })
    
    return questions

# 難易度選択画面を表示
def show_difficulty_selection():
    difficulties = [
        {"name": DIFFICULTY_PRACTITIONER, "color": RETRO_GREEN, "description": "初級: 有名サービスのみ (30秒)"},
        {"name": DIFFICULTY_ASSOCIATE, "color": RETRO_BLUE, "description": "中級: 特定カテゴリから (30秒)"},
        {"name": DIFFICULTY_PROFESSIONAL, "color": RETRO_PURPLE, "description": "上級: 全サービスから (30秒)"},
        {"name": DIFFICULTY_SPECIALIST, "color": RETRO_RED, "description": "超級: 全サービスから (15秒)"}
    ]
    
    selected_index = None  # 初期状態では何も選択されていない
    running = True
    
    # レトロゲーム風の効果音
    try:
        # 効果音を鳴らす関数（実際には効果音ファイルが必要）
        def play_select_sound():
            pass  # 実際には pygame.mixer.Sound を使用
        
        def play_confirm_sound():
            pass  # 実際には pygame.mixer.Sound を使用
    except:
        def play_select_sound():
            pass
        
        def play_confirm_sound():
            pass
    
    # アニメーション用の変数
    animation_time = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    play_select_sound()  # 効果音
                    if selected_index is None:
                        selected_index = 0
                    else:
                        selected_index = (selected_index - 1) % len(difficulties)
                elif event.key == pygame.K_DOWN:
                    play_select_sound()  # 効果音
                    if selected_index is None:
                        selected_index = 0
                    else:
                        selected_index = (selected_index + 1) % len(difficulties)
                elif event.key == pygame.K_RETURN:
                    if selected_index is not None:
                        play_confirm_sound()  # 効果音
                        return difficulties[selected_index]["name"]
                elif event.key == pygame.K_ESCAPE:
                    return None
            
            # マウスクリックの処理
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # 各難易度ボタンの位置をチェック
                for i, _ in enumerate(difficulties):
                    rect_height = 70
                    rect_width = 450
                    rect_x = WIDTH // 2 - rect_width // 2
                    rect_y = 160 + i * 90
                    
                    if (rect_x <= mouse_pos[0] <= rect_x + rect_width and 
                        rect_y <= mouse_pos[1] <= rect_y + rect_height):
                        selected_index = i  # マウスオーバーで選択状態にする
                        play_confirm_sound()  # 効果音
                        return difficulties[i]["name"]
                
                # 「タイトルに戻る」ボタンのクリック判定
                back_button_width = 200
                back_button_height = 50
                back_button_x = WIDTH // 2 - back_button_width // 2
                back_button_y = HEIGHT - 80
                
                if (back_button_x <= mouse_pos[0] <= back_button_x + back_button_width and 
                    back_button_y <= mouse_pos[1] <= back_button_y + back_button_height):
                    play_confirm_sound()  # 効果音
                    return None
        
        # 背景 - レトロゲーム風
        screen.fill(RETRO_DARK_BLUE)
        
        # ピクセルアート風の背景パターン
        for x in range(0, WIDTH, 16):
            for y in range(0, HEIGHT, 16):
                if (x // 16 + y // 16) % 2 == 0:
                    pygame.draw.rect(screen, RETRO_BLUE, (x, y, 16, 16))
        
        # アニメーション時間を更新
        animation_time += 0.1
        
        # タイトル背景 - レトロゲーム風の枠
        title_bg = pygame.Rect(WIDTH // 2 - 350, 50, 700, 70)
        pygame.draw.rect(screen, RETRO_BLACK, title_bg)
        pygame.draw.rect(screen, RETRO_WHITE, title_bg, 4)
        
        # タイトル - ピクセルアート風
        title_text = font_large.render("難易度を選択してください", True, RETRO_WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 70))
        
        # マウスの位置を取得
        mouse_pos = pygame.mouse.get_pos()
        
        # 難易度オプション - レトロゲーム風
        for i, difficulty in enumerate(difficulties):
            rect_height = 70
            rect_width = 450
            rect_x = WIDTH // 2 - rect_width // 2
            rect_y = 160 + i * 90
            
            # マウスがボタン上にあるかチェック
            button_hover = (rect_x <= mouse_pos[0] <= rect_x + rect_width and 
                            rect_y <= mouse_pos[1] <= rect_y + rect_height)
            
            # マウスホバーで選択状態にする
            if button_hover and selected_index != i:
                selected_index = i
                play_select_sound()  # 効果音（ホバー時）
            
            # 選択中またはホバー中のボタンを強調
            if i == selected_index:
                # 選択中のボタン - レトロゲーム風
                pygame.draw.rect(screen, RETRO_BLACK, (rect_x, rect_y, rect_width, rect_height))
                pygame.draw.rect(screen, difficulty["color"], (rect_x, rect_y, rect_width, rect_height), 4)
                
                # 選択カーソル - ピクセルアート風（選択されている場合のみ表示）
                cursor_x = rect_x - 30
                cursor_y = rect_y + rect_height // 2
                
                # 点滅するカーソル
                if int(animation_time * 4) % 2 == 0:
                    pygame.draw.polygon(screen, RETRO_WHITE, [
                        (cursor_x, cursor_y),
                        (cursor_x + 20, cursor_y - 10),
                        (cursor_x + 20, cursor_y + 10)
                    ])
                
                name_text = font_medium.render(difficulty["name"], True, RETRO_WHITE)
            else:
                # 非選択のボタン - レトロゲーム風
                pygame.draw.rect(screen, RETRO_BLACK, (rect_x, rect_y, rect_width, rect_height))
                pygame.draw.rect(screen, RETRO_WHITE, (rect_x, rect_y, rect_width, rect_height), 2)
                name_text = font_medium.render(difficulty["name"], True, RETRO_LIGHT_GRAY)
            
            # 難易度名を中央に配置
            name_rect = name_text.get_rect(center=(rect_x + rect_width // 2, rect_y + 25))
            screen.blit(name_text, name_rect)
            
            # 説明テキスト - レトロゲーム風
            desc_color = difficulty["color"] if (i == selected_index) else RETRO_LIGHT_GRAY
            desc_text = font_small.render(difficulty["description"], True, desc_color)
            desc_rect = desc_text.get_rect(center=(rect_x + rect_width // 2, rect_y + 50))
            screen.blit(desc_text, desc_rect)
        
        # 「タイトルに戻る」ボタン - レトロゲーム風
        back_button_width = 200
        back_button_height = 50
        back_button_x = WIDTH // 2 - back_button_width // 2
        back_button_y = HEIGHT - 80
        
        # マウスがボタン上にあるかチェック
        back_button_hover = (back_button_x <= mouse_pos[0] <= back_button_x + back_button_width and 
                            back_button_y <= mouse_pos[1] <= back_button_y + back_button_height)
        
        # ボタンの描画
        pygame.draw.rect(screen, RETRO_BLACK, (back_button_x, back_button_y, back_button_width, back_button_height))
        pygame.draw.rect(screen, RETRO_RED if back_button_hover else RETRO_WHITE, 
                        (back_button_x, back_button_y, back_button_width, back_button_height), 3)
        
        # ボタンテキスト
        back_text = font_medium.render("タイトルに戻る", True, RETRO_WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, back_button_y + 15))
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    return None

# スタート画面を表示
def show_start_screen():
    running = True
    animation_offset = 0
    
    # レトロゲーム風の効果音
    try:
        # 効果音を鳴らす関数（実際には効果音ファイルが必要）
        def play_retro_sound():
            pass  # 実際には pygame.mixer.Sound を使用
    except:
        def play_retro_sound():
            pass
    
    # ピクセルアート風の雲
    clouds = []
    for _ in range(5):
        clouds.append({
            "x": random.randint(0, WIDTH),
            "y": random.randint(50, 200),
            "width": random.randint(60, 120),
            "speed": random.uniform(0.5, 1.5)
        })
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    play_retro_sound()  # 効果音
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
            
            # マウスクリックの処理
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # スタートボタンの位置
                button_width = 300
                button_height = 60
                button_x = WIDTH // 2 - button_width // 2
                button_y = HEIGHT - 100
                
                # スタートボタンがクリックされたか確認
                if (button_x <= mouse_pos[0] <= button_x + button_width and 
                    button_y <= mouse_pos[1] <= button_y + button_height):
                    play_retro_sound()  # 効果音
                    return True
        
        # アニメーション用のオフセットを更新
        animation_offset = (animation_offset + 0.5) % 10
        
        # 背景 - レトロゲーム風の単色背景
        screen.fill(RETRO_DARK_BLUE)
        
        # ピクセルアート風の雲を描画
        for cloud in clouds:
            # 雲を動かす
            cloud["x"] -= cloud["speed"]
            if cloud["x"] + cloud["width"] < 0:
                cloud["x"] = WIDTH
                cloud["y"] = random.randint(50, 200)
                cloud["width"] = random.randint(60, 120)
            
            # ピクセルアート風の雲を描画
            cloud_rect = pygame.Rect(cloud["x"], cloud["y"], cloud["width"], cloud["width"] // 2)
            pygame.draw.rect(screen, RETRO_LIGHT_GRAY, cloud_rect, border_radius=10)
            pygame.draw.rect(screen, RETRO_WHITE, cloud_rect, 2, border_radius=10)
        
        # タイトル背景 - レトロゲーム風の枠
        title_bg = pygame.Rect(WIDTH // 2 - 350, 50, 700, 100)
        pygame.draw.rect(screen, RETRO_BLACK, title_bg)
        pygame.draw.rect(screen, RETRO_WHITE, title_bg, 4)
        
        # タイトル - ピクセルアート風
        title_text = font_large.render("AWS アーキテクチャ名当てクイズ", True, RETRO_WHITE)
        
        # ピクセル風のタイトル（点滅効果）
        if int(animation_offset) % 2 == 0:
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 85))
        else:
            title_text_alt = font_large.render("AWS アーキテクチャ名当てクイズ", True, RETRO_YELLOW)
            screen.blit(title_text_alt, (WIDTH // 2 - title_text_alt.get_width() // 2, 85))
        
        # AWSロゴ風のアイコン - ピクセルアート風
        logo_size = 80
        logo_x = WIDTH // 2 - logo_size // 2
        logo_y = 170
        
        # ピクセルアート風の矢印
        pygame.draw.rect(screen, RETRO_ORANGE, (logo_x, logo_y, logo_size, logo_size // 2))
        pygame.draw.polygon(screen, RETRO_ORANGE, [
            (logo_x + logo_size // 4, logo_y + logo_size // 2),
            (logo_x + logo_size * 3 // 4, logo_y + logo_size // 2),
            (logo_x + logo_size // 2, logo_y + logo_size)
        ])
        
        # 説明の背景 - レトロゲーム風の枠
        instruction_bg = pygame.Rect(WIDTH // 2 - 350, 230, 700, 220)
        pygame.draw.rect(screen, RETRO_BLACK, instruction_bg)
        pygame.draw.rect(screen, RETRO_WHITE, instruction_bg, 4)
        
        # 説明 - ピクセルアート風
        instructions = [
            "AWSのサービスアイコンを当てるクイズゲームです",
            "表示されたサービス名に対応するアイコンをクリックしてください",
            "全10問、難易度によって制限時間が変わります",
            "",
            "スタートボタンをクリックするか、スペースキーを押してください",
            "ESCキーを押すと終了します"
        ]
        
        for i, line in enumerate(instructions):
            # ピクセルアート風のテキスト
            text = font_small.render(line, True, RETRO_WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 35))
        
        # スタートボタン - レトロゲーム風
        button_width = 300
        button_height = 60
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT - 100
        
        # マウスの位置を取得
        mouse_pos = pygame.mouse.get_pos()
        
        # マウスがボタン上にあるかチェック
        button_hover = (button_x <= mouse_pos[0] <= button_x + button_width and 
                        button_y <= mouse_pos[1] <= button_y + button_height)
        
        # ボタン - レトロゲーム風
        pygame.draw.rect(screen, RETRO_BLACK, (button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, RETRO_RED if button_hover else RETRO_WHITE, 
                        (button_x, button_y, button_width, button_height), 4)
        
        # ボタンテキスト - ピクセルアート風
        button_text = font_medium.render("スタート！", True, RETRO_WHITE)
        screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, button_y + 15))
        
        # 点滅する矢印 - ピクセルアート風
        if button_hover or int(animation_offset) % 2 == 0:
            arrow_text = font_medium.render("▼", True, RETRO_WHITE)
            screen.blit(arrow_text, (WIDTH // 2 - arrow_text.get_width() // 2, button_y - 30))
        
        # 画面の更新
        pygame.display.flip()
        pygame.time.delay(30)
    
    return False

def main():
    # アイコンディレクトリを取得
    icons_dir = get_icons_dir()
    if not icons_dir:
        print("アイコンディレクトリが見つかりません。ゲームを終了します。")
        return
    
    # アイコンを読み込む
    all_services, category_services = load_icons(icons_dir)
    if not all_services:
        print("アイコンの読み込みに失敗しました。ゲームを終了します。")
        return
    
    # スタート画面を表示
    if not show_start_screen():
        return
    
    # メインゲームループ
    while True:
        # 難易度選択
        difficulty = show_difficulty_selection()
        if difficulty is None:
            # 難易度選択をキャンセルした場合はスタート画面に戻る
            if not show_start_screen():
                return
            continue
        
        # 難易度に基づいてサービスをフィルタリング
        filtered_services, selected_category = filter_services_by_difficulty(all_services, category_services, difficulty)
        
        # 選択されたサービスが少なすぎる場合
        if len(filtered_services) < 9:
            print(f"警告: 選択された難易度 '{difficulty}' では利用可能なサービスが不足しています。すべてのサービスを使用します。")
            filtered_services = all_services
            selected_category = None
        
        # 制限時間を設定
        time_limit = 15 if difficulty == DIFFICULTY_SPECIALIST else 30
        
        # クイズの問題を生成
        questions = generate_quiz(filtered_services)
        
        # ゲーム変数
        current_question = 0
        score = 0
        game_over = False
        start_time = None
        hints_remaining = HINTS_BY_DIFFICULTY[difficulty]  # 残りヒント回数
        hint_active = False  # ヒントが有効かどうか
        
        # ゲームループ
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not game_over:
                        # ESCキーで難易度選択に戻る
                        break
                
                if not game_over and current_question < len(questions) and event.type == pygame.MOUSEBUTTONDOWN:
                    # 制限時間内にクリックした場合
                    if start_time and time.time() - start_time <= time_limit:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # ESCキーで難易度選択に戻れるので、ボタンは不要
                        
                        # ヒントボタンがクリックされたか確認
                        if hints_remaining > 0:
                            hint_button_width = 180
                            hint_button_height = 40
                            hint_button_x = WIDTH - hint_button_width - 20
                            hint_button_y = 10  # 右上に移動
                            
                            if (hint_button_x <= mouse_pos[0] <= hint_button_x + hint_button_width and 
                                hint_button_y <= mouse_pos[1] <= hint_button_y + hint_button_height):
                                # ヒントを使用
                                hint_active = True
                                hints_remaining -= 1
                                continue  # クリック処理を終了
                        
                        # 選択肢のクリック判定
                        question = questions[current_question]
                        choices = question["choices"]
                        correct_service = question["correct_service"]
                        
                        # 3x3のグリッドで選択肢を配置
                        grid_center_x = WIDTH // 2
                        grid_center_y = HEIGHT // 2
                        grid_width = 600
                        grid_height = 450
                        
                        for i, service in enumerate(choices):
                            # グリッド内の位置を計算（中央揃え）
                            col = i % 3
                            row = i // 3
                            
                            x = grid_center_x - grid_width // 2 + col * (grid_width // 3) + (grid_width // 6)
                            y = grid_center_y - grid_height // 2 + row * (grid_height // 3) + (grid_height // 6)
                            
                            # ヒントが有効で、このアイコンがヒント対象外の場合はクリック判定をスキップ
                            if hint_active:
                                # 正解のインデックスを取得
                                correct_index = choices.index(correct_service)
                                hint_indices = [correct_index]  # 正解は必ず含める
                                
                                # 正解以外からランダムに3つ選ぶ（毎回同じ3つを選ぶためにシードを固定）
                                random.seed(current_question)  # 現在の問題番号をシードにする
                                other_indices = [j for j in range(9) if j != correct_index]
                                random.shuffle(other_indices)
                                hint_indices.extend(other_indices[:3])  # 3つ追加
                                random.seed()  # シードをリセット
                                
                                if i not in hint_indices:
                                    continue  # ヒント対象外はクリック判定をスキップ
                            
                            # クリック判定
                            if (x - 60 <= mouse_pos[0] <= x + 60) and (y - 60 <= mouse_pos[1] <= y + 60):
                                # 正解判定
                                if service == correct_service:
                                    score += 1
                                
                                # 次の問題へ
                                current_question += 1
                                if current_question < len(questions):
                                    start_time = time.time()
                                    hint_active = False  # ヒントをリセット
                                else:
                                    game_over = True
                                break
            
            # 画面をクリア - レトロゲーム風の背景
            screen.fill(RETRO_DARK_BLUE)
            
            if not game_over and current_question < len(questions):
                # ピクセルアート風の背景パターン
                for x in range(0, WIDTH, 16):
                    for y in range(0, HEIGHT, 16):
                        if (x // 16 + y // 16) % 2 == 0:
                            pygame.draw.rect(screen, RETRO_BLUE, (x, y, 16, 16))
                
                # 現在の問題を表示
                question = questions[current_question]
                choices = question["choices"]
                correct_service = question["correct_service"]
                
                # 難易度に応じた色を設定
                if difficulty == DIFFICULTY_PRACTITIONER:
                    difficulty_color = RETRO_GREEN
                elif difficulty == DIFFICULTY_ASSOCIATE:
                    difficulty_color = RETRO_BLUE
                elif difficulty == DIFFICULTY_PROFESSIONAL:
                    difficulty_color = RETRO_PURPLE
                else:  # DIFFICULTY_SPECIALIST
                    difficulty_color = RETRO_RED
                
                # 上部のステータスバー背景 - レトロゲーム風
                status_bar = pygame.Rect(0, 0, WIDTH, 60)
                pygame.draw.rect(screen, RETRO_BLACK, status_bar)
                pygame.draw.rect(screen, RETRO_WHITE, status_bar, 2)
                
                # 難易度と問題数を左上に表示 - レトロゲーム風
                difficulty_text = f"{difficulty} - 問題 {current_question + 1}/{len(questions)}"
                diff_surface = font_medium.render(difficulty_text, True, difficulty_color)
                screen.blit(diff_surface, (20, 15))
                
                # マウスの位置を取得
                mouse_pos = pygame.mouse.get_pos()
                
                # ヒントボタン（難易度に応じて表示/非表示）- レトロゲーム風
                if hints_remaining > 0:
                    hint_button_width = 180
                    hint_button_height = 40
                    hint_button_x = WIDTH - hint_button_width - 20
                    hint_button_y = 10  # 右上に移動
                    
                    # マウスがボタン上にあるかチェック
                    hint_hover = (hint_button_x <= mouse_pos[0] <= hint_button_x + hint_button_width and 
                                  hint_button_y <= mouse_pos[1] <= hint_button_y + hint_button_height)
                    
                    # ボタンの背景 - レトロゲーム風
                    pygame.draw.rect(screen, RETRO_BLACK, (hint_button_x, hint_button_y, hint_button_width, hint_button_height))
                    pygame.draw.rect(screen, RETRO_YELLOW if hint_hover else RETRO_WHITE, 
                                    (hint_button_x, hint_button_y, hint_button_width, hint_button_height), 2)
                    
                    # ボタンテキスト - レトロゲーム風
                    hint_text = font_small.render(f"ヒント: あと{hints_remaining}回", True, RETRO_YELLOW if hint_hover else RETRO_WHITE)
                    screen.blit(hint_text, (hint_button_x + 10, hint_button_y + 10))
                
                # 制限時間を表示
                if start_time is None:
                    start_time = time.time()
                
                elapsed_time = time.time() - start_time
                remaining_time = max(0, time_limit - elapsed_time)
                
                # 残り時間に応じて色を変更 - レトロゲーム風
                if remaining_time > time_limit * 0.5:
                    time_color = RETRO_GREEN
                elif remaining_time > time_limit * 0.25:
                    time_color = RETRO_YELLOW
                else:
                    time_color = RETRO_RED
                
                # タイマーの背景（四角形）- レトロゲーム風
                timer_width = 90
                timer_height = 60
                timer_x = 20
                timer_y = HEIGHT - 80
                pygame.draw.rect(screen, RETRO_BLACK, (timer_x, timer_y, timer_width, timer_height))
                pygame.draw.rect(screen, time_color, (timer_x, timer_y, timer_width, timer_height), 2)
                
                # 残り時間テキスト - レトロゲーム風
                time_text = f"{int(remaining_time)}"
                time_surface = font_large.render(time_text, True, time_color)
                time_rect = time_surface.get_rect(center=(timer_x + timer_width // 2, timer_y + timer_height // 2 - 10))
                screen.blit(time_surface, time_rect)
                
                # 「秒」の表示 - レトロゲーム風
                seconds_text = "秒"
                seconds_surface = font_small.render(seconds_text, True, time_color)
                seconds_rect = seconds_surface.get_rect(center=(timer_x + timer_width // 2, timer_y + timer_height // 2 + 15))
                screen.blit(seconds_surface, seconds_rect)
                
                # 下部に問題文を表示 - レトロゲーム風
                question_bg_rect = pygame.Rect(WIDTH // 2 - 250, HEIGHT - 80, 500, 60)
                pygame.draw.rect(screen, RETRO_BLACK, question_bg_rect)
                pygame.draw.rect(screen, difficulty_color, question_bg_rect, 2)
                
                # 問題文を中央に配置 - レトロゲーム風
                text = font_medium.render(f"{correct_service}", True, RETRO_WHITE)
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
                screen.blit(text, text_rect)
                
                # 選択肢を表示（3x3のグリッド）- レトロゲーム風
                grid_center_x = WIDTH // 2
                grid_center_y = HEIGHT // 2
                grid_width = 600
                grid_height = 450
                
                # ヒントが有効な場合、正解を含む4つ以外をグレーアウト
                hint_indices = []
                if hint_active:
                    # 正解のインデックスを取得
                    correct_index = choices.index(correct_service)
                    hint_indices = [correct_index]  # 正解は必ず含める
                    
                    # 正解以外からランダムに3つ選ぶ（毎回同じ3つを選ぶためにシードを固定）
                    random.seed(current_question)  # 現在の問題番号をシードにする
                    other_indices = [i for i in range(9) if i != correct_index]
                    random.shuffle(other_indices)
                    hint_indices.extend(other_indices[:3])  # 3つ追加
                    random.seed()  # シードをリセット
                
                for i, service in enumerate(choices):
                    # グリッド内の位置を計算（中央揃え）
                    col = i % 3
                    row = i // 3
                    
                    x = grid_center_x - grid_width // 2 + col * (grid_width // 3) + (grid_width // 6)
                    y = grid_center_y - grid_height // 2 + row * (grid_height // 3) + (grid_height // 6)
                    
                    # ヒントが有効で、このアイコンがヒント対象外の場合は非表示にする
                    if hint_active and i not in hint_indices:
                        # 背景の四角形だけ表示して、アイコンは表示しない - レトロゲーム風
                        pygame.draw.rect(screen, RETRO_BLACK, (x - 50, y - 50, 100, 100))
                        pygame.draw.rect(screen, RETRO_DARK_GRAY, (x - 50, y - 50, 100, 100), 2)
                    else:
                        # 通常表示 - レトロゲーム風
                        pygame.draw.rect(screen, RETRO_BLACK, (x - 50, y - 50, 100, 100))
                        pygame.draw.rect(screen, difficulty_color, (x - 50, y - 50, 100, 100), 2)
                    
                        # アイコンを表示（ヒント対象外の場合は表示しない）
                        if not (hint_active and i not in hint_indices):
                            icon = filtered_services[service]
                            icon_rect = icon.get_rect(center=(x, y))
                            screen.blit(icon, icon_rect)
                
                # 制限時間が過ぎたら次の問題へ
                if remaining_time <= 0:
                    current_question += 1
                    if current_question < len(questions):
                        start_time = time.time()
                        hint_active = False  # ヒントをリセット
                    else:
                        game_over = True
            
            elif game_over:
                # ゲーム終了画面 - レトロゲーム風
                screen.fill(RETRO_DARK_BLUE)
                
                # ピクセルアート風の背景パターン
                for x in range(0, WIDTH, 16):
                    for y in range(0, HEIGHT, 16):
                        if (x // 16 + y // 16) % 2 == 0:
                            pygame.draw.rect(screen, RETRO_BLUE, (x, y, 16, 16))
                
                # 難易度に応じた色を設定
                if difficulty == DIFFICULTY_PRACTITIONER:
                    difficulty_color = RETRO_GREEN
                elif difficulty == DIFFICULTY_ASSOCIATE:
                    difficulty_color = RETRO_BLUE
                elif difficulty == DIFFICULTY_PROFESSIONAL:
                    difficulty_color = RETRO_PURPLE
                else:  # DIFFICULTY_SPECIALIST
                    difficulty_color = RETRO_RED
                
                # 結果表示の背景 - レトロゲーム風の枠
                result_bg = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 200, 600, 350)
                pygame.draw.rect(screen, RETRO_BLACK, result_bg)
                pygame.draw.rect(screen, RETRO_WHITE, result_bg, 4)
                
                # 難易度表示 - レトロゲーム風
                difficulty_text = f"難易度: {difficulty}"
                if difficulty == DIFFICULTY_ASSOCIATE and selected_category:
                    difficulty_text += f" ({selected_category})"
                difficulty_text = font_medium.render(difficulty_text, True, difficulty_color)
                screen.blit(difficulty_text, (WIDTH // 2 - difficulty_text.get_width() // 2, HEIGHT // 2 - 150))
                
                # ゲーム終了テキスト - レトロゲーム風（点滅効果）
                if int(time.time() * 2) % 2 == 0:
                    game_over_text = font_large.render("ゲーム終了！", True, RETRO_WHITE)
                else:
                    game_over_text = font_large.render("ゲーム終了！", True, RETRO_YELLOW)
                screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
                
                # スコアを10点満点で計算（1問正解=10点）
                points_per_question = 10
                total_points = score * points_per_question
                max_points = len(questions) * points_per_question
                
                # スコア表示 - レトロゲーム風
                final_score_text = font_large.render(f"最終スコア: {total_points}点/{max_points}点", True, RETRO_WHITE)
                screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2 - 50))
                
                # スコアに応じたメッセージ - レトロゲーム風
                if score == len(questions):
                    message = "完璧です！おめでとうございます！"
                    color = RETRO_CYAN
                elif score >= len(questions) * 0.8:
                    message = "素晴らしい成績です！"
                    color = RETRO_GREEN
                elif score >= len(questions) * 0.6:
                    message = "良い成績です！"
                    color = RETRO_GREEN
                elif score >= len(questions) * 0.4:
                    message = "もう少し頑張りましょう！"
                    color = RETRO_YELLOW
                else:
                    message = "AWSサービスについてもっと学びましょう！"
                    color = RETRO_RED
                    
                # メッセージ表示 - レトロゲーム風
                message_text = font_medium.render(message, True, color)
                screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2))
                
                # 操作説明の背景（高さを拡大） - レトロゲーム風
                button_area_height = 150
                button_bg = pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 + 70, 600, button_area_height)
                pygame.draw.rect(screen, RETRO_BLACK, button_bg)
                pygame.draw.rect(screen, RETRO_WHITE, button_bg, 2)
                
                # ボタン - レトロゲーム風
                button_width = 180
                button_height = 50
                button_margin = 20
                
                # 難易度選択に戻るボタン
                restart_button_x = WIDTH // 2 - button_width - button_margin
                restart_button_y = HEIGHT // 2 + 100
                
                # マウスの位置を取得
                mouse_pos = pygame.mouse.get_pos()
                
                # マウスがボタン上にあるかチェック
                restart_hover = (restart_button_x <= mouse_pos[0] <= restart_button_x + button_width and 
                                restart_button_y <= mouse_pos[1] <= restart_button_y + button_height)
                
                # 難易度選択ボタンの描画
                pygame.draw.rect(screen, RETRO_BLACK, (restart_button_x, restart_button_y, button_width, button_height))
                pygame.draw.rect(screen, RETRO_GREEN if restart_hover else RETRO_WHITE, 
                                (restart_button_x, restart_button_y, button_width, button_height), 3)
                
                # ボタンテキスト
                restart_text = font_small.render("難易度選択に戻る", True, RETRO_WHITE)
                screen.blit(restart_text, (restart_button_x + button_width // 2 - restart_text.get_width() // 2, 
                                          restart_button_y + button_height // 2 - restart_text.get_height() // 2))
                
                # タイトル画面に戻るボタン
                title_button_x = WIDTH // 2 + button_margin
                title_button_y = HEIGHT // 2 + 100
                
                # マウスがボタン上にあるかチェック
                title_hover = (title_button_x <= mouse_pos[0] <= title_button_x + button_width and 
                              title_button_y <= mouse_pos[1] <= title_button_y + button_height)
                
                # タイトルボタンの描画
                pygame.draw.rect(screen, RETRO_BLACK, (title_button_x, title_button_y, button_width, button_height))
                pygame.draw.rect(screen, RETRO_BLUE if title_hover else RETRO_WHITE, 
                                (title_button_x, title_button_y, button_width, button_height), 3)
                
                # ボタンテキスト
                title_text = font_small.render("タイトルに戻る", True, RETRO_WHITE)
                screen.blit(title_text, (title_button_x + button_width // 2 - title_text.get_width() // 2, 
                                        title_button_y + button_height // 2 - title_text.get_height() // 2))
                
                # ゲーム終了ボタン
                quit_button_x = WIDTH // 2 - button_width // 2
                quit_button_y = HEIGHT // 2 + 160
                
                # マウスがボタン上にあるかチェック
                quit_hover = (quit_button_x <= mouse_pos[0] <= quit_button_x + button_width and 
                             quit_button_y <= mouse_pos[1] <= quit_button_y + button_height)
                
                # 終了ボタンの描画
                pygame.draw.rect(screen, RETRO_BLACK, (quit_button_x, quit_button_y, button_width, button_height))
                pygame.draw.rect(screen, RETRO_RED if quit_hover else RETRO_WHITE, 
                                (quit_button_x, quit_button_y, button_width, button_height), 3)
                
                # ボタンテキスト
                quit_text = font_small.render("ゲーム終了", True, RETRO_WHITE)
                screen.blit(quit_text, (quit_button_x + button_width // 2 - quit_text.get_width() // 2, 
                                       quit_button_y + button_height // 2 - quit_text.get_height() // 2))
                
                # イベント処理はメインのイベントループで行うため、ここでは行わない
                # キー入力を確認（キーボード操作も残しておく）
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    # 難易度選択に戻る
                    running = False  # ゲームループを抜ける
                elif keys[pygame.K_t]:
                    # タイトル画面に戻る
                    if not show_start_screen():
                        return
                    running = False  # ゲームループを抜ける
                elif keys[pygame.K_ESCAPE]:
                    return
                    
                # マウスクリックの処理
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 難易度選択ボタンがクリックされたか確認
                    if restart_hover:
                        running = False  # ゲームループを抜ける
                    
                    # タイトルボタンがクリックされたか確認
                    elif title_hover:
                        if not show_start_screen():
                            return
                        running = False  # ゲームループを抜ける
                    
                    # 終了ボタンがクリックされたか確認
                    elif quit_hover:
                        pygame.quit()
                        sys.exit()
                
                # キー入力を確認（キーボード操作も残しておく）
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    # 難易度選択に戻る
                    running = False  # ゲームループを抜ける
                    break
                elif keys[pygame.K_t]:
                    # タイトル画面に戻る
                    if not show_start_screen():
                        return
                    running = False  # ゲームループを抜ける
                    break
                elif keys[pygame.K_ESCAPE]:
                    return
            
            # 画面を更新
            pygame.display.flip()
            pygame.time.delay(30)

if __name__ == "__main__":
    main()
