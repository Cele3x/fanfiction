# -----------------------------------------------------------
# Selenium scraper for extracting names with gender from
# babynames.com.
# -----------------------------------------------------------

from time import sleep
from urllib.request import Request, urlopen
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys

if __name__ == "__main__":
    driver = webdriver.Safari()
    females = set()
    males = set()
    try:
        url = 'https://babynames.com/baby-names-by-origin.php'
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        soup = BeautifulSoup(page, 'html.parser')
        category_links = soup.select('ul.origin2 li a')
        for link in category_links:
            next_url = urljoin(url, link.get('href'))

            driver.get(next_url)
            WebDriverWait(driver, 15).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'ul.searchresults')))
            loop_without_change = 0

            while True:
                print('Loop without change: %i' % loop_without_change)
                start_females_count = len(females)
                start_males_count = len(males)

                female_items = driver.find_elements(by=By.CSS_SELECTOR, value='a.F')
                new_females = [f.text for f in female_items]
                females.update(new_females)

                male_items = driver.find_elements(by=By.CSS_SELECTOR, value='a.M')
                new_males = [f.text for f in male_items]
                males.update(new_males)

                print('Females: %i' % len(females))
                print('Males: %i' % len(males))

                if start_females_count == len(females) and start_males_count == len(males):
                    loop_without_change = loop_without_change + 1

                if loop_without_change > 3:
                    break

                try:
                    driver.find_element(by=By.XPATH, value="//input[@type='submit' and @value='Next']").send_keys(Keys.ENTER)
                    sleep(5)
                except Exception as e:
                    print(e)
                    break
    except Exception as ex:
        print(ex)
    finally:
        with open('data/females.txt', 'a', encoding='utf-8') as f:
            for female in females:
                f.write(female)
                f.write('\n')

        with open('data/males.txt', 'a', encoding='utf-8') as f:
            for male in males:
                f.write(male)
                f.write('\n')
        driver.quit()
