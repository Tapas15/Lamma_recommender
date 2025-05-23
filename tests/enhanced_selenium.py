"""
Enhanced Selenium Helpers

This module provides enhanced Selenium functions for more robust element interactions,
making the visual workflow more reliable.
"""

import time
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException
)

def wait_for_element(driver, locator_type, locator_value, timeout=10, visible=True):
    """
    Wait for an element to be present/visible and return it
    
    Args:
        driver: Selenium WebDriver instance
        locator_type: By type (e.g., By.ID, By.XPATH)
        locator_value: The locator value
        timeout: Maximum time to wait (seconds)
        visible: Whether to wait for visibility (True) or just presence (False)
        
    Returns:
        The found WebElement or None
    """
    try:
        wait = WebDriverWait(driver, timeout)
        condition = (
            EC.visibility_of_element_located if visible else 
            EC.presence_of_element_located
        )
        element = wait.until(condition((locator_type, locator_value)))
        return element
    except Exception as e:
        print(f"⚠️ Element not found: {locator_type}='{locator_value}', Error: {type(e).__name__}")
        return None

def find_element_with_alternatives(driver, locators, timeout=10, visible=True):
    """
    Try multiple locator strategies to find an element
    
    Args:
        driver: Selenium WebDriver instance
        locators: List of tuples (locator_type, locator_value)
        timeout: Maximum time to wait for each locator (seconds)
        visible: Whether to wait for visibility (True) or just presence (False)
        
    Returns:
        The found WebElement or None
    """
    for locator_type, locator_value in locators:
        element = wait_for_element(driver, locator_type, locator_value, timeout=timeout/len(locators), visible=visible)
        if element:
            return element
    
    print(f"❌ Element not found after trying {len(locators)} alternative locators")
    return None

def scroll_to_element_enhanced(driver, element, smooth=True, center=True):
    """
    Enhanced scrolling to element with smooth animation and centering
    
    Args:
        driver: Selenium WebDriver instance
        element: Target WebElement
        smooth: Whether to use smooth scrolling
        center: Whether to center the element in the viewport
    """
    try:
        if smooth:
            driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'center'
                });
            """, element)
        else:
            if center:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            else:
                driver.execute_script("arguments[0].scrollIntoView();", element)
        
        # Small pause to let the scroll complete
        time.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"⚠️ Error scrolling to element: {e}")
        # Fallback to basic scroll
        try:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(0.5)
            return True
        except:
            return False

def highlight_element_enhanced(driver, element, duration=1.0, style="background", pulsate=False):
    """
    Enhanced element highlighting with different styles and pulsate effect
    
    Args:
        driver: Selenium WebDriver instance
        element: Target WebElement
        duration: How long to highlight (seconds)
        style: Highlight style ("background", "outline", or "border")
        pulsate: Whether to create a pulsating effect
    """
    original_style = element.get_attribute("style")
    
    # Define styles
    styles = {
        "background": "background-color: yellow; border: 2px solid red;",
        "outline": "outline: 4px solid red; outline-offset: 2px;",
        "border": "border: 4px solid red !important;"
    }
    
    highlight_style = styles.get(style, styles["background"])
    
    try:
        if pulsate:
            # Create pulsating effect
            pulses = 4  # Number of pulses
            for i in range(pulses):
                # Fade in
                driver.execute_script(
                    f"arguments[0].setAttribute('style', '{highlight_style} transition: all 0.25s ease-in-out; opacity: 1;');", 
                    element
                )
                time.sleep(duration/(pulses*2))
                
                # Fade out
                driver.execute_script(
                    f"arguments[0].setAttribute('style', '{highlight_style} transition: all 0.25s ease-in-out; opacity: 0.3;');",
                    element
                )
                time.sleep(duration/(pulses*2))
        else:
            # Simple highlight
            driver.execute_script(
                f"arguments[0].setAttribute('style', '{highlight_style}');", 
                element
            )
            time.sleep(duration)
        
        # Restore original style
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);", 
            element, 
            original_style
        )
        
        return True
    except Exception as e:
        print(f"⚠️ Error highlighting element: {e}")
        return False

def click_with_retry_enhanced(driver, element, max_retries=3, scroll=True, highlight=True):
    """
    Enhanced click with retry logic and visual feedback
    
    Args:
        driver: Selenium WebDriver instance
        element: Target WebElement to click
        max_retries: Maximum number of retries
        scroll: Whether to scroll to the element first
        highlight: Whether to highlight the element
        
    Returns:
        True if click was successful, False otherwise
    """
    retries = 0
    
    while retries < max_retries:
        try:
            # Scroll to element first if requested
            if scroll:
                scroll_to_element_enhanced(driver, element)
            
            # Highlight element if requested
            if highlight:
                highlight_element_enhanced(driver, element, duration=0.5)
            
            # Try standard click first
            element.click()
            return True
        
        except StaleElementReferenceException:
            # If element is stale, we need to refind it using the same method
            print(f"⚠️ Element is stale, retrying... ({retries+1}/{max_retries})")
            time.sleep(1)
            
        except ElementClickInterceptedException:
            # Something is blocking the click, try JavaScript click
            print(f"⚠️ Element click intercepted, trying JavaScript click... ({retries+1}/{max_retries})")
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ Click failed, retrying... ({retries+1}/{max_retries}): {e}")
            
        retries += 1
        time.sleep(1)
    
    print(f"❌ Failed to click element after {max_retries} attempts")
    
    # Last resort - Try to use Action chains
    try:
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
        print("✅ Click successful using Action Chains")
        return True
    except:
        return False

def fill_input_enhanced(driver, element, value, clear_first=True, click_first=True, slow_typing=False):
    """
    Enhanced input field interaction with human-like typing
    
    Args:
        driver: Selenium WebDriver instance
        element: Target input WebElement
        value: Value to enter
        clear_first: Whether to clear the field first
        click_first: Whether to click the field first
        slow_typing: Whether to simulate human-like typing (slower)
        
    Returns:
        True if the operation was successful, False otherwise
    """
    try:
        # Click the element first if requested
        if click_first:
            try:
                element.click()
            except:
                # Fall back to JavaScript click if regular click fails
                driver.execute_script("arguments[0].click();", element)
        
        # Clear the field first if requested
        if clear_first:
            try:
                element.clear()
            except:
                # If clear() fails, try to select all and delete
                element.send_keys("\u0001")  # CTRL+A to select all text
                element.send_keys("\b")      # Backspace to delete
        
        # Enter the value
        if slow_typing:
            # Simulate human-like typing
            for char in value:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Random delay between keystrokes
        else:
            element.send_keys(value)
        
        return True
    
    except Exception as e:
        print(f"⚠️ Error filling input: {e}")
        
        # Try one more time with JavaScript as fallback
        try:
            driver.execute_script(f"arguments[0].value = '{value}';", element)
            return True
        except:
            return False

def select_option_from_dropdown(driver, dropdown_element, option_text, by_value=False, by_index=False):
    """
    Enhanced select option from dropdown with multiple selection methods
    
    Args:
        driver: Selenium WebDriver instance
        dropdown_element: The dropdown WebElement
        option_text: The option text, value, or index to select
        by_value: Set to True if option_text is actually the value attribute
        by_index: Set to True if option_text is actually the index (as string)
        
    Returns:
        True if selection was successful, False otherwise
    """
    try:
        # Click to open dropdown
        click_with_retry_enhanced(driver, dropdown_element)
        time.sleep(0.5)
        
        # Try to find the option by different methods
        if by_value:
            # Find option by value attribute
            option = driver.find_element_by_css_selector(f"option[value='{option_text}']")
        elif by_index:
            # Find option by index
            options = dropdown_element.find_elements_by_tag_name("option")
            option = options[int(option_text)]
        else:
            # Regular method - find option containing the text
            option = driver.find_element_by_xpath(f"//option[contains(text(), '{option_text}')]")
        
        # Click the option
        click_with_retry_enhanced(driver, option)
        return True
        
    except Exception as e:
        print(f"⚠️ Error selecting dropdown option: {e}")
        
        # Try an alternative approach for Streamlit-specific dropdowns
        try:
            # Try to find and click option in a more generic way
            options = driver.find_elements_by_xpath(f"//div[contains(@role, 'option') and contains(text(), '{option_text}')]")
            if options and len(options) > 0:
                click_with_retry_enhanced(driver, options[0])
                return True
        except:
            pass
            
        # Use JavaScript as a last resort
        try:
            if by_value:
                driver.execute_script(f"arguments[0].value = '{option_text}';", dropdown_element)
            elif by_index:
                driver.execute_script(f"arguments[0].selectedIndex = {option_text};", dropdown_element)
            else:
                # This is less reliable but worth a try
                driver.execute_script(f"""
                    var select = arguments[0];
                    for(var i=0; i<select.options.length; i++) {{
                        if(select.options[i].text.includes('{option_text}')) {{
                            select.selectedIndex = i;
                            break;
                        }}
                    }}
                """, dropdown_element)
            return True
        except:
            return False 