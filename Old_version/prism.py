import pygame
import sys
import math

# --- Constants ---
# Intern upplösning för simuleringen (fysiken och layouten baseras på denna)
INTERNAL_W, INTERNAL_H = 1200, 600
BACKGROUND_COLOR = (10, 10, 10)

# Physics Constants
SPEED_AIR = 4.0
STAGGER_SPACING = 35.0

# Colors & Refractive Indices
RAINBOW_DATA = [
    {"name": "Röd",    "rgb": (255, 0, 0),     "n": 1.25}, 
    {"name": "Orange", "rgb": (255, 127, 0),   "n": 1.29},
    {"name": "Gul",    "rgb": (255, 255, 0),   "n": 1.33},
    {"name": "Grön",   "rgb": (0, 255, 0),     "n": 1.38},
    {"name": "Blå",    "rgb": (0, 0, 255),     "n": 1.42},
    {"name": "Indigo", "rgb": (75, 0, 130),    "n": 1.46},
    {"name": "Violett", "rgb": (148, 0, 211),   "n": 1.50}, 
]

# UI Colors
BUTTON_COLOR = (50, 80, 50)
BUTTON_HOVER = (70, 100, 70)
BUTTON_ACTIVE = (100, 150, 100)
TEXT_WHITE = (255, 255, 255)

# --- Vector Math Helpers ---
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
    
    if 0 <= ua <= 1 and 0 <= ub <= 1:
        return ua
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
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    hw = width / 2
    hh = height / 2
    
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    verts = []
    for cx, cy in corners:
        rx = cx * cos_a - cy * sin_a
        ry = cx * sin_a + cy * cos_a
        verts.append((center[0] + rx, center[1] + ry))
        
    return verts

def calculate_polygon_verts(center, radius, rotation_deg, num_sides):
    verts = []
    angle_step = 360.0 / num_sides
    start_angle = 90 if num_sides == 3 else 45 
    
    for i in range(num_sides):
        angle = start_angle + i * angle_step - rotation_deg
        rad = math.radians(angle)
        x = center[0] + radius * math.cos(rad)
        y = center[1] - radius * math.sin(rad)
        verts.append((x, y))
    return verts

# --- Physics Engine ---

class PhysicsWorld:
    def __init__(self):
        # Default initialization (Idle)
        self.mode = None
        self.verts = []
        self.edges = []
        self.medium_active = False

    def set_mode(self, mode):
        self.mode = mode
        if mode == "block_straight":
            self.medium_active = True
            # Straight Square (0 rotation), doubled width (500)
            self.verts = calculate_rotated_rect_verts((600, 300), 500, 250, 0)
            self.edges = get_polygon_edges(self.verts)
        elif mode == "block_rotated":
            self.medium_active = True
            # Rotated Square (20 degrees)
            self.verts = calculate_rotated_rect_verts((600, 300), 250, 250, 20)
            self.edges = get_polygon_edges(self.verts)
        elif mode == "triangle":
            self.medium_active = True
            # Equilateral Triangle
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
        
        if not self.medium_active:
            return end_pos, velocity, None

        best_t = 2.0 
        hit_edge = None
        
        for edge in self.edges:
            t = intersect_segment_line(start_pos, end_pos, edge['p1'], edge['p2'])
            if t is not None:
                if t < best_t:
                    best_t = t
                    hit_edge = edge
        
        if hit_edge and best_t <= 1.0:
            hit_pos = vec_add(start_pos, vec_mul(move_vec, best_t))
            incident = vec_norm(velocity)
            normal = hit_edge['normal']
            
            dot_prod = vec_dot(incident, normal)
            entering = dot_prod < 0
            
            if entering:
                n1 = 1.0
                n2 = target_n
                effective_normal = normal 
                new_inside_state = True
            else:
                n1 = target_n
                n2 = 1.0
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
                if new_pos[0] > -50:
                    self.trail.append(new_pos)
                self.inside = hit['new_inside']
                current_vel = new_vel
                consumed = hit['t']
                remaining_t *= (1.0 - consumed)
                
                epsilon = 0.1
                nudge = vec_mul(vec_norm(current_vel), epsilon)
                current_pos = vec_add(new_pos, nudge)
                
                if remaining_t <= 0.001: break
            else:
                current_pos = new_pos
                if current_pos[0] > -50:
                    self.trail.append(current_pos)
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
    # Use reversed() to flip the order: Violet starts at the front, Red at the back.
    for i, data in enumerate(reversed(RAINBOW_DATA)):
        offset = i * STAGGER_SPACING
        photons.append(Photon(data, center_y, offset))
    return photons

def main():
    pygame.init()
    # Initiera fönstret med startstorlek men gör det skalbart
    win_w, win_h = INTERNAL_W, INTERNAL_H
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Refraktion: Hastighetsloppet")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    # Skapa en intern rityta (canvas) med fast upplösning
    canvas = pygame.Surface((INTERNAL_W, INTERNAL_H))
    
    world = PhysicsWorld()
    photons = [] # Start empty (Idle state)
    
    # UI Buttons Layout
    y_pos = 50
    w = 120
    h = 40
    gap = 10
    x = 50
    
    btn_air = pygame.Rect(x, y_pos, w, h); x += w + gap
    btn_straight = pygame.Rect(x, y_pos, w, h); x += w + gap
    btn_rotated = pygame.Rect(x, y_pos, w, h); x += w + gap
    btn_tri = pygame.Rect(x, y_pos, w, h); x += w + gap
    
    # Ny Rensa-knapp
    x += 20 # Lite extra avstånd
    btn_clear = pygame.Rect(x, y_pos, w, h)
    
    sim_surf = pygame.Surface((INTERNAL_W, INTERNAL_H))
    p_surf = pygame.Surface((INTERNAL_W, INTERNAL_H))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Uppdatera fönsterstorleken
                win_w, win_h = event.w, event.h
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Skala muspositionen från fönster-koordinater till intern-koordinater
                    mx, my = event.pos
                    scale_x = INTERNAL_W / win_w
                    scale_y = INTERNAL_H / win_h
                    scaled_pos = (mx * scale_x, my * scale_y)
                    
                    if btn_air.collidepoint(scaled_pos):
                        world.set_mode("air")
                        photons = reset_simulation()
                    elif btn_straight.collidepoint(scaled_pos):
                        world.set_mode("block_straight")
                        photons = reset_simulation()
                    elif btn_rotated.collidepoint(scaled_pos):
                        world.set_mode("block_rotated")
                        photons = reset_simulation()
                    elif btn_tri.collidepoint(scaled_pos):
                        world.set_mode("triangle")
                        photons = reset_simulation()
                    elif btn_clear.collidepoint(scaled_pos):
                        photons = [] # Rensa alla fotoner

        for p in photons:
            p.update(world)

        # Rita allt på den interna canvasen
        canvas.fill(BACKGROUND_COLOR)
        
        # Draw Medium
        if world.medium_active:
            pygame.draw.polygon(canvas, (30, 40, 50), world.verts)
            pygame.draw.polygon(canvas, (100, 120, 150), world.verts, 2)
            
            # Label
            name = "Okänd"
            if world.mode == "block_straight": name = "BLOCK (Rak)"
            elif world.mode == "block_rotated": name = "BLOCK (Roterad)"
            elif world.mode == "triangle": name = "PRISMA"
            
            label = font.render(name, True, (100, 120, 150))
            canvas.blit(label, (600 - label.get_width()//2, 150))

        # Draw Photons (Additive)
        if photons:
            sim_surf.fill((0, 0, 0))
            for p in photons:
                p_surf.fill((0, 0, 0))
                p.draw(p_surf)
                sim_surf.blit(p_surf, (0, 0), special_flags=pygame.BLEND_ADD)
            canvas.blit(sim_surf, (0, 0), special_flags=pygame.BLEND_ADD)

        # Draw GUI Buttons
        buttons = [
            (btn_air, "Inget medium", world.mode == "air"),
            (btn_straight, "Rak", world.mode == "block_straight"),
            (btn_rotated, "Roterad", world.mode == "block_rotated"),
            (btn_tri, "Prisma", world.mode == "triangle"),
            (btn_clear, "Rensa", False) # Rensa-knappen (aldrig aktiv status)
        ]
        
        # Hämta skalad musposition för hover-effekt
        raw_mx, raw_my = pygame.mouse.get_pos()
        scale_x = INTERNAL_W / win_w
        scale_y = INTERNAL_H / win_h
        scaled_mouse = (raw_mx * scale_x, raw_my * scale_y)
        
        for rect, text, active in buttons:
            col = BUTTON_ACTIVE if active else BUTTON_COLOR
            if rect.collidepoint(scaled_mouse): col = BUTTON_HOVER
            if active: col = BUTTON_ACTIVE
            
            pygame.draw.rect(canvas, col, rect, border_radius=5)
            pygame.draw.rect(canvas, TEXT_WHITE, rect, 2, border_radius=5)
            t_surf = font.render(text, True, TEXT_WHITE)
            canvas.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.centery - t_surf.get_height()//2))

        # Info Text
        msg = ""
        if world.mode is None:
            msg = "Välj ett läge för att starta simuleringen."
        elif world.mode == "air":
            msg = "Vakuum: Alla färger färdas med samma hastighet (c)."
        elif world.mode == "block_straight":
            msg = "Vinkelrätt infall: Ljuset saktar ner, men riktningen ändras inte. Rött är snabbast."
        elif world.mode == "block_rotated":
            msg = "Brytning: Ljuset böjs av och saktar ner. Rött är snabbast."
        elif world.mode == "triangle":
            msg = "Dispersion: Formen förstärker hastighetsskillnaden och separerar färgerna."
            
        msg_surf = font.render(msg, True, (150, 150, 150))
        canvas.blit(msg_surf, (INTERNAL_W//2 - msg_surf.get_width()//2, INTERNAL_H - 50))

        # Skala upp canvasen och rita på skärmen
        scaled_surf = pygame.transform.scale(canvas, (win_w, win_h))
        screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    return

if __name__ == "__main__":
    main()