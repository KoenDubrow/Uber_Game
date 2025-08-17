import math
import random
import time
import datetime;

class StarGame:
    def __init__(self,dist,drivers,n,epsilon):
        self.dist = dist;
        self.drivers = drivers;
        self.n = n;
        self.epsilon = epsilon;
    
    def initialize(self,centre,clients = []):
        if clients == []:
            for j in range(self.n):
                clients.append(self.dist.roll());
        return StarGameState(clients,self.drivers,centre,self.n,self.epsilon)    

    def dataforPotential(self,trials):
        f = [];
        g = [];
        for i in range(self.drivers + 1):
            f.append(0);
            g.append(0);
        customer = [];
        for j in range(self.n):
            customer.append(0);
        for i in range(trials):
            for j in range(self.n):
                customer[j] = self.dist.roll();
            setting = self.initialize(0,customer);
            for j in range(self.drivers + 1):
                d = setting.fastAvePayoff();
                setting.bumpDriver();
                f[j] += d[0]/trials;
                g[j] += d[1]/trials;
        #print(f"f: {f}\n g: {g}\n g total is {sum(g)}" )
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
        print(f"g {g}")
        return v;

    def findLocalMin(self,data):
        v = data;
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
        cnt = 0;
        for i in range(len(terminal)):
            if totalCust == 0:
                break;
            elif terminal[i] == 0:
                cnt += 1;
                terminal[i]=1-(2*self.epsilon);
                totalCust += -1;
        return [terminal,centre];

    def fastAvePayoff(self):
        terminal = 0;
        remainingTermDriver = 0;
        localClients = self.clients;
        #print(localClients);
        remClients = 0;
        terminalDrivers = [];
        terminalDriversBase = (self.drivers - self.centre)//self.n;
        terminalDriversR = (self.drivers - self.centre) % self.n;
        for i in range(self.n):
            add = terminalDriversBase;
            if i < terminalDriversR:
                add += 1;
            terminalDrivers.append(add);
        #First round drivers on terminals acrue clients at these terminals
        for i in range(len(localClients)):
            p = min(localClients[i],terminalDrivers[i]);
            remClients += (localClients[i]-p);
            remainingTermDriver += (terminalDrivers[i] - p);
            terminal += p
        #Drivers at centre pick off any remianing drivers
        p = min(remClients,self.centre);
        centre = p*(1-self.epsilon);
        remClients += -p;
        #Drivers at terminals that missed a driver before pick off any remaining clients
        p = min(remClients,remainingTermDriver);
        terminal += p*(1-2*self.epsilon);
        #print(self)
        if self.centre == 0:
            return [terminal/self.drivers,0];
        if self.centre == self.drivers:
            return [0,centre/self.centre];
        return [terminal/(self.drivers-self.centre),centre/self.centre]


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

    def __str__(self):
        return(f"clients: {self.clients}, driers: {self.drivers}, cars at centre: {self.centre}, terminals: {self.n}, epsilon: {self.epsilon}, total clients: {self.totalClients}")

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
    def __init__(self,indexOfVar,fixed,varBounds,varStep,mult,filename,trials):
        self.indexOfVar = indexOfVar;
        self.fixed = fixed;
        self.varBounds = varBounds;
        self.varStep = varStep;
        self.mult = mult;
        self.pSpace = [];
        self.tResults = [];
        self.f = open(filename,"a");
        self.trials = trials;
        self.f.write("""key: #0 - binom mean
     #1 - binom var factor
     #2 - drivers
     #3 - terminals
     #4 - epsilon\n""")
        self.f.write(f"began at time {datetime.datetime.now()}\n")
        self.f.write(f"i.v: #{self.indexOfVar} from {self.varBounds[0]} to {self.varBounds[1]} {"multiplying" if self.mult else "adding"} with step of {self.varStep}\nc.v: {self.fixed} run over {trials} trials\n")
        for i in range(5):
            if i == self.indexOfVar:
                self.pSpace.append(varBounds[0]);
            else:
                self.pSpace.append(fixed[0]);
                fixed.pop(0);
        self.startTime = time.time();

    def test(self):
        if self.tResults != []:
            return;
        i = self.varBounds[0];
        self.tResults = [];
        cnt = True;
        while cnt:
            print(i);
            if i>=self.varBounds[1]:
                cnt = False;
            self.pSpace[self.indexOfVar] = i;
            game = StarGame(binomFixedMean(self.pSpace[0],self.pSpace[1]),
                            self.pSpace[2],self.pSpace[3],self.pSpace[4]);
            self.tResults.append([i,game.findNE(self.trials)]);
            del game;
            if self.mult:
                i = i*self.varStep;
            else:
                i += self.varStep;

    #varVal & Z@NE1, Z@NE2, ...
    def resultsSimple(self):
        self.test();
        self.f.write("data:\n")
        prnt = "";
        for i in self.tResults:
            for j in i[1]:
                prnt += f"({i[0]},{j[0]})"
            prnt +="\n"
        self.f.write(prnt);
        self.f.write(f"\nlog complete\ntime: {time.time()-self.startTime}\n_______________________________________________________________\n")
        self.f.close();
#0 - binom mean
#1 - binom var factor
#2 - drivers
#3 - terminals
#4 - epsilon


t1 = time.time()
print(StarGame(binomFixedMean(1,1000),100,47,0).findNE(5000));
#TestNE(3,[1,1000,100,0.5],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\epsln_exp_1.txt",5000).resultsSimple();
t2 = time.time()
print('Total elapsed time: {} seconds'.format((t2 - t1)))
#r"C:\Users\koend\Documents\AGT Code\experiments\exp_1_raw_data.txt"
