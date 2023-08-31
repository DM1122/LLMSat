# Start new instance of STK Engine using the new API
from agi.stk12.stkengine import STKEngine
from agi.stk12.stkobjects import *

stk = STKEngine.StartApplication(noGraphics=False)  # optionally, noGraphics = True

# Get the IAgStkObjectRoot interface
root = stk.NewObjectRoot()

root.LoadScenario("./scenarios/mars/mars.sc")

input("Press any key to quit...")
stk.ShutDown()
