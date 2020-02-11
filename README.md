# MaxiMiser
#### Simple bonus optimization strategy of opening new checking or saving accounts

A web application to maximize bank account sign up strategy for optimal return based on user’s budget constraints and personalized requirements

Web Application Link: https://maximiser.herokuapp.com
[Project Slides](https://docs.google.com/presentation/d/e/2PACX-1vQG7KDThs3jOf9UwIpNeecrSf3KeJOFONO7UD6K0Eert46p6hyDwPmi1LgHxhtopPe9D5l68MMOZaBq/pub?start=false&loop=false&delayms=3000)

## Project Description

This project was built by Mengchao Jiang at Insight Data Science during the Spring 2020 Boston session.

New users can take advantage of bank sign up bonuses by opening checking and saving account without hurting their credit scores. For example, banks often require new users to open a checking or saving account and do monthly direct deposit to it to get a several bonus of several hundred with some constraints. As hundreds of different bonuses are released by banks every year, a problem that how to choose among those bonus to maximize the return within a fixed account numbers arises.  

This web application is built to help users to find an optimal bonus strategy to maximize the return based on user's personalized requirements. And an lazy strategy is also developed for comparison, which is the strategy how a lazy person will choose and earn without this web application.

## Directory Structure
```
├── README.md 
│
├── notebooks 
│   ├── scraping_data.ipynb    
│   └── extracting_features.ipynb
│
├── requirements.txt   
│           
├── data
│   ├── bonus_posts_page_1_30.csv 
│   ├── bonus_post.csv                 
│   └── real_time_bonuses.csv          
│
├── Procfile
│
└── maximiser.py
```
