import os

from finder import Finder
from flask import Flask, render_template, url_for, request, redirect, session

app = Flask(__name__)
app.secret_key = "37825789567878456784867878680"
f = Finder()

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        url = request.form["url"]
        term = request.form["term"]
        condition = request.form["condition"]
        maxresults = request.form["maxresults"]
        session["url"] = url
        session["term"] = term
        session["condition"] = condition
        session["maxresults"] = maxresults

        return redirect(url_for("results"))
    else:
        return render_template("index.html")

@app.route("/results", methods=["POST", "GET"])
def results():
    if request.method == "POST":
        filter_comments = request.form["filter"]
        session["filter_comments"] = filter_comments
        return redirect(url_for("results"))
    else:
        if "filter_comments" not in session:
            session["filter_comments"] = "Latest"
            comments, total = f.find(session["url"], session["term"], session["condition"], session["maxresults"], session["filter_comments"])
        else:
            comments, total = f.find(session["url"], session["term"], session["condition"], session["maxresults"], session["filter_comments"])

        if not comments:
            return render_template("error.html")
        else:
            return render_template("results.html", results=comments, total=total, filter_value=session["filter_comments"])


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("home"))
    #maybe make a 404 page at a later date

if __name__ == "__main__":
    app.run(debug=True)
