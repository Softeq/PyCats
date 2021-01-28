from common._webdriver_qa_api.web.web_pages import WebPage
from selenium.webdriver.common.by import By
from common._webdriver_qa_api.web.web_elements import WebElement, WebTextBox


class SignInPage(WebPage):

    def __init__(self, should_present=True):
        super().__init__(By.XPATH, "//form[@action='/users/sign_in']", "Sign In Page", should_present=should_present)
        self.lbl_form_title = WebElement(By.XPATH, "//div[@class='sign-form']/h3")
        self.txb_email = WebTextBox(By.ID, "user_email")
        self.txb_password = WebTextBox(By.ID, "user_password")
        self.btn_submit = WebElement(By.XPATH, "//input[@value='Submit']")
        self.lbl_error = WebElement(By.XPATH, "//div[@class='panel panel-red']/div[@class='panel-body']")
        self.btn_create_account = WebElement(By.XPATH, "//div[@class='sign-form']//a[@href='/users/sign_up']")
        self.btn_recover = WebElement(By.XPATH, "//div[@class='sign-form']//a[@href='#']")

    def fill_email(self, email):
        self.txb_email.set_text(email)

    def fill_password(self, password):
        self.txb_password.set_text(password)

    def click_submit_btn(self):
        self.btn_submit.click()

    def click_create_account(self):
        self.btn_create_account.click()

    def click_recover_password(self):
        self.btn_recover.click()

    def is_error_displayed(self):
        return self.lbl_error.is_present()
