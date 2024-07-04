import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from cdrive import generate_result_list, identify_and_fill_fields

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Web HTML Fetcher")

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=20)
        self.text_area.pack(padx=10, pady=10)

        self.button = tk.Button(root, text="Fetch HTML", command=self.fetch_html)
        self.button.pack(pady=10)

        self.start_browser()

    def start_browser(self):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get("https://www.example.com")

    def fetch_html(self):
        try:
            # Switch to the rightmost (most recent) tab
            self.driver.switch_to.window(self.driver.window_handles[-1])
            html_source = self.driver.page_source
            self.text_area.delete('1.0', tk.END)
            matched_content = generate_result_list(html_source)
            outputstr = "\n".join(t[0] + ":" + t[1] for t in matched_content)
            self.text_area.insert(tk.INSERT, outputstr)

            for tp in matched_content:
                k, v = tp
                try:
                    self.driver.find_element(By.NAME, k).send_keys(v)
                except Exception as e:
                    print(e)

        except Exception as e:
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.INSERT, f"Error fetching HTML: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
