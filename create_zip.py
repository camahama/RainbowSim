import zipfile
import os

# Definitioner av filinnehåll (kopierat från våra tidigare steg)

# 1. master.py
code_master = r"""import pygame
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

    def draw(self, surface, font):
        color = (60, 70, 80) if not self.hover else (80, 100, 120)
        border_col = (100, 100, 100) if not self.hover else ACCENT_COLOR
        
        pygame.draw.rect(surface, (10, 10, 15), self.rect.move(4, 4), border_radius=10)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=10)
        
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

        txt_surf = font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt_surf, (self.rect.centerx - txt_surf.get_width()//2, self.rect.centery + 15))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Fysiksimulator: Ljus & Optik")
    clock = pygame.time.Clock()
    
    title_font = pygame.font.SysFont("Arial", 40, bold=True)
    btn_font = pygame.font.SysFont("Arial", 20)
    
    cols = 3
    btn_w, btn_h = 200, 150
    gap = 40
    start_y = 200
    
    buttons = [
        MenuButton(0, 0, btn_w, btn_h, "Brytning (Refraction)", "wave", "refraction"),
        MenuButton(0, 0, btn_w, btn_h, "Prisma", "prism", "prism"),
        MenuButton(0, 0, btn_w, btn_h, "Regndroppe (Enkel)", "drop", "droplet"),
        MenuButton(0, 0, btn_w, btn_h, "Regndroppe (Avancerad)", "drop", "droplet2"),
        MenuButton(0, 0, btn_w, btn_h, "Regnbåge (Monte Carlo)", "rainbow", "rainbow"),
    ]

    def update_layout(w, h):
        num_btns = len(buttons)
        grid_cols = min(cols, num_btns)
        total_w = grid_cols * btn_w + (grid_cols - 1) * gap
        start_x = (w - total_w) // 2
        
        for i, btn in enumerate(buttons):
            row = i // cols
            col = i % cols
            btn.rect.x = start_x + col * (btn_w + gap)
            btn.rect.y = start_y + row * (btn_h + gap)

    update_layout(screen.get_width(), screen.get_height())

    running = True
    while running:
        screen.fill(BG_COLOR)
        
        title = title_font.render("Fysiksimulator: Ljusfenomen", True, ACCENT_COLOR)
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 80))
        
        subtitle = btn_font.render("Välj en simulering att starta", True, (150, 160, 170))
        screen.blit(subtitle, (screen.get_width()//2 - subtitle.get_width()//2, 130))

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
                            try:
                                module = MODULE_MAP.get(btn.module_name)
                                if module and hasattr(module, 'main'):
                                    module.main(screen)
                                    pygame.display.set_caption("Fysiksimulator: Ljus & Optik")
                                    update_layout(screen.get_width(), screen.get_height())
                                else:
                                    print(f"Modul {btn.module_name} hittades inte eller saknar main().")
                                    
                            except Exception as e:
                                print(f"Fel vid start av {btn.module_name}: {e}")
                                import traceback
                                traceback.print_exc()

        for btn in buttons:
            btn.hover = btn.rect.collidepoint((mx, my))
            btn.draw(screen, btn_font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
"""

# 2. refraction.py
code_refraction = r"""import pygame
import math
import sys

# --- Constants ---
GRID_WIDTH, GRID_HEIGHT = 400, 233 

# Colors
COLOR_BG = (0, 0, 0)
COLOR_UI_BG = (30, 30, 30)
COLOR_GLASS = (20, 20, 50) 

class WaveRenderer:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.refractive_index = 1.0
        self.time = 0.0
        self.base_wavelength = 30.0
        self.frequency = 0.1
        self.beam_width = 50.0 
        self.boundary_slope = 0.4
        self.center_x = self.width // 2 - 20
        self.center_y = self.height // 2
        l_len = math.hypot(0.4, 1.0)
        self.tangent = (0.4 / l_len, 1.0 / l_len)
        self.normal = (1.0 / l_len, -0.4 / l_len)
        self.pivot = (self.center_x, self.center_y)

    def set_refractive_index(self, n):
        self.refractive_index = n

    def update(self):
        self.time += self.frequency

    def render(self, surface):
        pixels = pygame.PixelArray(surface)
        w = self.width
        h = self.height
        n2 = self.refractive_index
        t = self.time
        k0 = (2 * math.pi) / self.base_wavelength
        
        k1_x, k1_y = k0, 0.0
        kt = k0 * self.tangent[0]
        k_glass_mag = n2 * k0
        kn_sq = k_glass_mag**2 - kt**2
        if kn_sq < 0: kn_sq = 0
        kn = math.sqrt(kn_sq)
        
        k2_x = kt * self.tangent[0] + kn * self.normal[0]
        k2_y = kt * self.tangent[1] + kn * self.normal[1]
        
        k2_len = math.hypot(k2_x, k2_y)
        dir2_x = k2_x / k2_len
        dir2_y = k2_y / k2_len
        
        slope = self.boundary_slope
        cx, cy = self.center_x, self.center_y
        pivot_x, pivot_y = self.pivot
        
        for y in range(h):
            y_rel = y - cy
            boundary_x_at_y = slope * y_rel + cx
            dy = y - pivot_y
            
            for x in range(w):
                dx = x - pivot_x
                if x < boundary_x_at_y:
                    phase = k1_x * dx + k1_y * dy - t
                    dist_from_beam = abs(y - cy)
                    bg_col = COLOR_BG
                else:
                    phase = k2_x * dx + k2_y * dy - t
                    dist_from_beam = abs(dx * dir2_y - dy * dir2_x)
                    bg_col = COLOR_GLASS

                val = math.sin(phase)
                wave_intensity = max(0.0, val)
                
                if dist_from_beam > self.beam_width:
                    fade = max(0.0, 1.0 - (dist_from_beam - self.beam_width) / 10.0)
                    wave_intensity *= fade
                
                if wave_intensity > 0.05:
                    w_int = int(wave_intensity * 255)
                    r = min(255, bg_col[0] + 0)
                    g = min(255, bg_col[1] + w_int)
                    b = min(255, bg_col[2] + w_int // 3)
                    pixels[x, y] = (r, g, b)
                else:
                    pixels[x, y] = bg_col
        pixels.close()

def main(screen=None):
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1200, 700), pygame.RESIZABLE)
        
    pygame.display.set_caption("Vågbrytning: Simulering")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    renderer = WaveRenderer()
    sim_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    
    back_btn_rect = pygame.Rect(10, 10, 100, 40)

    def get_slider_rect(w, h):
        return pygame.Rect(200, h - 60, max(100, w - 400), 10)

    win_w, win_h = screen.get_width(), screen.get_height()
    slider_rect = get_slider_rect(win_w, win_h)
    dragging = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
                slider_rect = get_slider_rect(win_w, win_h)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if back_btn_rect.collidepoint((mx, my)):
                    running = False
                
                if slider_rect.collidepoint(mx, my) or abs(my - slider_rect.centery) < 20:
                    if slider_rect.left <= mx <= slider_rect.right:
                        dragging = True
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
                    new_n = 1.0 + ratio * 2.0
                    renderer.set_refractive_index(new_n)

        renderer.update()
        renderer.render(sim_surface)
        
        ui_height = 100
        render_h = max(1, win_h - ui_height)
        scaled_surf = pygame.transform.scale(sim_surface, (win_w, render_h))
        
        screen.fill(COLOR_BG)
        screen.blit(scaled_surf, (0, 0))
        
        pygame.draw.rect(screen, COLOR_UI_BG, (0, win_h - ui_height, win_w, ui_height))
        
        pygame.draw.rect(screen, (100, 100, 100), slider_rect, border_radius=5)
        ratio = (renderer.refractive_index - 1.0) / 2.0
        knob_x = slider_rect.x + int(ratio * slider_rect.width)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 12)
        
        lbl_n = font.render(f"Brytningsindex (n): {renderer.refractive_index:.2f}", True, (255, 255, 255))
        screen.blit(lbl_n, (win_w//2 - lbl_n.get_width()//2, slider_rect.y - 30))
        
        screen.blit(font.render("1.0 (Luft)", True, (150,150,150)), (slider_rect.x, slider_rect.bottom + 5))
        screen.blit(font.render("3.0 (Segt)", True, (150,150,150)), (slider_rect.right - 60, slider_rect.bottom + 5))
        
        pygame.draw.rect(screen, (150, 50, 50), back_btn_rect, border_radius=5)
        back_txt = font.render("Meny", True, (255, 255, 255))
        screen.blit(back_txt, (back_btn_rect.centerx - back_txt.get_width()//2, back_btn_rect.centery - back_txt.get_height()//2))

        pygame.display.flip()
        clock.tick(60)

    return

if __name__ == "__main__":
    main()
"""

# 3. prism.py
code_prism = r"""import pygame
import sys
import math

# --- Constants ---
INTERNAL_W, INTERNAL_H = 1200, 600
BACKGROUND_COLOR = (10, 10, 10)
SPEED_AIR = 4.0
STAGGER_SPACING = 35.0

RAINBOW_DATA = [
    {"name": "Röd",    "rgb": (255, 0, 0),     "n": 1.25}, 
    {"name": "Orange", "rgb": (255, 127, 0),   "n": 1.29},
    {"name": "Gul",    "rgb": (255, 255, 0),   "n": 1.33},
    {"name": "Grön",   "rgb": (0, 255, 0),     "n": 1.38},
    {"name": "Blå",    "rgb": (0, 0, 255),     "n": 1.42},
    {"name": "Indigo", "rgb": (75, 0, 130),    "n": 1.46},
    {"name": "Violett", "rgb": (148, 0, 211),   "n": 1.50}, 
]

BUTTON_COLOR = (50, 80, 50)
BUTTON_HOVER = (70, 100, 70)
BUTTON_ACTIVE = (100, 150, 100)
TEXT_WHITE = (255, 255, 255)

def vec_add(v1, v2): return (v1[0] + v2[0], v1[1] + v2[1])
def vec_sub(v1, v2): return (v1[0] - v2[0], v1[1] - v2[1])
def vec_mul(v, s):   return (v[0] * s, v[1] * s)
def vec_dot(v1, v2): return v1[0] * v2[0] + v1[1] * v2[1]
def vec_len(v):      return math.hypot(v[0], v[1])
def vec_norm(v):
    l = vec_len(v)
    return (v[0]/l, v[1]/l) if l > 0 else (0, 0)

def intersect_segment_line(p1, p2, v1, v2):
    d = (v2[1] - v1[1]) * (p2[0] - p1[0]) - (v2[0] - v1[0]) * (p2[1] - p1[1])
    if d == 0: return None
    ua = ((v2[0] - v1[0]) * (p1[1] - v1[1]) - (v2[1] - v1[1]) * (p1[0] - v1[0])) / d
    ub = ((p2[0] - p1[0]) * (p1[1] - v1[1]) - (p2[1] - p1[1]) * (p1[0] - v1[0])) / d
    if 0 <= ua <= 1 and 0 <= ub <= 1: return ua
    return None

def get_polygon_edges(verts):
    edges = []
    n = len(verts)
    for i in range(n):
        p1 = verts[i]
        p2 = verts[(i + 1) % n]
        edge_vec = vec_sub(p2, p1)
        normal = vec_norm((edge_vec[1], -edge_vec[0]))
        edges.append({'p1': p1, 'p2': p2, 'normal': normal})
    return edges

def calculate_rotated_rect_verts(center, width, height, angle_deg):
    angle_rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    hw, hh = width / 2, height / 2
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    verts = []
    for cx, cy in corners:
        verts.append((center[0] + cx * cos_a - cy * sin_a, center[1] + cx * sin_a + cy * cos_a))
    return verts

def calculate_polygon_verts(center, radius, rotation_deg, num_sides):
    verts = []
    angle_step = 360.0 / num_sides
    start_angle = 90 if num_sides == 3 else 45 
    for i in range(num_sides):
        angle = start_angle + i * angle_step - rotation_deg
        rad = math.radians(angle)
        verts.append((center[0] + radius * math.cos(rad), center[1] - radius * math.sin(rad)))
    return verts

class PhysicsWorld:
    def __init__(self):
        self.mode = None
        self.verts = []
        self.edges = []
        self.medium_active = False

    def set_mode(self, mode):
        self.mode = mode
        if mode == "block_straight":
            self.medium_active = True
            self.verts = calculate_rotated_rect_verts((600, 300), 500, 250, 0)
            self.edges = get_polygon_edges(self.verts)
        elif mode == "block_rotated":
            self.medium_active = True
            self.verts = calculate_rotated_rect_verts((600, 300), 250, 250, 20)
            self.edges = get_polygon_edges(self.verts)
        elif mode == "triangle":
            self.medium_active = True
            self.verts = calculate_polygon_verts((600, 300), 180, 0, 3)
            self.edges = get_polygon_edges(self.verts)
        elif mode == "air":
            self.medium_active = False
            self.verts = []
            self.edges = []

    def trace_ray(self, start_pos, velocity, current_n, target_n):
        move_vec = velocity
        dist_to_move = vec_len(move_vec)
        if dist_to_move == 0: return start_pos, velocity, None
        end_pos = vec_add(start_pos, move_vec)
        if not self.medium_active: return end_pos, velocity, None

        best_t, hit_edge = 2.0, None
        for edge in self.edges:
            t = intersect_segment_line(start_pos, end_pos, edge['p1'], edge['p2'])
            if t is not None and t < best_t:
                best_t = t
                hit_edge = edge
        
        if hit_edge and best_t <= 1.0:
            hit_pos = vec_add(start_pos, vec_mul(move_vec, best_t))
            incident = vec_norm(velocity)
            normal = hit_edge['normal']
            dot_prod = vec_dot(incident, normal)
            entering = dot_prod < 0
            
            if entering:
                n1, n2 = 1.0, target_n
                effective_normal = normal 
                new_inside_state = True
            else:
                n1, n2 = target_n, 1.0
                effective_normal = vec_mul(normal, -1) 
                new_inside_state = False
                
            eta = n1 / n2
            c1 = -vec_dot(incident, effective_normal)
            cs2_sq = 1 - eta**2 * (1 - c1**2)
            
            if cs2_sq < 0:
                speed = vec_len(velocity)
                refl_dir = vec_add(incident, vec_mul(effective_normal, 2 * c1))
                new_velocity = vec_mul(refl_dir, speed)
                new_inside_state = not entering 
                if not entering: new_inside_state = True 
            else:
                term = eta * c1 - math.sqrt(cs2_sq)
                refr_dir = vec_add(vec_mul(incident, eta), vec_mul(effective_normal, term))
                new_speed = SPEED_AIR / n2
                new_velocity = vec_mul(refr_dir, new_speed)
            
            return hit_pos, new_velocity, {'t': best_t, 'new_inside': new_inside_state}
        else:
            return end_pos, velocity, None

class Photon:
    def __init__(self, data, y_pos, start_x_offset):
        self.color = data["rgb"]
        self.n = data["n"]
        self.pos = (50.0 - start_x_offset, y_pos)
        self.vel = (SPEED_AIR, 0.0)
        self.inside = False 
        self.trail = []
        self.finished = False

    def update(self, world):
        if self.pos[0] > INTERNAL_W + 50:
            self.finished = True
            return
        remaining_t = 1.0 
        current_pos = self.pos
        current_vel = self.vel
        for _ in range(3): 
            step_vel = vec_mul(current_vel, remaining_t)
            new_pos, new_vel, hit = world.trace_ray(current_pos, step_vel, 1.0 if not self.inside else self.n, self.n)
            if hit:
                if new_pos[0] > -50: self.trail.append(new_pos)
                self.inside = hit['new_inside']
                current_vel = new_vel
                consumed = hit['t']
                remaining_t *= (1.0 - consumed)
                epsilon = 0.1
                current_pos = vec_add(new_pos, vec_mul(vec_norm(current_vel), epsilon))
                if remaining_t <= 0.001: break
            else:
                current_pos = new_pos
                if current_pos[0] > -50: self.trail.append(current_pos)
                break
        self.pos = current_pos
        self.vel = current_vel

    def draw(self, surface):
        if self.pos[0] < -20: return
        if len(self.trail) > 1:
            pygame.draw.lines(surface, self.color, False, self.trail, 6)
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), 10)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.pos[0]), int(self.pos[1])), 4)

def reset_simulation():
    photons = []
    center_y = 300
    for i, data in enumerate(reversed(RAINBOW_DATA)):
        offset = i * STAGGER_SPACING
        photons.append(Photon(data, center_y, offset))
    return photons

def main(screen=None):
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1200, 600), pygame.RESIZABLE)
        
    pygame.display.set_caption("Refraktion: Hastighetsloppet")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    canvas = pygame.Surface((INTERNAL_W, INTERNAL_H))
    world = PhysicsWorld()
    photons = []
    
    y_pos = 50
    w = 120
    h = 40
    gap = 10
    x = 50
    
    btn_air = pygame.Rect(x, y_pos, w, h); x += w + gap
    btn_straight = pygame.Rect(x, y_pos, w, h); x += w + gap
    btn_rotated = pygame.Rect(x, y_pos, w, h); x += w + gap
    btn_tri = pygame.Rect(x, y_pos, w, h); x += w + gap
    x += 20
    btn_clear = pygame.Rect(x, y_pos, w, h)
    btn_back = pygame.Rect(INTERNAL_W - 130, 20, 110, 40)
    
    sim_surf = pygame.Surface((INTERNAL_W, INTERNAL_H))
    p_surf = pygame.Surface((INTERNAL_W, INTERNAL_H))

    running = True
    win_w, win_h = screen.get_width(), screen.get_height()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    scale_x = INTERNAL_W / win_w
                    scale_y = INTERNAL_H / win_h
                    scaled_pos = (mx * scale_x, my * scale_y)
                    
                    if btn_back.collidepoint(scaled_pos):
                        running = False
                    elif btn_air.collidepoint(scaled_pos):
                        world.set_mode("air"); photons = reset_simulation()
                    elif btn_straight.collidepoint(scaled_pos):
                        world.set_mode("block_straight"); photons = reset_simulation()
                    elif btn_rotated.collidepoint(scaled_pos):
                        world.set_mode("block_rotated"); photons = reset_simulation()
                    elif btn_tri.collidepoint(scaled_pos):
                        world.set_mode("triangle"); photons = reset_simulation()
                    elif btn_clear.collidepoint(scaled_pos):
                        photons = []

        for p in photons: p.update(world)

        canvas.fill(BACKGROUND_COLOR)
        if world.medium_active:
            pygame.draw.polygon(canvas, (30, 40, 50), world.verts)
            pygame.draw.polygon(canvas, (100, 120, 150), world.verts, 2)
            name = "Okänd"
            if world.mode == "block_straight": name = "BLOCK (Rak)"
            elif world.mode == "block_rotated": name = "BLOCK (Roterad)"
            elif world.mode == "triangle": name = "PRISMA"
            label = font.render(name, True, (100, 120, 150))
            canvas.blit(label, (600 - label.get_width()//2, 150))

        if photons:
            sim_surf.fill((0, 0, 0))
            for p in photons:
                p_surf.fill((0, 0, 0))
                p.draw(p_surf)
                sim_surf.blit(p_surf, (0, 0), special_flags=pygame.BLEND_ADD)
            canvas.blit(sim_surf, (0, 0), special_flags=pygame.BLEND_ADD)

        buttons = [
            (btn_air, "Inget medium", world.mode == "air"),
            (btn_straight, "Rak", world.mode == "block_straight"),
            (btn_rotated, "Roterad", world.mode == "block_rotated"),
            (btn_tri, "Prisma", world.mode == "triangle"),
            (btn_clear, "Rensa", False),
            (btn_back, "Meny", False)
        ]
        
        raw_mx, raw_my = pygame.mouse.get_pos()
        scale_x = INTERNAL_W / win_w
        scale_y = INTERNAL_H / win_h
        scaled_mouse = (raw_mx * scale_x, raw_my * scale_y)
        
        for rect, text, active in buttons:
            col = BUTTON_ACTIVE if active else BUTTON_COLOR
            if rect.collidepoint(scaled_mouse): col = BUTTON_HOVER
            if active: col = BUTTON_ACTIVE
            if rect == btn_back: col = (150, 50, 50)
            
            pygame.draw.rect(canvas, col, rect, border_radius=5)
            pygame.draw.rect(canvas, TEXT_WHITE, rect, 2, border_radius=5)
            t_surf = font.render(text, True, TEXT_WHITE)
            canvas.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.centery - t_surf.get_height()//2))

        msg = ""
        if world.mode is None: msg = "Välj ett läge för att starta simuleringen."
        elif world.mode == "air": msg = "Vakuum: Alla färger färdas med samma hastighet (c)."
        elif world.mode == "block_straight": msg = "Vinkelrätt infall: Ljuset saktar ner, men riktningen ändras inte. Rött är snabbast."
        elif world.mode == "block_rotated": msg = "Brytning: Ljuset böjs av och saktar ner. Rött är snabbast."
        elif world.mode == "triangle": msg = "Dispersion: Formen förstärker hastighetsskillnaden och separerar färgerna."
        msg_surf = font.render(msg, True, (150, 150, 150))
        canvas.blit(msg_surf, (INTERNAL_W//2 - msg_surf.get_width()//2, INTERNAL_H - 50))

        scaled_surf = pygame.transform.scale(canvas, (win_w, win_h))
        screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    return

if __name__ == "__main__":
    main()
"""

# 4. droplet.py
code_droplet = r"""import pygame
import math
import sys

# --- Constants ---
INTERNAL_WIDTH, INTERNAL_HEIGHT = 1200, 800
BACKGROUND_COLOR = (20, 20, 20)
UI_WIDTH = 250

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BUTTON_COLOR = (50, 50, 80)
BUTTON_HOVER_COLOR = (70, 70, 100)
BUTTON_ACTIVE_COLOR = (80, 100, 80)
DROP_FILL_COLOR = (20, 20, 60)   
DROP_OUTLINE_COLOR = (200, 200, 220) 

RAINBOW_DATA = [
    {"name": "Red",    "rgb": (255, 0, 0),     "n": 1.331},
    {"name": "Orange", "rgb": (255, 127, 0),   "n": 1.333},
    {"name": "Yellow", "rgb": (255, 255, 0),   "n": 1.335},
    {"name": "Green",  "rgb": (0, 255, 0),     "n": 1.338},
    {"name": "Blue",   "rgb": (0, 0, 255),     "n": 1.343},
    {"name": "Indigo", "rgb": (75, 0, 130),    "n": 1.345},
    {"name": "Violet", "rgb": (148, 0, 211),   "n": 1.348},
]

class SimulationState:
    def __init__(self):
        self.visible_flags = [False] * 7
        self.focused_index = 0
        self.impact_primary = [100.0] * 7 
        self.impact_secondary = [100.0] * 7
        self.is_dragging = False
        self.show_primary = True
        self.show_secondary = False

def get_layout(current_w, current_h):
    ui_x = current_w - UI_WIDTH
    drop_center = (ui_x // 2, current_h // 2)
    max_radius_w = (ui_x - 50) // 6
    max_radius_h = current_h // 7.5
    drop_radius = int(min(max_radius_w, max_radius_h))
    return ui_x, drop_center, drop_radius

def calculate_ray_path_from_bottom(x_offset, n_color, drop_center, drop_radius, screen_height, num_reflections):
    points = []
    start_x = drop_center[0] + x_offset
    start_y = screen_height
    points.append((start_x, start_y))
    if abs(x_offset) > drop_radius:
        points.append((start_x, 0))
        return points, None 
    dy_entry = math.sqrt(drop_radius**2 - x_offset**2)
    entry_x = start_x
    entry_y = drop_center[1] + dy_entry
    points.append((entry_x, entry_y))
    try:
        alpha = math.asin(x_offset / drop_radius)
    except ValueError:
        return points, None
    sin_beta = (1.0003 / n_color) * math.sin(alpha)
    if abs(sin_beta) > 1: return points, None 
    beta = math.asin(sin_beta)
    theta_current = math.atan2(dy_entry, x_offset)
    rotation_step = -(math.pi - 2 * beta)
    for _ in range(num_reflections):
        theta_current += rotation_step
        ref_x = drop_center[0] + drop_radius * math.cos(theta_current)
        ref_y = drop_center[1] + drop_radius * math.sin(theta_current)
        points.append((ref_x, ref_y))
    theta_current += rotation_step
    exit_x = drop_center[0] + drop_radius * math.cos(theta_current)
    exit_y = drop_center[1] + drop_radius * math.sin(theta_current)
    points.append((exit_x, exit_y))
    final_ray_angle = theta_current - alpha
    end_x = exit_x + 2000 * math.cos(final_ray_angle)
    end_y = exit_y + 2000 * math.sin(final_ray_angle)
    points.append((end_x, end_y))
    alpha_deg = math.degrees(abs(alpha))
    beta_deg = math.degrees(abs(beta))
    if num_reflections == 1: calc_deviation = 4 * beta_deg - 2 * alpha_deg
    else: calc_deviation = 180 + 2 * alpha_deg - 6 * beta_deg
    return points, abs(calc_deviation)

def draw_ui_right_panel(screen, state, font, ui_x_start, screen_height):
    pygame.draw.rect(screen, (40, 40, 40), (ui_x_start, 0, UI_WIDTH, screen_height))
    pygame.draw.line(screen, GRAY, (ui_x_start, 0), (ui_x_start, screen_height), 2)
    title = font.render("Colors", True, WHITE)
    screen.blit(title, (ui_x_start + 20, 20))
    start_y = 60
    spacing = 50
    l1 = font.render("Vis", True, GRAY)
    l2 = font.render("Control", True, GRAY)
    screen.blit(l1, (ui_x_start + 10, start_y - 20))
    screen.blit(l2, (ui_x_start + 60, start_y - 20))
    for i, data in enumerate(RAINBOW_DATA):
        y_pos = start_y + i * spacing
        checkbox_rect = pygame.Rect(ui_x_start + 10, y_pos, 20, 20)
        pygame.draw.rect(screen, GRAY, checkbox_rect, 2)
        if state.visible_flags[i]:
            pygame.draw.rect(screen, data["rgb"], (checkbox_rect.x+4, checkbox_rect.y+4, 12, 12))
        radio_center = (ui_x_start + 80, y_pos + 10)
        pygame.draw.circle(screen, GRAY, radio_center, 10, 2)
        if state.focused_index == i:
            pygame.draw.circle(screen, WHITE, radio_center, 6)
        color_name = font.render(data["name"], True, data["rgb"])
        screen.blit(color_name, (ui_x_start + 110, y_pos))
    inst_y = screen_height - 120
    lines = ["Drag Left side", "for Primary.", "Drag Right side", "for Secondary."]
    for idx, line in enumerate(lines):
        inst_surf = font.render(line, True, GRAY)
        screen.blit(inst_surf, (ui_x_start + 10, inst_y + (idx*20)))

def draw_top_controls(screen, state, font):
    buttons = []
    start_x = 20
    start_y = 20
    p_text = f"Primary: {'ON' if state.show_primary else 'OFF'}"
    surf = font.render(p_text, True, WHITE if state.show_primary else GRAY)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    color = BUTTON_ACTIVE_COLOR if state.show_primary else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)
    screen.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_primary"})
    start_x += rect.width + 20
    s_text = f"Secondary: {'ON' if state.show_secondary else 'OFF'}"
    surf = font.render(s_text, True, WHITE if state.show_secondary else GRAY)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    color = BUTTON_ACTIVE_COLOR if state.show_secondary else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)
    screen.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_secondary"})
    start_x += rect.width + 20
    opt_text = "Set Optimal"
    surf = font.render(opt_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    pygame.draw.rect(screen, BUTTON_COLOR, rect, border_radius=5)
    pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)
    screen.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "set_optimal"})
    
    start_x += rect.width + 30
    back_text = "Meny"
    surf = font.render(back_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, 80, 35)
    pygame.draw.rect(screen, (150, 50, 50), rect, border_radius=5)
    screen.blit(surf, (rect.centerx - surf.get_width()//2, rect.centery - surf.get_height()//2))
    buttons.append({"rect": rect, "action": "back"})
    return buttons

def handle_click(pos, state, ui_x_start, top_buttons, drop_radius):
    x, y = pos
    for btn in top_buttons:
        if btn["rect"].collidepoint(pos):
            if btn["action"] == "toggle_primary": state.show_primary = not state.show_primary
            elif btn["action"] == "toggle_secondary": state.show_secondary = not state.show_secondary
            elif btn["action"] == "set_optimal":
                for i, data in enumerate(RAINBOW_DATA):
                    n = data["n"]
                    if 4 - n**2 > 0: state.impact_primary[i] = drop_radius * math.sqrt((4 - n**2) / 3)
                    if 9 - n**2 > 0: state.impact_secondary[i] = drop_radius * math.sqrt((9 - n**2) / 8)
                state.show_primary = True; state.show_secondary = True
            elif btn["action"] == "back": return "BACK"
            return True
    if x >= ui_x_start:
        start_y = 60
        spacing = 50
        for i in range(len(RAINBOW_DATA)):
            y_pos = start_y + i * spacing
            if (ui_x_start + 10 <= x <= ui_x_start + 30) and (y_pos <= y <= y_pos + 20):
                state.visible_flags[i] = not state.visible_flags[i]
                state.focused_index = i
            if (ui_x_start + 60 <= x <= ui_x_start + 100) and (y_pos <= y <= y_pos + 20):
                state.focused_index = i
        return True
    return False

def main(screen=None):
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Regndroppe (Enkel)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    
    state = SimulationState()
    canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    buttons = []

    running = True
    win_w, win_h = screen.get_width(), screen.get_height()

    while running:
        ui_x_start, drop_center, drop_radius = get_layout(INTERNAL_WIDTH, INTERNAL_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    sx = INTERNAL_WIDTH / win_w
                    sy = INTERNAL_HEIGHT / win_h
                    scaled_pos = (mx * sx, my * sy)
                    
                    ui_res = handle_click(scaled_pos, state, ui_x_start, buttons, drop_radius)
                    if ui_res == "BACK": running = False
                    elif not ui_res: state.is_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                state.is_dragging = False
        
        if state.is_dragging:
            mx_raw, my_raw = pygame.mouse.get_pos()
            mx = mx_raw * (INTERNAL_WIDTH / win_w)
            if mx < ui_x_start:
                dx = mx - drop_center[0]
                raw_dist = abs(dx)
                limit = drop_radius - 2
                if raw_dist > limit: raw_dist = limit
                if raw_dist < 5: raw_dist = 5
                if dx < 0: state.impact_primary[state.focused_index] = raw_dist
                else: state.impact_secondary[state.focused_index] = raw_dist

        canvas.fill(BACKGROUND_COLOR)
        pygame.draw.circle(canvas, DROP_FILL_COLOR, drop_center, drop_radius)
        pygame.draw.circle(canvas, DROP_OUTLINE_COLOR, drop_center, drop_radius, 2)
        pygame.draw.line(canvas, (50, 50, 50), (drop_center[0], 0), (drop_center[0], INTERNAL_HEIGHT), 1)
        pygame.draw.line(canvas, (50, 50, 50), (0, drop_center[1]), (ui_x_start, drop_center[1]), 1)
        
        focused_deviation_p = 0.0
        focused_deviation_s = 0.0
        
        ray_layer = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        ray_layer.fill((0, 0, 0))
        
        for i, data in enumerate(RAINBOW_DATA):
            if state.visible_flags[i]:
                width = 4 if i == state.focused_index else 2
                intensity = 1.0 if i == state.focused_index else 0.7
                col = tuple(min(255, int(c * intensity)) for c in data["rgb"])
                temp_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
                temp_surf.fill((0,0,0))
                
                if state.show_primary:
                    impact_p = state.impact_primary[i]
                    path_p, dev_p = calculate_ray_path_from_bottom(-impact_p, data["n"], drop_center, drop_radius, INTERNAL_HEIGHT, 1)
                    if path_p:
                        pygame.draw.lines(temp_surf, col, False, path_p, width)
                        if i == state.focused_index: focused_deviation_p = dev_p
                if state.show_secondary:
                    impact_s = state.impact_secondary[i]
                    path_s, dev_s = calculate_ray_path_from_bottom(impact_s, data["n"], drop_center, drop_radius, INTERNAL_HEIGHT, 2)
                    if path_s:
                        pygame.draw.lines(temp_surf, col, False, path_s, width)
                        if i == state.focused_index: focused_deviation_s = dev_s
                ray_layer.blit(temp_surf, (0,0), special_flags=pygame.BLEND_ADD)

        canvas.blit(ray_layer, (0,0), special_flags=pygame.BLEND_ADD)
        buttons = draw_top_controls(canvas, state, font)
        draw_ui_right_panel(canvas, state, font, ui_x_start, INTERNAL_HEIGHT)
        
        if focused_deviation_p or focused_deviation_s:
            big_font = pygame.font.SysFont("Arial", 20, bold=True)
            txt_lines = [f"Color: {RAINBOW_DATA[state.focused_index]['name']}"]
            if state.show_primary: txt_lines.append(f"Primary Angle: {focused_deviation_p:.1f}°")
            if state.show_secondary: txt_lines.append(f"Secondary Angle: {focused_deviation_s:.1f}°")
            for idx, txt in enumerate(txt_lines):
                surf = big_font.render(txt, True, WHITE)
                canvas.blit(surf, (drop_center[0] + drop_radius + 20, drop_center[1] - drop_radius - 60 + idx*25))

        scaled_surf = pygame.transform.scale(canvas, (win_w, win_h))
        screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    return

if __name__ == "__main__":
    main()
"""

# 5. droplet2.py
code_droplet2 = r"""import pygame
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 1200, 800
BACKGROUND_COLOR = (5, 5, 5) 
DROP_CENTER = (WIDTH // 2, 200)
DROP_RADIUS = 23 

WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
BUTTON_COLOR = (50, 50, 80)
BUTTON_ACTIVE_COLOR = (80, 100, 80)
BUTTON_CLEAR_COLOR = (100, 50, 50) 
DROP_FILL_COLOR = (20, 20, 60)
DROP_OUTLINE_COLOR = (200, 200, 220)

RAINBOW_DATA = [
    {"name": "Red",    "rgb": (255, 0, 0),     "n": 1.331},
    {"name": "Orange", "rgb": (255, 127, 0),   "n": 1.333},
    {"name": "Yellow", "rgb": (255, 255, 0),   "n": 1.335},
    {"name": "Green",  "rgb": (0, 255, 0),     "n": 1.338},
    {"name": "Blue",   "rgb": (0, 0, 255),     "n": 1.343},
    {"name": "Indigo", "rgb": (75, 0, 130),    "n": 1.345},
    {"name": "Violet", "rgb": (148, 0, 211),   "n": 1.348},
]

def calculate_ray_path_from_bottom(x_offset, n_color, num_reflections):
    points = []
    start_x = DROP_CENTER[0] + x_offset
    start_y = HEIGHT
    points.append((start_x, start_y))
    if abs(x_offset) > DROP_RADIUS: return points 
    dy_entry = math.sqrt(DROP_RADIUS**2 - x_offset**2)
    entry_x = start_x
    entry_y = DROP_CENTER[1] + dy_entry
    points.append((entry_x, entry_y))
    try: alpha = math.asin(x_offset / DROP_RADIUS)
    except ValueError: return points
    sin_beta = (1.0003 / n_color) * math.sin(alpha)
    if abs(sin_beta) > 1: return points 
    beta = math.asin(sin_beta)
    theta_current = math.atan2(dy_entry, x_offset)
    rotation_step = -(math.pi - 2 * beta)
    for _ in range(num_reflections):
        theta_current += rotation_step
        ref_x = DROP_CENTER[0] + DROP_RADIUS * math.cos(theta_current)
        ref_y = DROP_CENTER[1] + DROP_RADIUS * math.sin(theta_current)
        points.append((ref_x, ref_y))
    theta_current += rotation_step
    exit_x = DROP_CENTER[0] + DROP_RADIUS * math.cos(theta_current)
    exit_y = DROP_CENTER[1] + DROP_RADIUS * math.sin(theta_current)
    points.append((exit_x, exit_y))
    final_ray_angle = theta_current - alpha
    end_x = exit_x + 3000 * math.cos(final_ray_angle) 
    end_y = exit_y + 3000 * math.sin(final_ray_angle)
    points.append((end_x, end_y))
    return points

def draw_buttons(surface, font, primary_visible, secondary_visible):
    buttons = []
    start_x = 20
    start_y = 20
    p_text = f"Single: {'CLEAR' if primary_visible else 'START'}"
    surf = font.render(p_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    color = BUTTON_CLEAR_COLOR if primary_visible else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=5)
    surface.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_primary"})
    start_x += rect.width + 20
    s_text = f"Double: {'CLEAR' if secondary_visible else 'START'}"
    surf = font.render(s_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, surf.get_width() + 20, 35)
    color = BUTTON_CLEAR_COLOR if secondary_visible else BUTTON_COLOR
    pygame.draw.rect(surface, color, rect, border_radius=5)
    pygame.draw.rect(surface, GRAY, rect, 2, border_radius=5)
    surface.blit(surf, (rect.x + 10, rect.y + 8))
    buttons.append({"rect": rect, "action": "toggle_secondary"})
    
    start_x += rect.width + 30
    back_text = "Meny"
    surf = font.render(back_text, True, WHITE)
    rect = pygame.Rect(start_x, start_y, 80, 35)
    pygame.draw.rect(surface, (150, 50, 50), rect, border_radius=5)
    surface.blit(surf, (rect.centerx - surf.get_width()//2, rect.centery - surf.get_height()//2))
    buttons.append({"rect": rect, "action": "back"})
    return buttons

def main(screen=None):
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Regndroppe (Avancerad)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    
    canvas = pygame.Surface((WIDTH, HEIGHT))
    primary_canvas = pygame.Surface((WIDTH, HEIGHT))
    primary_canvas.fill((0, 0, 0))
    secondary_canvas = pygame.Surface((WIDTH, HEIGHT))
    secondary_canvas.fill((0, 0, 0))
    
    animating_primary = False
    primary_visible = False 
    p_current_offset = -DROP_RADIUS * 0.99 
    animating_secondary = False
    secondary_visible = False
    s_current_offset = -DROP_RADIUS * 0.99 
    step_size = 0.1 
    rays_to_draw_per_frame = 1 
    buttons = []

    running = True
    win_w, win_h = screen.get_width(), screen.get_height()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    sx = WIDTH / win_w
                    sy = HEIGHT / win_h
                    logical_pos = (mx * sx, my * sy)
                    
                    for btn in buttons:
                        if btn["rect"].collidepoint(logical_pos):
                            if btn["action"] == "toggle_primary":
                                if primary_visible:
                                    animating_primary = False; primary_visible = False; primary_canvas.fill((0,0,0))
                                else:
                                    animating_primary = True; primary_visible = True; p_current_offset = -DROP_RADIUS * 0.99; primary_canvas.fill((0,0,0))
                            elif btn["action"] == "toggle_secondary":
                                if secondary_visible:
                                    animating_secondary = False; secondary_visible = False; secondary_canvas.fill((0,0,0))
                                else:
                                    animating_secondary = True; secondary_visible = True; s_current_offset = -DROP_RADIUS * 0.99; secondary_canvas.fill((0,0,0))
                            elif btn["action"] == "back":
                                running = False

        if animating_primary:
            for _ in range(rays_to_draw_per_frame):
                if p_current_offset > DROP_RADIUS * 0.99: animating_primary = False; break
                offset = p_current_offset
                for data in RAINBOW_DATA:
                    col = (*data["rgb"], 50) 
                    path = calculate_ray_path_from_bottom(offset, data["n"], 1)
                    if len(path) >= 2:
                        temp = pygame.Surface((WIDTH, HEIGHT))
                        pygame.draw.lines(temp, col, False, path, 1)
                        primary_canvas.blit(temp, (0,0), special_flags=pygame.BLEND_ADD)
                p_current_offset += step_size

        if animating_secondary:
            for _ in range(rays_to_draw_per_frame):
                if s_current_offset > DROP_RADIUS * 0.99: animating_secondary = False; break
                offset = s_current_offset
                for data in RAINBOW_DATA:
                    col = (*data["rgb"], 35)
                    path = calculate_ray_path_from_bottom(offset, data["n"], 2)
                    if len(path) >= 2:
                        temp = pygame.Surface((WIDTH, HEIGHT))
                        pygame.draw.lines(temp, col, False, path, 1)
                        secondary_canvas.blit(temp, (0,0), special_flags=pygame.BLEND_ADD)
                s_current_offset += step_size

        canvas.fill(BACKGROUND_COLOR)
        pygame.draw.circle(canvas, DROP_FILL_COLOR, DROP_CENTER, DROP_RADIUS)
        pygame.draw.circle(canvas, DROP_OUTLINE_COLOR, DROP_CENTER, DROP_RADIUS, 2)
        canvas.blit(primary_canvas, (0, 0), special_flags=pygame.BLEND_ADD)
        canvas.blit(secondary_canvas, (0, 0), special_flags=pygame.BLEND_ADD)
        buttons = draw_buttons(canvas, font, primary_visible, secondary_visible)

        scaled_surf = pygame.transform.scale(canvas, (win_w, win_h))
        screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    return

if __name__ == "__main__":
    main()
"""

# 6. rainbow.py
code_rainbow = r"""import pygame
import math
import random
import sys
import os

# --- Constants ---
INTERNAL_WIDTH, INTERNAL_HEIGHT = 1200, 800
FOV_DEGREES = 70.0   
SUN_ELEVATION = 40.0 
GLOBAL_INTENSITY = 2.5
MANUAL_CURSOR_OFFSET = (-10, -10) 

def gaussian(x, mu, sigma):
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def get_rainbow_color(angle_deg):
    r, g, b = 0.0, 0.0, 0.0
    retro_peak = 0.8 * math.exp(-0.5 * (angle_deg / 0.8) ** 2)
    r += retro_peak; g += retro_peak; b += retro_peak
    if angle_deg < 42.0:
        glow = 0.20 + 0.08 * math.exp((angle_deg - 42.0) * 0.15)
        r += glow; g += glow; b += glow
    if 38.0 < angle_deg < 45.0:
        intensity_prim = 0.6
        b += intensity_prim * gaussian(angle_deg, 40.8, 1.4) 
        g += intensity_prim * gaussian(angle_deg, 41.6, 1.3)
        r += intensity_prim * gaussian(angle_deg, 42.3, 1.3)
    if angle_deg > 50.0:
        outer_glow = 0.05 
        r += outer_glow; g += outer_glow; b += outer_glow
    if 48.0 < angle_deg < 56.0:
        intensity_sec = 0.22
        r += intensity_sec * gaussian(angle_deg, 50.6, 1.6)
        g += intensity_sec * gaussian(angle_deg, 52.0, 1.6)
        b += intensity_sec * gaussian(angle_deg, 53.4, 1.6)
    return r, g, b

def create_fallback_landscape():
    surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    for y in range(INTERNAL_HEIGHT//2):
        val = int(255 * (y / (INTERNAL_HEIGHT//2)))
        col = (50, 100, 150 + val//3)
        pygame.draw.line(surf, col, (0, y), (INTERNAL_WIDTH, y))
    pygame.draw.rect(surf, (20, 40, 20), (0, INTERNAL_HEIGHT//2, INTERNAL_WIDTH, INTERNAL_HEIGHT//2))
    font = pygame.font.SysFont("Arial", 30)
    txt = font.render("Ingen 'landscape.jpg' hittades.", True, (200, 200, 200))
    surf.blit(txt, (20, 20))
    return surf

def calculate_pixel_color(px, py, asp_x, asp_y, view_dist, boost_intensity=False):
    dx = px - asp_x; dy = py - asp_y
    r_px = math.sqrt(dx*dx + dy*dy)
    angle = math.degrees(math.atan2(r_px, view_dist))
    if angle < 65.0:
        rf, gf, bf = get_rainbow_color(angle)
        if rf > 0.001 or gf > 0.001 or bf > 0.001:
            brightness = 150
            intensity_multiplier = GLOBAL_INTENSITY
            if boost_intensity: intensity_multiplier *= 3.0
            r = min(255, int(rf * brightness * intensity_multiplier))
            g = min(255, int(gf * brightness * intensity_multiplier))
            b = min(255, int(bf * brightness * intensity_multiplier))
            return (r, g, b)
    return (0, 0, 0)

def main(screen=None):
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
    pygame.display.set_caption("Regnbåge: Monte Carlo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    try:
        if os.path.exists("landscape.jpg"):
            bg_image = pygame.image.load("landscape.jpg")
            bg_image = pygame.transform.scale(bg_image, (INTERNAL_WIDTH, INTERNAL_HEIGHT))
        else: raise FileNotFoundError
    except: bg_image = create_fallback_landscape()

    fov_rad = math.radians(FOV_DEGREES)
    view_dist = (INTERNAL_WIDTH / 2) / math.tan(fov_rad / 2)
    asp_angle_rad = math.radians(SUN_ELEVATION)
    asp_pixel_y = (INTERNAL_HEIGHT / 2) + math.tan(asp_angle_rad) * view_dist
    asp_pixel_x = INTERNAL_WIDTH / 2

    rainbow_layer = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    rainbow_layer.fill((0, 0, 0))
    
    start_btn = pygame.Rect(10, 50, 120, 35)
    clear_btn = pygame.Rect(140, 50, 100, 35)
    back_btn = pygame.Rect(INTERNAL_WIDTH - 120, 50, 100, 35)
    
    running = True
    simulating = False 
    manual_dragging = False
    manual_pos = (0, 0) 
    
    points_per_frame = 2.0
    acceleration = 1.02 
    max_points = 20000 
    total_points = 0
    
    win_w, win_h = screen.get_width(), screen.get_height()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    mx, my = event.pos
                    scale_x = INTERNAL_WIDTH / win_w
                    scale_y = INTERNAL_HEIGHT / win_h
                    logical_pos = (mx * scale_x, my * scale_y)

                    if back_btn.collidepoint(logical_pos):
                        running = False
                    elif start_btn.collidepoint(logical_pos):
                        simulating = not simulating
                    elif clear_btn.collidepoint(logical_pos):
                        rainbow_layer.fill((0,0,0))
                        total_points = 0
                        points_per_frame = 2.0 
                    else:
                        manual_dragging = True
                        manual_pos = logical_pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and manual_dragging:
                    target_pos = (manual_pos[0] + MANUAL_CURSOR_OFFSET[0], manual_pos[1] + MANUAL_CURSOR_OFFSET[1])
                    col = calculate_pixel_color(target_pos[0], target_pos[1], asp_pixel_x, asp_pixel_y, view_dist, boost_intensity=False)
                    if col != (0,0,0):
                        radius = 6 
                        temp_stamp = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
                        temp_stamp.fill((0,0,0,0))
                        pygame.draw.circle(temp_stamp, col, target_pos, radius)
                        rainbow_layer.blit(temp_stamp, (0,0), special_flags=pygame.BLEND_MAX)
                        total_points += 1 
                    manual_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                scale_x = INTERNAL_WIDTH / win_w
                scale_y = INTERNAL_HEIGHT / win_h
                manual_pos = (mx * scale_x, my * scale_y)

        if simulating:
            count = int(points_per_frame)
            frame_surface = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
            frame_surface.fill((0,0,0))
            if count > 0:
                pixels = pygame.PixelArray(frame_surface)
                for _ in range(count):
                    px = int(random.uniform(0, INTERNAL_WIDTH))
                    py = int(random.uniform(0, INTERNAL_HEIGHT))
                    col = calculate_pixel_color(px, py, asp_pixel_x, asp_pixel_y, view_dist, boost_intensity=False)
                    if col != (0,0,0): pixels[px, py] = col
                pixels.close()
                rainbow_layer.blit(frame_surface, (0,0), special_flags=pygame.BLEND_MAX)
            points_per_frame *= acceleration
            if points_per_frame > max_points: points_per_frame = max_points
            total_points += count

        canvas.blit(bg_image, (0, 0))
        canvas.blit(rainbow_layer, (0, 0), special_flags=pygame.BLEND_ADD)

        if manual_dragging:
            target_pos = (manual_pos[0] + MANUAL_CURSOR_OFFSET[0], manual_pos[1] + MANUAL_CURSOR_OFFSET[1])
            col = calculate_pixel_color(target_pos[0], target_pos[1], asp_pixel_x, asp_pixel_y, view_dist, boost_intensity=True)
            pygame.draw.circle(canvas, col, target_pos, 8) 
            pygame.draw.circle(canvas, (255, 255, 255), target_pos, 9, 1)
            pygame.draw.line(canvas, (200, 200, 200), manual_pos, target_pos, 1)

        status = f"Droppar: {total_points:,} | Hastighet: {int(points_per_frame) if simulating else 0}/bild"
        txt = font.render(status, True, (255, 255, 255))
        canvas.blit(txt, (15, 15))
        
        raw_mx, raw_my = pygame.mouse.get_pos()
        scale_x = INTERNAL_WIDTH / win_w
        scale_y = INTERNAL_HEIGHT / win_h
        log_mx, log_my = raw_mx * scale_x, raw_my * scale_y

        btn_hover = start_btn.collidepoint((log_mx, log_my))
        if simulating:
            base_col = (100, 150, 100) if btn_hover else (60, 100, 60)
            text_str = "Stoppa Regn"
        else:
            base_col = (100, 100, 150) if btn_hover else (60, 60, 100)
            text_str = "Starta Regn"
            
        pygame.draw.rect(canvas, base_col, start_btn, border_radius=5)
        pygame.draw.rect(canvas, (200, 200, 200), start_btn, 1, border_radius=5)
        btn_txt = font.render(text_str, True, (255, 255, 255))
        canvas.blit(btn_txt, (start_btn.centerx - btn_txt.get_width()//2, start_btn.centery - btn_txt.get_height()//2))

        clear_hover = clear_btn.collidepoint((log_mx, log_my))
        clear_col = (150, 100, 100) if clear_hover else (100, 60, 60)
        pygame.draw.rect(canvas, clear_col, clear_btn, border_radius=5)
        pygame.draw.rect(canvas, (200, 200, 200), clear_btn, 1, border_radius=5)
        clear_txt = font.render("Rensa", True, (255, 255, 255))
        canvas.blit(clear_txt, (clear_btn.centerx - clear_txt.get_width()//2, clear_btn.centery - clear_txt.get_height()//2))

        back_hover = back_btn.collidepoint((log_mx, log_my))
        back_col = (180, 50, 50) if back_hover else (150, 50, 50)
        pygame.draw.rect(canvas, back_col, back_btn, border_radius=5)
        pygame.draw.rect(canvas, (200, 200, 200), back_btn, 1, border_radius=5)
        back_txt = font.render("Meny", True, (255, 255, 255))
        canvas.blit(back_txt, (back_btn.centerx - back_txt.get_width()//2, back_btn.centery - back_txt.get_height()//2))

        if not simulating and total_points == 0:
            inst = font.render("Klicka & Dra för att placera droppar manuellt.", True, (200, 200, 200))
            canvas.blit(inst, (250, 60))

        scaled_surf = pygame.transform.scale(canvas, (win_w, win_h))
        screen.blit(scaled_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    return

if __name__ == "__main__":
    main()
"""

# Spara alla dessa filer
files = {
    "master.py": code_master,
    "refraction.py": code_refraction,
    "prism.py": code_prism,
    "droplet.py": code_droplet,
    "droplet2.py": code_droplet2,
    "rainbow.py": code_rainbow
}

# Skriv filerna
for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# Skapa ZIP-fil
zip_filename = "FysikLjus_Project.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for filename in files:
        zipf.write(filename)

print(f"Klar! '{zip_filename}' har skapats med alla 6 Python-filer.")