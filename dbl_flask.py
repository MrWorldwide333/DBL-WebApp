from flask import Flask, render_template, url_for
app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/vis")
def vis():
    return render_template('vis.html')

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)