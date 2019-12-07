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
        self.lastPos = Pos(getattr(self, 'x', None), getattr(self, 'x', None), getattr(self, 'x', None))
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

    def setPlayer(self, player):
        self.players.append(player)

    def getPlayer(self, id):
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

    def addtoarray(self, arrayname, value):
        self[arrayname].append(value)

    def deltoarray(self, arrayname, value):
        self[arrayname].pop(self[arrayname].index(value))

    def addActionToLog(self, playerId, turn, logmsg):
        self.actionLog[playerId].append((turn, logmsg))

    def getActionLog(self, playerId=None, turn=None):
        if playerId is None:
            playerScope = (0, len(self.players))
        else:
            playerScope = (playerId, PlayerId)
        for i in range(playerScope):
            if turn is None:
                turnScope = (0, len(self.actionLog[i]))
            else:
                turnScope = (turn, turn)
            for j in range(turnScope):
                for k in range(len(self.actionLog[i])):
                    if self.actionLog[i][0] == j:
                        self.log(self.actionLog[i][1], "player "+str(i) + " turn " + str(j))

    def setTurn(self, turn):
        self.turn = turn

    def getTurn(self):
        return self.turn

    def incTurn(self, step=1):
        self.turn += step

    def GetAllUniqueCombinations(self, arr):
        return [itertools.combinations(arr, r) for r in range(len(arr)+1)]


class Card:
    def __init__(self, cardListId, instanceId, cardType, cost, attack, defense, abilities="------"):
        self.alive = True
        self.cardListId = cardListId
        self.instanceId = instanceId
        self.cardType = cardType
        self.cost = cost
        self.attack = attack
        self.defense = defense
        self.abilities = abilities
        self.bonus = 0
        if self.abilities[0] == "B":
            self.bonus += 1
        if self.abilities[1] == "C":
            self.bonus += 2
        if self.abilities[2] == "D":
            self.bonus += 2
        if self.abilities[3] == "G":
            self.bonus += 2
        if self.abilities[4] == "L":
            self.attack += 20
        if self.abilities[5] == "D":
            self.bonus += 2
        if cardType == 0:
            self.ratio = (((attack + defense + bonus) - cost) / (attack + defense + cost)) * 100
        else:
            self.ratio = 1

    def dealDamage(self, dmg):
        self.defense -= dmg
        if self.defense <= 0:
            self.alive = False

    def getStat(self, stat):
        return self.__dict__[stat]

    def setStat(self, stat, newValue):
        self.__dict__[stat] = newValue

    def __repr__(self):
        return(f'id:{self.cardListId}, instanceId:{self.instanceId}, cost:{self.cost},cardtype:{self.cardtype} , attack:{self.attack} , defense:{self.defense}  ')


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

    def update(self, id, type, health, mana, deck, rune, draw, x=None, y=None, z=None):
        super().update(id, type,  x, y, z, params={})
        self.health = health
        self.mana = mana
        self.deck = deck
        self.rune = rune
        self.draw = draw

    def addToBoard(self, card):
        self.board.append(card)

    def addToHand(self, card):
        self.hand.append(card)

    def delToBoard(self, instanceId):
        for i in range(len(self.board)):
            if self.board[i].getStat("instanceId") == instanceId:
                self.board[i].alive = False
                return

    def delToHand(self, instanceId):
        for i in range(len(self.hand)):
            if self.hand[i].getStat("instanceId") == instanceId:
                self.hand[i].alive = False
                return

    def getHandCount(self):
        return len(self.hand)

    def reset(self):
        self.hand = []
        self.board = []


class GameLegendOfCodeAndMagic(Game):
    def __init__(self, option={}):
        super().__init__(option)
        self.playerId = 0
        self.enemyId = 1

    def getPlayerTypeId(self, who):
        if who == "player":
            return self.playerId
        if who == "enemy":
            return self.enemyId

    def setPlayerTypeId(self, who, id):
        self[who + "Id"] = id


class ODA:
    # https://fr.wikipedia.org/wiki/Boucle_OODA
    def __init__(self, g):
        self.g = g
        self.pipe = []
        self.draft = []

    def calcBestCombo(self, c, mana):
        couples = []
        for i in range(1, len(c)+1):
            couples += itertools.combinations(c, i)

        costarr = []
        for couple in couples:
            costarr.append(self.cost_sum(couple))
        couples = list(couples)
        for j in range(mana):
            for k in range(len(costarr)):
                if costarr[k] == (mana - j):
                    return couples[k]
        return []

    def cost_sum(self, cards):
        cost = 0
        for card in cards:
            if card.cardType > 0:
                cost += card.cost + 10
            else:
                cost += card.cost
        return cost

    def observe(self):
        self.g.log("in observe")
        for i in range(2):
            player_health, player_mana, player_deck, player_rune, player_draw = [int(j) for j in input().split()]
            self.g.players[i].update(i, "player", player_health, player_mana, player_deck, player_rune, player_draw)
        opponent_hand, opponent_actions = [int(i) for i in input().split()]
        for i in range(opponent_actions):
            card_number_and_action = input()
            self.g.addActionToLog(g.getPlayerTypeId("enemy"), g.getTurn(), card_number_and_action)
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
            if self.g.getTurn() < 30:
                self.draft.append(Card(card_number, instance_id, card_type, cost, attack, defense))
            else:
                if location == 0:
                    self.g.getPlayer(self.g.getPlayerTypeId("player")).addToHand(Card(card_number, instance_id, card_type, cost, attack, defense, abilities))
                elif location == 1:
                    self.g.getPlayer(self.g.getPlayerTypeId("player")).addToBoard(Card(card_number, instance_id, card_type, cost, attack, defense, abilities))
                elif location == -1:
                    self.g.getPlayer(self.g.getPlayerTypeId("enemy")).addToBoard(Card(card_number, instance_id, card_type, cost, attack, defense, abilities))

    def decide(self):
        """decide des actions a mener et dans quel ordre
           stock les resultat attendu dans le pipe """
        self.g.log("in decide")
        if int(self.g.getTurn()) > 29:
            myBoard = self.g.getPlayer(self.g.getPlayerTypeId("player")).board
            myboardCount = len(myBoard)
            myHand = self.g.getPlayer(self.g.getPlayerTypeId("player")).hand
            myCurrentMana = self.g.getPlayer(self.g.getPlayerTypeId("player")).mana
            advboard = self.g.getPlayer(self.g.getPlayerTypeId("enemy")).board
            # boucle sur les cartes du board
            if myboardCount > 0:
                for advcard in advboard:
                    if advcard.abilities[3] == "G":
                        for mycard in myBoard:
                            if advcard.alive is True:
                                if mycard.abilities[3] != "G":
                                    self.pipe.append("ATTACK " + str(mycard.instanceId) + " " + str(advcard.instanceId))
                                    self.g.getPlayer(self.g.getPlayerTypeId("player")).delToBoard(mycard.instanceId)
                                    advcard.dealDamage(mycard.attack)
                                    if advcard.alive is False:
                                        break

                for mycard in myBoard:
                    if mycard.alive is True:
                        for advcard in advboard:
                            if advcard.alive is True:
                                if mycard.ratio < advcard.ratio and mycard.attack >= advcard.defense:
                                    self.pipe.append("ATTACK " + str(mycard.instanceId) + " " + str(advcard.instanceId))
                                    self.g.getPlayer(self.g.getPlayerTypeId("player")).delToBoard(mycard.instanceId)
                                    self.g.getPlayer(self.g.getPlayerTypeId("enemy")).delToBoard(advcard.instanceId)
                                    break
                        self.pipe.append("ATTACK " + str(mycard.instanceId) + " -1")
                        self.g.getPlayer(self.g.getPlayerTypeId("player")).delToBoard(mycard.instanceId)

            self.g.log(len(myHand))
            if len(myHand) > 0 and myboardCount < 6:
                combo = self.calcBestCombo(myHand, myCurrentMana)
                if len(combo) > 0:
                    for card in combo:
                        self.pipe.append("SUMMON " + str(card.instanceId))
                        if card.abilities[1] == "C":
                            cible = []
                            for advcard in advboard:
                                if advcard.abilities[3] == "G":
                                    cible.append(advcard)
                                    break
                            if len(cible) == 0:
                                self.pipe.append("ATTACK " + str(card.instanceId) + " -1")
                            else:
                                self.pipe.append("ATTACK " + str(card.instanceId) + " " + str(cible[0].insanceId))
                                cible[0].dealDamage(card.attack)
                        self.g.getPlayer(self.g.getPlayerTypeId("player")).delToHand(card.instanceId)
                        myCurrentMana -= card.cost
                        myboardCount += 1
                        if myboardCount == 6:
                            return  # le board est plein

            if myCurrentMana > 0 and myboardCount > 0:
                for card in myHand:
                    if card.cardType > 0 and card.cost <= myCurrentMana:
                        self.pipe.append("USE " + str(card.instanceId) + " " + str(myBoard[0].instanceId))
                        self.g.getPlayer(self.g.getPlayerTypeId("player")).delToHand(card.instanceId)
                        myCurrentMana -= card.cost

        else:
            maxBest = 0
            choice = []
            for card in self.draft:
                bestCalc = card.ratio
                if bestCalc > maxBest:
                    maxBest = bestCalc
                choice.append(bestCalc)
            self.pipe.append("PICK " + str(choice.index(maxBest)))

    def act(self):
        """realise les actions"""
        self.g.log("in act")
        self.g.incTurn()
        command_line = ";".join(map(str, self.pipe))
        self.pipe = []
        self.draft = []
        self.g.getPlayer(self.g.getPlayerTypeId("enemy")).reset()
        self.g.getPlayer(self.g.getPlayerTypeId("player")).reset()
        self.g.log(command_line, "command_line")
        if(len(command_line) == 0):
            print("PASS")
        else:
            print(command_line)

g = GameLegendOfCodeAndMagic(OPTIONS)
brain = ODA(g)

while True:
    brain.observe()
    brain.decide()
    brain.act()
