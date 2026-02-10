import pygame
import sys
import importlib

# Importera simuleringarna
# OBS: Se till att filerna (refraction.py etc.) ligger i samma mapp
try:
    import refraction
    import prism
    import droplet
    import droplet2
    import rainbow
except ImportError as e:
    print(f"Kunde inte importera en modul: {e}")
    print("Se till att alla filer (refraction.py, prism.py, etc.) ligger i samma mapp.")

# --- Constants ---
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (20, 25, 30)
ACCENT_COLOR = (50, 150, 200)
TEXT_COLOR = (240, 240, 240)

class MenuButton:
    def __init__(self, x, y, w, h, text, icon_name, module_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon_name = icon_name
        self.module_name = module_name
        self.hover = False

    def draw(self, surface, font):
        color = (60, 70, 80) if not self.hover else (80, 100, 120)
        border_col = (100, 100, 100) if not self.hover else ACCENT_COLOR
        
        # Shadow
        pygame.draw.rect(surface, (10, 10, 15), self.rect.move(4, 4), border_radius=10)
        # Body
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=10)
        
        # Icon (Simple shapes for now)
        cx, cy = self.rect.centerx, self.rect.centery - 15
        if self.icon_name == "wave":
            pygame.draw.arc(surface, TEXT_COLOR, (cx-20, cy-10, 40, 40), 0, 3.14, 2)
            pygame.draw.arc(surface, TEXT_COLOR, (cx-20, cy-20, 40, 40), 0, 3.14, 2)
        elif self.icon_name == "prism":
            pygame.draw.polygon(surface, TEXT_COLOR, [(cx, cy-15), (cx-15, cy+10), (cx+15, cy+10)], 2)
        elif self.icon_name == "drop":
            pygame.draw.circle(surface, TEXT_COLOR, (cx, cy+5), 10, 2)
            pygame.draw.line(surface, TEXT_COLOR, (cx-7, cy), (cx, cy-12), 2)
            pygame.draw.line(surface, TEXT_COLOR, (cx+7, cy), (cx, cy-12), 2)
        elif self.icon_name == "rainbow":
            pygame.draw.arc(surface, (255, 100, 100), (cx-20, cy-10, 40, 40), 0, 3.14, 3)
            pygame.draw.arc(surface, (100, 255, 100), (cx-15, cy-5, 30, 30), 0, 3.14, 3)
            pygame.draw.arc(surface, (100, 100, 255), (cx-10, cy, 20, 20), 0, 3.14, 3)

        # Text
        txt_surf = font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.centery + 15))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Fysiksimulator: Ljus & Optik")
    clock = pygame.time.Clock()
    
    title_font = pygame.font.SysFont("Arial", 40, bold=True)
    btn_font = pygame.font.SysFont("Arial", 20)
    
    # Layout
    cols = 3
    btn_w, btn_h = 200, 150
    gap = 40
    start_x = (WIDTH - (cols * btn_w + (cols-1) * gap)) // 2
    start_y = 200
    
    buttons = [
        MenuButton(0, 0, btn_w, btn_h, "Brytning (Refraction)", "wave", "refraction"),
        MenuButton(0, 0, btn_w, btn_h, "Prisma", "prism", "prism"),
        MenuButton(0, 0, btn_w, btn_h, "Regndroppe (Enkel)", "drop", "droplet"),
        MenuButton(0, 0, btn_w, btn_h, "Regndroppe (Avancerad)", "drop", "droplet2"),
        MenuButton(0, 0, btn_w, btn_h, "Regnbåge (Monte Carlo)", "rainbow", "rainbow"),
    ]

    def update_layout(w, h):
        start_x = (w - (min(cols, len(buttons)) * btn_w + (min(cols, len(buttons))-1) * gap)) // 2
        for i, btn in enumerate(buttons):
            row = i // cols
            col = i % cols
            btn.rect.x = start_x + col * (btn_w + gap)
            btn.rect.y = start_y + row * (btn_h + gap)

    update_layout(WIDTH, HEIGHT)

    running = True
    while running:
        screen.fill(BG_COLOR)
        
        # Header
        title = title_font.render("Fysiksimulator: Ljusfenomen", True, ACCENT_COLOR)
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 80))
        
        subtitle = btn_font.render("Välj en simulering att starta", True, (150, 160, 170))
        screen.blit(subtitle, (screen.get_width()//2 - subtitle.get_width()//2, 130))

        # Events
        mx, my = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                update_layout(event.w, event.h)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for btn in buttons:
                        if btn.rect.collidepoint((mx, my)):
                            # Starta modulen
                            try:
                                module = sys.modules[btn.module_name]
                                # Vi antar att varje modul har en main() som vi kan kalla
                                # För att komma tillbaka måste vi modifiera modulerna så att de inte kör sys.exit()
                                # utan bara returnerar. 
                                # Hack: Vi kör modulen, och när den stängs kommer vi tillbaka hit (om sys.exit är borta).
                                if hasattr(module, 'main'):
                                    module.main()
                                    # När vi kommer tillbaka, återställ skärmen för menyn
                                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                                    pygame.display.set_caption("Fysiksimulator: Ljus & Optik")
                            except Exception as e:
                                print(f"Fel vid start av {btn.module_name}: {e}")

        # Draw Buttons
        for btn in buttons:
            btn.hover = btn.rect.collidepoint((mx, my))
            btn.draw(screen, btn_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()