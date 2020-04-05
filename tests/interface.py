import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

CHROME_DRIVER_PATH = "C:/Users/hugos/Downloads/chromedriver_win32/chromedriver.exe"

class SoftDesUploadFile(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("http://admin:admin@localhost")
        elem = driver.find_element_by_id('resposta')
        print('ELEMENT: ', elem)
        driver.execute_script("arguments[0].style.display = 'block';", elem)
        elem.send_keys('C:/Users/hugos/OneDrive/Documents/Github/dev-aberto/aulas/06-projeto-desconhecido/codigo/src/desafio.py')
        elem = driver.find_element_by_id('enviar')
        elem.click()
        #assert "No results found." not in driver.page_source

    def tearDown(self):
        self.driver.close()

class SoftDesUploadWrongFile(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)

    def test_search_in_python_org(self):
        driver = self.driver
        driver.get("http://admin:admin@localhost")
        elem = driver.find_element_by_id('resposta')
        print('ELEMENT: ', elem)
        driver.execute_script("arguments[0].style.display = 'block';", elem)
        elem.send_keys('C:/Users/hugos/OneDrive/Documents/Github/dev-aberto/aulas/06-projeto-desconhecido/codigo/src/adduser.py')
        elem = driver.find_element_by_id('enviar')
        elem.click()
        #assert "No results found." not in driver.page_source
        
    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()