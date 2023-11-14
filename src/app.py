# Step 1: Import the required libraries
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
import pandas as pd
from collections import Counter
import json

TEMPLATE = "plotly_white"

df = pd.read_json(r"data/modified_dataset_data_all.json")

file = open(r"data/geoBoundaries-MYS-ADM1.geojson")
geo_json = json.load(file)
file.close()

app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#Layout
app.layout = html.Div(
    [
    html.P(id="placeholder", style={"display":"none"}), #dash hack to get around callback for graph that don't need to use callback
    dbc.Row(
        html.Div([
                html.H1("Search Result of Data Analyst/Data Scientist from Linkedin (MY/SG)", className="center_alignment"),
                html.H4(["A set of information related to the search result of data analyst/data scientist from Linkedin.",html.Br(),
                         "Data is obtained during October 2023 on the publicly available job posting webpage of Linkedin " +
                         "and the dataset consist of 1000 rows from Malaysia and Singapore respectively."], className="center_alignment",style={"margin-top":"10px", "margin-bottom":"20px"}),
            ], className="container topic_header")
        ),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    dcc.Graph(id='experience_seniority_graph'),
                    ]), className="center_alignment graph"),
            dbc.Col(
                html.Div([
                    html.P(["Based on the result, there are mostly lack of correlation between the definition of each seniority level "+
                           "and the experience required by the employers when experiences are mentioned in numerical value. However, the average experienced required overall does increases " +
                           "in relation to the seniority level. Interesting observations: "]),
                    
                    html.P([html.B("Entry level jobs that mostly require at least 1 year of experience ", style={"color":"#0d6efd"}),
                           ", and ", 
                           html.B("mid-senior level job that is open for individuals with 0 year of experience.", style={"color":"#20c997"})]),
                    html.Br(),
                    html.P(html.Span(["Note:", html.Br(),
                            "The methods to aggregate the information is possibly not fully inclusive due to edge cases, improvement could be done through trained model. "+
                            "The method also does not convert keyword such as 'fresh graduate' as 'at least 0 year of experience', inclusion of this information may skew the result by varying degrees."], className="note"))
                    ]),width={"size":"auto"} , className="container content center_alignment"),
            ],
        align="start", className=""),
    
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="skills_graph"),className="center_alignment graph", style={"max-width":"100%","width":"100%", "margin-bottom":"0px"}),
            ],
        align="start"),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    html.P(["The expected broad skills expected from an employee is", html.B(" Python ", style={"color":"#edbf33"}), "and", html.B(" SQL ", style={"color":"#edbf33"}), 
                           "knowledge, with emphasis on AI and cloud knowledge, with", html.B(" AWS ", style={"color":"#0dcaf0"}), "being the most popular cloud platform that employer expects the employee to posess."]),
                    
                    html.P([html.B("Linux, Javascripts and Spark ", style={"color":"#0dcaf0"}), "proficiencies are oftenly expected by the employer as well, along with abilities into ", html.B("finance, statistics and mathematics.", style={"color":"#0dcaf0"}), 
                            html.B(" Data visualisation ", style={"color":"#B5B5B5"}), "ability is occasionally required but is apparantly not that high of a priority."])
                    ]),style={"max-width":"100%", "width":"100%", "height":"auto", "margin-top":"0px"} , className="content center_alignment container"),
            ],
        align="start"),
    
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="job_posting_map"),className="center_alignment graph"),
            dbc.Col(
                html.Div([
                    html.P(["More than half of the job posting from Malaysia comes from", html.B(" Kuala Lumpur ", style={"color":"#0dcaf0"}), "followed by ", html.B("Selangor, Penang", style={"color":"#0dcaf0"}), " and ", html.B("Johor. ", style={"color":"#0dcaf0"})]),
                    html.P(["Most other states have low level of job posting related to Data Scientist/Data Analyst possibly due to low demand, or/and low usage of Linkedin, no conclusion can be reached from the current dataset."]),
                    html.Br(),
                    html.Span(["Note:", html.Br(), "Singapore is not included due to the nature of the dataset making Singapore related data half of the dataset thus the comments will be related to Malaysia only."],className="note")
                    ]),width={"size":"auto"} , className="container content center_alignment"),
            ], 
        align="start", className=""),
    
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    html.P(["Majority of the employment types are of", html.B(" Full-time ", style={"color":"#0dcaf0"}), "and", html.B(" Contractual ", style={"color":"#0dcaf0"}), ", with all the", html.B(" fresh graduate suitable (0 experience) ", style={"color":"#ffffe0"}), "job found in the", html.B(" Full-time ", style={"color":"#0dcaf0"}), "category."]),
                    html.P(["One observation we can make here is that, majority of the works expect around", html.B(" 3 years of experiences ", style={"color":"#20c997"}), "minimum."]),
                    html.Br(),
                    html.Span(["Note:", html.Br(), "Due to some of the data not having experience stated in numerical form, we assume there is no such data, and thus are not shown in the 'Percentage of Experience Requirement to Employment Type' graph." +
                               "an example to this would be the 'Internship' employment type. "],className="note")
                    ]),width={"size":"auto"} , className="container content center_alignment"),
            dbc.Col(dcc.Graph(id="employment_type_graph"),className="graph center_alignment"),
            dbc.Col(dcc.Graph(id="experience_percentage_to_employment_type_graph"),className="graph center_alignment")
            ], 
        align="start", className="")
    ]
)

#Functions
@app.callback(
    Output("experience_seniority_graph", "figure"),
    Input("placeholder","children")
)
def update_experience_ridgeline(value):
    orders=["Internship", "Entry level", "Associate", "Mid-Senior level", "Executive", "Director", "Not Applicable"]
    
    experience_df = df[["Seniority level","Experience","Employment type"]]
    experience_df = experience_df.dropna()
    experience_df["Experience"] = experience_df["Experience"].astype(int)
    
    fig = go.Figure()
    
    for seniority in orders:
        df_filtered = experience_df[experience_df["Seniority level"]==seniority]
        
        if len(df_filtered) != 0:
            variance = df_filtered["Experience"].var()
            min_width = 2
            width = min_width if variance < min_width else variance**0.5
            
            fig.add_trace(go.Violin(x=df_filtered["Experience"], 
                                    y=df_filtered["Seniority level"], 
                                    width = width,
                                    hoverinfo="skip",
                                    name=seniority))

    fig.update_traces(meanline_visible = True, 
                      orientation='h', 
                      side='positive', 
                      points="all",
                      pointpos=0.5)
    
    fig.update_traces(marker=dict(opacity=0.5))
    
    fig.update_layout(template=TEMPLATE)
    
    fig.update_layout(xaxis={"range":[-0.5,15]})
    
    fig.update_layout(xaxis_title_text = "Experience (Year)",
                      xaxis_title_font = {"size":15})
    
    fig.update_layout(yaxis_title_text = "Seniority Level",
                      yaxis_title_font = {"size":15})
    
    fig.update_layout(title="Seniority Level to Experience Requirement",
                      title_font = {"size":20})

    
    return fig


@app.callback(
    Output("skills_graph","figure"),
    Input("placeholder","children")
)
def update_skill_bar(value):
    skill_keyword = set({'python', 'sql', 'ml', 'ai', 'java', 'cloud', 'agile', 'aws', 'linux', 'javascript', 'finance', 'statistics', 'powerbi', 'mathematics', 'spark', 'etl', 'tableau', 'dl', 'hadoop', 'sap', 'uat', 'sas', 'microsoft office', 'erp', 'economics', 'vba', 'microsoft excel', 'google sheet'})
    
    token_counter = Counter()

    for description in df["Description"]:
        paragraph = " ".join(description)
        paragraph = paragraph.lower()
        
        for skill in skill_keyword:
            prefix_suffix = [" {} ","/{}","{}/","{}.",".{}",",{}","{},","({}","{})","[{}","{}]","{}s"]
            if any(modifier.format(skill) in paragraph for modifier in prefix_suffix):
                token_counter.update([skill])
    
    token_counter_new = Counter()
    equivalent_dict = {
                        "artificial intelligence": "ai",
                        "power bi": "powerbi",
                        "machine learning": "ml",
                        "deep learning":"dl"
                    }
    
    for key, value in token_counter.items():
        if key in equivalent_dict:
            token_counter_new[equivalent_dict[key]] += value
        else:
            token_counter_new[key] += value
    
    token_counter = token_counter_new
    
    skill_df = pd.DataFrame.from_dict(token_counter,orient="index")
    skill_df = skill_df.reset_index()
    skill_df.columns = ["Skill","Count"]
    
    #changing bar properties
    skill_df = skill_df.sort_values(by=["Count"], ascending=False)
    
    colors = ["#edbf33"]*5 #Lizard Breath (Yellow)
    colors += ["#0d88e6"]*10 #Out of the Blue (Blue)
    
    try:
        colors += ["#cbd6e4"]*(len(skill_df)-15) #Gray
    except:
        pass
    
    
    #updating the bar plot
    fig = go.Figure()
    fig.add_trace(go.Bar(x=skill_df["Skill"],
                         y=skill_df["Count"],
                         marker_color=colors))
    
    fig.update_layout(template=TEMPLATE)
    
    fig.update_layout(title="Skill Mentioned in Count",
                      title_font = {"size":20})
    
    fig.update_layout(xaxis_title_text = "Skill",
                      xaxis_title_font = {"size":15})
    
    fig.update_layout(yaxis_title_text = "Count",
                      yaxis_title_font = {"size":15})
    
    return fig

@app.callback(
    Output("employment_type_graph","figure"),
    Input("placeholder","children")
)
def update_employment_type_bar(value):
    job_type_df = df.groupby(["Employment type"]).size().reset_index(name="Count")
    
    fig = px.bar(job_type_df, x="Employment type", y="Count")
    
    fig.update_yaxes(type="log", dtick=1)
    
    fig.update_layout(template=TEMPLATE)
    
    fig.update_layout(title="Distribution of Employment Type",
                      title_font = {"size":20})
    
    fig.update_layout(xaxis_title_text = "Employment Type",
                      xaxis_title_font = {"size":15})
    
    fig.update_layout(yaxis_title_text = "Count",
                      yaxis_title_font = {"size":15})
    
    return fig

@app.callback(
    Output("experience_percentage_to_employment_type_graph","figure"),
    Input("placeholder","children")
)
def update_experience_percentage_to_employment_type_bar(value):
    job_type_to_exp_df = df.groupby(["Employment type","Experience"]).size().reset_index(name="Count")
    job_type_to_exp_df = job_type_to_exp_df.groupby(["Employment type","Experience"]).agg({"Count":"sum"})
    job_type_to_exp_df["Percentage"] = job_type_to_exp_df.groupby(level=0).apply(lambda x: 100*x/x.sum()).reset_index(level=0, drop=True)
    job_type_to_exp_df = job_type_to_exp_df.reset_index()
    
    
    fig = px.bar(job_type_to_exp_df, x="Employment type", y="Percentage", color="Experience", color_continuous_scale="deep")

    fig.update_layout(template=TEMPLATE)
    
    fig.update_layout(title="Percentage of Experience Requirement <br>to Employment Type",
                      title_font = {"size":20})
    
    fig.update_layout(xaxis_title_text = "Employment Type",
                      xaxis_title_font = {"size":15})
    
    fig.update_layout(yaxis_title_text = "Percentage (%)",
                      yaxis_title_font = {"size":15})
    
    return fig
    

@app.callback(
    Output("job_posting_map","figure"),
    Input("placeholder","children")
)
def update_job_posting_map(value):
    location_names = ['Selangor','Johor','Kuala Lumpur','Malacca','Negeri Sembilan','Sabah','Sarawak','Kelantan','Putrajaya','Terengganu','Pahang','Kedah','Perlis','Perak','Penang','Labuan','Singapore']
    
    df_location_count = df.groupby("Location").count()["Title"]
    location_counter = Counter({location:0 for location in location_names})
    location_counter.update(dict(df_location_count))
    df_location_count = pd.DataFrame({"Location":location_counter.keys(),"Count":list(location_counter.values())})
    df_location_count["Count"] = df_location_count["Count"].apply(lambda x:x+0.1)
    
    
    fig = px.choropleth_mapbox(
        data_frame=df_location_count,
        featureidkey="properties.shapeName",
        color=np.log10(df_location_count["Count"]),
        color_continuous_scale="deep",
        color_continuous_midpoint=1,
        geojson=geo_json,
        locations="Location",
        center={"lat": 3.9434837, "lon": 109.1797548},
        zoom=5,
        opacity=0.8,
        hover_name = "Location",
        hover_data={
            "Job Posting Count": df_location_count["Count"] - 0.1,
            "Location": False
            }
        )
    
    #print(fig.data[0].hovertemplate)
    
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Job Posting Count=%{customdata[0]}<extra></extra>")
    
    fig.update_layout(
        coloraxis_colorbar=dict(
            tickvals=[-1, 0, 1, 2, 3],
            ticktext=['0', '1', '10', '100', '1000'],
            title="Job Posting Count"
            )
        )

    
    fig.update_layout(
        mapbox_style="carto-positron",
        )

    fig.update_layout(title="Malaysia Job Posting Distribution",
                      title_font = {"size":20})

    return fig

#Main
if __name__ == '__main__':
    app.run_server(debug=True)