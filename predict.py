import transcript
import scores
import climate
import scdb
import sys
import numpy as np
import logging
from pybrain.tools.xml.networkreader import NetworkReader
import json

net = NetworkReader.readFrom('second_net.xml')

climate.enable_default_logging()

def predict_case(docket_number, leaning=None):
    log = logging.getLogger('PREDICT_CASE')
    if not leaning:
        leaning = scdb.get_case_info(docket_number)["decisionDirection"]
    the_transcript = transcript.get_transcript_from_PDF("transcripts/" + docket_number + ".pdf")
    petitioners, respondents = transcript.get_petitioners_and_respondents(the_transcript)
    argument = transcript.get_argument(the_transcript)

    arguments_by_advocate = transcript.get_arguments_by_advocate(petitioners, respondents, argument)

    inputs = []

    for petitioner, argument in arguments_by_advocate["petitioner"].iteritems():
        statements = transcript.get_statements_in_argument(argument, petitioner)
        number_of_words_per_speaker = scores.get_number_of_words_per_speaker(statements)
        features = scores.get_features_from_statements(statements)
        flat_features = scores.flatten_features(features)
        normalized = scores.normalize_feature_list(flat_features)
        myscores = scores.get_feature_vector(normalized)
        inputs.extend(myscores)

    for respondent, argument in arguments_by_advocate["respondent"].iteritems():
        statements = transcript.get_statements_in_argument(argument, respondent)
        number_of_words_per_speaker = scores.get_number_of_words_per_speaker(statements)
        features = scores.get_features_from_statements(statements)
        flat_features = scores.flatten_features(features)
        normalized = scores.normalize_feature_list(flat_features)
        myscores = scores.get_feature_vector(normalized)
        inputs.extend(myscores)

    if len(inputs) < 774:
        # We were unable to match all arguments
        # Not gonna help us, continue
        print "Parsing error? Did not create enough features."
        return 0

    if len(inputs) > 774:
        # More than one argument per advocate
        # just get the first two
        inputs = inputs[:774]
        print "Parsing error? Had to truncate features."

    inputs.append(leaning)

    log.info(inputs[:25])
    log.info("Querying network. . .")
    return net.activate(inputs)[0]


if __name__=="__main__":
    print predict_case(sys.argv[1])
