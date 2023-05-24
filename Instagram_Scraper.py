from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import pandas as pd
import os
import random
import time
import sys
import requests


def initialize_bot():

    # Setting up chrome driver for the bot
    chrome_options  = webdriver.ChromeOptions()
    # suppressing output messages from the driver
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    # adding user agents
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    chrome_options.add_argument("--incognito")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # running the driver with no browser window
    #chrome_options.add_argument('--headless')
    #if not images:
    #    prefs = {"profile.managed_default_content_settings.images": 2}
    #    chrome_options.add_experimental_option("prefs", prefs)
    # installing the chrome driver
    driver_path = ChromeDriverManager().install()
    # configuring the driver
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    driver.set_page_load_timeout(60)
    driver.maximize_window()

    return driver

def initialize_bot2():

    class Spoofer(object):

        def __init__(self):
            self.userAgent = self.get()

        def get(self):
            ua = ('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36'.format(random.randint(90, 140)))

            return ua

    class DriverOptions(object):

        def __init__(self):

            self.options = uc.ChromeOptions()
            self.options.add_argument('--log-level=3')
            self.options.add_argument('--start-maximized')
            self.options.add_argument('--disable-dev-shm-usage')
            self.options.add_argument("--incognito")
            #self.options.add_argument("--headless")
            self.helperSpoofer = Spoofer()
            #self.seleniumwire_options = {}
           
            # random user agent
            self.options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36'.format(random.randint(90, 106)))
            self.options.page_load_strategy = 'eager'
           
            # Create empty profile for non Windows OS
            if os.name != 'nt':
                if os.path.isdir('./chrome_profile'):
                    shutil.rmtree('./chrome_profile')
                os.mkdir('./chrome_profile')
                Path('./chrome_profile/First Run').touch()
                self.options.add_argument('--user-data-dir=./chrome_profile/')
   
            # using proxies without credentials
            #if proxies:
            #   self.options.add_argument('--proxy-server=%s' % self.helperSpoofer.ip)


    class WebDriver(DriverOptions):

        def __init__(self):
            DriverOptions.__init__(self)
            self.driver_instance = self.get_driver()

        def get_driver(self):

            webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
      
            # uc Chrome driver
            driver = uc.Chrome(options=self.options)
            driver.set_page_load_timeout(20)
            driver.command_executor.set_timeout(10)


            return driver

    driver= WebDriver()
    driverinstance = driver.driver_instance
    return driverinstance

def get_IG_image(url, driver):

    restart = False
    if 'http' not in url: return '0'
    driver.get(url)
    time.sleep(3)
    try:
        title = wait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "h2"))).text
        if "Sorry, this page isn't available." in title:
            print('Warning: page is not available!')
            restart = True
    except:
        pass
    try:
        div = wait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div._aarf")))
        link = wait(div, 3).until(EC.presence_of_element_located((By.TAG_NAME, "img"))).get_attribute('src')
    except:
        link = '0'

    return link, restart

def login_instegram(driver, username, password):

    url = 'https://www.instagram.com/'
    driver.get(url)
    time.sleep(3)
    try:
        button = wait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.sqdOP.yWX7d.y3zKF')))
        driver.execute_script("arguments[0].click();", button)
        time.sleep(2)
        driver.refresh()
        user_tag = wait(driver, 10).until(EC.presence_of_element_located((By.ID, 'email')))
        pass_tag = wait(driver, 10).until(EC.presence_of_element_located((By.ID, 'pass')))
        user_tag.send_keys(username)
        time.sleep(2)
        pass_tag.send_keys(password)
        time.sleep(2)
        button = wait(driver, 10).until(EC.presence_of_element_located((By.ID, 'loginbutton')))
        driver.execute_script("arguments[0].click();", button)
        time.sleep(15)
    except:
        driver.quit()
        print('Failed to sign in using the given credentials, press any key to exit.')
        input()
        sys.exit(1)


def scrape_IG_img(schema):

    start = time.time() 
    username = ''
    password = ''

    output = schema[:-5] + '_update1.xlsx'
    # reading the latest final schema
    print('-'*75)
    print('Processing the input schema ....')
    try:
        df = pd.read_excel(schema)
        df['IG Account Image'] = df['IG Account Image'].astype(str)
        df['IG Account'] = df['IG Account'].astype(str)
    except Exception as err:
        print('Error in processing the brand performance sheet, Press any key to Exit.')
        print(err)
        input()
        sys.exit(1)

    try:
        urls = df['IG Account'].unique().tolist()
    except:
        print('The brand performance sheet must have a column named "IG Account", Press any key to Exit.')
        input()
        sys.exit(1)

    print('-'*75)
    print('Initializing the bot ....')
    driver = initialize_bot()
    print('-'*75)
    print('Signing In ....')
    print('-'*75)
    login_instegram(driver, username, password)
    print('Scraping Brands Logos Links ....')
    print('-'*75)
    # checking for saved urls library
    links = []
    done = {}
    n = len(urls)
    library = os.getcwd() + '\\IG_image_urls.csv'
    path = os.getcwd() + '\\IG_images_database.csv'
    if os.path.isfile(library):
        df_links = pd.read_csv(library)
    else:
        df_links = pd.DataFrame(columns=['IG account', 'image link'])

    if os.path.isfile(path):
        df_lib = pd.read_csv(path)

    try:
        for i, url in enumerate(urls):
            for _ in range(5):
                try:
                    url = str(url)
                    inds = df[df['IG Account'] == url].index
                    # no url is provided
                    if 'http' not in url:
                        df.loc[inds, 'IG Account Image'] = '0'
                        continue
                    # checking if the brand has already a logo           
                    #skip = False
                    #for ind in inds:
                    #    logo = df.loc[ind, 'IG Account Image']
                    #    if len(logo) > 0 and logo != 'nan':
                    #        df.loc[inds, 'IG Account Image'] = logo
                    #        skip = True
                    #        break
                    #if skip: continue

                    # if brand in the database then skip it
                    if url in df_lib['IG account'].values: continue

                    if url in df_links['IG account'].values:
                        mask = df_links[df_links['IG account'] == url]
                        inds = mask.index
                        link = mask.loc[inds[0], 'image link']
                        links.append({'IG account':url, 'image link':link})
                        done[url] = link
                        print(f'completed scraping logo {i+1}/{n}')
                    else:
                        if done.get(url, -1) == -1:
                            # link hasn't processed before
                            link, restart = get_IG_image(url, driver)
                            if restart:
                                driver.quit()
                                time.sleep(5)
                                driver = initialize_bot()
                                login_instegram(driver, username, password)
                            links.append({'IG account':url, 'image link':link})
                            done[url] = link
                            print(f'completed scraping logo {i+1}/{n}')
                            time.sleep(5)
                        else:
                            link = done[url]
                            links.append({'IG account':url, 'image link':link})
                            print(f'completed scraping logo {i+1}/{n}')

                    # adding the logo link to the df
                    df.loc[inds, 'IG Account Image'] = link
                    break
                except:
                    df_links = pd.DataFrame(links, columns=['IG account', 'image link'])
                    df_links.to_csv(library, encoding = 'UTF-8', index=False)
                    driver.quit()
                    time.sleep(5)
                    driver = initialize_bot()
                    print('-'*75)
                    print('Restarting the Bot ...')
                    print('-'*75)
                    login_instegram(driver, username, password)

        # updating the savd url library
        df_links = pd.DataFrame(links, columns=['IG account', 'image link'])
        df_links.to_csv(library, encoding = 'UTF-8', index=False)
        driver.quit()
        # adding the image url column to the master schema
        #df['IG Account Image'] = df_links['image link']
        df.to_excel(output, index= False)
        print('-'*75)
        print('Brands logos scraping Process Completed Successfully!')
        print('-'*75)
        #print('Press any key to exit')
        #input()
    except Exception as err:
        # updating the savd url library
        df_links = pd.DataFrame(links, columns=['IG account', 'image link'])
        df_links.to_csv(library, encoding = 'UTF-8', index=False)
        print('The Following error has occurred:')
        print(str(err))
        print('-'*75)
        print('Press any key to exit.')
        input()
        sys.exit(1)

def download_IG_imgs():

    path = os.getcwd() + '\\downloaded_images'
    if not os.path.isdir(path):
        os.mkdir(path)

    library = os.getcwd() + '\\IG_image_urls.csv'
    if os.path.isfile(library):
        df_links = pd.read_csv(library)
    else:
        print('Missing IG accounts csv file for the download! Press any key to exit.')
        input()
        sys.exit(1)

    print('Downloading Brands Logos ....')
    print('-'*75)
    df_links[['image link', 'IG account']] = df_links[['image link', 'IG account']].astype(str)
    df_links.drop_duplicates(inplace=True)
    links = df_links['image link'].values.tolist()
    accounts = df_links['IG account'].values.tolist()
    df_links['image_name'] = ''
    n = len(links)
    nimgs = 0
    for i in range(n):
        link = links[i]
        acc = accounts[i]
        if link == '0' or acc == '0': 
            inds = df_links[df_links['IG account'] == acc].index
            df_links.loc[inds, 'image_name'] = '0'
            continue
        name = acc.replace('https://', '')
        if 'google.com' in name:
            name = name.split('instagram.com')[-1].split('%2F')[1]
        else:
            name = name.split('/')[1]

        output = path + f"\\{name}.png"
        if os.path.isfile(output): 
            inds = df_links[df_links['IG account'] == acc].index
            df_links.loc[inds, 'image_name'] = name
            continue

        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{}.0.0.0 Safari/537.36'.format(random.randint(90, 140))
        headers = {'user-agent':agent}

        response = requests.get(link, headers=headers)
        with open(output, "wb") as f:
            f.write(response.content)

        inds = df_links[df_links['IG account'] == acc].index
        df_links.loc[inds, 'image_name'] = name
        time.sleep(1)
        nimgs += 1
        print(f"Image {i+1}/{n} is downloaded successfully")
        
    df_links.to_csv(os.getcwd() + '\\IG_image_urls_update1.csv', encoding='UTF-8', index=False)
    print('-'*75)
    print(f'Brands logos download Process Completed Successfully! downloaded images: {nimgs}')

if __name__ == '__main__':

    #freeze_support()
    schema = os.getcwd() + "\\IG_urls.xlsx"
    start = time.time()
    scrape_IG_img(schema)
    download_IG_imgs()
    time_mins = round((time.time() - start)/60, 2)
    time_hrs = round(time_mins / 60, 2)
    print(f'Process Completed Successfully! Elapsed time {time_hrs} hours ({time_mins} mins)')
    input('Press any key to exit.')