from flask import Flask, render_template, url_for, request, session
from bokeh.io import push_notebook, show, output_notebook,curdoc
from bokeh.server.server import Server
from bokeh.embed import components, server_document
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.layouts import column, layout, row
from bokeh.models import Slider, Div, CheckboxGroup, MultiSelect, Select, FileInput
from bokeh.plotting import figure, ColumnDataSource, show, output_file
from bokeh.models.callbacks import CustomJS
from bokeh.models import ImageURL 
from PIL import Image
import os
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

from bokeh.models import FixedTicker, FuncTickFormatter
from bokeh.transform import dodge




app = Flask(__name__)
app.secret_key="DIVISUALS"

@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    CurrentFile="No file has been selected yet, so the example dataset will be used"
    if "file_name" in session: 
        file_name=session["file_name"]
        CurrentFile=file_name

    FileText=""

    if request.method == "POST":
        file = request.files["FileSelect"]
        if file.filename == '':
            print("No file to be found, We'll use the example dataset")
            FileText="The currently selected file is either wrong or failed to send"
        else:
            file_name=file.filename
            session["file_name"] = file_name
            FileText="Your file {} uploaded succesfully!".format(file_name)
            CurrentFile=file_name

    return render_template('home.html', curfile=CurrentFile, filetext=FileText)

@app.route("/vis")
def vis():
    return render_template('vis.html')

@app.route("/about", methods=["POST", "GET"])
def about():

#     #Making
#     #THIS CELL IS THE ACTUAL CODE, THE OTHER CELLS ARE FOR PRACTICE!!!!!!!!
#     #Code that is commented out in this cell is old code, it's there as a backup for if all fails

    #CODE FOR THE GAZE STRIPE PLOT
    #The Gaze stripe plot has been made with the help of the following link: https://stackoverflow.com/questions/61908232/python-image-multiple-crops-with-pillow-and-grouped-and-displayed-in-a-row-with
    
    #Collecting the .csv file name from the POST method. If nothing has been posted yet, just take the example dataframe

    #KEEP IN MIND, IF THE FILE SELECTIO IS ON A DIFFERENT PAGE THEN MAKE SURE TO ADJUST THE CODE FOR SESSIONS SUCH THAT THE FIRST SESSION IS TERMINATED
    if "file_name" in session: file_name=session["file_name"]
    else: file_name="all_fixation_data_cleaned_up.csv" #Now it's fixed, later (via session) we will determine wether an example dataset is used or an already selected dataset
    
    if "image_name" in session: image_name=session["image_name"]
    else: image_name=""
    
    if "user_list" in session: user_list=session["user_list"]
    else: user_list=["Everyone"]

    def userListMaker(dataframe, stimuli):
        user_series = dataframe["user"][dataframe["StimuliName"] == stimuli].unique().copy()
        userlist=[]
        userlist.append({"name" : "Everyone"})
        for i in user_series:
            userlist.append({"name":i})
        return userlist

    def stimuliListMaker(dataframe): #Makes a list with all stimulinames for 
        images=dataframe["StimuliName"].unique().copy()
        menu=[]
        for i in images:
            menu.append({"name": i})
        return menu
    
    if request.method == "POST":
            user_list = request.form.getlist("user_select")
            session["user_list"] = user_list
            image_name = request.form.get("stimuli_select")
            session["image_name"]= image_name



    


    #Make the dataframe
    Eyetracking_data = pd.read_csv(file_name, encoding='latin1', sep="\t")
    Eyetracking_data
    df = Eyetracking_data.copy()

    #Get first image name from the dataset
    if image_name == "":
        image_name=df["StimuliName"][0]

    if user_list == ["Everyone"]:
        df_stimuli = df[df["StimuliName"] == image_name].copy()
    else:
        df_stimuli = df[(df["StimuliName"] == image_name) & (df["user"].isin(user_list))].copy()

    image_location = './static/images/MetroMapsEyeTracking/stimuli/{}'.format(image_name)
    #Get the X and Y coordinates of the points where people looked at and put them in a list
    
    coordinates = list(df_stimuli[['MappedFixationPointX', 'MappedFixationPointY']].itertuples(index=False, name=None))
    picture_size = 100 #Can be any value, I liked this one. (Maybe make a potential slider for size?)

    #Open the image and convert is to an image with RedGreenBlueAlpha as it's color scheme
    image = Image.open(image_location).convert('RGBA')
    images = [] #Here will all cropped images be appended to.
    
    for x, y in coordinates:
        box = (x - picture_size / 2, y - picture_size / 2, x + picture_size / 2, y + picture_size / 2) #Takes a certain part of the image in accordance with the coordinate given and size of the "box" it makes. Keep in mind this line isn't an actual image but more like a placeholder
        images.append(np.array(image.crop(box)).view(np.uint32)[::-1]) #Append the part of the image into the images list.

    #Make a new column in df_stimuli called 'Image'
    df_stimuli['Image'] = images

    # There's probably a better method to populate `TimeCoord` which I don't know.
    df_stimuli = df_stimuli.sort_values('FixationDuration') #Sort the rows in df_stimuli by 'FixationDuration'
    df_stimuli['TimeCoord'] = 0 #Makes new column in df_stimuli called 'TimeCoord' (In what order did the user look at the set of coordinates) and sets all values to 0.
    for u in df_stimuli['user'].unique(): 
        user_df = (df_stimuli['user'] == u) 
        df_stimuli.loc[user_df, 'TimeCoord'] = np.arange(user_df.sum()) #Add for the currend user 'u' in df_stimuli the sum of all rows that this user possesses for this stimuli

    
    #This part replaces the values in the user colomn with a sort of zipped dictionary where the user is inserted and a list with the tuple describing the dimension of df_stimuli[0] (may be any number)
    user_coords = dict(zip(df_stimuli['user'].unique(), range(df_stimuli.shape[0]))) 
    df_stimuli['UserCoord'] = df_stimuli['user'].replace(user_coords)

        
    gaze_stripe_plot = figure(match_aspect=True)  #Really needs to be True in order for the squares to not becomes messed up.
    for r in [gaze_stripe_plot.xaxis, gaze_stripe_plot.xgrid, gaze_stripe_plot.ygrid]: #Basically just turn the xaxis, xgrid and y grid invisible as you don't need them
        r.visible = False

    # Manually creating a categorical-like axis to make sure that we can use `dodge` below.
    gaze_stripe_plot.yaxis.ticker = FixedTicker(ticks=list(user_coords.values())) 
    gaze_stripe_plot.yaxis.formatter = FuncTickFormatter(args=dict(rev_user_coords={v: k for k, v in user_coords.items()}),
                                        code="return rev_user_coords[tick];")


    source = ColumnDataSource(df_stimuli)
    img_size = 0.8
    gaze_stripe_plot.image_rgba(image='Image',
                x=dodge('TimeCoord', -img_size / 2), y=dodge('UserCoord', -img_size / 2),
                dw=img_size, dh=img_size, source=source)
    gaze_stripe_plot.rect(x='TimeCoord', y='UserCoord', width=img_size, height=img_size, source=source,
        line_dash='dashed', fill_alpha=0)

    layout = row(gaze_stripe_plot)



    script, div = components(layout, wrap_script=False)

    return render_template('about.html', script=script, div=div, userdata= userListMaker(df, image_name), stimulidata=stimuliListMaker(df), activeusersdata=user_list, activestimulidata=[image_name])
    #return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)