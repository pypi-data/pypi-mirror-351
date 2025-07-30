from sier2 import Block, Connection
from sier2.panel import PanelDag
import param
import time
import pandas as pd 
import panel as pn
   
class StartBlock(Block):
    """Starts the test dag"""

    out_data = param.DataFrame()

    def execute(self):
        time.sleep(3)
        self.out_data = pd.DataFrame({'A':[1,2,3,4], 'B':[5,6,7,8]})

class FinishBlock(Block):
    """Finishes the test dag"""
    in_data = param.DataFrame()

sb = StartBlock(block_pause_execution=True)
fb = FinishBlock()
dag = PanelDag(doc='test', title='test')
dag.connect(sb, fb, Connection('out_data', 'in_data'))
dag.show()