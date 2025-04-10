from datetime import datetime
from pathlib import Path
import csv

class ChatDataService:
    def __init__(self, data_file='dataset/chat_data.csv'):
        self.data_file = Path(data_file)
        self._ensure_data_file()
        
    def _ensure_data_file(self):
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Messages Sent', 'Tokens Used', 'Total Price'])
    
    def save_chat_data(self, timestamp, messages_sent, tokens_used, total_price):
        with open(self.data_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                messages_sent,
                tokens_used,
                f"{float(total_price):.6f}"  # Simple float formatting
            ])
    
    def get_latest_stats(self):
        try:
            if not self.data_file.exists():
                return 0, 0, 0.0
                
            with open(self.data_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    return (
                        int(last_row[1]),  # messages_sent
                        int(last_row[2]),  # tokens_used
                        float(last_row[3])  # total_price
                    )
        except Exception as e:
            print(f"Error reading stats: {e}")
        return 0, 0, 0.0