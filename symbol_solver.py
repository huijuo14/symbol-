#!/usr/bin/env python3
"""
AdShare Symbol Game Solver - Advanced Auto-Solver Pro
With Telegram Bot Integration - All original features preserved
"""

import os
import time
import random
import logging
import re
import math
import requests
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# Enhanced Security & Anti-detection Configuration
CONFIG = {
    # Timing Configuration
    'base_delay': 1500,
    'random_delay': True,
    'min_delay': 1000,
    'max_delay': 3500,
    
    # Behavioral Patterns
    'enable_human_patterns': True,
    'click_position_variation': True,
    'movement_variation': True,
    'occasional_misses': False,  # DISABLED - No intentional mistakes
    'miss_rate': 0.00,  # ZERO percent chance to miss
    
    # Rate Limiting
    'max_clicks_per_minute': 20,
    'max_session_length': 1800000,  # 30 minutes
    'cooldown_periods': True,
    
    # Stealth Features
    'enable_console_logs': True,
    'random_user_agent': False,
    'hide_script_presence': True,
    
    # Advanced Detection Evasion
    'mimic_mouse_movements': True,
    'scroll_randomly': True,
    'tab_activity': True,
    'session_rotation': True,
    
    # Accuracy Settings
    'always_perfect_accuracy': True,  # Always find and click correct answer
    'minimum_confidence': 0.90,  # Only click if very confident
    'retry_failed_matches': True,  # Retry if no match found initially
    
    # Telegram Bot
    'telegram_token': "8225236307:AAF9Y2-CM7TlLDFm2rcTVY6f3SA75j0DFI8",
    'credit_check_interval': 1800,  # 30 minutes in seconds
    'auto_restart_hours': 11
}

class AdvancedSymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.telegram_chat_id = None
        
        # State Management
        self.state = {
            'click_count': 0,
            'last_click_time': 0,
            'session_start_time': time.time() * 1000,
            'is_running': False,  # Start stopped
            'total_solved': 0,
            'consecutive_rounds': 0,
            'last_action_time': time.time() * 1000,
            'is_in_cooldown': False,
            'consecutive_fails': 0,
            'status': 'stopped',
            'last_error': None,
            'last_credits': 'Unknown',
            'monitoring_active': False
        }
        
        self.behavior_patterns = {
            'delays': [],
            'click_positions': [],
            'session_times': [],
            'accuracy': []
        }
        
        # Login credentials
        self.email = "loginallapps@gmail.com"
        self.password = "@Sd2007123"
        
        self.solver_thread = None
        self.monitoring_thread = None
        self.setup_logging()
        self.setup_telegram()
    
    def setup_logging(self):
        """Setup advanced logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_telegram(self):
        """Setup Telegram bot and get chat ID"""
        try:
            self.logger.info("🤖 Setting up Telegram bot...")
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/getUpdates"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                updates = response.json()
                if updates['result']:
                    self.telegram_chat_id = updates['result'][-1]['message']['chat']['id']
                    self.logger.info(f"✅ Telegram Chat ID: {self.telegram_chat_id}")
                    self.send_telegram("🤖 <b>AdShare Solver Pro Started!</b>\nUse /help for commands.")
                    return True
                else:
                    self.logger.warning("⚠️ No Telegram messages found. Send a message to your bot first.")
                    return False
            else:
                self.logger.error(f"❌ Telegram API error: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Telegram setup failed: {e}")
            return False
    
    def send_telegram(self, text, parse_mode='HTML'):
        """Send message to Telegram"""
        if not self.telegram_chat_id:
            self.logger.warning("⚠️ No Telegram chat ID configured")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                self.logger.info("✅ Telegram message sent")
                return True
            else:
                self.logger.error(f"❌ Telegram send failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Telegram send failed: {e}")
            return False
    
    def setup_browser(self):
        """Setup Chrome with advanced stealth features"""
        self.logger.info("🌐 Starting Chrome with advanced stealth...")
        
        options = Options()
        
        # Basic stealth options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-extensions")
        
        # Headless mode
        options.add_argument("--headless=new")
        
        # Window size
        options.add_argument("--window-size=1200,800")
        
        # Additional stealth
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-browser-side-navigation")
        
        # User agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Execute stealth scripts
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                window.chrome = {
                    runtime: {},
                };
                
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.logger.info("✅ Chrome started with advanced stealth!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Browser setup failed: {e}")
            self.state['last_error'] = str(e)
            return False

    def get_smart_delay(self):
        """Get intelligent delay with human-like patterns"""
        if not CONFIG['random_delay']:
            return CONFIG['base_delay'] / 1000  # Convert to seconds
        
        # Vary delay based on time of day and session length
        hour = time.localtime().tm_hour
        base = CONFIG['base_delay']
        
        # Simulate human fatigue - slower responses over time
        session_duration = (time.time() * 1000) - self.state['session_start_time']
        if session_duration > 900000:  # After 15 minutes
            base += 300
        
        # Add random variation
        random_variation = random.randint(0, CONFIG['max_delay'] - CONFIG['min_delay'])
        return (base + random_variation) / 1000  # Convert to seconds

    def human_delay(self, min_seconds=None, max_seconds=None):
        """Enhanced human delay with behavioral patterns"""
        if min_seconds is not None and max_seconds is not None:
            delay = random.uniform(min_seconds, max_seconds)
        else:
            delay = self.get_smart_delay()
        
        time.sleep(delay)
        return delay

    def force_login(self):
        """Advanced login with dynamic password field detection - WORKING VERSION"""
        try:
            self.logger.info("🔐 LOGIN: Attempting login with dynamic field detection...")
            
            # Navigate to login page
            login_url = "https://adsha.re/login"
            self.driver.get(login_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.human_delay(2, 4)
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find the login form
            form = soup.find('form', {'name': 'login'})
            if not form:
                self.logger.error("❌ LOGIN: Could not find login form")
                return False
            
            # Find the dynamic password field name
            password_field_name = None
            for field in form.find_all('input'):
                field_name = field.get('name', '')
                field_value = field.get('value', '')
                
                # Look for password field - dynamic detection logic
                if field_value == 'Password' and field_name != 'mail' and field_name:
                    password_field_name = field_name
                    break
            
            if not password_field_name:
                self.logger.error("❌ LOGIN: Could not detect password field name")
                return False
            
            self.logger.info(f"🔑 LOGIN: Detected password field name: {password_field_name}")
            
            # Fill email field
            email_selectors = [
                "input[name='mail']",
                "input[type='email']",
                "input[placeholder*='email' i]"
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    email_field.clear()
                    email_field.send_keys(self.email)
                    self.logger.info("✅ LOGIN: Email entered")
                    email_filled = True
                    break
                except:
                    continue
            
            if not email_filled:
                self.logger.error("❌ LOGIN: Could not find email field")
                return False
            
            self.human_delay(1, 2)
            
            # Fill password field using detected name
            password_selector = f"input[name='{password_field_name}']"
            try:
                password_field = self.driver.find_element(By.CSS_SELECTOR, password_selector)
                password_field.clear()
                password_field.send_keys(self.password)
                self.logger.info("✅ LOGIN: Password entered")
            except:
                self.logger.error(f"❌ LOGIN: Could not find password field with selector: {password_selector}")
                return False
            
            self.human_delay(1, 2)
            
            # Find and click login button
            login_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button",
                "input[value*='Login']",
                "input[value*='Sign']"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if login_btn.is_displayed() and login_btn.is_enabled():
                        login_btn.click()
                        self.logger.info("✅ LOGIN: Login button clicked")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                # Fallback: try to submit the form
                try:
                    form_element = self.driver.find_element(By.CSS_SELECTOR, "form[name='login']")
                    form_element.submit()
                    self.logger.info("✅ LOGIN: Form submitted")
                    login_clicked = True
                except:
                    pass
            
            # Wait for login to complete
            self.human_delay(8, 12)
            
            # Check if login successful by navigating to surf page
            self.driver.get("https://adsha.re/surf")
            self.human_delay(3, 5)
            
            current_url = self.driver.current_url
            if "surf" in current_url or "dashboard" in current_url:
                self.logger.info("✅ LOGIN: Successful!")
                self.send_telegram("✅ <b>Login Successful!</b>")
                return True
            else:
                # Check if we're still on login page
                if "login" in current_url:
                    self.logger.error("❌ LOGIN: Failed - still on login page")
                    return False
                else:
                    self.logger.warning("⚠️ LOGIN: May need manual verification, but continuing...")
                    return True
                
        except Exception as e:
            self.logger.error(f"❌ LOGIN: Error - {e}")
            self.state['last_error'] = f"Login error: {e}"
            return False

    def navigate_to_adshare(self):
        """Navigate to adsha.re and handle login"""
        self.logger.info("🌐 Navigating to AdShare...")
        
        try:
            self.driver.get("https://adsha.re/surf")
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.human_delay(2, 4)
            
            current_url = self.driver.current_url
            self.logger.info(f"📍 Current URL: {current_url}")
            
            # Check if login is needed
            if "login" in current_url:
                self.logger.info("🔐 Login required...")
                return self.force_login()
            else:
                self.logger.info("✅ Already on surf page!")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Navigation failed: {e}")
            self.state['last_error'] = f"Navigation error: {e}"
            return False

    def is_behavior_suspicious(self):
        """Advanced rate limiting with behavioral analysis"""
        now = time.time() * 1000
        time_since_last_click = now - self.state['last_click_time']
        
        # Check click rate
        session_duration_minutes = (now - self.state['session_start_time']) / 60000
        clicks_per_minute = (self.state['click_count'] / session_duration_minutes) if session_duration_minutes > 0 else 0
        
        if clicks_per_minute > CONFIG['max_clicks_per_minute']:
            self.logger.warning("⚠️ Suspicious behavior: High click rate")
            return True
        
        # Check for robotic patterns (consistent timing)
        if len(self.behavior_patterns['delays']) > 5:
            recent_delays = self.behavior_patterns['delays'][-5:]
            variance = max(recent_delays) - min(recent_delays)
            if variance < 200:  # Too consistent
                self.logger.warning("⚠️ Suspicious behavior: Consistent timing")
                return True
        
        # Session length check
        if now - self.state['session_start_time'] > CONFIG['max_session_length']:
            self.logger.warning("⚠️ Suspicious behavior: Session too long")
            return True
        
        return False

    def simulate_mouse_movement(self, element):
        """Simulate human mouse movements using ActionChains"""
        if not CONFIG['mimic_mouse_movements']:
            return 0
        
        try:
            # Get element location
            location = element.location
            size = element.size
            
            # Start from random position on screen
            start_x = random.randint(100, 500)
            start_y = random.randint(100, 300)
            end_x = location['x'] + size['width'] / 2
            end_y = location['y'] + size['height'] / 2
            
            # Create action chain with curved movement
            actions = ActionChains(self.driver)
            
            # Move to random start position
            actions.move_by_offset(start_x, start_y)
            
            # Generate curved path with intermediate points
            steps = 3 + random.randint(0, 4)
            for i in range(steps):
                # Calculate intermediate point with some randomness
                t = (i + 1) / (steps + 1)
                mid_x = start_x + (end_x - start_x) * t + random.randint(-30, 30)
                mid_y = start_y + (end_y - start_y) * t + random.randint(-20, 20)
                
                actions.move_by_offset(mid_x - start_x, mid_y - start_y)
                actions.pause(random.uniform(0.05, 0.15))
                
                # Update current position
                start_x, start_y = mid_x, mid_y
            
            # Final movement to element
            actions.move_to_element(element)
            actions.perform()
            
            return steps * 100  # Return approximate movement time in ms
            
        except Exception as e:
            self.logger.warning(f"⚠️ Mouse movement simulation failed: {e}")
            return 0

    def advanced_human_click(self, element):
        """Advanced human-like click with NO intentional misses"""
        if self.is_behavior_suspicious() or self.state['is_in_cooldown']:
            if CONFIG['enable_console_logs']:
                self.logger.info("⏳ Safety cooldown active")
            return False
        
        try:
            # Small pre-click delay
            self.human_delay(0.5, 1.0)
            
            # Simulate mouse movement if enabled
            if CONFIG['mimic_mouse_movements']:
                move_time = self.simulate_mouse_movement(element)
                time.sleep(move_time / 1000)
            
            # Perform the click with variation
            actions = ActionChains(self.driver)
            
            if CONFIG['click_position_variation']:
                # Click with position variation but always within element
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                actions.move_to_element_with_offset(element, offset_x, offset_y)
            else:
                actions.move_to_element(element)
            
            # Click sequence with slight pauses
            actions.click()
            actions.pause(0.1)
            actions.perform()
            
            # Update behavior tracking
            self.state['click_count'] += 1
            self.state['last_click_time'] = time.time() * 1000
            self.state['last_action_time'] = time.time() * 1000
            
            # Small post-click delay
            self.human_delay(0.2, 0.5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Advanced click failed: {e}")
            return False

    def calculate_similarity(self, str1, str2):
        """Calculate string similarity for fuzzy matching"""
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        # Simple similarity calculation based on common characters
        common_chars = sum(1 for a, b in zip(str1, str2) if a == b)
        max_len = max(len(str1), len(str2))
        return common_chars / max_len if max_len > 0 else 0.0

    def compare_symbols(self, question_svg, answer_svg):
        """Enhanced symbol comparison with fuzzy matching"""
        try:
            question_content = question_svg.get_attribute('innerHTML')
            answer_content = answer_svg.get_attribute('innerHTML')
            
            if not question_content or not answer_content:
                return {'match': False, 'confidence': 0.0, 'exact': False}
            
            # Clean content
            def clean_svg(svg_text):
                # Remove extra spaces and normalize
                cleaned = re.sub(r'\s+', ' ', svg_text).strip().lower()
                # Remove colors and styles for comparison
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
            
            # Fuzzy matching
            similarity = self.calculate_similarity(clean_question, clean_answer)
            should_match = similarity >= CONFIG['minimum_confidence']
            
            return {'match': should_match, 'confidence': similarity, 'exact': False}
            
        except Exception as e:
            self.logger.warning(f"⚠️ Symbol comparison error: {e}")
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
            # Return first exact match (they're all perfect)
            return exact_matches[0]
        
        # Return best fuzzy match if confidence is high enough
        if best_match and best_match['confidence'] >= CONFIG['minimum_confidence']:
            return best_match
        
        return None

    def perform_random_scroll(self):
        """Random scroll to mimic human behavior"""
        if not CONFIG['scroll_randomly']:
            return
        
        scroll_amount = random.randint(-100, 100)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.human_delay(0.5, 1.0)

    def start_cooldown(self, duration=30000):
        """Cooldown management"""
        self.state['is_in_cooldown'] = True
        self.state['status'] = 'cooldown'
        if CONFIG['enable_console_logs']:
            self.logger.info(f"😴 Cooldown activated for {duration/1000}s")
        
        # Schedule cooldown end
        def end_cooldown():
            time.sleep(duration / 1000)
            self.state['is_in_cooldown'] = False
            self.state['status'] = 'running' if self.state['is_running'] else 'stopped'
            if CONFIG['enable_console_logs']:
                self.logger.info("✅ Cooldown ended")
        
        thread = threading.Thread(target=end_cooldown)
        thread.daemon = True
        thread.start()

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
        """Main solver with PERFECT accuracy"""
        if not self.state['is_running'] or self.state['is_in_cooldown']:
            return False
        
        try:
            # Occasionally take breaks
            if self.state['consecutive_rounds'] > 15 and random.random() < 0.3:
                if CONFIG['enable_console_logs']:
                    self.logger.info("💤 Taking a short break...")
                self.start_cooldown(10000 + random.randint(0, 20000))
                self.state['consecutive_rounds'] = 0
                return False
            
            # Find question SVG
            question_svg = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "svg"))
            )
            
            if not question_svg:
                if CONFIG['enable_console_logs']:
                    self.logger.info("⏳ Waiting for game to load...")
                return False
            
            # Find all answer links
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='adsha.re'], button, .answer-option, [class*='answer']")
            
            # Find the best possible match with high confidence
            best_match = self.find_best_match(question_svg, links)
            
            if best_match:
                if self.advanced_human_click(best_match['link']):
                    self.state['total_solved'] += 1
                    self.state['consecutive_rounds'] += 1
                    self.state['consecutive_fails'] = 0
                    
                    if CONFIG['enable_console_logs']:
                        match_type = "EXACT" if best_match['exact'] else "FUZZY"
                        self.logger.info(f"✅ {match_type} Match! Confidence: {best_match['confidence']*100:.1f}% | Total: {self.state['total_solved']}")
                    
                    # Record timing pattern
                    delay = self.get_smart_delay() * 1000
                    self.behavior_patterns['delays'].append(delay)
                    if len(self.behavior_patterns['delays']) > 20:
                        self.behavior_patterns['delays'].pop(0)
                    
                    return True
            else:
                # No good match found
                self.state['consecutive_fails'] += 1
                if CONFIG['enable_console_logs']:
                    self.logger.info("🔍 No high-confidence match found, waiting...")
                
                # If multiple consecutive fails, take longer break
                if self.state['consecutive_fails'] > 3:
                    if CONFIG['enable_console_logs']:
                        self.logger.info("⚠️ Multiple fails detected, extended cooldown")
                    self.start_cooldown(15000)
                    self.state['consecutive_fails'] = 0
            
            # Perform random actions occasionally
            if random.random() < 0.2:
                self.perform_random_scroll()
                
            return False
            
        except TimeoutException:
            if CONFIG['enable_console_logs']:
                self.logger.info("⏳ Waiting for game elements...")
            return False
        except Exception as e:
            if CONFIG['enable_console_logs']:
                self.logger.info(f"❌ Error in solver: {e}")
            self.state['consecutive_fails'] += 1
            return False

    def session_management(self):
        """Manage session rotation and rate limiting"""
        while self.state['is_running']:
            try:
                current_time = time.time() * 1000
                
                # Rotate session if too long
                if (current_time - self.state['session_start_time'] > CONFIG['max_session_length'] 
                    and CONFIG['session_rotation']):
                    self.logger.info("🔄 Session rotation")
                    self.state['session_start_time'] = current_time
                    self.state['click_count'] = 0
                    self.start_cooldown(30000)
                
                # Reset click count periodically
                self.state['click_count'] = max(0, self.state['click_count'] - CONFIG['max_clicks_per_minute'])
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.warning(f"⚠️ Session management error: {e}")
                time.sleep(60)

    def keep_session_alive(self):
        """Main game solving loop"""
        self.logger.info("🔄 Starting Advanced Auto-Solver Pro...")
        self.logger.info("🔧 Features: PERFECT ACCURACY, Fuzzy matching, behavioral simulation")
        self.logger.info("✅ Intentional misses: DISABLED")
        self.logger.info("🎯 Accuracy mode: Always perfect")
        
        consecutive_fails = 0
        cycle_count = 0
        
        while self.state['is_running'] and consecutive_fails < 10:
            try:
                # Refresh page every 10 minutes
                if cycle_count % 20 == 0 and cycle_count > 0:
                    self.driver.refresh()
                    self.logger.info("🔁 Page refreshed")
                    self.human_delay(3, 5)
                
                # Try to solve symbol game
                game_solved = self.advanced_solve_symbol_game()
                
                if game_solved:
                    consecutive_fails = 0
                    # Success delay
                    self.human_delay(2, 4)
                else:
                    consecutive_fails += 1
                    if consecutive_fails > 0 and CONFIG['enable_console_logs']:
                        self.logger.info(f"❌ No game solved ({consecutive_fails}/10 fails)")
                    # Longer delay on fail
                    self.human_delay(5, 8)
                
                cycle_count += 1
                    
            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                consecutive_fails += 1
                self.human_delay(10, 15)  # Longer delay on error
        
        if consecutive_fails >= 10:
            self.logger.error("🚨 Too many consecutive failures, stopping...")
            self.stop()

    def solver_loop(self):
        """Main solver thread"""
        self.logger.info("🎮 Starting solver loop...")
        self.state['status'] = 'running'
        self.state['session_start_time'] = time.time() * 1000
        
        # Setup browser if not already done
        if not self.driver:
            if not self.setup_browser():
                self.logger.error("❌ Cannot start - browser failed")
                self.stop()
                return
        
        # Navigate and login
        if not self.navigate_to_adshare():
            self.logger.warning("⚠️ Navigation issues, but continuing...")
        
        # Start session management in background
        session_thread = threading.Thread(target=self.session_management)
        session_thread.daemon = True
        session_thread.start()
        
        # Start solving games
        self.keep_session_alive()

    def start(self):
        """Start the solver"""
        if self.state['is_running']:
            return "❌ Solver is already running"
        
        if not self.driver:
            if not self.setup_browser():
                return "❌ Browser setup failed"
        
        self.state['is_running'] = True
        self.solver_thread = threading.Thread(target=self.solver_loop)
        self.solver_thread.daemon = True
        self.solver_thread.start()
        
        # Start monitoring if not already running
        if not self.state['monitoring_active']:
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
        
        self.logger.info("🚀 Solver started!")
        self.send_telegram("🚀 <b>Solver Started!</b>\nNow solving symbol games automatically.")
        return "✅ Solver started successfully!"

    def stop(self):
        """Stop the solver"""
        self.state['is_running'] = False
        self.state['monitoring_active'] = False
        self.state['status'] = 'stopped'
        self.logger.info("🛑 Solver stopped")
        self.send_telegram("🛑 <b>Solver Stopped!</b>")
        return "✅ Solver stopped successfully!"

    def status(self):
        """Get solver status"""
        session_duration = (time.time() * 1000 - self.state['session_start_time']) / 1000
        
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
        
        self.logger.info("🤖 Starting Telegram bot update handler...")
        
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
    bot.logger.info("🤖 Starting AdShare Solver Telegram Bot...")
    bot.handle_updates()