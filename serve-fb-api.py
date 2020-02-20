from flask import Flask, jsonify, abort, make_response
from flask_restful import Api, Resource, reqparse, fields, marshal
import pickle, time, re, json, os, sqlite3, csv
from dateutil.parser import parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)
api = Api(app)

comments = []
userPost = []
biography = []
_profileData = {}

_DRIVER = webdriver.Chrome()

_login_status = {
    'Status': False,
    'Logged in As': None
}

_login_status_fields = {
    'Status': fields.String,
    'Logged in as': fields.String
}

credentials_fields = {
    'email': fields.String,
    'password' : fields.String
}

comments_fields = {
    'comment_text': fields.String
}

userPost_fields = {
        'postText' : fields.String,
        'postDate' : fields.String,
        'postUrl' : fields.String,
        'reactionCount' : fields.String,
        'commentPost' : fields.List(fields.Nested(comments_fields))
}

biography_fields = {
    'biography':fields.String
}

profileData_fields = {
        'profile_url': fields.String,
        'fullName': fields.String,
        'userID' : fields.String,
        'photoProfile': fields.String,
        'coverImage' : fields.String,
        'biography' : fields.List(fields.Nested(biography_fields)),
        'birthday' : fields.String,
        'relationship' : fields.String,
        'friendCount' : fields.String,
        'posts' : fields.List(fields.Nested(userPost_fields))
}

class commentPosts:
    def __init__(self,comment_text):
        self.comment_text = comment_text

class biograpy_obj:
    def __init__(self,biography_input):
        self.biography = biography_input

class userPost:
    def __init__(self,post_url):
        self.postText = ""
        self.postDate = ""
        self.postUrl = post_url
        self.reactionCount = ""
        self.commentPost = []

    def grab_post(self):
        global _DRIVER

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

        comments = _DRIVER.find_elements_by_xpath("//div[@class='_72vr']")
        for comment in comments:
            # print(comment.text)
            c = commentPosts(comment.text)
            self.commentPost.append(marshal(c,comments_fields))

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
        global _DRIVER

        #get fullname
        self.full_name = _DRIVER.find_element_by_xpath("//a[@class='_2nlw _2nlv']").text

        #get user ID
        webelement_userID = _DRIVER.find_element_by_xpath("//div[@class='photoContainer']//a")
        urlString_id = webelement_userID.get_attribute("href")
        self.userID = re.findall('=a.(.*)&type', urlString_id)[0]
        
        #get photo and cover image url
        self.photoProfile = _DRIVER.find_element_by_xpath("//div[@class='photoContainer']//img").get_attribute('src')
        self.coverImage = _DRIVER.find_element_by_xpath("//img[@class='coverChangeThrobber img']").get_attribute('src')

        #get biography
        biography = _DRIVER.find_elements_by_xpath("//div[@class='_50f3']")
        for b in biography:
            bio = biograpy_obj(b.text)
            self.biography.append(marshal(bio,biography_fields))
        
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
        # for i in range(0,3):
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
                self.posts.append(marshal(post,userPost_fields))

    def get_profile_data(self):
        try:
            j = {'profile_url': self.profile_url,
                'full_name' : self.full_name,
                'user_ID' : self.userID,
                'birthday': self.birthday,
                'photo_profile' : self.photoProfile,
                'cover_image' : self.coverImage,
                'biography' : self.biography,
                'relationship' : self.relationship,
                'friend_count': self.friendCount,
                'posts':self.posts
                }
        
        except:
            j = {'status':'error'}

        return j

class dumpData:
    def __init__(self,profileData):
        self.conn = sqlite3.connect('newslist.db')
        self.new_profile_data = profileData

    def save_db(self):

        if self.conn is not None:
            c = self.conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS profile_data (user_ID integer PRIMARY KEY, profile_url text NOT NULL, full_name text NOT NULL,
                                    photo_profile text NOT NULL, cover_image text NOT NULL, biography text NOT NULL, birthday text NOT NULL,
                                    relationship text NOT NULL,friendcount text NOT NULL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS posts (
                                    post_id integer PRIMARY KEY AUTOINCREMENT, post_date text NOT NULL, post_text text NOT NULL,
                                    post_url text NOT NULL, reaction_count integer NOT NULL)''')
            c.execute(''' CREATE TABLE IF NOT EXISTS comments (
                                    comment_id integer PRIMARY KEY AUTOINCREMENT,
                                    comment_text text)''')
            c.execute('''CREATE TABLE IF NOT EXISTS user_to_post (user_to_post_id integer PRIMARY KEY AUTOINCREMENT, user_ID_f integer, post_id_f integer,
                            FOREIGN KEY (user_ID_f) REFERENCES profile_data (user_ID),
                            FOREIGN KEY (post_id_f) REFERENCES posts (post_id))''')
            c.execute('''CREATE TABLE IF NOT EXISTS post_to_comments (post_to_comments_id integer PRIMARY KEY AUTOINCREMENT, post_id_f integer, comment_id_f integer,
                                FOREIGN KEY (post_id_f) REFERENCES posts (post_id),
                                FOREIGN KEY (comment_id_f) REFERENCES comments (comment_id))''')

            bio = ""
            try:
                for b in self.new_profile_data.get('biography'):
                    bio += f"{b.get('biography')}, "

                user_data = (self.new_profile_data.get('userID'),self.new_profile_data.get('profile_url'),self.new_profile_data.get('fullName'),self.new_profile_data.get('photoProfile'),self.new_profile_data.get('coverImage'),
                            bio, self.new_profile_data.get('birthday'), self.new_profile_data.get('relationship'),self.new_profile_data.get('friendCount'))
                cur_user_data = self.conn.cursor()
                cur_user_data.execute('insert into profile_data values (?,?,?,?,?,?,?,?,?)',user_data)


                for p in self.new_profile_data.get('posts'):
                    cur_post = self.conn.cursor()
                    post = (p.get('postText'),p.get('postDate'),p.get('postUrl'),p.get('reactionCount'))
                    cur_post.execute('insert into posts(post_date, post_text, post_url, reaction_count) values (?,?,?,?)',post)

                    temp_pid = cur_post.lastrowid


                    cur_user2post = self.conn.cursor()
                    user2post = (self.new_profile_data.get('userID'),temp_pid)
                    cur_user2post.execute('insert into user_to_post(user_ID_f, post_id_f) values(?,?)',user2post)

                    for c in p.get('commentPost'):
                        cur_comm = self.conn.cursor()
                        comm = (c.get('comment_text'),)
                        # print(comm)
                        cur_comm.execute('insert into comments(comment_text) values (?)',comm)

                        temp_cid = cur_comm.lastrowid

                        cur_post2comm = self.conn.cursor()
                        comm2post = (temp_pid,temp_cid)
                        cur_user2post.execute('insert into post_to_comments(post_id_f, comment_id_f) values(?,?)',comm2post)

                self.conn.commit()
            except:
                print('user id exist')
        

    def save_csv(self):
        if self.new_profile_data != None:
            with open("profile-data.csv",'w',newline='') as profile_csv:
                write = csv.DictWriter(profile_csv,self.new_profile_data.keys())
                write.writeheader()
                write.writerow(self.new_profile_data)


    def save_json(self):
        if self.new_profile_data != None:
            try:
                with open('profile-data.json','w')as jsonfile:
                    data = json.load(jsonfile)
                    temp = data['Profile data']
                    temp.append(self.new_profile_data)
                    json.dump(data,jsonfile,indent=4)
            except:
                with open('profile-data.json','w')as jf:
                    json.dump(self.new_profile_data,jf,indent=4)
        else:
            print('empty profile data')

'''
Check login state

Login is required to view target's profile
Password and Email used for login is not stored, but the server stores the cookie used to login to facebook.
To log out and destroy cookie, go to http://www.127.0.0.1/fb-api/logout
'''
class loginStatus(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email',type=str, required = True, help='Your Facebook Email')
        self.reqparse.add_argument('password',type=str, required = True, help='password')
        super(loginStatus,self).__init__()

    def get(self):
        global _login_status
        global _DRIVER
        try:
            cookie = pickle.load(open("cookies.pkl","rb"))
            _DRIVER.get("https://www.facebook.com/")
            for i in cookie:
                if 'expiry' in i:
                    del i['expiry']
                _DRIVER.add_cookie(i)
            time.sleep(1.5)
            _DRIVER.get("https://www.facebook.com/")
            logged_in_as = _DRIVER.find_element_by_xpath("//a[@class='_5afe']").text
            _login_status = {'Status':True,'Logged in as':logged_in_as}
            return _login_status
        except:
            _login_status = {'Status':False,'Logged in as':None}
            return _login_status
    
    def post(self):
        global _login_status
        global _DRIVER

        if _login_status['Status']==False:
            args = self.reqparse.parse_args()
            _DRIVER.get("https://www.facebook.com/")
            time.sleep(1)
            username = _DRIVER.find_element_by_id("email")
            password = _DRIVER.find_element_by_id("pass")
            submit   = _DRIVER.find_element_by_id("loginbutton")

            username.send_keys(args['email'])
            password.send_keys(args['password'])

            submit.click()
            time.sleep(1)
            _DRIVER.get("https://www.facebook.com/")
            pickle.dump(_DRIVER.get_cookies(), open('cookies.pkl','wb'))
            logged_in_as = _DRIVER.find_element_by_xpath("//a[@class='_5afe']").text
            _login_status = {'Status':True,'Logged in as':logged_in_as}
            return _login_status
        elif _login_status['Status']==True:
            return _login_status

class logoutFB(Resource):
    def __init__(self):
        super(logoutFB,self).__init__()
    
    def get(self):
        global _login_status
        global _DRIVER

        if _login_status['Status']==True:
            _DRIVER.quit()
            _login_status = {'Status':False,'Logged in as':None}
            os.remove('cookies.pkl')
            _DRIVER = webdriver.Chrome()
        else:
            pass
        return _login_status

    def post(self):
        pass


class findUserData(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('u',type=str, required = True, help='Enter name to find')
        super(findUserData,self).__init__()

    def post(self):
        global _login_status
        global _DRIVER
        time.sleep(10)
        args = self.reqparse.parse_args()
        name_to_find = args['u']
        if _login_status['Status'] == True:
            _DRIVER.get("http://www.facebook.com/")

            time.sleep(5)
            input_keyword = _DRIVER.find_element_by_name("q")
            input_keyword.send_keys(name_to_find)
            input_keyword.submit()
            

            time.sleep(5)
            link = _DRIVER.find_element_by_xpath("//a[@data-ft='{\"tn\":\"-]\"}']").get_attribute('href')
            _DRIVER.get(link)
            time.sleep(1)

            current_profile_url = _DRIVER.current_url
            current_profile_url = current_profile_url.split('?')
            current_profile = profileData(current_profile_url[0])
            current_profile.grab_personals()
            # print(current_profile.get_json())

            global _profileData
            _profileData['profile_url']= current_profile.profile_url
            _profileData['fullName']= current_profile.full_name
            _profileData['userID']= current_profile.userID
            _profileData['photoProfile']= current_profile.photoProfile
            _profileData['coverImage']= current_profile.coverImage
            _profileData['biography']= current_profile.biography
            _profileData['birthday']= current_profile.birthday
            _profileData['relationship']= current_profile.relationship
            _profileData['friendCount']= current_profile.friendCount
            _profileData['posts']= current_profile.posts

            dumpdata = dumpData(_profileData)
            dumpdata.save_csv()
            dumpdata.save_json()
            # dumpdata.save_db()
            
            return {'Profile data': (marshal(_profileData,profileData_fields))}
        else:
            return {'message':"need login"},400


api.add_resource(loginStatus, '/fb-api/login', endpoint='loginCheck')
api.add_resource(logoutFB, '/fb-api/logout', endpoint='logout')
api.add_resource(findUserData, '/fb-api/find-user', endpoint='findUser')

def check_login():
    global _login_status
    global _DRIVER
    try:
        cookie = pickle.load(open("cookies.pkl","rb"))
        _DRIVER.get("https://www.facebook.com/")
        for i in cookie:
            if 'expiry' in i:
                del i['expiry']
            _DRIVER.add_cookie(i)
        time.sleep(1.5)
        _DRIVER.get("https://www.facebook.com/")
        logged_in_as = _DRIVER.find_element_by_xpath("//a[@class='_5afe']").text
        _login_status = {'Status':True,'Logged in as':logged_in_as}
    except:
        _login_status = {'Status':False,'Logged in as':None}

def main():
    global _login_status
    check_login()
    # app.run(debug=True)
    app.run(debug=False)

if __name__ == '__main__':
    main()