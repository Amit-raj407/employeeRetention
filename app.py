import os
from flask import Flask, render_template, request, redirect
import numpy as np
import _pickle as cPickle
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

files = 'csv_files'
app.config['UPLOAD_FOLDER'] = files
ALLOWED_EXTENSIONS = {'csv','xls'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def hello():
    return render_template('dashboard.html')

@app.route("/index", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        pass
    return render_template('index.html')

@app.route("/multiple", methods=['GET','POST'])
def multiple():
    if request.method == 'POST':
        if 'file' not in request.files:
            # flash('No File Part')
            return redirect(request.url)
        f = request.files['file']
        
        if(f.filename == ''):
            # flash("No Selected File")
            return redirect(request.url)
        
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "SUCCESS"
    return render_template('multiple.html')

def func():
    with open('model.pkl', 'rb') as f:
        rf = cPickle.load(f)
    with open("info.json") as file:
        json_object = json.loads(file.read())

    cols = ['satisfaction_level', 'Work_accident', 'promotion_last_5years', 'department_accounting', 'department_hr',
            'department_marketing', 'department_sales', 'department_support', 'salary_low', 'salary_medium']
    d = {i: 0 for i in cols}
    for i in json_object:
        if i in d:
            d[i] = float(json_object[i])
        else:
            x = str(i)+'_'+str(json_object[i])
            if x in d:
                d[x] = 1

    val = rf.predict(np.array(list(d.values())).reshape(1, 10))[0]
    return val

@app.route("/predict", methods=["POST"])
def predict():
    data = request.form.to_dict()
    # return data
    data["satisfaction_level"] = int(data["satisfaction_level"])/100
    data["last_evaluation"] = int(data["last_evaluation"])/100
    if(int(data["salary"]) < 15000):
        data["salary"] = "low"
    elif(15000 < int(data["salary"]) < 50000):
        data["salary"] = "medium"
    else:
        data["salary"] = "high"
    json_object = json.dumps(data)
    with open("info.json", "w") as f:
        f.write(json_object)
    val = func()
    if(val == 0):
        str = "not Leave"
    else:
        str = "Leave"
    return render_template("result.html",name=data["Name"],result=str)
    # return "Data Saved"


if __name__ == "__main__":
    app.run(debug=True)
