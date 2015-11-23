import csv


def get_case_info(docket_number):
    with open('scdb_2015.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['docket'] == docket_number:
                return row
    return {}

def get_winning_party(docket_number):
    case = get_case_info(docket_number)
    if case["partyWinning"] == "1":
        return "petitioner"
    if case["partyWinning"] == "0":
        return "respondent"
    if case["partyWinning"] == "2":
        return "unclear"




if __name__ == "__main__":
    print get_case_info("14-378")
    print get_winning_party("14-378")
