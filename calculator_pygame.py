import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 760
FPS = 60
BASE_WIDTH = 500
BASE_HEIGHT = 760

# Colors
BACKGROUND = (30, 60, 114)  # Deep blue
BACKGROUND_ACCENT = (42, 82, 152)  # Medium blue
CALCULATOR_BG = (255, 255, 255)  # White
DISPLAY_BG = (240, 244, 255)  # Light blue
DISPLAY_TEXT = (30, 60, 114)  # Dark blue
OPERATION_TEXT = (126, 34, 206)  # Purple

# Button Colors
NUM_BTN = (42, 82, 152)
NUM_BTN_HOVER = (30, 60, 114)
OPERATOR_BTN = (126, 34, 206)
OPERATOR_BTN_HOVER = (109, 27, 154)
DELETE_BTN = (255, 149, 0)
DELETE_BTN_HOVER = (245, 124, 0)
CLEAR_BTN = (244, 67, 54)
CLEAR_BTN_HOVER = (211, 47, 47)
EQUALS_BTN = (0, 200, 83)
EQUALS_BTN_HOVER = (0, 168, 77)
TAX_BTN = (2, 136, 209)
TAX_BTN_HOVER = (2, 119, 189)

# Set up display (resizable so user can maximize/fullscreen)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tax Calculator")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 48)
subtitle_font = pygame.font.Font(None, 20)
display_font = pygame.font.Font(None, 56)
operation_font = pygame.font.Font(None, 20)
button_font = pygame.font.Font(None, 28)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color

        # Shadow (slightly offset, darker)
        shadow_color = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 40))
        shadow_rect = self.rect.copy()
        shadow_rect.y += max(3, int(self.rect.height * 0.06))
        pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=max(6, int(self.rect.height * 0.15)))

        # Button on top
        pygame.draw.rect(surface, color, self.rect, border_radius=max(6, int(self.rect.height * 0.15)))

        text_surf = button_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.action:
                self.action()

class Calculator:
    def __init__(self):
        self.display = '0'
        self.first_value = None
        self.operator = None
        self.should_reset_display = False
        self.operation_display = ''
        self.buttons = []
        # Build layout according to current window size
        self.rebuild_layout(WINDOW_WIDTH, WINDOW_HEIGHT)

    def rebuild_layout(self, win_w, win_h):
        # compute uniform scale based on base size
        scale = min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT)

        # store scale and compute calculator container centered in window
        self.scale = scale
        calc_w = int(450 * scale)
        calc_h = int(660 * scale)
        calc_x = (win_w - calc_w) // 2
        calc_y = (win_h - calc_h) // 2
        self.calc_rect = pygame.Rect(calc_x, calc_y, calc_w, calc_h)

        # update fonts (global font objects)
        global title_font, subtitle_font, display_font, operation_font, button_font
        title_font = pygame.font.Font(None, max(24, int(48 * scale)))
        subtitle_font = pygame.font.Font(None, max(12, int(18 * scale)))
        display_font = pygame.font.Font(None, max(24, int(56 * scale)))
        operation_font = pygame.font.Font(None, max(12, int(16 * scale)))
        button_font = pygame.font.Font(None, max(14, int(28 * scale)))

        # base sizes (from original design) and offsets inside container
        base_btn_w = 85
        base_btn_h = 65
        base_gap = 14
        inner_left_offset = 10  # base_start_x (35) - container x (25) = 10
        inner_top_offset = 250  # base_start_y (300) - container y (50) = 250

        # scaled sizes
        btn_width = max(40, int(base_btn_w * scale))
        btn_height = max(30, int(base_btn_h * scale))
        gap = max(6, int(base_gap * scale))
        start_x = calc_x + int(inner_left_offset * scale)
        start_y = calc_y + int(inner_top_offset * scale)

        # display areas (store for drawing)
        da_x = calc_x + int(25 * scale)
        da_y = calc_y + int(100 * scale)
        da_w = int(400 * scale)
        da_h = int(120 * scale)
        self.display_area = pygame.Rect(da_x, da_y, da_w, da_h)
        self.display_rect = pygame.Rect(da_x + int(15 * scale), da_y + int(50 * scale), da_w - int(30 * scale), int(60 * scale))

        # rebuild buttons
        self.buttons = []

        # Row 1: 7,8,9,DEL
        x = start_x
        y = start_y
        self.buttons.append(Button(x, y, btn_width, btn_height, '7', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('7')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '8', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('8')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '9', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('9')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, 'DEL', DELETE_BTN, DELETE_BTN_HOVER, self.delete_last_digit))

        # Row 2: 4,5,6,-
        x = start_x
        y += btn_height + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '4', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('4')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '5', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('5')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '6', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('6')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '−', OPERATOR_BTN, OPERATOR_BTN_HOVER, lambda: self.set_operator('-')))

        # Row 3: 1,2,3,+
        x = start_x
        y += btn_height + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '1', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('1')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '2', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('2')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '3', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('3')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '+', OPERATOR_BTN, OPERATOR_BTN_HOVER, lambda: self.set_operator('+')))

        # Row 4: 0,.,Clear,=
        x = start_x
        y += btn_height + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '0', NUM_BTN, NUM_BTN_HOVER, lambda: self.add_number('0')))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '.', OPERATOR_BTN, OPERATOR_BTN_HOVER, self.add_decimal))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, 'Clear', CLEAR_BTN, CLEAR_BTN_HOVER, self.clear_display))
        x += btn_width + gap
        self.buttons.append(Button(x, y, btn_width, btn_height, '=', EQUALS_BTN, EQUALS_BTN_HOVER, self.calculate))

        # Row 5: Plus Tax full width
        y += btn_height + gap
        total_width = btn_width * 4 + gap * 3
        self.buttons.append(Button(start_x, y, total_width, btn_height, 'Plus Tax', TAX_BTN, TAX_BTN_HOVER, self.apply_tax))

    def add_decimal(self):
        if self.should_reset_display:
            self.display = '0.'
            self.should_reset_display = False
        else:
            if '.' not in self.display:
                self.display += '.'

    def delete_last_digit(self):
        if len(self.display) > 1:
            self.display = self.display[:-1]
        else:
            self.display = '0'

    def clear_display(self):
        self.display = '0'
        self.first_value = None
        self.operator = None
        self.should_reset_display = False
        self.operation_display = ''

    def set_operator(self, op):
        if self.operator is not None and not self.should_reset_display:
            self.calculate()

        self.first_value = float(self.display)
        self.operator = op
        self.should_reset_display = True
        self.operation_display = f"{self.first_value} {op}"

    def calculate(self):
        if self.operator is None or self.first_value is None:
            return

        second_value = float(self.display)
        result = 0

        if self.operator == '+':
            result = self.first_value + second_value
        elif self.operator == '-':
            result = self.first_value - second_value

        self.display = str(result)
        self.operator = None
        self.first_value = None
        self.should_reset_display = True
        self.operation_display = ''

    def apply_tax(self):
        try:
            current_value = float(self.display)
        except ValueError:
            return

        tax_rate = 0.10
        tax_amount = current_value * tax_rate
        total_with_tax = current_value + tax_amount

        self.display = f"{total_with_tax:.2f}"
        self.operator = None
        self.first_value = None
        self.should_reset_display = True
        self.operation_display = ''

    def draw(self, surface):
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.unicode.isdigit():
                self.add_number(event.unicode)
            elif event.key == pygame.K_PERIOD:
                self.add_decimal()
            elif event.key == pygame.K_BACKSPACE:
                self.delete_last_digit()
            elif event.key == pygame.K_c:
                self.clear_display()
            elif event.key == pygame.K_RETURN:
                self.calculate()
            elif event.key == pygame.K_PLUS:
                self.set_operator('+')
            elif event.key == pygame.K_MINUS:
                self.set_operator('-')

def draw_calculator_ui(surface, calculator):
    # Draw background gradient (simplified)
    surface.fill((30, 60, 114))

    win_w, win_h = surface.get_size()
    scale = getattr(calculator, 'scale', min(win_w / BASE_WIDTH, win_h / BASE_HEIGHT))

    # Use calculator's stored container rect (centered)
    calc_rect = getattr(calculator, 'calc_rect', pygame.Rect(int(25 * scale), int(50 * scale), int(450 * scale), int(660 * scale)))
    pygame.draw.rect(surface, CALCULATOR_BG, calc_rect, border_radius=max(12, int(20 * scale)))

    # Draw title (centered inside calculator container)
    title_text = title_font.render("Tax Calculator", True, (30, 60, 114))
    title_rect = title_text.get_rect(center=(calc_rect.centerx, calc_rect.top + max(20, int(24 * scale))))
    surface.blit(title_text, title_rect)

    # Draw subtitle (centered under title inside container)
    subtitle_text = subtitle_font.render("10% Tax Rate", True, (126, 34, 206))
    subtitle_rect = subtitle_text.get_rect(center=(calc_rect.centerx, title_rect.bottom + max(8, int(8 * scale))))
    surface.blit(subtitle_text, subtitle_rect)

    # Draw display area (from layout)
    display_area = getattr(calculator, 'display_area', pygame.Rect(int(50 * scale), int(150 * scale), int(400 * scale), int(120 * scale)))
    pygame.draw.rect(surface, DISPLAY_BG, display_area, border_radius=max(8, int(15 * scale)))
    pygame.draw.rect(surface, (232, 224, 245), display_area, border_radius=max(8, int(15 * scale)), width=max(1, int(2 * scale)))

    # Draw operation display
    if calculator.operation_display:
        op_text = operation_font.render(calculator.operation_display, True, OPERATION_TEXT)
        op_rect = op_text.get_rect(topright=(display_area.right - int(5 * scale), display_area.top + int(15 * scale)))
        surface.blit(op_text, op_rect)

    # Draw current display box and text
    display_rect = getattr(calculator, 'display_rect', pygame.Rect(display_area.x + int(15 * scale), display_area.y + int(50 * scale), display_area.width - int(30 * scale), int(60 * scale)))
    pygame.draw.rect(surface, CALCULATOR_BG, display_rect, border_radius=max(6, int(8 * scale)))
    pygame.draw.rect(surface, (224, 213, 245), display_rect, border_radius=max(6, int(8 * scale)), width=max(1, int(2 * scale)))

    display_text = display_font.render(calculator.display, True, DISPLAY_TEXT)
    text_rect = display_text.get_rect(right=display_rect.right - int(10 * scale), centery=display_rect.centery)
    surface.blit(display_text, text_rect)

    # Draw buttons (they were rebuilt on resize)
    calculator.draw(surface)

def main():
    global screen
    calculator = Calculator()
    fullscreen_mode = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                # Window resized (including maximize); update screen and layout
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                calculator.rebuild_layout(event.w, event.h)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                # Toggle fullscreen
                fullscreen_mode = not fullscreen_mode
                if fullscreen_mode:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
                w, h = screen.get_size()
                calculator.rebuild_layout(w, h)
            calculator.handle_event(event)

        draw_calculator_ui(screen, calculator)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
