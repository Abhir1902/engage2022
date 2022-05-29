import streamlit as st
import pickle
import pandas as pd
from streamlit_lottie import st_lottie
import requests
import pyrebase
def load_lotter(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
# function for recommendation
def recommend_function(laptop_brand,laptop_model,user_choice):
    laptop_index = laptop_df[(laptop_df['brand']==laptop_brand) & (laptop_df['model']==laptop_model)].index[0]
    t = laptop_df.loc[laptop_index,'laptop_id']
    
    distances = similarity[int(t)]
    laptop_list=sorted(list(enumerate(distances)),reverse = True,key = lambda x:x[1])[0:10]
    index = laptop_df.index
    recommended_laptop = []
    for i in laptop_list:
        s = [ str(integer) for integer in (index[i[0]==laptop_df['laptop_id']].tolist())]
        p = int("".join(s))
        recommended_laptop.append(laptop_df.loc[p,['brand','model','star_rating']].tolist())
    if len(user_choice)==2:
        for i in user_choice:
            t = recommend_function(i[0],i[1],user_choice)
            for j in t:
                recommended_laptop.insert(0,t)   
    return recommended_laptop
# Authentication for the user
config = {
    "apiKey": "AIzaSyB-WA5RK8Jvoza6KaGjrn5ihpCfHYp5_8c",
    "authDomain": "lapshop-d42ed.firebaseapp.com",
    "databaseURL": "https://lapshop-d42ed-default-rtdb.firebaseio.com/",
    "storageBucket": "lapshop-d42ed.appspot.com",
    "projectId" : "lapshop-d42ed",
    "messagingSenderId" : "509472297259",
    "appId" : "1:509472297259:web:c424f80ff085d5f940f56"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
# Database for storage of user's data. 
db = firebase.database()
st.set_page_config(layout="wide")
laptop_dict = pickle.load(open('laptop_dict.pkl','rb'))
laptop_df = pd.DataFrame(laptop_dict)
similarity = pickle.load(open('similarity.pkl','rb'))
with st.sidebar:
    st.markdown("""
    <style>
    .big-font {
        font-size:25px!important;
        font-weight: bold;
        background: #282525;
        box-shadow:  20px 20px 60px #221f1f,-20px -20px 60px #2e2b2b; 
        border-radius: 10px;
        text-align: center; 
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<p class="big-font">Login/Signup</p>', unsafe_allow_html=True)
    choice = st.selectbox('Choose',['Login in','Sign up'])
    email = st.text_input("Email address")
    password = st.text_input("Password")
    userName = ""
    if choice=="Sign up":
        handle = st.text_input('Username',value = 'Default')
        submit = st.button('Create my account')

        if submit: 
            user = auth.create_user_with_email_and_password(email,password)
            st.success("Your account is created successfully")
            db.child(user["localId"]).child("Handle").set(handle)
            db.child(user["localId"]).child("ID").set(user['localId'])
            db.child(user['localId']).child('userChoice')
    else :
        submit = st.button("Login")
        if submit:
            user = auth.sign_in_with_email_and_password(email,password)
            userName = user['localId']
            st.success("Successfully logged in")
st.markdown("<h1 style='text-align: center; color: white;border-radius: 50px;background: #282525;box-shadow:  20px 20px 60px #221f1f,-20px -20px 60px #2e2b2b; border-radius: 10px'>Lapfo</h1>", unsafe_allow_html=True)
option = st.selectbox(
    "Search for the model and brand you want",
    set(laptop_df['brand'].values + " " + laptop_df['model'].values)
)
button1 = st.button('Search')
if st.session_state.get('button')!=True:
    st.session_state['button'] = button1
count = 1
file = open("usersChoice.txt",'w')
user_choice = []
if st.session_state['button']==True: 
    laptopInfo = option.split(" ")
    laptop_brand,laptop_model = laptopInfo[0], laptopInfo[1]
    recommendations = recommend_function(laptop_brand,laptop_model,user_choice)
    # print(recommendations)
    col1, col2, col3 = st.columns(3)
    for i in recommendations: 
        recommended_laptop_brand = i[0]
        recommended_laptop_model = i[1]
        recommended_laptop_star_rating = i[2]
        for k in laptop_df.index:
            if laptop_df.loc[k,'brand']==i[0] and laptop_df.loc[k,'model']==i[1]:
                t = laptop_df.loc[k,['ram_gb','latest_price','storage_type','storage_space']].tolist()
        if count%3==0:
            with col1:
                expander = st.expander(recommended_laptop_brand+" "+recommended_laptop_model)
                if expander.expanded==True:    
                    if len(userName)!=0:
                        db.child(user[userName]).child('userChoice').update({recommended_laptop_brand})
                s = format(t[1], ',d')
                expander.write("Presenting to you the %s %s.\nLaptop has the RAM capacity of %s.If you are planning to buy one, the latest prices will be ₹%s. The storage type of the laptop is %s and the storage space is %d."%(recommended_laptop_brand,recommended_laptop_model,t[0][:-2],s,t[2],t[3]))
        if count%3==1:
            with col2:
                expander = st.expander(recommended_laptop_brand+" "+recommended_laptop_model)
                if expander.expanded==True: 
                    if len(userName)!=0:
                        db.child(user[userName]).child('userChoice').update({recommended_laptop_brand})
                s = format(t[1], ',d')
                expander.write("Presenting to you the %s %s.\nLaptop has the RAM capacity of %s.If you are planning to buy one, the latestprices will be ₹%s. The storage type of the laptop is %s and the storage space is %d."%(recommended_laptop_brand,recommended_laptop_model,t[0][:-2],s,t[2],t[3]))
        if count%3==2:
            with col3:
                expander = st.expander(recommended_laptop_brand+" "+recommended_laptop_model)
                if expander.expanded==True: 
                    if len(userName)!=0:
                        db.child(user[userName]).child('userChoice').update({recommended_laptop_brand}) 
                s = format(t[1], ',d')
                expander.write("Presenting to you the %s %s.\nLaptop has the RAM capacity of %s.If you are planning to buy one, the latest priceswill be ₹%s. The storage type of the laptop is %s and the storage space is %d."%(recommended_laptop_brand,recommended_laptop_model,t[0][:-2],s,t[2],t[3]))
        count+=1 