import json
import requests
import time
import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import ctypes
import random

class Bot:
    def __init__(self,driver,driver_location):
        self.info_file = "info/logininformation"          #specify a folder named info with a txt file called login info
        self.username = None
        self.password =None
        self.list_words = None
        self.url = "https://www.bing.com/"
        self.login_url = "https://login.live.com/"
        self.reward_url = "https://rewards.bing.com/"
        self.chrome_driver_location = driver_location
        self.driver = driver

    #close the current window and switch to main window
    def switch_main_window(self):
        time.sleep(5)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0]) #change back to the first tab

    #reset chrome driver to be able to log into next user without having issues with previous user still logged in
    def clear_driver(self):
        print("Resetting Chrome Driver.")
        self.driver.close()
        self.driver.quit()
        self.driver = webdriver.Chrome(service=self.chrome_driver_location)

    #parse and obtain username and password
    def get_user_info(self):
        with open(self.info_file, "r") as file:
            for lines in file:
                if "username" in lines:
                    self.username = (lines[lines.find(':') + 1:len(lines) - 1]).split(',')
                else:
                    self.password = lines[lines.find(':') + 1:len(lines) - 1].split(',')

    #obtain a list of random words from api call to use in search bar function
    def get_request_words(self):
        try:
            response = requests.get("https://random-word-api.herokuapp.com/word?number=35")
            self.list_words = json.loads(response.text)
        except Exception as e:
            print(e)
            print("Random word api server is down using manual words")
            self.list_words =["a","ability","able","about","above","accept","according","account","across","act","action","activity","actually","add",
                              "address","administration","admit","adult","affect","after","again",'against',"age","agency","agent","ago","agree","agreement",
                              "ahead","air",'all',"allow","almost","alone","along"]

    # login into microsoft with current user number
    def login_user(self):
        self.driver.get(self.url)
        self.driver.set_window_position(-1000, 0)
        time.sleep(5)
        # attempt to get login form, if page does not go to url, retry until it can
        while (self.login_url not in self.driver.current_url):
            self.driver.find_element(By.CLASS_NAME, "id_button").click()  # profile icon
            time.sleep(2)
        print(f"Login Form Retrieved, now logging in user.")
        self.driver.find_element(By.NAME, "loginfmt").send_keys(self.username)  # username path
        self.driver.find_element(By.ID, "idSIButton9").click()  # submit button
        time.sleep(3)
        self.driver.find_element(By.NAME, "passwd").send_keys(self.password)  # password path
        self.driver.find_element(By.ID, "idSIButton9").click()  # submit button
        time.sleep(3)
        self.driver.find_element(By.ID, "idBtn_Back").click()  # no button for remembering the user
        time.sleep(3)
        print("Login Successful")

    #perform auto search algo to reward points using the bing search bar
    def auto_searh(self):
        print("Initiating auto searching algorithm")
        time.sleep(2)
        for words in self.list_words:
            try:
                time.sleep(1)
                search_bar = self.driver.find_element(By.CLASS_NAME,"sb_form_q") #search bar
                time.sleep(1)
                search_bar.send_keys(words)
                time.sleep(1)
                search_bar.submit()
                time.sleep(1)
                self.driver.get(self.url) #reset to the search bar url
            except:
                time.sleep(1)
                self.driver.get(self.url) #force the browser to go back to the search bar if it fails above
                print("could not click on form because it was not clickable yet or going to search bar did not work")
                pass
        print("Finished auto searching")

    #this quiz format is for quizzes such as "test your smart" , "bing homepage quiz" "know your celebrity news"
    def quiz_format_one(self, elements,value,repetitions,quiz_name):
        try:
            elements[value].click()
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[1])
            for iterator in range(repetitions):
                time.sleep(2)
                self.driver.find_element(By.ID,f"ChoiceText_{iterator}_0").click() #chooses the first question in each question number
                time.sleep(3)
                self.driver.find_element(By.CLASS_NAME, "wk_button").click()
        except:
            print(f"Cannot finish task or {quiz_name} is already finished")
        self.switch_main_window()

    #this quiz format is for "this or that", "Supersonic quiz","Lightspeed quiz","word for word","who said it"
    def quiz_format_two(self,elements,value,quiz_name):
        try:
            elements[value].click()
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.find_element(By.ID, "rqStartQuiz").click()  # starts the quiz hits begin button
            if(quiz_name == "This or That?"):
                for iterator2 in range(10):
                    time.sleep(5)
                    self.driver.find_element(By.ID, "rqAnswerOption0").click()  # starts the quiz hits begin button
            elif(quiz_name == "Supersonic quiz"):
                for iterator4 in range(3):
                    for iterator5 in range(8):
                        time.sleep(5)
                        self.driver.find_element(By.ID, f"rqAnswerOption{iterator5}").click()  # starts the quiz hits begin button
            elif(quiz_name == "Lightspeed quiz"):
                for iterator3 in range(4):
                    time.sleep(4)
                    self.driver.find_element(By.ID, f"rqAnswerOption{random.randint(0, 3)}").click() #choose a random answer from 3 total answers
            elif(quiz_name == "True or false" or quiz_name == "Who said it?" or quiz_name == "Word for word"):
                time.sleep(4)
                self.driver.find_element(By.ID,f"rqAnswerOption0").click()  # first answer
                time.sleep(4)
                self.driver.find_element(By.ID,f"rqAnswerOption1").click()  # second answer
        except:
            print(f"Cannot finish task or {quiz_name} is already finished")
        self.switch_main_window()

    #this quiz format is for "daily poll", "true or false" and "hot takes"
    def quiz_format_three(self,elements,value,quiz_name):
        try:
            elements[value].click()
            time.sleep(3)
            self.driver.switch_to.window(self.driver.window_handles[1])     #switches focus to new windows tab
            time.sleep(2)
            if(quiz_name == "Hot takes"):
                self.driver.find_element(By.CLASS_NAME,"bt_PollRadio").click() # choose the first question
            else:
                self.driver.find_element(By.ID,"btoption0").click()  # second answer
        except:
            print(f"Cannot finish task or {quiz_name} is already finished")
        self.switch_main_window()

    #find all the card tags on the bing reward website and get points from them
    def farm_reward(self):
        print("Running Quiz Tasks")
        #attempt to retrive reward url constantly to make sure its the right url in order to run
        # the quizzes
        while(self.driver.current_url != self.reward_url):
            try:
                self.driver.get(self.reward_url)
            except Exception as e:
                print("error obtaining reward url, trying again")
        time.sleep(4)
        elements = self.driver.find_elements(By.TAG_NAME,"mee-card")  # tags of all the cards which have points to earn
        for value in range(0,len(elements)):
            time.sleep(3)
            try:
                if("Test your smarts" in elements[value].text):
                    self.quiz_format_one(elements,value,10,"Test your smarts")
                elif ("Bing homepage quiz" in elements[value].text):
                    self.quiz_format_one(elements,value,3,"Bing homepage quiz")
                elif ("This or That?" in elements[value].text):
                    self.quiz_format_two(elements,value,"This or That?")
                elif ("Supersonic quiz" in elements[value].text):
                    self.quiz_format_two(elements, value, "Supersonic quiz")
                elif("Lightspeed quiz" in elements[value].text):
                    self.quiz_format_two(elements,value,"Lightspeed quiz")
                elif("Daily poll" in elements[value].text ):
                    self.quiz_format_three(elements,value,"Daily poll")
                elif ("Hot takes" in elements[value].text):
                    self.quiz_format_three(elements, value, "Hot takes")
                elif("True or false" in elements[value].text):
                    self.quiz_format_two(elements,value,"True or false")
                elif("Who said it?" in elements[value].text):
                    self.quiz_format_two(elements,value,"Who said it?")
                elif("Word for word" in elements[value].text):
                    self.quiz_format_two(elements,value,"Word for word")
                elif("Know your celebrity news?" in elements[value].text):
                    self.quiz_format_one(elements,value,7,"Know your celebrity news?")
                else:
                    for i in range(4):
                        elements[value].click()
                        time.sleep(2)
                        #checks if card gives a pop up notification and clicks on it below
                        try:
                            self.driver.find_element(By.ID,"legalTextBox")  #attempts to find the notification pop-up
                            time.sleep(2)
                            self.driver.find_element(By.XPATH,
                                "/html/body/div[5]/div[2]/div[2]/mee-rewards-legal-text-box/div/div/div/div[3]/a").click() #if found then click on the link of the notification pop-up
                        except:
                            pass
                        time.sleep(2)
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        time.sleep(2)
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                        time.sleep(1)
            except:
                print("A tag could not be clicked, skipping to next one")
                continue
        time.sleep(2)

#start up bot, retrieve info , then farm points
def main():
    print("Welcome, to start press s on your keyboard to start the bot.")
    keyboard.wait("s")
    #use service object with manager to auto download most latest chrome driver
    chrome_driver_location = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_driver_location)
    driver.set_window_position(-1000,0)
    reward_bot = Bot(driver,chrome_driver_location)
    reward_bot.get_user_info()
    reward_bot.get_request_words()
    print(f"\nLogging in user")
    reward_bot.login_user()
    reward_bot.auto_searh()
    reward_bot.farm_reward()
    print("program is finished")
    time.sleep(1)
    reward_bot.clear_driver()

    #lock windows
    #ctypes.windll.user32.LockWorkStation()
    return 0

if __name__ == "__main__":
    main()