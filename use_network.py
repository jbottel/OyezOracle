from pybrain.tools.xml.networkreader import NetworkReader
import json

net = NetworkReader.readFrom('second_net.xml')
f = open('dataset')
correct = 0
total = 0
for line in f.readlines():
    total += 1
    case = json.loads(line)
    answer = net.activate(case["inputs"])
    print answer
    answer = int(round(answer[0]))
    if answer < 0:
        answer = 0
    if answer > 1:
        answer = 1
    if answer == 1 and case["output"] == "petitioner":
        print "Correct"
        correct += 1
        continue
    if answer == 0 and case["output"] == "resppondent":
        print "Correct"
        correct += 1
        continue
    print "Incorrect"


print "Total: %d, Correct: %d" % (total, correct)
print "Percent correct:", (float(correct) / float(total))
