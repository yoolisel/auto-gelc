import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


univ_uri = 'https:/gelc.or.kr'    # url
univ_index = 0                    # 대학 드롭다운 리스트 순서 index
univ_id = '2020XXXXXX'            # 학번
univ_pw = 'thisismypassword'      # 비밀번호
univ_goal = 11                    # 몇 번째 강의까지 들을 건지

options = Options()
options.add_argument("--disable-features=EnableEphemeralFlashPermission")
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")
options.add_argument("disable-gpu")

print('initialize preferences...')
prefs = {
    "profile.default_content_setting_values.plugins": 1,
    "profile.content_settings.plugin_whitelist.adobe-flash-player": 1,
    "profile.content_settings.exceptions.plugins.*,*.per_resource.adobe-flash-player": 1,
    "PluginsAllowedForUrls": univ_uri
}

options.add_experimental_option("prefs", prefs)

print('open chrome')
driver = webdriver.Chrome("chromedriver", options=options)
driver.implicitly_wait(1)

print('open uri : {0}'.format(univ_uri))
driver.get(univ_uri)
driver.implicitly_wait(1)

print('get main window')
main_window = driver.current_window_handle

# login sequence
print('login...')
driver.find_element_by_xpath('//*[@id="pop_login"]').click()
driver.find_element_by_xpath('//*[@id="univ_select"]/option[{0}]'.format(univ_index)).click()
driver.find_element_by_xpath('//*[@id="id"]').send_keys(univ_id)
driver.find_element_by_xpath('//*[@id="pass"]').send_keys(univ_pw)
driver.find_element_by_xpath('//*[@id="login_img"]').click()

driver.implicitly_wait(1)
print('success')

# close notice
found = driver.find_element_by_xpath('//*[@id="close_14260781"]/img')
if found is not None:
    found.click()
    driver.implicitly_wait(1)
    print('close announcement')

# close change password
found = driver.find_element_by_xpath('//*[@id="change_close"]/span')
if found is not None:
    found.click()
    driver.implicitly_wait(1)
    print('close change password window')

# go to my page
found = driver.find_element_by_xpath('//*[@id="gnbmenu"]/ul/li[3]/a/span')
if found is None:
    print('failed to find my page')
    print('there might be several window that blocks xpath')
    exit()

found.click()
driver.implicitly_wait(1)

# goto my lecture
driver.find_element_by_xpath('//*[@id="rows1"]/table/tbody/tr/td[4]/span[1]/a').click()
driver.implicitly_wait(100)
time.sleep(1)

windows = driver.find_elements_by_class_name('lectureWindow')
print('found lecture count : {0}'.format(len(windows)))

while len(windows) < univ_goal:
    windows = driver.find_elements_by_class_name('lectureWindow')
    time.sleep(1)

print('start to enumerate')
for i in range(0, univ_goal):
    driver.implicitly_wait(1)
    xpath = '//*[@id="lenAct"]/div[{0}]/div[2]/dl/dd[1]/span[2]'.format(i + 1)
    percentage = driver.find_element_by_xpath(xpath)

    watching = False

    # 최초 실행시 이미 진행된 강의면 스킵
    if '100%' in percentage.text:
        continue

    # 현제 세션이 완료되지 않은 상태
    while '100%' not in percentage.text:
        if not watching:
            driver.find_element_by_xpath('//*[@id="lenAct"]/div[{0}]/div[3]/a/img'.format(i + 1)).click()
            watching = True
            driver.implicitly_wait(20)
            print('open new lecture window... :: {0}'.format(i+1))

        time.sleep(100)

        driver.switch_to_window(main_window)
        driver.refresh()
        percentage = driver.find_element_by_xpath(xpath)

        print("refreshing... [{0}/{1}] 현재 강의 진행도 {2}".format(i+1, univ_goal, percentage.text))

    driver.switch_to_window(main_window)

    print("moving to next lecture...")
    time.sleep(10)

