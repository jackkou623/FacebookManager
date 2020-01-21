#!/usr/bin/python

import mysql.connector
import sys

class Database:
    def __init__(self):
        try:
            self.database = mysql.connector.connect( #have to modify this
                host = "36.220.218.138", 
                user = "root",
                passwd = "pw$",
                ssl_ca = "server-ca.pem",
                ssl_cert = "client-cert.pem",
                ssl_key = "client-key.pem",
                use_unicode = "True" 
            )
            self.cursor = self.database.cursor(buffered=True) 
        except:
            sys.exit("Something is wrong when trying connect to database\nTerminating...")

    def updateschedule(self, Actions_spec, id):
        print(str(Actions_spec[9]))
        schedule_query = "UPDATE `facebook`.`Schedules` SET `schedule_name` = %s,`share_link` = %s,`schedule_notes`= %s,`enable`= %s,`random_link`= %s,`random_time`= %s,`account_group_list`= %s,`comment_list`= %s,`link_list`= %s,`time_list`= %s WHERE `id` = '" + id + "';"
        schedule_tuple = (str(Actions_spec[0]), str(Actions_spec[1]), str(Actions_spec[2]), str(Actions_spec[3]), str(Actions_spec[4]), str(Actions_spec[5]), str(Actions_spec[6]), str(Actions_spec[7]), str(Actions_spec[8]), str(Actions_spec[9]))
        self.cursor.execute(schedule_query, schedule_tuple)
        self.database.commit()

    def retrieve_schedule_entry(self, schedule_id):
        self.cursor.execute("SELECT * FROM facebook.new_view2 WHERE `id` = '" + schedule_id + "';")
        schedule_entry = self.cursor.fetchone() 
        return schedule_entry

    def remove_schedule(self, schedule_id):
        self.cursor.execute("DELETE FROM `facebook`.`Schedules` WHERE (`id` = '" + schedule_id + "');")
        self.database.commit()

    def addschedule(self, username, Actions_spec):
        schedule_query = "INSERT INTO facebook.Schedules (`id`, `owner`, `schedule_name`,`share_link`,`schedule_notes`,`enable`,`random_link`,`random_time`,`account_group_list`,`comment_list`,`link_list`,`time_list`) VALUES (%s, %s, %s ,%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        schedule_id = self.generate_id("facebook.Schedules")
        schedule_tuple = (str(schedule_id), str(username), str(Actions_spec[0]), str(Actions_spec[1]), str(Actions_spec[2]), str(Actions_spec[3]), str(Actions_spec[4]), str(Actions_spec[5]), str(Actions_spec[6]), str(Actions_spec[7]), str(Actions_spec[8]), str(Actions_spec[9]))
        self.cursor.execute(schedule_query, schedule_tuple)
        self.database.commit()

    def updateGT(self,id,group_type):
        self.cursor.execute("UPDATE facebook.Accounts SET group_type = '" + group_type + "' WHERE ACID = " + id)
        self.database.commit()

    def update_ACTable(self,username):
        if username == 'Jack':
            self.cursor.execute("SELECT * FROM facebook.new_view ;")
        else:
            self.cursor.execute("SELECT * FROM facebook.new_view WHERE `owner` = '" + username + "';")
        ACTable = self.cursor.fetchall() 
        return ACTable

    def update_ScheduleTable(self,username):
        if username == 'Jack':
            self.cursor.execute("SELECT * FROM facebook.new_view2;")
        else:
            self.cursor.execute("SELECT * FROM facebook.new_view2 WHERE `owner` = '" + username + "';")
        ScheduleTable = self.cursor.fetchall() 
        return ScheduleTable

    def get_ScheduleID(self,username):
        if username == 'Jack':
            self.cursor.execute("SELECT id FROM facebook.new_view2;")
        else:
            self.cursor.execute("SELECT id FROM facebook.new_view2 WHERE `owner` = '" + username + "';")
        ScheduleId = self.cursor.fetchall() 
        return ScheduleId

    def update_Column_name(self):
        self.cursor.execute("SHOW COLUMNS FROM facebook.new_view;") 
        Column_name = self.cursor.fetchall() 
        return Column_name

    def update_Column_name2(self):
        self.cursor.execute("SHOW COLUMNS FROM facebook.new_view2;") 
        Column_name = self.cursor.fetchall() 
        return Column_name

    def get_ACNames(self,username):
        if username == 'Jack':
            self.cursor.execute("SELECT ACID,nickname,group_type FROM facebook.Accounts") 
        else:
            self.cursor.execute("SELECT ACID,nickname,group_type FROM facebook.Accounts WHERE owner = " + '"' + str(username) + '"') 
        ACNames = self.cursor.fetchall() 
        return ACNames

    def get_ACIDdata(self, ACID):
        self.cursor.execute("SELECT * FROM facebook.Accounts WHERE ACID = " + str(ACID))
        ACData = self.cursor.fetchone()
        return ACData

    def get_Group(self, ACID):
        self.cursor.execute("SELECT * FROM facebook.Group WHERE ACID2 = " + str(ACID))
        Group = self.cursor.fetchone()
        return Group

    def update_Groups(self, ACID, Groups):
        for a in range(len(Groups)):
            b = Groups[a]
            self.cursor.execute("UPDATE facebook.Group SET Group_" + str(a+1) + " = '" + b + "' WHERE ACID2 = " + str(ACID))
        self.cursor.execute("UPDATE facebook.Accounts SET group_count = '" + str(len(Groups)-1) + "' WHERE ACID = " + str(ACID))
        self.database.commit()

    def update_cookies(self, ACID, cookies):
        self.cursor.execute("UPDATE facebook.Accounts SET cookies = '" + str(cookies) + "' WHERE ACID = " + str(ACID))
        self.database.commit()

    def __del__(self):
        try:
            self.database.close()
        except:
            pass

    def signup(self, name, password):
        username_query = "INSERT INTO facebook.FANS_Users (`id`, `name`, `password`) VALUES (%s, %s, %s);"
        user_id = self.generate_id("facebook.FANS_Users")
        user_tuple = (user_id, name, password)
        self.cursor.execute(username_query, user_tuple)
        self.database.commit()

    def generate_id(self, table_name):
        sql_query = "SELECT id FROM %s ORDER BY id DESC LIMIT 1;"
        self.cursor.execute(sql_query % table_name)

        id_list = self.cursor.fetchall()
        next_id = int(id_list[0][0]) + 1 #The use of list is so interesting, this is called nested indexing

        return next_id

    def search_username(self, name):
        self.cursor.execute("SELECT name FROM facebook.FANS_Users")
        name_list = self.cursor.fetchall()

        for i in range(len(name_list)):
            if name == name_list[i][0]:
                return True

        return False

    def find_user_id(self, name):
        self.cursor.execute("SELECT `id` FROM facebook.FANS_Users WHERE `name` = '%s';" % name)
        id = self.cursor.fetchone()[0]
        return id

    def match_password(self, entered, user_id):
        self.cursor.execute("SELECT `password` FROM facebook.FANS_Users WHERE `id` = '%s';" % user_id)
        password = self.cursor.fetchone()[0]

        if password == entered:
            return True
        else:
            return False
