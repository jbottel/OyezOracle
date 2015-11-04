from justices import JUSTICE_CODES


def get_all_feature_codes():
    feature_codes_list = []
    for feature_code in feature_codes:
        for justice, code in JUSTICE_CODES.iteritems():
            feature_codes_list.append(code + "_" + feature_code)

    return feature_codes_list


feature_codes = [
    "MQSCORE",
    "NUMSTM",
    "AVGWRD",
    "NUMINTR",
    "NUMDK",
    "NUMWHY",
    "NUMWNG",
    "CC",
    "CD",
    "DT",
    "EX",
    "FW",
    "IN",
    "JJ",
    "JJR",
    "JJS",
    "LS",
    "MD",
    "NN",
    "NNS",
    "NNP",
    "NNPS",
    "PDT",
    "POS",
    "PRP",
    "PRP$",
    "RB",
    "RBR",
    "RBS",
    "RP",
    "SYM",
    "TO",
    "UH",
    "VB",
    "VBD",
    "VBG",
    "VBN",
    "VBP",
    "VBZ",
    "WDT",
    "WP",
    "WP$",
    "WRB"
]
