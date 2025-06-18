from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import logging
from selenium.webdriver import ActionChains

# Move logging configuration outside the function
logging.basicConfig(
    filename='video_test.log',
    level=logging.ERROR,  # Changed to ERROR level
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
)

def test_video_playback(url):
    # Remove the logging configuration from here
    
    # Initialize the webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Add service configuration
    service = webdriver.ChromeService()
    
    # Create the driver instance with service
    driver = webdriver.Chrome(service=service, options=options)
    # Initialize WebDriverWait
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navigate to the URL
        driver.get(url)
        time.sleep(4)
        
        # Get window size and calculate center point
        window_width = driver.execute_script("return window.innerWidth")
        window_height = driver.execute_script("return window.innerHeight")
        center_x = window_width // 2
        center_y = window_height // 2
        logging.info(f"Calculated screen center: ({center_x}, {center_y})")
        
        # Create action chain to move to center and click
        logging.info("Attempting to click center of screen")
        actions = ActionChains(driver)
        actions.move_by_offset(center_x, center_y).click().perform()
        logging.info("Successfully clicked center of screen")
        
        # Wait for iframe to load
        logging.info("Waiting 5 seconds for iframe to load...")
        time.sleep(1)
        
        # Find and switch to YouTube iframe
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        iframe_count = len(iframes)
        logging.info(f"Found {iframe_count} iframes on page")
        
        youtube_iframe_found = False
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if "youtube" in src.lower():
                driver.switch_to.frame(iframe)
                youtube_iframe_found = True
                logging.info(f"Switched to YouTube iframe with src: {src}")
                break
        
        if not youtube_iframe_found:
            logging.error(f"✗ No YouTube iframe found - URL: {url}")
            return
            
        # Click YouTube play button if present
        try:
            youtube_play = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-large-play-button")))
            youtube_play.click()
        except:
            pass  # Skip if button not found
        
        # Wait and check if video is playing
        time.sleep(1)
        logging.info("Checking video playback status...")
        
        is_playing = driver.execute_script("""
            return document.getElementsByTagName('video')[0] && 
                   !document.getElementsByTagName('video')[0].paused;
        """)
        if is_playing:
            time.sleep(1)
            
            # Check if video is still playing after 5 seconds
            is_still_playing = driver.execute_script("""
                return document.getElementsByTagName('video')[0] && 
                       !document.getElementsByTagName('video')[0].paused;
            """)
            if is_still_playing:
                pass  # Success case - no logging needed
            else:
                logging.error(f"✗ Video stopped during playback - URL: {url}")
        else:
            logging.error(f"✗ Video failed to start playing - URL: {url}")
            
    except TimeoutException:
        logging.error(f"✗ Video element not found - URL: {url}")
    except Exception as e:
        logging.error(f"✗ Error testing URL {url}: {str(e)}")
    finally:
        driver.quit()
        logging.info("✓ Browser closed successfully")

if __name__ == "__main__":
    base_url = "base_url"
    start_num = 19287
    end_num = 28900
    step = 1
    
    logging.info("\n\n" + "="*50)
    logging.info("Starting new test session")
    logging.info("="*50 + "\n")
    
    # Generate URLs and test each one
    for video_id in range(start_num, end_num + 1, step):
        video_url = f"{base_url}{video_id}"
        logging.info(f"\n{'='*50}")
        logging.info(f"Testing URL #{video_id}")
        logging.info(f"{'='*50}\n")
        test_video_playback(video_url)
        
        # Add a small delay between tests
        time.sleep(2)