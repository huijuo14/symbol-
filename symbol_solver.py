#!/usr/bin/env python3
"""
AdShare Symbol Game Solver Pro - Railway Optimized
Complete feature set with media disabled and dynamic login handling
"""

import os
import time
import random
import logging
import re
import threading
import math
from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Enhanced Configuration
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
    'disable_javascript': False,
    'block_popups': True
}

class AdvancedSymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.email = os.getenv('ADSHARE_EMAIL', 'loginallapps@gmail.com')
        self.password = os.getenv('ADSHARE_PASSWORD', '@Sd2007123')
        
        # State Management
        self.state = {
            'click_count': 0,
            'last_click_time': 0,
            'session_start_time': time.time(),
            'is_running': False,  # Start stopped
            'total_solved': 0,
            'consecutive_rounds': 0,
            'last_action_time': time.time(),
            'is_in_cooldown': False,
            'consecutive_fails': 0,
            'status': 'stopped',
            'last_error': None
        }
        
        # Advanced Pattern Storage
        self.behavior_patterns = {
            'delays': [],
            'accuracy': []
        }
        
        self.solver_thread = None
        self.setup_logging()
        self.logger.info("🚀 Advanced Symbol Game Solver Pro Initialized")
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('solver.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_browser(self):
        """Setup Chrome with maximum optimization and media disabled"""
        self.logger.info("🌐 Starting Chrome with maximum optimization...")
        
        options = Options()
        
        # Basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--headless=new")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=256")
        
        # Network optimizations - DISABLE MEDIA
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2 if CONFIG['disable_images'] else 1,  # 2=Block, 1=Allow
                'plugins': 2,
                'popups': 2 if CONFIG['block_popups'] else 1,
                'geolocation': 2,
                'notifications': 2,
                'auto_select_certificate': 2,
                'fullscreen': 2,
                'mouselock': 2,
                'mixed_script': 2,
                'media_stream': 2,
                'media_stream_mic': 2,
                'media_stream_camera': 2,
                'protocol_handlers': 2,
                'ppapi_broker': 2,
                'automatic_downloads': 2,
                'midi_sysex': 2,
                'push_messaging': 2,
                'ssl_cert_decisions': 2,
                'metro_switch_to_desktop': 2,
                'protected_media_identifier': 2,
                'app_banner': 2,
                'site_engagement': 2,
                'durable_storage': 2
            },
            'profile.managed_default_content_settings': {
                'images': 2 if CONFIG['disable_images'] else 1
            }
        }
        
        # Block videos and audio
        if CONFIG['disable_videos']:
            prefs['profile.default_content_setting_values']['plugins'] = 2
            prefs['profile.default_content_setting_values']['media_stream'] = 2
        
        if CONFIG['disable_audio']:
            prefs['profile.default_content_setting_values']['media_stream_mic'] = 2
            prefs['profile.default_content_setting_values']['media_stream_camera'] = 2
        
        options.add_experimental_option('prefs', prefs)
        
        # Window size
        options.add_argument("--window-size=1200,800")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Execute stealth scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_script("window.chrome = {runtime: {}};")
            
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            self.logger.info("✅ Chrome started with maximum optimization!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            self.state['last_error'] = str(e)
            return False

    def get_smart_delay(self):
        """Get intelligent delay with human-like patterns"""
        if not CONFIG['random_delay']:
            return CONFIG['base_delay']
        
        # Vary delay based on session length
        session_duration = time.time() - self.state['session_start_time']
        base = CONFIG['base_delay']
        
        # Simulate human fatigue - slower responses over time
        if session_duration > 900:  # After 15 minutes
            base += 1
        
        # Add random variation
        random_variation = random.uniform(CONFIG['min_delay'] - base, CONFIG['max_delay'] - base)
        
        return max(CONFIG['min_delay'], base + random_variation)

    def is_behavior_suspicious(self):
        """Advanced rate limiting with behavioral analysis"""
        now = time.time()
        time_since_last_click = now - self.state['last_click_time']
        
        # Check click rate
        clicks_per_minute = (self.state['click_count'] / ((now - self.state['session_start_time']) / 60)) if (now - self.state['session_start_time']) > 0 else 0
        
        if clicks_per_minute > CONFIG['max_clicks_per_minute']:
            self.logger.warning("⚠️ Suspicious behavior: High click rate")
            return True
        
        # Session length check
        if now - self.state['session_start_time'] > CONFIG['max_session_length']:
            self.logger.warning("⚠️ Suspicious behavior: Long session")
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
            self.logger.info("✅ Cooldown ended")
        
        threading.Thread(target=end_cooldown, daemon=True).start()

    def force_login(self):
        """Advanced login with dynamic password field detection and error handling"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🔐 Attempting login (Attempt {attempt + 1}/{max_retries})...")
                self.driver.get("https://adsha.re/login")
                time.sleep(5)
                
                # Look for password field with multiple strategies
                password_selectors = [
                    "input[type='password']",
                    "input[name*='pass']",
                    "input[name*='word']", 
                    "input[name*='pwd']",
                    "input[placeholder*='password']",
                    "input[placeholder*='pass']",
                    "input:not([type]):not([name*='mail']):not([name*='user'])"
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                password_field = element
                                self.logger.info(f"✅ Found password field with: {selector}")
                                break
                        if password_field:
                            break
                    except:
                        continue
                
                if not password_field:
                    self.logger.error("❌ Could not find password field")
                    continue
                
                # Fill credentials
                email_field = self.driver.find_element(By.CSS_SELECTOR, "input[name='mail'], input[type='email'], input[placeholder*='email']")
                email_field.clear()
                email_field.send_keys(self.email)
                time.sleep(2)
                
                password_field.clear()
                password_field.send_keys(self.password)
                time.sleep(2)
                
                # Submit form
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Login')",
                    "form button"
                ]
                
                for selector in submit_selectors:
                    try:
                        if "contains" in selector:
                            buttons = self.driver.find_elements(By.TAG_NAME, "button")
                            for button in buttons:
                                if "login" in button.text.lower():
                                    button.click()
                                    break
                        else:
                            submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                            submit_btn.click()
                        break
                    except:
                        continue
                
                time.sleep(8)
                
                # Verify login success
                self.driver.get("https://adsha.re/surf")
                time.sleep(5)
                
                if "surf" in self.driver.current_url or "dashboard" in self.driver.current_url:
                    self.logger.info("✅ Login successful!")
                    return True
                else:
                    self.logger.warning("⚠️ Login verification failed, checking for errors...")
                    
                    # Check for error messages
                    error_selectors = [".error", ".alert", "[class*='error']", "[class*='alert']"]
                    for selector in error_selectors:
                        try:
                            errors = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for error in errors:
                                if error.is_displayed():
                                    self.logger.error(f"❌ Login error: {error.text}")
                        except:
                            continue
                    
            except Exception as e:
                self.logger.error(f"❌ Login attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(10)
        
        self.state['last_error'] = "Login failed after all attempts"
        return False

    def calculate_similarity(self, str1, str2):
        """Calculate string similarity for fuzzy matching"""
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        longer = str1 if len(str1) > len(str2) else str2
        shorter = str1 if len(str1) <= len(str2) else str2
        
        # Simple character-based similarity
        common_chars = sum(1 for a, b in zip(longer, shorter) if a == b)
        return common_chars / max(len(str1), len(str2))

    def compare_symbols(self, question_svg, answer_svg):
        """Enhanced symbol comparison with fuzzy matching"""
        try:
            question_content = question_svg.get_attribute('innerHTML')
            answer_content = answer_svg.get_attribute('innerHTML')
            
            def clean_svg(svg_text):
                # Remove whitespace and normalize
                cleaned = re.sub(r'\s+', ' ', svg_text).strip().lower()
                # Remove colors and styles
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
            similarity = self.calculate_similarity(clean_question, clean_answer)
            should_match = similarity >= CONFIG['minimum_confidence']
            
            return {
                'match': should_match,
                'confidence': similarity,
                'exact': False
            }
            
        except Exception as e:
            self.logger.error(f"❌ Symbol comparison error: {e}")
            return {'match': False, 'confidence': 0.0, 'exact': False}

    def find_best_match(self, question_svg, links):
        """Find the BEST possible match with high confidence"""
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
            return exact_matches[0]  # Return first exact match
        
        # Return best fuzzy match if confidence is high enough
        if best_match and best_match['confidence'] >= CONFIG['minimum_confidence']:
            return best_match
        
        return None

    def advanced_human_click(self, element):
        """Advanced click with variation but NO intentional misses"""
        if self.is_behavior_suspicious() or self.state['is_in_cooldown']:
            self.logger.info("⏳ Safety cooldown active")
            return False
        
        try:
            # Get element position for variation
            location = element.location
            size = element.size
            
            if CONFIG['click_position_variation']:
                # Intelligent position variation - always within clickable area
                variation_x = size['width'] * (0.3 + random.random() * 0.4)
                variation_y = size['height'] * (0.3 + random.random() * 0.4)
            else:
                # Center click
                variation_x = size['width'] / 2
                variation_y = size['height'] / 2
            
            # Use ActionChains for reliable clicking
            actions = webdriver.ActionChains(self.driver)
            actions.move_to_element_with_offset(element, variation_x, variation_y)
            actions.click()
            actions.perform()
            
            # Update behavior tracking
            self.state['click_count'] += 1
            self.state['last_click_time'] = time.time()
            self.state['last_action_time'] = time.time()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Click failed: {e}")
            return False

    def advanced_solve_symbol_game(self):
        """Main solver with PERFECT accuracy"""
        if not self.state['is_running'] or self.state['is_in_cooldown']:
            return
        
        try:
            # Occasionally take breaks
            if self.state['consecutive_rounds'] > 15 and random.random() < 0.3:
                self.logger.info("💤 Taking a short break...")
                self.start_cooldown(10 + random.random() * 20)
                self.state['consecutive_rounds'] = 0
                return
            
            # Wait for game elements with multiple strategies
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
                self.logger.info("⏳ Waiting for game to load...")
                return
            
            # Find clickable links
            links = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='adsha.re'], button, [class*='option']"))
            )
            
            # Find the best possible match
            best_match = self.find_best_match(question_svg, links)
            
            if best_match:
                if self.advanced_human_click(best_match['link']):
                    self.state['total_solved'] += 1
                    self.state['consecutive_rounds'] += 1
                    self.state['consecutive_fails'] = 0
                    
                    match_type = "EXACT" if best_match['exact'] else "FUZZY"
                    self.logger.info(f"✅ {match_type} Match! Confidence: {(best_match['confidence'] * 100):.1f}% | Total: {self.state['total_solved']}")
                    
                    # Record timing pattern
                    self.behavior_patterns['delays'].append(self.get_smart_delay())
                    if len(self.behavior_patterns['delays']) > 20:
                        self.behavior_patterns['delays'].pop(0)
                    
                    return True
            else:
                # No good match found
                self.state['consecutive_fails'] += 1
                self.logger.info("🔍 No high-confidence match found, waiting...")
                
                # If multiple consecutive fails, take longer break
                if self.state['consecutive_fails'] > 3:
                    self.logger.warning("⚠️ Multiple fails detected, extended cooldown")
                    self.start_cooldown(15)
                    self.state['consecutive_fails'] = 0
            
        except Exception as error:
            self.logger.error(f"❌ Error in solver: {error}")
            self.state['consecutive_fails'] += 1

    def solver_loop(self):
        """Main solver loop"""
        self.logger.info("🎮 Starting solver loop...")
        self.state['status'] = 'running'
        self.state['session_start_time'] = time.time()
        
        # Initial login
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
                # Refresh every 10 minutes
                if fail_streak % 20 == 0 and fail_streak > 0:
                    self.driver.refresh()
                    self.logger.info("🔁 Page refreshed")
                    time.sleep(5)
                
                # Solve game
                if self.advanced_solve_symbol_game():
                    fail_streak = 0
                    time.sleep(self.get_smart_delay())
                else:
                    fail_streak += 1
                    time.sleep(8)
                
                if fail_streak >= 25:
                    self.logger.info("🔄 Resetting fail streak")
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
            return {"status": "error", "message": "Solver is already running"}
        
        if not self.driver:
            if not self.setup_browser():
                return {"status": "error", "message": "Browser setup failed"}
        
        self.state['is_running'] = True
        self.solver_thread = threading.Thread(target=self.solver_loop, daemon=True)
        self.solver_thread.start()
        
        self.logger.info("🚀 Solver started!")
        return {"status": "success", "message": "Solver started successfully"}

    def stop(self):
        """Stop the solver"""
        self.state['is_running'] = False
        self.state['status'] = 'stopped'
        self.logger.info("🛑 Solver stopped")
        return {"status": "success", "message": "Solver stopped successfully"}

    def status(self):
        """Get solver status"""
        return {
            "status": self.state['status'],
            "total_solved": self.state['total_solved'],
            "is_running": self.state['is_running'],
            "is_in_cooldown": self.state['is_in_cooldown'],
            "consecutive_fails": self.state['consecutive_fails'],
            "session_duration": time.time() - self.state['session_start_time'],
            "last_error": self.state['last_error']
        }

# Web Control Interface
app = Flask(__name__)
solver = AdvancedSymbolGameSolver()

@app.route('/')
def home():
    return """
    <html>
        <head><title>AdShare Solver Pro</title></head>
        <body>
            <h1>🎮 AdShare Symbol Game Solver Pro</h1>
            <p>Advanced solver with perfect accuracy</p>
            <div>
                <button onclick="startSolver()">▶️ Start</button>
                <button onclick="stopSolver()">⏹️ Stop</button>
                <button onclick="getStatus()">📊 Status</button>
            </div>
            <div id="status"></div>
            <script>
                async function startSolver() {
                    const response = await fetch('/start', {method: 'POST'});
                    const result = await response.json();
                    document.getElementById('status').innerHTML = `<p>${result.message}</p>`;
                }
                async function stopSolver() {
                    const response = await fetch('/stop', {method: 'POST'});
                    const result = await response.json();
                    document.getElementById('status').innerHTML = `<p>${result.message}</p>`;
                }
                async function getStatus() {
                    const response = await fetch('/status');
                    const result = await response.json();
                    document.getElementById('status').innerHTML = `
                        <p><strong>Status:</strong> ${result.status}</p>
                        <p><strong>Total Solved:</strong> ${result.total_solved}</p>
                        <p><strong>Running:</strong> ${result.is_running}</p>
                        <p><strong>Cooldown:</strong> ${result.is_in_cooldown}</p>
                        <p><strong>Session:</strong> ${Math.round(result.session_duration)}s</p>
                        ${result.last_error ? `<p><strong>Last Error:</strong> ${result.last_error}</p>` : ''}
                    `;
                }
            </script>
        </body>
    </html>
    """

@app.route('/start', methods=['POST'])
def start_solver():
    return jsonify(solver.start())

@app.route('/stop', methods=['POST'])
def stop_solver():
    return jsonify(solver.stop())

@app.route('/status')
def get_status():
    return jsonify(solver.status())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)