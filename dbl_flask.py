from flask import Flask, render_template, url_for, request, session
from bokeh.io import push_notebook, show, output_notebook,curdoc
from bokeh.server.server import Server
from bokeh.embed import components, server_document
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.layouts import column, layout, row
from bokeh.models import Slider, Div, CheckboxGroup, MultiSelect, Select, FileInput
from bokeh.plotting import figure, ColumnDataSource, show, output_file

from PIL import Image
import os
import numpy as np
import pandas as pd

import numpy as np
import pandas as pd
from math import pi

import os
from os.path import dirname, join
from scipy.signal import savgol_filter


from flask import Flask, render_template, request, Response, send_from_directory
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show, save, output_notebook, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.palettes import Spectral4
from bokeh.layouts import column, row
from bokeh.transform import factor_cmap
from bokeh.models import OpenURL, CustomJS, TapTool, Select, FileInput
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Tabs, Panel
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

@app.route("/vis", methods=["POST", "GET"])
def vis():
    NameFile="all_fixation_data_cleaned_up.csv"
    if "file_name" in session: NameFile=session["file_name"]
    else: NameFile="all_fixation_data_cleaned_up.csv" #Now it's fixed, later (via session) we will determine wether an example dataset is used or an already selected dataset




    df = pd.read_csv(NameFile, encoding = 'latin1', sep= '\t')
    
    orientation_xaxis=(6*pi/10) 
    
    df_sum= df[['StimuliName', 'description', 'user', 'FixationDuration']].groupby(['StimuliName', 'description', 'user'], as_index=False).sum()
    df_max= df[['StimuliName', 'description', 'user', 'FixationDuration']].groupby(['StimuliName', 'description', 'user'], as_index=False).max()
    df_mean= df[['StimuliName', 'description', 'user', 'FixationDuration']].groupby(['StimuliName', 'description', 'user'], as_index=False).mean()
    
    source_sum= ColumnDataSource(df_sum)
    source_max= ColumnDataSource(df_max)
    source_mean= ColumnDataSource(df_mean)
    
    Stimuli_list= df['StimuliName'].unique()
    Description_list= df['description'].unique()
    
    ToolBox= ['box_select', 'tap', 'pan', 'zoom_in', 'zoom_out', 'wheel_zoom', 'save', 'reset']
    ColorPalette= ['#20639B', '#3CAEA3', '#F6D55C', '#ED553B']
    
    
    #The creation of the plot, with the containing set of widgets
    plot_sum= figure(
        plot_height = 800, 
        plot_width= 1000,
        title = "Summation of Fixation Duration per Stimuli and User",
        x_range = Stimuli_list,
        y_axis_label= 'Fixation duration (sec)',
        tools = ToolBox )
    plot_sum.xaxis.major_label_orientation = orientation_xaxis
    
    
    plot_max= figure(
        plot_height = 800, 
        plot_width= 1000,
        title = "Maximum of Fixation Duration per Stimuli and User",
        x_range = Stimuli_list,
        y_axis_label= 'Fixation duration (sec)',
        tools = ToolBox )
    plot_max.xaxis.major_label_orientation = orientation_xaxis
    
    
    plot_mean= figure(
        plot_height = 800, 
        plot_width= 1000,
        title = "Mean of Fixation Duration per Stimuli and User",
        x_range = Stimuli_list,
        y_axis_label= 'Fixation duration (sec)',
        tools = ToolBox )
    plot_mean.xaxis.major_label_orientation = orientation_xaxis
    
    plot_sum.vbar(
        x="StimuliName",
        top= 'FixationDuration',
        width= 0.4,
        fill_color= factor_cmap('description', palette = ColorPalette, factors= Description_list),
        fill_alpha= 0.6,
        source= source_sum,
        selection_color= '#20639B',
        selection_alpha= 0.6,
        legend_field= 'description')

    plot_sum.legend.orientation = 'vertical'
    plot_sum.legend.location= 'top_right'
    plot_sum.toolbar.autohide = True
    tab_sum = Panel(child= plot_sum, title= 'Summation')
    
    
    plot_max.vbar(
        x="StimuliName",
        top= 'FixationDuration',
        width= 0.4,
        fill_color= factor_cmap('description', palette = ColorPalette, factors= Description_list),
        fill_alpha= 0.8,
        source= source_max,
        selection_color= '#F6D55C',
        selection_alpha= 0.6,
        legend_field= 'description')

    plot_max.legend.orientation = 'vertical'
    plot_max.legend.location= 'top_right'
    plot_max.toolbar.autohide = True
    tab_max = Panel(child= plot_max, title= 'Max') 
    
    
    plot_mean.vbar( 
        x="StimuliName",
        top= 'FixationDuration',
        width= 0.4,
        fill_color= factor_cmap('description', palette = ColorPalette, factors= Description_list),
        fill_alpha= 1.0,
        source= source_mean,
        selection_color= '#ED553B',
        selection_alpha= 0.6,
        legend_field= 'description')
    
    plot_mean.legend.orientation = 'vertical'
    plot_mean.legend.location= 'top_right'
    plot_mean.toolbar.autohide = True
    tab_mean = Panel(child= plot_mean, title= 'Mean')
    
    
    Taptools= plot_sum.select(type = TapTool)
    #url = '/barchart.html'
    #Taptools.callback= OpenURL (url = url)
    Tabben = Tabs(tabs= [tab_sum, tab_max, tab_mean])
    script, div = components(Tabben, wrap_script=False)
    return render_template('vis.html', script=script, div=div)


@app.route("/about")
def about():

    #Making
    #THIS CELL IS THE ACTUAL CODE, THE OTHER CELLS ARE FOR PRACTICE!!!!!!!!
    #Code that is commented out in this cell is old code, it's there as a backup for if all fails
    image_name="01_Antwerpen_S1.jpg"
    image_location = "./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)
    image= Image.open(image_location) #Opens the image location using the Image library
    image_width, image_height = image.size #image.size is width, height
    
    
    Eyetracking_data = pd.read_csv("all_fixation_data_cleaned_up.csv", encoding='latin1', sep="\t")
    Eyetracking_data
    df = Eyetracking_data.copy()
    
    def stimuliListMaker(dataframe): #Makes a list with all stimulinames for 
        images=dataframe["StimuliName"].unique().copy()
        menu=[]
        for i in images:
            menu.append(i)
        return menu
        
    #Used for user selection
    def userListMaker(dataframe, stimuli):
        user_series = dataframe["user"][dataframe["StimuliName"] == stimuli].unique().copy()
        user_list=[]
        user_list.append("Everyone")
        for i in user_series:
            user_list.append(i)
        return user_list
    
#     def activeListMaker(user_list):
#         active_list=[]
#         for i in range(0, len(user_list)):
#             active_list.append(i)
#         return active_list
    
    def get_data(df, figure, users=["Everyone"]):
        factor=0.05 #Factor to make non outlier Fixationtime values into the right radius size
        if users[0] == "Everyone":
            X = df["MappedFixationPointX"][df["StimuliName"] == figure] #Select every x-coordinate from the chosen map
            Y = image_height - df["MappedFixationPointY"][df["StimuliName"] == figure] #Select every y-coordinate from the chosen map
            Fixationtime = df["FixationDuration"][df["StimuliName"] == figure] #Collect every fixationtime per timestamp for the chosen map
            Description = df["description"][df["StimuliName"] == figure] #Collects the descriptions from the database
            User = df["user"][df["StimuliName"] == figure] #Collects about which user this dot is.
            Radius = [] #Create empty list where the radius of the circle will be put in
            Color = [] #Create empty list where the right color for the circle will be assigned
            
        else:
            X = df["MappedFixationPointX"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Select every x-coordinate from the chosen map
            Y = image_height - df["MappedFixationPointY"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Select every y-coordinate from the chosen map
            Fixationtime = df["FixationDuration"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Collect every fixationtime per timestamp for the chosen map
            Description = df["description"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Collects the descriptions from the database
            User = df["user"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Collects about which user this dot is.
            Radius = [] #Create empty list where the radius of the circle will be put in
            Color = [] #Create empty list where the right color for the circle will be assigned
            
            for u in range(1, len(users)):
                X1 = df["MappedFixationPointX"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Select every x-coordinate from the chosen map
                Y1 = image_height - df["MappedFixationPointY"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Select every y-coordinate from the chosen map
                Fixationtime1 = df["FixationDuration"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Collect every fixationtime per timestamp for the chosen map
                Description1 = df["description"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Collects the descriptions from the database
                User1 = df["user"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Collects about which user this dot is.
                
                X = X.append(X1) #Add X1 to X
                Y = Y.append(Y1) #Add Y1 to Y
                Fixationtime = Fixationtime.append(Fixationtime1) #Add Fixationtime1 to Fixationtime
                Description = Description.append(Description1) #Add Description1 to Description
                User = User.append(User1) #Add User1 to User
                
                
                
        #This for loop will assign the radius and color to each circle
        for i in Fixationtime: 
            r= i * factor #radius = Fixationtime[i] * factor
            if r > 75: #If radius is above 75 px than make the radius 75 px and make the circle red. Else just make the circle blue.
                r=75
                Color.append("RED")
            else:
                Color.append("BLUE")
            Radius.append(r)
            
        data = dict(
            x= X,
            y= Y,
            fixationtime= Fixationtime,
            radius= Radius,
            user= User,
            description= Description,
            color = Color
        )

        return data #Returns a dictionary

    def make_plot(Tools, source):
        #The Hover-tool shows the Tooltips as shown here. The "@" stands for the data collected from the source
        Tooltips = [ 
            ("(x, y)", "(@x, @y)"),
            ("Fixation duration", "@fixationtime ms"),
            ("user", "@user"),
            #("description", "@description")
        ]

        #Creation of the figure
        plot = figure(x_range=(0,image_width), y_range=(0,image_height), tooltips=Tooltips, tools=Tools)
        plot.image_url(url=[image_location], x=0, y=image_height, w=image_width, h=image_height)
        plot.circle(x='x', y='y', size='radius', color='color', alpha=0.2, source=source)
        return plot
    
    
    #The update functions:
    def update_plot_stimuli(attr, old, new):
#         try: #Will happen if dataset is selected, This is the case the first time because an example dataset is selected
        image = new #Image is selected value
        df = pd.read_csv(File_Input.filename, encoding='latin1', sep='\t')
        data_new = get_data(df, image)             

        #Change user selection to users of this plot stimuli and select the previously selected value if it exists.
        
        user_select.options = userListMaker(df, image)
        user_select.value = ["Everyone"]
        source.data = data_new
#         except: #Will happen if no dataset is selected.
#             print("error")
        
    
    def update_plot_dataset(attr, old, new):
        try: #Will happen if a dataset is selected
            dataframe = pd.read_csv(File_Input.filename, encoding='latin1', sep='\t')
            
            #Get the first image from the list to already show a map for the plot
            image_name = dataframe["StimuliName"][0] 
            image_location = "./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)
            image= Image.open(image_location)
            image_width, image_height = image.size
            
            data_new = get_data(dataframe, image_name)
            
            #Change the stimuliSelection menu so that only the images from this dataset can be selected
            stimuliSelect.options=stimuliListMaker(dataframe)
            stimuliSelect.value=image_name
            
            #Change the user_select menu so that it only shows the users for this dataset with the first stimuli of the new dataset. Also resets the chosen value to "Everyone"
            user_select.options=userListMaker(dataframe, image_name)
            user_select.value=["Everyone"]
            
            source.data = data_new
        
        except: #Will happen if no dataset is selected
            print("error")
    
    #Potential user selection code
    def update_plot_user(attr, old, new):
        active_list = new
        dataframe = pd.read_csv(File_Input.filename, encoding='latin1', sep='\t')
        stimuli = stimuliSelect.value
        data_new = get_data(dataframe, stimuli, active_list)
        source.data= data_new

    
    #Code needed to make stimuli selector 
    stimuliList = stimuliListMaker(df)
    stimuliSelect = Select(value=image_name, title='Stimuli', options=stimuliList)
    stimuliSelect.on_change('value', update_plot_stimuli)
    
    #Code needed for file upload system
    File_Input = FileInput(filename="all_fixation_data_cleaned_up.csv", accept=".csv")
    File_Input.on_change('value', update_plot_dataset)
    
    
    Tools_vis1="pan,wheel_zoom, box_select, tap, reset, save"
    source = ColumnDataSource(data=get_data(df, image_name))
    
    #Code for the user selection
    user_list = userListMaker(df, image_name)
    user_select = MultiSelect(title="Users:", value=["Everyone"],
                        options=user_list ) #Don't forget to press shift or control (shift for everyone in between, control for selecting specific people) when selecting multiple users
    user_select.on_change("value", update_plot_user)
    
    scatterplot = make_plot(Tools_vis1, source)
    controls = column(File_Input, stimuliSelect, user_select)
    layout = row(scatterplot, controls)
    #doc.add_root(layout)
    script, div = components(layout, wrap_script=False)
    return render_template('about.html', script=script, div=div)
    #return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)