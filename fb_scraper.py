from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import pickle, time, re, json, os
from dateutil.parser import parse

_DRIVER = webdriver.Chrome()

class credentials:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.cookie = ""

        global _DRIVER

    def set_username(self):
        input_username = input("Email:")
        self.username = input_username
    
    def set_password(self):
        input_password = input("Password:")
        self.password = input_password
    
    def load_cookie(self):
        cookie = pickle.load(open("cookies.pkl","rb"))
        for i in cookie:
            if 'expiry' in i:
                del i['expiry']
            _DRIVER.add_cookie(i)
        time.sleep(1)
        _DRIVER.get("https://www.facebook.com/")

    #login function
    def __login(self):
        time.sleep(1)
        print("Login Required")
        username = _DRIVER.find_element_by_id("email")
        password = _DRIVER.find_element_by_id("pass")
        submit   = _DRIVER.find_element_by_id("loginbutton")

        self.set_username()
        self.set_password()

        if not self.username or not self.password:
            print("empty email/password")
        else:
            #login and save cookie
            username.send_keys(self.username)
            password.send_keys(self.password)
            submit.click()
            _DRIVER.get("https://www.facebook.com/")
            pickle.dump(_DRIVER.get_cookies(), open('cookies.pkl','wb'))

    def destroy_cookie(self):
        self.cookie=''
        os.remove('cookies.pkl')


    def check(self):
        #load cookie, if not exist, create one by login
        try:
            self.load_cookie()
        except:
            self.__login()

class userPost:
    def __init__(self,post_url):
        self.postText = ""
        self.postDate = ""
        self.postUrl = post_url
        self.reactionCount = ""
        self.commentPost = []

        global _DRIVER

    def append_comments(self,comment_text):
        self.commentPost.append({'comment':comment_text})

    def grab_post(self):
        time.sleep(3)
        _DRIVER.get(self.postUrl)
        try:
            self.postText = _DRIVER.find_element_by_xpath("//div[@class='_5pbx userContent _3576']").text
        except:
            self.postText = "<empty text>"
        self.postDate = _DRIVER.find_element_by_xpath("//span[@class='timestampContent']").text

        try:
            reactionCount = _DRIVER.find_element_by_xpath("//span[@data-testid='UFI2ReactionsCount/sentenceWithSocialContext']").text
            if "and" in reactionCount:
                self.reactionCount = int(re.sub('[^0-9]','',reactionCount.text)) + 1
            else:
                self.reactionCount = reactionCount
        except:
            self.reactionCount = 0

        comments = _DRIVER.find_elements_by_xpath("//div[@class=' _6qw3']")
        for comment in comments:
            self.append_comments(comment.text)

class profileData:
    def __init__(self,profile_url):
        self.profile_url = profile_url
        self.full_name = ""
        self.userID = ""
        self.photoProfile = ""
        self.coverImage = ""
        self.biography = []
        self.birthday = ""
        self.relationship = ""
        self.friendCount = ""
        self.posts = []
        self.postUrls = []

        global _DRIVER

    def grab_personals(self):
        #get 
        self.full_name = _DRIVER.find_element_by_xpath("//a[@class='_2nlw _2nlv']").text

        #get user ID
        webelement_userID = _DRIVER.find_element_by_xpath("//div[@class='photoContainer']//a")
        urlString_id = webelement_userID.get_attribute("href")
        self.userID = re.findall('=a.(.*)&type', urlString_id)
        
        #get photo and cover image url
        self.photoProfile = _DRIVER.find_element_by_xpath("//div[@class='photoContainer']//img").get_attribute('src')
        self.coverImage = _DRIVER.find_element_by_xpath("//img[@class='coverChangeThrobber img']").get_attribute('src')

        #get biography
        biography = _DRIVER.find_elements_by_xpath("//div[@class='_50f3']")
        for b in biography:
            self.biography.append({'bio_text' : b.text})
        
        #grab birthday
        _DRIVER.get(f"{self.profile_url}/about?")
        birthday = _DRIVER.find_elements_by_xpath("//div[@class='_4bl9 _zu9']")
        for b in birthday:
            try:
                z = parse(b.text,fuzzy=True)
                self.birthday = z.strftime('%d %B')
            except:
                self.birthday = "not mentioned"


        #grab relationship
        _DRIVER.get(f"{self.profile_url}/about?section=relationship")        
        rels = _DRIVER.find_element_by_xpath("//div[@class='_42ef']").text
        if "married" in rels.lower():
            self.relationship = 'Married'
        elif "single" in rels.lower():
            self.relationship = "Single"
        elif "in a relationship" in rels.lower():
            self.relationship = "In relationship"
        elif "complicated" in rels.lower():
            self.relationship = "Complicated"
        elif "engaged" in rels.lower():
            self.relationship = "Engaged"
        elif "divorced" in rels.lower():
            self.relationship = "Divorced"
        elif "widowed" in rels.lower():
            self.relationship = "Widowed"
        elif "separated" in rels.lower():
            self.relationship = "Separated"
        elif "domestic" in rels.lower():
            self.relationship = "In a domestic partnership"
        elif "civil union" in rels.lower():
            self.relationship = "In a Civil union"
        else:
            self.relationship = "Not mentioned"

        #grab friends count
        time.sleep(1)
        _DRIVER.get(f"{self.profile_url}/friends")
        friendCount = _DRIVER.find_element_by_xpath("//a[@name='All Friends']").text
        friendCount = re.sub('[^0-9]','',friendCount)
        self.friendCount = friendCount

        #grab posts url
        time.sleep(1)
        _DRIVER.get(self.profile_url)
        page = _DRIVER.find_element_by_tag_name("html")
        for i in range(0,10):
            page.send_keys(Keys.END)
            time.sleep(1.5)

        
        post_urls = _DRIVER.find_elements_by_xpath("//a[@class='_5pcq']")
        for post_url in post_urls:
            p = post_url.get_attribute('href')
            self.postUrls.append(p)
        
        for stored_post_url in self.postUrls:
            if self.profile_url in stored_post_url:
            # self.post_url.append()
                post = userPost(stored_post_url)
                post.grab_post()
                self.posts.append(json.dumps(post.__dict__))

    
    def get_json(self):
        try:
            j = [
                {'profile_url': self.profile_url},
                {'full_name' : self.full_name},
                {'user_ID' : self.userID},
                {'birthday': self.birthday},
                {'photo_profile' : self.photoProfile},
                {'cover_image' : self.coverImage},
                {'biography' : self.biography},
                {'relationship' : self.relationship},
                {'friend_count': self.friendCount},
                {'posts':self.posts}
            ]
        
        except:
            j = {'status':'error'}

        return j

if __name__ == "__main__":
    _DRIVER.get("http://www.facebook.com/")
    login_data = credentials()
    time.sleep(1)
    login_data.check()

    name_to_find = input("Name to find:")
    input_keyword = _DRIVER.find_element_by_name("q")
    input_keyword.send_keys(name_to_find)
    input_keyword.submit()
    

    time.sleep(3)
    link = _DRIVER.find_element_by_xpath("//a[@data-ft='{\"tn\":\"-]\"}']").get_attribute('href')
    _DRIVER.get(link)
    time.sleep(1)

    current_profile_url = _DRIVER.current_url
    current_profile_url = current_profile_url.split('?')
    current_profile = profileData(current_profile_url[0])
    current_profile.grab_personals()
    print(current_profile.get_json())
    
