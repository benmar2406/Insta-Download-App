from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from docx import Document
import os
from io import BytesIO
from PIL import Image
import urllib.request
import credentials



#Initialize Chromedriver and Browser
chromedriver_path = '/usr/local/bin/chromedriver'
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
wait = WebDriverWait(driver, 20)



# Navigate to insta and log in. Not that the direct link to the specific collection needs to be included
driver.get(credentials.insta_url_to_collection)

privacy_popup = wait.until(
    EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Alle Cookies erlauben')]"))
)

#Agree to cookies 
privacy_popup = driver.find_element(By.XPATH, "//button[contains(text(), 'Alle Cookies erlauben')]")
privacy_popup.click()


username_input = wait.until(
    EC.visibility_of_element_located((By.NAME, 'username'))
)
password_input = wait.until(
    EC.visibility_of_element_located((By.NAME, 'password'))
)

#enter logindata
username_input = driver.find_element(By.NAME, 'username')
password_input = driver.find_element(By.NAME, 'password')

username = credentials.insta_username  
password = credentials.insta_userpassword      

username_input.send_keys(username)
password_input.send_keys(password)

password_input.send_keys(Keys.RETURN)

#Don't save login data
time.sleep(10)
jetzt_nicht_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Jetzt nicht')]")
jetzt_nicht_button.click()


time.sleep(10)

#get texts and images from posts saved in a specific collection
try:
    recipes = driver.find_elements(By.TAG_NAME, "img")
    
    #texte
    alt_texts = [recipe.get_attribute("alt") for recipe in recipes]

    #bilder
    img_srcs = [recipe.get_attribute("src") for recipe in recipes]

except NoSuchElementException as e:
    print("Element not found:", e)


print(alt_texts)


#Speichere Rezepte in Textdatei wenn Inhalt vorhanden

if alt_texts:
    # store the files
    user_directory = os.path.expanduser(credentials.project_Directory)
    doc_path = os.path.join(user_directory, "rezepte.docx")
    img_folder = os.path.join(user_directory, "images")

    if not os.path.exists(img_folder):
        os.makedirs(img_folder)

    doc = Document()

    for i, (alt_text, img_src) in enumerate(zip(alt_texts, img_srcs)):
        # Download the image
        driver.get(img_src)
        image_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
        image_url = image_element.get_attribute("src")

        # Open the image URL and read the image data
        with urllib.request.urlopen(image_url) as response:
            image_data = response.read()

        image = Image.open(BytesIO(image_data))
        
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Store the image locally
        img_filename = f"image_{i+1}.jpg"  
        img_path = os.path.join(img_folder, img_filename)
        image.save(img_path)

        # Insert the image + caption into the document
        doc.add_picture(img_path)
        doc.add_paragraph(alt_text)
          

    doc.save(doc_path)

driver.quit()





