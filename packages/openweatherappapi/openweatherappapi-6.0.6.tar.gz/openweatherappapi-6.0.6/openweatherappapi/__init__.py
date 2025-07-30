from tkinter import *
import tkinter as tk
from tkinter import BOTTOM
import pytz
import requests
from datetime import datetime
from geopy.geocoders import Nominatim
from PIL import ImageTk, Image
from timezonefinder import TimezoneFinder
import tkinter.messagebox as messagebox
import pystray
import PIL.Image
import sys
file=f"{sys.executable.replace('python.exe','').replace('pythonw.exe','')}\Lib\site-packages\openweatherappapi"
class weatherApp:

    def run(self, api_key):

        root=Tk()
        root.title("Weather App By Ali")
        root.geometry("750x470+300+200")
        root.resizable(False,False)
        root.config(bg="#202731")
        import threading

        def getweather():
            city = textfield.get()
            geolocator = Nominatim(user_agent="newgeoapiExercises")
            try:
                location = geolocator.geocode(city)
                if location is None:
                    timezone.config(text="Location not found")
                    return
                obj = TimezoneFinder()
                result = obj.timezone_at(lat=location.latitude, lng=location.longitude)
                timezone.config(text=result)
                long_lat.config(text=f'{round(location.latitude, 4)}°N {round(location.longitude, 4)}°E')
                home = pytz.timezone(result)
                local_time = datetime.now(home)
                current_time = local_time.strftime("%H:%M:%S")
                clock.config(text=current_time)
                api_key = api_key 
                api_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
                response = requests.get(api_url).json()
                current = response['list'][0]
                temp = current['main']['temp']
                humidity = current['main']['humidity']
                pressure = current['main']['pressure']
                wind_speed = current['wind']['speed']
                description = current['weather'][0]['description']
                t.config(text=f"{temp}°C")
                h.config(text=f"{humidity}%")
                p.config(text=f"{pressure}hPa")
                w.config(text=f"{wind_speed}m/s")
                d.config(text=f"{description}")
                daily_data = []
                for i in response['list']:
                    if "12:00:00" in i['dt_txt']:
                        daily_data.append(i)
                icons = []
                temps = []
                for i in range(5):
                    if i >= len(daily_data):
                        break
                    icon_code = daily_data[i]['weather'][0]['icon']
                    img = Image.open(f"{file}\{icon_code}@2x.png")
                    icons.append(ImageTk.PhotoImage(img))
                    temps.append((daily_data[i]['main']['temp_max'], daily_data[i]['main']['feels_like']))
                day_widget = [
                    (firstimage, day1, day1temp),
                    (secondimage, day2, day2temp),
                    (thirdimage, day3, day3temp),
                    (fourthimage, day4, day4temp),
                    (fifthimage, day5, day5temp)
                ]
                from datetime import timedelta

                for i, (img_label, day_label, temp_label) in enumerate(day_widget):
                    if i >= len(icons):
                        break
                    img_label.config(image=icons[i])
                    img_label.image = icons[i]
                    temp_label.config(text=f"Day: {temps[i][0]}\nNight: {temps[i][1]}")
                    future_date = datetime.now() + timedelta(days=i)
                    day_label.config(text=future_date.strftime("%A"))

            except Exception:
                pass

            # Auto update every 10 minutes (600000 ms)
        import time
        def schedule_update():
            while True:
                time.sleep(0.5)
                getweather()
        image = PIL.Image.open(f"{file}\logo.png")



        run=threading.Thread(target=schedule_update)
        run.start()
        def on_closing():
            global run, getweather, schedule_update,theard_close
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                icon.stop()
                
                del getweather
                del theard_close
                del schedule_update
                del run
                
                root.quit()
        import webbrowser
        def on_clicked(icon, item):
            if str(item) == 'О себя':
                messagebox.showinfo("О себя", "Telegram: https://t.me/ALIKUSHBAEVYT\nDiscord: https://discord.gg/nEYmfYQWcw\nSites: https://alikushbaev.github.io/Sites/\nВладелиц: Ali Kushbaev")
            elif str(item) == 'Выход':
                on_closing()
            elif str(item) == 'Другие Работы ;)':
                webbrowser.open("https://alikushbaev.github.io/Sites/")

        icon = pystray.Icon('Wether App By Ali', image, menu=pystray.Menu(
            pystray.MenuItem('О себя', on_clicked),
            pystray.MenuItem('Выход', on_clicked),
            pystray.MenuItem('Другие Работы ;)', on_clicked)

        ))
        def theard_close():
            icon.run()
        thread1 = threading.Thread(target=theard_close)
        thread1.start()
        root.protocol("WM_DELETE_WINDOW", on_closing)
        image_icon=PhotoImage(file=f"{file}\logo.png")
        root.iconphoto(False,image_icon)
        round_box=PhotoImage(file=f"{file}\Rounded Rectangle 1.png")
        Label(root,image=round_box,bg="#202731").place(x=30,y=60)
        Label(root, text= "by Ali_Dev", bg='#202731', fg='#ffffff').place(x=670, y=60)
        label1=Label (root, text="Temperature", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        label1.place(x=50,y=120)

        label2=Label (root, text="Humidity", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        label2.place(x=50,y=140)

        label3=Label (root, text="Pressure", font=("Helvetica", 11), fg="#323661", bg="#aad1c8") 
        label3.place(x=50,y=160)

        label4=Label (root, text="Wind Speed", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        label4.place(x=50,y=180)

        label5=Label (root, text="Description", font=("Helvetica", 11), fg="#323661",bg="#aad1c8") 
        label5.place(x=50,y=200)
        Search_image = PhotoImage(file=f"{file}\Rounded Rectangle 3.png")

        myimage = Label(root, image=Search_image, bg="#202731")

        myimage.place(x=270, y=122)

        weat_image = PhotoImage(file=f"{file}\Layer 7.png")

        weatherimage = Label(root, image=weat_image, bg="#333c4c")

        weatherimage.place(x=290, y=127)

        textfield = tk.Entry(root, justify="center", width=15, font=("poppins", 25, "bold"), bg="#333c4c", border=0, fg="white")

        textfield.place(x=370, y=130)

        Search_icon = PhotoImage(file=f"{file}\Layer 6.png")
        # on click bg 




        myimage_icon = Button(root, image=Search_icon, borderwidth=0, cursor="hand2", bg="#333c4c", highlightcolor="#333c4c", activebackground="#333c4c", command=getweather)

        myimage_icon.place(x=640, y=135)
        #Bottom boX

        frame=Frame (root, width=900,height=180, bg="#7094d4")

        frame.pack(side=BOTTOM)

        #boxes
        firstbox = PhotoImage(file=f"{file}\Rounded Rectangle 2.png")

        secondbox = PhotoImage(file=f"{file}\Rounded Rectangle 2 copy.png")
        secondbox = PhotoImage(file=f"{file}\Rounded Rectangle 2 copy.png")

        Label (frame, image=firstbox,bg="#7094d4").place(x=30,y=20)

        Label (frame, image=secondbox, bg="#7094d4").place(x=300,y=30)

        Label (frame, image=secondbox, bg="#7094d4").place(x=400,y=30)

        Label (frame, image=secondbox, bg="#7094d4").place(x=500,y=30)

        Label (frame, image=secondbox, bg="#7094d4").place(x=600,y=30)
        #clock

        clock=Label (root, font=("Helvetica", 20), bg="#202731",fg="white")

        clock.place(x=30,y=20)

        #timezone

        timezone=Label(root, font=("Helvetica", 20), bg="#202731", fg="white")

        timezone.place(x=500,y=20)

        long_lat=Label(root, font=("Helvetica", 10), bg="#202731", fg="white")

        long_lat.place (x=500,y=50)

        #thpwd

        t=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        t.place(x=150,y=120)
        h=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        h.place(x=150,y=140)
        p=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        p.place(x=150,y=160)
        w=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        w.place(x=150,y=180)
        d=Label(root, font=("Helvetica", 9), bg="#333c4c", fg="white")
        d.place(x=150,y=200)
        # #
        firstframe = Frame(root, width=230, height=132, bg="#323661")
        firstframe.place(x=35, y=315)

        firstimage = Label(firstframe, bg="#323661")
        firstimage.place(x=0, y=15)
        day1 = Label(firstframe, font=("arial 20"), bg="#323661", fg="white")
        day1.place(x=1000, y=5)
        day1temp = Label(firstframe, font=("arial 15 bold"), bg="#323661", fg="white")
        day1temp.place(x=100, y=50)
        image_label = Label(firstframe, bg="#323661")
        image_label.place(x=0, y=15)
        city = Label(firstframe, font=("arial 20"), bg="#323661", fg="white")
        city.place(x=0, y=45)

        daytime = Label(firstframe, font=("arial 15 bold"), bg="#323661", fg="white")
        daytime.place(x=0, y=50)

        secondframe = Frame(root, width=70, height=115, bg="#eefefa")
        secondframe.place(x=305, y=325)

        secondimage = Label(secondframe, bg="#eefefa")
        secondimage.place(x=7, y=10)
        day2=Label(secondframe, bg="#eefefa", fg="#000")
        day2.place(x=10, y=5)
        day2temp = Label(secondframe, bg="#eefefa", fg="#000")
        day2temp.place(x=2, y=70)
        thirdframe = Frame(root, width=70, height=115, bg="#eefefa")
        thirdframe.place(x=405, y=325)

        thirdimage = Label(thirdframe, bg="#eefefa")
        thirdimage.place(x=7, y=20)
        day3 = Label(thirdframe, bg="#eefefa", fg="#000")
        day3.place(x=10, y=5)
        day3temp = Label(thirdframe, bg="#eefefa", fg="#000")
        day3temp.place(x=2, y=70)
        fourthframe = Frame(root, width=70, height=115, bg="#eefefa")
        fourthframe.place(x=505, y=325)

        fourthimage = Label(fourthframe, bg="#eefefa")
        fourthimage.place(x=7, y=20)

        day4 = Label(fourthframe, bg="#eefefa", fg="#000")
        day4.place(x=10, y=5)

        day4temp = Label(fourthframe, bg="#eefefa", fg="#000")
        day4temp.place(x=2, y=70)
        fifthframe = Frame(root, width=70, height=115, bg="#eefefa")
        fifthframe.place(x=605, y=325)

        fifthimage = Label(fifthframe, bg="#eefefa")
        fifthimage.place(x=7, y=20)

        day5 = Label(fifthframe, bg="#eefefa", fg="#000")
        day5.place(x=10, y=5)

        day5temp = Label(fifthframe, bg="#eefefa", fg="#000")
        day5temp.place(x=2, y=70)
        root.mainloop()
