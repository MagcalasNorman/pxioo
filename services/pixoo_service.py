from threading import Thread, Lock
from PIL import Image
from pixoo import Pixoo
from config import Config

class PixooService:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self):
        self.pixoo = Pixoo(Config.PIXOO_HOST, Config.PIXOO_SCREEN_SIZE, Config.PIXOO_DEBUG)
        self.animation_thread = None
        self.stop_animation = False
        self.animation_lock = Lock()

    def start_animation(self, target, args=()):
        with self.animation_lock:
            if self.animation_thread:
                self.stop_animation = True
                self.animation_thread.join()
                
            self.stop_animation = False
            self.animation_thread = Thread(target=target, args=args, daemon=True)
            self.animation_thread.start()

    def draw_image(self, image):
        try:
            self.pixoo.draw_image(image.convert("RGB"))
            self.pixoo.push()
            print("Image sent to device")
        except Exception as e:
            print(f"Error updating Pixoo display: {e}")
    
    def draw_tokens_used(self, tokens_used):
        try:
            self.clear()
            
            # Background gradient
            for y in range(64):
                self.set_color(0, 0, min(255, y*4))
                self.draw_line((0, y), (63, y))
            
            # Main text
            self.set_color(255, 255, 255)
            self.draw_text("AI RESPONSE", (5, 5), 1)
            
            # Tokens display
            self.set_color(0, 255, 0)
            self.draw_text(f"TOKENS USED:", (5, 20), 1)
            self.set_color(255, 255, 0)
            self.draw_text(f"{tokens_used}", (5, 30), 2)  # Bigger font
            
            # Visual indicator
            token_bar = min(63, int(tokens_used / 10))  # Scale for display
            self.set_color(255, 0, 0)
            self.draw_filled_rectangle((0, 50), (token_bar, 58))
            
            self.push()
            return True
        except Exception as e:
            print(f"Error drawing tokens: {e}")
            return False