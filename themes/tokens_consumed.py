from PIL import Image, ImageDraw
from themes.base_theme import BaseTheme
from config import Config

class TokensConsumedTheme(BaseTheme):
    
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'AUD': 'A$',
        'EUR': '€',
        'PHP': 'P',
        'INR': 'R',
        'COP': '$'  # Colombian peso uses same symbol as USD
    }

    def get_name(self):
        return "tokens_consumed"

    def render_static(self, data):
        bg_color = self.parse_color(data.get('background_color', '0,0,0'))  # Black default
        text_color = self.parse_color(data.get('text_color', '0,255,0'))   # Green text
        
        img = Image.new("RGBA", (Config.PIXOO_SCREEN_SIZE, Config.PIXOO_SCREEN_SIZE), bg_color)
        draw = ImageDraw.Draw(img)

        # Draw AI icon (replace with your own frames if desired)
        self._draw_ai_icon(draw, img.size)

        # Draw stats
        self._draw_stats(draw, data, text_color)
        return img

    def _draw_ai_icon(self, draw, img_size):
        """Simple AI icon (a robot face) - moved up by 4 pixels"""
        width, height = img_size
        # Head (moved up by 4 pixels)
        draw.rectangle([(10, 1), (width-10, height-30)], outline=(0, 255, 0), width=1)
        # Eyes (moved up by 4 pixels)
        draw.ellipse([(20, 10-4), (30, 20-4)], fill=(0, 255, 0))  # Left eye
        draw.ellipse([(width-30, 10-4), (width-20, 20-4)], fill=(0, 255, 0))  # Right eye
        # Mouth (smile, moved up by 4 pixels)
        draw.arc([(25, 10-4), (width-25, 35-4)], start=0, end=180, fill=(0, 255, 0), width=1)

    def _draw_stats(self, draw, data, text_color):
        messages = self.format_kpi(data.get("messages_sent", 0))
        tokens = self.format_kpi(data.get("tokens_used", 0))
        
        raw_price = float(data.get('total_price', 0))
        currency = data.get('currency', 'USD')
        
        print(f"Drawing stats - Currency: {currency}, Price: {raw_price}")  # Debug log

        # Apply exchange rate if needed
        exchange_rates = {
            'USD': 1.0,
            'AUD': 1.50,
            'PHP': 56.23,
            'INR': 83.33,
            'COP': 4165.0
        }
        
        converted_price = raw_price * exchange_rates.get(currency, 1.0)
        symbol = self.CURRENCY_SYMBOLS.get(currency, currency)

        # Format based on currency type
        if currency in ['USD', 'AUD', 'EUR']:
            if converted_price < 0.1:
                price = f"{symbol}{converted_price:.3f}"[:8]
            else:
                price = f"{symbol}{converted_price:.2f}"[:8]
        else:
            price = f"{symbol}{int(round(converted_price))}"[:8]

        # Position text
        draw.text((2, 37), f"M:{messages}", fill=text_color, font=self.font)
        draw.text((2, 47), f"T:{tokens}", fill=text_color, font=self.font)
        draw.text((2, 57), f"C:{price}", fill=text_color, font=self.font)


    def animate_frame(self, data, frame_index, static_bg):
        """Improved blinking eyes animation"""
        animated = static_bg.copy()
        draw = ImageDraw.Draw(animated)
        width, height = animated.size
        
        # Blinking logic - more visible animation
        if frame_index % 20 < 3:  # Blink for 3 frames every 20 frames
            # Closed eyes (thicker horizontal lines)
            draw.line([(20, 15-4), (30, 15-4)], fill=(0, 255, 0), width=3)
            draw.line([(width-30, 15-4), (width-20, 15-4)], fill=(0, 255, 0), width=3)
        else:
            # Open eyes (normal state)
            draw.ellipse([(20, 10-4), (30, 20-4)], fill=(0, 255, 0))  # Left eye
            draw.ellipse([(width-30, 10-4), (width-20, 20-4)], fill=(0, 255, 0))  # Right eye
            
        # Always draw the mouth (unchanged)
        draw.arc([(25, 10-4), (width-25, 35-4)], start=0, end=180, fill=(0, 255, 0), width=1)
        
        return animated