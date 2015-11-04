import subprocess
import sys
import re
import logging
import nameparser
import itertools
from justices import JUSTICE_NAMES

PDFTOTEXT_COMMAND = "pdftotext"
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

JUSTICES = []
for justice in JUSTICE_NAMES:
    JUSTICES.append(nameparser.HumanName(justice.upper()))

logging.addLevelName(logging.WARNING, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
logging.addLevelName(logging.ERROR, "\033[1;41m%s\033[1;0m" % logging.getLevelName(logging.ERROR))


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def getTextFromPDF(filename):
    log = logging.getLogger('PDF_TO_TEXT')
    log.info("Getting text from PDF")
    # dependent on age of transcript, we may have to adjust the cropping later on
    result = subprocess.check_output(
        [PDFTOTEXT_COMMAND + " -enc UTF-8 -layout -x 130 -y 80 -W 1050 -H 670 " + filename + " -"],
        shell=True)
    if result:
        log.info("Got text from PDF")
    # Turn unicode characters into something useful.
    result = result.decode('utf8').replace(u"\xa0", " ").replace(u"\xad", "-").encode('ascii')
    return result


def get_transcript_from_PDF(filename):
    log = logging.getLogger('PARSE_TRANSCRIPT')
    text = getTextFromPDF(filename)
    # Remove Garbage
    text = re.sub(r"", "", text, flags=re.MULTILINE)
    # Remove Line Numbering that remains (most should be gone from crop)
    text = re.sub(r"^\d+\ *\n*", "", text, flags=re.MULTILINE)
    # Remote Reporting Company Info (should be gone from crop as well)
    text = re.sub(r".*Alderson.*", "", text, flags=re.MULTILINE)
    # Remote Official Designation (also cropped)
    text = re.sub(r"Official\n*", "", text, flags=re.MULTILINE)
    # Trim each line of whitepsace around the edges
    text = '\n'.join([line.strip() for line in text.split('\n')])
    log.info("Success in parsing transcript.")
    return text


def get_petitioners_and_respondents(text):
    log = logging.getLogger('GET_PET_AND_RES')
    log.info("Attempting to find petitioners and respondents...")
    # Find portion of transcript detailing who appears in the court.
    start = text.find('APPEARANCES:') + len('APPEARANCES:')
    end = text.find('C O N T E N T S')
    if end == -1:
        end = text.find('CONTENTS')
    if end == -1:
        end = text.find('PROCEED')
    if end == -1:
        end = text.find('P R O C E E D')
    if end == -1:
        end = text.find('CHIEF')
    names_text = text[start:end].strip()

    # Regex to match names including lowercase c for Mc-names and apostrophe for O'-names and r for "Jr."
    # Assumes names are completely capitalized and end with a comma (not matched)
    names_pattern = re.compile(r"([A-Zrc',\.\ ]+),\ ")
    names = names_pattern.findall(names_text)
    log.info("Found %d names:" % len(names))
    log.info("Name strings: %s" % names)
    full_names = []
    for name in names:
        full_names.append(nameparser.HumanName(name))

    log.info("First and last from parse: %s" % [name.first + " " + name.last for name in full_names])

    petitioners = []
    respondents = []

    # Zip together a copy of the list so we can use the next object
    for full_name, nxt in zip(full_names, full_names[1:]+[None]):
        start = names_text.find(full_name.last)
        if nxt:
            end = names_text.find(nxt.last)
        else:
            end = len(names_text)

        # We define some names to search for to determine the side of the advocate
        pet_names = ['etition', 'ppellant', 'emand', 'evers', 'laintiff']
        res_names = ['espond', 'ppellee', 'efendant']
        pet = False
        res = False

        # We now search within the two names for "petitioner or respondent"
        if any(search in names_text[start:end] for search in pet_names):
            # He/She is a petitioner
            pet = True
        if any(search in names_text[start:end] for search in res_names):
            # He/She is a respondent
            res = True

        if pet and res:
            log.error("You've got an advocate who represents both sides!")
        if pet:
            petitioners.append(full_name)
        if res:
            respondents.append(full_name)
        if not res and not pet:
            log.info("Undetermined amicus curiae: %s" % full_name.last)

    log.info("Petitioners are: %s" % [petitioner.last for petitioner in petitioners])
    log.info("Respondents are: %s" % [respondent.last for respondent in respondents])

    return petitioners, respondents


def get_argument(text):
    log = logging.getLogger('GET_ARG_TEXT')
    log.info("Attempting to isolate argument from transcript")
    start = text.find('P R O C E E D')
    if start == -1:
        start = text.find('PROCEEDINGS')
    if start == -1:
        start = text.find("We'll now hear")
    if start == -1:
        start = 0
    end = text.rfind('Whereupon')
    if end == -1:
        end = text.rfind('Case is submitted.')
    if end == -1:
        end = text.rfind('Short break')
    if end == -1:
        log.error("Could not parse argument section from transcript.")
        return text
    log.info("Successfully isolated argument from transcript")
    return text[start:end]


def get_arguments_by_advocate(petitioners, respondents, argument_text):
    log = logging.getLogger('GET_ARG_BY_ADV')
    log.info("Attempting to isolate argument sections for each advocate")
    arguments_pattern = re.compile(r"ARGUMENT OF ([A-Zrc'\ \.]+)")
    arguments = arguments_pattern.finditer(argument_text)

    petitioner_arguments = {}
    respondent_arguments = {}
    for argument, next_argument in pairwise(itertools.chain(arguments, [None])):
        log.info("Found argument: %s" % argument.group())

        start = argument.end()
        if next_argument:
            end = next_argument.start()
        else:
            log.info("Finished looking for arguments")
            end = len(argument_text)

        pet = False
        res = False

        for petitioner in petitioners:
            if petitioner.last and petitioner.first in argument.group():
                log.info("Assigning %d:%d to petitioner: %s" % (start, end, petitioner))
                if petitioner in petitioner_arguments:
                    petitioner_arguments[petitioner] += argument_text[start:end]
                else:
                    petitioner_arguments[petitioner] = argument_text[start:end]
                pet = True

        for respondent in respondents:
            if respondent.last and respondent.first in argument.group():
                log.info("Assigning %d:%d to respondent: %s" % (start, end, respondent))
                if respondent in respondent_arguments:
                    respondent_arguments[respondent] += argument_text[start:end]
                else:
                    respondent_arguments[respondent] = argument_text[start:end]
                res = True

        if pet and res:
            log.error("You've got an argument assigned to both respondents and petitioners!")

        if not pet and not res:
            log.warning("An argument was unable to be matched and will not be returned")

    arguments = {}
    arguments["petitioner"] = petitioner_arguments
    arguments["respondent"] = respondent_arguments
    return arguments


def get_statements_in_argument(argument_text, arguer_name):
    log = logging.getLogger('GET_STMTS_IN_ARG')
    identifier_pattern = re.compile(r"([A-Z rc'\.]+):")
    statement_matches = identifier_pattern.finditer(argument_text)

    speakers = []
    statements = {}
    for justice in JUSTICES:
        speakers.append(justice)
        statements[justice] = []
    speakers.append(arguer_name)
    statements[arguer_name] = []

    interrupted = False
    for statement, next_statement in pairwise(itertools.chain(statement_matches, [None])):
        start = statement.end()
        if next_statement:
            end = next_statement.start()
        else:
            log.info("Finished looking for statements")
            end = len(argument_text)

        # log.info("Statement is: %s" % argument_text[start:start+50] + "... ")
        found = False
        for speaker in speakers:
            if speaker.last in statement.group():
                # log.info("Found %s, assigned to %s" % (statement.group(), speaker))
                processed_statement = argument_text[start:end].strip()
                processed_statement = " ".join([line.strip()
                                                for line in processed_statement.splitlines() if line.strip()])
                if interrupted:
                    processed_statement = "@$" + processed_statement
                statements[speaker].append(processed_statement)
                interrupted = False
                if processed_statement.endswith("--"):
                    # set the flag so the next speaker gets marked as an
                    # interruptor
                    interrupted = True

                found = True

        if not found:
            log.warning("Couldn't assign %s to a known speaker" % statement.group())

    return statements
