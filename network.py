from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.xml.networkwriter import NetworkWriter
from pybrain.structure import SoftmaxLayer
import json
from os import listdir
from os.path import isfile, join
mypath = "transcripts"
files = ["transcripts/" + f for f in listdir(mypath) if isfile(join(mypath, f))]

net = buildNetwork(775, 2, 1, bias=True, hiddenclass=SoftmaxLayer,)

ds = SupervisedDataSet(775, 1)

f = open('dataset')
for line in f.readlines():
    case = json.loads(line)
    print case
    if case["output"] == "petitioner":
        output = 1
    else:
        output = 0
    ds.addSample(case["inputs"], output)


test_data, training_data = ds.splitWithProportion(0.25)

trainer = BackpropTrainer(net, training_data)

print trainer.trainUntilConvergence(verbose=True)

NetworkWriter.writeToFile(net, "saved_network.xml")

for data in test_data:
    print "Network says: ", net.activate(data[0])
    print "Actual answer: ", data[1]
