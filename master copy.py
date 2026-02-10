import pygame
import sys
import os

# --- EXPLICIT IMPORT (Krävs för PyInstaller) ---
import refraction
import prism
import droplet
import droplet2
import rainbow

# --- Constants ---
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (20, 25, 30)
ACCENT_COLOR = (50, 150, 200)
TEXT_COLOR = (240, 240, 240)

# Mappa modulnamn till faktiska moduler
MODULE_MAP = {
    "refraction": refraction,
    "prism": prism,
    "droplet": droplet,
    "droplet2": droplet2,
    "rainbow": rainbow
}

class MenuButton:
    def __init__(self, x, y, w, h, text, icon_name, module_name):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.icon_name = icon_name
        self.module_name = module_name
        self.hover = False

    def draw(self, surface, font, scale=1.0):
        # Skala position och storlek
        s_rect = pygame.Rect(
            self.rect.x * scale, 
            self.rect.y * scale, 
            self.rect.width * scale, 
            self.rect.height * scale
        )
        
        color = (60, 70, 80) if not self.hover else (80, 100, 120)
        border_col = (100, 100, 100) if not self.hover else ACCENT_COLOR
        
        # Rita knappkropp
        pygame.draw.rect(surface, (10, 10, 15), s_rect.move(4, 4), border_radius=int(10*scale))
        pygame.draw.rect(surface, color, s_rect, border_radius=int(10*scale))
        pygame.draw.rect(surface, border_col, s_rect, max(1, int(2*scale)), border_radius=int(10*scale))
        
        # Ikon-center
        cx, cy = s_rect.centerx, s_rect.centery - int(15 * scale)
        isize = scale  # Skalfaktor för ritkommandon
        
        # --- RITA IKONER ---
        if self.icon_name == "refraction":
            # Yta (horisontell linje)
            y_level = cy + 5 * isize
            pygame.draw.line(surface, (150, 150, 150), (cx - 20*isize, y_level), (cx + 20*isize, y_level), max(1, int(2*isize)))
            # Inkommande stråle
            pygame.draw.line(surface, (255, 255, 100), (cx - 15*isize, y_level - 20*isize), (cx, y_level), max(1, int(3*isize)))
            # Bruten stråle
            pygame.draw.line(surface, (255, 255, 100), (cx, y_level), (cx + 10*isize, y_level + 20*isize), max(1, int(3*isize)))
            
        elif self.icon_name == "prism":
            # Triangel
            pts = [
                (cx, cy - 20*isize),
                (cx - 20*isize, cy + 15*isize),
                (cx + 20*isize, cy + 15*isize)
            ]
            pygame.draw.polygon(surface, (200, 200, 200), pts, max(1, int(2*isize)))
            # Stråle genom prisma
            pygame.draw.line(surface, (255, 255, 255), (cx - 25*isize, cy), (cx - 10*isize, cy + 5*isize), max(1, int(2*isize))) # In
            pygame.draw.line(surface, (255, 255, 255), (cx - 10*isize, cy + 5*isize), (cx + 10*isize, cy + 5*isize), max(1, int(2*isize))) # Genom
            pygame.draw.line(surface, (255, 100, 100), (cx + 10*isize, cy + 5*isize), (cx + 25*isize, cy + 15*isize), max(1, int(2*isize))) # Ut (Röd)
            
        elif self.icon_name == "ray_drop":
            # Cirkelkontur
            rad = int(18 * isize)
            pygame.draw.circle(surface, (150, 200, 255), (cx, cy), rad, max(1, int(2*isize)))
            # Strålgång (intern reflektion)
            p1 = (cx - rad, cy - 5*isize)
            p2 = (cx + rad*0.9, cy)
            p3 = (cx - rad*0.6, cy + rad*0.7)
            pygame.draw.lines(surface, (255, 255, 100), False, [p1, p2, p3], max(1, int(2*isize)))

        elif self.icon_name == "real_drop":
            # Fylld droppform (Triangel + Cirkel)
            color_drop = (50, 100, 200)
            rad = int(12 * isize)
            circle_center = (cx, cy + 5*isize)
            # Triangeltopp
            top_pt = (cx, cy - 20*isize)
            # Tangentpunkter på cirkeln (approximativt)
            t1 = (cx - rad*0.8, circle_center[1] - rad*0.5)
            t2 = (cx + rad*0.8, circle_center[1] - rad*0.5)
            
            pygame.draw.polygon(surface, color_drop, [top_pt, t2, t1])
            pygame.draw.circle(surface, color_drop, circle_center, rad)
            # Glans (highlight)
            pygame.draw.circle(surface, (200, 230, 255), (cx - 4*isize, cy - 2*isize), int(3*isize))

        elif self.icon_name == "rainbow":
            # Bågar
            rect1 = (cx - 20*isize, cy - 10*isize, 40*isize, 40*isize)
            rect2 = (cx - 15*isize, cy - 5*isize, 30*isize, 30*isize)
            rect3 = (cx - 10*isize, cy, 20*isize, 20*isize)
            pygame.draw.arc(surface, (255, 100, 100), rect1, 0, 3.14, max(1, int(3*isize)))
            pygame.draw.arc(surface, (100, 255, 100), rect2, 0, 3.14, max(1, int(3*isize)))
            pygame.draw.arc(surface, (100, 100, 255), rect3, 0, 3.14, max(1, int(3*isize)))

        # Text
        txt_surf = font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt_surf, (s_rect.centerx - txt_surf.get_width()//2, s_rect.centery + int(20*scale)))
        
        return s_rect

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Fysiksimulator: Regnbåge")
    clock = pygame.time.Clock()
    
    # Bas-dimensioner
    base_w, base_h = 1000, 700
    
    cols = 3
    btn_w, btn_h = 200, 150
    gap = 40
    start_y = 200
    
    # Uppdaterade ikoner
    buttons = [
        MenuButton(0, 0, btn_w, btn_h, "Brytning", "refraction", "refraction"),
        MenuButton(0, 0, btn_w, btn_h, "Prisma", "prism", "prism"),
        MenuButton(0, 0, btn_w, btn_h, "Strålgång", "ray_drop", "droplet"),
        MenuButton(0, 0, btn_w, btn_h, "Regndroppe", "real_drop", "droplet2"),
        MenuButton(0, 0, btn_w, btn_h, "Regnbåge", "rainbow", "rainbow"),
    ]

    # Layout beräkning
    num_btns = len(buttons)
    grid_cols = min(cols, num_btns)
    total_w = grid_cols * btn_w + (grid_cols - 1) * gap
    start_x = (base_w - total_w) // 2
    
    for i, btn in enumerate(buttons):
        row = i // cols
        col = i % cols
        btn.rect.x = start_x + col * (btn_w + gap)
        btn.rect.y = start_y + row * (btn_h + gap)

    running = True
    while running:
        screen.fill(BG_COLOR)
        
        curr_w, curr_h = screen.get_width(), screen.get_height()
        scale = min(curr_w / base_w, curr_h / base_h)
        
        title_font = pygame.font.SysFont("Arial", int(40 * scale), bold=True)
        btn_font = pygame.font.SysFont("Arial", int(20 * scale))
        
        title = title_font.render("Fysiksimulator: Regnbåge", True, ACCENT_COLOR)
        screen.blit(title, (curr_w//2 - title.get_width()//2, int(80 * scale)))
        
        subtitle = btn_font.render("(c) 2025 Martin Magnusson, martin.magnusson@fysik.lu.se", True, (150, 160, 170))
        screen.blit(subtitle, (curr_w//2 - subtitle.get_width()//2, int(130 * scale)))

        mx, my = pygame.mouse.get_pos()
        click_processed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_processed = True

        for btn in buttons:
            s_rect = btn.draw(screen, btn_font, scale)
            
            is_hover = s_rect.collidepoint((mx, my))
            btn.hover = is_hover
            
            if click_processed and is_hover:
                try:
                    module = MODULE_MAP.get(btn.module_name)
                    if module and hasattr(module, 'main'):
                        module.main(screen)
                        pygame.display.set_caption("Fysiksimulator: Regnbåge")
                    else:
                        print(f"Modul {btn.module_name} saknas.")
                except Exception as e:
                    print(f"Fel: {e}")

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()