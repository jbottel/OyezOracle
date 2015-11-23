import transcript
import scdb
import simplejson
import scores
from os import listdir
from os.path import isfile, join
mypath = "transcripts"
files = ["transcripts/" + f for f in listdir(mypath) if isfile(join(mypath, f))]

f = open("scores","w")
f.write("Scores:\n")
f.close()

for file in files:
    print "Now processing " + file

    slash = file.find('/')
    end_docket = file.find('_')
    if file.find('q') != -1:
        docket_number = file.find('q')
    docket_number = file[slash+1:end_docket]
    print "Checking database for docket #%s" % docket_number
    print "Winner identified: %s" % scdb.get_winning_party(docket_number)
    raw_input()

    the_transcript = transcript.get_transcript_from_PDF(file)
    petitioners, respondents = transcript.get_petitioners_and_respondents(the_transcript)
    argument = transcript.get_argument(the_transcript)

    arguments_by_advocate = transcript.get_arguments_by_advocate(petitioners, respondents, argument)

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
        print "Number of features: %d" % len(myscores)
        f = open("scores","a")
        f.write(simplejson.dumps(myscores)+"\n")
        f.close()

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
        print "Number of features: %d" % len(myscores)
        f = open("scores","a")
        f.write(simplejson.dumps(myscores)+"\n")
        f.close()
