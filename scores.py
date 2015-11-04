import string
import matplotlib.pyplot as plt
import numpy
import nltk
from collections import Counter
from mpltools import style


def get_features_from_statements(grouping_of_statements):
    num_of_words_per_speaker = []
    features_for_speakers = {}
    for speaker, statements in grouping_of_statements.iteritems():
        features_for_speakers[speaker] = {}
        all_words = []
        interrupt_number = 0
        dunno = 0
        why = 0
        wrong = 0
        for statement in statements:
            words = get_words_from_string(statement)
            all_words.extend(words)
            if "don't know" in statement:
                dunno = dunno + 1
            if "why" in statement:
                why = why + 1
            if "@$" in statement:
                interrupt_number = interrupt_number + 1
            if "wrong" in statement:
                wrong = wrong + 1

        if len(statements) != 0:
            avg_words = len(all_words) / len(statements)
        else:
            avg_words = 0

        print "Identifying parts of speech. . ."
        tags = nltk.pos_tag(all_words)
        counts = dict(Counter(tag for word, tag in tags))
        print "Parts of Speech: %s" % counts
        num_of_words_per_speaker.append((speaker, len(all_words)))

        features_for_speakers[speaker]["NUMSTM"] = len(statements)
        features_for_speakers[speaker]["AVGWRD"] = avg_words
        features_for_speakers[speaker]["NUMINTR"] = interrupt_number
        features_for_speakers[speaker]["NUMDK"] = dunno
        features_for_speakers[speaker]["NUMWHY"] = why
        features_for_speakers[speaker]["NUMWNG"] = wrong

        features_for_speakers[speaker] = dict(features_for_speakers[speaker].items() + counts.items())

    return features_for_speakers


def get_statistics_from_statements(grouping_of_statements):
    num_of_words_per_speaker = []
    for speaker, statements in grouping_of_statements.iteritems():
        print "\n" + "-"*60
        print "Statistics for speaker %s " % speaker
        print "-"*60
        print "Number of statements: %d " % len(statements)
        all_words = []
        interrupt_number = 0
        dunno = 0
        why = 0
        wrong = 0
        for statement in statements:
            words = get_words_from_string(statement)
            all_words.extend(words)
            if "don't know" in statement:
                dunno = dunno + 1
            if "why" in statement:
                why = why + 1
            if "@$" in statement:
                interrupt_number = interrupt_number + 1
            if "wrong" in statement:
                wrong = wrong + 1
        if len(statements) != 0:
            avg_words = len(all_words) / len(statements)
        else:
            avg_words = 0
        print "Average # of words per statement: %d" % avg_words
        print "Number of interruptions: %d" % interrupt_number
        print "Number of dunnos: %d" % dunno
        print "Number of whys: %d" % why
        print "Number of wrongs: %d" % wrong
        print "Number of words: %d" % len(all_words)
        fdist = nltk.FreqDist(all_words)
        print "Most commonly used words: %s" % fdist.most_common(3)
        print "Identifying parts of speech. . ."
        tags = nltk.pos_tag(all_words)
        counts = Counter(tag for word, tag in tags)
        print "Parts of Speech: %s" % counts
        num_of_words_per_speaker.append((speaker, len(all_words)))
    return num_of_words_per_speaker


def get_words_from_string(statement, exclude_stopwords=True):
    # Remove punctuation in string
    statement = statement.translate(string.maketrans("", ""), string.punctuation)
    # Split into list of words
    words = statement.split()
    if exclude_stopwords:
        from nltk.corpus import stopwords
        stopwords = stopwords.words('english')
        # Remove words from list if they are stopwords
        words = [word for word in words if word.lower() not in stopwords]
    return words


def get_number_of_words_per_speaker(grouping_of_statements):
    num_of_words_per_speaker = []
    for speaker, statements in grouping_of_statements.iteritems():
        all_words = []
        for statement in statements:
            words = get_words_from_string(statement)
            all_words.extend(words)
            # Append a tuple of (speaker, number_of_words) to list
            num_of_words_per_speaker.append((speaker, len(all_words)))

    return num_of_words_per_speaker


def get_plot_number_of_words_per_speaker(num_words, ignore_petitioner=False, petitioner=None):
    """Plot a number of words per speaker.
    num_words is a list of tuples of (speaker, num_words_for_speaker)

    One can pass in a petitioner to ignore for plotting convenience.
    """

    if ignore_petitioner:
        num_words = [s for s in num_words if s[0] != petitioner]

    # A list comprehension where we compile the list of tuples into two lists
    # (converting the HumanName into a last name string)
    speakers, num_words = [str(e[0].last) for e in num_words], [e[1] for e in num_words]

    # Call the plot_names_and_numbers method and plot the speakers and their num_words
    plot = get_plot_names_and_numbers(speakers, num_words, "Number of Words", "Number of Words Spoken in Argument")

    return plot


def get_plot_number_of_statements_per_speaker(grouping_of_statements, ignore_petitioner=False, petitioner=None):
    names = []
    numbers = []
    for speaker, statements in grouping_of_statements.iteritems():
        if speaker is petitioner:
            continue
        names.append(speaker.last)
        numbers.append(len(statements))

    plot = get_plot_names_and_numbers(names, numbers, "Number of Interruptions",
                                      "Number of Individual Interruptions in Argument")

    return plot


def get_plot_names_and_numbers(names, numbers, x_label=None, title=None):
    style.use('ggplot')
    y_positions = numpy.arange(len(names))
    plt.barh(y_positions, numbers, align='center')
    plt.yticks(y_positions, names)
    plt.xlabel(x_label)
    plt.title(title)
    return plt
