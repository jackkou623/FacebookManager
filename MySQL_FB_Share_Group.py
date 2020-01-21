# coding=utf-8 This version keep looping the same article, but with a list of social group at HR page
from time import sleep      
import re        
import os 
import subprocess     
import sys  
import pyperclip
import codecs  
import shutil
import urllib
import json
from selenium import webdriver        
from selenium.webdriver.common.keys import Keys   
import selenium.webdriver.support.ui as ui        
from selenium.webdriver.common.action_chains import ActionChains
from DatabaseConnection import Database

def Duplicate(PostGroup,repeatednum):
    size = len(PostGroup)
    repeated = []
    for i in range(size): 
        k = i + 1
        for j in range(k, size): 
            if PostGroup[i] == PostGroup[j] and PostGroup[i] not in repeated: 
                repeated.append(PostGroup[i]) 
                repeatednum.append(j)
    return repeated 

def Close():
        try:
                driver.find_element_by_link_text('Close').click()
        except:
                pass


def Share1(driver): #Share to the timeline
        try:
                x = driver.find_element_by_xpath('//*[@title="Send this to friends or post it on your timeline."][@role="button"]')
        except:
                x = driver.find_element_by_xpath('//*[@title="Send this to friends or post it on your Timeline."][@role="button"]')

        x.location_once_scrolled_into_view
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
        sleep(2)
        x.click()
        sleep(2)
                
        try:
                driver.find_element_by_link_text('Share Now (Public)').click()
        except:
                driver.find_element_by_link_text('Share Now (Friends)').click()
        sleep(8)

def identify1(driver) : #Identify Share In a group button exist or not:
        try:
                x = driver.find_element_by_xpath('//*[@title="Send this to friends or post it on your timeline."][@role="button"]')
        except:
                x = driver.find_element_by_xpath('//*[@title="Send this to friends or post it on your Timeline."][@role="button"]')

        x.location_once_scrolled_into_view
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
        sleep(2)
        x.click()
        sleep(2)
                
        try:
                try:
                        driver.find_element_by_link_text('Share in a Group').click()
                except:
                        try:
                                driver.find_element_by_link_text('Share to your story now (Friends)')
                                driver.find_element_by_link_text('Share…').click()
                        except:
                                driver.find_element_by_link_text('Share to Your Story Now (Friends)')
                                driver.find_element_by_link_text('Share…').click()
        except:
                driver.find_element_by_link_text('Share…').click()

def share2_2(exception,driver,PostGroup,Link,a):
        sleep(2)
        try:
                x = driver.find_element_by_xpath('//input[@data-testid="searchable-text-input"][@aria-expanded="false"][@placeholder="Group name"]')
        except:
                x = driver.find_element_by_xpath('//input[@data-testid="searchable-text-input"][@aria-expanded="false"][@placeholder="Group Name"]')
        pyperclip.copy(PostGroup[a])
        sleep(2)
        x.send_keys(Keys.CONTROL,('v'))

        sleep(2)

        try:
                y = driver.find_element_by_xpath('//input[@data-testid="searchable-text-input"][@aria-expanded="true"]')
                y.send_keys(Keys.SPACE) 
                y.send_keys(Keys.BACKSPACE) 
        except:
                print('Failed' + str(PostGroup[a]))
                driver.get(Link)
                return(1)

        sleep(3)
        z = y.get_attribute('aria-activedescendant')

        if exception == 1 and z != None:
                sleep(1)
                y.send_keys(Keys.DOWN, Keys.RETURN)      
        elif exception == 1:
                y.send_keys(Keys.DOWN)
                sleep(1)
                y.send_keys(Keys.DOWN, Keys.RETURN)
        elif z != None:
                y.send_keys(Keys.RETURN)
                sleep(1)
        else:
                sleep(1)
                y.send_keys(Keys.DOWN, Keys.RETURN)

        sleep(2)

def share2_1(exception,driver,Say,PostGroup,Link,a):
        sleep(2)
        try:
                driver.find_element_by_xpath('//span[@audience="self"]').click()
                driver.find_element_by_xpath('//span[@audience="group"]').click()
        except:
                pass

        if share2_2(exception,driver,PostGroup,Link,a) == 1:
                return
        
        try:
                y = driver.find_element_by_xpath("//div[@data-testid='status-attachment-mentions-input']")
                y.send_keys(Say)
                sleep(2)
                y.send_keys(Keys.ENTER)
        except:
                y = driver.find_elements_by_xpath("//div[@data-testid='status-attachment-mentions-input']")
                y[1].send_keys(Say)
                sleep(2)
                y[1].send_keys(Keys.ENTER)
        
        driver.find_element_by_xpath("//*[@data-testid='react_share_dialog_post_button']").click()
        sleep(2)
        identify2(PostGroup,a)
        sleep(3)

def identify2(PostGroup,a): #to identify whether this group allow to post or not
        try:
                driver.find_element_by_xpath("//*[@action='cancel'][@role='button']").click()
                print('Not allowed to post to ' + str(PostGroup[a]))
        except:
                print(str(PostGroup[a]))
                

def share_actions(ACID, link, Say, PostGroup, share_timeline):
        #Global variables:
        database = Database()
        repeatednum = []

        from MySQL_FB_Retrieve_Cookies import input_cookies

        #Menu
        ACData = database.get_ACIDdata(ACID)

        #Disable Chrome notification alerts
        options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        options.add_experimental_option("prefs",prefs)
        driver = webdriver.Chrome(options=options)

        input_cookies(ACData, link, driver)

        print(Duplicate(PostGroup,repeatednum)) 
        print(repeatednum)
        Close()
        if share_timeline == True:
                Share1(driver)
        for a in range(len(PostGroup)):
                identify1(driver)
                exception = 0
                if a in repeatednum:
                        exception = 1
                share2_1(exception,driver,Say,PostGroup,link,a)

        driver.quit()