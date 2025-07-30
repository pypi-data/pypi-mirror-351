import os, math, sys, re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def load_csv_output(simulation_file, delimiter=';'):
    Sim_df = pd.read_csv(simulation_file, delimiter=delimiter)

    # removing leading and trailing whitespace in column names
    keys_clean = [key.strip() for key in Sim_df.keys()]
    
    # edit repeat variables with a .# ending 
    # within a csv holding measurements to be have _# on the end
    # will work up to 10 layers
    for i in range(len(keys_clean)):
        if keys_clean[i][-2]=='.':
            raw_variable_name = keys_clean[i][:-2].strip()

            if keys_clean[i][-1]=='1':
                # search for the previous one and append _1
                index_first_variable_instance = keys_clean.index(raw_variable_name)
                keys_clean[index_first_variable_instance] = raw_variable_name + '_1'
            
            keys_clean[i] = raw_variable_name + '_'+str(int(keys_clean[i][-1])+1)

    keys_update_dict = dict(zip(Sim_df.keys(), keys_clean))
    Sim_df.rename(columns=keys_update_dict, inplace=True)

    #include a date column
    Sim_df['Date'] = pd.to_datetime({'year':Sim_df['YYYY'], 
                                    'month':Sim_df['MM'], 
                                    'day':Sim_df['DD']})

    Sim_df['in'] = 0
    Sim_df['out'] = 0
    Sim_df['storage change'] = 0
    Sim_df['balance'] = 0

    return Sim_df


def cycle(filename, 
          cellsize_m2=1000*1000, num_cells_domain=153451, 
          return_figures=False, onlyCircle=False, onlyTypeFlows=False, margins=True,
          delimiter=';'):

    figure_title = filename.split('/')[-1]
    figure_title = figure_title.split('\\')[-1] 
    figure_title = figure_title.split('.')[0]                               

    SIM_df = pd.DataFrame()
    Circles_df = pd.read_csv(filename, delimiter=delimiter)

    labels = ['total', 'in', 'out', 'storage change', 'balance']
    parents = ['', 'total', 'total', 'total', 'total']
    values = [0, 0, 0, 0, 0]
    colors_dict = {'in':'#636EFA', 'out':'#EF5538', 'balance':'black', 'storage change':'#D2D2D3'}
    colors = ['balance', 'in', 'out', 'storage change', 'balance']

    fig_lines_all_flows = go.Figure()

    # Progressing through the list of variables
    for flow_n in range(len(Circles_df['VARIABLES'])):

        simulation_file = Circles_df['SIMULATION'][flow_n]
        flow_name = Circles_df['VARIABLES'][flow_n]
        parent_name = Circles_df['TYPE'][flow_n]

        try: not math.isnan(simulation_file)
        except: 
            Sim_df = load_csv_output(simulation_file, delimiter=delimiter)
            
            # create the master as a copy of the first dataframe
            if SIM_df.empty:
                SIM_df['in'] = Sim_df[flow_name]*0
                SIM_df['out'] = Sim_df[flow_name]*0
                SIM_df['storage change'] = Sim_df[flow_name]*0
                SIM_df['balance'] = Sim_df[flow_name]*0

        # unify units to m3/m2/simulation
        unit = Circles_df['UNITS'][flow_n]
        multiplier = 1

        #transform to units m/day/basin
        if unit[-4:] == 'cell':
            multiplier *= num_cells_domain

        if unit[-6:] == 'domain':
            multiplier /= num_cells_domain

        if 'm3s' in unit:
            multiplier *= 60*60*24

        elif 'mm' in unit:
            multiplier /= 1000 
            multiplier *= cellsize_m2

        Sim_df[flow_name] *= multiplier
        
        # create storage change variables
        if Circles_df['TYPE'][flow_n] == 'storage':

            storage_component = Circles_df['VARIABLES'][flow_n]
            new_storage_change_key = storage_component + ' change'
            Sim_df[new_storage_change_key] = Sim_df[storage_component] - Sim_df[storage_component].shift(1)

            flow_name = new_storage_change_key
            parent_name = 'storage change'

        flow_name_original = flow_name
        name_counter = 2
        if flow_name in SIM_df.keys():
            while flow_name in SIM_df.keys():
                flow_name = flow_name_original + '_' + str(name_counter)
                name_counter +=1
            Sim_df.rename(columns={flow_name_original:flow_name}, inplace=True)

        SIM_df[flow_name] = Sim_df[flow_name]

        # line graphs
        fig_lines_all_flows.add_trace(go.Scatter(x=Sim_df['Date'], y=Sim_df[flow_name],
                            mode='lines',
                            name=flow_name))
        

        # sum the variables and add to circle
        #total_sum = Sim_df[flow_name][1:].sum()
        total_sum = Sim_df[flow_name].sum()

        if parent_name == 'in':
            SIM_df['in'] += Sim_df[flow_name]
            values[1] += total_sum
            colors.append('in')

        elif parent_name == 'out':
            SIM_df['out'] += Sim_df[flow_name]
            values[2] += total_sum
            colors.append('out')

        elif parent_name == 'storage change':
            SIM_df['storage change'] += Sim_df[flow_name]
            values[3] += abs(total_sum)
            values[4] -= total_sum

            if total_sum>0:
                colors.append('in')
            else:
                colors.append('out')
        else:
            #find parent in labels
            parent_color_index = labels.index(parent_name)
            colors.append(colors[parent_color_index])

        labels.append(flow_name)
        parents.append(parent_name)
        values.append(abs(total_sum))

    SIM_df['balance'] = SIM_df['in'] - SIM_df['out'] - SIM_df['storage change']
    SIM_df['Date'] = Sim_df['Date']

    fig_lines_type_flows = go.Figure()
    colors_dict_lines = colors_dict.copy()
    colors_dict_lines['balance']='#AB63FA'
    for flow_name in ['in', 'out', 'storage change', 'balance']:
        fig_lines_type_flows.add_trace(go.Scatter(x=SIM_df['Date'], y=SIM_df[flow_name],
                                mode='lines',
                                line=dict(color=colors_dict_lines[flow_name]),
                                name=flow_name))
        
    values[4] += values[1] - values[2] # balance = inputs - outputs, beforehand:  minus actual storage change
    values[4] = abs(values[4])
    values[0] = values[1]+values[2]+values[3]+values[4] # total flows

    Sunburst = {'labels':labels, 'parents':parents, 'values':values, 'colors':colors}
    Sunburst_df = pd.DataFrame(data=Sunburst)

    fig_circle=px.sunburst(Sunburst_df, names = 'labels', parents = 'parents', values = 'values', 
                        color='colors', 
                        color_discrete_map=colors_dict,
                        branchvalues="total",
                            #textfont_color="White"
                            )

    fig_circle.update_layout(template = 'plotly_dark')
    fig_circle.update_layout(plot_bgcolor='rgb(0,0,0)', 
                        paper_bgcolor ='rgb(0,0,0)',
                        title = dict(
                            text=figure_title,
                            xanchor='center',
                            yanchor='bottom',
                            y=0.04,
                            x=0.5,
                            #font=dict(size=10)
                            ))
    if margins==True:
        fig_circle.update_layout(margin=dict(l=20, r=20, t=20, b=45))
    

    marker_colors = [colors_dict[i] for i in colors]
    marker_line_color = ['black']*len(marker_colors)
    marker_line_color[0]='white'
    marker_line_color[4]='white'
    #marker_colors[2]='#AB63FA'
    fig_bar = go.Figure(data=[go.Bar(x=labels, 
                                     y=values, 
                                     marker_color=marker_colors,
                                     marker_line_color=marker_line_color,
                                     #marker_line_width=3
                                     )],
                                     layout=dict(barcornerradius="10%"))
    
    fig_bar.update_layout(
        template = 'plotly_dark',
        plot_bgcolor='rgb(0,0,0)', 
        paper_bgcolor ='rgb(0,0,0)',
        title = figure_title,
        yaxis_title="m<sup>3</sup> (total/period)",
        font=dict(size=10))

    fig_lines_type_flows.update_layout(template = 'plotly_dark')
    fig_lines_type_flows.update_layout(plot_bgcolor='rgb(0,0,0)', 
                        paper_bgcolor ='rgb(0,0,0)',
                        title = figure_title,
                        yaxis_title="m<sup>3</sup> (total/day)",
                        font=dict(size=10))

    fig_lines_all_flows.update_layout(template = 'plotly_dark')
    fig_lines_all_flows.update_layout(plot_bgcolor='rgb(0,0,0)', 
                        paper_bgcolor ='rgb(0,0,0)',
                        title = figure_title,
                        yaxis_title = "m<sup>3</sup> (total/day)",
                        font=dict(size=10))

    fig_lines_type_flows.update_layout(
        legend=dict(
        orientation="h",),
        #font=dict(size=10)),
        margin=dict(l=45, r=30, t=50, b=45)
        )

    fig_lines_all_flows.update_layout(
        legend=dict(
        orientation="h",
        font=dict(size=10)),
        margin=dict(l=45, r=30, t=50, b=45)
        )

    fig_lines_type_flows.update_xaxes(automargin='height')
    fig_lines_all_flows.update_xaxes(automargin='height')

    if return_figures:
        return fig_circle, fig_bar, fig_lines_type_flows, fig_lines_all_flows
    elif onlyCircle:
        fig_circle.show()
    elif onlyTypeFlows:
        fig_lines_type_flows.show()
    else:
        fig_circle.show()
        fig_bar.show()
        fig_lines_type_flows.show()
        fig_lines_all_flows.show()
    