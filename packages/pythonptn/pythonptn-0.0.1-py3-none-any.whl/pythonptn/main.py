import time
# -*- coding: utf-8 -*-
#help(time.sleep)

class Loongtu:
    def __init__(self):
        self.name = "Prayuth"
        self.lastname = "Chanocha"
        self.nickname = "ลุงตู่"
    
    def WhoIAm(self):
        '''
        This function will print the name, lastname, and nickname of Loongtu.
        '''
        
        print("My Name is : {}" .format(self.name))
        print("My Lastname is : {}" .format(self.lastname))
        print("My Nickname is : {}" .format(self.nickname))
        
    def email_1(self):
        return "Email : {}.{}@gmail.com".format(self.name.lower(), self.lastname.lower())
    
    @property
    def email_2(self):
        return "Email : {}.{}@gmail.com".format(self.name.lower(), self.lastname.lower())
    
    def thainame(self):
        print("ประยุทธ์ จันทร์โอชา")
        return "ประยุทธ์ จันทร์โอชา"
    
    def __str__(self):
        return 'นี่..คือ..คลาสของลุงตู่'

if __name__ == "__main__":

    myloong = Loongtu()
    print(help(myloong.WhoIAm))


    print(myloong.name)
    print(myloong.lastname)
    print(myloong.nickname)
    print("==========================")
    #########################################
    mypaa = Loongtu()

    mypaa.name = "Warunee"
    mypaa.lastname = "Somsee"
    mypaa.nickname = "ป้าสมศรี"
    print(mypaa.name)
    print(mypaa.lastname)
    print(mypaa.nickname)
    print("==========================")
    #########################################
    myloong.WhoIAm()
    print("\n")
    print("==========================")
    #########################################
    mypaa.WhoIAm()
    print("==========================")
    #########################################
    print(myloong.email_1())
    print("==========================")
    #########################################
    print(myloong.email_2)
    print("==========================")
    #########################################
    print(myloong)
    print("==========================")
    #########################################
    myloong.thainame()
    print("==========================")
    #print(dir(myloong))