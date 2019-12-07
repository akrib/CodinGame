import sys
import math
import copy
import itertools


OPTIONS = {
  # nombre de dimension de la carte
  "dimension": 1,
  # largeur de la carte
  "width": 30,
  # hauteur de la carte
  "height": None,
  # profondeur de la carte
  "depth": None,
  # grille de stockage dans un tableau valeur possible True ou False
  "usegrid": False,
  # nombe de tour maximum
  "maxturn": 200,
  # nombre de joueur
  "playercount": 2
}


class EventManager:
    class Event:
        def __init__(self, functions):
            if type(functions) is not list:
                raise ValueError("functions parameter has to be a list")
            self.functions = functions

        def __iadd__(self, func):
            self.functions.append(func)
            return self

        def __isub__(self, func):
            self.functions.remove(func)
            return self

        def __call__(self, *args, **kvargs):
            for func in self.functions:
                func(*args, **kvargs)

        @classmethod
        def addEvent(cls, **kvargs):
            """
            #Create an event with no listeners assigned to it
                EventManager.addEvent( eventName = [] )

            #Create an event with listeners assigned to it
                EventManager.addEvent( eventName = [fun1, fun2,...] )

            #Create any number event with listeners assigned to them
                EventManager.addEvent( eventName1 = [e1fun1, e1fun2,...],
                    eventName2 = [e2fun1, e2fun2,...], ... )

            #Add or remove listener to an existing event
                EventManager.eventName += extra_fun
                EventManager.eventName -= removed_fun

            #Delete an event
                del EventManager.eventName

            #Fire the event
                EventManager.eventName()

            addEvent( event1 = [f1,f2,...], event2 = [g1,g2,...], ... )
            creates events using **kvargs to create any number of events.
            Each event recieves a list of functions,
            where every function in the list recieves the same parameters.

            Example:

            def hello(): print "Hello ",
            def world(): print "World"

            EventManager.addEvent( salute = [hello] )
            EventManager.salute += world

            EventManager.salute()

            Output:
            Hello World
            """

            for key in kvargs.keys():
                if type(kvargs[key]) is not list:
                    raise ValueError("value has to be a list")
                else:
                    kvargs[key] = cls.Event(kvargs[key])

                cls.__dict__.update(kvargs)


class Pos:
    def __init__(self, x, y=None, z=None):
        self.x = x
        self.dim = 1
        if(y is not None):
            self.y = y
            self.dim = 2
        if(z is not None):
            self.z = z
            self.dim = 3

    # def manhattan_distance(self, pos):
    #    return abs(self.x - pos.x) + abs(self.y - pos.y)

    def distance(self, pos):
        if(self.dim is None or pos.dim is None):
            raise Exception('class Pos().dim : self == None')
        elif(pos.dim is None):
            raise Exception('class Pos().dim : self == None')
        elif(self.dim != pos.dim):
            raise Exception('class Pos().dim : self != pos')
        elif(self.dim == 1):
            return abs(self.x - pos.x)
        elif(self.dim == 2):
            return math.sqrt(abs(self.x - pos.x)**2 + abs(self.y - pos.y)**2)
        elif(self.dim == 3):
            return math.sqrt(abs(self.x - pos.x)**2 + abs(self.y - pos.y)**2)
        else:
            raise Exception('class Pos().dim : unknown')


class Entity(Pos):
    def __init__(self, id, type, x, y=None, z=None, params={}):
        super().__init__(x, y, z)
        self.id = id
        self.type = type
        self.lastPos = Pos(0, None, None)
        self.setParams(params)

    def setParams(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    def update(self, id, type,  x, y=None, z=None, params={}):
        self.lastPos = Pos(getattr(self, 'x',None), getattr(self, 'x',None), getattr(self, 'x',None))
        self.x = x
        self.y = y
        self.z = z
        self.id = id
        self.type = type
        self.setParams(params)


class Cell(Pos):
    def __init__(self, x, y, z, params={}):
        super().__init__(x, y, z)
        self.setParams(params)

    def setParams(self, params):
        for key, value in params.items():
            setattr(self, key, value)


class Grid:
    def __init__(self, width, height=None, depth=None, params={}):
        self.cells = []
        self.width = width
        self.height = height
        self.depth = depth

        if self.depth is None and self.height is None:
            for x in range(self.width):
                self.cells.append(Cell(x, None, None, {}))
            return
        if self.depth is None:
            for y in range(self.height):
                for x in range(self.width):
                    self.cells.append(Cell(x, y, None, {}))
            return
        for z in range(self.depth):
            for y in range(self.height):
                for x in range(self.width):
                    self.cells.append(Cell(x, y, z, {}))

    def get_cell(self, x, y, z):
        if self.depth is None and self.height is None:
            return self.cells[x]
        if self.depth is None:
            if self.width > x >= 0 and self.height > y >= 0:
                return self.cells[x + self.width * y]
        if self.width > x >= 0 and self.height > y >= 0 and self.depth > z >= 0:
            return self.cells[x + (self.width * y) + (self.depth * z)]
        return None

    def update_cell(self, x, y, z, params):
        self.get_cell(x, y, z).setParams(params)


class Game:
    def __init__(self, options={}):
        self.turn = 0
        self.dimension = 0
        self.width = None
        self.height = None
        self.depth = None
        self.maxturn = 200
        self.usegrid = False
        self.playercount = 2
        self.players = []
        self.eventManager = EventManager()
        self.actionLog = []
        self.setOption(options)
        if self.usegrid is True:
            self.grid = Grid(self.width, self.height, self.depth, {})
        for i in range(self.playercount):
            self.setPlayer(Player(i, "default_player", 0))
            self.actionLog.append([])
                
    def setPlayer(self,player):
        self.players.append(player)
        
    def getPlayer(self,id):
        return self.players[id]
        
    def resetGrid(self):
        self.prev_grid = copy.deepcopy(self.grid)
        self.grid = Grid(self.width, self.height, self.depth)

    def setParams(self, params):
        for key, value in params.items():
            setattr(self, key, value)

    def setOption(self, options):
        # map dimension
        if 'dimension' in options:
            self.dimension = options['dimension']
        # map width int
        if 'width' in options:
            self.width = options['width']
        # map height int
        if 'height' in options:
            self.height = options['height']
        # map depth int
        if 'depth' in options:
            self.depth = options['depth']
        # maxturn int
        if 'maxturn' in options:
            self.maxturn = options['maxturn']
        # usegrid boolean
        if 'usegrid' in options:
            self.usegrid = options['usegrid']
        # playercount int
        if 'usegrid' in options:
            self.usegrid = options['usegrid']

    def log(self, obj, desc=""):
        print(desc, obj, file=sys.stderr)

    def addtoarray(self,arrayname,value):
        self[arrayname].append(value)
        
    def deltoarray(self,arrayname,value):
        self[arrayname].pop(self[arrayname].index(value))
    
    def addActionToLog(self,playerId,turn,logmsg):
        self.actionLog[playerId].append((turn,logmsg))
    
    def getActionLog(self, playerId=None,turn=None):
        if playerId is None:
            playerScope = (0, len(self.players))
        else:
            playerScope = (playerId, PlayerId)
        for i in range(playerScope):
            if turn is None:
                turnScope = (0,len(self.actionLog[i]))
            else:
                turnScope = (turn, turn)
            for j in range(turnScope):
                for k in range(len(self.actionLog[i])):
                    if self.actionLog[i][0] == j:
                        self.log(self.actionLog[i][1], "player "+str(i) + " turn " + str(j))
                        
    def setTurn(self,turn):
        self.turn = turn
    
    def getTurn(self):
        return self.turn
    
    def incTurn(self,step=1):
        self.turn += step
    
    def GetAllUniqueCombinations(self,arr):
        return [itertools.combinations(arr, r) for r in range(len(arr)+1)]


                

#END OF MY CODINGAME DEFAULT Class
cards=[["1","Slimer","creature","1","2","1","------","1","0","0","2 / 1 Creature Summon: You gain 1 health."],
["2","Scuttler","creature","1","1","2","------","0","-1","0","1 / 2 Creature Summon: Deal 1 damage to your opponent."],
["3","Beavrat","creature","1","2","2","------","0","0","0","2 / 2 Creature"],
["4","Plated Toad","creature","2","1","5","------","0","0","0","1 / 5 Creature"],
["5","Grime Gnasher","creature","2","4","1","------","0","0","0","4 / 1 Creature"],
["6","Murgling","creature","2","3","2","------","0","0","0","3 / 2 Creature"],
["7","Rootkin Sapling","creature","2","2","2","-----W","0","0","0","2 / 2 Creature Ward"],
["8","Psyshroom","creature","2","2","3","------","0","0","0","2 / 3 Creature"],
["9","Corrupted Beavrat","creature","3","3","4","------","0","0","0","3 / 4 Creature"],
["10","Carnivorous Bush","creature","3","3","1","--D---","0","0","0","3 / 1 Creature Drain"],
["11","Snowsaur","creature","3","5","2","------","0","0","0","5 / 2 Creature"],
["12","Woodshroom","creature","3","2","5","------","0","0","0","2 / 5 Creature"],
["13","Swamp Terror","creature","4","5","3","------","1","-1","0","5 / 3 Creature Summon: You gain 1 health and deal1 damage to your opponent."],
["14","Fanged Lunger","creature","4","9","1","------","0","0","0","9 / 1 Creature"],
["15","Pouncing Flailmouth","creature","4","4","5","------","0","0","0","4 / 5 Creature"],
["16","Wrangler Fish","creature","4","6","2","------","0","0","0","6 / 2 Creature"],
["17","Ash Walker","creature","4","4","5","------","0","0","0","4 / 5 Creature"],
["18","Acid Golem","creature","4","7","4","------","0","0","0","7 / 4 Creature"],
["19","Foulbeast","creature","5","5","6","------","0","0","0","5 / 6 Creature"],
["20","Hedge Demon","creature","5","8","2","------","0","0","0","8 / 2 Creature"],
["21","Crested Scuttler","creature","5","6","5","------","0","0","0","6 / 5 Creature"],
["22","Sigbovak","creature","6","7","5","------","0","0","0","7 / 5 Creature"],
["23","Titan Cave Hog","creature","7","8","8","------","0","0","0","8 / 8 Creature"],
["24","Exploding Skitterbug","creature","1","1","1","------","0","-1","0","1 / 1 Creature Summon: Deal 1 damage to your opponent."],
["25","Spiney Chompleaf","creature","2","3","1","------","-2","-2","0","3 / 1 Creature Summon: Deal 2 damage to each player."],
["26","Razor Crab","creature","2","3","2","------","0","-1","0","3 / 2 Creature Summon: Deal 1 damage to your opponent."],
["27","Nut Gatherer","creature","2","2","2","------","2","0","0","2 / 2 Creature Summon: You gain 2 health."],
["28","Infested Toad","creature","2","1","2","------","0","0","1","1 / 2 Creature Summon: Draw a card."],
["29","Steelplume Nestling","creature","2","2","1","------","0","0","1","2 / 1 Creature Summon: Draw a card."],
["30","Venomous Bog Hopper","creature","3","4","2","------","0","-2","0","4 / 2 Creature Summon: Deal 2 damage to your opponent."],
["31","Woodland Hunter","creature","3","3","1","------","0","-1","0","3 / 1 Creature Summon: Deal 1 damage to your opponent."],
["32","Sandsplat","creature","3","3","2","------","0","0","1","3 / 2 Creature Summon: Draw a card."],
["33","Chameleskulk","creature","4","4","3","------","0","0","1","4 / 3 Creature Summon: Draw a card."],
["34","Eldritch Cyclops","creature","5","3","5","------","0","0","1","3 / 5 Creature Summon: Draw a card."],
["35","Snail-eyed Hulker","creature","6","5","2","B-----","0","0","1","5 / 2 Creature BreakthroughSummon: Draw a card."],
["36","Possessed Skull","creature","6","4","4","------","0","0","2","4 / 4 Creature Summon: Draw two cards."],
["37","Eldritch Multiclops","creature","6","5","7","------","0","0","1","5 / 7 Creature Summon: Draw a card."],
["38","Imp","creature","1","1","3","--D---","0","0","0","1 / 3 Creature Drain"],
["39","Voracious Imp","creature","1","2","1","--D---","0","0","0","2 / 1 Creature Drain"],
["40","Rock Gobbler","creature","3","2","3","--DG--","0","0","0","2 / 3 Creature Drain, Guard"],
["41","Blizzard Demon","creature","3","2","2","-CD---","0","0","0","2 / 2 Creature Charge, Drain"],
["42","Flying Leech","creature","4","4","2","--D---","0","0","0","4 / 2 Creature Drain"],
["43","Screeching Nightmare","creature","6","5","5","--D---","0","0","0","5 / 5 Creature Drain"],
["44","Deathstalker","creature","6","3","7","--D-L-","0","0","0","3 / 7 Creature Drain, Lethal"],
["45","Night Howler","creature","6","6","5","B-D---","-3","0","0","6 / 5 Creature Breakthrough, DrainSummon: You lose 3 health."],
["46","Soul Devourer","creature","9","7","7","--D---","0","0","0","7 / 7 Creature Drain"],
["47","Gnipper","creature","2","1","5","--D---","0","0","0","1 / 5 Creature Drain"],
["48","Venom Hedgehog","creature","1","1","1","----L-","0","0","0","1 / 1 Creature Lethal"],
["49","Shiny Prowler","creature","2","1","2","---GL-","0","0","0","1 / 2 Creature Guard, Lethal"],
["50","Puff Biter","creature","3","3","2","----L-","0","0","0","3 / 2 Creature Lethal"],
["51","Elite Bilespitter","creature","4","3","5","----L-","0","0","0","3 / 5 Creature Lethal"],
["52","Bilespitter","creature","4","2","4","----L-","0","0","0","2 / 4 Creature Lethal"],
["53","Possessed Abomination","creature","4","1","1","-C--L-","0","0","0","1 / 1 Creature Charge, Lethal"],
["54","Shadow Biter","creature","3","2","2","----L-","0","0","0","2 / 2 Creature Lethal"],
["55","Hermit Slime","creature","2","0","5","---G--","0","0","0","0 / 5 Creature Guard"],
["56","Giant Louse","creature","4","2","7","------","0","0","0","2 / 7 Creature"],
["57","Dream-Eater","creature","4","1","8","------","0","0","0","1 / 8 Creature"],
["58","Darkscale Predator","creature","6","5","6","B-----","0","0","0","5 / 6 Creature Breakthrough"],
["59","Sea Ghost","creature","7","7","7","------","1","-1","0","7 / 7 Creature Summon: You gain 1 health and deal1 damage to your opponent."],
["60","Gritsuck Troll","creature","7","4","8","------","0","0","0","4 / 8 Creature 1"],
["61","Alpha Troll","creature","9","10","10","------","0","0","0","0 / 10 Creature 1"],
["62","Mutant Troll","creature","12","12","12","B--G--","0","0","0","2 / 12 Creature Breakthrough, Guard"],
["63","Rootkin Drone","creature","2","0","4","---G-W","0","0","0","0 / 4 Creature Guard, Ward"],
["64","Coppershell Tortoise","creature","2","1","1","---G-W","0","0","0","1 / 1 Creature Guard, Ward"],
["65","Steelplume Defender","creature","2","2","2","-----W","0","0","0","2 / 2 Creature Ward"],
["66","Staring Wickerbeast","creature","5","5","1","-----W","0","0","0","5 / 1 Creature Ward"],
["67","Flailing Hammerhead","creature","6","5","5","-----W","0","-2","0","5 / 5 Creature WardSummon: Deal 2 damage to your opponent."],
["68","Giant Squid","creature","6","7","5","-----W","0","0","0","7 / 5 Creature Ward"],
["69","Charging Boarhound","creature","3","4","4","B-----","0","0","0","4 / 4 Creature Breakthrough"],
["70","Murglord","creature","4","6","3","B-----","0","0","0","6 / 3 Creature Breakthrough"],
["71","Flying Murgling","creature","4","3","2","BC----","0","0","0","3 / 2 Creature Breakthrough, Charge"],
["72","Shuffling Nightmare","creature","4","5","3","B-----","0","0","0","5 / 3 Creature Breakthrough"],
["73","Bog Bounder","creature","4","4","4","B-----","4","0","0","4 / 4 Creature BreakthroughSummon: You gain 4 health."],
["74","Crusher","creature","5","5","4","B--G--","0","0","0","5 / 4 Creature Breakthrough, Guard"],
["75","Titan Prowler","creature","5","6","5","B-----","0","0","0","6 / 5 Creature Breakthrough"],
["76","Crested Chomper","creature","6","5","5","B-D---","0","0","0","5 / 5 Creature Breakthrough, Drain"],
["77","Lumbering Giant","creature","7","7","7","B-----","0","0","0","7 / 7 Creature Breakthrough"],
["78","Shambler","creature","8","5","5","B-----","0","-5","0","5 / 5 Creature BreakthroughSummon: Deal 5 damage to your opponent."],
["79","Scarlet Colossus","creature","8","8","8","B-----","0","0","0","8 / 8 Creature Breakthrough"],
["80","Corpse Guzzler","creature","8","8","8","B--G--","0","0","1","8 / 8 Creature Breakthrough, GuardSummon: Draw a card."],
["81","Flying Corpse Guzzler","creature","9","6","6","BC----","0","0","0","6 / 6 Creature Breakthrough, Charge"],
["82","Slithering Nightmare","creature","7","5","5","B-D--W","0","0","0","5 / 5 Creature Breakthrough, Drain, Ward"],
["83","Restless Owl","creature","0","1","1","-C----","0","0","0","1 / 1 Creature Charge"],
["84","Fighter Tick","creature","2","1","1","-CD--W","0","0","0","1 / 1 Creature Charge, Drain, Ward"],
["85","Heartless Crow","creature","3","2","3","-C----","0","0","0","2 / 3 Creature Charge"],
["86","Crazed Nose-pincher","creature","3","1","5","-C----","0","0","0","1 / 5 Creature Charge"],
["87","Bloat Demon","creature","4","2","5","-C-G--","0","0","0","2 / 5 Creature Charge, Guard"],
["88","Abyss Nightmare","creature","5","4","4","-C----","0","0","0","4 / 4 Creature Charge"],
["89","Boombeak","creature","5","4","1","-C----","2","0","0","4 / 1 Creature ChargeSummon: You gain 2 health."],
["90","Eldritch Swooper","creature","8","5","5","-C----","0","0","0","5 / 5 Creature Charge"],
["91","Flumpy","creature","0","1","2","---G--","0","1","0","1 / 2 Creature GuardSummon: Your opponent gains 1 health."],
["92","Wurm","creature","1","0","1","---G--","2","0","0","0 / 1 Creature GuardSummon: You gain 2 health."],
["93","Spinekid","creature","1","2","1","---G--","0","0","0","2 / 1 Creature Guard"],
["94","Rootkin Defender","creature","2","1","4","---G--","0","0","0","1 / 4 Creature Guard"],
["95","Wildum","creature","2","2","3","---G--","0","0","0","2 / 3 Creature Guard"],
["96","Prairie Protector","creature","2","3","2","---G--","0","0","0","3 / 2 Creature Guard"],
["97","Turta","creature","3","3","3","---G--","0","0","0","3 / 3 Creature Guard"],
["98","Lilly Hopper","creature","3","2","4","---G--","0","0","0","2 / 4 Creature Guard"],
["99","Cave Crab","creature","3","2","5","---G--","0","0","0","2 / 5 Creature Guard"],
["100","Stalagopod","creature","3","1","6","---G--","0","0","0","1 / 6 Creature Guard"],
["101","Engulfer","creature","4","3","4","---G--","0","0","0","3 / 4 Creature Guard"],
["102","Mole Demon","creature","4","3","3","---G--","0","-1","0","3 / 3 Creature GuardSummon: Deal 1 damage to your opponent."],
["103","Mutating Rootkin","creature","4","3","6","---G--","0","0","0","3 / 6 Creature Guard"],
["104","Deepwater Shellcrab","creature","4","4","4","---G--","0","0","0","4 / 4 Creature Guard"],
["105","King Shellcrab","creature","5","4","6","---G--","0","0","0","4 / 6 Creature Guard"],
["106","Far-reaching Nightmare","creature","5","5","5","---G--","0","0","0","5 / 5 Creature Guard"],
["107","Worker Shellcrab","creature","5","3","3","---G--","3","0","0","3 / 3 Creature GuardSummon: You gain 3 health."],
["108","Rootkin Elder","creature","5","2","6","---G--","0","0","0","2 / 6 Creature Guard"],
["109","Elder Engulfer","creature","5","5","6","------","0","0","0","5 / 6 Creature"],
["110","Gargoyle","creature","5","0","9","---G--","0","0","0","0 / 9 Creature Guard"],
["111","Turta Knight","creature","6","6","6","---G--","0","0","0","6 / 6 Creature Guard"],
["112","Rootkin Leader","creature","6","4","7","---G--","0","0","0","4 / 7 Creature Guard"],
["113","Tamed Bilespitter","creature","6","2","4","---G--","4","0","0","2 / 4 Creature GuardSummon: You gain 4 health."],
["114","Gargantua","creature","7","7","7","---G--","0","0","0","7 / 7 Creature Guard"],
["115","Rootkin Warchief","creature","8","5","5","---G-W","0","0","0","5 / 5 Creature Guard, Ward"],
["116","Emperor Nightmare","creature","12","8","8","BCDGLW","0","0","0","8 / 8 Creature Breakthrough, Charge, Drain, Guard, Lethal, Ward"],
["117","Protein","itemGreen","1","1","1","B-----","0","0","0","Green Item Give a friendly Creature  +1/+1 and Breakthrough."],
["118","Royal Helm","itemGreen","0","0","3","------","0","0","0","Green Item Give a friendly Creature  +0/+3."],
["119","Serrated Shield","itemGreen","1","1","2","------","0","0","0","Green Item Give a friendly Creature  +1/+2."],
["120","Venomfruit","itemGreen","2","1","0","----L-","0","0","0","Green Item Give a friendly Creature  +1/+0 and Lethal."],
["121","Enchanted Hat","itemGreen","2","0","3","------","0","0","1","Green Item Give a friendly Creature  +0/+3.Draw a card."],
["122","Bolstering Bread","itemGreen","2","1","3","---G--","0","0","0","Green Item Give a friendly Creature  +1/+3 and Guard."],
["123","Wristguards","itemGreen","2","4","0","------","0","0","0","Green Item Give a friendly Creature  +4/+0."],
["124","Blood Grapes","itemGreen","3","2","1","--D---","0","0","0","Green Item Give a friendly Creature  +2/+1 and Drain."],
["125","Healthy Veggies","itemGreen","3","1","4","------","0","0","0","Green Item Give a friendly Creature  +1/+4."],
["126","Heavy Shield","itemGreen","3","2","3","------","0","0","0","Green Item Give a friendly Creature  +2/+3."],
["127","Imperial Helm","itemGreen","3","0","6","------","0","0","0","Green Item Give a friendly Creature  +0/+6."],
["128","Enchanted Cloth","itemGreen","4","4","3","------","0","0","0","Green Item Give a friendly Creature  +4/+3."],
["129","Enchanted Leather","itemGreen","4","2","5","------","0","0","0","Green Item Give a friendly Creature  +2/+5."],
["130","Helm of Remedy","itemGreen","4","0","6","------","4","0","0","Green Item Give a friendly Creature  +0/+6.You gain 4 health."],
["131","Heavy Gauntlet","itemGreen","4","4","1","------","0","0","0","Green Item Give a friendly Creature  +4/+1."],
["132","High Protein","itemGreen","5","3","3","B-----","0","0","0","Green Item Give a friendly Creature  +3/+3 and Breakthrough."],
["133","Pie of Power","itemGreen","5","4","0","-----W","0","0","0","Green Item Give a friendly Creature  +4/+0 and Ward."],
["134","Light The Way","itemGreen","4","2","2","------","0","0","1","Green Item Give a friendly Creature  +2/+2.Draw a card."],
["135","Imperial Armour","itemGreen","6","5","5","------","0","0","0","Green Item Give a friendly Creature  +5/+5."],
["136","Buckler","itemGreen","0","1","1","------","0","0","0","Green Item Give a friendly Creature  +1/+1."],
["137","Ward","itemGreen","2","0","0","-----W","0","0","0","Green Item Give a friendly Creature  Ward."],
["138","Grow Horns","itemGreen","2","0","0","---G--","0","0","1","Green Item Give a friendly Creature  Guard.Draw a card."],
["139","Grow Stingers","itemGreen","4","0","0","----LW","0","0","0","Green Item Give a friendly Creature  Lethal and Ward."],
["140","Grow Wings","itemGreen","2","0","0","-C----","0","0","0","Green Item Give a friendly Creature  Charge."],
["141","Throwing Knife","itemRed","0","-1","-1","------","0","0","0","Red Item Give an enemy Creature  -1/-1."],
["142","Staff of Suppression","itemRed","0","0","0","BCDGLW","0","0","0","Red Item Remove all abilities from an enemy Creature ."],
["143","Pierce Armour","itemRed","0","0","0","---G--","0","0","0","Red Item Remove Guard from an enemy Creature ."],
["144","Rune Axe","itemRed","1","0","-2","------","0","0","0","Red Item Deal 2 damage to an enemy Creature ."],
["145","Cursed Sword","itemRed","3","-2","-2","------","0","0","0","Red Item Give an enemy Creature  -2/-2."],
["146","Cursed Scimitar","itemRed","4","-2","-2","------","0","-2","0","Red Item Give an enemy Creature  -2/-2.Deal 2 damage to your opponent."],
["147","Quick Shot","itemRed","2","0","-1","------","0","0","1","Red Item Deal 1 damage to an enemy Creature .Draw a card."],
["148","Helm Crusher","itemRed","2","0","-2","BCDGLW","0","0","0","Red Item Remove all abilities from an enemy Creature ,then deal 2 damage to it."],
["149","Rootkin Ritual","itemRed","3","0","0","BCDGLW","0","0","1","Red Item Remove all abilities from an enemy Creature .Draw a card."],
["150","Throwing Axe","itemRed","2","0","-3","------","0","0","0","Red Item Deal 3 damage to an enemy Creature ."],
["151","Decimate","itemRed","5","0","-99","BCDGLW","0","0","0","Red Item Remove all abilities from an enemy Creature ,then deal 99 damage to it."],
["152","Mighty Throwing Axe","itemRed","7","0","-7","------","0","0","1","Red Item Deal 7 damage to an enemy Creature .Draw a card."],
["153","Healing Potion","itemBlue","2","0","0","------","5","0","0","Blue Item Gain 5 health."],
["154","Poison","itemBlue","2","0","0","------","0","-2","1","Blue Item Deal 2 damage to your opponent.Draw a card."],
["155","Scroll of Firebolt","itemBlue","3","0","-3","------","0","-1","0","Blue Item Deal 3 damage.Deal 1 damage to your opponent"],
["156","Major Life Steal Potion","itemBlue","3","0","0","------","3","-3","0","Blue Item Deal 3 damage to your opponent and gain 3 health."],
["157","Life Sap Drop","itemBlue","3","0","-1","------","1","0","1","Blue Item Deal 1 damage, gain 1 health, and draw a card."],
["158","Tome of Thunder","itemBlue","3","0","-4","------","0","0","0","Blue Item Deal 4 damage."],
["159","Vial of Soul Drain","itemBlue","4","0","-3","------","3","0","0","Blue Item Deal 3 damage and gain 3 health."],
["160","Minor Life Steal Potion","itemBlue","2","0","0","------","2","-2","0","Blue Item Deal 2 damage to your opponent and gain 2 health."]]


class CardList:
    def __init__(self,cardInfo):
        self.id=int(cardInfo[0])
        self.name=cardInfo[1]
        self.cardType=cardInfo[2]
        self.cost=int(cardInfo[3])
        self.damage=int(cardInfo[4])
        self.health=int(cardInfo[5])
        self.Abilities=cardInfo[6]
        self.playerHP=int(cardInfo[7])
        self.enemyHP=int(cardInfo[8])
        self.cardDraw=int(cardInfo[9])
        self.description=cardInfo[10]


class Card:
    def __init__(self,cardListId,instanceId,cardType,cost,attack,defense,abilities="------"):
        self.alive = True
        self.cardListId = cardListId
        self.instanceId = instanceId
        self.cardType = cardType
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.abilities = abilities
        self.bonus = 0
        self.BCDGLW
        if self.abilities[0] == "B":
            self.bonus +=1
        if self.abilities[1] == "C":
            self.bonus +=2
        if self.abilities[2] == "D":
            self.bonus +=2
        if self.abilities[3] == "G":
            self.bonus +=2
        if self.abilities[4] == "L":
            self.attack += 20
        if self.abilities[5] == "D":
            self.bonus +=2
        if cardType == 0 :
            self.ratio = (((attack + defense+ bonus) -  cost)/(attack + defense +  cost))*100
        else: 
            self.ratio = 1
    def dealDamage(self,dmg):
        self.defense -= dmg
        if self.defense <= 0:
            self.alive = False
    
    def getStat(self,stat):
        return self.__dict__[stat]
        
    def setStat(self,stat, newValue):
        self.__dict__[stat] = newValue

    def __repr__(self):
        return(f'id:{self.cardListId}, instanceId:{self.instanceId}, cost:{self.cost},cardtype:{self.cardtype} , attack:{self.attack} , defense:{self.defense}  ')
    #mettre des filtre __lt__ et __gt__ pour trier les plus forte et les moins fortes.

class Player(Entity):
    def __init__(self, id, type, x, y=None, z=None, params={}):
        super().__init__(id, type, x, y, z, params)
        self.hand = []
        self.board = []
        self.health = 0
        self.mana = 0
        self.rune = 0
        self.draw = 0
        
    def setParams(self, params):
        for key, value in params.items():
            setattr(self, key, value)
    
    def update(self,id, type, health, mana, deck, rune, draw ,x=None, y=None,z=None):
        super().update(id, type,  x, y, z, params={})
        self.health = health
        self.mana = mana 
        self.deck = deck
        self.rune = rune
        self.draw = draw 

    def addToBoard(self,card):
        self.board.append(card)
        
    def addToHand(self,card):
        self.hand.append(card)
        
    def delToBoard(self,instanceId):
        for i in range(len(self.board)):
            if self.board[i].getStat("instanceId") == instanceId:
                self.board[i].alive = False
                return
        
    def delToHand(self,instanceId):
        for i in range(len(self.hand)):
            if self.hand[i].getStat("instanceId") == instanceId:
                self.hand[i].alive = False
                return

    def getHandCount(self):
        return  len(self.hand)

    def reset(self):
        self.hand = []
        self.board = []



class GameLegendOfCodeAndMagic(Game):
    def __init__(self, cards, option={}):
        super().__init__(option)
        self.cardList=[]
        self.playerId=0
        self.enemyId=1
        for c in cards:
            self.cardList.append(CardList(c))
        
    def getCardInCardList(self, id):
        if -1 < id < (len(self.cardList) - 1):
            return self.cardList[id-1].id
    
    def getPlayerTypeId(self, who):
        if who=="player":
            return self.playerId
        if who=="enemy":
            return self.enemyId
            
    def setPlayerTypeId(self, who, id):
        self[who + "Id"]=id

class OODA:
    # https://fr.wikipedia.org/wiki/Boucle_OODA
    def __init__(self,g):
        self.g = g
        self.pipe = [] 
        self.draft = []
        
    
    def calcBestCombo(self,c,mana):
        couples = []
        for i in range(1,len(c)+1):
            couples += itertools.combinations(c, i)
    
        costarr= []
        for couple in couples:
            costarr.append(self.cost_sum(couple))
        couples = list(couples)
        for j in range(mana):
            for k in range(len(costarr)):
                if costarr[k] == (mana-j):
                    return couples[k]
        return []



    def cost_sum(self,cards):
        cost = 0
        for card in cards:
            if card.cardType > 0 :
                cost += card.cost + 10
            else :
                cost += card.cost
        return cost
    # recupere les inputs et verifie que le résultat attendu est obtenu sinon log une anomalie
    def observe(self):
        self.g.log("in observe")
        for i in range(2):
            player_health, player_mana, player_deck, player_rune, player_draw = [int(j) for j in input().split()]
            self.g.players[i].update(i,"player",player_health, player_mana, player_deck, player_rune, player_draw)
        opponent_hand, opponent_actions = [int(i) for i in input().split()]
        for i in range(opponent_actions):
            card_number_and_action = input()
            self.g.addActionToLog(g.getPlayerTypeId("enemy"),g.getTurn(),card_number_and_action)
        card_count = int(input())
        for i in range(card_count):
            card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
            card_number = int(card_number)
            instance_id = int(instance_id)
            location = int(location)
            card_type = int(card_type)
            cost = int(cost)
            attack = int(attack)
            defense = int(defense)
            my_health_change = int(my_health_change)
            opponent_health_change = int(opponent_health_change)
            card_draw = int(card_draw)
            #self.g.getPlayer(self.g.getPlayerTypeId("enemy")).reset()
            #self.g.getPlayer(self.g.getPlayerTypeId("player")).reset()
            if self.g.getTurn() < 30:
                self.draft.append(Card(card_number,instance_id,card_type,cost,attack,defense))
            else:
                if location == 0:
                   self.g.getPlayer(self.g.getPlayerTypeId("player")).addToHand(Card(card_number,instance_id,card_type,cost,attack,defense,abilities))
                elif location == 1:
                    self.g.getPlayer(self.g.getPlayerTypeId("player")).addToBoard(Card(card_number,instance_id,card_type,cost,attack,defense,abilities))
                elif location == -1:
                    self.g.getPlayer(self.g.getPlayerTypeId("enemy")).addToBoard(Card(card_number,instance_id,card_type,cost,attack,defense,abilities))
    
    # decide des actions a mener et dans quel ordre
    # stock les resultat attendu 
    def decide(self):
        self.g.log("in decide")    
        if int(self.g.getTurn()) > 29:
            
            myBoard=self.g.getPlayer(self.g.getPlayerTypeId("player")).board
            myboardCount = len(myBoard)
            myHand=self.g.getPlayer(self.g.getPlayerTypeId("player")).hand       
            myCurrentMana=self.g.getPlayer(self.g.getPlayerTypeId("player")).mana
            advboard=self.g.getPlayer(self.g.getPlayerTypeId("enemy")).board
            # boucle sur les cartes du board
            if myboardCount > 0:
                #self.g.log(myBoard)
                for advcard in advboard:
                    if advcard.abilities[3] == "G":
                        for mycard in myBoard:
                            if advcard.alive == True:
                                if mycard.abilities[3] != "G":
                                    self.pipe.append("ATTACK " + str(mycard.instanceId) + " " + str(advcard.instanceId))
                                    self.g.getPlayer(self.g.getPlayerTypeId("player")).delToBoard(mycard.instanceId)
                                    advcard.dealDamage(mycard.attack)
                                    if advcard.alive == False:
                                        break
                               
                    
                for mycard in myBoard:
                    if mycard.alive == True:
                        for advcard in advboard:
                            if advcard.alive == True:
                                if mycard.ratio < advcard.ratio and mycard.attack >= advcard.defense:
                                    self.pipe.append("ATTACK " + str(mycard.instanceId) + " " + str(advcard.instanceId))
                                    self.g.getPlayer(self.g.getPlayerTypeId("player")).delToBoard(mycard.instanceId)
                                    self.g.getPlayer(self.g.getPlayerTypeId("enemy")).delToBoard(advcard.instanceId)
                                    break
                        self.pipe.append("ATTACK " + str(mycard.instanceId) + " -1")
                        self.g.getPlayer(self.g.getPlayerTypeId("player")).delToBoard(mycard.instanceId)

                    #self.g.log( str(card.instanceId)  + " " + str(card.cost) + " " + str(card.attack) + " " + str(card.defense)  , "on board");
            self.g.log(len(myHand))
            if len(myHand) > 0 and myboardCount < 6 :
                #self.g.log(myHand)
                
                combo=self.calcBestCombo(myHand,myCurrentMana)
                #self.g.log(combo)
                if len(combo) > 0:
                    for card in combo:
                        self.pipe.append("SUMMON "+ str(card.instanceId))
                        if card.abilities[1] == "C":
                            cible=[]
                            for advcard in advboard:
                                if advcard.abilities[3] == "G":
                                    cible.append(advcard)
                                    break
                            if len(cible) == 0:
                                self.pipe.append("ATTACK "+ str(card.instanceId) + " -1" )
                            else:
                                self.pipe.append("ATTACK "+ str(card.instanceId) + " " + str(cible[0].insanceId))
                                cible[0].dealDamage(card.attack)
                        self.g.getPlayer(self.g.getPlayerTypeId("player")).delToHand(card.instanceId)
                        myCurrentMana -= card.cost
                        myboardCount+=1
                        if myboardCount==6:
                            return # le board est plein 
               
               if myCurrentMana > 0 and myboardCount > 0:
                   for card in myHand:
                       if card.cardType > 0: 
                           if card.cost <= myCurrentMana:
                            self.pipe.append("USE "+ str(card.instanceId) + " " + str(myBoard[0].instanceId))
                            self.g.getPlayer(self.g.getPlayerTypeId("player")).delToHand(card.instanceId)
                            myCurrentMana -= card.cost
                
                    #return
                #for card in myHand:
                 #   self.g.log( str(card.instanceId)  + " " + str(card.cost) + " " + str(card.attack) + " " + str(card.defense)  , "on myHand");
            
                  #if my card is not gard 
                  #for borad adv
                    #if adv gard count +1
                    #if my card can kill guard go gard count -=1
                  #if my card can kill player go
                  # for board adv
                    # if gardcount ==0 
                      #if my card can kill card go
                  #for my item card in my hand
                    #if enough mana
                    #for my card on board
                        #for adv gard card 
                          #if my boosted card can kill go (boost and attack in this order) gard count -=1
                        #if my boosted card can kill player go (boost and attack in this order) 
                        #for adv card
                            #if my boosted card can kill go (boost and attack in this order)
                        #for each item card reduce mana by cost
                        #atk hero (boost and attack in this order)
                #atk hero 
                # for all my hand card
  
           # your_list = 'abcdefghijklmnopqrstuvwxyz'
           # complete_list = []
            #for current in xrange(10):
             #   a = [i for i in your_list]
              #  for y in xrange(current):
               #     a = [x+i for i in your_list for x in a]
                #    complete_list = complete_list+a

            
            # si card d'item de boost dans la main utiliser la carte  
            
            # si une carte booster sur board capable de tuer un monstre guard sur le board adverse
            
            # si monstre guard sur le terrain prioriser les monstre garde en commançant par les lethal ou les plus faible
            
            # si un monstre adverse capable de me tuer , tuer le monstre
            
            # si une carte sur board capable de tuer un monstre sur le board adverse
            
            # si la voie est libre attaquer le héros adverse (les carte de type guard peuvent attaquer aussi)
            
            # si toute les carte posé ont jouer, placer de nouvelle carte 
            #   (optimiser au mieux le mana ,sort list par plus gros et additionne les carte et si commpte rond jouer cette combinaison)
            
            # si plus assez de point pour jouer une carte essayer de posé les items pieges
            
            # si la boucle atteint ce niveau lancer l'action (si rien n'est jouer passer le tour) 
            
            
        else:
            maxBest=0
            choice = [] 
            for card in self.draft:
                bestCalc=card.ratio
                if bestCalc > maxBest:
                    maxBest = bestCalc
                choice.append(bestCalc)
            self.pipe.append("PICK " + str(choice.index(maxBest)))


    # realise les actions 
    def act(self):
        self.g.log("in act")
        self.g.incTurn()
        command_line =  ";".join(map(str, self.pipe)) 
        self.pipe = []
        self.draft = []
        self.g.getPlayer(self.g.getPlayerTypeId("enemy")).reset()
        self.g.getPlayer(self.g.getPlayerTypeId("player")).reset()
        self.g.log(command_line,"command_line")
        if(len(command_line) == 0):
            print("PASS")
        else:
            print(command_line)
        

g = GameLegendOfCodeAndMagic(cards,OPTIONS)
brain=OODA(g)  

while True:
    brain.observe()
    brain.decide()
    brain.act()
