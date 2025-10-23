#!/usr/bin/env python3
"""
AdShare Symbol Game Solver Pro - Telegram Bot Version
With credit monitoring and bot commands
"""

import os
import time
import random
import logging
import re
import threading
import math
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
CONFIG = {
    # Timing Configuration
    'base_delay': 3,
    'random_delay': True,
    'min_delay': 2,
    'max_delay': 5,
    
    # Behavioral Patterns
    'enable_human_patterns': True,
    'click_position_variation': True,
    'occasional_misses': False,
    'miss_rate': 0.00,
    
    # Rate Limiting
    'max_clicks_per_minute': 15,
    'max_session_length': 1800,  # 30 minutes
    'cooldown_periods': True,
    
    # Accuracy Settings
    'always_perfect_accuracy': True,
    'minimum_confidence': 0.90,
    'retry_failed_matches': True,
    
    # Performance
    'disable_images': True,
    'disable_videos': True,
    'disable_audio': True,
    'block_popups': True,
    
    # Telegram & Monitoring
    'telegram_token': "8225236307:AAF9Y2-CM7TlLDFm2rcTVY6f3SA75j0DFI8",
    'credit_check_interval': 1800,  # 30 minutes
    'auto_restart_hours': 11
}

class AdvancedSymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.email = os.getenv('ADSHARE_EMAIL', 'loginallapps@gmail.com')
        self.password = os.getenv('ADSHARE_PASSWORD', '@Sd2007123')
        self.telegram_chat_id = None
        
        # State Management
        self.state = {
            'click_count': 0,
            'last_click_time': 0,
            'session_start_time': time.time(),
            'is_running': False,
            'total_solved': 0,
            'consecutive_rounds': 0,
            'last_action_time': time.time(),
            'is_in_cooldown': False,
            'consecutive_fails': 0,
            'status': 'stopped',
            'last_error': None,
            'last_credits': 'Unknown',
            'monitoring_active': False
        }
        
        self.solver_thread = None
        self.monitoring_thread = None
        self.setup_logging()
        self.setup_telegram()
        self.logger.info("🚀 Advanced Symbol Game Solver Pro with Telegram Bot Initialized")
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_telegram(self):
        """Setup Telegram bot and get chat ID"""
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/getUpdates"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                updates = response.json()
                if updates['result']:
                    self.telegram_chat_id = updates['result'][-1]['message']['chat']['id']
                    self.logger.info(f"✅ Telegram Chat ID: {self.telegram_chat_id}")
                    self.send_telegram("🤖 <b>AdShare Solver Bot Started!</b>\nUse commands to control the solver.")
                    return True
            self.logger.error("❌ No Telegram messages found. Send a message to your bot first.")
            return False
        except Exception as e:
            self.logger.error(f"❌ Telegram setup failed: {e}")
            return False
    
    def send_telegram(self, text, parse_mode='HTML'):
        """Send message to Telegram"""
        if not self.telegram_chat_id:
            self.logger.error("❌ No Telegram chat ID configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"❌ Telegram send failed: {e}")
            return False
    
    def setup_browser(self):
        """Setup Chrome with optimization"""
        self.logger.info("🌐 Starting Chrome with optimization...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless=new")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=256")
        
        # Block media
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
                'plugins': 2,
                'popups': 2,
                'geolocation': 2,
                'notifications': 2,
                'media_stream': 2,
            }
        }
        options.add_experimental_option('prefs', prefs)
        options.add_argument("--window-size=1200,800")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.set_page_load_timeout(30)
            self.logger.info("✅ Chrome started successfully!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            self.state['last_error'] = str(e)
            return False

    def get_smart_delay(self):
        """Get intelligent delay"""
        if not CONFIG['random_delay']:
            return CONFIG['base_delay']
        
        session_duration = time.time() - self.state['session_start_time']
        base = CONFIG['base_delay']
        
        if session_duration > 900:  # After 15 minutes
            base += 1
        
        random_variation = random.uniform(CONFIG['min_delay'] - base, CONFIG['max_delay'] - base)
        return max(CONFIG['min_delay'], base + random_variation)

    def is_behavior_suspicious(self):
        """Rate limiting check"""
        now = time.time()
        clicks_per_minute = (self.state['click_count'] / ((now - self.state['session_start_time']) / 60)) if (now - self.state['session_start_time']) > 0 else 0
        
        if clicks_per_minute > CONFIG['max_clicks_per_minute']:
            return True
        if now - self.state['session_start_time'] > CONFIG['max_session_length']:
            return True
        return False

    def start_cooldown(self, duration=30):
        """Start cooldown period"""
        self.state['is_in_cooldown'] = True
        self.state['status'] = 'cooldown'
        self.logger.info(f"😴 Cooldown activated for {duration}s")
        
        def end_cooldown():
            time.sleep(duration)
            self.state['is_in_cooldown'] = False
            self.state['status'] = 'running' if self.state['is_running'] else 'stopped'
        
        threading.Thread(target=end_cooldown, daemon=True).start()

    def force_login(self):
        """Login with dynamic password detection"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🔐 Login attempt {attempt + 1}")
                self.driver.get("https://adsha.re/login")
                time.sleep(5)
                
                # Find password field
                password_field = None
                password_selectors = [
                    "input[type='password']",
                    "input[name*='pass']",
                    "input[name*='word']", 
                    "input[name*='pwd']",
                ]
                
                for selector in password_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                password_field = element
                                break
                        if password_field:
                            break
                    except:
                        continue
                
                if not password_field:
                    continue
                
                # Fill credentials
                email_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='mail'], input[type='email']")
                email_field.clear()
                email_field.send_keys(self.email)
                time.sleep(2)
                
                password_field.clear()
                password_field.send_keys(self.password)
                time.sleep(2)
                
                # Submit form
                submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
                submit_btn.click()
                time.sleep(8)
                
                # Verify login
                self.driver.get("https://adsha.re/surf")
                time.sleep(5)
                
                if "surf" in self.driver.current_url:
                    self.logger.info("✅ Login successful!")
                    return True
                    
            except Exception as e:
                self.logger.error(f"❌ Login attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
        
        self.state['last_error'] = "Login failed"
        return False

    def calculate_similarity(self, str1, str2):
        """Calculate string similarity"""
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        longer = str1 if len(str1) > len(str2) else str2
        shorter = str1 if len(str1) <= len(str2) else str2
        
        common_chars = sum(1 for a, b in zip(longer, shorter) if a == b)
        return common_chars / max(len(str1), len(str2))

    def compare_symbols(self, question_svg, answer_svg):
        """Compare SVG symbols"""
        try:
            question_content = question_svg.get_attribute('innerHTML')
            answer_content = answer_svg.get_attribute('innerHTML')
            
            def clean_svg(svg_text):
                cleaned = re.sub(r'\s+', ' ', svg_text).strip().lower()
                cleaned = re.sub(r'fill:#[a-f0-9]+', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'stroke:#[a-f0-9]+', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'style="[^"]*"', '', cleaned)
                cleaned = re.sub(r'class="[^"]*"', '', cleaned)
                return cleaned
            
            clean_question = clean_svg(question_content)
            clean_answer = clean_svg(answer_content)
            
            if clean_question == clean_answer:
                return {'match': True, 'confidence': 1.0, 'exact': True}
            
            similarity = self.calculate_similarity(clean_question, clean_answer)
            should_match = similarity >= CONFIG['minimum_confidence']
            
            return {
                'match': should_match,
                'confidence': similarity,
                'exact': False
            }
            
        except Exception as e:
            return {'match': False, 'confidence': 0.0, 'exact': False}

    def find_best_match(self, question_svg, links):
        """Find best symbol match"""
        best_match = None
        highest_confidence = 0
        exact_matches = []
        
        for link in links:
            try:
                answer_svg = link.find_element(By.TAG_NAME, "svg")
                if answer_svg:
                    comparison = self.compare_symbols(question_svg, answer_svg)
                    
                    if comparison['exact'] and comparison['match']:
                        exact_matches.append({
                            'link': link,
                            'confidence': comparison['confidence'],
                            'exact': True
                        })
                    elif comparison['match'] and comparison['confidence'] > highest_confidence:
                        highest_confidence = comparison['confidence']
                        best_match = {
                            'link': link,
                            'confidence': comparison['confidence'],
                            'exact': False
                        }
            except:
                continue
        
        if exact_matches:
            return exact_matches[0]
        if best_match and best_match['confidence'] >= CONFIG['minimum_confidence']:
            return best_match
        return None

    def advanced_human_click(self, element):
        """Click element with variation"""
        if self.is_behavior_suspicious() or self.state['is_in_cooldown']:
            return False
        
        try:
            location = element.location
            size = element.size
            
            if CONFIG['click_position_variation']:
                variation_x = size['width'] * (0.3 + random.random() * 0.4)
                variation_y = size['height'] * (0.3 + random.random() * 0.4)
            else:
                variation_x = size['width'] / 2
                variation_y = size['height'] / 2
            
            actions = webdriver.ActionChains(self.driver)
            actions.move_to_element_with_offset(element, variation_x, variation_y)
            actions.click()
            actions.perform()
            
            self.state['click_count'] += 1
            self.state['last_click_time'] = time.time()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Click failed: {e}")
            return False

    def extract_credits(self):
        """Extract credit balance from page"""
        if not self.driver:
            return "BROWSER_NOT_RUNNING"
        
        try:
            self.driver.refresh()
            time.sleep(5)
            page_source = self.driver.page_source
            
            credit_patterns = [
                r'(\d{1,3}(?:,\d{3})*)\s*Credits',
                r'Credits.*?(\d{1,3}(?:,\d{3})*)',
                r'>\s*(\d[\d,]*)\s*Credits<',
                r'balance.*?(\d[\d,]*)',
            ]
            
            for pattern in credit_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                if matches:
                    credits = matches[0]
                    return f"{credits} Credits"
            
            return "CREDITS_NOT_FOUND"
            
        except Exception as e:
            return f"ERROR: {str(e)}"

    def send_credit_report(self):
        """Send credit report to Telegram"""
        credits = self.extract_credits()
        self.state['last_credits'] = credits
        
        message = f"""
💰 <b>Credit Report</b>
⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}
💎 {credits}
🎯 Games Solved: {self.state['total_solved']}
🔄 Status: {self.state['status']}
        """
        
        self.send_telegram(message)
        self.logger.info(f"📊 Credit report sent: {credits}")

    def monitoring_loop(self):
        """Background monitoring for credits"""
        self.logger.info("📊 Starting credit monitoring...")
        self.state['monitoring_active'] = True
        
        while self.state['monitoring_active']:
            try:
                if self.state['is_running']:
                    self.send_credit_report()
                
                # Wait for next check
                for _ in range(CONFIG['credit_check_interval']):
                    if not self.state['monitoring_active']:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)
        
        self.logger.info("📊 Credit monitoring stopped")

    def advanced_solve_symbol_game(self):
        """Solve one game round"""
        if not self.state['is_running'] or self.state['is_in_cooldown']:
            return
        
        try:
            # Take breaks occasionally
            if self.state['consecutive_rounds'] > 15 and random.random() < 0.3:
                self.logger.info("💤 Taking a short break...")
                self.start_cooldown(10 + random.random() * 20)
                self.state['consecutive_rounds'] = 0
                return
            
            # Find question SVG
            question_svg = None
            svg_selectors = ["svg", "[class*='symbol']", "[class*='question'] svg"]
            
            for selector in svg_selectors:
                try:
                    question_svg = WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not question_svg:
                return
            
            # Find clickable options
            links = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='adsha.re'], button, [class*='option']"))
            )
            
            # Find and click best match
            best_match = self.find_best_match(question_svg, links)
            
            if best_match and self.advanced_human_click(best_match['link']):
                self.state['total_solved'] += 1
                self.state['consecutive_rounds'] += 1
                self.state['consecutive_fails'] = 0
                
                match_type = "EXACT" if best_match['exact'] else "FUZZY"
                self.logger.info(f"✅ {match_type} Match! Confidence: {(best_match['confidence'] * 100):.1f}% | Total: {self.state['total_solved']}")
                return True
            else:
                self.state['consecutive_fails'] += 1
                if self.state['consecutive_fails'] > 3:
                    self.start_cooldown(15)
                    self.state['consecutive_fails'] = 0
            
        except Exception as error:
            self.state['consecutive_fails'] += 1

    def solver_loop(self):
        """Main solver loop"""
        self.logger.info("🎮 Starting solver loop...")
        self.state['status'] = 'running'
        self.state['session_start_time'] = time.time()
        
        # Initial setup
        self.driver.get("https://adsha.re/surf")
        time.sleep(5)
        
        if "login" in self.driver.current_url:
            if not self.force_login():
                self.logger.error("❌ Cannot login, stopping solver")
                self.stop()
                return
        
        fail_streak = 0
        
        while self.state['is_running']:
            try:
                # Refresh periodically
                if fail_streak % 20 == 0 and fail_streak > 0:
                    self.driver.refresh()
                    time.sleep(5)
                
                # Solve game
                if self.advanced_solve_symbol_game():
                    fail_streak = 0
                    time.sleep(self.get_smart_delay())
                else:
                    fail_streak += 1
                    time.sleep(8)
                
                if fail_streak >= 25:
                    fail_streak = 0
                    time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Loop error: {e}")
                time.sleep(15)
                fail_streak += 1
        
        self.logger.info("🛑 Solver loop stopped")

    def start(self):
        """Start the solver"""
        if self.state['is_running']:
            return "❌ Solver is already running"
        
        if not self.driver:
            if not self.setup_browser():
                return "❌ Browser setup failed"
        
        self.state['is_running'] = True
        self.solver_thread = threading.Thread(target=self.solver_loop, daemon=True)
        self.solver_thread.start()
        
        # Start monitoring if not already running
        if not self.state['monitoring_active']:
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        
        self.logger.info("🚀 Solver started!")
        return "✅ Solver started successfully!"

    def stop(self):
        """Stop the solver"""
        self.state['is_running'] = False
        self.state['status'] = 'stopped'
        self.logger.info("🛑 Solver stopped")
        return "✅ Solver stopped successfully!"

    def status(self):
        """Get solver status"""
        session_duration = time.time() - self.state['session_start_time']
        
        status_text = f"""
📊 <b>Status Report</b>
⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}
🔄 Status: {self.state['status']}
🎯 Games Solved: {self.state['total_solved']}
💰 Last Credits: {self.state['last_credits']}
⏱️ Session: {int(session_duration)}s
🔢 Clicks: {self.state['click_count']}
❌ Fails: {self.state['consecutive_fails']}
        """
        
        if self.state['last_error']:
            status_text += f"\n⚠️ Last Error: {self.state['last_error']}"
        
        return status_text

    def credits(self):
        """Get current credits"""
        credits = self.extract_credits()
        self.state['last_credits'] = credits
        
        return f"""
💰 <b>Credit Check</b>
⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}
💎 {credits}
        """

# Telegram Bot Handler
class TelegramBot:
    def __init__(self):
        self.solver = AdvancedSymbolGameSolver()
        self.logger = logging.getLogger(__name__)
    
    def handle_updates(self):
        """Handle Telegram updates"""
        last_update_id = None
        
        while True:
            try:
                url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/getUpdates"
                params = {'timeout': 30, 'offset': last_update_id}
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    updates = response.json()
                    if updates['result']:
                        for update in updates['result']:
                            last_update_id = update['update_id'] + 1
                            self.process_message(update)
                
            except Exception as e:
                self.logger.error(f"❌ Telegram update error: {e}")
                time.sleep(5)
    
    def process_message(self, update):
        """Process incoming message"""
        if 'message' not in update or 'text' not in update['message']:
            return
        
        chat_id = update['message']['chat']['id']
        text = update['message']['text']
        
        # Ensure we're using the correct chat ID
        if not self.solver.telegram_chat_id:
            self.solver.telegram_chat_id = chat_id
        
        response = ""
        
        if text.startswith('/start'):
            response = self.solver.start()
        elif text.startswith('/stop'):
            response = self.solver.stop()
        elif text.startswith('/status'):
            response = self.solver.status()
        elif text.startswith('/credits'):
            response = self.solver.credits()
        elif text.startswith('/help'):
            response = """
🤖 <b>AdShare Solver Bot Commands</b>

/start - Start the symbol solver
/stop - Stop the solver  
/status - Check current status
/credits - Get credit balance
/help - Show this help message

💡 <i>Credit reports are sent automatically every 30 minutes</i>
            """
        else:
            response = "❌ Unknown command. Use /help for available commands."
        
        if response:
            self.solver.send_telegram(response)

if __name__ == '__main__':
    bot = TelegramBot()
    bot.logger.info("🤖 Starting Telegram Bot...")
    bot.handle_updates()