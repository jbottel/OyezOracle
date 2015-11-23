import climate
import theanets
import json
import numpy as np

climate.enable_default_logging()

net = theanets.Regressor([775, 9, 1])

listinputs = []
listoutputs = []
data = []
f = open('dataset')
for line in f.readlines():
    case = json.loads(line)
    print case
    if case["output"] == "petitioner":
        output = 1
    else:
        output = 0
    data.append({"inputs": case["inputs"], "output": output})
    listinputs.append(case["inputs"])
    listoutputs.append([output])


numout =  len(listoutputs)
inputs = np.array(listinputs)
outputs = np.array(listoutputs)


inputs.shape = (numout,775)

inputs = inputs.astype('f')
outputs = outputs.astype('i')
print outputs.shape
print inputs.shape
cut = int(len(inputs) * 0.8)  # training / validation split
train = inputs[:cut], outputs[:cut]
valid = inputs[cut:], outputs[cut:]


net.train(train, valid, algo='sgd', learning_rate=1e-4, momentum=0.9,patience=200)


numco = 0.0
for datum in data:
    these_input = np.array(datum["inputs"])
    these_input.shape = (1,775)
    correct, predicted =  datum["output"], net.predict(these_input)[0][0]
    print correct, predicted
    predicted = int(round(predicted))
    if predicted > 1:
        predicted = 1
    if predicted < 0:
        predicted = 0
    if correct == predicted:
        print "Correct!"
        numco += 1

print "percentage correct:", (numco / len(data))

net.save("theanet_network.p")
