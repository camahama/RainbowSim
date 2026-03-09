import pygame
import math
import sys

# --- Constants ---
# Initial window size
INIT_WIDTH, INIT_HEIGHT = 1200, 700
# Internal simulation resolution (kept fixed for performance consistency)
GRID_WIDTH, GRID_HEIGHT = 400, 233 

# Colors
COLOR_BG = (0, 0, 0)
COLOR_UI_BG = (30, 30, 30)
COLOR_GLASS = (20, 20, 50) # Tydligare blåton för glaset

class WaveRenderer:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        
        # Inställningar
        self.refractive_index = 1.0
        self.time = 0.0
        
        # Vågparametrar
        self.base_wavelength = 30.0 # Pixlar i rutnätet
        self.frequency = 0.1
        self.beam_width = 50.0 # Halva bredden av strålen
        
        # Gränsyta: x = ky + m
        # Vi definierar en punkt och en normal
        self.boundary_slope = 0.4
        self.center_x = self.width // 2 - 20
        self.center_y = self.height // 2
        
        # Förberäkna geometriska vektorer
        # Linjevektor (tangent)
        # x = 0.4y -> dy=1, dx=0.4. Längd = sqrt(1 + 0.16) ~= 1.077
        l_len = math.hypot(0.4, 1.0)
        self.tangent = (0.4 / l_len, 1.0 / l_len)
        
        # Normalvektor (pekar in i glaset, åt höger)
        # Roterad -90 deg från tangenten (som pekar neråt) -> (1, -0.4)
        self.normal = (1.0 / l_len, -0.4 / l_len)
        
        # Pivot-punkt på linjen (för fasmätning)
        self.pivot = (self.center_x, self.center_y)

    def set_refractive_index(self, n):
        self.refractive_index = n

    def update(self):
        self.time += self.frequency

    def render(self, surface):
        pixels = pygame.PixelArray(surface)
        w = self.width
        h = self.height
        
        # Hämta värden till lokala variabler för snabb loop
        n2 = self.refractive_index
        t = self.time
        k0 = (2 * math.pi) / self.base_wavelength
        
        # Vågvektor i Luft (n=1)
        # Går rakt åt höger (1, 0)
        k1_x = k0
        k1_y = 0.0
        
        # Vågvektor i Glas (n=n2)
        # Beräkna riktning med Snells lag (vektorform)
        # k_incident dot tangent = k_refracted dot tangent (bevarande av tangentialmoment)
        
        # Incident k: (k0, 0)
        # Tangent t: self.tangent
        # k_tangential = k0 * t.x + 0 * t.y
        kt = k0 * self.tangent[0]
        
        # Magnitud av k i glas: k_glass = n * k0
        k_glass_mag = n2 * k0
        
        # Normal-komponent: kn = sqrt(k_mag^2 - kt^2)
        # Om k_mag < kt har vi totalreflektion (TIR), men här går vi från lågt till högt index, så det sker ej.
        kn_sq = k_glass_mag**2 - kt**2
        if kn_sq < 0: kn_sq = 0 # Safety
        kn = math.sqrt(kn_sq)
        
        # Vågvektor i glas = kt * tangent + kn * normal
        k2_x = kt * self.tangent[0] + kn * self.normal[0]
        k2_y = kt * self.tangent[1] + kn * self.normal[1]
        
        # Strål-riktning (normaliserad k2)
        k2_len = math.hypot(k2_x, k2_y)
        dir2_x = k2_x / k2_len
        dir2_y = k2_y / k2_len
        
        # Gränslinje-konstant för snabb check: x - 0.4y = offset
        # x - slope * (y - cy) = cx
        slope = self.boundary_slope
        cx, cy = self.center_x, self.center_y
        
        pivot_x, pivot_y = self.pivot
        
        # Loopa över alla pixlar
        for y in range(h):
            # Optimering: Förberäkna y-termer
            y_rel = y - cy
            boundary_x_at_y = slope * y_rel + cx
            
            dy = y - pivot_y
            
            for x in range(w):
                dx = x - pivot_x
                
                # Är vi i luft eller glas?
                if x < boundary_x_at_y:
                    # --- LUFT ---
                    # Fas: k1 dot r - w*t
                    phase = k1_x * dx + k1_y * dy - t
                    
                    # Strålens bredd (Beam Width)
                    # Avstånd från mittenlinjen (y=cy)
                    dist_from_beam = abs(y - cy)
                    
                    bg_col = COLOR_BG
                else:
                    # --- GLAS ---
                    # Fas: k2 dot r - w*t
                    # Eftersom vi mäter r från pivoten på gränslinjen där faserna möts,
                    # blir övergången automatiskt kontinuerlig.
                    phase = k2_x * dx + k2_y * dy - t
                    
                    # Strålens bredd i glaset
                    # Vi måste projicera punkten på strålens centrumlinje
                    # Centrumlinjen går genom pivot med riktning dir2
                    # Avstånd d = |det(dir, pos)| = |dx*dir.y - dy*dir.x|
                    dist_from_beam = abs(dx * dir2_y - dy * dir2_x)
                    
                    bg_col = COLOR_GLASS

                # Beräkna vågintensitet
                # Sinusvåg mappad till 0..1
                # Använd cosinus för att få en topp vid fas=0 om man vill, eller sin.
                val = math.sin(phase)
                
                # Visualisering: Bara positiva toppar
                wave_intensity = max(0.0, val)
                
                # Applicera mask för strålens bredd (mjuk kant)
                # Smoothstep eller linear fade
                if dist_from_beam > self.beam_width:
                    fade = max(0.0, 1.0 - (dist_from_beam - self.beam_width) / 10.0)
                    wave_intensity *= fade
                
                if wave_intensity > 0.05:
                    # Grönt ljus (0, 255, 100)
                    # Additiv blandning med bakgrund
                    w_int = int(wave_intensity * 255)
                    
                    r = min(255, bg_col[0] + 0)
                    g = min(255, bg_col[1] + w_int)
                    b = min(255, bg_col[2] + w_int // 3)
                    pixels[x, y] = (r, g, b)
                else:
                    pixels[x, y] = bg_col
                    
        pixels.close()

def main():
    pygame.init()
    # Start with initial size but allow resizing
    win_w, win_h = INIT_WIDTH, INIT_HEIGHT
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Wave Refraction: Illustration")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    renderer = WaveRenderer()
    
    # Render-yta (fast upplösning)
    sim_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    
    # Helper to position slider based on current window size
    def get_slider_rect(w, h):
        return pygame.Rect(200, h - 60, max(100, w - 400), 10)

    slider_rect = get_slider_rect(win_w, win_h)
    dragging = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # Handle window resizing
                win_w, win_h = event.w, event.h
                # In newer pygame versions set_mode is not strictly needed on resize event 
                # for OpenGL context, but for software rendering it might be safe to ensure surface matches.
                # Usually event.w/h is enough to update logic.
                slider_rect = get_slider_rect(win_w, win_h)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if slider_rect.collidepoint(mx, my) or abs(my - slider_rect.centery) < 20:
                    if slider_rect.left <= mx <= slider_rect.right:
                        dragging = True
                        # Update on click immediately
                        mx = max(slider_rect.left, min(slider_rect.right, mx))
                        ratio = (mx - slider_rect.left) / slider_rect.width
                        new_n = 1.0 + ratio * 2.0
                        renderer.set_refractive_index(new_n)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mx = event.pos[0]
                    mx = max(slider_rect.left, min(slider_rect.right, mx))
                    ratio = (mx - slider_rect.left) / slider_rect.width
                    # Index range: 1.0 to 3.0
                    new_n = 1.0 + ratio * 2.0
                    renderer.set_refractive_index(new_n)

        # Update
        renderer.update()
        
        # Render
        renderer.render(sim_surface)
        
        # Scale up to window size (minus UI area)
        ui_height = 100
        render_h = max(1, win_h - ui_height)
        scaled_surf = pygame.transform.scale(sim_surface, (win_w, render_h))
        
        screen.fill(COLOR_BG)
        screen.blit(scaled_surf, (0, 0))
        
        # UI
        pygame.draw.rect(screen, COLOR_UI_BG, (0, win_h - ui_height, win_w, ui_height))
        
        # Slider
        pygame.draw.rect(screen, (100, 100, 100), slider_rect, border_radius=5)
        
        ratio = (renderer.refractive_index - 1.0) / 2.0
        knob_x = slider_rect.x + int(ratio * slider_rect.width)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 12)
        
        # Labels
        lbl_n = font.render(f"Brytningsindex (n): {renderer.refractive_index:.2f}", True, (255, 255, 255))
        screen.blit(lbl_n, (win_w//2 - lbl_n.get_width()//2, slider_rect.y - 30))
        
        screen.blit(font.render("1.0 (Luft)", True, (150,150,150)), (slider_rect.x, slider_rect.bottom + 5))
        screen.blit(font.render("3.0 (Segt)", True, (150,150,150)), (slider_rect.right - 60, slider_rect.bottom + 5))
        
        # Info
        info_lines = [
            "Huygens Princip: Vågorna saktar ner i glaset.",
            "För att vågfronterna ska hänga ihop måste riktningen ändras.",
            "Högre index -> Långsammare våg -> Kortare våglängd -> Mer brytning."
        ]
        for i, line in enumerate(info_lines):
            t = font.render(line, True, (150, 200, 150))
            screen.blit(t, (win_w//2 - t.get_width()//2, 10 + i*25))

        pygame.display.flip()
        # Lås till 60 FPS men tillåt drop om beräkningen är tung (bör vara snabb nu)
        clock.tick(60)

    return

if __name__ == "__main__":
    main()