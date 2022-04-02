import string
import random


class userX:
    fullname = "Jean Dupont"
    username = "".join(random.choice(string.ascii_lowercase) for i in range(5))  
    password = "AxsEred457"
    
#DELETE FROM custumer where fullname="Jean Dupont"
