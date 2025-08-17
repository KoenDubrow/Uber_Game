import datetime
from enum import Enum
import random
import math
import time
# class syntax
class Vertex(Enum):
    A = 1
    B = 2
    C = 3

class SymetrixUberGame:
    def __init__(self,drivers,clients):
        self.drivers = drivers;
        self.clients = clients;

    #Iterates untill every agent has chosen best responce
    def Find_NE(self,state,epsilon):
        it = 1;
        while (not(self.isNE(state,epsilon))) & (it < 500):
            print(str(it) + str(state))
            it += 1;
            if (self.Best_A(state,epsilon) == Vertex.B):
                print(" A to B");
                state = [state[0]-1,state[1]+1,state[2]];
            elif (self.Best_A(state,epsilon) == Vertex.C):
                print("A to C");
                state = [state[0]-1,state[1],state[2]+1];
            elif (self.Best_B(state,epsilon) == Vertex.A):
                print("B to A");
                state = [state[0]+1,state[1]-1,state[2]];
            elif (self.Best_B(state,epsilon) == Vertex.C):
                print("B to C");
                state = [state[0],state[1]-1,state[2]+1];
            elif (self.Best_C(state,epsilon) == Vertex.B):
                print("C to B")
                state = [state[0],state[1]+1,state[2]-1];
            elif (self.Best_C(state,epsilon) == Vertex.A):
                print("C to A")
                state = [state[0]+1,state[1],state[2]-1];
            else:
                print("self stopper!!!!!!!")
                break
            #print(str(state[0])+","+str(state[1])+","+str(state[2]));
        return state;

    #counts How many NE occur for a given epsilon
    def countNE(self,epsilon):
        count = 0;
        for a in range(self.drivers + 1):
            for b in range (self.drivers + 1-a):
                x = [a,b,self.drivers-(a+b)]
                if (self.isNE(x,epsilon)):
                    count += 1;
        return count;

    #Best Responce of a car at A
    def Best_A(self,state,epsilon):
        if (state[0] == 0):
            return Vertex.A;
        bestPayoff = max(self.U_A(state,epsilon),self.U_B([state[0]-1,state[1]+1, state[2]],epsilon), self.U_C([state[0]-1,state[1], state[2]+1],epsilon))
        if (self.U_A(state,epsilon) == bestPayoff):
            return Vertex.A;
        elif (self.U_B([state[0]-1,state[1]+1, state[2]],epsilon) == bestPayoff):
            return Vertex.B;
        elif (self.U_C([state[0]-1,state[1], state[2]+1],epsilon) == bestPayoff):
            return Vertex.C;

    #Best Responce of a car at B
    def Best_B(self,state,epsilon):
        if (state[1] == 0):
            return Vertex.B;
        bestPayoff = max(self.U_B(state,epsilon),self.U_A([state[0]+1,state[1]-1, state[2]],epsilon), self.U_C([state[0],state[1]-1, state[2]+1],epsilon))
        if (self.U_B(state,epsilon) == bestPayoff):
            return Vertex.B;
        elif (self.U_A([state[0]+1,state[1]-1, state[2]],epsilon) == bestPayoff):
            return Vertex.A;
        elif(self.U_C([state[0],state[1]-1, state[2]+1],epsilon) == bestPayoff):
            return Vertex.C;

    #Best Responce of a car at C
    def Best_C(self,state,epsilon):
        if (state[2] == 0):
            return Vertex.C;
        bestPayoff = max(self.U_C(state,epsilon),self.U_A([state[0]+1,state[1], state[2]-1],epsilon), self.U_B([state[0],state[1]+1, state[2]-1],epsilon))
        if (self.U_C(state,epsilon) == bestPayoff):
            return Vertex.C;
        elif (self.U_A([state[0]+1,state[1], state[2]-1],epsilon) == bestPayoff):
            return Vertex.A;
        elif (self.U_B([state[0],state[1]+1, state[2]-1],epsilon) == bestPayoff):
            return Vertex.B;
    
#Payoff of players at A given a certain state
    def U_A(self,state,epsilon):
        return 1/2*self.Pr1_A(state)+1/2*(1-2*epsilon)*self.Pr2_A(state);

    #Payoff of players at B given a certain state
    def U_B(self,state,epsilon):
        return 1/2*self.Pr2_B(state)+1/2*(1-2*epsilon)*self.Pr1_B(state);

    #Payoff of players at C given a certain state
    def U_C(self,state,epsilon):
        return 1/2*(1-epsilon)*self.Pr1_C(state)+1/2*(1-epsilon)*self.Pr2_C(state);

    #Probability of Cars at A obtaining client given they go to A
    def Pr1_A(self,state):
        if state[0]<= self.clients:
            return 1;
        else:
            return self.clients/state[0];

    #Probability of Cars at B obtaining client given they go to A
    def Pr1_B(self,state):
        if state[0]+state[2]>=self.clients:
            return 0;
        elif (self.clients-(state[0]+state[2])) >= state[1]:
            return 1;
        else:
            return (self.clients-(state[0]+state[2]))/state[1];

    #Probability of Cars at C obtaining client given they go to A
    def Pr1_C(self,state):
        if state[0]>= self.clients:
            return 0;
        elif self.clients -state[0]>=state[2]:
            return 1;
        else:
            return (self.clients - state[0])/state[2];

    #Probability of Cars at A obtaining client given they go to B
    def Pr2_A(self,state):
        return self.Pr1_B([state[1],state[0],state[2]]);

    #Probability of Cars at B obtaining client given they go to B
    def Pr2_B(self,state):
        return self.Pr1_A([state[1],state[0],state[2]]);

    #Probability of Cars at C obtaining client given they go to B
    def Pr2_C(self,state):
        return self.Pr1_C([state[1],state[0],state[2]]);

    #Evaluates if each car is responding best
    def isNE(self,state,epsilon):
        return (Vertex.A == self.Best_A(state,epsilon)) & (Vertex.B == self.Best_B(state,epsilon)) & (Vertex.C == self.Best_C(state,epsilon))

    #Iterates Through posssible values of epsilon and attemps to find an NE by taking steps
    def NESearch(self,startingState):
        epsilon = 0.05;
        ret = ""
        while(epsilon<0.5):
            y=self.Find_NE(startingState);
            if (self.isNE(y)):
                ret += str(epsilon)[0:4] + " & "+ str(self.drivers) + "&" + str(self.clients) +"&"+str(startingState) + " & " + str(y) + "& ["+str(U_A(y))[0:5]+", "+ str(U_B(y))[0:5] + ", " + str(U_C(y))[0:5] + "] \\\\ \hline \n";
            epsilon += 0.05
        return ret;

    #Brute forces all possible combinations and evaluates if it is an NE.
    #Will return a count of all NE given a value of epsilon
    def FindAllNE(self,epsilon):
        count = 0;
        for a in range(self.drivers + 1):
            for b in range (self.drivers + 1-a):
                x = [a,b,self.drivers-(a+b)]
                if (self.isNE(x,epsilon)):
                    count += 1;
        return count

    #Iterates over several values of Epsilon, Prints How many NE given these values
    def CountNEPossible(self,step):
        res = []
        for e in range(step):
            epsilon = (e+1)/(2*step);
            res.append([epsilon,self.countNE(epsilon)]);
            #print(str(epsilon) + " & " + str(self.countNE(epsilon)));
        return res;

    #Iterates over several values of Epsilon, Gives a list of NE counts at each index index i->epsilon=(i+1)/(2step)
    def CountNEPossibleList(self,step):
        counts = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            counts.append(self.countNE(epsilon));
        return counts
    
    def getRangeOfNoNE(self,step):
        counts = self.CountNEPossibleList(step);
        foundMin = False;
        i = 0
        while (not foundMin) & (i < step):
            if counts[i] == 0:
                min = (i+1)/(2*step);
                foundMin = True;
            i += 1;
        if not foundMin:
            return (0.5,0.5);
        foundMax = False;
        i = 0;
        while (not foundMax):
            if counts[(step-1)-i] == 0:
                max = ((step)-i)/(2*step);
                foundMax = True;
            i += 1;
        return (min,max);
    #Returns all NE for given epsilon
    def getNE(self,epsilon):
        NashE = [];
        for b in range(self.drivers + 1):
            for c in range (self.drivers + 1-b):
                x = [self.drivers-(b+c),b,c]
                if (self.isNE(x,epsilon)):
                    NashE.append(x);
        return NashE

    #Get all possible distrubution:
    def getPositions(self):
        positions = [];
        for c in range(self.drivers+1):
            for b in range (self.drivers+1-c):
                x = [self.drivers-(b+c),b,c]
                positions.append(x);
        return positions;

    #C counts distribution of all NE
    def cDistNE(self,step):
        NE = self.getAllNE(step);
        cDist = [];
        for i in range(self.drivers+1):
            count = 0;
            for arr in NE:
                if arr[2] == i:
                    count += 1
            cDist.append(count);
        return cDist;

    def cDistNECherryPicked(self,step):
        cDist = self.cDistNE(step);
        for i in range(self.drivers+1):
            if (i != 1) & (i != 2) & (i != 3):
                cDist[i] = cDist[i]/step;
        return cDist;

    #(|a-b|) counts distribution of all NE
    def aSymDistNE(self,step):
        NE = self.getAllNE(step);
        aSymDist = [];
        for i in range(self.drivers+1):
            count = 0;
            for arr in NE:
                if abs(arr[0]-arr[1]) == i:
                    count += 1
            aSymDist.append(count);
        return aSymDist;

    def aSymDistNECherryPicked(self,step):
        aSym = self.aSymDistNE(step);
        for i in range(self.drivers+1):
            if (i != 5) & (i != 7) & (i != 9):
                aSym[i] = aSym[i]/step;
        return aSym;

    #All NE found iterating over step uniform epsilon values
    def getAllNE(self,step):
        NE = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            NE += self.getNE(epsilon);
        return NE

    #NE associated w each epsilon
    def getALLNEwEps(self,step):
        NE = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            NE.append([epsilon,self.getNE(epsilon)]);
        return NE
    
    #Given a set of NE will return the smalled mode vertex counts of them all
    def minmaxNE(self,epsilon):
        NE = self.getNE(epsilon);
        mi = math.inf;
        for i in NE:
            mi = min(max(i[0],i[1],i[2]),mi);
        return mi
    
    #Gets the geometric mean of the vertex Counnts
    def geoMean(self,ne):
        return math.pow(ne[0]*ne[2]*ne[2],0.333)
    #get the minmaxNE associated with each epsilon values:
    def epsWMinMaxNE(self,step):
        NE = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            NE.append([epsilon,self.minmaxNE(epsilon)]);
        return NE
    
    def epsWGeoMeanNE(self,step):
        NE = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            data = self.getNE(epsilon);
            for i in range(len(data)):
                data[i] = self.geoMean(data[i]);
            NE.append([epsilon,data]);
        return NE
    
    def epsWSDNE(self,step):
        NE = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            data = self.getNE(epsilon);
            for i in range(len(data)):
                data[i] = self.getSDOfState(data[i]);
            NE.append([epsilon,data]);
        return NE
    
    def epsWExpWaitAve(self,step):
        NE = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            data = self.getNE(epsilon);
            l = len(data);
            if l != 0:
                ave = 0;
                for i in range(l):
                    ave += (self.expWaitTime(data[i],epsilon))/epsilon
                NE.append([epsilon,ave/l]);
        return NE
    
    #Potential function candidate
    def potentialFuncSummedProbs(self,state,epsilon):
        a = 0.5*(self.Pr1_A(state)+(1-(2*epsilon))*self.Pr1_B(state)+(1-epsilon)*self.Pr1_C(state));
        b = 0.5*((1-(2*epsilon))*self.Pr2_A(state)+self.Pr2_B(state)+(1-(2*epsilon))*self.Pr2_C(state));
        return a+b;

    def potentialFuncProbA(self,state,epsilon):
        return self.Pr1_A(state)+self.Pr2_A(state);

    #Applies potential function to state;
    def matchStateWPF(self,state,v,epsilon):
        return [state,v(state,epsilon)];

    def getVOfAllState(self,epsilon,v):
        pos = self.getPositions();
        data = "";
        for i in pos:
            data += str(self.matchStateWPF(i,v,epsilon))+str(self.isNE(i,epsilon)) + "\n";
        return data;

    def getVAroundNE(self,epsilon,v,Ne):
        inf = [Ne,[Ne[0]-1,Ne[1]+1,Ne[2]],[Ne[0]-1,Ne[1],Ne[2]+1],[Ne[0]+1,Ne[1]-1,Ne[2]],[Ne[0],Ne[1]-1,Ne[2]+1],
                [Ne[0]+1,Ne[1],Ne[2]-1],[Ne[0],Ne[1]+1,Ne[2]-1]
        ]
        
        data = "";
        for i in inf:
            data += str(self.matchStateWPF(i,v,epsilon))+str(self.isNE(i,epsilon)) + "\n";
        return data;
    #Driver based desirability eval:
    def evalDriverDes(self,state,epsilon):
        return (state[0]/self.drivers)*self.U_A(state,epsilon) + (state[1]/self.drivers)*self.U_B(state,epsilon) + (state[2]/self.drivers)*self.U_C(state,epsilon);

    def payoffDiff(self,state,epsilon):
        ma = 0;
        mi = 1;
        if state[0]!=0:
            ma = max(ma,self.U_A(state,epsilon));
            mi = min(mi,self.U_A(state,epsilon));
        if state[1]!=0:
            ma = max(ma,self.U_B(state,epsilon));
            mi = min(mi,self.U_B(state,epsilon));
        if state[2]!=0:
            ma = max(ma,self.U_C(state,epsilon));
            mi = min(mi,self.U_C(state,epsilon));
        return ma-mi;

    #Returns maximum time a costumer should expect to wait
    def maxWaitTime(self,state,epsilon):
        a = 0;
        b = 0;
        i = -1;
        cars = 0;
        while cars < self.clients:
            i += 1;
            cars += state[i];
        a = i*epsilon;
        i = -1;
        cars = 0;
        while cars < self.clients:
            i += 1;
            cars += state[2-i];
        b = i*epsilon;
        return max(a,b);

    #Returns expected wait time
    def expWaitTime(self,state,epsilon):
        if (self.clients > self.drivers):
            return math.inf;
        aT = 0;
        bT = 0;
        i = -1;
        cars = 0;
        statep = [state[0],state[2],state[1]]
        while cars < self.clients:
            i += 1;
            if (cars + statep[i]>= self.clients):
                aT += (self.clients - cars) * i * epsilon;
            else:
                aT += statep[i] * i * epsilon;
            cars += statep[i];
        i = -1;
        cars = 0;
        while cars < self.clients:
            i += 1;

            if (cars + statep[2-i]>= self.clients):
                bT += (self.clients - cars) * i * epsilon;
            else:
                bT += statep[2-i] * i * epsilon;
            cars += statep[2-i];
        return (aT+bT)/(2*self.clients);
    #Returns evaluation of most desirable state for drivers
    def getBestCaseMetric(self,epsilon,ev):
        positions = self.getPositions();
        best = ev(positions[0],epsilon);
        for pos in positions:
            m = ev(pos,epsilon);
            if best > m:
                best = m;
        return best;

    #Returns most ideal casses
    def getBestCases(self,epsilon,ev):
        best = self.getBestCaseMetric(epsilon,ev);
        positions = self.getPositions();
        bestPositions = [];
        for pos in positions:
            if best == ev(pos,epsilon):
                bestPositions.append(pos);
        return bestPositions;

    #return price of anarchy with given social cost
    def pOA(self,epsilon,ev):
        NE = self.getNE(epsilon);
        best = self.getBestCaseMetric(epsilon,ev);
        if len(NE) == 0:
            return 0;
        worst = ev(NE[0],epsilon);
        for pos in NE:
            worst = max(worst,ev(pos, epsilon));
        if best == 0:
            if worst == 0:
                return 0;
            else:
                return math.inf;
        return worst / best;

    def POADrivers(self,epsilon):
        return self.pOA(epsilon,self.evalDriverDes);

    def POAEpectedWait(self,epsilon):
        return self.pOA(epsilon,self.expWaitTime);

    def POAOverLength(self,step,ev):
        data = (self.POAOverLengthTable(step,ev));
        POA = 0;
        for d in data:

            POA = max(d[1],POA);
        return POA;

    def POAOverLengthTable(self,step,ev):
        POA = [];
        for e in range(step):
            epsilon = (e+1)/(2*step);
            POA.append([epsilon,self.pOA(epsilon,ev)])
        return POA;

    def makeTable(self,steps, distFunc):
        ret = "";
        for s in steps:
            ret += str(s) + " steps &";
            data = distFunc(s);
            for i in range(self.drivers+1):
                if i!= self.drivers:
                    ret += str(data[i]) + "&";
                else:
                    ret += str(data[i])
            ret+= "\\\\ \hline \n "
        return ret;

    def getAllNEVCount(self,v,val,step):
        i = v.value - 1;
        NE = self.getAllNE(step);
        filt = [];
        for n in NE:
            if n[i] == val:
                filt.append(n);
        return filt;

    def getSDOfState(self,state):
        m = self.drivers/3;
        sum = (state[0]-m)**2+(state[1]-m)**2+(state[2]-m)**2;
        return math.sqrt(1/10*sum)

    def __str__(self):
        return "d" + str(self.drivers) + "c" + str(self.clients);

    def set(self,c,d):
        self.clients = c;
        self.drivers = d;

#Tests from base games and games within driver and client range according to steps
def gamesNoEpsilonRangeGrid(gameBase,driverRange,clientsRange,driverStep,clientsStep):
    d = gameBase[0];
    c = gameBase[1];
    data = [];
    while (d <= driverRange):
        while (c <= clientsRange):
            game = SymetrixUberGame(d,c);
            data.append([d,c,game.getRangeOfNoNE(100)]);
            c += clientsStep
        c = gameBase[1];
        d += driverStep
    return data;

#Tests from base game up to driver range moving clients up by jump and drivers by 2jump
def gamesNoEpsilonRange2d_d(gameBase,driversRange,jump):
    d = gameBase[0];
    c = gameBase[1];
    data = [];
    while (d <= driversRange):
        game = SymetrixUberGame(d,c);
        data.append([d,c,game.getRangeOfNoNE(100)]);
        c += jump;
        d += 2*jump;
    return data;

#Predicts and tests the value for which we expect the minimum of our epsilon range for no NE to be
def predictNE(game,step):
    c = game.clients;
    d = game.drivers;
    real = game.getRangeOfNoNE(step)[0];
    cStar = 2*c - d + 1;
    q = (4*cStar)/(cStar-1);
    pred = -1/(q*(c-(d/2)))+(1/2);
    pred = (2*c-d)/(4*c-2*d+2)
    return [real,pred,(real-pred)]

def testPredict(drange,step,n):
    s = 0;
    f = 0;
    for i in range(n):
        d = random.randrange(drange[0],drange[1]+1);
        if (d%2==0):
            l = int(d/2+1);
        else:
            l =int((d+1)/2);
        c = random.randrange(l,d-1);
        game = SymetrixUberGame(d,c);
        data = predictNE(game,step);
        if data[2]<=1/(2*step):
            s += 1;
            print(str(game) + " passed with " + str(data));
        else:
            f += 1;
            print(str(game) + " failed with " + str(data));
    return [s,f,s/n];

#Tests from base games and games within driver and client range according to steps for POA
def gamesGridTestPOA(gameBase,driverRange,clientsRange,driverStep,clientsStep):
    d = gameBase[0];
    c = gameBase[1];
    data = [];
    while (d <= driverRange):
        while (c <= clientsRange):
            game = SymetrixUberGame(d,c);
            data.append([d,c,game.POAOverLength(100,game.expWaitTime)]);
            c += clientsStep
        c = gameBase[1];
        d += driverStep
    return data;

def latexTabulate(data):
    ret = "";
    print(data);
    for d in data:
        t = 0;
        for i in d:
            if t!= len(d)-1:
                ret += str(i) + "&";
            else:
                ret += str(i)
            t +=1;
        ret+= "\\\\ \hline \n "
    return ret;
#print(str(gamesNoEpsilonRange2d_d((6,5),25,1)))

def EpsilonNEPlot(game,f,step):
    file = open(f,"a");
    file.write(f"began at time {datetime.datetime.now()}\n");
    file.write(f"drivers: {game.drivers}, clients: {game.clients}, step {step}\n");
    res = game.CountNEPossible(step);
    prnt = "";
    cnt = 0;
    st = time.time();
    for i in res:
        prnt += f"({i[0]},{i[1]})"
        cnt += 1;
        if cnt == 10:
            prnt += "\n";
            cnt = 0;
    file.write(prnt);
    file.write(f"\nlog complete\ntime: {time.time()-st}\n_______________________________________________________________\n")
    file.close();

def gamPlot(game,f,eps):
    file = open(f,"a");
    file.write(f"began at time {datetime.datetime.now()}\n");
    file.write(f"experiment match gamma to s_1, drivers: {game.drivers}, clients: {game.clients}, epsilon {eps}\n");
    prnt = "";
    cnt = 0;
    st = time.time();
    d = game.drivers;
    for i in range(d+1):
        prnt += f"({i},{game.U_A([i,math.floor((d-i)/2),math.ceil((d-i)/2)],eps)})"
        cnt += 1;
        if cnt == 10:
            prnt += "\n";
            cnt = 0;
    file.write(prnt);
    file.write(f"\nlog complete\ntime: {time.time()-st}\n_______________________________________________________________\n")
    file.close();

def predTab(f,tCount):
    file = open(f,"a");
    file.write(f"began at time {datetime.datetime.now()}\n");
    file.write(f"experiment to test prediction\n");
    st=time.time();
    for i in range(tCount):
        c = random.randint(2,100);
        d = c + random.randint(1,c-1);
        game = SymetrixUberGame(d,c);
        pred = predictNE(game,200);
        file.write(f"\hline {c}&{d}&{pred[0]}&{pred[1]}&{pred[2]}")
        if pred[2] < 0 or pred[2] > 0.0025:
            file.write(f"***")
        file.write(r"\\" + f"\n")
        print(i)
    file.write(f"\nlog complete\ntime: {time.time()-st}\n_______________________________________________________________\n")
    file.close();


#game = SymetrixUberGame(10,6);

predTab(r"C:\Users\koend\Documents\AGT Code\experiments\bound_data.txt",50)

#gamPlot(game,r"C:\Users\koend\Documents\AGT Code\experiments\gamma_w_s_1.txt",0);
#for i in range(5):
#    e = (i+1)/10;
#    gamPlot(game,r"C:\Users\koend\Documents\AGT Code\experiments\gamma_w_s_1.txt",e);



#for i in range(5):
#    c = random.randint(2,15);
#    d = random.randint(1,c-1);
#    game = SymetrixUberGame(c+d,c);
#    EpsilonNEPlot(game,r"C:\Users\koend\Documents\AGT Code\experiments\dependant_rand_NE_count.txt",200);



#print(game.getNE(0.3));
#print((game.getVAroundNE(0.3,game.payoffDiff,[3,5,2])));
#game.Find_NE([11,0,0],0.48)
#print(str(testPredict((5,100),1000,50)))
#print(str(game.getRangeOfNoNE(10000)))

#print((1-(math.sqrt(133)-11)/6))
#print()