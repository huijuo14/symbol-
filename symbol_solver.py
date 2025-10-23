#!/usr/bin/env python3
"""
AdShare Symbol Game Solver - Koyeb Web Service Version
Optimized for continuous operation without mouse movement
"""

import os
import time
import random
import logging
import re
import math
import threading
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

# Configuration
CONFIG = {
    'base_delay': 2000,
    'min_delay': 1500,
    'max_delay': 4000,
    'max_clicks_per_minute': 15,
    'max_session_length': 3600000,  # 1 hour
    'minimum_confidence': 0.90,
    'enable_console_logs': True
}

class SymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.state = {
            'click_count': 0,
            'last_click_time': 0,
            'session_start_time': time.time() * 1000,
            'is_running': True,
            'total_solved': 0,
            'consecutive_fails': 0,
            'is_in_cooldown': False
        }
        
        self.email = "loginallapps@gmail.com"
        self.password = "@Sd2007123"
        self.setup_logging()
        
        # Flask app for health checks
        self.app = Flask(__name__)
        self.setup_flask_routes()

    def setup_flask_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({
                'status': 'running',
                'total_solved': self.state['total_solved'],
                'consecutive_fails': self.state['consecutive_fails'],
                'uptime': f"{(time.time() * 1000 - self.state['session_start_time']) / 1000:.0f}s"
            })
        
        @self.app.route('/health')
        def health():
            return jsonify({'status': 'healthy'})
        
        @self.app.route('/stats')
        def stats():
            return jsonify({
                'total_solved': self.state['total_solved'],
                'consecutive_fails': self.state['consecutive_fails'],
                'is_running': self.state['is_running']
            })

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        """Setup Chrome for Koyeb"""
        self.logger.info("🌐 Starting Chrome for Koyeb...")
        
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1200,800")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.logger.info("✅ Chrome started successfully!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False

    def smart_delay(self):
        """Simple delay without complex patterns"""
        delay = random.uniform(CONFIG['min_delay'] / 1000, CONFIG['max_delay'] / 1000)
        time.sleep(delay)
        return delay

    def force_login(self):
        """Login with dynamic password field detection"""
        try:
            self.logger.info("🔐 Attempting login...")
            
            self.driver.get("https://adsha.re/login")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.smart_delay()
            
            # Parse page to find dynamic password field
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            form = soup.find('form', {'name': 'login'})
            if not form:
                self.logger.error("❌ Login form not found")
                return False
            
            password_field_name = None
            for field in form.find_all('input'):
                field_name = field.get('name', '')
                field_value = field.get('value', '')
                if field_value == 'Password' and field_name != 'mail' and field_name:
                    password_field_name = field_name
                    break
            
            if not password_field_name:
                self.logger.error("❌ Password field not detected")
                return False
            
            self.logger.info(f"🔑 Password field: {password_field_name}")
            
            # Fill email
            email_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='mail']")
            email_field.clear()
            email_field.send_keys(self.email)
            self.logger.info("✅ Email entered")
            
            self.smart_delay()
            
            # Fill password
            password_field = self.driver.find_element(By.CSS_SELECTOR, f"input[name='{password_field_name}']")
            password_field.clear()
            password_field.send_keys(self.password)
            self.logger.info("✅ Password entered")
            
            self.smart_delay()
            
            # Submit form
            form_element = self.driver.find_element(By.CSS_SELECTOR, "form[name='login']")
            form_element.submit()
            self.logger.info("✅ Form submitted")
            
            # Wait for login
            time.sleep(8)
            
            # Verify login
            self.driver.get("https://adsha.re/surf")
            time.sleep(5)
            
            if "surf" in self.driver.current_url:
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.warning("⚠️ Login verification needed")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False

    def simple_click(self, element):
        """Simple click without mouse movement"""
        try:
            self.smart_delay()
            element.click()
            self.state['click_count'] += 1
            self.state['last_click_time'] = time.time() * 1000
            return True
        except Exception as e:
            self.logger.error(f"❌ Click failed: {e}")
            return False

    def compare_symbols(self, question_svg, answer_svg):
        """Compare SVG symbols"""
        try:
            question_content = question_svg.get_attribute('innerHTML')
            answer_content = answer_svg.get_attribute('innerHTML')
            
            if not question_content or not answer_content:
                return {'match': False, 'confidence': 0.0}
            
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
                return {'match': True, 'confidence': 1.0}
            
            # Simple similarity check
            common_chars = sum(1 for a, b in zip(clean_question, clean_answer) if a == b)
            max_len = max(len(clean_question), len(clean_answer))
            similarity = common_chars / max_len if max_len > 0 else 0
            
            return {'match': similarity >= CONFIG['minimum_confidence'], 'confidence': similarity}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Symbol comparison error: {e}")
            return {'match': False, 'confidence': 0.0}

    def solve_symbol_game(self):
        """Solve one game round"""
        if not self.state['is_running'] or self.state['is_in_cooldown']:
            return False
        
        try:
            # Wait longer for game elements to appear
            question_svg = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "svg"))
            )
            
            # Find answer options with longer wait
            links = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='adsha.re'], button, .answer-option"))
            )
            
            # Find best match
            best_match = None
            highest_confidence = 0
            
            for link in links:
                try:
                    answer_svg = link.find_element(By.TAG_NAME, "svg")
                    if answer_svg:
                        comparison = self.compare_symbols(question_svg, answer_svg)
                        if comparison['match'] and comparison['confidence'] > highest_confidence:
                            highest_confidence = comparison['confidence']
                            best_match = link
                except:
                    continue
            
            if best_match and highest_confidence >= CONFIG['minimum_confidence']:
                if self.simple_click(best_match):
                    self.state['total_solved'] += 1
                    self.state['consecutive_fails'] = 0
                    self.logger.info(f"✅ Match! Confidence: {highest_confidence*100:.1f}% | Total: {self.state['total_solved']}")
                    return True
            
            self.state['consecutive_fails'] += 1
            self.logger.info(f"❌ No confident match found (Fails: {self.state['consecutive_fails']})")
            return False
            
        except TimeoutException:
            self.state['consecutive_fails'] += 1
            self.logger.info(f"⏳ Game elements not ready (Fails: {self.state['consecutive_fails']})")
            return False
        except Exception as e:
            self.state['consecutive_fails'] += 1
            self.logger.error(f"❌ Game solving error: {e}")
            return False

    def start_cooldown(self, duration=30000):
        """Start cooldown period"""
        self.state['is_in_cooldown'] = True
        self.logger.info(f"😴 Cooldown for {duration/1000}s")
        
        def end_cooldown():
            time.sleep(duration / 1000)
            self.state['is_in_cooldown'] = False
            self.logger.info("✅ Cooldown ended")
        
        thread = threading.Thread(target=end_cooldown)
        thread.daemon = True
        thread.start()

    def game_loop(self):
        """Main game solving loop"""
        self.logger.info("🎮 Starting game solver loop...")
        
        fail_streak = 0
        max_fail_streak = 20  # Increased fail tolerance for web service
        
        while self.state['is_running']:
            try:
                # Refresh page every 5 minutes to stay active
                if fail_streak % 10 == 0 and fail_streak > 0:
                    self.driver.refresh()
                    self.logger.info("🔁 Page refreshed")
                    time.sleep(5)
                
                # Try to solve game
                if self.solve_symbol_game():
                    fail_streak = 0
                    # Short delay after success
                    time.sleep(3)
                else:
                    fail_streak += 1
                    # Longer delay after failure
                    time.sleep(8)
                
                # Reset fail streak occasionally to prevent false stops
                if fail_streak >= 50:
                    self.logger.info("🔄 Resetting fail streak")
                    fail_streak = 0
                
            except Exception as e:
                self.logger.error(f"❌ Game loop error: {e}")
                time.sleep(10)
                fail_streak += 1

    def run_solver(self):
        """Run the solver (to be called in thread)"""
        if not self.setup_browser():
            return
        
        # Navigate and login
        self.driver.get("https://adsha.re/surf")
        time.sleep(5)
        
        if "login" in self.driver.current_url:
            if not self.force_login():
                self.logger.error("❌ Cannot continue without login")
                return
        
        self.logger.info("✅ Starting solver service...")
        self.game_loop()

    def start_service(self):
        """Start both Flask web service and solver"""
        # Start solver in background thread
        solver_thread = threading.Thread(target=self.run_solver)
        solver_thread.daemon = True
        solver_thread.start()
        
        # Start Flask app
        self.logger.info("🌐 Starting Flask web service on port 8080...")
        self.app.run(host='0.0.0.0', port=8080, debug=False)

    def cleanup(self):
        """Cleanup resources"""
        self.state['is_running'] = False
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def main():
    solver = SymbolGameSolver()
    
    try:
        solver.start_service()
    except KeyboardInterrupt:
        solver.logger.info("🛑 Service stopped by user")
        solver.cleanup()
    except Exception as e:
        solver.logger.error(f"💥 Service crashed: {e}")
        solver.cleanup()
        raise

if __name__ == '__main__':
    main()
