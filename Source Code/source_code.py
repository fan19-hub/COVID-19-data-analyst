from tkinter import *
from tkinter import messagebox,filedialog,ttk
# import the psycopg2 database adapter for PostgreSQL
from psycopg2 import connect, sql
from PIL import Image,ImageTk
import pandas as pd
import matplotlib.pyplot as plt
# set the DB name, table, and table data to 'None'
db_name = "final" #need to modify based on the name of your database

#change these globals (user name and user password) to match your settings
user_name = "postgres" #the username for accessing your postgreSQL
user_pass = "123qwe" #the password for accessing your postgreSQL
CASE=''
COUNTRY=['','','']
STATE=['','','']
QUERY=0
DATE=''


def connect_postgres(db):
    '''Connect to PostgreSQL ; input: the database name  ;  return: connection object'''
    print ("\nPlease wait, connecting......")
    try:
        conn = connect (
            dbname = db,
            user = user_name,
            host = "localhost",
            password = user_pass
        )
    except Exception as err:
        print("Connection Failed")
        print ("PostgreSQL Connect() ERROR:", err)
        conn = None

    # return the connection object
    return conn


def return_records(conn,n):
    if conn==None:
        return None
    if QUERY==1:
        Name=COUNTRY[n]
        SQLquery1="SELECT Date, "+CASE+" FROM countries WHERE Country='"+Name+"';"
        print('Sending: \"',SQLquery1,' \" to PostgreSQL')
    elif QUERY==2:
        Name=STATE[n]
        SQLquery1="SELECT Date, "+CASE+" FROM states WHERE province_or_state='"+Name+"';"
        print('Sending: \"',SQLquery1,' \" to PostgreSQL')
    elif QUERY==3:
        Name=DATE
        SQLquery1="SELECT Date, "+CASE+", Country FROM countries WHERE Country=(SELECT Country  FROM countries WHERE date='"+DATE+"'  ORDER BY confirmed DESC LIMIT 1);"
        print('Sending: \"',SQLquery1,' \" to PostgreSQL')
    # instantiate a new cursor object
    cursor = conn.cursor()
    # (use sql.SQL() to prevent SQL injection attack)
    sql_object = sql.SQL(
        # pass SQL statement to sql.SQL() method
        SQLquery1
    )
    try:
        # use the execute() method to put table data into cursor obj
        cursor.execute( sql_object )    #commit
        # use the fetchall() method to return a list of all the data
        result1 = cursor.fetchall()#fetch 
    except Exception as err:
        # print psycopg2 error and set table data to None
        print ("PostgreSQL psycopg2 cursor.execute() ERROR:", err)
        result1= None
    return result1



#app definition 
class application(Frame):
    '''Application definition is here'''
    global CASE

    def __init__(self,master):
        super(application,self).__init__(master)
        self.grid()             #initialize the grid
        self.create_widgets()   #add the widgets
        messagebox.showinfo(title="Covid-19 Data Analyst",message="Welcome!")

    def get_image(self,filename, w,h):
        im=Image.open(filename).resize((w,h))
        return ImageTk.PhotoImage(im)

    def handle_data(self,data):
        print("The data:")
        if QUERY<=2:
            data = pd.DataFrame(list(data), columns=['date','number'])
        elif QUERY==3:
            data = pd.DataFrame(list(data), columns=['date','number','countries'])
            COUNTRY[0]=str(data.iat[2,2])
            data=data.loc[:,['date','number']]
        print(COUNTRY[0])
        print(data)
        self.data_box.insert("insert",COUNTRY[0]) 
        self.data_box.insert("insert", data.applymap(str))
        return data

    
    def display(self,mode):
        '''display the infomation based on the CASE COUNTRY STATE that you choose'''
        global CASE
        global COUNTRY
        if CASE==None:
            messagebox.showerror(title="Invalid input",message="Please select Confrimed/Recovered/Deaths, and try again")
            return None
        elif QUERY==0:
            messagebox.showerror(title="Invalid input",message="Please select the query, and try again")
            return None
        elif (COUNTRY[1]=='' and COUNTRY[2]=='' and STATE[1]=='' and STATE[2]=='') and (QUERY<=2):
            messagebox.showerror(title="Invalid input",message="Please select the country or state, and try again")
            return None

        CASE=['','Confirmed','Recovered','Deaths'][mode] #set variable CASE according to the mode
        try:
            self.output.delete(1.0, END) #display the infomation in the status bar
            self.output.insert("insert", "Please wait, connecting the PostgreSQL......\n")
            print("The button was clicked by the user")
            conn=connect_postgres(db_name) #build the connection
            if conn==None:                 #if the connection failed
                self.output.insert("insert", "Connection Failed") #display "connection failed" in the status bar
                return -1      #return -1 for failure
            elif QUERY<=2:
                data1=return_records(conn,1)  #get the data of the first area
                data2=return_records(conn,2)  #get the data of the second area
                self.output.delete(1.0, END)   
                self.output.insert("insert", "Data fetching succeeded!")#display successful information in the status bar
                D1=self.handle_data(data1)   #handle the data that we fetched back
                D2=self.handle_data(data2)
                '''The following are the ploting code'''
                x1=D1['date']
                x2=D2['date']

                y1=D1['number']
                y2=D2['number']
                if QUERY==1:
                    plt.plot(x1, y1,label=COUNTRY[1])
                    plt.plot(x2, y2,label=COUNTRY[2])
                    plt.xticks(rotation=45)
                    plt.title('Two Countries')
                elif QUERY==2:
                    plt.plot(x1, y1,label=STATE[1])
                    plt.plot(x2, y2,label=STATE[2])
                    plt.xticks(rotation=45)
                    plt.title('Two States')
                plt.xlabel('DATE')
                plt.ylabel('NUMBER')
                plt.legend()
                plt.show()
            elif  QUERY==3:
                data3=return_records(conn,0)
                self.output.delete(1.0, END)   
                self.output.insert("insert", "Data fetching succeeded!")#display successful information in the status bar
                D3=self.handle_data(data3)   #handle the data that we fetched back
                x3=D3['date']
                y3=D3['number']      
                plt.plot(x3, y3,label=COUNTRY[0])  
                plt.xticks(rotation=45) 
                plt.title('Max '+CASE+' case country by '+DATE+': '+COUNTRY[0]) 
                plt.legend()
                plt.show()  
        except Exception as err:
            print ("\tERROR:", err)
            self.output.delete(1.0, END)

    def open(self):
        '''This function is used to change the usename, userpass, dbname as the user want'''
        global screenheight
        global screenwidth
        #initialize the subwindow:top (with size 300x150)
        self.top = Toplevel()
        self.top.title('open the database')
        self.top.geometry('%dx%d+%d+%d'%(300,150,(screenwidth-300)/2,(screenheight-150)/2))
        #database name
        Label(self.top,text='Database name:').grid(row=0,column=0,sticky=E)                        
        self.e1=Entry(self.top,width=10)  #the input bar
        self.e1.grid(row=0,column=1,padx=1,pady=1) 
        #user name
        Label(self.top,text='User name:').grid(row=1,column=0,sticky=E)                        
        self.e2=Entry(self.top,width=10)  #the input bar
        self.e2.grid(row=1,column=1,padx=1,pady=1) 
        #password
        Label(self.top,text='Password:').grid(row=2,column=0,sticky=E)                        
        self.e3=Entry(self.top,width=10)  #the input bar
        self.e3.grid(row=2,column=1,padx=1,pady=1) 
        Button(self.top, text='Submit',command=self.commit).grid(row=3,column=1,sticky=E)
    def commit(self):
        '''commit the data from feature OPEN'''
        global db_name
        global user_name
        global user_pass
        db_name=self.e1.get() 
        user_name=self.e2.get() 
        user_pass=self.e3.get()
        self.top.destroy()

    def commit2(self):
        '''commit the data from the subwindow: input_date'''
        global DATE
        y=self.year.get()
        m=self.month.get()
        d=self.day.get()
        if m=='' or int(m)>12 or int(m)<1:
            messagebox.showerror(title='Error',message="Invalid month")
        elif y=='' or y!='2020':
            messagebox.showerror(title='Error',message="This year is not included in the database ")
        elif d=='' or (m=='2' and (int(d)>29 or int(d)<1)) or (m in ['3','5','7','8','10'] and (int(d)>31 or int(d)<1)) or (m=='1' and (int(d)>31 or int(d)<22)):
            messagebox.showerror(title='Error',message="Invalid day")
        elif int(d)>30 or int(d)<1:
            messagebox.showerror(title='Error',message="Invalid day")
        else:
            DATE=y+'-'+ m +'-'+d
            self.input_date.destroy()


    def store(self):   
        '''Used to export our Data output text inside the box'''                         
        contents = self.data_box.get(1.0, "end")    
        with filedialog.asksaveasfile(filetypes=[('TXT','.txt')]) as f:
            f.write(contents)
        print("Save successfully") 
        self.output.insert("insert", "Data successfully saved")                      
        messagebox.askquestion(title='Notice', message='Save successfully')

    def help(self):
        txt="This application is used to access and analyze the database of COVID-19\n(c)2020 Lingyuan Ye. All rights reserved."
        messagebox.showinfo(title='About',message=txt)
    def quitt(self):
        q= messagebox.askquestion(title='Notice', message='Are you sure to quit?')
        if(q=='yes'):
            root.quit()
    def select(self,event):
        global COUNTRY
        global STATE
        global QUERY
        S1=self.comb1.get()#get the data from the combobox 
        S2=self.comb2.get()  
        if(S1!=S2): 
            if(QUERY==1): 
                print('Selected1: ',S1)  
                print('Selected2: ',S2)
                COUNTRY[1]=S1
                COUNTRY[2]=S2
            if(QUERY==2): 
                print('Selected1: ',S1)  
                print('Selected2: ',S2)
                STATE[1]=S1
                STATE[2]=S2
        else:# if the  user didn't select the same area, show warning
            messagebox.showwarning(title='Notice', message='You have selected the same place, please select again')      
    def query(self,q):
        global QUERY
        QUERY=q
        def get_list(filename):
            '''this function is used to read the countries and states file to get the name list for creating the comobox'''
            l=[]                            #initialize the returning list
            with open(filename,'r') as f:   #open the file
                name=f.readline()           #read line by line
                name=name.strip('\n')
                while(name!=''):          
                    name=f.readline()
                    name=name.strip('\n')
                    l.append(name)          #update the list
            return l                        #return the list
        if(QUERY==1):
            countryfile="countries.txt"
            self.comb1["value"] =get_list(countryfile)   # set the value of the combo box
            self.comb2["value"] =get_list(countryfile)  
            self.comb2.bind("<<ComboboxSelected>>", self.select)     #bind theh combo box to the function
        elif(QUERY==2):
            statefile="states.txt"
            self.comb1["value"] =get_list(statefile)   # set the value of the combo box
            self.comb2["value"] =get_list(statefile)   
            self.comb2.bind("<<ComboboxSelected>>", self.select)     #bind theh combo box to the function
        elif(QUERY==3):
            col=0
            global screenheight
            global screenwidth
            #initialize the subwindow:top (with size 300x150)
            self.input_date = Toplevel()
            self.input_date.title('open the database')
            self.input_date.geometry('%dx%d+%d+%d'%(355,60,(screenwidth-300)/2,(screenheight-150)/2))

            Label(self.input_date,text='Month:').grid(row=0,column=col)
            col+=1                        
            self.month=Entry(self.input_date,width=10)  #the input bar
            self.month.grid(row=0,column=col)
            col+=1 

            Label(self.input_date,text='Day:').grid(row=0,column=col) 
            col+=1                       
            self.day=Entry(self.input_date,width=10)  #the input bar
            self.day.grid(row=0,column=col) 
            col+=1
            
            Label(self.input_date,text='Year:').grid(row=0,column=col) 
            col+=1                       
            self.year=Entry(self.input_date,width=10)  #the input bar
            self.year.grid(row=0,column=col)
            Button(self.input_date, text='Submit',command=self.commit2).grid(row=1,column=col)
            col+=1 
            
                
    def create_widgets(self):
        '''widget creatation and positioning control'''
        line=0        
        try:
            #Main Label
            self.photo=self.get_image('label.png',300,80)     
            Label(self,text="",borderwidth=1,image=self.photo,compound =CENTER).grid(row=line,column=1,columnspan=2 ,pady=10) #locate the widget(label)            
            line+=1


            #Label+Combobox
            Label(self,text="Select",bg='black',fg='white',font=('Times New Roman',15)).grid(row=line,column=0,sticky=W,pady=10)
            Label(self,text="areas to compare:",bg='black',fg='white',font=('Times New Roman',15)).grid(row=line,column=1,sticky=W,pady=5)#Combobox label
            line+=1

            Label(self,text="First:",
                        compound = CENTER,
                        font=("Times New Roman",15),
                        bg='black',
                        fg = "white").grid(row=line,column=0,sticky=E) #locate the widget(label)
            self.comb1 = ttk.Combobox(self)     #Create Combobox1
            self.comb1.grid(row=line,column=1,sticky=W)
            line+=1

            Label(self,text="Next:",
                        compound = CENTER,
                        font=("Times New Roman",15),
                        bg='black',
                        fg = "white").grid(row=line,column=0,sticky=E) #locate the widget(label)
            self.comb2 = ttk.Combobox(self)     #Create Combobox2
            self.comb2.grid(row=line,column=1,sticky=W)
            line+=1
          

            #Set up the buttons that represents the confirmed CASE mode, death CASE mode, etc
            Label(self,text="Select",bg='black',fg='white',font=('Times New Roman',15)).grid(row=line,column=0,sticky=W)
            Label(self,text="case type:",bg='black',fg='white',font=('Times New Roman',15)).grid(row=line,column=1,sticky=W)
            line+=1
            self.buttonimage1=self.get_image('1.png',40,40)
            self.buttonimage2=self.get_image('2.png',40,40)
            self.buttonimage3=self.get_image('3.png',40,40)
            self.check1=Button(self,text = "mode1",
                                    command=lambda:self.display(1),
                                    image=self.buttonimage1,
                                    activebackground='red',
                                    bg='black')          #mode1,confirmed CASE
            self.check2= Button(self,text = "mode2",
                                    command=lambda:self.display(2),
                                    image=self.buttonimage2,
                                    activebackground='red',
                                    bg='black')          #mode2,confirmed CASE
            self.check3= Button(self,text = "mode3",
                                    command=lambda:self.display(3),
                                    image=self.buttonimage3,
                                    activebackground='red',
                                    bg='black')          #mode3,confirmed CASE
            #Button
            self.check1.grid(row=line,sticky=E,pady=4) 
            line+=1
            self.check2.grid(row=line,sticky=E,pady=4)
            line+=1
            self.check3.grid(row=line,sticky=E,pady=4)


            Label(self,text="Confirmed",
                        compound = CENTER,
                        font=("Times New Roman",20),
                        bg='black',
                        fg = "white").grid(row=line-2,column=1 ,sticky=W) #locate the widget(label)#创建控件并设置背景图              

            Label(self,text="Recovered",
                        compound = CENTER,
                        font=("Times New Roman",20),
                        bg='black',
                        fg = "white").grid(row=line-1,column=1 ,sticky=W) #locate the widget(label)#创建控件并设置背景图               

            Label(self,text="Deaths",
                        compound = CENTER,
                        font=("Times New Roman",20),
                        bg='black',
                        fg = "white").grid(row=line,column=1 ,sticky=W) #locate the widget(label)#创建控件并设置背景图              
            line+=1

            #data_box
            Label(self,text="Data Output:",bg='black',fg='white',font=('Times New Roman',15)).grid(row=1,column=2,sticky=W)
            self.data_box=Text(self,bg='RoyalBlue',fg='white',width=30,height=15)
            self.data_box.grid(row=2,column=2,columnspan=2,rowspan=4,sticky=W)     
        except Exception as err: #in CASE the pictures is missing, we can still use the app without flashing back
            print ("ERROR:", err)
            print("If you didn't see the widgets, it is most likely you choose the wrong working directory to run the python code, or the images are lost")
        #The output bar
        Label(self,text="Status",bg='black',fg='white',font=('Times New Roman',15)).grid(row=line,column=0,sticky=E)
        Label(self,text="Bar:",bg='black',fg='white',font=('Times New Roman',15)).grid(row=line,column=1,sticky=W)
        line+=1
        self.output=Text(self,width=60,height=2,bg='Gainsboro')
        self.output.grid(row=line,column=1,columnspan=2,sticky=W) 
        line+=1


        #Set the menu bar
        appmenu = Menu(self, tearoff=0)
        appmenu.add_command(label="Open",command=self.open)
        appmenu.add_separator()
        appmenu.add_command(label="Save",command=self.store)
        appmenu.add_separator()
        appmenu.add_command(label="Setting")#None

        choosemenu = Menu(self, tearoff=0)
        choosemenu.add_command(label="Compare countries",command=lambda:self.query(1))
        choosemenu.add_separator()
        choosemenu.add_command(label="Compare states",command=lambda:self.query(2))
        choosemenu.add_separator()
        choosemenu.add_command(label="Max case country",command=lambda:self.query(3))


        menubar = Menu(root)
        menubar.add_cascade(label="Start", menu=appmenu) # First add a menu in the main menu, binding with the previously created menu.
        menubar.add_cascade(label="Query",menu=choosemenu)
        menubar.add_command(label="About",command=self.help)
        menubar.add_command(label="Exit", command=self.quitt)
        root.config(menu=menubar)


if __name__ == "__main__":  
    root=Tk()                   #The creation of a root window object, called the root
    root.title("COVID-19 Data Analyst")       #set title, default: tk
    #Access to the screen size to calculate the layout parameters, make the window in the middle of screen
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    width =520
    height =580
    root.geometry('%dx%d+%d+%d'%(width,height,(screenwidth-width)/2,(screenheight-height)/2))
    app=application(root)       #Create a application instance called app
    app['bg']='black'
    root['bg'] ='black'
    app.mainloop()              
