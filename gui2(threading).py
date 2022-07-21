from tkinter import *
from pythonosc.udp_client import SimpleUDPClient
import numpy as np
import time, random
import threading

# pip install tk
# pip install python-osc
# pip install numpy


gui = Tk()
ySpace = 3
xSpace = 0
expression = ""
current = ""
first = ""
last = ""
play = False
loop = False
bWidth = 10
bHeight = 2
copyList = np.array([0])
masterList = np.array([0])
tapTime = 1
flashTime = .1
flashLoop = True
times = np.array([0])
lastTime = 0


#OSC STUFF
targetIP = "192.168.10.62"
TargetPort = 8000
client = SimpleUDPClient(targetIP, TargetPort)

def createMlist():
    global first, last, copyList, masterList
    masterList = np.array([0])

    for x in range((last - first)+1):
        masterList = np.append(masterList, (first+x))
    masterList = np.delete(masterList, 0)

def macroLoop():
    global copyList, masterList, loop
    if(loop == True):
        i = random.randint(0, copyList.size-1)
        lastNum = copyList[i]

        command = "/eos/macro/"+str(lastNum)+"/fire"
        client.send_message(command, 1)

        copyList = np.delete(copyList, i)
        if(copyList.size == 0):
            copyList = masterList
            print(str(lastNum) + " - " +str(first))
            copyList = np.delete(copyList, lastNum-first)






#GUI STUFF
def press(num):
    global expression
    expression = expression + str(num)
    equation.set(expression)

def clear():
    global expression, first, last, loop

    loop = False
    bplay['text'] = "play"

    if(expression == ""):
        if(last != ""):
            last = ""
            text.delete('1.0', END)
            text.insert(INSERT, "   Macro "+str(first)+" thru...")
        elif(last == "" and first != ""):
            first = ""
            text.delete('1.0', END)
            text.insert(INSERT, "   Add macro range")
    else:
        expression = ""
        equation.set("")
    
    gui.update()

def enter():
    global expression, first, last
    
    if(first == ""):
        first = int(expression)
        text.delete('1.0', END)
        text.insert(INSERT, "   Macro "+str(first)+" thru...")
        expression = ""
        equation.set("")
    elif(last == ""):
        last = int(expression)
        if(last > first):
            text.delete('1.0', END)
            text.insert(INSERT, "   Looping Macro "+str(first)+" thru "+str(last))
            expression = ""
            equation.set("")
            createMlist()
        else:
            last = ""
            expression = "INVALID RANGE"
            equation.set("INVALID RANGE")

    else: 
        text.delete('1.0', END)
        text.insert(INSERT, "Error: method \"enter\" --- press clear twice to reset")
        expression = ""
        equation.set("")
    
    gui.update

def lockOut():
    b0.grid_forget()
    b1.grid_forget()
    b2.grid_forget()
    b3.grid_forget()
    b4.grid_forget()
    b5.grid_forget()
    b6.grid_forget()
    b7.grid_forget()
    b8.grid_forget()
    b9.grid_forget()
    bEnter.grid_forget()
    bClear.grid_forget()
    bLock.grid_forget()
    bTap.grid_forget()
    expression_field.grid_forget()

    bUnLock.grid(row=2, column=0, pady = 0, padx = 5)
    bTap2.grid(row=3, column=1, pady = 10, padx = 25)
    bplay.grid(row=2, column=3, pady = ySpace, padx = 0)

def unlock():
    bUnLock.grid_forget()
    bTap2.grid_forget()
    text.grid_forget()
    bplay.grid_forget()
    expression_field.grid(columnspan = 10, ipadx=2, ipady=0)
    text.grid(columnspan=200, ipadx=150, ipady=0)
    b0.grid(row=5, column=1, pady = ySpace, padx = xSpace)
    b1.grid(row=4, column=0, pady = ySpace, padx = xSpace)
    b2.grid(row=4, column=1, pady = ySpace, padx = xSpace)
    b3.grid(row=4, column=2, pady = ySpace, padx = xSpace)
    b4.grid(row=3, column=0, pady = ySpace, padx = xSpace)
    b5.grid(row=3, column=1, pady = ySpace, padx = xSpace)
    b6.grid(row=3, column=2, pady = ySpace, padx = xSpace)
    b7.grid(row=2, column=0, pady = ySpace, padx = xSpace)
    b8.grid(row=2, column=1, pady = ySpace, padx = xSpace)
    b9.grid(row=2, column=2, pady = ySpace, padx = xSpace)
    bEnter.grid(row=5, column=2, pady = ySpace, padx = xSpace)
    bClear.grid(row=5, column=0, pady = ySpace, padx = xSpace)
    bLock.grid(row=5, column=3, pady = ySpace, padx = 0)
    bTap.grid(row=3, column=3, pady = ySpace, padx = 5)
    bplay.grid(row=4, column=3, pady = ySpace, padx = 0)

def playS():
    global play, first, last, loop
    if(play == False):
        print("play")
        bplay['text'] = "pause"
        play = True
        if(first != "" and last != ""):
            loop = True
    else:
        print("pause")
        bplay['text'] = "play"
        play = False
        loop = False

# Tap function (runs when bTap or bTap2 are pressed)
    # records time.time, and adds the diffrence between that and the time from the last tap to 'times'
    # if the array has 4 elements, it delets the first one (the oldest one)
    # the average is taken from 'times' and set as the new 'tapTime'
def tap():
    global times, flashLoop, lastTime, tapTime

    flashLoop = False
    seconds = time.time()
    times = np.append(times, (seconds-lastTime))
    lastTime = seconds

    if(times.size == 4):
        times = np.delete(times, 0)

    average = (times[0]+times[1]+times[2])/3
    tapTime = average
    flashLoop = True

    # print(times)
    print(average)

# flash function (loops in a thread)
    # changes color of the button to red, runs macroLoop() in a thread, sleeps for 'flashTime' and turnd the button back to white, then sleeps for the remainder of tapTime
def flash():
    while(flashLoop):
        bTap["background"] = "red"
        bTap2["background"] = "red"
        threading.Thread(target=macroLoop).start()
        time.sleep(flashTime)
        bTap["background"] = "white"
        bTap2["background"] = "white"
        time.sleep((tapTime)-flashTime)


if __name__ == "__main__":
    gui.title("OSC Controller")
        # "382x270" is the approximate usable screen resolution of the touch screen used. This is for testing purposes. It is recommended to use ‘-fullscreen’ below it
    # gui.geometry("382x270")
    gui.attributes('-fullscreen', True)
    gui.configure(background="grey")

    # Creates 'expression_field', the primary text box for displaying the keypad input
    equation = StringVar()
    expression_field = Entry(gui, textvariable=equation, font=('Georgia 30'), width=19, justify='left')
    expression_field.config(state=DISABLED)
    expression_field.grid(columnspan = 10, ipadx=2, ipady=0)

    # Creates ‘text’, the text field used to show the user what needs to be typed in, on what macros are currently selected
    text = Text(gui, height = 1, fg = "red")
    text.insert(INSERT, "   Add macro range")
    text.grid(columnspan=200, ipadx=150, ipady=0)

        # buttons 1 - 3
    b1 = Button(gui, text ="One", width = bWidth, height = bHeight, command = lambda: press(1))
    b1.grid(row=4, column=0, pady = ySpace, padx = xSpace)
    b2 = Button(gui, text ="Two", width = bWidth, height = bHeight, command = lambda: press(2))
    b2.grid(row=4, column=1, pady = ySpace, padx = xSpace)
    b3 = Button(gui, text ="Three", width = bWidth, height = bHeight, command = lambda: press(3))
    b3.grid(row=4, column=2, pady = ySpace, padx = xSpace)

        # buttons 4 - 6
    b4 = Button(gui, text ="Four", width = bWidth, height = bHeight, command = lambda: press(4))
    b4.grid(row=3, column=0, pady = ySpace, padx = xSpace)
    b5 = Button(gui, text ="Five", width = bWidth, height = bHeight, command = lambda: press(5))
    b5.grid(row=3, column=1, pady = ySpace, padx = xSpace)
    b6 = Button(gui, text ="Six", width = bWidth, height = bHeight, command = lambda: press(6))
    b6.grid(row=3, column=2, pady = ySpace, padx = xSpace)

        # buttons 7 - 9
    b7 = Button(gui, text ="Seven", width = bWidth, height = bHeight, command = lambda: press(7))
    b7.grid(row=2, column=0, pady = ySpace, padx = xSpace)
    b8 = Button(gui, text ="Eight", width = bWidth, height = bHeight, command = lambda: press(8))
    b8.grid(row=2, column=1, pady = ySpace, padx = xSpace)
    b9 = Button(gui, text ="Nine", width = bWidth, height = bHeight, command = lambda: press(9))
    b9.grid(row=2, column=2, pady = ySpace, padx = xSpace)

        # buttons 0, clear, enter
    bClear = Button(gui, text ="Clear", width = bWidth, height = bHeight, command = lambda: clear())
    bClear.grid(row=5, column=0, pady = ySpace, padx = xSpace)
    b0 = Button(gui, text ="Zero", width = bWidth, height = bHeight, command = lambda: press(0))
    b0.grid(row=5, column=1, pady = ySpace, padx = xSpace)
    bEnter = Button(gui, text ="Enter", width = bWidth, height = bHeight, command = lambda: enter())
    bEnter.grid(row=5, column=2, pady = ySpace, padx = xSpace)

        # buttons Lock, play/pause, Tap
    bLock = Button(gui, text ="Lock", width = bWidth, height = bHeight, command = lambda: lockOut())
    bLock.grid(row=5, column=3, pady = ySpace, padx = 0)
    bplay = Button(gui, text ="play", width = bWidth, height = bHeight, command = lambda: playS())
    bplay.grid(row=4, column=3, pady = ySpace, padx = 0)
    bTap = Button(gui, text ="TAP", width = bWidth, height = bHeight, command = lambda: tap())
    bTap.grid(row=2, column=3, pady = ySpace, padx = 5)

        # buttons Tap2, Unlock (Hidden buttons)
    bTap2 = Button(gui, text ="TAP", width = 20, height = 5, command = lambda: tap())
    bTap2.grid(row=5, column=5, pady = ySpace, padx = xSpace)
    bTap2.grid_forget()
    bUnLock = Button(gui, text ="Unlock", width = bWidth, height = bHeight, command = lambda: unlock())
    bUnLock.grid(row=5, column=4, pady = ySpace, padx = xSpace)
    bUnLock.grid_forget()


    # starts Multithreaded loop that flashes the tap button, and triggures the osc command
    t1 = threading.Thread(target=flash)
    gui.after(10, t1.start())

    # Primes the 'times' array and 'lastTime', so that the first reading isn't
    seconds = time.time()
    lastTime = seconds
    times = np.append(times, (1))
    times = np.append(times, (1))
    times = np.append(times, (1))
    times = np.delete(times, 0)

    # t2 = threading.Thread(target=macroLoop)
    # gui.after(10, t2.start())

    gui.mainloop()