import sys
import transcript
import scores

if __name__ == "__main__":
    for arg in sys.argv:
        if '.pdf' in arg:
            the_transcript = transcript.get_transcript_from_PDF(arg)
            petitioners, respondents = transcript.get_petitioners_and_respondents(the_transcript)
            argument = transcript.get_argument(the_transcript)

            arguments_by_advocate = transcript.get_arguments_by_advocate(petitioners, respondents, argument)
            for petitioner, argument in arguments_by_advocate["petitioner"].iteritems():
                statements = transcript.get_statements_in_argument(argument, petitioner)
                scores.get_statistics_from_statements(statements)
                number_of_words_per_speaker = scores.get_number_of_words_per_speaker(statements)

            for respondent, argument in arguments_by_advocate["respondent"].iteritems():
                statements = transcript.get_statements_in_argument(argument, respondent)
                scores.get_statistics_from_statements(statements)
                number_of_words_per_speaker = scores.get_number_of_words_per_speaker(statements)
