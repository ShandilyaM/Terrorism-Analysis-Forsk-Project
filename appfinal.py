#Terrorism analysis with insights

#importing libraries
import pandas as pd
import dash
import dash_html_components as html
from dash.dependencies import Input, State, Output 
import webbrowser
import dash_core_components as dcc 
import plotly.graph_objects as go  
import plotly.express as px
from dash.exceptions import PreventUpdate


app = dash.Dash()


def load_data():
  dataset_name = "global_terror.csv"

  pd.options.mode.chained_assignment = None
  
  #reading the csv file  
  global df
  df = pd.read_csv(dataset_name)
  print(df.head(5))
  
  #global variables
  global month_list
  month = {"January":1,"February": 2,"March": 3,"April":4,"May":5,"June":6,
         "July": 7,"August":8,"September":9,"October":10,"November":11,
          "December":12}
  month_list= [{"label":key, "value":values} for key,values in month.items()]
  global date_list
  date_list = [x for x in range(1, 32)]
  global region_list
  region_list = [{"label": str(i), "value": str(i)}  for i in sorted( df['region_txt'].unique().tolist())]
  global country_list
  country_list = df.groupby("region_txt")["country_txt"].unique().apply(list).to_dict()
  global state_list
  state_list = df.groupby("country_txt")["provstate"].unique().apply(list).to_dict()
  global city_list
  city_list  = df.groupby("provstate")["city"].unique().apply(list).to_dict()
  global attack_type_list
  attack_type_list = [{"label": str(i), "value": str(i)}  for i in df['attacktype1_txt'].unique().tolist()]
  global year_list
  year_list = sorted ( df['iyear'].unique().tolist()  )
  global year_dict
  year_dict = {str(year): str(year) for year in year_list}
  
  #chart dropdown options
  global chart_dropdown_values
  chart_dropdown_values = {"Terrorist Organisation":"gname","Target Nationality":"natlty1_txt", 
                            "Target Type":"targtype1_txt","Attack Type":"attacktype1_txt", 
                            "Weapon Type":"weaptype1_txt","Region":'region_txt', 
                            "Country Attacked":"country_txt"}
                              
  chart_dropdown_values = [{"label":keys,"value":value} for keys, value in chart_dropdown_values.items()]
 

def open_browser():
  #opening default browser  
  webbrowser.open_new('http://127.0.0.1:8050/')

#layout of the page
def create_app_ui():
  main_layout = html.Div([
  html.H1(id='Main_title',children = "TERRORISM ANALYSIS AND FINDING INSIGHTS"),
  dcc.Tabs(id="maintabs", value="tab1",parent_className="customtabs",children=[
      dcc.Tab(label="Map Tool" ,id="maptool",value="tab1",className='first-tab',selected_className='first-sel',
        children=[
          dcc.Tabs(id = "mapsubtabs", value="tab2",children = [
              dcc.Tab(label="World Map Tool", id="worldmap", value="tab2",className="second-tab",selected_className="second-sel"),
              dcc.Tab(label="India Map Tool", id="indiamap", value="tab3",className="second-tab",selected_className="second-tab")
              ],colors={"border":"white","primary":"black","background":"cornsilk"}),
          html.Br(),
          dcc.Dropdown(id='month-dropdown',options=month_list,placeholder='Select Month',multi = True),
          dcc.Dropdown(id='date-dropdown',placeholder='Select Day',multi = True),
          dcc.Dropdown(id='region-dropdown',options=region_list,placeholder='Select Region',multi = True),
          dcc.Dropdown(id='country-dropdown',options=[{'label': 'All', 'value': 'All'}],placeholder='Select Country',multi = True),
          dcc.Dropdown(id='state-dropdown',options=[{'label': 'All', 'value': 'All'}],placeholder='Select State',multi = True),
          dcc.Dropdown(id='city-dropdown',options=[{'label': 'All', 'value': 'All'}],placeholder='Select City',multi = True),
          dcc.Dropdown(id='attacktype-dropdown',options=attack_type_list,placeholder='Select Attack Type',multi = True),

          html.H4('Select the Year', id='year_title'),
          dcc.RangeSlider(id='year-slider',
                          min=min(year_list),
                          max=max(year_list),
                          value=[min(year_list),max(year_list)],
                          marks=year_dict,step=None),
          html.Br()
          ]),
          dcc.Tab(label="Chart Tool",id="charttool", value="chart",className="first-sel",selected_className="first-sel",
            children=[
          dcc.Tabs(id="chartsubtabs",value="tab4",children = [
              dcc.Tab(label="World Chart Tool", id="worldchart",value="tab4",className="second-tab",selected_className="second-sel"),          
              dcc.Tab(label="India Chart Tool", id="indiachart",value="tab5",className="second-tab",selected_className="second-sel")],
              colors={"border":"white","primary":"black","background":"#e6ffff"}),
              html.Br(),
              dcc.Dropdown(id="chart_dropdown", options = chart_dropdown_values, placeholder="Select option", value = "region_txt"), 
              html.Br(),
              html.Br(),
              html.Hr(),
              dcc.Input(id="search", placeholder="Search Filter"),
              html.Hr(),
              html.Br(),
              dcc.RangeSlider(
                      id='chart_year_slider',
                      min=min(year_list),
                      max=max(year_list),
                      value=[min(year_list),max(year_list)],
                      marks=year_dict,step=None),
              html.Br()
              ]),
         ]),
  html.Div(id='graph-object',children ='Graph is loading')
  ])    
  return main_layout

#callbacks for the application
@app.callback(dash.dependencies.Output('graph-object','children'),
    [
    dash.dependencies.Input('maintabs','value'),
    dash.dependencies.Input('month-dropdown','value'),
    dash.dependencies.Input('date-dropdown','value'),
    dash.dependencies.Input('region-dropdown','value'),
    dash.dependencies.Input('country-dropdown','value'),
    dash.dependencies.Input('state-dropdown','value'),
    dash.dependencies.Input('city-dropdown','value'),
    dash.dependencies.Input('attacktype-dropdown','value'),
    dash.dependencies.Input('year-slider','value'), 
    dash.dependencies.Input('chart_year_slider','value'), 
    dash.dependencies.Input("chart_dropdown", "value"),
    dash.dependencies.Input("search", "value"),
    dash.dependencies.Input("chartsubtabs", "value")
    ])

def update_app_ui(Tabs,month_value,date_value,region_value,country_value,state_value,city_value,attack_value,year_value,
                  chart_year_selector, chart_dp_value, search,chartsubtabs):
    fig = None
    if Tabs == "tab1":
        print('Data Type of month value:',str(type(month_value)))
        print('Data Type of date value:',str(type(date_value)))
        print('Data Type of region value:',str(type(region_value)))
        print('Data Type of country value:',str(type(country_value)))
        print('Data Type of state value:',str(type(state_value)))
        print('Data Type of city value:',str(type(city_value)))
        print('Data Type of Attack value:',str(type(attack_value)))    
        print('Data Type of year value:',str(type(year_value)))
        
        # year filter
        year_range = range(year_value[0], year_value[1]+1)
        df1 = df[df["iyear"].isin(year_range)]
        
        # month filter
        if month_value==[] or month_value is None:
            pass
        else:
            if date_value==[] or date_value is None:
                df1 = df1[df1["imonth"].isin(month_value)]
            else:
                df1 = df1[df1["imonth"].isin(month_value)
                                & (df1["iday"].isin(date_value))]
        # region, country, state, city filter
        if region_value==[] or region_value is None:
            pass
        else:
            if country_value==[] or country_value is None :
                df1 = df1[df1["region_txt"].isin(region_value)]
            else:
                if state_value == [] or state_value is None:
                    df1 = df1[(df1["region_txt"].isin(region_value))&
                             (df1["country_txt"].isin(country_value))]
                else:
                    if city_value == [] or city_value is None:
                        df1 = df1[(df1["region_txt"].isin(region_value))&
                        (df1["country_txt"].isin(country_value)) &
                        (df1["provstate"].isin(state_value))]
                    else:
                        df1 = df1[(df1["region_txt"].isin(region_value))&
                        (df1["country_txt"].isin(country_value)) &
                        (df1["provstate"].isin(state_value))&
                        (df1["city"].isin(city_value))]
        #attack type filter           
        if attack_value == [] or attack_value is None:
            pass
        else:
            df1 = df1[df1["attacktype1_txt"].isin(attack_value)] 
        
        mapfigure = go.Figure()
        if df1.shape[0]:
            pass
        else: 
            df1 = pd.DataFrame(columns = ['iyear','imonth','iday','country_txt','region_txt','provstate',
                                          'city','latitude','longitude','attacktype1_txt','nkill'])
            df1.loc[0] = [0, 0 ,0, None, None, None, None, None, None, None, None]
            
        
        mapFigure = px.scatter_mapbox(df1,lat="latitude", 
                                      lon="longitude",
                                      color="attacktype1_txt",
                                      hover_name="city", 
                                      hover_data=["region_txt","country_txt","provstate","city","attacktype1_txt","nkill","iyear","imonth","iday"],
                                      zoom=1)                       
        mapFigure.update_layout(mapbox_style="open-street-map",
                                autosize=True,
                                margin=dict(l=0,r=0,t=25,b=20),
                                )
        fig = mapFigure

    elif Tabs=="chart":
        fig = None
        year_range_c = range(chart_year_selector[0], chart_year_selector[1]+1)
        chart_df = df[df["iyear"].isin(year_range_c)]
        
        
        if chartsubtabs == "tab4":
            pass
        elif chartsubtabs == "tab5":
            chart_df = chart_df[(chart_df["region_txt"]=="South Asia") 
            &(chart_df["country_txt"]=="India")]
        if chart_dp_value is not None and chart_df.shape[0]:
            if search is not None:
                chart_df = chart_df.groupby("iyear")[chart_dp_value].value_counts().reset_index(name = "count")
                chart_df  = chart_df[chart_df[chart_dp_value].str.contains(search, case=False)]
            else:
                chart_df = chart_df.groupby("iyear")[chart_dp_value].value_counts().reset_index(name="count")
        
        if chart_df.shape[0]:
            pass
        else: 
            chart_df = pd.DataFrame(columns = ['iyear', 'count', chart_dp_value])
            chart_df.loc[0] = [0, 0,"No data"]
        chartfigure = px.area(chart_df, x="iyear", y ="count", color = chart_dp_value)
        fig = chartfigure
    return dcc.Graph(figure = fig)


@app.callback(
  Output("date-dropdown","options"),
  [
  Input("month-dropdown","value")
  ])
def update_date(month):
    option = []
    if month:
        option= [{"label":m, "value":m} for m in date_list]
    return option

@app.callback(
  [
  Output('region-dropdown','value'),
  Output('region-dropdown','disabled'),
  Output('country-dropdown','value'),
  Output('country-dropdown','disabled')],
  [Input('mapsubtabs','value')])

def update_indiamap(tab):
    region=None
    disabled_r=False
    country=None
    disabled_c=False
    if tab == "tab2":
        pass
    elif tab == "tab3":
        region = ["South Asia"]
        disabled_r = True
        country = ["India"]
        disabled_c = True
    return region, disabled_r, country, disabled_c


@app.callback(
    Output('country-dropdown','options'),
    [Input('region-dropdown','value')])

def set_country_options(region_value):
    option = []
    if region_value is  None:
        raise PreventUpdate
    else:
        for var in region_value:
            if var in country_list.keys():
                option.extend(country_list[var])
    return [{'label':m , 'value':m} for m in option]


@app.callback(
    Output('state-dropdown','options'),
    [Input('country-dropdown','value')])

def set_state_options(country_value):
    option = []
    if country_value is None :
        raise PreventUpdate
    else:
        for var in country_value:
            if var in state_list.keys():
                option.extend(state_list[var])
    return [{'label':m , 'value':m} for m in option]


@app.callback(
    Output('city-dropdown', 'options'),
    [Input('state-dropdown', 'value')])

def set_city_options(state_value):
    option = []
    if state_value is None:
        raise PreventUpdate
    else:
        for var in state_value:
            if var in city_list.keys():
                option.extend(city_list[var])
    return [{'label':m , 'value':m} for m in option]



#flow of the project
def main():
    print("Welcome to the Application")
    
    load_data()
    open_browser()
  
  
    global app
    app.layout = create_app_ui()
    app.title = "Terrorism Analysis"
  
    app.run_server() 

    print("Thank You")
    df = None
    app = None



if __name__ == '__main__':
    main()




