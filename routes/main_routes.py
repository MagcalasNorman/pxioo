from flask import Blueprint, jsonify, request, send_from_directory, current_app
from services.data_service import DataService, BeerDataService
from services.chat_data_service import ChatDataService
from services.pixoo_service import PixooService
from services.dify_service import DifyService
from themes.flags_attendance import FlagsAttendanceTheme
from themes.beer_consumed import BeerConsumedTheme
from themes.tokens_consumed import TokensConsumedTheme
from datetime import datetime
from config import Config
import time
import json

main_bp = Blueprint('main', __name__)
current_theme = None  # For theme-based animations

THEME_MAP = {
    "flags": FlagsAttendanceTheme,
    "beer": BeerConsumedTheme,
    "ai": TokensConsumedTheme,
}

# Dashboard Routes
@main_bp.route("/")
def serve_dashboard():
    return send_from_directory("views", "dashboard.html")

@main_bp.route("/api/kpi-data", methods=["GET"])
def get_kpi_data():
    theme = request.args.get("theme", "flags")
    if theme == "ai":
        service = ChatDataService()
        messages_sent, tokens_used, total_price = service.get_latest_stats()
        return jsonify({
            "messages_sent": messages_sent,
            "tokens_used": tokens_used,
            "total_price": total_price,
            'currency': request.args.get('currency', 'USD')
        })
    else:
        service = DataService if theme == "flags" else BeerDataService
        return jsonify(service.read_data())

@main_bp.route("/api/update-kpis", methods=["POST"])
def update_kpis():
    data = request.json
    theme = data.pop("theme", "flags")
    currency = data.get("currency", "USD")  # Get currency from the request data

    current_app.logger.debug(f"Received data: {data}, Currency: {currency}")  # Debugging log

    # Select appropriate data service
    if theme == "ai":
        service = ChatDataService()
    else:
        service = DataService if theme == "flags" else BeerDataService
    service.write_data(data)
    
    # Update Pixoo display
    update_pixoo_display(theme, {**data, "currency": currency})  # Pass currency to Pixoo
    return jsonify(status="success", data=data)

# AI Chat Routes
@main_bp.route('/api/ai-chat', methods=['POST'])
def ai_chat():
    try:
        request_data = request.get_json()
        current_app.logger.debug(f"Received AI Chat request: {request_data}")  # Debugging log
        currency = request_data.get('currency', 'USD')
        user_message = request_data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        dify_service = DifyService(
            api_key=current_app.config['DIFY_API_KEY'],
            api_url=current_app.config['DIFY_API_URL']
        )
        chat_service = ChatDataService()
        
        start_time = time.time()
        response = dify_service.send_message(user_message)
        
        if response.status_code != 200:
            return jsonify({
                'error': f'Dify API returned {response.status_code}',
                'details': response.text
            }), 500

        # Process streaming response
        collected_answer = []
        current_tokens = 0
        current_price = 0.0
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    try:
                        event_data = json.loads(decoded_line[5:])
                        if event_data.get('event') == 'message':
                            collected_answer.append(event_data.get('answer', ''))
                        elif event_data.get('event') == 'message_end':
                            metadata = event_data.get('metadata', {})
                            usage = metadata.get('usage', {})
                            current_tokens = usage.get('total_tokens', 0)
                            
                            # Simplified price extraction
                            price_str = str(usage.get('total_price', '0.0'))
                            try:
                                current_price = float(price_str.replace('$', '').replace(',', ''))
                            except ValueError:
                                current_price = 0.0

                    except (json.JSONDecodeError, ValueError) as e:
                            current_app.logger.warning(f"Failed to parse event data: {e}")
                            continue

        final_answer = " ".join(collected_answer).strip()
        if not final_answer:
            return jsonify({'error': 'Empty response from AI'}), 500

        # Update stats and Pixoo
        end_time = time.time
        messages_sent, tokens_used, total_price = chat_service.get_latest_stats()
        messages_sent += 1
        tokens_used += current_tokens
        total_price += current_price
        
        current_app.logger.debug(f"Saving: messages={messages_sent}, tokens={tokens_used}, price={total_price}")
        
        chat_service.save_chat_data(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            messages_sent,
            tokens_used,
            total_price
        )

        # Update Pixoo with new stats
        update_pixoo_display("ai", {
            "messages_sent": messages_sent,
            "tokens_used": tokens_used,
            "total_price": total_price,
            "currency": currency,
        })

        return jsonify({
             'response': final_answer,
            'tokens_used': tokens_used,
            'messages_sent': messages_sent,
            'total_price': round(total_price, 6),
            'currency': currency  # Make sure to return the currency
        })

    except Exception as e:
        current_app.logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def update_pixoo_display(theme, data):
    """Update Pixoo display with the current theme and data"""
    global current_theme
    current_theme = THEME_MAP[theme]()
    pixoo = PixooService()

    # Debug logs to verify data
    current_app.logger.debug(f"Updating Pixoo display with data: {data}")
    current_app.logger.debug(f"Currency being used: {data.get('currency', 'USD')}")

    # Ensure currency is included in the data
    if 'currency' not in data:
        data['currency'] = 'USD'  # Default if not provided
        current_app.logger.warning("Currency not provided, defaulting to USD")

    current_app.logger.debug(f"Display update - Full data: {data}")
    current_app.logger.debug(f"Updating Pixoo display with data: {data}")
    current_app.logger.debug(f"Currency being used: {data.get('currency')}")

    static_img = current_theme.render_static(data)
    pixoo.draw_image(static_img)
    
    def animation_loop():
        frame_index = 0
        while not pixoo.stop_animation:
            animated_frame = current_theme.animate_frame(data, frame_index, static_img)
            pixoo.draw_image(animated_frame)
            frame_index += 1
            time.sleep(Config.ANIMATION_FRAME_DELAY)
    
    pixoo.start_animation(animation_loop)