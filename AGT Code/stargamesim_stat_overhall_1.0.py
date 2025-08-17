import math
import time
import datetime;
import random;

class Game:
    def __init__(self,dist,drivers,n,epsilon,error):
        self.cDist = dist;
        self.drivers = drivers;
        self.n = n;
        self.epsilon = epsilon
        self.error = error;
    
    def initState(self,centre):
        return GameState(self.cDist,self.drivers,centre,self.n,self.epsilon)    

    def dataforPotential(self):
        f = [];
        g = [];
        for i in range(self.drivers + 1):
            f.append(0);
            g.append(0);
        setting = self.initState(0);
        for j in range(self.drivers):
            d = setting.payouts(self.error);
            setting.bumpDriver();
            f[j] = d[0];
            g[j] = d[1];
        return [f,g];

    def potentialFunc(self):
        data = self.dataforPotential();
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
        #print(f"g {g}");
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
    
    def findNE(self):
        d = self.potentialFunc();
        
        return self.findLocalMin(d);

class GameState:
    def __init__(self,dist,drivers,centre,n,epsilon):
        self.cDist = dist;
        self.d = drivers;
        self.centre = centre;
        self.n = n;
        self.epsilon = epsilon;
        self.dDist = driverDist(self.d-self.centre,self.n);
    
    def bumpDriver(self):
        self.centre += 1;
        self.dDist = driverDist(self.d - self.centre,self.n);

    
    def payouts(self,error):
        #number of terminal drivers
        termD = self.d-self.centre;
        #print(f"drivers at term {termD}")
        failcount = max(0,self.d-(self.n*self.cDist.mean));
        #print(f"global failcount {failcount}")
        termP = 0;
        centP = 0;
        eTermFail1 = 0;
        if termD != 0:
            termSucc1Chance = self.calcTermSucc1Chance(error);
            #print(f"termSucc1Chance {termSucc1Chance}")
            eTermFail1 = (1-termSucc1Chance)*termD;
            #print(f"eTermFail1 {eTermFail1}")
            if eTermFail1 == 0:
                termFail3Chance = 0;
            else:
                termFail3Chance = min(1,failcount/eTermFail1)*(1-termSucc1Chance);
            #print(f"termFail3Chance {termFail3Chance}")
            termP = termSucc1Chance + (1-2*self.epsilon)*(max(0,1-termSucc1Chance-termFail3Chance));
            #print(f"termP {termP}")
        if self.centre != 0:
            failcount = max(0,failcount - eTermFail1);
            #print(f"fail count for centres {failcount}")
            centP = (1-self.epsilon)*(1-min(1,failcount/self.centre));
            #print(f"centre payoff {centP}")
        return [termP,centP]
    
    def calcTermFail3Chance(self):
        failCount = max(0,self.drivers-(self.n*self.cdist.mean()));
        return min(1,failCount/(self.drivers - self.centre));

    def calcTermSucc1Chance(self,error):
        #Multiple of var we check up to abusing Chebyshev
        k = math.ceil(math.sqrt(1/error));
        #print(f"k {k}")
        #Variance of customer dist
        cVar = self.cDist.var;
        #print(f"cVar {cVar}")
        cRange = math.ceil(min((k*cVar),self.cDist.n));
        #print(f"cRange {cRange}")
        #Variance of drivers
        dVar = self.dDist.var;
        #print(f"dVar {dVar}")
        dRange = min(math.ceil(k*dVar),self.d-self.centre-1);
        #print(f"dRange {dRange}")
        #Expected of C_i/D_i+1 see paper then ref
        rawExp = (self.cDist.mean)*(self.dDist.mean);

        #print(f"rawExp {rawExp}");
        #Value of the tail adjustment
        t = 0;
        for d in range(0,dRange+1):
            if (d+1<cRange):
                for c in range(d+1,cRange+1):
                    t+=(1-(c/(d+1)))*self.cDist.pr(c)*self.dDist.pr(d);
        #print(f"t {t}")
        return rawExp + t;

        """ Double check lema about auto balancing. 
            """

    def calcCentreFail2Chance(self):
        failCount = max(0,self.drivers-(self.n*self.dist.mean()) - (self.drivers - self.centre));
        return min(1,failCount/self.drivers);

    def __str__(self):
        return(f"drivers: {self.drivers}, cars at centre: {self.centre}, terminals: {self.n}, epsilon: {self.epsilon}")


class distribution():
    def __init__(self,mean,var,pdf):
        self.pdf = pdf;
        self.mean = mean;
        self.var = var;
    
    def mean(self):
        return self.mean;

    def var(self):
        return self.pr;

    def pr(self,val):
        self.pdf(val);

class binomDist(distribution):
    def __init__(self,mean,varfactor):
        self.mean = mean;
        self.var = mean*(1-1/varfactor);
        self.n = math.ceil(varfactor*mean);
        #print(f"trials for cDist {self.n}");
        self.p = 1/varfactor;

    def pr(self,val):
        if val > self.n or val < 0:
            return 0;
        return math.comb(self.n,val)*math.pow(self.p,val)*math.pow(1-self.p,self.n-val);

class driverDist(distribution):
    def __init__(self,d,n):
        self.d = d;
        self.n = n;
        self.p = 1/n;
        if d == 0:
            self.mean = 0;
            self.var = 0;
        else:
            self.mean = (n/d)*(1-math.pow(1-(self.p),d));
            self.var = (1/(self.p*self.p*(self.d*self.d+self.d)))*(1-math.pow(1-self.p,self.d+1)-(self.p*(self.d+1)*math.pow(1-self.p,self.d)));
    #Pr of val other drivers
    def pr(self,val):
        if val > self.d-1 | val < 0:
            return 0;
        return math.comb(self.d-1,val)*math.pow(self.p,val)*math.pow(1-self.p,self.d-(val+1));


class DistTest():
    def __init__(self,game):
        self.game = game

    def testTerm1(self,trials):
        print(f"trials: {trials}");
        for j in range(self.game.drivers):
            gs = self.game.initState(j);
            cDist = gs.cDist;
            dDist = gs.dDist;
            pred = cDist.mean*dDist.mean;
            real = 0;
            for i in range(trials):
                real += (random.binomialvariate(cDist.n,cDist.p)/(1+random.binomialvariate(dDist.d-1,dDist.p)))/trials;
            print(f"centre {j}, predicted {pred}, sample {real}, difference {abs(pred-real)}")

    def testExp(self,trials,error):
        print(f"trials: {trials}");
        for j in range(self.game.drivers):
            gs = self.game.initState(j);
            cDist = gs.cDist;
            dDist = gs.dDist;
            pred = gs.calcTermSucc1Chance(error);
            real = 0;
            for i in range(trials):
                real += min(1,random.binomialvariate(cDist.n,cDist.p)/(1+random.binomialvariate(dDist.d-1,dDist.p)))/trials;
            print(f"centre {j}, predicted {pred}, sample {real}, difference {abs(pred-real)}")
    
    def testFirstRoundFail(self,trials,error):
        print(f"testing prediction of drivers to fail first time, trials: {trials}");
        for j in range(self.game.drivers):
            gs = self.game.initState(j);
            cDist = gs.cDist;
            predsuccChance =  gs.calcTermSucc1Chance(error);
            termD = gs.d-gs.centre;
            pred = termD*(1-predsuccChance);
            real = 0;
            for k in range(trials):
                left = 0;
                drivers = [];
                for i in range(gs.n):
                    drivers.append(0);
                for i in range(termD):
                    p = random.randrange(0,gs.n);
                    drivers[p] += 1;
                for i in range(gs.n):
                    left += max(0,drivers[i] - random.binomialvariate(cDist.n,cDist.p));
                real += (left/trials)
            print(f"centre {j}, predicted {pred}, sample {real}, difference {abs(pred-real)}")



class TestNE():
    #We consider the space of game as its parameter space indexed from 0 to 4 e.g.
    #0 - binom mean
    #4 - epsilon
    #We give the fixed values in order in list fixed skipping the varied
    #We vary the independant variable from varbounds[0] and increase by step until we exceed varBound[1]
    def __init__(self,indexOfVar,fixed,varBounds,varStep,mult,filename,error):
        self.indexOfVar = indexOfVar;
        self.fixed = fixed;
        self.varBounds = varBounds;
        self.varStep = varStep;
        self.error = error;
        self.mult = mult;
        self.pSpace = [];
        self.tResults = [];
        self.f = open(filename,"a");
        self.f.write("""key: #0 - binom mean
     #1 - binom var factor
     #2 - drivers
     #3 - terminals
     #4 - epsilon\n""")
        self.f.write(f"began at time {datetime.datetime.now()}\n")
        self.f.write(f"i.v: #{self.indexOfVar} from {self.varBounds[0]} to {self.varBounds[1]} {"multiplying" if self.mult else "adding"} with step of {self.varStep}\nc.v: {self.fixed}\n")
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
            game = Game(binomDist(self.pSpace[0],self.pSpace[1]),self.pSpace[2],self.pSpace[3],self.pSpace[4],self.error);
            self.tResults.append([i,game.findNE()]);
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

def varToVarf(var):
    return 1/(1-var);

t1 = time.time()
for i in range(10):
    TestNE(3,[1,1+i,100,0.4],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\var_exp_amnd_3.txt",0.001).resultsSimple();

TestNE(3,[1,100,100,0.4],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\var_exp_amnd_3.txt",0.001).resultsSimple();
TestNE(3,[1,1000,100,0.4],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\var_exp_amnd_3.txt",0.001).resultsSimple();

#test = DistTest(Game(binomDist(1,1),100,25,0.4,0.001));
#test.testExp(1000,0.0001)
#TestNE(3,[1,1000,100,0],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\epsln_exp_amnd_1.txt",0.001).resultsSimple();
#e = 0.0001;
#for i in range(3):
#    TestNE(3,[1,1000,100,e],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\epsln_exp_amnd_1.txt",0.001).resultsSimple();
#    e = e*10;
#for i in range(5):
#        TestNE(3,[1,1000,100,(i+1)/10],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\epsln_exp_amnd_1.txt",0.001).resultsSimple();

#for i in range(9):
#    TestNE(3,[1,varToVarf(i/10),100,0.4],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\var_exp_amnd_1.txt",0.001).resultsSimple();
#v = 10;
#for i in range(6):
#    TestNE(3,[1,v,100,0.4],[1,100],1,False,r"C:\Users\koend\Documents\AGT Code\experiments\var_exp_amnd_1.txt",0.001).resultsSimple();
#    v = v * 10;



#print(Game(binomDist(1,1),100,50,0.4,0.0001).findNE())
t2 = time.time()
print('Total elapsed time: {} seconds'.format((t2 - t1)))
#r"C:\Users\koend\Documents\AGT Code\experiments\exp_1_raw_data.txt"
