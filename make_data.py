from pybrain.tools.shortcuts import buildNetwork
import transcript
import scdb
import simplejson
import scores
import re
from os import listdir
from os.path import isfile, join
mypath = "transcripts"
files = ["transcripts/" + f for f in listdir(mypath) if isfile(join(mypath, f))]

net = buildNetwork(775, 9, 1)

for file in files:
    print "Now processing " + file

    slash = file.find('/')
    end_docket = file.find('_')
    if end_docket == -1:
        end_docket = file.find(".pdf")
    questionnumber = re.search(r"q\d", file)
    if questionnumber:
        end_docket = questionnumber.start()
    docket_number = file[slash+1:end_docket]
    print "Checking database for docket #%s" % docket_number
    info = scdb.get_case_info(docket_number)
    if not info:
        print "Couldn't find case in SCDB. Will skip."
        continue
    print "Now processing transcript for ", info["caseName"]
    winner = scdb.get_winning_party(docket_number)
    if winner == "unclear":
        print "The winner of this case is unclear. Will skip."
        continue
    print "Winner identified: %s" % winner
    print "Decision direction: %s" % info["decisionDirection"]

    the_transcript = transcript.get_transcript_from_PDF(file)
    petitioners, respondents = transcript.get_petitioners_and_respondents(the_transcript)
    argument = transcript.get_argument(the_transcript)

    arguments_by_advocate = transcript.get_arguments_by_advocate(petitioners, respondents, argument)

    inputs = []

    for petitioner, argument in arguments_by_advocate["petitioner"].iteritems():
        statements = transcript.get_statements_in_argument(argument, petitioner)
        #scores.get_statistics_from_statements(statements)
        number_of_words_per_speaker = scores.get_number_of_words_per_speaker(statements)
        features = scores.get_features_from_statements(statements)
        flat_features = scores.flatten_features(features)
        #import matplotlib.pyplot as plt
        #from mpltools import style
        #style.use('ggplot')
        #plt.ion()

        #D = flat_features


        #plt.barh(range(20), D.values()[:20], align='center')
        #plt.yticks(range(20), D.keys()[:20])

        #plt.draw()
        #plt.clf()
        normalized = scores.normalize_feature_list(flat_features)
        myscores = scores.get_feature_vector(normalized)
        inputs.extend(myscores)

    for respondent, argument in arguments_by_advocate["respondent"].iteritems():
        statements = transcript.get_statements_in_argument(argument, respondent)
        #scores.get_statistics_from_statements(statements)
        number_of_words_per_speaker = scores.get_number_of_words_per_speaker(statements)
        features = scores.get_features_from_statements(statements)
        flat_features = scores.flatten_features(features)
        #import matplotlib.pyplot as plt
        #from mpltools import style
        #style.use('ggplot')
        #plt.ion()

        #D = flat_features

        #plt.barh(range(20), D.values()[:20], align='center')
        #plt.yticks(range(20), D.keys()[:20])

        #plt.draw()
        #plt.clf()

        #normalized = scores.normalize_feature_list(flat_features)
        myscores = scores.get_feature_vector(normalized)
        inputs.extend(myscores)
        f = open("scores","a")
        f.write(simplejson.dumps(myscores)+"\n")
        f.close()

    if len(inputs) < 774:
        # We were unable to match all arguments
        # Not gonna help us, continue
        print "Parsing error? Did not create enough features."
        continue

    if len(inputs) > 774:
        # More than one argument per advocate
        # just get the first two
        inputs = inputs[:774]
        print "Parsing error? Had to truncate features."

    # Add final "decisionDirection" score

    inputs.append(int(info["decisionDirection"]))

    print "Final input vector length: %d" % len(inputs)
    line_to_write = {}
    line_to_write["inputs"] = inputs
    line_to_write["output"] = winner
    f = open("dataset", "a")
    f.write(simplejson.dumps(line_to_write)+"\n")
    f.close()

    print inputs
    print net.activate(inputs)
