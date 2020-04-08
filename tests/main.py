import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from softdes import lambda_handler

CHROME_DRIVER_PATH = "C:/Users/hugos/Downloads/chromedriver_win32/chromedriver.exe"

class SoftDesLogout(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)

    def test_logout(self):
        driver = self.driver
        driver.get("http://admin:hugo123@localhost")
        elem = driver.find_element_by_id('logout')
        elem.click()
        #assert "No results found." not in driver.page_source
        
    def tearDown(self):
        self.driver.close()

class SoftDesChangePassword(unittest.TestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)

    def test_change_password(self):
        driver = self.driver
        driver.get("http://admin:hugo123@localhost/pass")
        elem = driver.find_element_by_id('velha')
        elem.send_keys('hugo123')
        elem = driver.find_element_by_id('nova')
        elem.send_keys('hugo123')
        elem = driver.find_element_by_id('repeteco')
        elem.send_keys('hugo123')
        elem = driver.find_element_by_id('change_pwd')
        elem.click()
        #assert "No results found." not in driver.page_source
        
    def tearDown(self):
        self.driver.close()



class SoftDesUploadFile(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH)

    def test_upload_correct_file(self):
        driver = self.driver
        driver.get("http://admin:hugo123@localhost")
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

    def test_upload_wrong_file(self):
        driver = self.driver
        driver.get("http://admin:hugo123@localhost")
        elem = driver.find_element_by_id('resposta')
        print('ELEMENT: ', elem)
        driver.execute_script("arguments[0].style.display = 'block';", elem)
        elem.send_keys('C:/Users/hugos/OneDrive/Documents/Github/dev-aberto/aulas/06-projeto-desconhecido/codigo/src/adduser.py')
        elem = driver.find_element_by_id('enviar')
        elem.click()
        #assert "No results found." not in driver.page_source
        
    def tearDown(self):
        self.driver.close()


class SoftDesTestLambdaHandler(unittest.TestCase):
    
    def test_lambda_handler_right_case(self):
        with open("../src/desafio.py", 'r') as f_p:
            code_file = f_p.read()
        obj = {}
        obj['ndes'] = 1
        obj['code'] = code_file
        obj['args'] = [[1],[2],[3]]
        obj['resp'] = [0,0,0]
        obj['diag'] = ['a','b','c']
        assert len(lambda_handler(obj)) == 0

    def test_lambda_handler_wrong_case(self):
        with open("../src/desafio.py", 'r') as f_p:
            code_file = f_p.read()
        obj = {}
        obj['ndes'] = 1
        obj['code'] = code_file
        obj['args'] = [1,2,3]
        obj['resp'] = [0,0,0]
        obj['diag'] = ['a','b','c']
        assert len(lambda_handler(obj)) > 0

if __name__ == "__main__":
    unittest.main()