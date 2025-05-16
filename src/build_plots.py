#!/usr/env python3
#
#    build_plots.py
#
# MIT License
#
# Copyright (c) 2025 Alicia González Martínez
#
# usage:
#   $ python3 build_plots.py
#
#############################################

import math
import pandas as pd
import ujson as json
import statistics
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


with open("../data/app_data.json") as fp:
    data = json.load(fp)

sample_data = []

for obj in data:
    try:
        date_of_book_author = int(obj["date_of_author"]["hijri"]) if obj["date_of_author"]["hijri"] else None
    except (ValueError, TypeError):
        date_of_book_author = None

    try:
        date_of_manuscript_author = int(obj["date_of_author_of_book_commented_upon"]["hijri"]) if obj["date_of_author_of_book_commented_upon"]["hijri"] else None
    except (ValueError, TypeError):
        date_of_manuscript_author = None

    try:
        date_of_manuscript = int(obj["date_of_book_commented_upon"]["hijri"]) if obj["date_of_book_commented_upon"]["hijri"] else None
    except (ValueError, TypeError):
        date_of_manuscript = None

    try:
        date_of_copy = int(obj["date_of_book"]["hijri"]) if obj["date_of_book"]["hijri"] else None
    except (ValueError, TypeError):
        date_of_copy = None

    lines_per_page = list(filter(None, obj["lines_per_page"])) if obj["lines_per_page"] else None
    lines_per_page = int(statistics.mean(lines_per_page)) if lines_per_page else None
    
    script = obj["script"]
    if script == "Asiatique très soignée":
        script = "Asiatique"
    if script == "Asiatique très serrée":
        script = "Asiatique"

    printing_date = None
    printing_place = None
    if obj["publication"] and len(obj["publication"]) > 0:
        try:
            printing_date = int(obj["publication"][0]["date_hijri"]) if obj["publication"][0]["date_hijri"] else None
            printing_place = obj["publication"][0]["place"]
        except (ValueError, TypeError, KeyError):
            printing_date = None
            printing_place = None
    
    sample_data.append({
        "date_of_author": date_of_book_author,
        "date_of_manuscript_author": date_of_manuscript_author,
        "date_of_book_commented_upon": date_of_manuscript,
        "date_of_book": date_of_copy,
        "date_of_printing": printing_date,
        "place_of_printing": printing_place,
        "material": obj["material"],
        "script": obj["script"],
        "number_of_folios": obj["number_of_folios"],
        "lines_per_page": lines_per_page,
    })


df = pd.DataFrame(sample_data)

script_colors = {
    "Asiatique": "#FFFF00",  # yellow
    "Magrébine": "#DDA0DD",  # light Purple
    "Orientale": "#90EE90",  # light Green
}


fig = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=[
        "Date of book compared to number of folia and script",
        "Date and place of publication compared to number of folia and script",
        "Lines per page and number of folia compared to script"
    ],
    specs=[
        [{"type": "scatter"}],
        [{"type": "scatter"}],
        [{"type": "scatter"}]
    ],
    horizontal_spacing=0.1,
    vertical_spacing=0.15
)

date_types = [
    "date_of_book",     # data key of 1st plot
    "date_of_printing"  # data key of 2nd plot
]

# positions for each subplot
positions = [(1,1), (2,1), (3,1)]

for i, date_type in enumerate(date_types):
    row, col = positions[i]
    
    # sort the dataframe by the current date type for clean lines
    df_sorted = df.sort_values(by=date_type)
    
    fig.add_trace(
        go.Scatter(
            x=df_sorted[date_type],
            y=df_sorted["number_of_folios"],
            mode='lines+markers',
            name='Number of Folios',
            line=dict(color='blue'),
            legendgroup='folios',
            # showlegend=(i==0)  # only show legend for first subplot
        ),
        row=row, col=col
    )
    
    if date_type == "date_of_printing":
        for _, row_data in df_sorted.iterrows():
            if row_data["place_of_printing"]:
                fig.add_annotation(
                    x=row_data[date_type],
                    y=row_data["number_of_folios"],
                    text=row_data["place_of_printing"],
                    showarrow=True,
                    arrowhead=1,
                    ax=0,
                    ay=-40,
                    row=row,
                    col=col
                )
    
    fig.update_yaxes(title_text="Number of Folios", row=row, col=col)
    
    fig.update_xaxes(title_text="Hijri Year", row=row, col=col)

    for _, row_data in df_sorted.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row_data[date_type]],
                y=[row_data["number_of_folios"]],
                mode='markers',
                marker=dict(
                    size=8,
                    color=script_colors.get(row_data["script"], "#000000"),
                    line=dict(width=1, color='DarkSlateGrey')
                ),
                name=row_data["script"],
                legendgroup=row_data["script"],
                showlegend=False
            ),
            row=row, col=col
        )


########################
# third subplot
########################

row, col = positions[2]

df['script_color'] = df['script'].map(script_colors)

fig.add_trace(
    go.Scatter(
        y=df["lines_per_page"],
        x=df["number_of_folios"],
        mode='markers',
        marker=dict(
            color=df['script_color'],  # use the mapped colors
            size=8,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        name='Script Types',
        hovertext=df.apply(lambda row: f"Script: {row['script']}<br>Material: {row['material']}<br>Place: {row['place_of_printing']}", axis=1),
        hoverinfo='text+x+y',
        showlegend=True,
        legendgroup='scripts'
    ),
    row=row, col=col
)

fig.update_xaxes(title_text="Number of Folios", row=row, col=col)
fig.update_yaxes(title_text="Lines per Page", row=row, col=col)

# add script legend items
for script, color in script_colors.items():
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            marker=dict(size=14, color=color, line=dict(width=1, color='DarkSlateGrey')),
            name=script,
            legendgroup='scripts',
            showlegend=True
        )
    )


fig.update_layout(
    title_text="<b>Sample of Manuscript Plottings</b>",
    height=900
)

# rearrange date ranges in plots
fig.update_xaxes(range=[500, 1050], row=1, col=1)
fig.update_xaxes(range=[1230, 1285], row=2, col=1)
fig.update_xaxes(range=[None, 500], row=3, col=1)


# fig.show()

# save as standalone html
fig.write_html("html/plot.html")
