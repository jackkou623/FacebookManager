# coding=utf-8
from time import sleep                   
from selenium import webdriver        
from DatabaseConnection import Database
from selenium.webdriver.common.keys import Keys        
from pathlib import Path
import sys
import os
import json

def Login(username,password,ACID):
    try:
        driver.get("https://www.facebook.com/")
        sleep(2)
        
        try:
            driver.find_element_by_id("email").send_keys(username)
            try:
                driver.find_element_by_id("pass").send_keys(password)
                sleep(3)
                driver.find_element_by_xpath("//*[@id='loginbutton']").click()
            except:
                driver.find_element_by_xpath('//*[@placeholder="password"]').send_keys(password)
                sleep(3)
                driver.find_element_by_xpath("//*[@name='login']").click()

        except:
            driver.find_element_by_xpath('//*[@name="email"]').send_keys(username)
            driver.find_element_by_xpath('//*[@name="password"]').send_keys(password)
            sleep(3)
            driver.find_element_by_xpath("//*[@name='login']").click()
        sleep(2)
        
        #Function 2: get Cookies
        print ("Cookies are retrieving")
        sleep(10)
        cookies = driver.get_cookies()
        print (cookies)
        Database().update_cookies(ACID, json.dumps(cookies))
        print('End LoginFaceBookSuccessfully!\n\n')

    except:      
        print("Error")

def input_cookies(ACData, Link, driver):
    driver.get("https://www.google.com/") #Warm reminder, if you want to change it, do it carefully
    driver.maximize_window() 
    sleep(5)
    cookie = ACData[7]
    cookie = json.loads(cookie)
    for c in cookie:
            if 'expiry' in c:
                    del c['expiry'] #For Chrome version 76.x
                    driver.add_cookie(c)
            else:
                    driver.add_cookie(c)
    driver.get(Link) #Warm reminder, don't change this without good reason
    print("Cookies are successfully input-ed.")
    sleep(3)

def GetGroups():
    Groups = []
    print('start exporting groups list ')
    driver.get('https://www.facebook.com/bookmarks/groups/')
    sleep(5)
    b = driver.find_element_by_id('pagelet_seeall_filter')
    a = b.find_elements_by_xpath('.//a[@class="_5afe" and contains(@href,"/groups/")]')
    for i in range(len(a)):
        print(a[i].get_attribute('title'))
        Groups.append(a[i].get_attribute('title'))
    Groups.append("END")
    return Groups

def actions(Actions_spec, ACID):
    #Global variables:
    ACData = Database().get_ACIDdata(ACID)
    Link = "https://www.facebook.com/"

    #Chrome Settings
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    if Actions_spec[1] == True:
        Cloc = Path(os.path.abspath("")) #Current Location
        Extension = Cloc / 'toolkit.crx'
        options.add_extension(Extension)
    options.add_experimental_option("prefs",prefs)
    global driver
    driver = webdriver.Chrome(options=options)

    if Actions_spec[0] ==True:
        Login(ACData[1],ACData[2],ACID)
    elif Actions_spec[0] ==False:
        input_cookies(ACData, Link, driver)

    if Actions_spec[2] == True:
        Groups = GetGroups()
        Database().update_Groups(ACID, Groups)

    if Actions_spec[3] == True:
        driver.quit()
    else:
        print('do nothin')