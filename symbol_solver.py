#!/usr/bin/env python3
"""
AdShare Symbol Game Solver - Koyeb Web Service with Controls
Fixed for low-resource environment
"""

import os
import time
import random
import logging
import re
import threading
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Configuration optimized for low RAM
CONFIG = {
    'base_delay': 3000,
    'min_delay': 2000,
    'max_delay': 5000,
    'max_clicks_per_minute': 10,
    'minimum_confidence': 0.90,
    'enable_console_logs': True
}

class SymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.state = {
            'click_count': 0,
            'session_start_time': time.time() * 1000,
            'is_running': False,  # Start stopped
            'total_solved': 0,
            'consecutive_fails': 0,
            'is_in_cooldown': False,
            'status': 'stopped'
        }
        
        self.email = "loginallapps@gmail.com"
        self.password = "@Sd2007123"
        self.setup_logging()
        
        # Flask app for health checks and controls
        self.app = Flask(__name__)
        self.setup_flask_routes()

    def setup_flask_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({
                'status': self.state['status'],
                'total_solved': self.state['total_solved'],
                'consecutive_fails': self.state['consecutive_fails'],
                'uptime': f"{(time.time() * 1000 - self.state['session_start_time']) / 1000:.0f}s"
            })
        
        @self.app.route('/health')
        def health():
            return jsonify({'status': 'healthy'})
        
        @self.app.route('/stats')
        def stats():
            return jsonify(self.state)
        
        @self.app.route('/start', methods=['POST'])
        def start_solver():
            if not self.state['is_running']:
                self.state['is_running'] = True
                self.state['status'] = 'starting'
                # Start solver in background
                solver_thread = threading.Thread(target=self.run_solver)
                solver_thread.daemon = True
                solver_thread.start()
                return jsonify({'status': 'started', 'message': 'Solver starting...'})
            return jsonify({'status': 'already_running'})
        
        @self.app.route('/stop', methods=['POST'])
        def stop_solver():
            self.state['is_running'] = False
            self.state['status'] = 'stopped'
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass
            return jsonify({'status': 'stopped', 'message': 'Solver stopped'})
        
        @self.app.route('/restart', methods=['POST'])
        def restart_solver():
            self.state['is_running'] = False
            time.sleep(2)
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass
            self.state['is_running'] = True
            self.state['status'] = 'restarting'
            solver_thread = threading.Thread(target=self.run_solver)
            solver_thread.daemon = True
            solver_thread.start()
            return jsonify({'status': 'restarting', 'message': 'Solver restarting...'})

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        """Setup Chrome for low-resource Koyeb instance"""
        self.logger.info("🌐 Starting Chrome with low-resource settings...")
        
        options = Options()
        # Memory-saving options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=256")
        
        # Basic stealth
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Headless with minimal resources
        options.add_argument("--headless=new")
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-images")  # Save memory
        options.add_argument("--disable-javascript")  # Try without JS first
        
        # Memory limits
        options.add_argument("--max_old_space_size=256")
        options.add_argument("--aggressive-cache-discard")
        options.add_argument("--disable-features=VizDisplayCompositor")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts to prevent hanging
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            
            self.logger.info("✅ Chrome started successfully!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            return False

    def smart_delay(self):
        """Simple delay"""
        delay = random.uniform(CONFIG['min_delay'] / 1000, CONFIG['max_delay'] / 1000)
        time.sleep(delay)
        return delay

    def force_login(self):
        """Login with error handling"""
        try:
            self.logger.info("🔐 Attempting login...")
            
            self.driver.get("https://adsha.re/login")
            time.sleep(5)  # Simple wait instead of WebDriverWait
            
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
            
            time.sleep(2)
            
            # Fill password
            password_field = self.driver.find_element(By.CSS_SELECTOR, f"input[name='{password_field_name}']")
            password_field.clear()
            password_field.send_keys(self.password)
            self.logger.info("✅ Password entered")
            
            time.sleep(2)
            
            # Submit form
            form_element = self.driver.find_element(By.CSS_SELECTOR, "form[name='login']")
            form_element.submit()
            self.logger.info("✅ Form submitted")
            
            # Wait for login
            time.sleep(10)
            
            # Verify login by checking URL
            self.driver.get("https://adsha.re/surf")
            time.sleep(5)
            
            if "surf" in self.driver.current_url:
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.warning("⚠️ May need manual verification")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False

    def simple_click(self, element):
        """Simple click without complex actions"""
        try:
            time.sleep(1)
            element.click()
            self.state['click_count'] += 1
            return True
        except Exception as e:
            self.logger.error(f"❌ Click failed: {e}")
            return False

    def compare_symbols(self, question_svg, answer_svg):
        """Simple symbol comparison"""
        try:
            question_content = question_svg.get_attribute('innerHTML')
            answer_content = answer_svg.get_attribute('innerHTML')
            
            if not question_content or not answer_content:
                return {'match': False, 'confidence': 0.0}
            
            def clean_svg(svg_text):
                cleaned = re.sub(r'\s+', ' ', svg_text).strip().lower()
                # Remove variable content
                cleaned = re.sub(r'fill:#[a-f0-9]+', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'stroke:#[a-f0-9]+', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'style="[^"]*"', '', cleaned)
                cleaned = re.sub(r'class="[^"]*"', '', cleaned)
                return cleaned
            
            clean_question = clean_svg(question_content)
            clean_answer = clean_svg(answer_content)
            
            # Exact match
            if clean_question == clean_answer:
                return {'match': True, 'confidence': 1.0}
            
            # Simple similarity
            if len(clean_question) > 10 and len(clean_answer) > 10:
                common_chars = sum(1 for a, b in zip(clean_question, clean_answer) if a == b)
                similarity = common_chars / max(len(clean_question), len(clean_answer))
                if similarity >= CONFIG['minimum_confidence']:
                    return {'match': True, 'confidence': similarity}
            
            return {'match': False, 'confidence': 0.0}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Symbol comparison error: {e}")
            return {'match': False, 'confidence': 0.0}

    def solve_symbol_game(self):
        """Solve one game round with error handling"""
        if not self.state['is_running']:
            return False
        
        try:
            # Simple element finding with retry
            for attempt in range(3):
                try:
                    question_svg = self.driver.find_element(By.TAG_NAME, "svg")
                    links = self.driver.find_elements(By.CSS_SELECTOR, "a, button")
                    break
                except:
                    if attempt == 2:
                        return False
                    time.sleep(3)
                    continue
            
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
                    self.state['status'] = 'running'
                    self.logger.info(f"✅ Solved! Confidence: {highest_confidence*100:.1f}% | Total: {self.state['total_solved']}")
                    return True
            
            self.state['consecutive_fails'] += 1
            self.logger.info(f"❌ No match found (Fails: {self.state['consecutive_fails']})")
            return False
            
        except Exception as e:
            self.state['consecutive_fails'] += 1
            self.logger.error(f"❌ Game solving error: {e}")
            return False

    def game_loop(self):
        """Main game solving loop"""
        self.logger.info("🎮 Starting game solver loop...")
        self.state['status'] = 'running'
        
        fail_streak = 0
        
        while self.state['is_running']:
            try:
                # Refresh page every 10 minutes
                if fail_streak % 20 == 0 and fail_streak > 0:
                    try:
                        self.driver.refresh()
                        self.logger.info("🔁 Page refreshed")
                        time.sleep(5)
                    except:
                        pass
                
                # Try to solve game
                if self.solve_symbol_game():
                    fail_streak = 0
                    time.sleep(5)  # Success delay
                else:
                    fail_streak += 1
                    time.sleep(10)  # Failure delay
                
                # Reset fail streak to prevent memory issues
                if fail_streak >= 30:
                    self.logger.info("🔄 Resetting fail streak")
                    fail_streak = 0
                    time.sleep(30)  # Long cooldown
                
            except Exception as e:
                self.logger.error(f"❌ Game loop error: {e}")
                time.sleep(15)
                fail_streak += 1

    def run_solver(self):
        """Run the solver"""
        if not self.setup_browser():
            self.state['status'] = 'browser_failed'
            return
        
        try:
            # Navigate and login
            self.driver.get("https://adsha.re/surf")
            time.sleep(8)
            
            if "login" in self.driver.current_url:
                if not self.force_login():
                    self.logger.error("❌ Cannot continue without login")
                    self.state['status'] = 'login_failed'
                    return
            
            self.logger.info("✅ Starting solver service...")
            self.game_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Solver crashed: {e}")
            self.state['status'] = 'crashed'
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def start_service(self):
        """Start Flask web service"""
        self.logger.info("🌐 Starting Flask web service on port 8080...")
        self.app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

def main():
    solver = SymbolGameSolver()
    
    try:
        solver.start_service()
    except KeyboardInterrupt:
        solver.logger.info("🛑 Service stopped by user")
    except Exception as e:
        solver.logger.error(f"💥 Service crashed: {e}")
        raise

if __name__ == '__main__':
    main()