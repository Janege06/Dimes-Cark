import pygame
import math
import asyncio
from game_state import GameState
from question_manager import QuestionManager, Category
from ui import Ui, Button, Panel, StatBox, ProgressBar, CategoryTag, render_with_emojis, draw_text_wrapped
from wheel import Wheel

async def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Dimes - Bilgi Çarkı")
    clock = pygame.time.Clock()
    running = True

    # Colors & Fonts
    bg_color = pygame.Color("#0d1b2a")
    gold = pygame.Color("#fbbf24")
    white = pygame.Color("#ffffff")
    orange_gradient = (pygame.Color("#ff8c00"), pygame.Color("#ff4500"))
    orange_shadow = pygame.Color("#8b2400")
    gray_gradient = (pygame.Color("#1e3a55"), pygame.Color("#122236"))
    gray_shadow = pygame.Color("#060e18")
    
    font_fredoka_lg = pygame.font.SysFont("arial", 48, bold=True)
    font_fredoka_md = pygame.font.SysFont("arial", 32, bold=True)
    font_fredoka_sm = pygame.font.SysFont("arial", 24, bold=True)
    font_nunito_reg = pygame.font.SysFont("arial", 20)
    font_nunito_bold = pygame.font.SysFont("arial", 20, bold=True)
    font_stat_val = pygame.font.SysFont("arial", 22, bold=True)
    font_stat_lbl = pygame.font.SysFont("arial", 12, bold=True)
    
    # Use system emoji fonts that might be available in browser/WASM
    # More extensive list including lowercase, no-space, and common names
    emoji_font_names = [
        "Segoe UI Emoji", "segoeuiemoji", 
        "Apple Color Emoji", "applecoloremoji",
        "Noto Color Emoji", "notocoloremoji",
        "Android Emoji", "androidemoji",
        "EmojiSymbols", "emojisymbols",
        "Symbola", "symbola",
        "Segoe UI Symbol", "segoeuisymbol",
        "DejaVu Sans", "dejavusans"
    ]
    
    font_emoji = None
    for f_name in emoji_font_names:
        matched = pygame.font.match_font(f_name)
        if matched:
            try:
                font_emoji = pygame.font.Font(matched, 32)
                # Quick check if it's not just a generic font by rendering an emoji
                # (though this doesn't guarantee it's not a square, some fonts have the square glyph)
                if font_emoji.render("🌿", True, (255,255,255)).get_width() > 10:
                    break
            except:
                continue
    
    if font_emoji is None:
        font_emoji = pygame.font.SysFont("arial, sans-serif", 32)

    # Components
    ui = Ui()
    qm = QuestionManager()
    wheel = Wheel(emoji_font=font_emoji)
    gs = GameState()

    # HUD Elements
    score_box = StatBox(pygame.Rect(950, 10, 80, 40), "SKOR", font_stat_val, font_stat_lbl)
    streak_box = StatBox(pygame.Rect(1040, 10, 80, 40), "SERI", font_stat_val, font_stat_lbl)
    progress_bar = ProgressBar(800, 25, gs.TOTAL_ROUNDS)

    # Panels
    q_panel = Panel(pygame.Rect(750, 150, 450, 450), gray_gradient, pygame.Color("#1e3a55"))
    start_panel = Panel(pygame.Rect(440, 120, 400, 480), gray_gradient, pygame.Color("#1e3a55"))
    end_panel = Panel(pygame.Rect(440, 160, 400, 450), gray_gradient, pygame.Color("#1e3a55"))

    # Buttons
    start_btn = Button(pygame.Rect(480, 560, 320, 80), "🎥 OYUNU BAŞLAT", font_fredoka_sm, orange_gradient, orange_shadow, white, emoji_font=font_emoji)
    
    # Category Tags for Start Screen
    tag_font = font_nunito_bold
    tags = [
        CategoryTag(pygame.Rect(460, 380, 175, 50), "🌿 Sürdürülebilirlik", tag_font, pygame.Color("#f97316"), emoji_font=font_emoji),
        CategoryTag(pygame.Rect(645, 380, 115, 50), "🆓 Ürünler", tag_font, pygame.Color("#22c55e"), emoji_font=font_emoji),
        CategoryTag(pygame.Rect(460, 440, 150, 50), "🌍 Genel Kültür", tag_font, pygame.Color("#3b82f6"), emoji_font=font_emoji),
        CategoryTag(pygame.Rect(620, 440, 140, 50), "⭐ BONUS x2", tag_font, pygame.Color("#fbbf24"), emoji_font=font_emoji),
    ]
    spin_btn = Button(pygame.Rect(200, 620, 200, 50), "ÇARKI ÇEVİR", font_fredoka_sm, orange_gradient, orange_shadow, white, emoji_font=font_emoji)
    next_btn = Button(pygame.Rect(1020, 540, 150, 40), "DEVAM →", font_nunito_bold, gray_gradient, gray_shadow, white, border_radius=12, emoji_font=font_emoji)
    replay_btn = Button(pygame.Rect(540, 480, 200, 50), "TEKRAR OYNA", font_fredoka_sm, orange_gradient, orange_shadow, white, emoji_font=font_emoji)
    menu_btn = Button(pygame.Rect(540, 540, 200, 40), "MENÜYE DÖN", font_nunito_bold, gray_gradient, gray_shadow, white, emoji_font=font_emoji)
    pause_btn = Button(pygame.Rect(1200, 10, 40, 40), "||", font_fredoka_sm, gray_gradient, gray_shadow, white, border_radius=8, emoji_font=font_emoji)
    resume_btn = Button(pygame.Rect(540, 300, 200, 50), "DEVAM ET", font_fredoka_sm, orange_gradient, orange_shadow, white, emoji_font=font_emoji)
    quit_btn = Button(pygame.Rect(540, 370, 200, 40), "MENUYE DON", font_nunito_bold, gray_gradient, gray_shadow, white, emoji_font=font_emoji)

    option_buttons = []
    
    def start_game():
        gs.__init__()
        gs.screen = 'main'
        wheel.angle = 0
        build_round_bar()

    def build_round_bar():
        progress_bar.results = gs.round_results
        progress_bar.current_round = gs.round

    def on_landed(cat):
        gs.spinning = False
        gs.current_category = cat
        gs.answering = True
        
        q, idx = qm.get_random_question(cat, gs.used_questions[cat.value])
        gs.current_question = q
        gs.used_questions[cat.value].append(idx)
        
        gs.time_left = gs.Q_TIME
        # Setup option buttons
        option_buttons.clear()
        if q:
            for i, opt in enumerate(q['opts']):
                row = i // 2
                col = i % 2
                rect = pygame.Rect(780 + col * 200, 370 + row * 60, 180, 50)
                btn = Button(rect, opt, font_nunito_bold, gray_gradient, gray_shadow, white, border_radius=12, emoji_font=font_emoji)
                option_buttons.append(btn)

    def handle_answer(idx):
        if not gs.answering or gs.current_question is None: return
        gs.answering = False
        correct = gs.current_question['ans']
        
        is_bonus = gs.current_category == Category.BONUS
        time_bonus = round(gs.time_left * 3)
        
        if idx == correct:
            gs.streak += 1
            gs.max_streak = max(gs.max_streak, gs.streak)
            gs.correct_answers += 1
            base = 100
            streak_mul = min(gs.streak, 4)
            pts = (base + time_bonus) * streak_mul * (2 if is_bonus else 1)
            gs.score += pts
            if is_bonus: gs.bonus_points += pts
            gs.round_results.append('ok')
            gs.feedback = "DOĞRU! ✅"
        else:
            gs.streak = 0
            gs.lives -= 1
            gs.round_results.append('bad')
            gs.feedback = "YANLIŞ! 😬"
        
        build_round_bar()
        if gs.lives <= 0:
            gs.screen = 'end'

    def next_round():
        gs.round += 1
        if gs.round >= gs.TOTAL_ROUNDS:
            gs.screen = 'end'
        else:
            gs.current_question = None
            gs.answering = False
            gs.current_category = None
            build_round_bar()

    while running:
        dt = clock.tick(60) / 1000.0
        await asyncio.sleep(0)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            if gs.screen == 'start':
                if start_btn.handle_event(event):
                    start_game()
            elif gs.screen == 'main':
                if pause_btn.handle_event(event):
                    gs.screen = 'pause'
                
                if not gs.spinning and not gs.answering:
                    if spin_btn.handle_event(event):
                        gs.spinning = True
                        wheel.spin(on_landed)
                
                if gs.answering:
                    for i, btn in enumerate(option_buttons):
                        if btn.handle_event(event):
                            handle_answer(i)
                elif gs.current_question is not None:
                    if next_btn.handle_event(event):
                        next_round()
            elif gs.screen == 'pause':
                if resume_btn.handle_event(event):
                    gs.screen = 'main'
                if quit_btn.handle_event(event):
                    gs.screen = 'start'
            elif gs.screen == 'end':
                if replay_btn.handle_event(event):
                    start_game()
                if menu_btn.handle_event(event):
                    gs.screen = 'start'

        # Update
        if gs.screen == 'main':
            wheel.update()
            if gs.answering:
                gs.time_left -= dt
                if gs.time_left <= 0:
                    gs.time_left = 0
                    handle_answer(-1)

        # Draw
        screen.fill(bg_color)
        
        if gs.screen == 'start':
            # Background
            screen.fill(bg_color)
            
            # 1. Logo
            logo_rect = pygame.Rect(640 - 40, 60, 80, 80)
            pygame.draw.rect(screen, white, logo_rect, border_radius=15)
            # Dimes text in red inside the logo
            dimes_font = pygame.font.SysFont("arial", 20, bold=True)
            dimes_surf = dimes_font.render("DİMES", True, pygame.Color("#e11d48"))
            dimes_rect = dimes_surf.get_rect(center=logo_rect.center)
            screen.blit(dimes_surf, dimes_rect)
            # Red underline
            pygame.draw.line(screen, pygame.Color("#e11d48"), (dimes_rect.left, dimes_rect.bottom-2), (dimes_rect.right, dimes_rect.bottom-2), 2)

            # 2. Title with shadow
            # Shadow
            title_text = "BİLGİ ÇARKI"
            title_shadow = font_fredoka_lg.render(title_text, True, pygame.Color(0, 0, 0, 100))
            title_rect = title_shadow.get_rect(center=(640 + 4, 220 + 4))
            screen.blit(title_shadow, title_rect)
            # Main Title
            title_main = font_fredoka_lg.render(title_text, True, gold)
            title_rect = title_main.get_rect(center=(640, 220))
            screen.blit(title_main, title_rect)

            # 3. Description
            desc_text = "Çarkı çevir, kategori kazan,\nsoruyu bil, bonus puan kap!"
            draw_text_wrapped(screen, desc_text, font_nunito_reg, pygame.Color(200, 200, 200), pygame.Rect(440, 270, 400, 80), align="center")

            # 4. Tags
            for tag in tags:
                tag.draw(screen)

            # 5. Start Button
            start_btn.draw(screen)
            
        elif gs.screen == 'main':
            # HUD
            pygame.draw.rect(screen, pygame.Color("#0a121e"), (0, 0, 1280, 60))
            pygame.draw.line(screen, pygame.Color("#1e3a55"), (0, 60), (1280, 60), 2)
            
            logo_text = font_fredoka_sm.render("BİLGİ ÇARKI", True, gold)
            screen.blit(logo_text, (20, 15))
            
            score_box.value = gs.score
            score_box.draw(screen)
            streak_box.value = gs.streak
            streak_box.draw(screen)
            progress_bar.draw(screen)
            pause_btn.draw(screen)
            
            # Lives
            for i in range(3):
                color = pygame.Color("red") if i < gs.lives else pygame.Color(100, 100, 100)
                pygame.draw.circle(screen, color, (1150 + i*25, 30), 8)

            # Wheel
            wheel_surf = pygame.Surface((600, 600), pygame.SRCALPHA)
            wheel.draw(wheel_surf)
            screen.blit(pygame.transform.scale(wheel_surf, (400, 400)), (100, 150))
            # Pointer
            # In the image it's a yellow triangle pointing down.
            # Wheel is at (100, 150), size (400, 400). CX=200, CY=200 relative to that.
            # Absolute CX = 100 + 200 = 300. Absolute top of wheel is 150.
            pygame.draw.polygon(screen, gold, [(300, 150), (280, 115), (320, 115)])
            # Hub - The wheel has its own hub, but we might want to ensure it's not scaled away or is clear.
            # The wheel is scaled from 600 to 400.
            # The hub in wheel.py is at CX=300, CY=300 with IR=60.
            # Scaled to (400, 400), CX=200, CY=200, IR=40.
            # It's already drawn inside wheel.draw.
            
            if not gs.spinning and not gs.answering and gs.current_question is None:
                spin_btn.draw(screen)
            
            # Question Panel
            q_panel.draw(screen)
            if gs.current_question:
                cat_props = wheel.CAT_PROPS[gs.current_category]
                cat_tag = font_fredoka_sm.render(cat_props['name'].upper(), True, pygame.Color(cat_props['color']))
                screen.blit(cat_tag, (780, 180))
                
                # Timer
                timer_text = font_fredoka_md.render(str(math.ceil(gs.time_left)), True, gold)
                screen.blit(timer_text, (1130, 180))
                
                # Question text
                q_text_rect = pygame.Rect(780, 230, 400, 120)
                draw_text_wrapped(screen, gs.current_question['q'], font_nunito_bold, white, q_text_rect, align="left", emoji_font=font_emoji)
                
                for btn in option_buttons:
                    btn.draw(screen)
                
                if not gs.answering:
                    if font_emoji:
                        render_with_emojis(screen, gs.feedback, font_fredoka_sm, font_emoji, gold, pygame.Rect(780, 540, 230, 40), align="left")
                    else:
                        feedback_surf = font_fredoka_sm.render(gs.feedback, True, gold)
                        screen.blit(feedback_surf, (780, 540))
                    next_btn.draw(screen)
            else:
                placeholder = font_nunito_bold.render("Çarkı çevirerek kategori seç", True, white)
                screen.blit(placeholder, placeholder.get_rect(center=q_panel.rect.center))

        elif gs.screen == 'pause':
            Panel(pygame.Rect(490, 200, 300, 300), gray_gradient, pygame.Color("#1e3a55")).draw(screen)
            title = font_fredoka_md.render("DURAKLATILDI", True, gold)
            screen.blit(title, title.get_rect(center=(640, 250)))
            resume_btn.draw(screen)
            quit_btn.draw(screen)
            
        elif gs.screen == 'end':
            end_panel.draw(screen)
            title_text = "HARİKAYDIN! 🏆" if gs.correct_answers >= 6 else "OYUN BİTTİ!"
            if font_emoji:
                render_with_emojis(screen, title_text, font_fredoka_lg, font_emoji, gold, pygame.Rect(440, 200, 400, 60))
            else:
                title = font_fredoka_lg.render(title_text, True, gold)
                screen.blit(title, title.get_rect(center=(640, 220)))
            
            res_text = f"{gs.TOTAL_ROUNDS} soruda {gs.correct_answers} doğru!"
            res_surf = font_nunito_bold.render(res_text, True, white)
            screen.blit(res_surf, res_surf.get_rect(center=(640, 280)))
            
            score_text = font_fredoka_md.render(f"SKOR: {gs.score}", True, gold)
            screen.blit(score_text, score_text.get_rect(center=(640, 350)))
            
            replay_btn.draw(screen)
            menu_btn.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    asyncio.run(main())
