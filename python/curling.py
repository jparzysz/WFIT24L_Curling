import pygame
import sys
import math

# Inicjalizuje PyGame
pygame.init()

# Definicja stałych
WIDTH, HEIGHT = 1456, 523
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (169, 169, 169)
FRICTION = 0.98  # Współczynnik tarcia
FONT_SIZE = 36

# Parametry kameni
STONE_RADIUS = 24
STONE_MASS = 18

# Tworzenie ekranu
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Curling Game Simulator")

# Załadowanie planszy z pliku
background_image = pygame.image.load('resources/curling_board.png')
background_rect = background_image.get_rect()

#
font = pygame.font.Font(None, FONT_SIZE)


class Stone:
    def __init__(self, color, pos, team):
        self.color = color
        self.pos = pos
        self.velocity = [0, 0]
        self.mass = STONE_MASS
        self.team = team

    def update_position(self):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.velocity[0] *= FRICTION
        self.velocity[1] *= FRICTION

        # Gdy prędkość wystarczająco spadnie, program zatrzymuje kamień
        if abs(self.velocity[0]) < 0.1 and abs(self.velocity[1]) < 0.1:
            self.velocity = [0, 0]

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), STONE_RADIUS)
        pygame.draw.circle(screen, GRAY, (int(self.pos[0]), int(self.pos[1])), STONE_RADIUS, 1)

    def handle_collision(self, other):
        # Wektor między kamienami
        dx = self.pos[0] - other.pos[0]
        dy = self.pos[1] - other.pos[1]
        distance = math.hypot(dx, dy)

        # Zderzenie następuje, gdy dystans między środkami kamieni jest mniejszy od 2 promieni
        if distance < 2 * STONE_RADIUS:
            # Wektor normalny
            if distance != 0:
                nx = dx / distance
                ny = dy / distance
            else:
                nx = 0
                ny = 0

            # Wektor styczny
            tx = -ny
            ty = nx

            # Iloczyn skalarny styczny
            dpTan1 = self.velocity[0] * tx + self.velocity[1] * ty
            dpTan2 = other.velocity[0] * tx + other.velocity[1] * ty

            # Iloczyn skalarny normalny
            dpNorm1 = self.velocity[0] * nx + self.velocity[1] * ny
            dpNorm2 = other.velocity[0] * nx + other.velocity[1] * ny

            # Zasada zachowania pędu w 1D
            m1 = (dpNorm1 * (self.mass - other.mass) + 2 * other.mass * dpNorm2) / (self.mass + other.mass)
            m2 = (dpNorm2 * (other.mass - self.mass) + 2 * self.mass * dpNorm1) / (self.mass + other.mass)

            # Aktualizacja prędkośći
            self.velocity[0] = tx * dpTan1 + nx * m1
            self.velocity[1] = ty * dpTan1 + ny * m1
            other.velocity[0] = tx * dpTan2 + nx * m2
            other.velocity[1] = ty * dpTan2 + ny * m2

            # Program przesuwa kamienie, aby upewnić się, że nie zachodzą na siebie i się nie połączą
            overlap = 2 * STONE_RADIUS - distance
            self.pos[0] += nx * (overlap / 2)
            self.pos[1] += ny * (overlap / 2)
            other.pos[0] -= nx * (overlap / 2)
            other.pos[1] -= ny * (overlap / 2)

# Tworzenie kamieni dla każdej drużyny
stones = []
stone_counter = 0  # Licznik kamieni
max_stones_per_team = 5

# Inicjalizacja wyników drużyn
global green_wins
green_wins = 0
global yellow_wins
yellow_wins = 0


# Funkcja do rysowania przycisków
def draw_button(text, rect, color):
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


# Funkcja do sprawdzenia, czy gra już się skończyła
def is_game_over():
    return stone_counter >= 2 * max_stones_per_team


# Funkcja określająca zwycięzcę
def determine_winner():
    center_x, center_y = WIDTH - 100, HEIGHT // 2
    min_distance_green = float('inf')
    min_distance_yellow = float('inf')

    for stone in stones:
        distance = math.hypot(stone.pos[0] - center_x, stone.pos[1] - center_y)
        if stone.team == 0:
            min_distance_green = min(min_distance_green, distance)
        else:
            min_distance_yellow = min(min_distance_yellow, distance)

    if min_distance_green < min_distance_yellow:
        return "Green Wins!"
    elif min_distance_yellow < min_distance_green:
        return "Yellow Wins!"
    else:
        return "It's a tie!"


# Funkcja do restartu gry
def restart_game():
    global stones, stone_counter
    stones = []
    stone_counter = 0


# Prostokąty przycisków
set_stone_button = pygame.Rect(10, 10, 150, 50)
restart_button = pygame.Rect(10, 70, 150, 50)

# Pętla główna
running = True
selected_stone = None
mouse_start_pos = None
game_over = False
winner_text = ""

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Program sprawdza, czy kliknięto przycisk "set stone"
            if set_stone_button.collidepoint(mouse_pos) and not game_over:
                selected_stone = None
                # Na podstawie "stone counter" program zamienia kolory kolejnych kamieni
                if stone_counter % 2 == 0:
                    color = GREEN
                    team = 0
                else:
                    color = YELLOW
                    team = 1
                # Umieszczenie kamienia w pozycji startowej
                stone = Stone(color, [85, HEIGHT // 2], team)
                stones.append(stone)
                stone_counter += 1  # Inkrementacja licznika kamieni (stone counter)
            # Program sprawdza, czy wciśnięto przycisk "restart"
            elif restart_button.collidepoint(mouse_pos):
                restart_game()
                game_over = False
                winner_text = ""
            else:
                # Program wybiera kamień, gdy go naciśnięto
                for stone in stones:
                    if (mouse_pos[0] - stone.pos[0]) ** 2 + (mouse_pos[1] - stone.pos[1]) ** 2 < STONE_RADIUS ** 2:
                        selected_stone = stone
                        mouse_start_pos = mouse_pos
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_stone:
                if mouse_start_pos:
                    mouse_end_pos = event.pos
                    dx = mouse_end_pos[0] - mouse_start_pos[0]
                    dy = mouse_end_pos[1] - mouse_start_pos[1]
                    selected_stone.velocity = [dx * 0.1, dy * 0.1]  # Program dostosowuje mnożnik dla pożądanej prędkości
                selected_stone = None
                mouse_start_pos = None
        elif event.type == pygame.MOUSEMOTION:
            # Przeciąganie wybranego kamienia
            if selected_stone and mouse_start_pos:
                selected_stone.pos = list(event.pos)

    # Aktualizacja pozycji kamieni, wprowadzenie obsługi kolizji
    for i, stone in enumerate(stones):
        stone.update_position()
        for j in range(i + 1, len(stones)):
            stone.handle_collision(stones[j])

    # Program rysuje tło
    screen.fill(WHITE)
    screen.blit(background_image, background_rect)

    # Program rysuje centralną linię i pierścienie
    pygame.draw.line(screen, BLACK, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

    # Program rysuje przycisk "set stone"
    draw_button("Set Stone", set_stone_button, GREEN)

    # Program rysuje przycisk restart
    draw_button("Restart", restart_button, RED)

    # Program rysuje kamienie
    for stone in stones:
        stone.draw()

    # Sprawdzanie, czy ostatni kamień przestał się ruszać i gra dobiegła końca
    if stone_counter == 2 * max_stones_per_team and not any(stone.velocity != [0, 0] for stone in stones):
        game_over = True
        winner_text = determine_winner()

        # Aktualizacja wyników na podstawie zwycięzcy
        if "Green Wins" in winner_text:
            green_wins += 1
        elif "Yellow Wins" in winner_text:
            yellow_wins += 1

        # Po określeniu zwycięzcy, program restartuje grę
        pygame.time.delay(3000)  # Program najpierw czeka 3 sekundy
        restart_game()
        game_over = False
        winner_text = ""

    if game_over:
        winner_surf = font.render(winner_text, True, BLACK)
        screen.blit(winner_surf, (WIDTH // 2 - winner_surf.get_width() // 2, 10))

    # Program rysuje licznik kamieni
    green_score = sum(1 for stone in stones if stone.team == 0)
    yellow_score = sum(1 for stone in stones if stone.team == 1)
    green_score_surf = font.render(f"Green: {green_score}", True, GREEN)
    yellow_score_surf = font.render(f"Yellow: {yellow_score}", True, YELLOW)
    screen.blit(green_score_surf, (10, 130))
    screen.blit(yellow_score_surf, (10, 170))

    # Program rysuje tablicę wyników
    scoreboard_surf = font.render(f"Green Wins: {green_wins}  Yellow Wins: {yellow_wins}", True, BLACK)
    screen.blit(scoreboard_surf, (WIDTH - 400, 10))

    # Odświeżanie stanu interfejsu
    pygame.display.flip()

pygame.quit()
sys.exit()