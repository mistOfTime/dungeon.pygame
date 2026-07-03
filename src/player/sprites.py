# Eclipse Depths - Detailed pixel-art style sprite drawing functions

import pygame


def draw_player(surface: pygame.Surface, facing_angle: float = 0,
                is_dodging: bool = False, is_attacking: bool = False,
                hit_flash: bool = False) -> None:
    """Draw a detailed top-down player character (32x36)."""
    w, h = surface.get_size()
    surface.fill((0, 0, 0, 0))

    # Shadow
    shadow = pygame.Surface((w, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 60), (4, 1, w - 8, 6))
    surface.blit(shadow, (0, h - 6))

    # Cloak / body base
    cloak_col = (55, 70, 140) if not is_dodging else (80, 100, 200)
    pygame.draw.ellipse(surface, cloak_col, (5, 14, w - 10, h - 18))

    # Cloak highlight
    pygame.draw.ellipse(surface, (75, 95, 170), (8, 16, w - 16, 10))

    # Cloak trim
    pygame.draw.ellipse(surface, (30, 40, 90), (5, 14, w - 10, h - 18), 1)

    # Belt
    pygame.draw.rect(surface, (140, 100, 40), (7, h // 2 + 2, w - 14, 4), border_radius=2)
    pygame.draw.rect(surface, (200, 160, 60), (w // 2 - 3, h // 2 + 2, 6, 4))  # buckle

    # Arm (left)
    arm_col = (55, 70, 140)
    pygame.draw.ellipse(surface, arm_col, (1, h // 2 - 4, 7, 12))
    # Arm (right)
    pygame.draw.ellipse(surface, arm_col, (w - 8, h // 2 - 4, 7, 12))
    # Hands
    pygame.draw.circle(surface, (200, 160, 120), (4, h // 2 + 6), 3)
    pygame.draw.circle(surface, (200, 160, 120), (w - 4, h // 2 + 6), 3)

    # Weapon (sword) on right side when not attacking
    if not is_attacking:
        pygame.draw.rect(surface, (180, 180, 200), (w - 6, h // 2 - 8, 3, 14), border_radius=1)
        pygame.draw.rect(surface, (200, 170, 50), (w - 8, h // 2 - 2, 7, 3))  # crossguard
        pygame.draw.rect(surface, (160, 130, 60), (w - 5, h // 2 + 6, 2, 4))  # hilt
    else:
        # Raised sword
        pygame.draw.rect(surface, (200, 200, 220), (w - 4, h // 2 - 14, 3, 16), border_radius=1)
        pygame.draw.rect(surface, (220, 190, 60), (w - 7, h // 2 - 5, 7, 3))

    # Neck
    pygame.draw.circle(surface, (190, 150, 110), (w // 2, 14), 5)

    # Head
    head_col = (220, 185, 140)
    pygame.draw.circle(surface, head_col, (w // 2, 10), 9)
    # Head highlight
    pygame.draw.circle(surface, (240, 210, 170), (w // 2 - 2, 7), 4)

    # Hood / hair
    pygame.draw.arc(surface, (40, 30, 60),
                    pygame.Rect(w // 2 - 9, 1, 18, 14), 0, 3.14159, 3)
    pygame.draw.ellipse(surface, (50, 38, 72), (w // 2 - 8, 1, 16, 9))

    # Eyes - direction based
    import math
    angle_rad = math.radians(facing_angle)
    ex_off = int(math.cos(angle_rad) * 2)
    ey_off = int(math.sin(angle_rad) * 2)
    eye_x = w // 2 + ex_off
    eye_y = 10 + ey_off
    pygame.draw.circle(surface, (40, 40, 80), (eye_x - 3, eye_y), 2)
    pygame.draw.circle(surface, (40, 40, 80), (eye_x + 3, eye_y), 2)
    # Eye shine
    pygame.draw.circle(surface, (255, 255, 255), (eye_x - 2, eye_y - 1), 1)
    pygame.draw.circle(surface, (255, 255, 255), (eye_x + 4, eye_y - 1), 1)

    # Feet
    pygame.draw.ellipse(surface, (40, 35, 60), (6, h - 10, 8, 6))
    pygame.draw.ellipse(surface, (40, 35, 60), (w - 14, h - 10, 8, 6))

    # Hit flash overlay
    if hit_flash:
        flash = pygame.Surface((w, h), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 180))
        surface.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
