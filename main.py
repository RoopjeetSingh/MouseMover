import pyautogui
import pygame
import random

pygame.init()


def draw_bordered_rounded_rect(surface, rect, color, border_color, corner_radius, border_thickness):
    rect_tmp = pygame.Rect(rect)

    if border_thickness:
        if corner_radius <= 0:
            pygame.draw.rect(surface, border_color, rect_tmp)
        else:
            pygame.draw.rect(surface, border_color, rect_tmp, border_radius=corner_radius)

        rect_tmp.inflate_ip(-2 * border_thickness, -2 * border_thickness)
        inner_radius = corner_radius - border_thickness + 1
    else:
        inner_radius = corner_radius

    if inner_radius <= 0:
        pygame.draw.rect(surface, color, rect_tmp)
    else:
        pygame.draw.rect(surface, color, rect_tmp, border_radius=inner_radius)


class Button:
    """A fairly straight forward button class."""

    def __init__(self, master, position, bg=(255, 255, 255), command=None, text=None,
                 font=pygame.font.Font(None, 36), call_on_release=True,
                 highlight_color=None, active_background=None, fg=(0, 0, 0), hover_font_color=None,
                 active_foreground=None, click_sound=None, hover_sound=None, image=None, text_position=None,
                 image_position=None, border_radius=0, border_color=None, image_align="bottom", fill_bg=True,
                 bd: int = 7, state: bool | str = True, disabled_image=None, disabled_color=None,
                 disabled_border_color=None, alpha=255, justify_text: str = "center", width=0, height=0,
                 underline=False, bold=False, italic=False, **kwargs):
        self.master = master
        self.image: pygame.Surface = image
        self.alpha = alpha
        self.text: pygame.Surface = text
        self.font = font
        self.call_on_release = call_on_release
        self.hover_color = highlight_color
        self.clicked_color = active_background
        self.font_color = fg
        self.hover_font_color = hover_font_color
        self.clicked_font_color = active_foreground
        self.click_sound = click_sound
        self.hover_sound = hover_sound
        self.image_original = image
        self.text_position = text_position
        self.image_position = image_position
        self.border_radius = border_radius
        self.border_color = border_color
        self.border_color_copy = border_color
        self.image_align = image_align
        self.image_copy = self.image_original
        self.fill_bg = fill_bg
        self.border_thickness = bd
        if isinstance(state, bool):
            self.state_disabled = not state
        else:
            self.state_disabled = True if state == "disabled" else False
        self.disabled_image = disabled_image
        self.disabled_color = disabled_color
        self.disabled_border_color = disabled_border_color
        self.justify = justify_text
        self.kwargs = kwargs
        self.value_from_function = None
        if underline:
            font.set_underline(True)
        if bold:
            font.set_bold(True)
        if italic:
            font.set_italic(True)
        if self.image_original:
            if not isinstance(self.image_original, list):
                self.image_copy = pygame.transform.scale(
                    self.image_original,
                    (0.87 * self.image_original.get_width(), 0.76 * self.image_original.get_height()))
            else:
                self.image_copy = [pygame.transform.scale(
                    image, (0.87 * image.get_width(), 0.76 * image.get_height()))
                    for image in self.image_original]
        self.render_text()
        if width and height:
            self.rect_original = pygame.Rect(position[0], position[1], width, height)
        elif self.image and not self.text:
            if isinstance(self.image_original, list):
                max_width = width or max(self.image_original, key=lambda img: img.get_width())
                max_height = height or max(self.image_original, key=lambda img: img.get_height())
            else:
                max_width = width or self.image.get_width()
                max_height = height or self.image.get_height()
            self.rect_original = pygame.Rect(position[0], position[1], max_width, max_height)
        elif self.text and not self.image:
            max_width = width or self.text.get_width() + 15
            max_height = height or self.text.get_height() + 10
            self.rect_original = pygame.Rect(position[0], position[1], max_width, max_height)
        elif self.text and self.image:
            max_height = self.text.get_height() + self.image.get_height() + 10
            max_width = max(self.text.get_width(), self.image.get_width()) + 10
            self.rect_original = pygame.Rect(position[0], position[1], width or max_width, height or max_height)
        else:
            self.rect_original = pygame.Rect(position[0], position[1], width or 100, height or 50)

        self.rect = self.rect_original.copy()
        self.rect_inflated = self.rect_original.inflate(-0.13 * self.rect_original.w,
                                                        -0.24 * self.rect_original.h)
        self.text_original = self.text.copy()
        self.text_inflated = pygame.transform.scale(self.text_original, ((1-0.13)*self.text_original.get_width(),
                                                                         (1-0.24)*self.text_original.get_height()))
        self.color = bg
        self.color_copy = bg
        self.function = command
        self.clicked = False
        self.hovered = False
        self.hover_text = None
        self.clicked_text = None

    def move(self, x_add=0, y_add=0):
        """
        This function can be used to move the button
        :param x_add: This is the number of pixels to add to the x position
        :param y_add: This is the number of pixels to add to the y position
        """
        self.rect_original.x += x_add
        self.rect_inflated.x += x_add
        self.rect_original.y += y_add
        self.rect_inflated.y += y_add

    def render_text(self):
        """Pre render the button text.
        If for some reason you change the text you must call the render_text method"""
        if self.text:
            if self.hover_font_color:
                color = self.hover_font_color
                self.hover_text = self.font.render(self.text, True, color)
            if self.clicked_font_color:
                color = self.clicked_font_color
                self.clicked_text = self.font.render(self.text, True, color)
            self.text: pygame.Surface = self.font.render(self.text, True, self.font_color)

    def check_event(self, event):
        """
        This is the method that checks if the player is pressing a button. It should be called inside the for loop
        that has all the events eg.
        for event in pygame.event.get():
            button.check_event(event)
        :param event: event is the event obtained from pygame.event.get(), it is not the complete list and hence this
                      function should be called inside the for loop
        """
        if not self.state_disabled:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.clicked = True
                    if not self.call_on_release and self.function:
                        if self.kwargs:
                            self.value_from_function = self.function(self.kwargs)
                        else:
                            self.value_from_function = self.function()
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.function and self.clicked and self.call_on_release:
                    if self.kwargs:
                        self.value_from_function = self.function(self.kwargs)
                    else:
                        self.value_from_function = self.function()
                self.clicked = False

    def update(self):
        """Update needs to be called every frame in the main loop."""
        color = self.color
        self.image = self.image_original
        self.rect = self.rect_original
        self.color = self.color_copy
        self.border_color = self.border_color_copy
        self.text = self.text_original

        # The next block of code checks mouse hovering, I wanted to create a method for this but then the user
        # of this library would be disturbed with an unnecessary method
        if self.rect.collidepoint(pygame.mouse.get_pos()) and not self.state_disabled:
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:
            self.hovered = False
        if self.state_disabled and self.disabled_image:
            self.image = self.disabled_image
        if self.state_disabled and self.disabled_color:
            self.color = self.disabled_color
        if self.state_disabled and self.disabled_border_color:
            self.border_color = self.disabled_border_color

        if self.clicked:
            if self.clicked_color:
                color = self.clicked_color
                if self.clicked_font_color:
                    self.text = self.clicked_text
            self.image = self.image_copy
            self.rect = self.rect_inflated
            self.text = self.text_inflated
        elif self.hovered and self.hover_color:
            color = self.hover_color
            if self.hover_font_color:
                self.text = self.hover_text

        if self.image and not isinstance(self.image, list):
            self.image.set_alpha(self.alpha)
        elif isinstance(self.image, list):
            for img in self.image:
                img.set_alpha(self.alpha)
        if self.text:
            self.text.set_alpha(self.alpha)
        if self.border_radius and self.border_color and not self.clicked:
            draw_bordered_rounded_rect(self.master, self.rect, color, self.border_color, self.border_radius,
                                       self.border_thickness)
        elif self.border_radius:
            pygame.draw.rect(self.master, color, self.rect, border_radius=self.border_radius)
        elif self.fill_bg:
            self.master.fill(pygame.Color("black"), self.rect)
            pygame.draw.rect(self.master, self.color, self.rect.inflate(-4, -4))

        if self.text and not self.text_position and not self.image:
            if self.justify == "left":
                text_rect = self.text.get_rect(midleft=(self.rect.midleft[0] + 3, self.rect.midleft[1]))
            elif self.justify == "right":
                text_rect = self.text.get_rect(midright=(self.rect.midright[0] - 3, self.rect.midright[1]))
            else:
                text_rect = self.text.get_rect(center=self.rect.center)
            self.master.blit(self.text, text_rect)
        elif self.text and self.text_position:
            self.master.blit(self.text, (self.rect.x + self.text_position[0], self.rect.y + self.text_position[1]))

        if self.image and self.image_position:
            if not isinstance(self.image, list):
                self.master.blit(self.image,
                                 (self.rect.x + self.image_position[0], self.rect.y + self.image_position[1]))
            else:
                for index, image in enumerate(self.image):
                    self.master.blit(image, (
                        self.rect.x + self.image_position[index][0], self.rect.y + self.image_position[index][1]))
        elif self.image and not self.text:
            image_rect = self.image.get_rect(center=self.rect.center)
            self.master.blit(self.image, image_rect)
        elif self.image and self.image_align == "bottom" and self.text:
            image_rect = self.image.get_rect()
            image_rect.centerx = self.rect.centerx
            image_rect.bottom = self.rect.bottom - (
                    self.rect.height - self.image.get_height() - self.text.get_height() - 5) / 2
            text_rect = self.text.get_rect()
            text_rect.centerx = self.rect.centerx
            text_rect.top = self.rect.y + (self.rect.height - self.image.get_height() - self.text.get_height() - 5) / 2
            self.master.blit(self.image, image_rect)
            self.master.blit(self.text, text_rect)
        elif self.image and self.image_align == "top" and self.text:
            image_rect = self.image.get_rect()
            image_rect.centerx = self.rect.centerx
            text_rect = self.text.get_rect()
            text_rect.centerx = self.rect.centerx
            image_rect.top = self.rect.y + (self.rect.height - self.image.get_height() - self.text.get_height()) / 2
            text_rect.bottom = self.rect.y + self.rect.height - (
                    self.rect.height - self.image.get_height() - self.text.get_height()) / 2
            self.master.blit(self.image, image_rect)
            self.master.blit(self.text, text_rect)


def start():
    global move
    move = True


def stop():
    global move
    move = False


move = False
root = pygame.display.set_mode((300, 50))
clock = pygame.time.Clock()

start_btn = Button(root, (0, 0), width=150, height=50, text="Start", command=start, bg=(0, 0, 0), fg=(255, 255, 255))
stop_btn = Button(root, (150, 0), width=150, height=50, text="Stop", command=stop, bg=(0, 0, 0), fg=(255, 255, 255))
button_list = [start_btn, stop_btn]

while True:
    root.fill("black")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        for i in button_list:
            i.check_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                move = True
            if event.key == pygame.K_q:
                move = False

    for i in button_list:
        i.update()

    if move:
        pyautogui.moveTo(random.randint(150, 1700), random.randint(150, 900), 1)
        
    pygame.display.update()
    clock.tick(60)
