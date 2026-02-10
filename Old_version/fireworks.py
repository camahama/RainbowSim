import pygame
import random
import math
import sys

# --- Constants ---
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colors
SKY_TOP = (5, 10, 20)       # Deep space blue
SKY_BOTTOM = (20, 30, 50)   # Lighter horizon blue
AURORA_BASE = (0, 255, 150) # Cyan/Green
WHITE = (255, 255, 255)
SNOW_COLOR = (220, 220, 255)

# Firework Parameters
GRAVITY = 0.05
DRAG = 0.98  # Air resistance

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, int(HEIGHT * 0.8))
        self.brightness = random.randint(50, 255)
        self.flicker_speed = random.uniform(0.02, 0.05)
        self.timer = random.uniform(0, 6.28)

    def update(self):
        self.timer += self.flicker_speed
        # Sine wave flicker
        self.val = 150 + 100 * math.sin(self.timer)

    def draw(self, surface):
        c = max(0, min(255, int(self.val)))
        # Draw a tiny plus sign or dot for stars
        surface.set_at((self.x, self.y), (c, c, c))
        if self.val > 230: # Glint effect for bright stars
             surface.set_at((self.x + 1, self.y), (c//2, c//2, c//2))
             surface.set_at((self.x - 1, self.y), (c//2, c//2, c//2))
             surface.set_at((self.x, self.y + 1), (c//2, c//2, c//2))
             surface.set_at((self.x, self.y - 1), (c//2, c//2, c//2))

class AuroraLayer:
    def __init__(self, y_base, amplitude, frequency, speed, color, alpha):
        self.y_base = y_base
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.phase = random.uniform(0, 100)
        self.color = color
        self.alpha = alpha
        
        # Pre-create a surface for this layer to handle alpha
        self.surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def update(self):
        self.phase += self.speed

    def draw(self, target_surface):
        # We clear the specific surface for this frame
        self.surface.fill((0,0,0,0))
        
        points = []
        # Create a wavy line along the width
        # We add points for the polygon: 
        # Start bottom-left, go along the wave, end bottom-right, close loop.
        
        points.append((0, HEIGHT)) # Bottom Left anchor
        
        step = 20 # Pixel step size for the curve
        for x in range(0, WIDTH + step, step):
            # Complex noise using summed sines
            n1 = math.sin(x * self.frequency + self.phase)
            n2 = math.sin(x * (self.frequency * 2.5) - self.phase * 0.5)
            
            y_offset = (n1 + n2 * 0.5) * self.amplitude
            y = self.y_base + y_offset
            points.append((x, y))
            
        points.append((WIDTH, HEIGHT)) # Bottom Right anchor
        
        # Draw the polygon
        # We draw a polygon that fills from the wave DOWN to the bottom (or up)
        # However, real aurora creates "curtains". 
        # To simulate a curtain, let's actually draw vertical thick lines or a filled shape 
        # with a vertical gradient. 
        # For performance in Pygame, drawing a semi-transparent polygon is fastest.
        
        # We want the "glow" to be upwards from the curve, fading out?
        # Let's try drawing the polygon defined by the wave and the BOTTOM of screen,
        # but blended.
        
        # Let's make the shape extend UPWARDS to simulate the curtain hanging down
        # Modify points:
        
        poly_points = []
        poly_points.append((0, 0)) # Top Left
        
        for x in range(0, WIDTH + step, step):
            n1 = math.sin(x * self.frequency + self.phase)
            n2 = math.sin(x * (self.frequency * 1.5) + self.phase * 0.3)
            y = self.y_base + (n1 + n2) * self.amplitude
            poly_points.append((x, y))
            
        poly_points.append((WIDTH, 0)) # Top Right
        
        pygame.draw.polygon(self.surface, (*self.color, self.alpha), poly_points)
        
        # Additive blend onto the main screen
        target_surface.blit(self.surface, (0,0), special_flags=pygame.BLEND_ADD)

class Particle:
    def __init__(self, x, y, color, is_rocket=False):
        self.x = x
        self.y = y
        self.color = color
        self.is_rocket = is_rocket
        self.life = 255.0
        self.decay = random.uniform(1.5, 3.0)
        
        if self.is_rocket:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-12, -8)
            self.size = 3
            self.decay = 0 # Rockets die by altitude/velocity, not time
        else:
            # Explosion particle
            angle = random.uniform(0, 6.28)
            speed = random.uniform(1, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.size = random.randint(1, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY
        
        if not self.is_rocket:
            self.vx *= DRAG
            self.vy *= DRAG
            self.life -= self.decay
            
    def draw(self, surface):
        if self.life > 0:
            alpha = int(self.life)
            # Create a small surface for alpha blending if needed, 
            # or just draw solid for performance if small.
            # For glow, let's draw a larger faint circle and a smaller bright one.
            
            # Bright core
            col = self.color
            if not self.is_rocket:
                # Fade color
                factor = self.life / 255.0
                col = (int(self.color[0]*factor), int(self.color[1]*factor), int(self.color[2]*factor))
            
            pygame.draw.circle(surface, col, (int(self.x), int(self.y)), self.size)
            
            # Simple glow (optional, costs performance)
            # pygame.draw.circle(surface, (col[0]//3, col[1]//3, col[2]//3), (int(self.x), int(self.y)), self.size + 2, 1)

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = HEIGHT # Start at bottom
        self.target_y = y
        self.color = random.choice([
            (255, 50, 50),   # Red
            (50, 255, 50),   # Green
            (50, 100, 255),  # Blue
            (255, 255, 50),  # Yellow
            (255, 100, 255), # Purple
            (255, 165, 0),   # Orange
            (200, 255, 255)  # Cyan
        ])
        self.rocket = Particle(self.x, HEIGHT, self.color, is_rocket=True)
        # Override rocket velocity to reach target height roughly
        # v^2 = u^2 + 2as -> u = sqrt(-2as) roughly
        h = HEIGHT - self.target_y
        u = math.sqrt(2 * GRAVITY * h) * 1.05 # Add a bit extra
        self.rocket.vy = -u
        
        self.particles = []
        self.exploded = False
        self.done = False

    def update(self):
        if not self.exploded:
            self.rocket.update()
            # Explode if we reach apex (velocity turns positive) or height
            if self.rocket.vy >= 0 or self.rocket.y <= self.target_y:
                self.explode()
        else:
            for p in self.particles:
                p.update()
            # Remove dead particles
            self.particles = [p for p in self.particles if p.life > 0]
            if len(self.particles) == 0:
                self.done = True

    def explode(self):
        self.exploded = True
        num_particles = 80
        for _ in range(num_particles):
            self.particles.append(Particle(self.rocket.x, self.rocket.y, self.color))

    def draw(self, surface):
        if not self.exploded:
            self.rocket.draw(surface)
        else:
            for p in self.particles:
                p.draw(surface)

def draw_terrain(surface):
    # Draw silhouette of terrain
    # Simple jagged polygon
    points = [(0, HEIGHT), (0, HEIGHT - 50)]
    
    # Generate some random peaks for trees/mountains if not static
    # But for static nice look:
    mountain_color = (10, 15, 25)
    
    # Create a horizon line with some trees
    for x in range(0, WIDTH + 20, 20):
        # Noise-like base
        base_h = HEIGHT - 60 + math.sin(x * 0.01) * 20
        points.append((x, base_h))
        
        # Occasionally draw a pine tree spike
        if x % 80 == 0:
            tree_h = base_h - random.randint(30, 80)
            # Add tree points: left base, top, right base
            # We just adding to the polygon path creates a jagged fill
            points.append((x - 10, base_h)) 
            points.append((x, tree_h))
            points.append((x + 10, base_h))
            
    points.append((WIDTH, HEIGHT - 50))
    points.append((WIDTH, HEIGHT))
    
    pygame.draw.polygon(surface, mountain_color, points)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Winter Night in Northern Canada")
    clock = pygame.time.Clock()
    
    # Initialize Stars
    stars = [Star() for _ in range(150)]
    
    # Initialize Aurora Layers (Curtains)
    auroras = [
        AuroraLayer(y_base=200, amplitude=50, frequency=0.005, speed=0.02, color=(0, 200, 100), alpha=30),
        AuroraLayer(y_base=180, amplitude=70, frequency=0.003, speed=0.01, color=(50, 255, 50), alpha=20),
        AuroraLayer(y_base=220, amplitude=40, frequency=0.007, speed=0.03, color=(0, 100, 200), alpha=25),
    ]
    
    fireworks = []

    # Pre-render background gradient to save FPS
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        # Linear interpolation between sky colors
        factor = y / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * factor)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * factor)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * factor)
        pygame.draw.line(background, (r, g, b), (0, y), (WIDTH, y))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Launch firework targeting mouse y
                fireworks.append(Firework(mx, my))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fireworks.append(Firework(random.randint(100, WIDTH-100), random.randint(100, 400)))

        # 1. Draw Background
        screen.blit(background, (0, 0))

        # 2. Draw Stars
        for star in stars:
            star.update()
            star.draw(screen)
            
        # 3. Draw Aurora
        for aurora in auroras:
            aurora.update()
            aurora.draw(screen)

        # 4. Update and Draw Fireworks
        for fw in fireworks:
            fw.update()
            fw.draw(screen)
        
        # Cleanup finished fireworks
        fireworks = [fw for fw in fireworks if not fw.done]
        
        # 5. Draw Terrain (Silhouette)
        # Re-generating points every frame allows for swaying trees if we wanted, 
        # but for performance let's keep it simple or static. 
        # Since we put random values in the draw function, we should actually move that out 
        # or use a fixed seed. Let's fix the seed by creating a static surface for terrain.
        # (Optimized approach: do it once)
        
        # We handle this logic inside the loop for simplicity in this script, 
        # but to prevent "shaking" trees due to random, we seed or pre-render.
        # Let's pre-render terrain logic quickly:
        if 'terrain_surf' not in locals():
            terrain_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            random.seed(42) # Fixed seed for consistent terrain
            draw_terrain(terrain_surf)
            random.seed() # Reset seed
            
        screen.blit(terrain_surf, (0,0))
        
        # Instructions
        font = pygame.font.SysFont("Arial", 16)
        txt = font.render("Click to Launch Fireworks | Space for Random", True, (150, 180, 200))
        screen.blit(txt, (10, HEIGHT - 30))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()