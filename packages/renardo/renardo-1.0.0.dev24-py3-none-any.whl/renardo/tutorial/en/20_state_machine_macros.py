

class POne():
    def __init__(self):
        self.oct = [4,5,6,5]
        self.index = 0
        p1 >> blip()
    def state_cycling(self):
        p1.oct = self.oct[self.index%len(self.oct)]
        self.index += 1
        
p1 >> pluck()

pone = POne()

pone.state_cycling()

rpit1 = rpit(period=8, beat=now())

#{rpit1}
pone.state_cycling()


########################

#{machine1.init}
oct = [4,5,P[3,4,7],5]
index = 0
p1 >> blip()
#{machine1.cycle}
p1.oct = oct[index%len(oct)]
#{machine1.cycle2}