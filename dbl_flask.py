from flask import Flask, render_template, url_for, request, session
from bokeh.io import push_notebook, show, output_notebook,curdoc
from bokeh.server.server import Server
from bokeh.embed import components, server_document
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.layouts import column, layout, row
from bokeh.models import Slider, Div, CheckboxGroup, MultiSelect, Select, FileInput, TapTool
from bokeh.plotting import figure, ColumnDataSource, show, output_file
from bokeh.models.callbacks import CustomJS
from bokeh.models import ImageURL 
from PIL import Image
import os
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from math import pi
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Tabs, Panel


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
            FileText="The currently uploaded file is either the wrong format or failed to send"
        else:
            file_name=file.filename
            session["file_name"] = file_name
            FileText="Your file {} uploaded succesfully!".format(file_name)
            CurrentFile=file_name #Needed for the the text that says what file is currently selected

    return render_template('home.html', curfile=CurrentFile, filetext=FileText)

@app.route("/vis")
def vis():
    return render_template('vis.html')

@app.route("/about", methods=["POST", "GET"])
def about():

    #Making
    #THIS CELL IS THE ACTUAL CODE, THE OTHER CELLS ARE FOR PRACTICE!!!!!!!!
    #Code that is commented out in this cell is old code, it's there as a backup for if all fails
    if "file_name" in session: file_name=session["file_name"]
    else: file_name="all_fixation_data_cleaned_up.csv" #Now it's fixed, later (via session) we will determine wether an example dataset is used or an already selected dataset
    
    if "image_name" in session: image_name=session["image_name"]
    else: image_name=""
    
    if "user_list" in session: user_list=session["user_list"]
    else: user_list=["Everyone"]


    if request.method == "POST":
            print("No file to be found")
            # if  "Everyone" not in request.form.getlist("user_select"):
            user_list = request.form.getlist("user_select")
            session["user_list"] = user_list
            image_name = request.form.get("stimuli_select")
            session["image_name"]= image_name


    Eyetracking_data = pd.read_csv(file_name, encoding='latin1', sep="\t")
    df = Eyetracking_data.copy()
    df_stimuli = df[df["StimuliName"] == image_name]
    
    

    if (image_name == "" or (image_name not in df["StimuliName"])):
        image_name=df["StimuliName"][0]
        session['image_name'] = image_name

    if user_list == ["Everyone"]:
        df_stimuli = df[df["StimuliName"] == image_name].copy()
    else:
        df_stimuli = df[(df["StimuliName"] == image_name) & (df["user"].isin(user_list))].copy()

    if (user_list[0] != "Everyone"):
        df_stimuli = df[df["user"].isin(user_list)]

    image_location = "./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)
    image= Image.open(image_location) #Opens the image location using the Image library
    image_width, image_height = image.size #image.size is width, height
    source_image = ColumnDataSource(dict(
            url = ["./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)],
            x  = [0],
            y  = [image_height],
            w  = [image_width],
            h  = [image_height]
        ))
    
    
    
    factor=0.05 #Factor to make non outlier Fixationtime values into the right radius size

    def stimuliListMaker(dataframe): #Makes a list with all stimulinames for 
        images=dataframe["StimuliName"].unique().copy()
        menu=[]
        for i in images:
            menu.append({"name": i})
        return menu
        
    #Used for user selection
    def userListMaker(dataframe, stimuli):
        user_series = dataframe["user"][dataframe["StimuliName"] == stimuli].unique().copy()
        userlist=[]
        userlist.append({"name" : "Everyone"})
        for i in user_series:
            userlist.append({"name":i})
        return userlist
    
    
    def get_data(df, figure, users=["Everyone"]):
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
        ]

        #Creation of the figure
        plot = figure(x_range=(0,image_width), y_range=(0,image_height), tooltips=Tooltips, tools=Tools)
        
        
        image1 = ImageURL(url="url", x="x", y="y", w="w", h="h", anchor="top_left")
        plot.add_glyph(source_image, image1)
        plot.circle(x='x', y='y', size='radius', color='color', alpha=0.2, source=source)
        return plot
    
    orientation_xaxis=(6*pi/10) 

    
    df_sum= df_stimuli[['user', 'description', 'StimuliName', 'FixationDuration']].copy().groupby(['user', 'description', 'StimuliName'], as_index=False)
    df_sum_data = df_sum[["FixationDuration"]].sum()
    df_sum_data = df_sum_data[df_sum_data["StimuliName"] == image_name]

    df_max= df_stimuli[['user', 'description', 'StimuliName', 'FixationDuration']].copy().groupby(['user', 'description', 'StimuliName'], as_index=False)
    df_max_data = df_max[["FixationDuration"]].max()
    df_max_data = df_max_data[df_max_data["StimuliName"] == image_name]
    df_mean= df_stimuli[['user', 'description', 'StimuliName', 'FixationDuration']].copy().groupby(['user', 'description', 'StimuliName'], as_index=False)
    df_mean_data = df_mean[["FixationDuration"]].mean()
    df_mean_data = df_mean_data[df_mean_data["StimuliName"] == image_name]

    source_sum= ColumnDataSource(df_sum_data)
    source_max= ColumnDataSource(df_max_data)
    source_mean= ColumnDataSource(df_mean_data)
    
    User_list= df['user'].unique()
    Description_list= df['description'].unique()
    
    ToolBox= ['box_select', 'tap', 'pan', 'zoom_in', 'zoom_out', 'wheel_zoom', 'save', 'reset']
    ColorPalette= ['#20639B', '#3CAEA3', '#F6D55C', '#ED553B']
    
    
    #The creation of the plot, with the containing set of widgets
    plot_sum= figure(
        plot_height = 800, 
        plot_width= 1000,
        title = "Summation of Fixation Duration per Stimuli and User",
        x_range = User_list,
        y_axis_label= 'Fixation duration (sec)',
        tools = ToolBox )
    plot_sum.xaxis.major_label_orientation = orientation_xaxis
    
    
    plot_max= figure(
        plot_height = 800, 
        plot_width= 1000,
        title = "Maximum of Fixation Duration per Stimuli and User",
        x_range = User_list,
        y_axis_label= 'Fixation duration (sec)',
        tools = ToolBox )
    plot_max.xaxis.major_label_orientation = orientation_xaxis
    
    
    plot_mean= figure(
        plot_height = 800, 
        plot_width= 1000,
        title = "Mean of Fixation Duration per Stimuli and User",
        x_range = User_list,
        y_axis_label= 'Fixation duration (sec)',
        tools = ToolBox )
    plot_mean.xaxis.major_label_orientation = orientation_xaxis
    
    plot_sum.vbar(
        x="user",
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
        x="user",
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
        x="user",
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

    #Code needed to make stimuli selector 
    # stimuliList = stimuliListMaker(df)
    # stimuliSelect = Select(value=image_name, title='Stimuli', options=stimuliList)  
    
    Tools_vis1="pan,wheel_zoom, box_select, tap, reset, save"
    source = ColumnDataSource(data=get_data(df_stimuli, image_name))
    
    #Code for the user selection
    # user_list = userListMaker(df, image_name)
    # user_select = MultiSelect(title="Users:", value=["Everyone"],
                        # options=user_list ) #Don't forget to press shift or control (shift for everyone in between, control for selecting specific people) when selecting multiple users

    # userSelect_callback = CustomJS(args=dict(source=source, dataframe=ColumnDataSource(df), source_image=source_image, factor=factor, stimuli=stimuliSelect, source_sum=source_sum), code=
    #     """
    #         //Collect every piece of data and that is given in the dictionary and put it in a variable
    #         var datadf = dataframe.data
    #         var datasource_scatterplot = source.data;
    #         var userList = cb_obj.value;
    #         var dataimagesource= source_image.data;

    #         var image_height = dataimagesource['h'][0];
    #         var image_width = dataimagesource['w'][0];

    #         var stimuli_name=stimuli.value;

    #         var f = factor;

    #         //Empty all lists that are in the source so that we can add new values to them
    #         datasource_scatterplot['x']=[];
    #         datasource_scatterplot['y']=[];
    #         datasource_scatterplot['fixationtime']=[];
    #         datasource_scatterplot['radius']=[];
    #         datasource_scatterplot['user']=[];
    #         datasource_scatterplot['description']=[];
    #         datasource_scatterplot['color']=[];

    #         for (var i = 0; i < datadf['StimuliName'].length; i++) { //MAYBE LOOK INTO PANDAS FOR JAVASCRIPT AS IT WOULD BE A LOT CLEANER THAN THIS 
    #             if (userList[0] == "Everyone") {
    #                 if (datadf['StimuliName'][i] == stimuli_name ) {
    #                     datasource_scatterplot['x'].push(datadf['MappedFixationPointX'][i])
    #                     datasource_scatterplot['y'].push(image_height - datadf['MappedFixationPointY'][i])
    #                     datasource_scatterplot['fixationtime'].push(datadf['FixationDuration'][i])

    #                     // Check if Radius that we want to give to the circle isn't to big. Else cap it to 75 px and make the circle RED
    #                     var Radius = datadf['FixationDuration'][i]*f;
    #                     if (Radius > 75) {
    #                         datasource_scatterplot['radius'].push(75)
    #                         datasource_scatterplot['color'].push("RED")
    #                     }
    #                     else {
    #                         datasource_scatterplot['radius'].push(Radius)
    #                         datasource_scatterplot['color'].push("BLUE")
    #                     }
                        
    #                     datasource_scatterplot['user'].push(datadf['user'][i])
    #                     datasource_scatterplot['description'].push(datadf['description'][i])
    #                 }
    #             } else {
    #                 for (var j=0; j < userList.length; j++){
    #                     if (datadf['StimuliName'][i] == stimuli_name && datadf['user'][i] == userList[j]) {
    #                         datasource_scatterplot['x'].push(datadf['MappedFixationPointX'][i])
    #                         datasource_scatterplot['y'].push(image_height - datadf['MappedFixationPointY'][i])
    #                         datasource_scatterplot['fixationtime'].push(datadf['FixationDuration'][i])

    #                         // Check if Radius that we want to give to the circle isn't to big. Else cap it to 75 px and make the circle RED
    #                         var Radius = datadf['FixationDuration'][i]*f;
    #                         if (Radius > 75) {
    #                             datasource_scatterplot['radius'].push(75)
    #                             datasource_scatterplot['color'].push("RED")
    #                         }
    #                         else {
    #                             datasource_scatterplot['radius'].push(Radius)
    #                             datasource_scatterplot['color'].push("BLUE")
    #                         }
                            
    #                         datasource_scatterplot['user'].push(datadf['user'][i])
    #                         datasource_scatterplot['description'].push(datadf['description'][i])
    #                     }
    #                 }
    #             }
    #         }


    #         //Code for the changes made to the sum_barchart when selecting a stimuli
    #         var datasource_sum = source_sum.data;
    #         datasource_sum['user']=[];
    #         datasource_sum['description'] = [];
    #         datasource_sum['StimuliName'] =[];
    #         datasource_sum['FixationDuration']=[];
    #         datasource_sum['index']=[]
            

    #         for (var i = 1; i <= datadf['StimuliName'].length+1; i++) {
    #             if (userList[0] == "Everyone") {
    #                 if (datadf['StimuliName'][i-1] == stimuli_name) {
    #                     if (datadf['user'][i] != datadf['user'][i-1]) {
    #                         datasource_sum['user'].push(datadf['user'][i-1]);
    #                         datasource_sum['description'].push(datadf['description'][i-1]);
    #                         datasource_sum['StimuliName'].push(datadf['StimuliName'][i-1]);
    #                         datasource_sum['FixationDuration'].push(datadf['FixationDuration'][i-1]);
    #                         datasource_sum['index'].push(datasource_sum['user'].length-1);
    #                     } else {
    #                         datasource_sum['FixationDuration'][(datasource_sum['user'].length)-1] += datadf['FixationDuration'][i-1]
    #                     }   
    #                 }
    #             } else {
    #                 for (var j = 0; j < userList.length; j++){
    #                     if (userList[j] == datadf['user'][i-1]) {
    #                         if (datadf['StimuliName'][i-1] == stimuli_name) {
    #                             if (datadf['user'][i] != datadf['user'][i-1]) {
    #                                 datasource_sum['user'].push(datadf['user'][i-1]);
    #                                 datasource_sum['description'].push(datadf['description'][i-1]);
    #                                 datasource_sum['StimuliName'].push(datadf['StimuliName'][i-1]);
    #                                 datasource_sum['FixationDuration'].push(datadf['FixationDuration'][i-1]);
    #                                 datasource_sum['index'].push(datasource_sum['user'].length-1);
    #                             } else {
    #                                 datasource_sum['FixationDuration'][(datasource_sum['user'].length)-1] += datadf['FixationDuration'][i-1]
    #                             }      
    #                         }  
    #                     }
    #                 } 
    #             }
    #         }
    #         console.log(datasource_sum);
            

    #         source.change.emit();
    #         source_sum.change.emit();


    #     """
    # )

    # stimuliSelect_callback = CustomJS(args=dict(source=source, dataframe=ColumnDataSource(df), source_image=source_image, factor=factor, users=user_select, source_sum=source_sum), code=
    #     """
    #         users.value=["Everyone"]

    #         //Collect every piece of data and that is given in the dictionary and put it in a variable
    #         var datadf = dataframe.data
    #         var datasource = source.data;
    #         var userList = users;
    #         var dataimagesource= source_image.data;
            
    #         var new_stimuli = cb_obj.value;
    #         var location= ("./static/images/MetroMapsEyeTracking/stimuli/"+new_stimuli)
    #         dataimagesource['url'][0] = location    

    #         //Collect data on the new stimuli, so how wide is the corresponding image
    #         //COMMENT ON IMAGE SIZES: THE SIZE OF THE IMAGE DOESN'T CORRESPOND WITH THE DATAFRAME -_-. That's probably why we were also given a .csv File with the sizes of all the images. However this file is hard to make a correct dataframe from


    #         var new_image = new Image();
    #         new_image.src= location
    #         new_image.onload = function() {
    #             dataimagesource['h'][0] = this.height;
    #             dataimagesource['w'][0] = this.width;
    #         } 
    #         var image_height = dataimagesource['h'][0];
    #         var image_width = dataimagesource['w'][0];

    #         var f= factor;
    #         //console.log(userList[0]);
    #         //console.log(cb_obj.value);
    #         //console.log(datasource);
    #         //console.log(datadf);


    #         //Empty all lists that are in the source so that we can add new values to them
    #         datasource['x']=[];
    #         datasource['y']=[];
    #         datasource['fixationtime']=[];
    #         datasource['radius']=[];
    #         datasource['user']=[];
    #         datasource['description']=[];
    #         datasource['color']=[];
            

    #         //Add new values to the lists in the source
    #         for (var i = 0; i < datadf['StimuliName'].length; i++) { //MAYBE LOOK INTO PANDAS FOR JAVASCRIPT AS IT WOULD BE A LOT CLEANER THAN THIS 
    #             if (userList.value[0] == "Everyone") {
    #                 if (datadf['StimuliName'][i] == new_stimuli ) {
    #                     datasource['x'].push(datadf['MappedFixationPointX'][i])
    #                     datasource['y'].push(image_height - datadf['MappedFixationPointY'][i])
    #                     datasource['fixationtime'].push(datadf['FixationDuration'][i])

    #                     // Check if Radius that we want to give to the circle isn't to big. Else cap it to 75 px and make the circle RED
    #                     var Radius = datadf['FixationDuration'][i]*f;
    #                     if (Radius > 75) {
    #                         datasource['radius'].push(75)
    #                         datasource['color'].push("RED")
    #                     }
    #                     else {
    #                         datasource['radius'].push(Radius)
    #                         datasource['color'].push("BLUE")
    #                     }
                        
    #                     datasource['user'].push(datadf['user'][i])
    #                     datasource['description'].push(datadf['description'][i])
                        

    #                 }



    #             }
    #         }

            

    #         //https://appdividend.com/2019/04/11/how-to-get-distinct-values-from-array-in-javascript/
    #         //This function makes a list filter on unique values
    #         const unique = (value, index, self) => {
    #             return self.indexOf(value) === index
    #         }
    #         //Make a new List that will replace the old list with all users that look at the newly selected stimuli.
    #         var distinct_userList= ['Everyone'] 
    #         var distinctList=datasource['user'].filter(unique);
    #         for (var i=0; i < (distinctList.length); i++){
    #             //console.log(datasource['user'].filter(unique))
    #             distinct_userList.push(distinctList[i]);
    #         }
    #         users.options=distinct_userList;


    #         //Code for the changes made to the sum_barchart when selecting a stimuli
    #         var datasource_sum = source_sum.data;
    #         datasource_sum['user']=[];
    #         datasource_sum['description'] = [];
    #         datasource_sum['StimuliName'] =[];
    #         datasource_sum['FixationDuration']=[];
    #         datasource_sum['index']=[]
            

    #         for (var i = 1; i <= datadf['StimuliName'].length+1; i++) {
    #             if (datadf['StimuliName'][i-1] == new_stimuli) {
    #                 if (datadf['user'][i] != datadf['user'][i-1] || i==51) {
    #                     datasource_sum['user'].push(datadf['user'][i-1]);
    #                     datasource_sum['description'].push(datadf['description'][i-1]);
    #                     datasource_sum['StimuliName'].push(datadf['StimuliName'][i-1]);
    #                     datasource_sum['FixationDuration'].push(datadf['FixationDuration'][i-1]);
    #                     datasource_sum['index'].push(datasource_sum['user'].length-1);
    #                 } else {
    #                     datasource_sum['FixationDuration'][(datasource_sum['user'].length)-1] += datadf['FixationDuration'][i-1]
    #                 }   
    #             }
    #         }

    #         console.log(datasource_sum);
            
    #         //source.change.emit() and source_image.change.emit() are needed to actually update the data that's in the source
    #         //users.options=["Everyone", "P1"];
    #         //users.value=["Everyone"]
    #         source.change.emit();
    #         source_image.change.emit();
    #         source_sum.change.emit();

    #     """)

    #JS_Callbacks, so basically calling an update function that runs on Javascript -_-
    # stimuliSelect.js_on_change('value', stimuliSelect_callback)
    # user_select.js_on_change('value', userSelect_callback)
    # File_Input.js_on_change('value', fileInput_callback)

    scatterplot = make_plot(Tools_vis1, source)
    # controls = column(stimuliSelect, user_select)
    layout = column(row(scatterplot), Tabben)
    # curdoc.add_root(layout)
    script, div = components(layout, wrap_script=False)    
    return render_template('about.html', script=script, div=div, userdata= userListMaker(df, image_name), stimulidata=stimuliListMaker(df), activeusersdata=user_list, activestimulidata=[image_name])
    #return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)