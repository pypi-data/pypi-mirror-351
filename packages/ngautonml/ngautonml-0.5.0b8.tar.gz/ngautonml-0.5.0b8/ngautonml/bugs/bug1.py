'''File to  explore https://gitlab.com/autonlab/ngautonml/-/issues/1'''

import code
import logging
import warnings

from ..problem_def.problem_def import ProblemDefinition
from ..wrangler.wrangler import Wrangler

logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

if __name__ == '__main__':
    pdef = ProblemDefinition('''
    {
        "_comments" : [
            "A json file fully encapsulating the problem definition for openml dataset #31.",
            "This dataset is a tabular binary classification problem.",
            "People are classified as good or bad credit risks based on attributes."
        ],
        "dataset" : {
            "config" : "local",
            "train_path" : "examples/classification/credit-train.csv",
            "test_path": "examples/classification/credit-test.csv",
            "column_roles": {
                "target" : {
                    "name" : "class",
                    "pos_label": "good"
                }
            }
        },
        "problem_type" : {
            "data_type": "TABULAR",
            "task": "BINARY_CLASSIFICATION"
        },
        "metrics" :  {
            "roc_auc_score": {},
            "accuracy_score": {}
        },
        "output" : {}
    }
    ''')

    dut = Wrangler(problem_definition=pdef)

    got = dut.fit_predict_rank()

    code.interact(local=locals())
