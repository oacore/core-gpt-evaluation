import csv
from flask import Flask, render_template, request, make_response, redirect
import sqlite3

app = Flask(__name__, template_folder=".")


def read_csv(file_path):
    with open(file_path, newline='', encoding='ISO-8859-1') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


def create_database():
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results
                (annotator_id INTEGER, question_number INTEGER, scale_value INTEGER, trust_value INTEGER, utility_value INTEGER,
                relevance_1 INTEGER, 
                relevance_2 INTEGER, 
                relevance_3 INTEGER,
                relevance_4 INTEGER,
                relevance_5 INTEGER)''')
    conn.commit()
    conn.close()


create_database()


def get_stage_value(annotator_id):
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("SELECT stage FROM annotators WHERE annotator=?", (annotator_id,))
    stage = c.fetchone()
    conn.close()
    print('retreivng stage for annotator:', annotator_id)
    print('Stage:', stage)
    print(type(stage[0]))
    return stage[0] if stage else 1


def update_stage_value(annotator_id, stage):
    conn = sqlite3.connect("results.db")
    c = conn.cursor()
    c.execute("UPDATE annotators SET stage=? WHERE annotator=?", (stage, annotator_id))
    conn.commit()
    conn.close()


@app.route('/enter_id', methods=['GET', 'POST'])
def enter_id():
    if request.method == 'POST':
        annotator_id = request.form['annotator_id']
        response = make_response(redirect('/'))
        return response
    else:
        return render_template('enter_id.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        annotator_id = int(request.form['annotator_id'])
        if annotator_id is None:
            return render_template('enter_id.html')
        question_number = get_stage_value(annotator_id)
        if 'index' in request.form:
            index = int(request.form['index']) - 1
            print(f"Question Number {question_number}:")
            print("Scale Value:", request.form['scale_value'])
            print("Trust Value:", request.form['trust_value'])
            print("Utility:", request.form['utility_value'])
            for i in range(1, 6):
                print(f"Relevance {i}:", request.form[f'relevance_{i}'])

            conn = sqlite3.connect("results.db")
            c = conn.cursor()
            data = (annotator_id, question_number, int(request.form['scale_value']), int(request.form['trust_value']),
                    int(request.form['utility_value']))
            relevance_scores = tuple(int(request.form[f'relevance_{i}']) for i in range(1, 6))
            data = data + relevance_scores
            c.execute("INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data)

            conn.commit()
            conn.close()

            # Update the stage value in the annotators table
            update_stage_value(annotator_id, question_number + 1)

            question_number += 1
        else:
            if annotator_id is None:
                return render_template('enter_id.html')
            else:
                index = 0
                data = read_csv('output.csv')
                row = data[index]
                response = make_response(
                    render_template('index.html', row=row, index=index + 1, question_number=question_number, annotator_id=annotator_id))
                return response

        index = int(request.form['index'])
        data = read_csv('output.csv')
        row = data[question_number]
        response = make_response(
            render_template('index.html', row=row, index=index + 1, question_number=question_number, annotator_id=annotator_id))
        return response
    else:
        response = make_response(redirect('/enter_id'))
        return response


if __name__ == '__main__':
    app.run(debug=True)
