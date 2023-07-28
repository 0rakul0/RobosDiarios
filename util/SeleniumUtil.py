from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from util.ConfigManager import ConfigManager
from bs4 import BeautifulSoup as bs
import time


def open_selenium(path_selenium, headless=False, options=None, minimize_window=False, path_download_file=None):

    browser = None

    try:
        chrome_options = webdriver.ChromeOptions()

        # if len(options) != 0:
        #
        #     chrome_options.add_experimental_option('prefs', options)

        if headless:
            chrome_options.add_argument("enable-automation")
            chrome_options.add_argument("--disable-infobars")
            chrome_options.add_argument("--disable-browser-side-navigation")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--incognito')

        browser = webdriver.Chrome (chrome_options=chrome_options, executable_path=path_selenium) # path sempre contendo o .exe no windows
        time.sleep (2)

        if not headless and minimize_window:
            browser.minimize_window ()

    except Exception as e:
        ConfigManager().escreve_log('Impossível executar o selenium webdriver')
        print(e)

    return browser


def ctrl_a(browser, element_to_click=None):

    actions = ActionChains(browser)

    if element_to_click:
        find_element_by_xpath_with_click(browser, element_to_click)

    actions.key_down(Keys.CONTROL)  # Pressionar o CTRL
    actions.key_down('a')  # Pressionar o A
    actions.perform() # Executar ação
    time.sleep(0.25)

    actions.key_up(Keys.CONTROL)  # Liberar o CTRL
    actions.key_up('a') # Liberar o A
    time.sleep(1)

    actions.key_down(Keys.BACKSPACE) # Pressionar o BACKSPACE
    actions.perform() # Executar ação
    time.sleep(0.25)

    actions.key_up(Keys.BACKSPACE) # Liberar o BACKSPACE
    time.sleep(0.5)


def find_element_by_xpath_with_click(browser, element_xpath):

    browser.find_element(By.XPATH, element_xpath).click()
    time.sleep(1)


def send_keys_by_xpath(browser, element_xpath, value):

    browser.find_element(By.XPATH, element_xpath).send_keys(value)
    time.sleep(1)


def selenium_for_bs(browser, page_element, mode_search):

    if mode_search == 'XPATH':
        soup = bs(browser.find_element(By.XPATH, page_element).get_attribute("outerHTML"), "html5lib")
        time.sleep(0.5)

    elif mode_search == 'ID':
        soup = bs (browser.find_element (By.ID, page_element).get_attribute ("outerHTML"), "html5lib")
        time.sleep (0.5)

    elif mode_search == 'TAG_NAME':
        soup = bs (browser.find_element (By.TAG_NAME, page_element).get_attribute ("outerHTML"), "html5lib")
        time.sleep (0.5)

    else:
        soup = 'Necessário implementar o mode_search {} no SeleniumUtil.py'.format(mode_search)

    return soup


def create_modheaders_plugin(plugin_path=None, remove_headers=None, add_or_modify_headers=None):

    """Create modheaders extension

    kwargs:
        plugin_path (str): absolute plugin path
        remove_headers (list): headers name to remove
        add_or_modify_headers (dict): ie. {"Header-Name": "Header Value"}

    return str -> plugin path
    """
    import string
    import zipfile

    if plugin_path is None:
        plugin_path = './vimm_chrome_modheaders_plugin.zip'

    if remove_headers is None:
        remove_headers = []

    if add_or_modify_headers is None:
        add_or_modify_headers = {}

    assert isinstance(remove_headers, list), "remove_headers must be a list"
    assert isinstance(add_or_modify_headers, dict), "add_or_modify_headers must be dict"

    # only keeping the unique headers key in remove_headers list
    remove_headers = list(set(remove_headers))


    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome HeaderModV",
        "permissions": [
            "webRequest",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequestBlocking",
            "http://*/*, https://*/*"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
    """
    function callbackFn(details) {
        var remove_headers = ${remove_headers};
        var add_or_modify_headers = ${add_or_modify_headers};

        function inarray(arr, obj) {
            return (arr.indexOf(obj) != -1);
        }

        // remove headers
        for (var i = 0; i < details.requestHeaders.length; ++i) {
            if (inarray(remove_headers, details.requestHeaders[i].name)) {
                details.requestHeaders.splice(i, 1);
                var index = remove_headers.indexOf(5);
                remove_headers.splice(index, 1);
            }
            if (!remove_headers.length) break;
        }

        // modify headers
        for (var i = 0; i < details.requestHeaders.length; ++i) {
            if (add_or_modify_headers.hasOwnProperty(details.requestHeaders[i].name)) {
                details.requestHeaders[i].value = add_or_modify_headers[details.requestHeaders[i].name];
                delete add_or_modify_headers[details.requestHeaders[i].name];
            }
        }

        // add modify
        for (var prop in add_or_modify_headers) {
            details.requestHeaders.push(
                {name: prop, value: add_or_modify_headers[prop]}
            );
        }

        return {requestHeaders: details.requestHeaders};
    }

    chrome.webRequest.onBeforeSendHeaders.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking', 'requestHeaders']
    );
    """
    ).substitute(
        remove_headers=remove_headers,
        add_or_modify_headers=add_or_modify_headers,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path
