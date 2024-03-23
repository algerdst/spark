import math

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


import spark_config
import spark_creditors
import time
import os


def logout():
    driver.get('https://spark-interfax.ru/system/#/dashboard')
    wrapper = driver.find_element(By.CSS_SELECTOR, 'div.user-toolbar-wrapper')
    buttons = wrapper.find_elements(By.TAG_NAME, 'button')
    button_logout = buttons[2]
    button_logout.click()


def login():
    login_form = driver.find_element(By.CSS_SELECTOR, 'input.login-form__input')
    login_form.send_keys(spark_config.LOGIN)

    password_form = driver.find_elements(By.CSS_SELECTOR, 'input.login-form__input')[1]
    password_form.send_keys(spark_config.PASSWORD)

    submit = driver.find_element(By.CSS_SELECTOR, 'button.login-form__btn')
    submit.click()
    time.sleep(10)
    try:
        close_modal = driver.find_element(By.CSS_SELECTOR, 'div.modal-content').find_element(By.TAG_NAME, 'button')
        close_modal.click()
    except:
        pass
    time.sleep(2)


def write_to_file(result):
    f = open('cad.txt', 'a')
    filesize = os.path.getsize('cad.txt')
    if filesize != 0:
        f.write('\n')

    for i in range(len(result)):
        f.write(result[i])
        if i != len(result) - 1:
            f.write('\n')

    f.close()


def search(creditor, start):
    reg_numbers=[]
    search_field = driver.find_element(By.CSS_SELECTOR, 'span.twitter-typeahead').find_element(By.TAG_NAME, 'input')
    search_field.click()
    search_field.send_keys(creditor)
    search_button = driver.find_element(By.CSS_SELECTOR, 'div.input-group').find_element(By.CSS_SELECTOR,
                                                                                         'button.sp-search-btn')
    search_button.click()
    try:
        driver.find_element(By.CSS_SELECTOR, 'div.sp-list-summary__item')
        item_link = driver.find_element(By.CSS_SELECTOR, 'div.sp-list-summary__item').find_element(By.CLASS_NAME,
                                                                                                   'sp-list-summary__item-content').find_element(
            By.TAG_NAME, 'a').get_attribute('href')
        driver.get(item_link)
        groups=driver.find_elements(By.CSS_SELECTOR, 'div.card-menu-items__group')[4]
        groups_buttons=groups.find_elements(By.TAG_NAME, 'button')
        for but in groups_buttons:
            if but.text=='Залоги':
                zalog_but=but
                break
        zalog_but.click()
        time.sleep(3)
        quantity_button=driver.find_element(By.CSS_SELECTOR, 'div.counter-filter-list__item').find_element(By.TAG_NAME, 'button')
        zalog_quantity=int(quantity_button.text)
        scroll_quantity=math.ceil(zalog_quantity/30)
        quantity_button.click()
        time.sleep(3)
        for scroll in range(scroll_quantity):
            elem = driver.find_element(By.TAG_NAME, "html")
            elem.send_keys(Keys.END)
            time.sleep(1)
        zalogi=driver.find_elements(By.CSS_SELECTOR, 'button.pledges-message-link')[start::]
        for zalog in zalogi:
            index=zalogi.index(zalog)
            ActionChains(driver).move_to_element(zalog).click(zalog).perform()
            time.sleep(0.2)
            reg_number=driver.find_element(By.CLASS_NAME, 'sp-table-type-details').find_elements(By.TAG_NAME, 'tr')[4].find_elements(By.TAG_NAME, 'td')[1].text
            reg_numbers.append(reg_number)
            button_close=driver.find_element(By.CSS_SELECTOR, 'button.close')
            button_close.click()
            if index==len(zalogi)-1:
                break
        return reg_numbers
    except:
        return 'Ничего не найдено'


if __name__ == '__main__':
    with webdriver.Chrome() as driver:
        driver.get('https://www.spark-interfax.ru/')
        driver.implicitly_wait(1000)
        driver.maximize_window()
        login()
        for creditor in spark_creditors.creditors:
            start=spark_creditors.creditors[creditor]
            result=search(creditor, start)
            if isinstance(result, list):
                write_to_file(result)
            else:
                continue


        logout()
        time.sleep(5)
