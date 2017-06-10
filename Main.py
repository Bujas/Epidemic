# some_file.py
# encoding=utf-8
import re
import ttk
import Person
import datetime
from pymnet import *
from Tkinter import *
from random import randint, choice
from shutil import copyfile
import webbrowser as wb

mplex = MultiplexNetwork(couplings="none")
people = {}
infected = []
S = 0
I = 0
R = 0
probabilityInfected = 1
endOfCycle = 10
backToBlack = 10


def openResults():
    wb.open(str(textPathToSave.get()))

def readNodes():
    try:
        people.clear()
        with open(str(pathToNodes.get())) as openfileobject:
            next(openfileobject)
            for lineInFile in openfileobject:
                tmp = lineInFile.split()
                people[int(tmp[0])] = Person.Person(1, int(tmp[0]))
    except:
        labelProgressBar.set(
            "Oups, we have problem: \n" + str(sys.exc_info()) + "\n  Fill all space with correct inputs!")


def readGraph():
    with open(str(pathToGraphs.get())) as openfileobject:
        for lineInFile in openfileobject:
            numbers = map(int, re.findall(r'\d+', lineInFile))
            if (numbers[1] != numbers[2]):
                mplex[numbers[1], numbers[0]][numbers[2], numbers[0]] = 1


def infection():
    global probabilityInfected
    infectedIds = [person.number for person in infected]
    for e in mplex.edges:
        if int(e[0]) in infectedIds and people[e[1]].status != 3:
            k = randint(0, 100)
            if k < probabilityInfected:
                people[e[1]].status = 2
        elif int(e[1]) in infectedIds and people[e[0]].status != 3:
            k = randint(0, 100)
            if k < probabilityInfected:
                people[e[0]].status = 2


def finalForm():
    global infected, S, I, R, endOfCycle, backToBlack
    for person in infected:
        k = randint(0, 100)
        if k < endOfCycle:
            person.status = 3
        else:
            k = randint(0, 100)
            if k < backToBlack:
                person.status = 1
    infected = [people[id] for id in people if people[id].status == 2]
    I = len(infected)
    R = 0
    for id in people:
        if people[id].status == 3:
            R += 1
    S = len(people) - I - R


def runSimulation():
    try:
        global S, I, R, progressBar, probabilityInfected, endOfCycle, backToBlack
        fig = draw(mplex, layout="random", show=True, backend="threejs")
        progressBar["maximum"] = int(textNumberOfCycles.get())
        endOfCycle = int(textResistOrDead.get())
        backToBlack = int(textBackToBlack.get())
        probabilityInfected = int(textProbabilityInfected.get())
        infectedAtBegin = int(round(int(textProbabilityInfectedAtBegin.get()) * len(people) / 100))
        for i in range(infectedAtBegin):
            person = choice(people)
            person.status = 2
            infected.append(person)
        I = len(infected)
        S = len(people) - I
        R = 0
        now = datetime.datetime.now()
        csv_file = open(str(textPathToSave.get()) + '\\result from ' + str(now.strftime("%Y-%m-%d %H-%M")) + '.csv','w')
        html_file = open(str(textPathToSave.get()) + '\\result from ' + str(now.strftime("%Y-%m-%d %H-%M")) + '.html',"w")
        html_file.write(fig)
        html_file.close()
        copyfile("Detector.js", str(textPathToSave.get()) + "\\Detector.js")
        copyfile("OrbitControls.js", str(textPathToSave.get()) + "\\OrbitControls.js")
        copyfile("three.min.js", str(textPathToSave.get()) + "\\three.min.js")
        csv_file.write('Population; Susceptible; Infective; Removed\n%d;%d;%d;%d\n' % (len(people), S, I, R))

        for z in range(int(textNumberOfCycles.get())):
            infection()
            finalForm()
            csv_file.write("%d;%d;%d;%d\n" % (len(people), S, I, R))
            progressBar["value"] = z + 1
            frame.update_idletasks()
        csv_file.close()
        labelProgressBar.set("Done")
    except:
        labelProgressBar.set(
            "Oups, we have problem: \n" + str(sys.exc_info()) + "\n  Fill all space with correct inputs!")


def create():
    global pathToNodes, pathToGraphs, labelProgressBar, textNumberOfCycles, progressBar, textPathToSave, textResistOrDead, textBackToBlack, textProbabilityInfected, textProbabilityInfectedAtBegin, frame
    frame = Tk()
    frame.title("Simulation of epidemic")
    frame.geometry("500x600")

    # label for field for nodes
    labelTexstForNodes = StringVar()
    labelTexstForNodes.set("Set path to file with nodes")
    label1 = Label(frame, textvariable=labelTexstForNodes)
    label1.pack(padx=5);

    # field  to load nodes button
    pathToNodes = StringVar()
    path = Entry(frame, textvariable=pathToNodes, width=40)
    path.pack(padx=5, pady=5);

    # add button to load nodes button
    button1 = Button(frame, text="Load nodes", width=20, command=readNodes)
    button1.pack(padx=5, pady=5);

    # label for field for edges
    labelTexstForEdges = StringVar()
    labelTexstForEdges.set("Set path to file with edges")
    label2 = Label(frame, textvariable=labelTexstForEdges)
    label2.pack(padx=5);

    # field to load nodes graphs
    pathToGraphs = StringVar()
    GraphsPath = Entry(frame, textvariable=pathToGraphs, width=40)
    GraphsPath.pack(padx=5, pady=5);

    # add button to load nodes graphs
    button2 = Button(frame, text="Load edges", width=20, command=readGraph)
    button2.pack(padx=5, pady=5);

    # label for field for Percent infected at the beginning
    labelQuantityInfectedAtBegin = StringVar()
    labelQuantityInfectedAtBegin.set("Percent infected at the beginning - Value from compartment: 1-100 ")
    label3 = Label(frame, textvariable=labelQuantityInfectedAtBegin)
    label3.pack(padx=5);

    # field to quantity Percent infected at the beginning
    textProbabilityInfectedAtBegin = StringVar(None)
    ProbabilityInfecteddAtBegin = Entry(frame, textvariable=textProbabilityInfectedAtBegin, width=20)
    ProbabilityInfecteddAtBegin.pack(padx=5, pady=5);

    # label for field for Percent infected from neighbor
    labelQuantityInfected = StringVar()
    labelQuantityInfected.set("Percent infected from neighbor - Value from compartment: 1-100 ")
    label4 = Label(frame, textvariable=labelQuantityInfected)
    label4.pack(padx=5);

    # field to percent to Percent infected from neighbor
    textProbabilityInfected = StringVar(None)
    QuantityInfected = Entry(frame, textvariable=textProbabilityInfected, width=20)
    QuantityInfected.pack(padx=5, pady=5);

    # label for field for Percentage of cured but susceptible
    labelBackToBlack = StringVar()
    labelBackToBlack.set("Percentage of cured but susceptible - Value from compartment: 1-100 ")
    label5 = Label(frame, textvariable=labelBackToBlack)
    label5.pack(padx=5);

    # field to Percentage of cured but susceptible
    textBackToBlack = StringVar(None)
    BackToBlack = Entry(frame, textvariable=textBackToBlack, width=20)
    BackToBlack.pack(padx=5, pady=5);

    # label for field for Percentage of immunization or death
    labelResistOrDead = StringVar()
    labelResistOrDead.set("Percentage of immunization or death - Value from compartment: 1-100 ")
    label6 = Label(frame, textvariable=labelResistOrDead)
    label6.pack(padx=5);

    # Percentage of immunization or death
    textResistOrDead = StringVar(None)
    ResistOrDead = Entry(frame, textvariable=textResistOrDead, width=20)
    ResistOrDead.pack(padx=5, pady=5);

    # label for field for Number of cycles
    labelNumberOfCycles = StringVar(None)
    labelNumberOfCycles.set("Number of cycles")
    label7 = Label(frame, textvariable=labelNumberOfCycles)
    label7.pack(padx=5);

    # field to percent to Number of cycles
    textNumberOfCycles = StringVar(None)
    numberOfCycles = Entry(frame, textvariable=textNumberOfCycles, width=20)
    numberOfCycles.pack(padx=5, pady=5);

    # label for field for Path
    labelPathToSave = StringVar(None)
    labelPathToSave.set("Path to save csv file and graph in html")
    label8 = Label(frame, textvariable=labelPathToSave)
    label8.pack(padx=5);

    # field to percent to Path
    textPathToSave = StringVar(None)
    PathToSave = Entry(frame, textvariable=textPathToSave, width=20)
    PathToSave.pack(padx=5, pady=5);

    # add button to load run symulation
    button3 = Button(frame, text="Start simulation", width=20, command=runSimulation)
    button3.pack(padx=5, pady=5);

    labelProgressBar = StringVar(None)
    labelProgressBar.set("Progress")
    label9 = Label(frame, textvariable=labelProgressBar)
    label9.pack(padx=5);

    progressBar = ttk.Progressbar(frame)
    progressBar.pack(fill=X, expand=1)

    button4 = Button(frame, text="Open folder with results", width=20, command=openResults)
    button4.pack(padx=5, pady=5);

    # run
    frame.mainloop()

if __name__ == '__main__':
    create()
