from common._webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement, WebTextBox


class SignUpPage(WebPage):

    def __init__(self):
        super().__init__(By.XPATH, "//form[@action='/users']", "Sign Up Page")
        self.lbl_form_title = WebElement(By.XPATH, "//div[@class='sign-form']/h3")
        self.txb_username = WebTextBox(By.ID, "user_username")
        self.txb_email = WebTextBox(By.ID, "user_email")
        self.txb_password = WebTextBox(By.ID, "user_password")
        self.txb_password_confirmation = WebTextBox(By.ID, "user_password_confirmation")
        self.btn_privacy_policy = WebElement(By.XPATH, "//form[@id='new_user']//a[@href="
                                                       "'https://openweather.co.uk/privacy-policy']")
