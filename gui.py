import PySimpleGUI as sg
from PIL import Image

sg.theme('DarkTeal')
sg.set_options(font=("Arial Bold", 14))

global b
b=18

plantData = [[sg.Text(('Temperature: ' + str(b) + "C"), key='temp', text_color = 'white')], 
             [sg.Text(('Humidity: ' + str(b) + "%"), key='humidity', text_color = 'white')],
             [sg.Text(('Soil moisture: ' + str(b) + "%"), key='moisture',text_color = 'white')],
]

phone1 = sg.Text('Please enter your phone number: ', font=('Arial Bold', 15), key='-OUT-', expand_x = True, text_color = 'white')
phone2 = sg.Input('', enable_events=True, key='-INPUT-', expand_x=False, font=('Arial Bold', 15), text_color='white')
Enter = sg.Button('Enter', key='-Enter-', font=('Arial Bold', 15))

plantframe = sg.Frame('Plant Data', plantData,)


layout = [[plantframe],
        [phone1], [phone2], [Enter]
]

window = sg.Window("Plant Data", layout, resizable=True)

event, values = window.read(timeout = 10)
while True:
    if event == sg.WIN_CLOSED:
        break
    print(event, values)
    if event == '-Enter-':
        if (values['-INPUT-']).isdigit() == False:
            sg.popup("Please enter only digits.")
            window['-INPUT-'].update(values['-INPUT-'])
        else:
            number = int(values['-INPUT-'])
            print(number)
            sg.popup("Phone number successfully registered!")
            window['-INPUT-'].update(values['-INPUT-'][:-100])
    event, values = window.read(timeout = 10)
    if event == sg.TIMEOUT_KEY:
        b+=0.1
        b = round(b,1)
        print("Timeout")
        window["temp"].update("Temperature: "+str(b)+"C")