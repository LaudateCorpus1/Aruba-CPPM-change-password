"""
Regression_tests for FLASK application
User test123 is used in these tests
It must be existed on CPPM
"""
import pytest
import string
import secrets
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager
from classes import Cppm_Connect
from common_functions import change_password

# Define class from classes file
connect_class = Cppm_Connect()

driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())


def test_index_page():
    """
    Check index page and click to Login
    """
    #    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
    #    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("http://127.0.0.1:5000/")
    assert "AAA Home" in driver.title
    driver.find_element_by_xpath(
        "//a[contains(text(),'Please login')]").click()
    assert "AAA Log in" in driver.title


def gen_password():
    """
    Password generation function
    :return:
           generated password
    """
    alphabet = string.ascii_letters + string.digits
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(7))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)):
            break
    password = password + secrets.choice(string.punctuation)
    return password


# New password for login check (user test123)
new_password = gen_password()
# Change password for user test123 on CPPM
change_password(connect_class, 'test123', new_password)
# New password for password change (user test123)
new_password1 = gen_password()


scenarios_to_login = [
    ('FAke@password17', 'AAA Log in'),
    (new_password, 'AAA Logged_in')]


@pytest.mark.parametrize("password,l_assert_res",
                         scenarios_to_login,
                         ids=["Wrong password",
                              "Success login"])


# @pytest.mark.skipif("AAA Log in" not in driver.title, reason="Cannot open login page")


def test_logging_in(password,l_assert_res):
    """
    Check login for user test123:
        1. FAIL with fake password
        2. SUCCESS with "real" password
    """
    driver.find_element_by_xpath("//input[@name='username']"). \
        send_keys("test123")
    driver.find_element_by_xpath("//input[@name='password']"). \
        send_keys(password)
    driver.find_element_by_xpath("//input[@id='butn']"). \
        click()
    assert l_assert_res in driver.title


def test_link_to_change_password():
    """
    Check "Change password link"
    """
    driver.find_element_by_xpath(
        "//a[contains(text(),'Change password')]").click()
    assert "AAA Change Password" in driver.title


scenarios_to_check_change_password = [
    ('12345', '1234', 'Passwords don\'t match'),
    ('123456789jJ', '123456789jJ', 'Password must contain'),
    ('123', '123', 'Password length'),
    (new_password, new_password, 'Password must be'),
    (new_password1, new_password1, 'Password changed successfully')]


@pytest.mark.parametrize("pass1,pass2,assert_res",
                         scenarios_to_check_change_password,
                         ids=["Mistyped passwords",
                              "Passwords doesn't match policy for complexity",
                              "Passwords doesn't match policy for password lengths",
                              "Old password", "New strong password"])
def test_password_change(pass1, pass2, assert_res):
    """
    Check change password:
    1. Mistyped passwords
    2. Passwords doesn't match policy for complexity
    3. Passwords doesn't match policy for password lengths
    4. Old password (CPPM must be configured for password history)
    5. New strong password
    """
    driver.find_element_by_xpath("//input[@name='new_password1']"). \
        send_keys(pass1)
    driver.find_element_by_xpath("//input[@name='new_password2']"). \
        send_keys(pass2)
    driver.find_element_by_xpath("//input[@id='butn']"). \
        click()
    assert assert_res in driver.find_element_by_xpath("//h3").text
