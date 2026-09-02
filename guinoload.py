import sys, tty, termios

needsprint=True
solvereturn=False
unknown="?"
# FRECUENCIA ABSOLUTA / ABSOLUTE FREQUENCY
# FRECUENCIA ABSOLUTA SUMMADA / SUMMED ABSOLUTE FREQUENCY
# FRECUENCIA PROPORCIONAL / PROPORTIONAL FREQUENCY
# FRECUENCIA PROPORCIONAL SUMMADA / SUMMED PROPORTIONAL FREQUENCY
# PUNTOS DE DATOS TOTALES / TOTAL DATAPOINTS
dd=[unknown]
fa=[unknown]
faa=[unknown]
fp=[unknown]
fpp=[unknown]

errormsg=""

findex = {"fa": 0,
       "faa": 1,
       "fp": 2,
       "fpp": 3,
       "dd": 4
       }
settings={"decprec":3,
          "solvedd":False,
          "spacing":1,
          "write on move": True,
          "fa":"fi",
          "faa": "Fi",
          "fp": "hi",
          "fpp": "Hi",
          "dd": "N",

          "cursorcolor":96,
          "K rm col": "n",
          "K add col": "m",
          "K brute": "b",
          "K solve": "f",
          "K erasechart": "e",
          "K clearcell": "x",
          "K ch set": "p",
          "K help": "h",
          "K quit": "q",

          }

chart=[]

defsettings=settings.copy()
cursor=[0,0]

buffer=""

def logic():
    global chart,fa,faa,fp,fpp,dd,settings, needsprint, errormsg, buffer

    buffer=""
    while True:
        # Refresh the chart
        chart = [fa, faa, fp, fpp, dd]
        biggestrow = []
        for i in chart[:4]:
            biggestrow.append(len(i) - 1)
        chart = padtable(biggestrow, chart, 1)
        for row in range(len(chart)):
            for cell in range(len(chart[row])):
                try:
                    if type(chart[row][cell])==float:
                        if float(chart[row][cell]).is_integer():
                            chart[row][cell] = int(chart[row][cell])
                            if chart[row][cell] < 0:
                                chart[row][cell] = unknown

                        try:
                            if len(cutup(chart[row][cell], ".")[1]) > settings["decprec"]:
                                chart[row][cell] = float(chart[row][cell], settings["decprec"])
                        except IndexError:
                            pass

                except ValueError:
                    pass
        if needsprint:
            print('\033[2J\033[H')
            print(f'{" "*10}{settings["K rm col"]},{settings["K add col"]}-Remove/Add last entries  {settings["K brute"]}-Bruteforce  {settings["K erasechart"]}-Erase Chart  {settings["K clearcell"]}-Clear Cell  {settings["K ch set"]}-Change Settings  {settings["K solve"]}-Solve Cell  {settings["K help"]}-Help  {settings["K quit"]}-Quit')
            tableprint()
        needsprint=True
        print(f"\033[{settings["cursorcolor"]};1m{buffer}\033[0m")
        print(f"\033[91;1m{errormsg}\033[0m")
        errormsg=""
        key = wait_for_key()
        if cursor[0] != 4:
            position = f"{cursor[0]},{cursor[1]}"
        else:
            position = "dd"
        if key in ("UP", "DOWN", "LEFT", "RIGHT"):
            if settings["write on move"]:
                write_to_cell(position, silent=True)
            ishoriz = 1
            if key in ("UP", "DOWN"):
                ishoriz = 0
            movement = 1
            if key in ("UP", "LEFT"):
                movement = -1

            cursor[ishoriz]+=movement

        elif key.isdigit() or key == ".":
            buffer += key

        elif key == "BACKSPACE":
            buffer = buffer[:-1]

        elif key == "ENTER":
            write_to_cell(position)

        elif key == settings["K rm col"].upper():
            for frequency in chart[:4]:
                if not len(frequency) <= 1:
                    frequency.pop()

        elif key == settings["K add col"].upper():
            for frequency in chart[:4]:
                frequency.append(unknown)

        elif key == settings["K brute"].upper():
            brutesolve()

        elif key == settings["K solve"].upper():
             solve(position, override=False)

        elif key == settings["K help"].upper():
            helptxt()

        elif key == settings["K erasechart"].upper():
            fullclear = (0,1,2,3,4)
            freqclear = cursor[0]
            clearbox = (" ",
                        "Do you want to clear the table or the frequency?",
                        f"{settings['K rm col']} - Frequency",
                        f"{settings['K add col']} - Table",
                        "Anything else to cancel",
                        " ")
            make_box(clearbox, "101;97;1")
            victim = wait_for_key()
            if victim == settings['K add col'].upper():
                cleartable(fullclear)
            elif victim == settings['K rm col'].upper():
                cleartable(freqclear)


        elif key == settings["K clearcell"].upper():
            try:
                modify(f"{position}-clr")
                buffer = ""
            except IndexError:
                pass

        elif key == settings["K quit"].upper():
            quittingbox = (" ",
                           "Are you sure you want to quit?",
                           "Y = Yes",
                           "Other = No",
                           " ")
            make_box(quittingbox, "44;97;1", 60)
            quitcmd = wait_for_key()
            if quitcmd == "Y":
                quitlogic()

        elif key == settings["K ch set"].upper():
            settingschange()

        cursor[0]%=5
        cursor[1]%=(len(chart[0])if len(chart[0]) != 0 else 1)
        #Set the dd variable because im not globalizing dd every single time im sloppy enough when it comes to global vars
        dd=chart[4]

def write_to_cell(where, silent=False):
    global buffer, errormsg
    if buffer=="":
        if not silent:
            errormsg="Empty buffer"
        return
    try:
        modify(f"{where}-{buffer}")
        buffer = ""
    except IndexError:
        errormsg="Out of index"

def make_box(boxtext, style="44;97", boxwidth=None):
    print(f'\033[2J\033[H\033[{style}m', end="")
    if boxwidth==None:
        boxwidth=0
        for i in boxtext:
            boxwidth=max(len(i), boxwidth)
    for textline in boxtext:
        print(f"  {textline:{boxwidth}}  ")
    print("\033[0m")

def settingschange():
    global settings
    options = {
        "Decimal Precision (fp)":int,
        "Solve Total Datapoints?":bool,
        "Table File Destination":str,
        "Spacing in table":int,
        "Write buffer to cell on cursor?": bool,
        "Absolute Frequency Label":str,
        "Summed Absolute Frequency Label":str,
        "Proportional Frequency Label":str,
        "Summed Proportional Frequency Label":str,
        "Total Datapoints Label":str,
        "Color of Cursor (In Ansi Color Code) (Use Foreground code)": int,
        "KEY - Remove": str,
        "KEY - Add Column": str,
        "KEY - Brute Solve": str,
        "KEY - Solve Cell": str,
        "KEY - Erase Chart": str,
        "KEY - Clear Cell": str,
        "KEY - Change settings": str,
        "KEY - Help Key": str,
        "KEY - Quit": str,
    }
    print("Leave blank to not change, input minus to reset to its default value")
    for i in range(len(tuple(settings.keys()))):
        option=tuple(settings.keys())[i]
        prompt=tuple(options.keys())[i]
        type=tuple(options.values())[i]

        worked=False
        while not worked:
            want=input((prompt + "\n{v}\n> ").format(v=settings[option])).strip()
            worked=True

            try:
                if want=="":
                    pass
                elif want=="-":
                    settings[option]=defsettings[option]
                elif type==bool:
                    if want.lower() in ("true", "1", "y"):
                        settings[option] = True
                    else:
                        settings[option] = False
                elif option[:2]=="K " and len(want)!=1:
                    worked=False
                    print("\033[31mInvalid Value! Must only be one character.\033[0m")
                else:
                    settings[option] = type(want)
            except ValueError:
                worked = False
                print("\033[31mInvalid Value!.\033[0m")

        flag="w" if os.path.exists("settings.json") else "x"
        json.dump(settings, open("settings.json", flag), indent=0)

def quitlogic():
    print('\033[2J\033[H')
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

    freqpad=0
    freqlie=tuple(settings.keys()).index("fa")
    for i in tuple(settings.values())[freqlie:freqlie+5]:
        freqpad=max(freqpad, len(i))

    for frequency in range(len(printchart)):
        if row=="":
            graphic=frequency
        else:
            graphic=row
        prettyprint=""

        for entry in range(len(printchart[frequency])):
            selectcolor = ""
            if (tuple(cursor) == (frequency, entry) or (frequency == cursor[0] == 4)):
                selectcolor = f'\033[30;{settings["cursorcolor"]+10}m'
            elif printchart[frequency][entry]==unknown:
                selectcolor = f'\033[90m'
            prettyprint+=f"{selectcolor}{printchart[frequency][entry]:>{biggest}}\033[0m,{' '*settings["spacing"]}"
        prettyprint='['+prettyprint[:-(settings["spacing"]+1)]+"]"
        print(f'{settings[tuple(findex.keys())[graphic]]:>{freqpad+1}}{' '*settings["spacing"]}{prettyprint:>{biggest}}')


def brutesolve():
    global chart
    significant=True
    while significant:
        # Do this loop until it has no effect on the board
        significant=False
        for y in range(len(chart[0])):
            for x in (range(4)):
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
        modify(f"{xa},{ya}-{va}")
        solvereturn=True

def solve(txt,bg=False, override=True):
    #X AND Y FUNCTION ARGUMENTS USE USER ROWS AND COLUMNS (start at 1, not 0).
    global chart, solvereturn, errormsg
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
                    errormsg="Already Solved!"
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
                elif unknown not in chart[x-1]:
                    smod(c, sum(chart[x-1]))

            ## general cases
            # CAN I GET THIS FROM THE ABSOLUTE/PROPORTIONAL FREQ?

            if isknown(4, 0, atp, y) and not solvereturn:
                smod(c,(chart[atp][y] / chart[4][0]) if x > 1 else (chart[atp][y] * chart[4][0]))
        except IndexError:
            pass

        if solvereturn==False and not bg:
            errormsg="Couldn't solve cell :("

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
        return int(input)
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
    global chart, settings, errormsg
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
            cell.append(int(temp[1]))
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
    txt=str(txt)
    prev = 0
    found = [-1, ]
    if txt[0]==lookfor:
        found.append(0)
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
    helpentries=("This is the help book. e to elaborate, f to finish reading, p to spill",

                 '---ACTIONS',
                 'Move around the table with the arrow keys',
                 'Typing numbers will put them into a releaseable buffer. Release this buffer with the enter key',
                 f"Clear a cell by pressing {settings["K clearcell"]}",
                 f"You can try to solve a cell by pressing {settings["K solve"]}",
                 f"You can try to brute force the whole table by pressing {settings["K brute"]}",
                 f"Add or remove last entries by pressing {settings["K add col"]} and {settings["K rm col"]} respectively",
                 f"Quit the program by pressing {settings["K quit"]}",
                 f"Erase the whole chart by pressing {settings["K erasechart"]}",
                 f"Adjust some settings by pressing {settings["K ch set"]}",

                 '---FREQUENCIES',
                 f'{settings["fa"]} - ABSOLUTE FREQUENCY',
                 f'{settings["faa"]} - SUMMED ABSOLUTE FREQUENCY',
                 f'{settings["fp"]} - PROPORTIONAL FREQUENCY',
                 f'{settings["fpp"]} - SUMMED PROPORTIONAL FREQUENCY',
                 f'{settings["dd"]} - TOTAL DATAPOINTS',
                 )
    elaborateentries = ("This help book will contain everything you need to know to use this program efficiently. If contains commands, the syntax, and explanations on most everything in the program. use e to elaborate, f to finish reading, and p to spill, anything else to exit. if using p after elaborating, will print everything elaborated",

                        'These are what you will be using to interface with your table. This script is no longer a CLI/Text Based Interface because i rock and am awesome so a GUI is provided',
                        'Move around the table with the arrow keys. A bright cursor will tell you where you are. The selected cell is the one all cell-specific actions will be executed on',
                        'Typing numbers or a period for a decimal will put them into a releaseable buffer, shown under the chart. Release this buffer into the selected cell with the enter key.',
                        f"Clear a cell by pressing {settings["K clearcell"]}. Has no confirmation.",
                        f"You can try to solve a cell by pressing {settings["K solve"]}. It will use surrounding information to determine the value, but might not always work.",
                        f"You can try to brute force the whole table by pressing {settings["K brute"]}. Might not always work completely and might be very resource heavy",
                        f"Add or remove last entries by pressing {settings["K add col"]} and {settings["K rm col"]} respectively. This is destructive. Dont add to many entries, as your terminal may render them funky!",
                        f"Quit the program by pressing {settings["K quit"]}, and chose to save the chart or not.",
                        f"Erase the whole chart by pressing {settings["K erasechart"]}. Has confirmation",
                        f"Adjust some settings by pressing {settings["K ch set"]}",

                        f'---FREQUENCIES',
                        f'{settings["fa"]} - ABSOLUTE FREQUENCY: How many datapoints fall into that category',
                        f'{settings["faa"]} - SUMMED ABSOLUTE FREQUENCY: How many datapoints fall into that category and the ones preceeding it',
                        f'{settings["fp"]} - PROPORTIONAL FREQUENCY: How much of the total datapoints fall into that category',
                        f'{settings["fpp"]} - SUMMED PROPORTIONAL FREQUENCY: How much of the total datapoints fall into that category and the ones preceeding it',
                        f'{settings["dd"]} - TOTAL DATAPOINTS: How many datapoints were collected',

                        )

    doingshit=True
    print('\033[2J\033[H')
    while doingshit:
        for i in range(len(helpentries)):
            issimple = True
            onthisentry = True
            canelaborate = True

            print("\033[s")
            prompt = f"[_{"/e" if canelaborate else ""}/p/f]      "
            print(f"\033[H{prompt}")
            print("\033[u")

            while onthisentry:
                if not issimple:
                    print(f"\033[{settings["cursorcolor"]}m{elaborateentries[i]}\033[0m")
                else:
                    print(helpentries[i])
                usr=wait_for_key().lower()
                onthisentry = False
                if canelaborate and usr=="e":
                    onthisentry = True
                    canelaborate=False
                    issimple=False
                    continue
                match usr:
                    case "p":
                        if not issimple:
                            tospill=elaborateentries
                        else:
                            tospill=helpentries
                        print("")
                        for entry in tospill:
                            print(entry)
                        print("")
                        doingshit = False
                        break
                    case "f":
                        doingshit=False
                    case _:
                        pass
                if not doingshit:
                    break
            if not doingshit:
                break
        doingshit=False
    print("")


def cleartable(arg=(0,1,2,3,4)):
    global fa,faa,fp,fpp,dd,unknown
    if type(arg)==int:
        arg=(arg,)
    for frequency in arg:
        for cell in range(len(chart[frequency])):
            chart[frequency][cell]=unknown

commands={"mod": modify,
          "settings": settingschange,
          "solve": solve,
          "clr": cleartable,
          "cleartable": cleartable,
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

prettykey = {
    "\033[A": "Up",
    "\033[B": "Down",
    "\033[C": "Right",
    "\033[D": "Left",
    " ": "Space",
    "\r": "Enter",
    "\n": "Enter",
    "\x7f": "Backspace",
    "\x08": "Backspace",
}

def wait_for_key(desiredkey: str|None =None, *args, **kwargs):
    pressedkey = ""
    while pressedkey == "":
        pressedkey = get_key(*args, **kwargs)
        if desiredkey!=None and pressedkey!=desiredkey.upper():
            pressedkey=""
    return pressedkey.upper()

def get_key(lookup=prettykey):
    fd_for_stdin=sys.stdin.fileno()
    old_stdin_settings=termios.tcgetattr(fd_for_stdin)
    try:
        tty.setcbreak(fd_for_stdin)
        read=sys.stdin.read(1)
        if read=="\033":
            read+=sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd_for_stdin, termios.TCSADRAIN, old_stdin_settings)
    try:
        if read.isalnum():
            pressedkey=read
        else:
            pressedkey=lookup[read].upper()
    except KeyError:
        pressedkey=read
    return pressedkey

if __name__ == '__main__':
    logic()
