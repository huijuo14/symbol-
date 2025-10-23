#!/usr/bin/env python3
"""
AdShare Symbol Game Solver - Pure Selenium Automation
"""

import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
EMAIL = "loginallapps@gmail.com"
PASSWORD = "@Sd2007123"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SymbolGameSolver:
    def __init__(self):
        self.driver = None
        self.monitoring = False
        self.total_solved = 0
        self.session_start = time.time()
        
    def setup_browser(self):
        """Setup Firefox with minimal settings"""
        logger.info("🦊 Starting Firefox...")
        
        options = Options()
        options.headless = True
        
        # ABSOLUTE MINIMUM preferences
        options.set_preference("dom.ipc.processCount", 1)
        options.set_preference("browser.tabs.remote.autostart", False)
        options.set_preference("javascript.options.mem.max", 50000000)  # 50MB
        
        # Essential arguments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        try:
            self.driver = webdriver.Firefox(options=options)
            self.driver.set_window_size(1200, 800)
            logger.info("✅ Firefox started successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Browser setup failed: {e}")
            return False

    def human_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def navigate_to_adshare(self):
        """Navigate to adsha.re and login"""
        logger.info("🌐 Navigating to AdShare...")
        
        try:
            self.driver.get("https://adsha.re/surf")
            
            # Wait for page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.human_delay(2, 4)
            
            current_url = self.driver.current_url
            logger.info(f"📍 Current URL: {current_url}")
            
            # Check if login is needed
            if "login" in current_url:
                logger.info("🔐 Login required...")
                return self.perform_login()
            else:
                logger.info("✅ Already on surf page!")
                return True
                
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False

    def perform_login(self):
        """Perform login with multiple selector attempts"""
        try:
            # Email field
            email_selectors = [
                "input[name='mail']",
                "input[type='email']",
                "input[placeholder*='email' i]"
            ]
            
            for selector in email_selectors:
                try:
                    email_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    email_field.clear()
                    email_field.send_keys(EMAIL)
                    logger.info("✅ Email entered")
                    break
                except:
                    continue
            
            self.human_delay(1, 2)
            
            # Password field
            password_selectors = [
                "input[type='password']",
                "input[name='password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    password_field.clear()
                    password_field.send_keys(PASSWORD)
                    logger.info("✅ Password entered")
                    break
                except:
                    continue
            
            self.human_delay(1, 2)
            
            # Login button
            login_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "a.button[onclick*='submit']"
            ]
            
            for selector in login_selectors:
                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    login_btn.click()
                    logger.info("✅ Login button clicked")
                    break
                except:
                    continue
            
            # Wait for login to complete
            self.human_delay(8, 12)
            
            # Check if login successful
            if "surf" in self.driver.current_url:
                logger.info("✅ Login successful!")
                return True
            else:
                logger.warning("⚠️ Login may need manual verification")
                return True  # Continue anyway
                
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False

    def extract_svg_content(self, svg_element):
        """Extract SVG content for comparison"""
        try:
            return svg_element.get_attribute('innerHTML').strip()
        except:
            return ""

    def compare_symbols(self, question_svg, answer_svg):
        """Compare two SVG elements for matching"""
        try:
            question_content = self.extract_svg_content(question_svg)
            answer_content = self.extract_svg_content(answer_svg)
            
            # Clean content for comparison
            def clean_svg(svg_text):
                return (svg_text
                        .replace(' ', '')
                        .replace('\n', '')
                        .replace('\t', '')
                        .lower())
            
            question_clean = clean_svg(question_content)
            answer_clean = clean_svg(answer_content)
            
            # Exact match
            if question_clean == answer_clean:
                return True, 1.0
            
            # Check if they share significant similarity
            if len(question_clean) > 10 and len(answer_clean) > 10:
                common_chars = sum(1 for a, b in zip(question_clean, answer_clean) if a == b)
                similarity = common_chars / max(len(question_clean), len(answer_clean))
                
                if similarity > 0.8:  # 80% similarity threshold
                    return True, similarity
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"❌ Symbol comparison error: {e}")
            return False, 0.0

    def find_symbol_game_elements(self):
        """Find the symbol game question and answers"""
        try:
            # Find question SVG (the symbol to match)
            question_svg = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "svg"))
            )
            
            # Find all answer links/buttons
            answer_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='adsha.re'], button, .answer-option, [class*='answer']")
            
            if question_svg and answer_links:
                logger.info(f"🎯 Found symbol game: 1 question, {len(answer_links)} answers")
                return question_svg, answer_links
            else:
                return None, None
                
        except TimeoutException:
            return None, None
        except Exception as e:
            logger.error(f"❌ Error finding game elements: {e}")
            return None, None

    def solve_symbol_game(self):
        """Solve one round of the symbol matching game"""
        try:
            question_svg, answer_links = self.find_symbol_game_elements()
            
            if not question_svg or not answer_links:
                logger.info("🔍 No symbol game detected")
                return False
            
            logger.info("🎮 Solving symbol game...")
            
            # Compare question with each answer
            best_match = None
            highest_confidence = 0
            
            for answer_link in answer_links:
                try:
                    # Find SVG in this answer
                    answer_svg = answer_link.find_element(By.CSS_SELECTOR, "svg")
                    if answer_svg:
                        matches, confidence = self.compare_symbols(question_svg, answer_svg)
                        
                        if matches and confidence > highest_confidence:
                            highest_confidence = confidence
                            best_match = answer_link
                            
                            # If we found a perfect match, use it immediately
                            if confidence == 1.0:
                                break
                except:
                    continue
            
            # Click the best match
            if best_match and highest_confidence > 0.7:  # 70% confidence threshold
                logger.info(f"✅ Found match with {highest_confidence:.1%} confidence")
                
                # Human-like delay before clicking
                self.human_delay(1, 2)
                
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", best_match)
                self.human_delay(0.5, 1)
                
                # Click the answer
                best_match.click()
                self.total_solved += 1
                logger.info(f"🎯 Clicked answer! Total solved: {self.total_solved}")
                
                # Wait for next round
                self.human_delay(3, 5)
                return True
            else:
                logger.info("❌ No confident match found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error solving symbol game: {e}")
            return False

    def check_credits(self):
        """Check current credit balance"""
        try:
            page_text = self.driver.page_source.lower()
            if "credits" in page_text:
                # Simple credit extraction
                import re
                credit_match = re.search(r'(\d[\d,]*) credits', page_text)
                if credit_match:
                    credits = credit_match.group(1)
                    logger.info(f"💰 Current credits: {credits}")
                    return credits
            return "Unknown"
        except:
            return "Error"

    def keep_session_alive(self):
        """Keep the session active and solve games"""
        logger.info("🔄 Starting symbol game solver...")
        self.monitoring = True
        
        consecutive_fails = 0
        cycle_count = 0
        
        while self.monitoring and consecutive_fails < 5:
            try:
                # Refresh page every 10 minutes
                if cycle_count % 6 == 0:
                    self.driver.refresh()
                    logger.info("🔁 Page refreshed")
                    self.human_delay(3, 5)
                
                # Try to solve symbol game
                game_solved = self.solve_symbol_game()
                
                if game_solved:
                    consecutive_fails = 0
                else:
                    consecutive_fails += 1
                    logger.info(f"❌ No game solved ({consecutive_fails}/5 fails)")
                
                # Check credits every 30 minutes
                if cycle_count % 18 == 0:
                    self.check_credits()
                
                cycle_count += 1
                
                # Wait before next attempt
                self.human_delay(10, 15)  # Wait 10-15 seconds between attempts
                    
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                consecutive_fails += 1
                self.human_delay(30, 60)  # Longer delay on error
        
        if consecutive_fails >= 5:
            logger.error("🚨 Too many consecutive failures, stopping...")

    def run(self):
        """Main function"""
        logger.info("🚀 Starting AdShare Symbol Game Solver")
        
        # Setup browser
        if not self.setup_browser():
            logger.error("💥 Cannot start - browser failed")
            return
        
        # Navigate and login
        if not self.navigate_to_adshare():
            logger.warning("⚠️ Navigation issues, but continuing...")
        
        # Start solving games
        self.keep_session_alive()
        
        # Cleanup
        self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up...")
        self.monitoring = False
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        logger.info("✅ Solver stopped")

def main():
    solver = SymbolGameSolver()
    
    try:
        solver.run()
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        solver.cleanup()
    except Exception as e:
        logger.error(f"💥 Solver crashed: {e}")
        solver.cleanup()
        raise

if __name__ == '__main__':
    main()
