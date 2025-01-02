import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import pandas as pd
import time
import json

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    return driver

def scrape_elements(url):
    try:
        driver = setup_driver()
        
        with st.spinner(f"Accessing URL: {url}"):
            driver.get(url)
            time.sleep(5)
        
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="draggable-screenshot-image"]')
        st.info(f"Found {len(elements)} matching elements")
        
        all_elements_data = []
        
        progress_bar = st.progress(0)
        for idx, element in enumerate(elements, 1):
            element_data = {
                'element_index': idx,
                'main_div': {
                    'tag': 'div',
                    'classes': element.get_attribute('class'),
                    'data-testid': element.get_attribute('data-testid'),
                    'styles': driver.execute_script("""
                        var styles = window.getComputedStyle(arguments[0]);
                        return {
                            'position': styles.position,
                            'display': styles.display,
                            'alignItems': styles.alignItems,
                            'justifyContent': styles.justifyContent,
                            'backgroundColor': styles.backgroundColor,
                            'width': styles.width,
                            'height': styles.height
                        };
                    """, element)
                }
            }
            
            try:
                img = element.find_element(By.TAG_NAME, 'img')
                element_data['image'] = {
                    'src': img.get_attribute('src'),
                    'class': img.get_attribute('class'),
                    'inline_style': img.get_attribute('style'),
                    'data-testid': img.get_attribute('data-testid'),
                    'computed_styles': driver.execute_script("""
                        var styles = window.getComputedStyle(arguments[0]);
                        return {
                            'position': styles.position,
                            'display': styles.display,
                            'transform': styles.transform,
                            'transition': styles.transition,
                            'cursor': styles.cursor,
                            'borderRadius': styles.borderRadius,
                            'width': styles.width,
                            'height': styles.height
                        };
                    """, img)
                }
            except Exception as e:
                st.warning(f"Error getting image element {idx}: {e}")
            
            try:
                pointer = element.find_element(By.CSS_SELECTOR, 'div[data-testid="action-click-target"]')
                element_data['pointer'] = {
                    'class': pointer.get_attribute('class'),
                    'inline_style': pointer.get_attribute('style'),
                    'data-testid': pointer.get_attribute('data-testid'),
                    'computed_styles': driver.execute_script("""
                        var styles = window.getComputedStyle(arguments[0]);
                        return {
                            'position': styles.position,
                            'pointerEvents': styles.pointerEvents,
                            'overflow': styles.overflow,
                            'borderRadius': styles.borderRadius,
                            'borderWidth': styles.borderWidth,
                            'borderColor': styles.borderColor,
                            'backgroundColor': styles.backgroundColor,
                            'transition': styles.transition,
                            'transform': styles.transform,
                            'width': styles.width,
                            'height': styles.height,
                            'left': styles.left,
                            'top': styles.top
                        };
                    """, pointer)
                }
            except Exception as e:
                st.warning(f"Error getting pointer element {idx}: {e}")
            
            all_elements_data.append(element_data)
            progress_bar.progress((idx) / len(elements))
            
        return all_elements_data
        
    except Exception as e:
        st.error(f"Error during scraping: {e}")
        return None
        
    finally:
        if 'driver' in locals():
            driver.quit()

def main():
    st.title("Web Element Style Scraper")
    
    url = st.text_input("Enter the URL to scrape:")
    
    if st.button("Start Scraping"):
        if url:
            data = scrape_elements(url)
            
            if data:
                # Display results in expandable sections
                for elem in data:
                    with st.expander(f"Element {elem['element_index']}"):
                        st.json(elem)
                
                # Provide download buttons
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name="scraped_elements.json",
                    mime="application/json"
                )
                
                # Convert to DataFrame for CSV download
                df = pd.json_normalize(data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="scraped_elements.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Please enter a URL")

if __name__ == "__main__":
    main()