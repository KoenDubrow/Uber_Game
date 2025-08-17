import math
import random
import time
import numpy as np

#Butros idea
#Improvement - optimizing randomization.
#Less consistent results as a result

class StarGame:
    def __init__(self,dist,drivers,n,epsilon):
        self.dist = dist;
        self.drivers = drivers;
        self.n = n;
        self.epsilon = epsilon;
    
    def initialize(self,centre,clients):
        return StarGameState(clients,self.drivers,centre,self.n,self.epsilon)    

    def dataforPotential(self,trials):
        #establish lists for holding data
        f = [];
        g = [];
        for i in range(self.drivers + 1):
            f.append(0);
            g.append(0);
        customer = [];
        noise = [];
        #Establish source of random var
        for i in range(trials + self.n):
            noise.append(self.dist.roll());
        #Establish holder for instance of random var
        for j in range(self.n):
            customer.append(0);
        for i in range(trials):
            for j in range(self.n):
                customer[j] = noise[random.randrange(trials+self.n)];
            setting = self.initialize(0,customer);
            for j in range(self.drivers + 1):
                d = setting.avePayoffPlayout();
                setting.bumpDriver();
                f[j] += d[0]/trials;
                g[j] += d[1]/trials;
        return [f,g];

    def potentialFunc(self,trials):
        data = self.dataforPotential(trials);
        f = data[0];
        g = data[1];
        v = [];
        for i in range(self.drivers + 1):
            x = 0;
            for j in range(self.drivers + 1):
                if j < i:
                    x += f[j];
                elif j > i:
                    x += g[j];
            v.append(x);
        return v;

    def findLocalMin(self,data):
        v = data;
        print(v)
        old = 0;
        lpNE = False;
        x = [];
        for i in range(len(v)):
            if v[i] > v[old]:
                if lpNE:
                    x.append(old);
                lpNE = False;
                old = i;
            elif v[i] == v[old]:
                if lpNE:
                    x.append(old);
                lpNE = True;
                old = i;
            elif v[i] < v[old]:
                lpNE = True;
                old = i;
                if i == len(v)-1:
                    x.append(i)
        results = [];
        for i in x:
            results.append([i,v[i]])
        return results
    
    def findNE(self,trials):
        d = self.potentialFunc(trials);
        return self.findLocalMin(d);



class StarGameState:
    def __init__(self,clients,drivers,centre,n,epsilon):
        self.clients = clients;
        self.drivers = drivers;
        self.centre = centre;
        self.n = n;
        self.epsilon = epsilon;
        self.totalClients = sum(clients);
    
    def bumpDriver(self):
        self.centre += 1;
    
    #Will simulate the game and return payoffs
    #@Return (term,centre) term: the payoff for each car at a terminal centre: the payoff for each car at the centre
    def payoffPlayout(self):
        #Setup array for building output
        terminal = [];
        centre = []
        #setup array for exact edge distribution
        terminalDrivers = [];
        terminalDriversBase = (self.drivers - self.centre)//self.n;
        terminalDriversR = (self.drivers - self.centre) % self.n;
        for i in range(self.n):
            add = terminalDriversBase;
            if i < terminalDriversR:
                add += 1;
            terminalDrivers.append(add);
        #Plays out the first phase of collecting payoffs
        #And coleects how many costumers remain after the fact
        totalCust = 0;
        for i in range(len(self.clients)):
            localClients = self.clients[i];
            #print("beginning of loop, local cust = " + str(localClients) + " and " + str(terminalDrivers[i]) + "drivers")
            for j in range(terminalDrivers[i]):
                if localClients > 0:
                    terminal.append(1);
                    localClients += -1;
                else:
                    terminal.append(0);
            #print("there are " + str(localClients) + "unserviced customers from terminal " + str(i))
            totalCust += localClients;
        #print("in total " + str(totalCust) + " remain costumers")
        #Plays out the second phase
        for i in range(self.centre):
            if totalCust > 0:
                centre.append(1-self.epsilon);
                totalCust += -1;
            else:
                centre.append(0);
        #Plays out the final phase
        for i in terminal:
            if totalCust == 0:
                break;
            elif i == 0:
                i=1-2*self.epsilon;
                totalCust += -1;
        return [terminal,centre];

    def avePayoffPlayout(self):
        res = self.payoffPlayout();
        if len(res[1]) == 0:
            res[1] = 0;
        else:
            res[1] = sum(res[1])/len(res[1]);
        if len(res[0]) == 0:
            res[0] = 0;
        else:
            res[0] = sum(res[0])/len(res[0]);
        return (res[0],res[1]);

class binomFixedMean():
    def __init__(self,mean,varFactor):
        self.n = mean;
        self.p = 1;
        self.n = self.n*varFactor;
        self.p = self.p/varFactor;

    def roll(self):
        return random.binomialvariate(self.n,self.p)

class TestNE():
    #We consider the space of game as its parameter space indexed from 0 to 4 e.g.
    #0 - binom mean
    #4 - epsilon
    #We give the fixed values in order in list fixed skipping the varied
    #We vary the independant variable from varbounds[0] and increase by step until we exceed varBound[1]
    def __init__(self,indexOfVar,fixed,varBounds,varStep):
        self.indexOfVar = indexOfVar;
        self.fixed = fixed;
        self.varBounds = varBounds;
        self.varStep = varStep;
        self.pSpace = [];
        self.tResults = [];
        for i in range(5):
            if i == self.indexOfVar:
                self.pSpace.append(varBounds[0]);
            else:
                self.pSpace.append(fixed[0]);
                fixed.pop(0);

    def test(self,trials):
        if self.tResults != []:
            return;
        i = self.varBounds[0];
        self.tResults = [];
        while i <= self.varBounds[1]:
            print(i);
            self.pSpace[self.indexOfVar] = i;
            game = StarGame(binomFixedMean(self.pSpace[0],self.pSpace[1]),
                            self.pSpace[2],self.pSpace[3],self.pSpace[4]);
            self.tResults.append([i,game.findNE(trials)]);
            del game;
            i += self.varStep;

    #varVal & Z@NE1, Z@NE2, ...
    def resultsSimple(self,trials):
        self.test(trials);
        prnt = "";
        for i in self.tResults:
            prnt += str(i[0]) + " & ";
            for j in i[1]:
                prnt += str(j[0]) + ", "
            prnt += "\n";
        print(prnt);

    def resultsNECount(self,trials):
        self.test(trials);
        prnt = "";
        for i in self.tResults:
            prnt += str(i[0]) + " & " + str(len(i[1])) + "\\\\ \n";
        print(prnt);
#0 - binom mean
#1 - binom var factor
#2 - drivers
#3 - terminals
#4 - epsilon

#Run tomorrow morning before class
#TestNE(3,[5,1000,100,0],[1,150],1).resultsSimple(5000)
t1 = time.time()
for i in range(10):
    print(str(StarGame(binomFixedMean(5,1000),100,20,0).findNE(5000)));
t2 = time.time()
print('Elapsed time: {} seconds'.format((t2 - t1)))