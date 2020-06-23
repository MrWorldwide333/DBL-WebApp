from flask import Flask, render_template, url_for, request
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


app = Flask(__name__)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/vis")
def vis():
    return render_template('vis.html')

@app.route("/about", methods=["POST", "GET"])
def about():

#     #Making
#     #THIS CELL IS THE ACTUAL CODE, THE OTHER CELLS ARE FOR PRACTICE!!!!!!!!
#     #Code that is commented out in this cell is old code, it's there as a backup for if all fails
#     file_name="all_fixation_data_cleaned_up.csv"
#     if request.method == "POST":
#         file = request.files["FileSelect"]
#         if file.filename == '':
#             print("No file to be found, We'll use the example dataset")
#         else:
#             print(file.filename)
#             file_name=file.filename
        
        
#     image_data= pd.read_excel("./static/images/MetroMapsEyeTracking/stimuli/resolution.xlsx", encoding='latin1')
#     df_images= image_data.copy()

#     image_name="01_Antwerpen_S1.jpg"
#     image_location = "./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)
#     image= Image.open(image_location) #Opens the image location using the Image library
#     image_width, image_height = image.size #image.size is width, height
#     source_image = ColumnDataSource(dict(
#             url = ["./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)],
#             x  = [0],
#             y  = [image_height],
#             w  = [image_width],
#             h  = [image_height]
#         ))
    
#     Eyetracking_data = pd.read_csv(file_name, encoding='latin1', sep="\t")
#     Eyetracking_data
#     df = Eyetracking_data.copy()
    
#     factor=0.05 #Factor to make non outlier Fixationtime values into the right radius size

#     def stimuliListMaker(dataframe): #Makes a list with all stimulinames for 
#         images=dataframe["StimuliName"].unique().copy()
#         menu=[]
#         for i in images:
#             menu.append(i)
#         return menu
        
#     #Used for user selection
#     def userListMaker(dataframe, stimuli):
#         user_series = dataframe["user"][dataframe["StimuliName"] == stimuli].unique().copy()
#         user_list=[]
#         user_list.append("Everyone")
#         for i in user_series:
#             user_list.append(i)
#         return user_list
    
# #     def activeListMaker(user_list):
# #         active_list=[]
# #         for i in range(0, len(user_list)):
# #             active_list.append(i)
# #         return active_list
    
#     def get_data(df, figure, users=["Everyone"]):
#         if users[0] == "Everyone":
#             X = df["MappedFixationPointX"][df["StimuliName"] == figure] #Select every x-coordinate from the chosen map
#             Y = image_height - df["MappedFixationPointY"][df["StimuliName"] == figure] #Select every y-coordinate from the chosen map
#             Fixationtime = df["FixationDuration"][df["StimuliName"] == figure] #Collect every fixationtime per timestamp for the chosen map
#             Description = df["description"][df["StimuliName"] == figure] #Collects the descriptions from the database
#             User = df["user"][df["StimuliName"] == figure] #Collects about which user this dot is.
#             Radius = [] #Create empty list where the radius of the circle will be put in
#             Color = [] #Create empty list where the right color for the circle will be assigned
            
#         else:
#             X = df["MappedFixationPointX"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Select every x-coordinate from the chosen map
#             Y = image_height - df["MappedFixationPointY"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Select every y-coordinate from the chosen map
#             Fixationtime = df["FixationDuration"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Collect every fixationtime per timestamp for the chosen map
#             Description = df["description"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Collects the descriptions from the database
#             User = df["user"][(df["StimuliName"] == figure) & (df["user"] == users[0])] #Collects about which user this dot is.
#             Radius = [] #Create empty list where the radius of the circle will be put in
#             Color = [] #Create empty list where the right color for the circle will be assigned
            
#             for u in range(1, len(users)):
#                 X1 = df["MappedFixationPointX"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Select every x-coordinate from the chosen map
#                 Y1 = image_height - df["MappedFixationPointY"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Select every y-coordinate from the chosen map
#                 Fixationtime1 = df["FixationDuration"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Collect every fixationtime per timestamp for the chosen map
#                 Description1 = df["description"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Collects the descriptions from the database
#                 User1 = df["user"][(df["StimuliName"] == figure) & (df["user"] == users[u])] #Collects about which user this dot is.
                
#                 X = X.append(X1) #Add X1 to X
#                 Y = Y.append(Y1) #Add Y1 to Y
#                 Fixationtime = Fixationtime.append(Fixationtime1) #Add Fixationtime1 to Fixationtime
#                 Description = Description.append(Description1) #Add Description1 to Description
#                 User = User.append(User1) #Add User1 to User
                
                
                
#         #This for loop will assign the radius and color to each circle
#         for i in Fixationtime: 
#             r= i * factor #radius = Fixationtime[i] * factor
#             if r > 75: #If radius is above 75 px than make the radius 75 px and make the circle red. Else just make the circle blue.
#                 r=75
#                 Color.append("RED")
#             else:
#                 Color.append("BLUE")
#             Radius.append(r)
            
#         data = dict(
#             x= X,
#             y= Y,
#             fixationtime= Fixationtime,
#             radius= Radius,
#             user= User,
#             description= Description,
#             color = Color
#         )

#         return data #Returns a dictionary

#     def make_plot(Tools, source):
#         #The Hover-tool shows the Tooltips as shown here. The "@" stands for the data collected from the source
#         Tooltips = [ 
#             ("(x, y)", "(@x, @y)"),
#             ("Fixation duration", "@fixationtime ms"),
#             ("user", "@user"),
#             #("description", "@description")
#         ]

#         #Creation of the figure
#         plot = figure(x_range=(0,image_width), y_range=(0,image_height), tooltips=Tooltips, tools=Tools)
        
        
#         image1 = ImageURL(url="url", x="x", y="y", w="w", h="h", anchor="top_left")
#         plot.add_glyph(source_image, image1)
#         # plot.image_url(url=[image_location], x=0, y=image_height, w=image_width, h=image_height)
#         plot.circle(x='x', y='y', size='radius', color='color', alpha=0.2, source=source)
#         return plot
    
    
#     #The update functions:
# #     def update_plot_stimuli(attr, old, new):
# # #         try: #Will happen if dataset is selected, This is the case the first time because an example dataset is selected
# #         image = new #Image is selected value
# #         df = pd.read_csv(File_Input.filename, encoding='latin1', sep='\t')
# #         data_new = get_data(df, image)             

# #         #Change user selection to users of this plot stimuli and select the previously selected value if it exists.
        
# #         user_select.options = userListMaker(df, image)
# #         user_select.value = ["Everyone"]
# #         source.data = data_new
# # #         except: #Will happen if no dataset is selected.
# # #             print("error")
        
    
#     # def update_plot_dataset(attr, old, new):
#     #     try: #Will happen if a dataset is selected
#     #         dataframe = pd.read_csv(File_Input.filename, encoding='latin1', sep='\t')
            
#     #         #Get the first image from the list to already show a map for the plot
#     #         image_name = dataframe["StimuliName"][0] 
#     #         image_location = "./static/images/MetroMapsEyeTracking/stimuli/{}".format(image_name)
#     #         image= Image.open(image_location)
#     #         image_width, image_height = image.size
            
#     #         data_new = get_data(dataframe, image_name)
            
#     #         #Change the stimuliSelection menu so that only the images from this dataset can be selected
#     #         stimuliSelect.options=stimuliListMaker(dataframe)
#     #         stimuliSelect.value=image_name
            
#     #         #Change the user_select menu so that it only shows the users for this dataset with the first stimuli of the new dataset. Also resets the chosen value to "Everyone"
#     #         user_select.options=userListMaker(dataframe, image_name)
#     #         user_select.value=["Everyone"]
            
#     #         source.data = data_new
        
#     #     except: #Will happen if no dataset is selected
#     #         print("error")
    
#     #Potential user selection code
#     # def update_plot_user(attr, old, new):
#     #     active_list = new
#     #     dataframe = pd.read_csv(File_Input.filename, encoding='latin1', sep='\t')
#     #     stimuli = stimuliSelect.value
#     #     data_new = get_data(dataframe, stimuli, active_list)
#     #     source.data= data_new


    
    
#     #Code needed to make stimuli selector 
#     stimuliList = stimuliListMaker(df)
#     stimuliSelect = Select(value=image_name, title='Stimuli', options=stimuliList)
#     # stimuliSelect.on_change('value', update_plot_stimuli)
    

#     #Code needed for file upload system
#     # File_Input = FileInput(filename="all_fixation_data_cleaned_up.csv", accept=".csv")
#     # File_Input.on_change('value', update_plot_dataset)
    
    
#     Tools_vis1="pan,wheel_zoom, box_select, tap, reset, save"
#     source = ColumnDataSource(data=get_data(df, image_name))
    
#     #Code for the user selection
#     user_list = userListMaker(df, image_name)
#     user_select = MultiSelect(title="Users:", value=["Everyone"],
#                         options=user_list ) #Don't forget to press shift or control (shift for everyone in between, control for selecting specific people) when selecting multiple users
#     # user_select.on_change("value", update_plot_user)
    
#     # fileInput_callback = CustomJS(args=dict(source=source, dataframe=ColumnDataSource(df), factor=factor, stimuli=stimuliSelect, users=user_select, FileInput=File_Input), code= 
#     #     """
            
#     #         //Collect every piece of data and that is given in the dictionary and put it in a variable
#     #         var File_name=FileInput.filename;
#     #         console.log(File_name);
#     #         var oldDatadf = dataframe.data;
#     #         var datasource = source.data;
#     #         var userList = users.value;
#     #         var newDatadf = atob(cb_obj.value);
#     #         console.log(newDatadf);
            

#     #         var f = factor;
    
#     #         //Empty all lists that are in the source so that we can add new values to them
#     #         datasource['x']=[];
#     #         datasource['y']=[];
#     #         datasource['fixationtime']=[];
#     #         datasource['radius']=[];
#     #         datasource['user']=[];
#     #         datasource['description']=[];
#     #         datasource['color']=[];


#     #     """
#     # )

#     userSelect_callback = CustomJS(args=dict(source=source, dataframe=ColumnDataSource(df), source_image=source_image, factor=factor, stimuli=stimuliSelect), code=
#         """
#             //Collect every piece of data and that is given in the dictionary and put it in a variable
#             var datadf = dataframe.data
#             var datasource = source.data;
#             var userList = cb_obj.value;
#             var dataimagesource= source_image.data;

#             var image_height = dataimagesource['h'][0];
#             var image_width = dataimagesource['w'][0];

#             var stimuli_name=stimuli.value;

#             var f = factor;

#             //Empty all lists that are in the source so that we can add new values to them
#             datasource['x']=[];
#             datasource['y']=[];
#             datasource['fixationtime']=[];
#             datasource['radius']=[];
#             datasource['user']=[];
#             datasource['description']=[];
#             datasource['color']=[];

#             for (var i = 0; i < datadf['StimuliName'].length; i++) { //MAYBE LOOK INTO PANDAS FOR JAVASCRIPT AS IT WOULD BE A LOT CLEANER THAN THIS 
#                 if (userList[0] == "Everyone") {
#                     if (datadf['StimuliName'][i] == stimuli_name ) {
#                         datasource['x'].push(datadf['MappedFixationPointX'][i])
#                         datasource['y'].push(image_height - datadf['MappedFixationPointY'][i])
#                         datasource['fixationtime'].push(datadf['FixationDuration'][i])

#                         // Check if Radius that we want to give to the circle isn't to big. Else cap it to 75 px and make the circle RED
#                         var Radius = datadf['FixationDuration'][i]*f;
#                         if (Radius > 75) {
#                             datasource['radius'].push(75)
#                             datasource['color'].push("RED")
#                         }
#                         else {
#                             datasource['radius'].push(Radius)
#                             datasource['color'].push("BLUE")
#                         }
                        
#                         datasource['user'].push(datadf['user'][i])
#                         datasource['description'].push(datadf['description'][i])
#                     }
#                 } else {
#                     for (var j=0; j < userList.length; j++){
#                         if (datadf['StimuliName'][i] == stimuli_name && datadf['user'][i] == userList[j]) {
#                             datasource['x'].push(datadf['MappedFixationPointX'][i])
#                             datasource['y'].push(image_height - datadf['MappedFixationPointY'][i])
#                             datasource['fixationtime'].push(datadf['FixationDuration'][i])

#                             // Check if Radius that we want to give to the circle isn't to big. Else cap it to 75 px and make the circle RED
#                             var Radius = datadf['FixationDuration'][i]*f;
#                             if (Radius > 75) {
#                                 datasource['radius'].push(75)
#                                 datasource['color'].push("RED")
#                             }
#                             else {
#                                 datasource['radius'].push(Radius)
#                                 datasource['color'].push("BLUE")
#                             }
                            
#                             datasource['user'].push(datadf['user'][i])
#                             datasource['description'].push(datadf['description'][i])
#                         }
#                     }
#                 }
#             }
#             source.change.emit();


#         """
#     )

#     stimuliSelect_callback = CustomJS(args=dict(source=source, dataframe=ColumnDataSource(df), source_image=source_image, factor=factor, users=user_select), code=
#         """
#             users.value=["Everyone"]

#             //Collect every piece of data and that is given in the dictionary and put it in a variable
#             var datadf = dataframe.data
#             var datasource = source.data;
#             var userList = users;
#             var dataimagesource= source_image.data;
            
#             var new_stimuli = cb_obj.value;
#             var location= ("./static/images/MetroMapsEyeTracking/stimuli/"+new_stimuli)
#             dataimagesource['url'][0] = location    

#             //Collect data on the new stimuli, so how wide is the corresponding image
#             //COMMENT ON IMAGE SIZES: THE SIZE OF THE IMAGE DOESN'T CORRESPOND WITH THE DATAFRAME -_-. That's probably why we were also given a .csv File with the sizes of all the images. However this file is hard to make a correct dataframe from


#             var new_image = new Image();
#             new_image.src= location
#             new_image.onload = function() {
#                 dataimagesource['h'][0] = this.height;
#                 dataimagesource['w'][0] = this.width;
#             } 
#             var image_height = dataimagesource['h'][0];
#             var image_width = dataimagesource['w'][0];

#             var f= factor;
#             //console.log(userList[0]);
#             //console.log(cb_obj.value);
#             //console.log(datasource);
#             //console.log(datadf);


#             //Empty all lists that are in the source so that we can add new values to them
#             datasource['x']=[];
#             datasource['y']=[];
#             datasource['fixationtime']=[];
#             datasource['radius']=[];
#             datasource['user']=[];
#             datasource['description']=[];
#             datasource['color']=[];
            

#             //Add new values to the lists in the source
#             for (var i = 0; i < datadf['StimuliName'].length; i++) { //MAYBE LOOK INTO PANDAS FOR JAVASCRIPT AS IT WOULD BE A LOT CLEANER THAN THIS 
#                 if (userList.value[0] == "Everyone") {
#                     if (datadf['StimuliName'][i] == new_stimuli ) {
#                         datasource['x'].push(datadf['MappedFixationPointX'][i])
#                         datasource['y'].push(image_height - datadf['MappedFixationPointY'][i])
#                         datasource['fixationtime'].push(datadf['FixationDuration'][i])

#                         // Check if Radius that we want to give to the circle isn't to big. Else cap it to 75 px and make the circle RED
#                         var Radius = datadf['FixationDuration'][i]*f;
#                         if (Radius > 75) {
#                             datasource['radius'].push(75)
#                             datasource['color'].push("RED")
#                         }
#                         else {
#                             datasource['radius'].push(Radius)
#                             datasource['color'].push("BLUE")
#                         }
                        
#                         datasource['user'].push(datadf['user'][i])
#                         datasource['description'].push(datadf['description'][i])
                        

#                     }



#                 }
#             }

            

#             //https://appdividend.com/2019/04/11/how-to-get-distinct-values-from-array-in-javascript/
#             //This function makes a list filter on unique values
#             const unique = (value, index, self) => {
#                 return self.indexOf(value) === index
#             }
#             //Make a new List that will replace the old list with all users that look at the newly selected stimuli.
#             var distinct_userList= ['Everyone'] 
#             var distinctList=datasource['user'].filter(unique);
#             for (var i=0; i < (distinctList.length); i++){
#                 //console.log(datasource['user'].filter(unique))
#                 distinct_userList.push(distinctList[i]);
#             }
#             users.options=distinct_userList;
            
            
#             //source.change.emit() and source_image.change.emit() are needed to actually update the data that's in the source
#             //users.options=["Everyone", "P1"];
#             //users.value=["Everyone"]
#             source.change.emit();
#             source_image.change.emit();
#         """)

#     #JS_Callbacks, so basically calling an update function that runs on Javascript -_-
#     stimuliSelect.js_on_change('value', stimuliSelect_callback)
#     user_select.js_on_change('value', userSelect_callback)
#     # File_Input.js_on_change('value', fileInput_callback)

#     scatterplot = make_plot(Tools_vis1, source)
#     controls = column(stimuliSelect, user_select)
#     layout = row(scatterplot, controls)
#     # curdoc.add_root(layout)








    script, div = components(layout, wrap_script=False)
    return render_template('about.html', script=script, div=div)
    #return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)