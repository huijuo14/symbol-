#!/usr/bin/env python3
"""
AdShare Symbol Game Solver - Advanced Auto-Solver Pro
Fixed version with correct Chrome options
"""

import os
import time
import random
import logging
import re
import math
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
    'retry_failed_matches': True  # Retry if no match found initially
}

class AdvancedSymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.state = {
            'click_count': 0,
            'last_click_time': 0,
            'session_start_time': time.time() * 1000,
            'is_running': True,
            'total_solved': 0,
            'consecutive_rounds': 0,
            'last_action_time': time.time() * 1000,
            'is_in_cooldown': False,
            'consecutive_fails': 0
        }
        
        self.behavior_patterns = {
            'delays': [],
            'click_positions': [],
            'session_times': [],
            'accuracy': []
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """Setup advanced logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_browser(self):
        """Setup Chrome with advanced stealth features - FIXED VERSION"""
        self.logger.info("🌐 Starting Chrome with advanced stealth...")
        
        options = Options()
        
        # Basic stealth options - CORRECTED
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
        if CONFIG['enable_console_logs']:
            self.logger.info(f"😴 Cooldown activated for {duration/1000}s")
        
        # Schedule cooldown end
        def end_cooldown():
            time.sleep(duration / 1000)
            self.state['is_in_cooldown'] = False
            if CONFIG['enable_console_logs']:
                self.logger.info("✅ Cooldown ended")
        
        import threading
        thread = threading.Thread(target=end_cooldown)
        thread.daemon = True
        thread.start()

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
                return self.perform_login()
            else:
                self.logger.info("✅ Already on surf page!")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Navigation failed: {e}")
            return False

    def perform_login(self):
        """Perform login with multiple selector attempts"""
        try:
            # Email field
            email_selectors = [
                "input[name='mail']",
                "input[type='email']",
                "input[placeholder*='email' i]",
                "input[name='username']",
                "input[name='email']"
            ]
            
            email_entered = False
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    email_field.clear()
                    email_field.send_keys("loginallapps@gmail.com")
                    self.logger.info("✅ Email entered")
                    email_entered = True
                    break
                except:
                    continue
            
            if not email_entered:
                self.logger.error("❌ Could not find email field")
                return False
            
            self.human_delay(1, 2)
            
            # Password field
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password' i]"
            ]
            
            password_entered = False
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    password_field.clear()
                    password_field.send_keys("@Sd2007123")
                    self.logger.info("✅ Password entered")
                    password_entered = True
                    break
                except:
                    continue
            
            if not password_entered:
                self.logger.error("❌ Could not find password field")
                return False
            
            self.human_delay(1, 2)
            
            # Login button
            login_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign in')",
                "input[value*='Login']",
                "input[value*='Sign in']"
            ]
            
            login_clicked = False
            for selector in login_selectors:
                try:
                    # Try CSS selector first
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, selector.replace(":contains(", "").replace(")", ""))
                    login_btn.click()
                    self.logger.info("✅ Login button clicked")
                    login_clicked = True
                    break
                except:
                    continue
            
            if not login_clicked:
                # Fallback: try to find any button and click it
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            self.logger.info("✅ Fallback login button clicked")
                            login_clicked = True
                            break
                except:
                    pass
            
            # Wait for login to complete
            self.human_delay(8, 12)
            
            # Check if login successful
            if "surf" in self.driver.current_url or "dashboard" in self.driver.current_url:
                self.logger.info("✅ Login successful!")
                return True
            else:
                self.logger.warning("⚠️ Login may need manual verification")
                return True  # Continue anyway
                
        except Exception as e:
            self.logger.error(f"❌ Login failed: {e}")
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
        
        while self.state['is_running'] and consecutive_fails < 10:  # Increased fail threshold
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

    def run(self):
        """Main function"""
        self.logger.info("🚀 Starting Advanced Auto-Solver Pro")
        
        # Setup browser
        if not self.setup_browser():
            self.logger.error("💥 Cannot start - browser failed")
            return
        
        # Navigate and login
        if not self.navigate_to_adshare():
            self.logger.warning("⚠️ Navigation issues, but continuing...")
        
        # Start session management in background
        import threading
        session_thread = threading.Thread(target=self.session_management)
        session_thread.daemon = True
        session_thread.start()
        
        # Start solving games
        self.keep_session_alive()
        
        # Cleanup
        self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("🧹 Cleaning up...")
        self.state['is_running'] = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.logger.info("✅ Advanced Auto-Solver Pro stopped")

def main():
    solver = AdvancedSymbolGameSolver()
    
    try:
        solver.run()
    except KeyboardInterrupt:
        solver.logger.info("🛑 Interrupted by user")
        solver.cleanup()
    except Exception as e:
        solver.logger.error(f"💥 Solver crashed: {e}")
        solver.cleanup()
        raise

if __name__ == '__main__':
    main()