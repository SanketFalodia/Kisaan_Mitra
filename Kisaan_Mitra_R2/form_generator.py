import json
import os
from datetime import datetime
from typing import Dict, List

# Simple file-based database for call logs
CALL_LOGS_FILE = "call_logs/call_history.json"

def ensure_logs_file():
    """Create call logs file if doesn't exist"""
    os.makedirs("call_logs", exist_ok=True)
    if not os.path.exists(CALL_LOGS_FILE):
        with open(CALL_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def save_call_log(phone: str, user_query: str, schemes: List[str], choice: str, timestamp: str = None):
    """Save call log to JSON file"""
    ensure_logs_file()
    
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    log_entry = {
        "phone": phone,
        "user_query": user_query,
        "schemes_offered": schemes,
        "user_choice": choice,  # "yes", "no", "skip"
        "timestamp": timestamp
    }
    
    with open(CALL_LOGS_FILE, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    logs.append(log_entry)
    
    with open(CALL_LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Call log saved: {log_entry}")
    return log_entry

def get_farmer_profile(phone: str) -> Dict:
    """Fetch farmer's previous interactions"""
    ensure_logs_file()
    
    with open(CALL_LOGS_FILE, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    farmer_logs = [log for log in logs if log['phone'] == phone]
    
    return {
        "phone": phone,
        "total_calls": len(farmer_logs),
        "schemes_interested": list(set(
            scheme for log in farmer_logs 
            for scheme in log['schemes_offered']
        )),
        "last_call": farmer_logs[-1]['timestamp'] if farmer_logs else None,
        "interaction_history": farmer_logs
    }

def generate_form_html(phone: str, scheme_name: str, scheme_id: str) -> str:
    """
    Generate HTML form for scheme application
    Pre-filled with phone number
    """
    html_form = f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{scheme_name} - आवेदन फॉर्म</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #333;
            }}
            input, select, textarea {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
                font-size: 14px;
            }}
            textarea {{
                resize: vertical;
                min-height: 100px;
            }}
            button {{
                width: 100%;
                padding: 12px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #229954;
            }}
            .scheme-info {{
                background-color: #ecf0f1;
                padding: 15px;
                border-left: 4px solid #3498db;
                margin-bottom: 20px;
            }}
            .required {{
                color: red;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌾 {scheme_name}</h1>
            <h2>आवेदन फॉर्म</h2>
            
            <div class="scheme-info">
                <p><strong>योजना ID:</strong> {scheme_id}</p>
                <p>कृपया नीचे दिए गए सभी विवरण सही से भरें।</p>
            </div>
            
            <form method="POST" action="/submit-form">
                <input type="hidden" name="scheme_id" value="{scheme_id}">
                <input type="hidden" name="scheme_name" value="{scheme_name}">
                
                <div class="form-group">
                    <label for="phone">मोबाइल नंबर <span class="required">*</span></label>
                    <input type="tel" id="phone" name="phone" value="{phone}" required>
                </div>
                
                <div class="form-group">
                    <label for="name">पूरा नाम <span class="required">*</span></label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="age">आयु <span class="required">*</span></label>
                    <input type="number" id="age" name="age" min="18" required>
                </div>
                
                <div class="form-group">
                    <label for="aadhaar">आधार नंबर <span class="required">*</span></label>
                    <input type="text" id="aadhaar" name="aadhaar" placeholder="12 अंक" required>
                </div>
                
                <div class="form-group">
                    <label for="district">जिला <span class="required">*</span></label>
                    <select id="district" name="district" required>
                        <option value="">-- चुनें --</option>
                        <option value="almora">अल्मोड़ा</option>
                        <option value="bageshwar">बागेश्वर</option>
                        <option value="chamoli">चमोली</option>
                        <option value="champawat">चम्पावत</option>
                        <option value="dehradun">देहरादून</option>
                        <option value="haridwar">हरिद्वार</option>
                        <option value="nainital">नैनीताल</option>
                        <option value="pauri">पौड़ी</option>
                        <option value="pithoragarh">पिथौरागढ़</option>
                        <option value="rudraprayag">रुद्रप्रयाग</option>
                        <option value="tehri">टेहरी</option>
                        <option value="udham_singh_nagar">उधम सिंह नगर</option>
                        <option value="uttarkashi">उत्तरकाशी</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="village">गांव का नाम <span class="required">*</span></label>
                    <input type="text" id="village" name="village" required>
                </div>
                
                <div class="form-group">
                    <label for="land_size">भूमि का आकार (एकड़) <span class="required">*</span></label>
                    <input type="number" id="land_size" name="land_size" step="0.1" required>
                </div>
                
                <div class="form-group">
                    <label for="crop_type">फसल का प्रकार <span class="required">*</span></label>
                    <select id="crop_type" name="crop_type" required>
                        <option value="">-- चुनें --</option>
                        <option value="wheat">गेहूं</option>
                        <option value="rice">चावल</option>
                        <option value="corn">मक्का</option>
                        <option value="apple">सेब</option>
                        <option value="potato">आलू</option>
                        <option value="onion">प्याज</option>
                        <option value="vegetables">सब्जियां</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="bank_account">बैंक खाता संख्या <span class="required">*</span></label>
                    <input type="text" id="bank_account" name="bank_account" required>
                </div>
                
                <div class="form-group">
                    <label for="additional_info">अतिरिक्त जानकारी</label>
                    <textarea id="additional_info" name="additional_info" placeholder="यदि कोई विशेष जानकारी है तो यहाँ लिखें"></textarea>
                </div>
                
                <button type="submit">आवेदन जमा करें</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html_form

def save_form_submission(phone: str, scheme_id: str, form_data: Dict) -> bool:
    """Save submitted form data"""
    os.makedirs("form_submissions", exist_ok=True)
    
    submission = {
        "phone": phone,
        "scheme_id": scheme_id,
        "form_data": form_data,
        "submitted_at": datetime.now().isoformat(),
        "status": "pending_review"
    }
    
    filename = f"form_submissions/{phone}_{scheme_id}_{datetime.now().timestamp()}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(submission, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Form submission saved: {filename}")
    return True