class test_fail(Exception):
    def __init__(self, what):
        self.what = what
    pass

from selenium.webdriver.common.keys import Keys
class todo_tester:
    def __init__(self, driver):
        self.driver = driver
        self.input_field = driver.find_element_by_class_name("new-todo")
        self.list = driver.find_element_by_class_name("todo-list")
        self.test_count = 0

    def action_chain(self, element = None):
        from selenium.webdriver.common.action_chains import ActionChains
        if element:
            return ActionChains(self.driver).move_to_element(element)
        else:
            return ActionChains(self.driver)
    
    def get_list_entry(self, name):
        return self.list.find_element_by_xpath(
            "//*[contains(text(), '" + name + "')]"
        )

    def add(self, value):
        self.action_chain(self.input_field) \
            .click().send_keys(value).send_keys(Keys.ENTER) \
            .perform()
        return self.get_list_entry(value)

    def edit(self, element, new_value):
        self.action_chain(element) \
            .double_click() \
            .key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL) \
            .send_keys(Keys.DELETE).send_keys(new_value).send_keys(Keys.ENTER) \
            .perform()

    def toggle(self, element):
        self.action_chain(
            element.find_element_by_xpath("..") \
                   .find_element_by_class_name("toggle")
        ).click().perform()

    def remove(self, element):
        parent = element.find_element_by_xpath("..")
        self.action_chain().move_to_element_with_offset(
            parent, parent.rect["width"] - 40, parent.rect["height"] / 2
        ).click().perform()

    def require_count(self, count):
        parent = self.driver.find_element_by_class_name("todo-count")
        counter = parent.find_element_by_tag_name("strong")
        if not count == int(counter.text):
            raise test_fail(str(count) + " todo entries expected, but " \
                + counter.text + " is found instead.")
        else:
            self.test_count = self.test_count + 1
    def require_text(self, element, value):
        if not element.text == value:
            raise test_fail("Value '" + value + "' is expected for " + element.tag_name + \
                + " but '" + element.text + "' is found instead.")
        else:
            self.test_count = self.test_count + 1

    def test(self):
        test    = self.add("Run this test.")
        self.require_text(test, "Run this test.")
        self.require_count(1)

        x       = self.add("I should do X.")
        y       = self.add("And Y, too.")
        z       = self.add("Z is important as well.")
        edit_y  = self.add("I need to edit that second one.")
        self.require_text(x, "I should do X.")
        self.require_text(y, "And Y, too.")
        self.require_text(z, "Z is important as well.")
        self.require_text(edit_y, "I need to edit that second one.")
        self.require_count(5)

        self.edit(y, "And Y, too, using the results of X")
        self.toggle(edit_y)
        self.require_count(4)
        self.require_text(y, "And Y, too, using the results of X")

        fix     = self.add("Wait, I want to fix wording, as well.")
        self.require_text(fix, "Wait, I want to fix wording, as well.")
        self.toggle(edit_y)
        self.edit(y, "I should use X to finish Y.")
        self.require_text(y, "I should use X to finish Y.")
        self.toggle(edit_y)
        self.toggle(fix)
        self.require_count(4)

        mistake  = self.add("Created by mistake.")
        fix      = self.add("Delete created by mistake element.")
        self.require_text(mistake, "Created by mistake.")
        self.require_text(fix, "Delete created by mistake element.")
        self.require_count(6)
        self.remove(mistake)
        self.require_count(5)
        self.toggle(mistake)
        self.require_count(4)

        long = self.add("And this entry is super-puper-duper-incredibly-obnoxiously-annoyingly"
                + "-unbelievably-long. No-one should need something as long as this, "
                + "but just to be safe, a thousand more symbols: " 
                + "A" * 500 + "R" * 200 + "G" * 220 + "H" * 80)
        self.require_text(long, \
                "And this entry is super-puper-duper-incredibly-obnoxiously-annoyingly"
                + "-unbelievably-long. No-one should need something as long as this, "
                + "but just to be safe, a thousand more symbols: " 
                + "A" * 500 + "R" * 200 + "G" * 220 + "H" * 80)
        self.require_count(5)

        self.toggle(test)


def main():
    from selenium import webdriver
    options = webdriver.chrome.options.Options()
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome("../binary/chromedriver.exe", options = options
        #resource_path = "C:\Anaconda\pkgs\python-chromedriver-binary-87.0.4280.20.0-py37hc8dfbb8_0\Lib\site-packages\chromedriver_binary\chromedriver.exe"
    )
    driver.implicitly_wait(5)
    driver.get("http://todomvc.com/examples/angularjs/#/")

    try:
        print("Initialize testing:", driver.title, "(", driver.current_url, ")")
        tester = todo_tester(driver)
        tester.test()
        print("Testing successful:", driver.title, "(", driver.current_url, ")")
        print(tester.test_count, "test were passed.")
    except test_fail as fail:
        print("Testing failed:", driver.title, "(", driver.current_url, ")")
        print(tester.test_count, "test were passed.")
        print("Failed test message: ", fail.what)
    finally:
        driver.quit()


main()