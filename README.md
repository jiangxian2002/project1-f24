# Rating/Social App for Broadway Shows

Team Members: Jessica Yo (jay2143), Xian Jiang (xj2281)

## Description
The application is a social platform where users can share, review, and discuss Broadway musicals. Users can follow others, build wishlists of upcoming shows, and rate or comment on musicals they have watched. Users, musicals, showtimes, theatres, and cast/production are key entities. Users can interact by reviewing musicals, finding showtimes, adding favorites to their wishlist, and engaging with other users. Data could be populated from real-world Broadway schedules and actor profiles. The challenge involves managing user interaction, diverse showtime schedules, and personalized recommendations. This model is based on the Beli app, and other social media, that allow a community to interact and find common interests to explore. 


## Link to Website
[http://35.185.108.243:8111/](http://35.185.108.243:8111/)

## How to Run
Use a .env file and dotenv module to load database credentials

```
DB_USER="your_username"
DB_PASSWORD="your_password"
DB_SERVER="your_server"
```


## Example Credentials
Username: amy

Email: amy@123.com

Password: amy


Username: ABC

Email: abc@123.com

Password: ABC


Username: test

Email: test@123.com

Password: test


## Features

### Without Login

#### Homepage
<img width="1506" alt="image" src="https://github.com/user-attachments/assets/377da671-630a-4ccf-9ec0-9dfe7a90de9f">

List of musicals that can be clicked on to display more details

#### Search function supported
<img width="1511" alt="image" src="https://github.com/user-attachments/assets/b101a21c-458a-4dee-bd70-1c06accebb9f">

Searches for titles that contain the search string (case ignored)

#### Musical Page 
<img width="1510" alt="image" src="https://github.com/user-attachments/assets/e6c0eb44-263a-4252-b2f7-b6b785aa446d">

<img width="1512" alt="image" src="https://github.com/user-attachments/assets/1a1e5ed2-8bb8-4537-bd3f-0b22b3484d2a">

Links to theatres and cast members

Requires login to comment

#### Theatre Page 
<img width="1510" alt="image" src="https://github.com/user-attachments/assets/e6b13049-f2b4-4435-a1cf-b89fd5b8076c">
Links back to musicals

#### Cast Member Page 
Links back to musicals

### User Features with Login

#### Register for an account 
<img width="1508" alt="image" src="https://github.com/user-attachments/assets/340b5c93-be55-46ec-8f56-06a5c045c046">
Users can register for an account

#### Login with account credentials
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/8e01f625-e334-4cd6-9b3b-d87ac303d810">

#### Homepage after login
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/e060b09f-e303-414e-9c9d-35710937cefc">


#### Accounts page
<img width="1506" alt="image" src="https://github.com/user-attachments/assets/732136cd-e06d-4df1-9346-4be70d136b25">

Can update their bio and city, view followers and following, and logout.


#### Following page 
<img width="1506" alt="image" src="https://github.com/user-attachments/assets/463c0fa4-cd7e-4375-b530-9e191d37a482">
Links to profile

#### Followers page
Similar


#### Manage Social Page
<img width="1506" alt="image" src="https://github.com/user-attachments/assets/550c809e-336e-48cf-91d0-987f9312c242">

Allow for follow, unfollow, and remove follow
Links to each profile

### User page
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/3fe20bf4-9dcf-4f5f-bd22-032ce58f923f">
Display some basic information on that user 

