#!/usr/bin/python

from DatabaseConnection import Database

def login(username, password):
    existence = username_existence(username)
    if not existence:
        result = "UNE"
        return result
    else:
        user_id = database.find_user_id(username)
        match = database.match_password(password, user_id)
        if not match:
            result = "WP"
            return result
        else:
            print("Login successfully")
            return True

def signup(name, passwd, confirm_passwd):
    exist_name = username_existence(name)
    if exist_name:
        result = "EN"
        return result
    else:
        valid_passwd = password_validation(passwd, confirm_passwd)
        if not valid_passwd:
            result = "UP"
            return result

    database.signup(name, passwd)
    return True

def username_existence(name):
    return database.search_username(name)

def password_validation(pass1, pass2):
    if pass1 != pass2:
        return False
    return True
    
database = Database()
