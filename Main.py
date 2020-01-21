from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox, QTabWidget, QTableWidgetItem, QTableWidget, QInputDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QTime, QDateTime
from GUI_login import Ui_Login
from GUI_Signup import Ui_Dialog
from GUI_MainWindow import Ui_TabWidget
from GUI_ShareEditor import Ui_ShareEditor
from DatabaseConnection import Database
from MySQL_FB_Retrieve_Cookies import actions
from MySQL_FB_Share_Group import share_actions
import sys, random, hashlib, requests, threading, schedule
from datetime import datetime
from distutils.util import strtobool

class GUI_login(QDialog): 
    def __init__(self): 
        super(GUI_login, self).__init__() 
        self.ui = Ui_Login() 
        self.ui.setupUi(self) 
        self.ui.Login_btn.clicked.connect(self.login_clk)
        self.ui.Signup_btn.clicked.connect(self.signup_clk)

    def signup_clk(self):
        self.hide()
        if Signup.exec(): 
            pass
        self.show()

    def login_clk(self):
        from Login import login
        global username
        username = self.ui.Username.text()
        password = self.ui.Password.text()
        result = login(username, password)
        if result == "UNE":
            msg = QMessageBox()
            msg.setText("This user does not exist.")
            msg.exec()
        elif result == "WP":
            msg = QMessageBox()
            msg.setText("Wrong Password")
            msg.exec()
        elif result == True:
            self.hide() 
            MainWindow.show()
            MainWindow.load_info()
            MainWindow.table_refresh_clk()
            MainWindow.refresh_table_clk()
            MainWindow.schedule_table_refresh_clk()
            
class GUI_Signup(QDialog): 
    def __init__(self): 
        super(GUI_Signup, self).__init__() 
        self.ui = Ui_Dialog() 
        self.ui.setupUi(self) 
        self.ui.Signup_btn.clicked.connect(self.FANSSignup)

    def FANSSignup(self):
        if  encrypt(encode(self.ui.Password_3.text())) == "a37d225ff4746ca7e6b58f80cddf3bfc":
            from Login import signup
            name = self.ui.Username.text()
            passwd = self.ui.Password.text()
            confirm_passwd = self.ui.Password_2.text()
            result = signup(name, passwd, confirm_passwd)
            if result == "EN":
                msg = QMessageBox()
                msg.setText("Username exist already, try another one la!")
                msg.exec_()
            elif result == "UP":
                msg = QMessageBox()
                msg.setText("Two password don't match!")
                msg.exec_()
            elif result == True:
                msg = QMessageBox()
                msg.setText("Signup successfully, try try login la~")
                msg.exec_()
                self.hide()
                Login.show()
        else:
            msg = QMessageBox()
            msg.setText("No, You can't register by your own. Please Ask Jack =D")
            msg.exec_()

class GUI_MainWindow(QTabWidget): 
    def __init__(self): 
        super(GUI_MainWindow, self).__init__() 
        self.ui = Ui_TabWidget() 
        self.ui.setupUi(self) 
        self.ui.submit_btn_2.clicked.connect(self.cookies_thread)
        self.ui.refresh_btn_2.clicked.connect(self.table_refresh_clk)
        self.ui.submit_btn.clicked.connect(self.sharenow_thread)
        self.ui.ShareUsername_comboBox.currentIndexChanged.connect(self.updateGL_combo)
        self.ui.group_type_btn.clicked.connect(self.updateGT_clk)
        self.ui.add_btn.clicked.connect(self.add_clk)
        self.ui.refresh_btn.clicked.connect(self.refresh_table_clk)
        self.ui.remove_btn.clicked.connect(self.remove_entry_clk)
        self.ui.edit_btn.clicked.connect(self.edit_entry_clk)
        self.ui.refresh_schedule_btn.clicked.connect(self.schedule_table_refresh_clk)
        self.ui.run_schedule_btn.clicked.connect(self.run_schedule_clk)

    def schedule_share(self, rownum):
        Group = eval(schedule_task[rownum][7])
        share_actions(schedule_task[rownum][5], schedule_task[rownum][1], schedule_task[rownum][8], Group, True)

    def run_schedule_clk(self):
        self.ui.refresh_schedule_btn.setEnabled(False)
        self.ui.run_schedule_btn.setEnabled(False)
        self.ui.run_schedule_btn.setText("Scheduling Running. If you want to change running schedule, please restart the program.")

        global schedule_task
        schedule_task = []

        for row in range(self.ui.schedule_table.rowCount()):
            schedule_task.append([])
            for column in range(self.ui.schedule_table.columnCount()):
                schedule_task[row].append(str(self.ui.schedule_table.item(row, column).text()))

        threadlist = []
        for i in range(len(schedule_task)):
            threadlist.append(threading.Thread(target=self.schedule_share, args=(i,)))
            schedule.every().day.at(schedule_task[i][0]).do(threadlist[i].start) #threadlist[i].start() , no () sign, for () sign means run now

        thread_run_pending = threading.Thread(target=self.run_pending)
        thread_run_pending.start()
    
    def run_pending(self):
        while True:
            schedule.run_pending()

    def schedule_table_refresh_clk(self):
        id = Database().get_ScheduleID(username)
        schedule_task = []

        for i in id:
            schedule_entry = Database().retrieve_schedule_entry(i[0])
            if schedule_entry[5] == 'True':
                ac_data = eval(schedule_entry[8])
                for j in range(len(ac_data)):
                    if schedule_entry[6] == 'False' and schedule_entry[7] == 'False':
                        comment = eval(schedule_entry[9])
                        tasktr = [ac_data[j][2], schedule_entry[3], schedule_entry[2], schedule_entry[4], ac_data[j][0], ac_data[j][1], ac_data[j][3], ac_data[j][4], random.choice(comment)]
                        schedule_task.append(tasktr)
                    elif schedule_entry[6] == 'True' and schedule_entry[7] == 'False':
                        comment = eval(schedule_entry[9])
                        link = eval(schedule_entry[10])
                        tasktr = [ac_data[j][2], random.choice(link), schedule_entry[2], schedule_entry[4], ac_data[j][0], ac_data[j][1], ac_data[j][3], ac_data[j][4], random.choice(comment)]
                        schedule_task.append(tasktr)
                    elif schedule_entry[6] == 'False' and schedule_entry[7] == 'True':
                        comment = eval(schedule_entry[9])
                        time = eval(schedule_entry[11])
                        tasktr = [random.choice(time), schedule_entry[3], schedule_entry[2], schedule_entry[4], ac_data[j][0], ac_data[j][1], ac_data[j][3], ac_data[j][4], random.choice(comment)]
                        schedule_task.append(tasktr)
                    elif schedule_entry[6] == 'True' and schedule_entry[7] == 'True':
                        comment = eval(schedule_entry[9])
                        link = eval(schedule_entry[10])
                        time = eval(schedule_entry[11])
                        tasktr = [random.choice(time), random.choice(link), schedule_entry[2], schedule_entry[4], ac_data[j][0], ac_data[j][1], ac_data[j][3], ac_data[j][4], random.choice(comment)]
                        schedule_task.append(tasktr)

        table = self.ui.schedule_table
        table.setRowCount(len(schedule_task))
        if schedule_task == []:
            table.setColumnCount(0)
        else:
            table.setColumnCount(len(schedule_task[0]))
            horHeaders = ['Time', 'Share_link', 'Schedule_Name', 'Schedule_Notes', 'Group_Type/Name', 'ACID', 'Group_Count', 'Groups', 'Comments']

            for m in range(len(schedule_task)):
                for n in range(len(schedule_task[m])):
                    a = str(schedule_task[m][n])
                    newitem = QTableWidgetItem(a)
                    table.setItem(m, n, newitem)

            table.setHorizontalHeaderLabels(horHeaders)
            header = table.horizontalHeader()  
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            table.sortItems(0, QtCore.Qt.AscendingOrder)

    def edit_entry_clk(self):
        ShareEditor.load_info()
        row = self.ui.scheduler_table.currentRow()
        schedule_id = str(self.ui.scheduler_table.item(row, 0).text())
        ShareEditor.load_entryinfo(schedule_id)
        ShareEditor.show()

    def remove_entry_clk(self):
        confirm = QMessageBox.question(self, 'Please Confirm',"Are you sure you want to remove this entry?", QMessageBox.Yes | QMessageBox.No)
        if confirm == 16384:
            row = self.ui.scheduler_table.currentRow()
            schedule_id = str(self.ui.scheduler_table.item(row, 0).text())
            self.ui.scheduler_table.removeRow(row)
            self.ui.scheduler_table.sortItems(2, QtCore.Qt.AscendingOrder)
            Database().remove_schedule(schedule_id)

    def refresh_table_clk(self):
        ScheduleTable = Database().update_ScheduleTable(username)
        
        table = self.ui.scheduler_table
        table.setRowCount(len(ScheduleTable))
        if ScheduleTable == []:
            table.setColumnCount(0)
        else:
            table.setColumnCount(len(ScheduleTable[0]))

            Column_name = Database().update_Column_name2()

            horHeaders = []
            for m in range(len(ScheduleTable)):
                for n in range(len(ScheduleTable[m])):
                    horHeaders.append(Column_name[n][0])
                    a = str(ScheduleTable[m][n])
                    newitem = QTableWidgetItem(a)
                    table.setItem(m, n, newitem)
            table.setHorizontalHeaderLabels(horHeaders)
            header = table.horizontalHeader()  
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def add_clk(self):
        ShareEditor.load_info()
        ShareEditor.ui.label_12.setText("Schedule_id: None")
        ShareEditor.show()

    def updateGT_clk(self):
        try:
            id = QInputDialog.getText(self, "Change Group Type", "Enter ACID")
            if any(int(id[0]) in k for k in userlist) == True:
                group_type = QInputDialog.getText(self, "Change Group Type", "Enter group_type")
                Database().updateGT(id[0],group_type[0])
                self.table_refresh_clk()
            else:
                sys.exit()
        except:
            msg = QMessageBox()
            msg.setText("Incorrect ACID")
            msg.exec()

    def sharenow_clk(self):
        name = self.ui.ShareUsername_comboBox.currentText()
        link = self.ui.Link_line.text()
        comment = self.ui.Comment_line.text() 
        share_timeline = self.ui.timeline_cb.isChecked()
        ACID = self.get_ACID(name)
        SelectedGroup_table = self.ui.SelectedGroup_table
        b = SelectedGroup_table.rowCount()
        selected_group = []

        if b > 0:
            for i in range(b):
                selected_group.append(SelectedGroup_table.item(i,0).text())
        try:
            if selected_group == []:
                msg = QMessageBox()
                msg.setText("Group list has nothing")
                msg.exec_()
            elif requests.get(link).status_code == 200:
                share_actions(ACID, link, comment, selected_group, share_timeline)
                msg = QMessageBox()
                msg.setText("Share Actions Successfully Finished")
                msg.exec()
        except:
                msg = QMessageBox()
                msg.setText("Weblink incorrect")
                msg.exec_()

    def sharenow_thread(self):
        thread = threading.Thread(target=self.sharenow_clk)
        thread.start()

    def updateGL_combo(self):
        Group_table = self.ui.Group_table
        Group_table.setColumnCount(1)
        Group_table.setRowCount(0)

        SelectedGroup_table = self.ui.SelectedGroup_table
        SelectedGroup_table.setColumnCount(1)
        SelectedGroup_table.setRowCount(0)

        name = self.ui.ShareUsername_comboBox.currentText()
        ACID = self.get_ACID(name)
        GL = Database().get_Group(ACID)

        for i in range(1, len(GL)):
            if GL[i] == "END":
                break
            else:
                a = str(GL[i])
                c = QTableWidgetItem(a)
                Group_table.insertRow(Group_table.rowCount())
                Group_table.setItem(i-1,0,c)
        header = Group_table.horizontalHeader()       
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        Group_table.sortItems(0, QtCore.Qt.AscendingOrder)

    def get_ACID(self, name2):
        name = []
        for i in name2:
            if i == '/':
                name.pop()
                break
            else:
                name.append(i)

        for i in userlist:
            if "".join(name) == i[1]:
                global ACID
                ACID = i[0]
                break

        return(ACID)

    def table_refresh_clk(self):
        ACTable = Database().update_ACTable(username)
        
        #Create Empty Table
        table = self.ui.tableWidget
        table.setRowCount(len(ACTable))
        if ACTable == []:
            table.setColumnCount(0)
        else:
            table.setColumnCount(len(ACTable[0]))

            Column_name = Database().update_Column_name()

            horHeaders = []
            for m in range(len(ACTable)):
                for n in range(len(ACTable[m])):
                    horHeaders.append(Column_name[n][0])
                    a = str(ACTable[m][n])
                    newitem = QTableWidgetItem(a)
                    table.setItem(m, n, newitem)
            table.setHorizontalHeaderLabels(horHeaders)

    def load_info(self):
        global userlist
        userlist = Database().get_ACNames(username)

        for i in userlist:
            a = i[1] + " / " + i[2]
            self.ui.Username_comboBox.addItem(a)
            self.ui.ShareUsername_comboBox.addItem(a)

    def cookies_clk(self):
        name = self.ui.Username_comboBox.currentText()
        ACID = self.get_ACID(name)

        Actions_spec = [self.ui.RetrieveCookies_rbtn.isChecked(), self.ui.FBtoolkit_cb.isChecked(), self.ui.UpdateGL_cb.isChecked(), self.ui.AutoShutdown_rbtn.isChecked()]

        actions(Actions_spec, ACID)

    def cookies_thread(self):
        thread = threading.Thread(target=self.cookies_clk)
        thread.start()

class GUI_ShareEditor(QMainWindow): 
    def __init__(self): 
        super(GUI_ShareEditor, self).__init__() 
        self.ui = Ui_ShareEditor() 
        self.ui.setupUi(self) 
        self.ui.ShareUsername_comboBox.currentIndexChanged.connect(self.updateGL_combo)
        self.ui.AddAC_btn.clicked.connect(self.add_ac)
        self.ui.RemoveAC_btn.clicked.connect(self.remove_ac)
        self.ui.AddComment.clicked.connect(self.add_comment)
        self.ui.RemoveComment.clicked.connect(self.remove_comment)
        self.ui.Addlink_btn.clicked.connect(self.add_link)
        self.ui.Removelink_btn.clicked.connect(self.remove_link)
        self.ui.Addtime_btn.clicked.connect(self.add_time)
        self.ui.Removetime_btn.clicked.connect(self.remove_time)
        self.ui.randomlink_cb.clicked.connect(self.enable_pl)
        self.ui.randomtime_cb.clicked.connect(self.enable_tl)
        self.ui.saveall_btn.clicked.connect(self.saveall_clk)

    def load_entryinfo(self, schedule_id):
        schedule_entry = Database().retrieve_schedule_entry(schedule_id)

        self.ui.label_12.setText("Schedule_id: " + schedule_entry[0])
        self.ui.schedule_name.setText(schedule_entry[2])
        self.ui.share_link.setText(schedule_entry[3])
        self.ui.schedule_notes.setText(schedule_entry[4])
        self.ui.Enable_cb.setChecked(bool(strtobool(schedule_entry[5])))
        self.ui.randomlink_cb.setChecked(bool(strtobool(schedule_entry[6])))
        self.ui.randomtime_cb.setChecked(bool(strtobool(schedule_entry[7])))

        #add ac
        ac_data = eval(schedule_entry[8])
        Group_table = self.ui.Sharelist
        Group_table.setColumnCount(5)
        Group_table.setRowCount(0)
        Group_table.setHorizontalHeaderLabels(['Name/Group_type', 'ACID', 'Time', 'Group Count', 'Groups']) 
        
        for k in ac_data:
            Group_table.insertRow(Group_table.rowCount())
            for i in range(len(k)):
                c = QTableWidgetItem(str(k[i]))
                Group_table.setItem(Group_table.rowCount()-1,i,c)
            header = Group_table.horizontalHeader()      

        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        Group_table.sortItems(2, QtCore.Qt.AscendingOrder)

        #add comment
        comment_data = eval(schedule_entry[9])

        CommentList = self.ui.CommentList
        CommentList.setColumnCount(1)
        CommentList.setRowCount(0)

        for i in range(len(comment_data)):
            CommentList.insertRow(CommentList.rowCount())
            c = QTableWidgetItem(str(comment_data[i]))
            CommentList.setItem(CommentList.rowCount()-1,0,c)
        header = CommentList.horizontalHeader()      
        CommentList.setHorizontalHeaderLabels(['Comments']) 
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.ui.CommentList.sortItems(0, QtCore.Qt.AscendingOrder)

        #add link
        link_data = eval(schedule_entry[10])

        linklist = self.ui.PastlinkList
        linklist.setColumnCount(1)
        linklist.setRowCount(0)

        for i in range(len(link_data)):
            linklist.insertRow(linklist.rowCount())
            c = QTableWidgetItem(str(link_data[i]))
            linklist.setItem(linklist.rowCount()-1,0,c)
        header = linklist.horizontalHeader()      
        linklist.setHorizontalHeaderLabels(['Links']) 
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.ui.PastlinkList.sortItems(0, QtCore.Qt.AscendingOrder)

        #add time
        time_data = eval(schedule_entry[11])

        Timelist = self.ui.Timelist
        Timelist.setColumnCount(1)
        Timelist.setRowCount(0)

        for i in range(len(time_data)):
            Timelist.insertRow(Timelist.rowCount())
            c = QTableWidgetItem(str(time_data[i]))
            Timelist.setItem(Timelist.rowCount()-1,0,c)
        header = Timelist.horizontalHeader()      
        Timelist.setHorizontalHeaderLabels(['Time']) 
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.ui.Timelist.sortItems(0, QtCore.Qt.AscendingOrder)

    def saveall_clk(self):
        try:
            schedule_name = self.ui.schedule_name.text()
            share_link = self.ui.share_link.text()
            schedule_notes = self.ui.schedule_notes.text()
            Enable_cb = self.ui.Enable_cb.isChecked()
            randomlink_cb = self.ui.randomlink_cb.isChecked()
            randomtime_cb = self.ui.randomtime_cb.isChecked()
            ac = []
            for row in range(self.ui.Sharelist.rowCount()):
                ac.append([])
                for column in range(self.ui.Sharelist.columnCount()):
                    ac[row].append(str(self.ui.Sharelist.item(row, column).text()))

            comments = []
            for row in range(self.ui.CommentList.rowCount()):
                comments.append(str(self.ui.CommentList.item(row, 0).text()))

            links = []
            for row in range(self.ui.PastlinkList.rowCount()):
                links.append(str(self.ui.PastlinkList.item(row, 0).text()))

            Times = []
            for row in range(self.ui.Timelist.rowCount()):
                Times.append(str(self.ui.Timelist.item(row, 0).text()))

            if ac == []:
                msg = QMessageBox()
                msg.setText("Account list has nothing, are you serious???")
                msg.exec()
                sys.exit()

            elif comments == []:
                msg = QMessageBox()
                msg.setText("Dun be lazy, at least should have 1 comment")
                msg.exec()
                sys.exit()

            elif randomlink_cb == True and links == []:
                msg = QMessageBox()
                msg.setText("You have turned on Random Past Link Mode but there hasn't any valid share link. Please fix.")
                msg.exec()
                sys.exit()

            elif randomtime_cb == True and Times == []:
                msg = QMessageBox()
                msg.setText("You have turned on Random Time Mode but there hasn't anything in the timelist. Please fix.")
                msg.exec()
                sys.exit()
            
            elif randomlink_cb == False:
                try:
                    if requests.get(share_link).status_code == 200:
                        pass
                except:
                    msg = QMessageBox()
                    msg.setText("You haven't turned on Random Past Link Mode and you haven't input a valid share link. Please fix.")
                    msg.exec()
                    sys.exit()

            Actions_spec = [schedule_name, share_link, schedule_notes, Enable_cb, randomlink_cb, randomtime_cb, ac, comments, links, Times]
            a = self.ui.label_12.text()
            if a == 'Schedule_id: None':
                Database().addschedule(username, Actions_spec)
            else:
                id = a.split(" ")
                Database().updateschedule(Actions_spec, id[1])
                
            self.hide()
            MainWindow.refresh_table_clk()
        except:
            pass
        
    def enable_tl(self):
        if self.ui.randomtime_cb.isChecked() == True:
            self.ui.Timelist.setEnabled(True)
        elif self.ui.randomtime_cb.isChecked() == False:
            self.ui.Timelist.setEnabled(False)

    def enable_pl(self):
        if self.ui.randomlink_cb.isChecked() == True:
            self.ui.PastlinkList.setEnabled(True)
        elif self.ui.randomlink_cb.isChecked() == False:
            self.ui.PastlinkList.setEnabled(False)

    def add_time(self):
        try:
            time = QInputDialog.getText(self, "Add Time", "Time")

            if int(time[0][0]) > 2 or int(time[0][0]) == 2 and int(time[0][1]) > 4:
                sys.exit()
            elif int(time[0][0]) < 3 and isinstance(int(time[0][1]),int) and time[0][2] == ":" and int(time[0][3]) < 7 and isinstance(int(time[0][4]),int):
                Timelist = self.ui.Timelist
                Timelist.setColumnCount(1)
                Timelist.insertRow(Timelist.rowCount())
                c = QTableWidgetItem(str(time[0]))
                Timelist.setItem(Timelist.rowCount()-1,0,c)
                header = Timelist.horizontalHeader()      
                Timelist.setHorizontalHeaderLabels(['Time']) 
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
                self.ui.Timelist.sortItems(0, QtCore.Qt.AscendingOrder)
            else:
                sys.exit()
        except:
                msg = QMessageBox()
                msg.setText("Time format wrong, should be xx:xx. Example: 00:00 to 23:59")
                msg.exec_()

    def remove_time(self):
        row = self.ui.Timelist.currentRow()
        self.ui.Timelist.removeRow(row)
        self.ui.Timelist.sortItems(0, QtCore.Qt.AscendingOrder)

    def add_link(self):
        try:
            link = QInputDialog.getText(self, "Add link", "link")
            request = requests.get(link[0])
            if request.status_code == 200:
                linklist = self.ui.PastlinkList
                linklist.setColumnCount(1)
                linklist.insertRow(linklist.rowCount())
                c = QTableWidgetItem(str(link[0]))
                linklist.setItem(linklist.rowCount()-1,0,c)
                header = linklist.horizontalHeader()      
                linklist.setHorizontalHeaderLabels(['Links']) 
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
                self.ui.PastlinkList.sortItems(0, QtCore.Qt.AscendingOrder)
            else:
                sys.exit()
        except:
            msg = QMessageBox()
            msg.setText("Weblink incorrect")
            msg.exec_()

    def remove_link(self):
        row = self.ui.PastlinkList.currentRow()
        self.ui.PastlinkList.removeRow(row)
        self.ui.PastlinkList.sortItems(0, QtCore.Qt.AscendingOrder)

    def add_comment(self):
        Comment = QInputDialog.getText(self, "Add Comment", "Comment")
        CommentList = self.ui.CommentList
        CommentList.setColumnCount(1)
        CommentList.insertRow(CommentList.rowCount())
        c = QTableWidgetItem(str(Comment[0]))
        CommentList.setItem(CommentList.rowCount()-1,0,c)
        header = CommentList.horizontalHeader()      
        CommentList.setHorizontalHeaderLabels(['Comments']) 
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.ui.CommentList.sortItems(0, QtCore.Qt.AscendingOrder)

    def remove_comment(self):
        row = self.ui.CommentList.currentRow()
        self.ui.CommentList.removeRow(row)
        self.ui.CommentList.sortItems(0, QtCore.Qt.AscendingOrder)

    def remove_ac(self):
        row = self.ui.Sharelist.currentRow()
        self.ui.Sharelist.removeRow(row)
        self.ui.Sharelist.sortItems(2, QtCore.Qt.AscendingOrder)

    def add_ac(self):
        try:
            name = self.ui.ShareUsername_comboBox.currentText()
            ACID = self.get_ACID(name)

            hour = str(self.ui.timeEdit.time().hour())
            minute = str(self.ui.timeEdit.time().minute())
            if int(hour) < 10:
                hour = "0" + str(hour)
            if int(minute) < 10:
                minute = "0" + str(minute)

            SelectedGroup_table = self.ui.SelectedGroup_table
            b = SelectedGroup_table.rowCount()
            selected_group = []
            if b > 0:
                for i in range(b):
                    selected_group.append(SelectedGroup_table.item(i,0).text())
            
            if selected_group == []:
                sys.exit()

            Group_table = self.ui.Sharelist
            Group_table.setColumnCount(5)
            
            a = [name, ACID, hour + ":" + minute, str(len(selected_group)), str(selected_group)]
            Group_table.insertRow(Group_table.rowCount())
            for i in range(len(a)):
                c = QTableWidgetItem(str(a[i]))
                Group_table.setItem(Group_table.rowCount()-1,i,c)
            header = Group_table.horizontalHeader()      
            Group_table.setHorizontalHeaderLabels(['Name/Group_type', 'ACID', 'Time', 'Group Count', 'Groups']) 
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

            Group_table.sortItems(2, QtCore.Qt.AscendingOrder)
        except:
            msg = QMessageBox()
            msg.setText("You haven't select any groups to the selected group list.")
            msg.exec_()

    def updateGL_combo(self):
        Group_table = self.ui.Group_table
        Group_table.setColumnCount(1)
        Group_table.setRowCount(0)

        SelectedGroup_table = self.ui.SelectedGroup_table
        SelectedGroup_table.setColumnCount(1)
        SelectedGroup_table.setRowCount(0)

        name = self.ui.ShareUsername_comboBox.currentText()
        ACID = self.get_ACID(name)

        GL = Database().get_Group(ACID)

        for i in range(1, len(GL)):
            if GL[i] == "END":
                break
            else:
                a = str(GL[i])
                c = QTableWidgetItem(a)
                Group_table.insertRow(Group_table.rowCount())
                Group_table.setItem(i-1,0,c)
        header = Group_table.horizontalHeader()       
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        Group_table.sortItems(0, QtCore.Qt.AscendingOrder)

        this_moment = QtCore.QTime.currentTime()
        self.ui.timeEdit.setTime(this_moment)

    def get_ACID(self, name2):
        name = []
        for i in name2:
            if i == '/':
                name.pop()
                break
            else:
                name.append(i)

        for i in userlist:
            if "".join(name) == i[1]:
                global ACID
                ACID = i[0]
                break

        return(ACID)

    def load_info(self):
        global userlist
        userlist = Database().get_ACNames(username)

        for i in userlist:
            a = i[1] + " / " + i[2]
            self.ui.ShareUsername_comboBox.addItem(a)
        
        this_moment = QtCore.QTime.currentTime()
        self.ui.timeEdit.setTime(this_moment)
        ShareEditor.enable_tl()
        ShareEditor.enable_pl()
            
def encode(string):
    return string.encode('utf-8')

def encrypt(code):
    string = encode(str(code))
    return hashlib.md5(string).hexdigest()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = GUI_MainWindow()    #Therefore, in this case, MainWindow is the instance - 'self'
    Login = GUI_login()
    Signup = GUI_Signup()
    ShareEditor = GUI_ShareEditor()
    Login.show()
    sys.exit(app.exec_()) #It means, when press the close button of MainWindow Page = the end of the whole program

    #app = QtWidgets.QApplication(sys.argv)
    #Login = GUI_login()  #Therefore, in this case, Login is the instance - 'self'
    #Login.show()
    #sys.exit(app.exec_()) #It means, when press the close button of Login Page = the end of the whole program. When use this, after login, the page will hide and consider as the dialog is closed. So the whole program will end.