import board
import time
import displayio

try:
    import adafruit_displayio_sh1107
    import adafruit_display_text.label
except ImportError:
    try:
        import adafruit_ssd1306
        import adafruit_display_text.label
    except ImportError:
        print("Required display libraries not found.")
        time.sleep(10)

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.layers import Layers
from kmk.extensions.display import Display
from kmk.modules.encoder import RotaryEncoderKeys

# --- CONFIGURATION ---
keyboard = KMKKeyboard()
keyboard.modules.append(Layers())

# 3x3 Key Matrix Pins: Rows are outputs (D0, D1, D2), Columns are inputs (D3, D6, D7)
keyboard.row_pins = (board.D0, board.D1, board.D2)
keyboard.col_pins = (board.D3, board.D6, board.D7)

# --- KEYMAPS ---
keyboard.keymaps = [
    # Layer 0: BASE LAYER
    [
        # Row 0
        KC.MPLY,      KC.VOLU,      KC.MUTE,
        # Row 1
        KC.LCTL(KC.C), KC.LCTL(KC.V), KC.LCTL(KC.Z),
        # Row 2
        KC.LGUI(KC.L), KC.LGUI(KC.R),  KC.TO(1),
    ],
    # Layer 1: FUNCTION LAYER
    [
        # Row 0
        KC.F1,        KC.F2,        KC.F3,
        # Row 1
        KC.F4,        KC.F5,        KC.F6,
        # Row 2
        KC.NO,        KC.NO,        KC.TO(0),
    ]
]

# --- EC11 ROTARY ENCODER SETUP ---
# Pins: D8 (A), D9 (B), D10 (Button)
encoder_ext = RotaryEncoderKeys(
    pins=(board.D8, board.D9, board.D10),
    codes=((KC.VOLU, KC.VOLD, KC.MUTE), # Layer 0 actions
           (KC.PGUP, KC.PGDN, KC.LSFT(KC.MUTE))), # Layer 1 actions
)
keyboard.extensions.append(encoder_ext)


# --- 0.91" OLED DISPLAY SETUP ---
displayio.release_displays()

# I2C Bus: D4=SCL, D5=SDA
i2c = board.I2C(scl=board.D4, sda=board.D5)
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
WIDTH = 128
HEIGHT = 32

try:
    display = adafruit_displayio_sh1107.SH1107(display_bus, width=WIDTH, height=HEIGHT, rotation=0)
except NameError:
    display = adafruit_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT, rotation=0)


display_ext = Display(
    display=display,
    width=WIDTH,
    height=HEIGHT,
    layer_names={
        0: "LAYER 0: BASE",
        1: "LAYER 1: FUNC",
    },
)

def draw_display_content(layer_name):
    text_group = displayio.Group()

    title_label = adafruit_display_text.label.Label(
        display_ext.terminal_font,
        text="Hack Club Pad",
        color=0xFFFFFF,
        x=2,
        y=10
    )
    text_group.append(title_label)

    status_label = adafruit_display_text.label.Label(
        display_ext.terminal_font,
        text=layer_name,
        color=0xFFFFFF,
        x=2,
        y=25
    )
    text_group.append(status_label)

    if display_ext.splash.groups:
        display_ext.splash.groups.clear()
    
    display_ext.splash.groups.append(text_group)


display_ext.on_layer_change = draw_display_content
keyboard.extensions.append(display_ext)

# --- START THE FIRMWARE ---
if __name__ == '__main__':
    time.sleep(0.5) 
    draw_display_content("LAYER 0: BASE")
    keyboard.go()