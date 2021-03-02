from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import * 
import dateutil.parser
import logging

f = open("config.txt", "r")
LOGGING_PATH = f.readline().replace('\n','')
CHROME_DRIVER_PATH = f.readline().replace('\n','')
EMAIL = f.readline().replace('\n','')
PASSWORD = f.readline().replace('\n','')

logging.basicConfig(filename=LOGGING_PATH + str(date.today()) + '.log', level=logging.INFO)

driver = webdriver.Chrome(executable_path = CHROME_DRIVER_PATH)

driver.get("https://warrior.uwaterloo.ca/Program/GetProgramDetails?courseId=cc2a16d7-f148-461e-831d-7d4659726dd1&semesterId=b0d461c3-71ea-458e-b150-134678037221")
login_button = driver.find_element_by_class_name("navbar-right").find_element_by_id("loginLink")
login_button.click()
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "loginOption"))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "userNameInput"))).send_keys(EMAIL)
driver.find_element_by_id("nextButton").click()
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "passwordInput"))).send_keys(PASSWORD)
driver.find_element_by_id("submitButton").click()
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "duo_iframe")))
driver.switch_to.frame("duo_iframe")
# WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "push-label")))
driver.find_element_by_class_name("push-label").find_element_by_class_name("auth-button").click()

WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, "program-schedule-card-caption")))
# sleep(3)
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

timeslots = driver.find_elements_by_class_name("program-schedule-card-caption")

# 6 days from today:
idealdate = date.today() + timedelta(days = 5)
idealdatetime = datetime(idealdate.year, idealdate.month, idealdate.day)
clickedSomething = False
for timeslot in timeslots:
  timeslot_obj = dateutil.parser.parse(timeslot.find_element_by_class_name("program-schedule-card-header").text)
  temp = dateutil.parser.parse(timeslot.find_element_by_tag_name("small").text[:8])
  timeslot_obj = timeslot_obj.replace(hour=temp.hour)

  if (idealdatetime <= timeslot_obj):
    logging.info(timeslot_obj)
    try:
      btn = timeslot.find_element_by_class_name("btn")
      if (btn.text.lower() == "DETAILS".lower()):
        logging.info("already booked")
        # break
      else:
        btn.click()
        logging.info("trying to book time slot: " + str(timeslot_obj))
        clickedSomething = True
        break
    except:
      logging.info("feels bad")


if not clickedSomething: 
  logging.info("didn't find anything")
  exit(1)

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"waiverContainer\"]/div/img")))


WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "btnAccept"))).click()

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "rbtnNo")))

noButtons = driver.find_elements_by_id("rbtnNo")

for btn in noButtons:
  driver.executeScript("arguments[0].scrollIntoView(true);", btn); 
  btn.click()

driver.find_element_by_xpath("//*[@id=\"mainContent\"]/div[2]/form[2]/div[2]/button[2]").click()

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "checkoutButton"))).click()

WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "CheckoutModal")))

driver.find_element_by_id("CheckoutModal").find_element_by_class_name("btn-primary").click()

logging.info("successfully booked!")

driver.close()