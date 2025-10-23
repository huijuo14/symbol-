#!/usr/bin/env python3
"""
AdShare Symbol Game Solver - Alpine Chromium Version
With fixed user directory and memory optimization
"""

import os
import time
import random
import logging
import re
import threading
import tempfile
from flask import Flask, jsonify, request
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
        self.user_data_dir = None
        self.state = {
            'click_count': 0,
            'session_start_time': time.time() * 1000,
            'is_running': False,
            'total_solved': 0,
            'consecutive_fails': 0,
            'is_in_cooldown': False,
            'status': 'stopped',
            'browser_status': 'not_started'
        }
        
        self.email = "loginallapps@gmail.com"
        self.password = "@Sd2007123"
        self.setup_logging()
        
        # Flask app
        self.app = Flask(__name__)
        self.setup_flask_routes()

    def setup_flask_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({
                'status': self.state['status'],
                'browser_status': self.state['browser_status'],
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
                solver_thread = threading.Thread(target=self.run_solver)
                solver_thread.daemon = True
                solver_thread.start()
                return jsonify({'status': 'started', 'message': 'Solver starting...'})
            return jsonify({'status': 'already_running'})
        
        @self.app.route('/stop', methods=['POST'])
        def stop_solver():
            self.state['is_running'] = False
            self.state['status'] = 'stopped'
            # Cleanup user data directory
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                import shutil
                try:
                    shutil.rmtree(self.user_data_dir)
                except:
                    pass
            if self.driver:
                try:
                    self.driver.quit()
                    self.driver = None
                except:
                    pass
            return jsonify({'status': 'stopped', 'message': 'Solver stopped'})
        
        @self.app.route('/test-browser', methods=['POST'])
        def test_browser():
            """Test Chromium browser"""
            try:
                if self.setup_browser():
                    self.state['browser_status'] = 'test_passed'
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                    # Cleanup test directory
                    if self.user_data_dir and os.path.exists(self.user_data_dir):
                        import shutil
                        try:
                            shutil.rmtree(self.user_data_dir)
                        except:
                            pass
                    return jsonify({'status': 'success', 'message': 'Chromium test passed'})
                else:
                    return jsonify({'status': 'failed', 'message': 'Chromium test failed'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_browser(self):
        """Setup Chromium for Alpine with unique user directory"""
        self.logger.info("🖥️ Starting Chromium on Alpine...")
        
        options = Options()
        
        # Set Chromium binary location for Alpine
        options.binary_location = '/usr/bin/chromium-browser'
        
        # Memory optimization
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless=new")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-images")
        options.add_argument("--single-process")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=128")
        options.add_argument("--window-size=400,300")
        
        # FIX: Create unique user data directory
        self.user_data_dir = tempfile.mkdtemp(prefix="chromium_data_")
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # Stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            
            # Test browser
            self.logger.info("📄 Testing Chromium...")
            self.driver.get("about:blank")
            time.sleep(2)
            
            if "about:blank" in self.driver.current_url:
                self.logger.info("✅ Chromium started successfully!")
                self.state['browser_status'] = 'chromium_ready'
                return True
            else:
                self.logger.error("❌ Chromium test failed")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Chromium setup failed: {e}")
            # Cleanup on failure
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                import shutil
                try:
                    shutil.rmtree(self.user_data_dir)
                except:
                    pass
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False

    def smart_delay(self):
        """Simple delay"""
        delay = random.uniform(CONFIG['min_delay'] / 1000, CONFIG['max_delay'] / 1000)
        time.sleep(delay)
        return delay

    def force_login(self):
        """Login with Chromium"""
        try:
            self.logger.info("🔐 Starting login process...")
            
            # Navigate to login page
            self.driver.get("https://adsha.re/login")
            time.sleep(5)
            
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
            
            self.logger.info(f"🔑 Found password field: {password_field_name}")
            
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
            time.sleep(8)
            
            # Verify login
            self.driver.get("https://adsha.re/surf")
            time.sleep(5)
            
            if "surf" in self.driver.current_url:
                self.logger.info("🎉 Login successful! Ready for games.")
                self.state['browser_status'] = 'logged_in'
                return True
            else:
                self.logger.warning("⚠️ May need manual verification")
                self.state['browser_status'] = 'login_verification_needed'
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
            return False

    def advanced_human_click(self, element):
        """Advanced human-like click with variation"""
        try:
            # Pre-click delay
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click with position variation
            actions = ActionChains(self.driver)
            
            # Random offset within element bounds
            offset_x = random.randint(-8, 8)
            offset_y = random.randint(-8, 8)
            
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            actions.click()
            actions.perform()
            
            self.state['click_count'] += 1
            self.state['last_click_time'] = time.time() * 1000
            
            # Post-click delay
            time.sleep(random.uniform(0.2, 0.8))
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Advanced click failed: {e}")
            return False

    def compare_symbols(self, question_svg, answer_svg):
        """Enhanced symbol comparison with fuzzy matching"""
        try:
            question_content = question_svg.get_attribute('innerHTML')
            answer_content = answer_svg.get_attribute('innerHTML')
            
            if not question_content or not answer_content:
                return {'match': False, 'confidence': 0.0, 'exact': False}
            
            def clean_svg(svg_text):
                cleaned = re.sub(r'\s+', ' ', svg_text).strip().lower()
                cleaned = re.sub(r'fill:#[a-f0-9]+', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'stroke:#[a-f0-9]+', '', cleaned, flags=re.IGNORECASE)
                cleaned = re.sub(r'style="[^"]*"', '', cleaned)
                cleaned = re.sub(r'class="[^"]*"', '', cleaned)
                return cleaned
            
            clean_question = clean_svg(question_content)
            clean_answer = clean_svg(answer_content)
            
            # Exact match (preferred)
            if clean_question == clean_answer:
                return {'match': True, 'confidence': 1.0, 'exact': True}
            
            # Fuzzy matching for similar symbols
            if len(clean_question) > 10 and len(clean_answer) > 10:
                common_chars = sum(1 for a, b in zip(clean_question, clean_answer) if a == b)
                similarity = common_chars / max(len(clean_question), len(clean_answer))
                
                if similarity >= CONFIG['minimum_confidence']:
                    return {'match': True, 'confidence': similarity, 'exact': False}
            
            return {'match': False, 'confidence': 0.0, 'exact': False}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Symbol comparison error: {e}")
            return {'match': False, 'confidence': 0.0, 'exact': False}

    def find_best_match(self, question_svg, links):
        """Find the best possible match with high confidence"""
        best_match = None
        highest_confidence = 0
        exact_matches = []
        
        for link in links:
            try:
                answer_svg = link.find_element(By.TAG_NAME, "svg")
                if answer_svg:
                    comparison = self.compare_symbols(question_svg, answer_svg)
                    
                    # Always prefer exact matches
                    if comparison['exact'] and comparison['match']:
                        exact_matches.append({
                            'link': link,
                            'confidence': comparison['confidence'],
                            'exact': True
                        })
                    
                    # Consider high-confidence fuzzy matches
                    elif comparison['match'] and comparison['confidence'] > highest_confidence:
                        highest_confidence = comparison['confidence']
                        best_match = {
                            'link': link,
                            'confidence': comparison['confidence'],
                            'exact': False
                        }
            except:
                continue
        
        # Return exact match if available
        if exact_matches:
            return exact_matches[0]
        
        # Return best fuzzy match if confidence is high enough
        if best_match and best_match['confidence'] >= CONFIG['minimum_confidence']:
            return best_match
        
        return None

    def solve_symbol_game(self):
        """Solve one game round with perfect accuracy"""
        if not self.state['is_running']:
            return False
        
        try:
            # Find game elements
            question_svg = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "svg"))
            )
            
            links = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='adsha.re'], button, .answer-option"))
            )
            
            # Find the best possible match
            best_match = self.find_best_match(question_svg, links)
            
            if best_match:
                if self.advanced_human_click(best_match['link']):
                    self.state['total_solved'] += 1
                    self.state['consecutive_fails'] = 0
                    self.state['status'] = 'running'
                    
                    match_type = "EXACT" if best_match['exact'] else "FUZZY"
                    self.logger.info(f"✅ {match_type} Match! Confidence: {best_match['confidence']*100:.1f}% | Total: {self.state['total_solved']}")
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

    def game_loop(self):
        """Main game solving loop"""
        self.logger.info("🎮 Starting game solver loop...")
        self.state['status'] = 'running'
        
        fail_streak = 0
        cycle_count = 0
        
        while self.state['is_running']:
            try:
                # Refresh page every 10 minutes
                if cycle_count % 20 == 0 and cycle_count > 0:
                    try:
                        self.driver.refresh()
                        self.logger.info("🔁 Page refreshed")
                        time.sleep(5)
                    except:
                        pass
                
                # Try to solve game
                if self.solve_symbol_game():
                    fail_streak = 0
                    time.sleep(4)  # Success delay
                else:
                    fail_streak += 1
                    time.sleep(8)  # Failure delay
                
                # Reset fail streak occasionally
                if fail_streak >= 25:
                    self.logger.info("🔄 Resetting fail streak")
                    fail_streak = 0
                    time.sleep(30)
                
                cycle_count += 1
                
            except Exception as e:
                self.logger.error(f"❌ Game loop error: {e}")
                time.sleep(15)
                fail_streak += 1

    def run_solver(self):
        """Run the solver with Chromium"""
        self.logger.info("🚀 Starting solver with Chromium...")
        
        # Setup Chromium browser
        if not self.setup_browser():
            self.state['status'] = 'browser_failed'
            return
        
        try:
            # Login
            if not self.force_login():
                self.state['status'] = 'login_failed'
                return
            
            # Start game loop
            self.logger.info("🎯 Starting game solving...")
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
            # Cleanup user data directory
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                import shutil
                try:
                    shutil.rmtree(self.user_data_dir)
                except:
                    pass

    def start_service(self):
        """Start Flask web service"""
        self.logger.info("🌐 Starting Flask web service on port 8000...")
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