# -*- coding: utf-8 -*-
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import schedule

# تنظیمات و اطلاعات کاربر - مقادیر را اینجا قرار دهید یا از متغیرهای محیطی استفاده کنید
STUDENT_NUMBER = os.getenv("STUDENT_NUMBER", "<شماره_دانشجویی>")
STUDENT_NAME = os.getenv("STUDENT_NAME", "<نام_و_نام‌خانوادگی>")
STUDENT_DEPT = os.getenv("STUDENT_DEPT", "<رشته>")
ACTIVATION_CODE = os.getenv("ACTIVATION_CODE", "<کد_فعال‌سازی_درس>")
COURSE_NAME = os.getenv("COURSE_NAME", "<نام_درس_یا_کد_درس>")
# توکن بات تلگرام و شناسه چت گیرنده (مثلاً شناسه کاربر یا گروه)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "<توکن_بات_تلگرام>")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "<شناسه_چت_تلگرام>")

def take_attendance():
    driver = None
    try:
        # تنظیمات مرورگر (Chrome) برای حالت بدون‌سربرگ (Headless)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # ایجاد WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(10)
        # باز کردن صفحه ورود دانشجو
        driver.get("https://pdks.nisantasi.edu.tr/ogrenci/giris")
        # پر کردن فرم حضور و غیاب
        driver.find_element(By.XPATH, "//input[@placeholder='Öğrenci Numarası']").send_keys(STUDENT_NUMBER)
        driver.find_element(By.XPATH, "//input[@placeholder='Öğrenci Ad Soyad']").send_keys(STUDENT_NAME)
        driver.find_element(By.XPATH, "//input[@placeholder='Öğrenci Bölüm']").send_keys(STUDENT_DEPT)
        driver.find_element(By.XPATH, "//input[@placeholder='Ders Aktivasyon Kodu']").send_keys(ACTIVATION_CODE)
        # انتخاب درس از فهرست کشویی
        select_element = Select(driver.find_element(By.TAG_NAME, "select"))
        select_element.select_by_visible_text(COURSE_NAME)
        # کلیک روی دکمه "DERSE KATIL"
        driver.find_element(By.XPATH, "//*[contains(text(), 'DERSE KATIL')]").click()
        # چند لحظه مکث برای بارگذاری نتیجه
        time.sleep(3)
        # گرفتن اسکرین‌شات از صفحه
        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
    except Exception as e:
        # در صورت بروز خطا، چاپ خطا برای بررسی
        print("Error in take_attendance:", e)
    finally:
        # بستن مرورگر در پایان (جهت اطمینان از بسته شدن حتی در صورت خطا)
        if driver:
            driver.quit()
    # ارسال تصویر اسکرین‌شات به تلگرام (در صورت موفقیت‌آمیز بودن مراحل قبل)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID and os.path.exists("screenshot.png"):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open("screenshot.png", "rb") as photo_file:
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"photo": photo_file})

# زمان‌بندی اجرای ربات هر نیم‌ساعت از ساعت 10 صبح تا 5 عصر (سه‌شنبه تا جمعه)
times = ["10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00"]
for t in times:
    schedule.every().tuesday.at(t).do(take_attendance)
    schedule.every().wednesday.at(t).do(take_attendance)
    schedule.every().thursday.at(t).do(take_attendance)
    schedule.every().friday.at(t).do(take_attendance)

# اجرای بی‌نهایت برای ربات زمان‌بندی‌شده
while True:
    schedule.run_pending()
    time.sleep(1)
