# Mozaic Chart Creator
#
#This module is to create a 2D mozaic chart with corresponding data table.

# Import module
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

def mozaic_chart_data (d_frame, sr_column_portion, name_of_total):
    '''
    INPUT
    d_frame: dataframe with total column
    sr_column_portion: series with values of column portions of d_frame
    name of total: str, name of total column of d_frame, default as 'All'
    OUTPUT
    df: dataframe adjusted to make chart
    sr_por: series to make numeric part of xticklabel
    '''
    data = d_frame.copy()
    data.insert(0, 'Total', data[name_of_total])
    data.insert(1, '', np.nan)
    d_frame_adj = data.drop(name_of_total, axis = 1)
    
    sr = sr_column_portion.copy()
    sr_column_portion_adj = pd.concat([pd.Series([np.nan, np.nan], ['Total', np.nan]), sr])
    
    return d_frame_adj, sr_column_portion_adj

def mozaic_chart_plot (d_frame_adj, sr_column_portion_adj,
                       figsize, name_of_total,
                       pct_chart, min_dis_val,
                       fixed_color,
                       chart_title, title_left, 
                       title_right, data_unit):
    
    # base data for chart body, ytick and table
    base_num = d_frame_adj * 100 if pct_chart else d_frame_adj    
    
    ### dataframe of chart body: reversed data of base_num
    df_chart = base_num.reindex(index = base_num.index[::-1])
    
    ##### bottom points to stacked parts
    df_chart_cumsum = df_chart.cumsum().set_index(df_chart.index.astype(str) + '_cs')
    df_chart_cumsum_shift = df_chart_cumsum.shift(periods = 1, fill_value = 0)
    bottom_list = []
    for i in df_chart_cumsum_shift.index:
        globals()[i] = list(df_chart_cumsum_shift.loc[i])
        bottom_list.append(globals()[i])
    
    ##### heights and values of stacked parts
    value_list = []
    for i in df_chart.index:
        globals()[i] = list(df_chart.loc[i])
        value_list.append(globals()[i])
    
    ##### points of ytick  
    df_ytick = (df_chart_cumsum + df_chart_cumsum_shift) / 2
    ytick_list = []
    for i in df_ytick.index:
        globals()[i] = list(df_ytick.loc[i])
        ytick_list.append(globals()[i])

    ##### ylabels
    df_ylabel = df_chart.copy()
    df_ylabel['ylabels'] = np.where(df_ylabel['Total'] > min_dis_val, df_ylabel.index, '')
    ylabels = list(df_ylabel['ylabels'])
   
    ### dataframe of table
    df_table = base_num.drop('', axis = 1).fillna(0).round(decimals = 0).astype('int')
    df_table.replace(0, '', inplace = True)

    # base data for xtick
    sr_column_portion_adj = sr_column_portion_adj.fillna(0)
    xtick_num = list(sr_column_portion_adj * 100 if pct_chart else sr_column_portion_adj)
    xtick_data = xtick_num[2:]
    xtick_data_sum = sum(xtick_data)
    
    ##### widths of bars
    xtick_width = [100 * i / xtick_data_sum for i in xtick_data]
    width = [15, 5] + xtick_width
       
    ##### start points of bars
    xPoint_num, xPoint = 0, [0]
    for i in width[:-1]:
        xPoint_num += i
        xPoint.append(xPoint_num)

    ##### points of xtick
    xPoint_120 = xPoint.copy()
    xPoint_120.append(120)
    xtick_Point = []
    for i, j in zip(xPoint_120[:-1], xPoint_120[1:]):
        xtick_Point.append((i + j)/2)

    ##### xlabels
    xtick_add = [int(round(i, 0)) for i in xtick_data]
    xtick_add = ['', ''] + xtick_add  
    xlabels = [f"{x1}\n{x2}" for x1, x2, in zip(df_chart.columns, xtick_add)]
    
    # color list
    def mozaic_chart_color (d_frame_adj, fixed_color):
        if d_frame_adj.shape[0] == len(fixed_color):
            color_list = fixed_color
        else:
            color_list = []
            for i in d_frame_adj.index:
                color_list.append(["#"+''.join([random.choice('ABCDEF89') for i in range(6)])])
        return color_list
    color_list = mozaic_chart_color(d_frame_adj, fixed_color)

    # chart plot
    fig, ax = plt.subplots(figsize = figsize)

    for i, j in enumerate(value_list):      
        bar = ax.bar(xPoint, width = width, height = j, bottom = bottom_list[i],
                     align = 'edge', color = color_list[i], edgecolor = 'gray')
        for k, l in enumerate(j):
            plt.text(xtick_Point[k], ytick_list[i][k], 
                     '%.0f' %l if l > min_dis_val else '',
                     ha = 'center', va = 'center', size = figsize[1] * 2)
    plt.rcParams['font.family'] = 'Arial'
    
    plt.xticks(xtick_Point, xlabels, size = figsize[1] * 2.1, family ='Arial');
    plt.tick_params(axis= 'x', length = 0, pad = figsize[1])
    plt.yticks(df_ytick['Total'], ylabels, size = figsize[1] * 2.1, family ='Arial');
    ax.margins(x = 0.02);
    plt.tick_params(axis = 'y', length = 0)

    plt.axhline(color='gray', linestyle='solid', linewidth=2);
    plt.box(False)
    
    table = ax.table(
        cellText=df_table.values, rowLabels = df_table.index, rowLoc = 'right',
        colLabels=df_table.columns, cellLoc = 'center',
        bbox=[0.015,-0.92,0.97,0.8]);
    table.set_fontsize(figsize[1] * 2)

    plt.title(
        '{}'.format(chart_title)+': '+'{}'.format(title_left)+' / '+'{}'.format(title_right),
        size = figsize[1] * 2.2);
    data_unit = '%' if pct_chart else data_unit
    fig.suptitle('(Unit: '+'{}'.format(data_unit)+')', size = figsize[1] * 2,
                 x=0.88, y=0.88, ha = 'right');

def mozaic_chart (d_frame, sr_column_portion, figsize = (12, 5),
                  name_of_total = 'All', pct_chart = True, min_dis_val = 3,
                  fixed_color = [],
                  chart_title = 'Mozaic Chart', title_left = 'yaxis', 
                  title_right = 'xaxis', data_unit = 'Sum'):
    
    d_frame_adj, sr_column_portion_adj = mozaic_chart_data (d_frame, sr_column_portion, name_of_total)
    mozaic_chart_plot(d_frame_adj, sr_column_portion_adj, figsize,
                      name_of_total, pct_chart, min_dis_val,
                      fixed_color, 
                      chart_title, title_left, 
                      title_right, data_unit)