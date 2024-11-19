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

Can update their bio and city, view followers and following, and log out.


#### Following page 
<img width="1506" alt="image" src="https://github.com/user-attachments/assets/463c0fa4-cd7e-4375-b530-9e191d37a482">
Links to profile

#### Followers page
Similar


#### Manage Social Page
<img width="1506" alt="image" src="https://github.com/user-attachments/assets/550c809e-336e-48cf-91d0-987f9312c242">
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/e912a6d1-60c4-4232-a585-78443a4f5f38">
<img width="1507" alt="image" src="https://github.com/user-attachments/assets/00f739b3-a726-4fa9-8918-16ddc9ad9e68">

Allow for follow, unfollow, and remove follow functionalities
Links to each profile

#### User page
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/3fe20bf4-9dcf-4f5f-bd22-032ce58f923f">
Display some basic information on that user 


#### My Wishlist page
<img width="1505" alt="image" src="https://github.com/user-attachments/assets/d0f8a01c-d14c-4304-9a75-d8cc591db2a9">
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/4a87c707-01b0-4920-881c-49039cdb19da">

Shows all the musicals that the user has added to their wishlist

Can remove musicals from wishlist

Displays if other friends (bidirectional follows) have added the same musical to their wishlist, as well as their watch status (Useful for determining if there is anyone they can go watch that musical will)


Recommendations for wishlist are also displayed, and users can conveniently add that musical to their wishlist

We want to build a recommendation system, which will suggest musicals to every user based on the musicals that their friends enjoy (so much so that they have watched it twice, thrice, or even more). (Excludes shows that the user has watched or already added to their wishlist.)



#### Manage Showtimes
<img width="1502" alt="image" src="https://github.com/user-attachments/assets/4b2fc51e-85de-44fd-94bd-eda59e211818">

Can delete showtimes or edit their notes for the showtimes that they have gone to
<img width="382" alt="image" src="https://github.com/user-attachments/assets/971e5068-3833-4e05-94cb-1b14e3ad8ff7">
<img width="382" alt="image" src="https://github.com/user-attachments/assets/d713a3b4-d4e8-4f80-8f82-054f2b2170bc">


#### Musical page with login 
<img width="1512" alt="image" src="https://github.com/user-attachments/assets/6b6bebaf-ee53-4cd8-9d35-2f5672acc20b">
Add / remove wishlist functionality appears


<img width="880" alt="image" src="https://github.com/user-attachments/assets/124013f3-19aa-4014-9b4c-b087f531de65">
Add (with or without notes) / remove showtime functionality appears


Can now post comments
<img width="884" alt="image" src="https://github.com/user-attachments/assets/ea873d65-dbc6-41b4-ba7c-65f1df65ff4d">
<img width="886" alt="image" src="https://github.com/user-attachments/assets/2fbd4b80-3ab8-4a14-bb97-dfd31322bc25">


