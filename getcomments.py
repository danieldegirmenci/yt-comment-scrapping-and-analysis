from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json
import time

def setup_driver():
    # WebDriver ayarlarını yapılandırın ve YouTube videosunun URL'sini ziyaret edin
    options = webdriver.ChromeOptions()
    # Headless mod için pencere boyutunu belirleyin
    # ChromeDriver'ın yolu doğru şekilde belirtilmelidir.
    driver = webdriver.Chrome(options=options)
    return driver

def load_comments(driver, timeout=30):
    # Sayfayı aşağı kaydırarak daha fazla yorum yükleyin
    start_time = time.time()
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(1)  # Sayfanın yüklenmesi için biraz bekleyin
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height or (time.time() - start_time) > timeout:
            break
        last_height = new_height

def fetch_comments(driver):
    # Yüklenen yorumları bir Python listesine ekleyin
    comments = []
    comment_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-comment-thread-renderer")
    for comment_element in comment_elements:
        try:
            comment_text = comment_element.find_element(By.CSS_SELECTOR, "#content-text").text
            comment_author = comment_element.find_element(By.CSS_SELECTOR, "#author-text").text
            like_count_element = comment_element.find_element(By.CSS_SELECTOR, "#vote-count-middle")
            like_count = like_count_element.text if like_count_element.text else "0"
            
            # Kanal üyesi rozetini kontrol edin
            is_channel_member = False
            # Kanal üyeliği rozeti kontrolü - daha kesin bir kontrol
            member_badges = comment_element.find_elements(By.CSS_SELECTOR, "ytd-sponsor-comment-badge-renderer:not([hidden]), span#sponsor-comment-badge:not([hidden])")
            if member_badges:
                is_channel_member = True
            
            comment_data = {
                "nickname": comment_author,
                "comment": comment_text,
                "like_count": like_count,
                "is_channel_member": is_channel_member
            }
            comments.append(comment_data)
        except NoSuchElementException:
            continue  # Eksik element varsa yoruma atla
    return comments

def save_comments_to_file(comments, file_name="comments.json"):
    # Yorumları JSON dosyasına yazın
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(comments, file, ensure_ascii=False, indent=4)

def main():
    driver = setup_driver()
    video_url = "YT-VIDEO_URL"
    driver.get(video_url)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-comments#comments")))
    except TimeoutException:
        print("Yorumlar bölümü zaman aşımına uğradı.")
        driver.quit()
        return
    
    load_comments(driver)
    comments = fetch_comments(driver)
    save_comments_to_file(comments)
    driver.quit()

if __name__ == "__main__":
    main()
