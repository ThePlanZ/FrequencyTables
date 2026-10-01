import os, csv, json

needsprint=True
solvereturn=False
unknown="?"
# FRECUENCIA ABSOLUTA / ABSOLUTE FREQUENCY
# FRECUENCIA ABSOLUTA SUMMADA / SUMMED ABSOLUTE FREQUENCY
# FRECUENCIA PROPORCIONAL / PROPORTIONAL FREQUENCY
# FRECUENCIA PROPORCIONAL SUMMADA / SUMMED PROPORTIONAL FREQUENCY
# PUNTOS DE DATOS TOTALES / TOTAL DATAPOINTS
dd=unknown
fa=[]
faa=[]
fp=[]
fpp=[]

findex = {"fa": 0,
       "faa": 1,
       "fp": 2,
       "fpp": 3,
       "dd": 4
       }
settings={"decprec":3,
          "usrnum":True, # If true, row and column indexes will start at 1. if False, row and column indexes start at 0
          "solvedd":False,
          "tablefiledst":"table.csv",
          "spacing":1
          }

defsettings=settings

def logic():
    global chart,fa,faa,fp,fpp,dd,settings, needsprint
    if os.path.exists("settings.json"):
        pendsettings=json.load(open("settings.json", "r"))
    else:
        json.dump(defsettings, open("settings.json", "x"), indent=0)
        pendsettings= defsettings
    if tuple(pendsettings) != tuple(defsettings):
        print("settings dont match, using defaults")
        json.dump(defsettings, open("settings.json", "w"), indent=0)
        settings=defsettings
    else:
        settings=pendsettings

    for file in ["tmp.csv", settings["tablefiledst"]]:
        try:
            if loadchart(file):
                break
        except IndexError:
            print("corrupt chart: index error. try quitting without saving to restore the last properly saved chart")
        except Exception:
            os.remove(file)


    while True:
        # Refresh the chart
        chart = [fa, faa, fp, fpp, dd]
        for row in range(len(chart)):
            for cell in range(len(chart[row])):
                try:
                    if float(chart[row][cell]).is_integer():
                        chart[row][cell] = int(chart[row][cell])
                        if chart[row][cell] < 0:
                            chart[row][cell] = unknown
                except ValueError:
                    pass
        if needsprint:
            tableprint()
        needsprint=True
        if os.path.exists("tmp.csv"):
            os.remove("tmp.csv")
        writer = csv.writer(open("tmp.csv", "x"), quotechar="'", delimiter=",", quoting=csv.QUOTE_STRINGS)
        for row in chart:
            writer.writerow(row)
        #clean usr
        usr=""
        arg=""
        while usr=="":
            usr=input(">>")
        biggestrow=[]
        for i in chart[:4]:
            biggestrow.append(len(i)-1)
        chart = padtable(biggestrow, chart, 1)
        isinvalid = True
        for command in commands:
            tolook = len(command)
            if usr[:tolook] == command:
                isinvalid = False
                torun=commands[command]
                if torun not in tuple(commandprompts):
                    torun()
                    break
                if len(usr) == tolook:
                    arg = ""
                else:
                    arg = usr[tolook:]
                while arg.strip() == "":
                    arg = input(commandprompts[torun])
                torun(arg)

        if isinvalid:
            print("Invalid Command")
            needsprint = False
        #Set the dd variable because im not globalizing dd every single time im sloppy enough when it comes to global vars
        dd=chart[4]


def settingschange():
    global settings
    options = {
        "Decimal Precision (fp)":int,
        "Use UsrNumber?":bool,
        "Solve Total Datapoints?":bool,
        "Table File Destination":str,
        "Spacing in table":int,
    }
    print("Leave blank to not change, input r to reset to its default value")
    for i in range(len(tuple(settings.keys()))):
        option=tuple(settings.keys())[i]
        prompt=tuple(options.keys())[i]
        type=tuple(options.values())[i]

        want=input((prompt + "\n{v}\n> ").format(v=settings[option]))
        if want=="":
            pass
        elif want=="r":
            settings[option]=defsettings[option]
        elif type==bool:
            if want.lower() in ("true", "1", "y"):
                print("nwf")
                settings[option] = True
            else:
                settings[option] = False
        else:
            settings[option] = type(want)

        flag="w" if os.path.exists("settings.json") else "x"
        json.dump(settings, open("settings.json", flag), indent=0)

def quitlogic(save=""):
    if save=="y":
        if os.path.exists(settings["tablefiledst"]):
            os.remove(settings["tablefiledst"])
        os.rename("tmp.csv", settings["tablefiledst"])
    if save=="clr":
        if os.path.exists(settings["tablefiledst"]):
            os.remove(settings["tablefiledst"])
    if os.path.exists("tmp.csv"):
        os.remove("tmp.csv")
    exit(0)


def tableprint(txt=""):
    global findex, chart, needsprint
    needsprint=False
    row=""
    if txt != "":
        ignore=True
        if txt.count(",") == 0:
            txt += ",1-clr"
        elif txt.count("-") == 0:
            txt += "-clr"
            ignore = False
        output=freqsyntax(txt, True)
        row=rowhandler(output[0][0]+1)
        begin=output[1][0]
        end=output[2][0]
        if end=="clr":
            if ignore:
                end=len(chart[row])
            else:
                end=begin+1

        printchart=[chart[row][begin:end]]
    else:
        printchart=chart
    biggest=max(len(str(i)) for freq in printchart for i in freq)
    for frequency in range(len(printchart)):
        if row=="":
            graphic=frequency
        else:
            graphic=row
        prettyprint=""
        for entry in printchart[frequency]:
            prettyprint+=f"{entry:>{biggest}},{' '*settings["spacing"]}"
        prettyprint='['+prettyprint[:-(settings["spacing"]+1)]+"]"
        print(f'{tuple(findex.keys())[graphic]:>3}{' '*settings["spacing"]}{prettyprint:>{biggest}}')


def brutesolve():
    global chart
    significant=True
    while significant:
        # Do this loop until it has no effect on the board
        significant=False
        for y in range(len(chart[0])):
            y+=1
            for x in (range(1,5)):
                if solve(f"{x},{y}", True, False):
                    significant=True
                if x in (1,2):
                    solve("dd", True, False)


def isknown(xa, ya, xb="", yb=""):
    global unknown, chart
    if xa=="dd":
        xa=4
        ya=0
    if str(str(chart[xa][ya])+str(("" if xb=="" or yb=="" else chart[xb][yb]))).count(unknown)<=0:
        return True
    else:
        return False


def smod(coords, va):
    global solvereturn
    xa=coords[0]
    ya=coords[1]
    if va<0:
        solvereturn=False
    else:
        modify("{x},{y}-{v}".format(x=xa+1, y=ya+1, v=va))
        solvereturn=True

def solve(txt,bg=False, override=True):
    #X AND Y FUNCTION ARGUMENTS USE USER ROWS AND COLUMNS (start at 1, not 0).
    global chart, solvereturn
    syntaxreturn=freqsyntax(txt)
    xval=syntaxreturn[0]
    yval=syntaxreturn[1]
    for i in range(len(xval)):
        x=xval[i]
        y=yval[i]
        solvereturn=False
        c=[x,y]

        try:
            if isknown(x, y) and not override:
                if not bg:
                    print("Already Solved!")
                return False

            if x=="dd":
                #if the last faa entry isnt unknown, set chart[4][0] (dd) to it
                if isknown(1, len(chart[1])-1):
                    smod([4,0], chart[1][len(chart[1])-1])
                elif unknown not in chart[0]:
                    smod([4,0], sum(chart[0]))
                else:
                    for chx in [0,1]:
                        for chy in range(len(chart[chx])):
                            if isknown(chx, chy, chx+2, chy):
                                smod([4,0], chart[chx][chy]/chart[chx+2][chy])
                return solvereturn
            #if the cell is known and override is untrue
            #this code is now less of a mess

            # FORMULAS
            accualt = x + ((((x + 1) % 2) * 2) - 1)
            atp = (x + 2) % 4

            # First cell edgecases (fa,faa)(fp,fpp)
            if y==0 and isknown(accualt, y):
                smod(c,chart[accualt][y])

            # Last cell edgecases (fx,dd)(fxx,dd)
            elif y==len(chart[1])-1 and x==1 and isknown("dd", 0):
                smod(c, chart[4][0])
            ## general cases
            # CAN I GET THIS FROM THE ABSOLUTE/PROPORTIONAL FREQ?
            elif isknown(4, 0, atp, y):
                smod(c,(chart[atp][y] / chart[4][0]) if x > 1 else (chart[atp][y] * chart[4][0]))

            ## fa fp cases
            elif x % 2 == 0:
                # CAN I GET THIS FROM THE ACCUMULATED ENTRY BESIDE ME AND THE ACCUMULATED ENTRY BELOW IT?
                if isknown(x+1, y, x+1, y-1):
                    smod(c,chart[x+1][y]-chart[x+1][y-1])

            ## faa fpp cases
            elif x % 2 == 1:
                # CAN I SOLVE MYSELF USING THE ACCUMULATED ENTRY BEFORE ME AND THE NON ACUMMULATED ENTRY AT MY LEVEL?
                if isknown(x, y-1, x-1, y):
                    smod(c, chart[x][y-1] + chart[x-1][y])
                # CAN I SOLVE MYSELF USING THE ACCUMULATED ENTRY ABOVE ME AND THE NON ACUMMULATED ENTRY BESIDES IT?
                elif y<(len(chart)-1) and isknown(x, y+1, x-1, y+1):
                    smod(c, chart[x][y+1] - chart[x-1][y+1])
        except IndexError:
            pass

        return solvereturn


def modify(txt):
    global chart, settings
    syntaxoutput=freqsyntax(txt, True)
    freq=syntaxoutput[0]
    cell=syntaxoutput[1]
    val=syntaxoutput[2]

    #check to see if the table is big enough. if not, pad it
    chart = padtable(cell, chart, 1)
    if len(cell) == len(freq) == len(val):
        for i in range(len(val)):
            if val[i] == -1:
                continue
            elif val[i]=="clr":
                pass
            elif freq[i]<2:
                toval=int(val[i])
            else:
                toval=round(val[i], settings["decprec"])
            chart[freq[i]][cell[i]] = (unknown if val[i]=="clr" else toval)
    else:
        exit(f"[freq][cell][val] dont line up: f{freq} c{cell} v{val}")


def rowhandler(input, candd=False):
    global findex
    input=str(input)
    if input.isdigit() and int(input)<=len(findex):
        return int(input) - int(settings["usrnum"])
    elif input in findex.keys():
        if input=="dd":
            if not candd:
                exit(f"DD not accepted here!")
            elif candd:
                return "dd"
        else:
            return findex.get(input)
    else:
        print(input)
        exit(f"Unknown column type : {input}")


def freqsyntax(txt, needval=False):
    global chart, settings
    pending = []
    freqcol = []
    cell = []
    val = []
    # FOR EVERY INDIVIDUAL ADD COMMAND
    for i in cutup(txt, ")"):
        # APPEND IT CLEANLY TO A SEPRATAE LIST "a,b-c)A,B-C" >> ["a,b-c", "A,B-C"]
        pending.append(i)
    for cmd in range(len(pending)):
        if str(pending[cmd])[:3] == "dd-" and needval==True:
            toval=str(pending[cmd])[3:]
            toval=unknown if toval=="clr" else int(toval)
            chart[4][0] = toval
            val.append(-1)
            cell.append(-1)
            freqcol.append(-1)
        else:
            if needval:
                temp = (cutup(pending[cmd], "-"))
                if temp[1]==("clr" or "c"):
                    temp[1]=="clr"
                elif float(temp[1]).is_integer():
                    temp[1] = int(float(temp[1]))
                else:
                    temp[1] = float(temp[1])
                val.append(temp[1])
            else:
                temp=[unknown]
                temp[0]=pending[cmd]
            if temp[0]=="dd":
                temp[0]="dd,-1"
            temp = cutup(temp[0], ",")
            freqcol.append(rowhandler(temp[0], candd=True))
            cell.append(int(temp[1]) - int(settings["usrnum"]))

    if needval:
        returnval = [freqcol, cell, val]
    else:
        returnval = [freqcol, cell]
    return returnval


def padtable(to, table, endomit):
    #USES TRUENUM
    for column in range(len(table) - endomit):
        if max(to) > len(table[column])-1:
            table[column] = padrow(max(to), table[column], unknown)
    return table


def cutup(txt, lookfor):
    returnval=[]
    prev = 0
    found = [-1, ]
    #While the previous found position isnt -1 (the value given if its not findable)
    while prev != -1:
        #append to the "found" list the position of the first occurence of character you're looking for, starting from right after what's been previously found
        found.append(txt.find(lookfor, prev+1))
        # set prev to the position that has just been found
        prev=found[-1]
    #adds a space to the end of txt for reasons you will see later
    txt+=" "
    for i in range(len(found)-1):
        #start right after the index of one of the characters we've. If its the first itteration, it will use the first value of found (-1), add 1 to it, and start at 0
        b=found[i] + 1
        #end right before the next character we've found. If it's the last itteration, it will use -1, which will cut off the last character, hence the space character being added
        e=found[i+1]
        returnval.append(txt[b:e])
    return returnval


def padrow(truenumneed, list, fill):
    if truenumneed > len(list)-1:
        for pad in range(truenumneed - (len(list)-1)):
            list.append(fill)
    return list

def loadchart(file):
    global fa,faa,fp,fpp,dd
    if os.path.exists(file):
        with open(file, "r") as file:
            reader = csv.reader(file, delimiter=",", quoting=csv.QUOTE_STRINGS, quotechar="'", )
            chart = []
            for row in reader:
                chart.append(row)
        fa = chart[0]
        faa = chart[1]
        fp = chart[2]
        fpp = chart[3]
        dd = chart[4]
        return True

def helptxt():
    print()
    helpentries=("This is the help book. blank input to next, e to elaborate, f to finish reading",
                 '---COMMANDS',
                 'MOD - modify a chart cell. uses freqsyntax',
                 "SETTINGS - change a few settings",
                 "PRINT - Print the full or part of table",
                 "SOLVE - Solve a cell given surrounding information.",
                 "BRUTE - Brute solve the table", # Really need to optomize and give an algorythm to this function...
                 "CLR/CLEAR - Clears the table",
                 "Q - Quits the program, and is the recommended way to terminate.",
                 '---FREQUENCIES',
                 'fa - ABSOLUTE FREQUENCY',
                 'faa - SUMMED ABSOLUTE FREQUENCY',
                 'fp - PROPORTIONAL FREQUENCY',
                 'fpp - SUMMED PROPORTIONAL FREQUENCY',
                 'dd - TOTAL DATAPOINTS',

                 '---MISC',
                 'freqsyntax - "x1,y1-value)x2,y2-value"/"x1,y1)x2,y2" (parenthesis seperate)',
                 )
    elaborateentries = ("This help bok will contain everything you need to know to use this program efficiently. If contains commands, the syntax, and explanations on most everything in the program",
                   'These are what you will be using to interface with your table. This script is a CLI/Text Based Interface, so a GUI is not provided',
                   'Modify a cell on your chart. Uses freqsyntax, which is explained later in the help book. needs a value, which can be set to "clr" to clear the cell. The two coordinates can also be replaced with "dd" to set the total datapoints.',
                   "change settings such as rounding levels, table destination, and if you use UsrNum or not. If you dont know what a setting oes, or like its already set value, leave the input empty to leave it unchanged",
                   "Print the table, or if a column is given right after the print command (print1, printdd), that column. Uneccessary, but available",
                   "Solve a cell given surrounding information. fa and faa use the Rounding Precision setting, while fp and fpp use the Decimal Precision setting",
                   "Brute solve the table, or what can be brute solved. Can be very resource heavy as it is quite unoptomized.",  # Really need to optomize and give an algorythm to this function...
                   "When run as a command, clears the entire table",
                   "Quits the program, and is the recommended way to terminate due to chart saving. When quitting and prompted to save, Y saves, N doesnt save, and CLR clears the saved file to give a fresh slate next launch",

                   'The data rows/columns on the table.',
                   '(call with fa or 1) How many datapoints fall into that category',
                   '(call with faa or 2) How many datapoints fall into that category and the ones preceeding it',
                   '(call with fp or 3) How much of the total datapoints fall into that category',
                   '(call with fpp or 4) How much of the total datapoints fall into that category and the ones preceeding it',
                   '(call with dd or 5, usually dd) How many datapoints were collected',
                   'Miscelaneous things you might need',
                   'uses coordinates for the cell, seperated by commas. (x,y). If a value is needed, seperate with a dash (x,y-v). Multiple commands at once are supported by seperating the commands with a closing parenthesis [cmd1)cmd2]',
                   )
    for i in range(len(helpentries)):
        print(helpentries[i])
        usr=input("[e/_/f] >>")
        if usr=="f":
            break
        elif usr=="e":
            print(elaborateentries[i])
            usr = input("[_/f] >>")
            if usr == "f":
                break

def clear(arg):
    global fa,faa,fp,fpp,dd
    todel = ""
    try:
        todel = int(arg)
    except (ValueError, IndexError):
        pass
    match todel:
        case 1:
            fa = []
        case 2:
            faa = []
        case 3:
            fp = []
        case 4:
            fpp = []
        case 5:
            dd = []
        case _:
            fa,faa,fp,fpp,dd = [],[],[],[],dd
            chart[4] = [unknown]

commands={"mod": modify,
          "settings": settingschange,
          "solve": solve,
          "clr": clear,
          "clear": clear,
          "print": tableprint,
          "brute": brutesolve,
          "help": helptxt,
          "q": quitlogic,
          "quit": quitlogic,
         }

commandprompts={modify: ">",
                solve: ">",
                quitlogic: "Save? [y/n/clr] >> ",
                }


if __name__ == '__main__':
    logic()
