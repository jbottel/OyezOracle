from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect
import transcript
import scores
import scdb
import climate
from predict import predict_case
app = Flask(__name__)

climate.enable_default_logging()

@app.route("/case_info/<docket_number>")
def get_case_info(docket_number):
    return jsonify(scdb.get_case_info(docket_number))

@app.route("/json_predict/<docket_number>")
def json_predict(docket_number):
    return str(predict_case(docket_number))

@app.route("/")
def index():
    return render_template('index.html', **locals())

@app.route("/predict/<docket_number>")
def predict(docket_number):
    info = scdb.get_case_info(docket_number)
    return render_template('predict.html', **locals())

@app.route("/inline_predict/<docket_number>")
def inline_predict(docket_number):
    info = scdb.get_case_info(docket_number)
    result = predict_case(docket_number)
    if result == 1:
        winner = "Petitioner"
    else:
        winner = "Respondent"
    if info["partyWinning"] == "1":
        actual = "Petitioner"
    elif info["partyWinning"] == "0":
        actual = "Respondent"
    else:
        actual = "Unclear"
    correct = False
    if winner == actual:
        correct = True
    confidence_level = int(abs(result - 0.5)*100)
    if confidence_level < 40:
        low_confidence = True
    return render_template('inline_predict.html', **locals())


@app.route("/bar_chart_data/<docket_number>")
def bar_chart_data(docket_number):
    the_transcript = transcript.get_transcript_from_PDF("transcripts/" + docket_number + ".pdf")
    petitioners, respondents = transcript.get_petitioners_and_respondents(the_transcript)
    argument = transcript.get_argument(the_transcript)

    arguments_by_advocate = transcript.get_arguments_by_advocate(petitioners, respondents, argument)
    for petitioner, argument in arguments_by_advocate["petitioner"].iteritems():
        statements = transcript.get_statements_in_argument(argument, petitioner)
        return jsonify(scores.bar_chart_speaker(statements))

    return {}

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"], host='0.0.0.0')
