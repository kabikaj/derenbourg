
import math
import pandas as pd
import ujson as json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


with open("../data/app_data.json") as fp:
    data = json.load(fp)

sample_data = []

for obj in data:

    try:
        date_of_book_author = int(obj["author_date_hijri"])
    except ValueError:
        date_of_book_author = None

    try:
        date_of_manuscript_author = int(obj["date_of_author_of_original_text_commented_upon_hijri"])
    except ValueError:
        date_of_manuscript_author = None

    try:
        date_of_manuscript = int(obj["date_of_original_text_commented_upon_hijri"])
    except ValueError:
        date_of_manuscript = None

    try:
        date_of_copy = int(obj["date_of_copying_hijri"])
    except ValueError:
        date_of_copy = None

    try:
        date_of_printing = int(obj["date_of_printing_hijri"])
    except ValueError:
        date_of_printing = None

    script = obj["script"]
    if script == "Asiatique très soignée":
        script = "Asiatique"
    elif script == "Magrobine":
        script = "Magrébine"

    # make the difference in lines per page much bigger
    # try:
    #     lines_per_page = float(obj["layaout_or_lines_per_page"])
    #     if lines_per_page > 0:
    #         lines_per_page = lines_per_page ** 2  # Square the value
    #     else:
    #         lines_per_page = None
    # except (ValueError, KeyError):
    #     lines_per_page = None

    lines_per_page = obj["layaout_or_lines_per_page"]
    
    sample_data.append({
        "date_of_book_author": date_of_book_author,
        "date_of_manuscript_author": date_of_manuscript_author,
        "date_of_manuscript": date_of_manuscript,
        "date_of_copy": date_of_copy,
        "date_of_printing": date_of_printing,
        "place_of_printing": obj["place_of_printing"],
        "material": obj["material"],
        "script": script,
        "number_of_folios": obj["number_of_folios"],
        "lines_per_page": lines_per_page,
    })


df = pd.DataFrame(sample_data)

script_colors = {
    "Asiatique": "#FFFF00",  # Yellow
    "Magrébine": "#DDA0DD",  # Light Purple
    "Orientale": "#90EE90",  # Light Green
}


fig = make_subplots(
    rows=3,
    cols=1,
    subplot_titles=[
        "Book Author Date", 
        # "Manuscript Author Date",
        # "Manuscript Date", 
        "Copy Date",
        "Printing Date",
    ],
    # specs=[
    #     [{"type": "scatter"}, {"type": "scatter"}],
    #     [{"type": "scatter"}, {"type": "scatter"}],
    #     [{"type": "scatter"}, {"type": "scatter"}]
    # ],
    specs=[
        [{"type": "scatter"}],
        [{"type": "scatter"}],
        [{"type": "scatter"}]
    ],
    horizontal_spacing=0.1,
    vertical_spacing=0.15
)

date_types = [
    "date_of_book_author",
    # "date_of_manuscript_author",
    # "date_of_manuscript",
    "date_of_copy",
    "date_of_printing"
]

# positions for each subplot
positions = [(1,1), (2,1), (3,1)]

for i, date_type in enumerate(date_types):
    row, col = positions[i]
    
    # Sort the dataframe by the current date type for clean lines
    df_sorted = df.sort_values(by=date_type)
    
    # Add folios line
    fig.add_trace(
        go.Scatter(
            x=df_sorted[date_type],
            y=df_sorted["number_of_folios"],
            mode='lines+markers',
            name='Number of Folios',
            line=dict(color='blue'),
            legendgroup='folios',
            showlegend=(i==0)  # only show legend for first subplot
        ),
        row=row, col=col
    )
    
    # Add lines per page line (on secondary y-axis)
    fig.add_trace(
        go.Scatter(
            x=df_sorted[date_type],
            y=df_sorted["lines_per_page"],
            mode='lines+markers',
            name='Lines per Page',
            line=dict(color='red'),
            legendgroup='lines',
            showlegend=(i==0)  # only show legend for first subplot
        ),
        row=row, col=col
    )
    
    # Add place annotations for printing date
    if date_type == "date_of_printing":
        for _, row_data in df_sorted.iterrows():
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
    
    # Add secondary y-axis for lines per page
    fig.update_yaxes(title_text="Num. Folios / Layout", row=row, col=col)
    
    # Update x-axis title
    fig.update_xaxes(title_text="Year", row=row, col=col)

    # Add big dots indicating script class
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
                showlegend=False  # We'll add the legend manually
            ),
            row=row, col=col
        )

for script, color in script_colors.items():
    fig.add_trace(
        go.Scatter(
            x=[None],  # No actual data
            y=[None],
            mode='markers',
            marker=dict(size=14, color=color, line=dict(width=1, color='DarkSlateGrey')),
            name=script,
            legendgroup='scripts',  # Group them under the same legend group
            showlegend=True  # Make sure they appear in the legend
        )
    )

# Update layout
fig.update_layout(
    title_text="<b>Manuscript Analysis Dashboard</b>",
)

# Hide axes for the legend subplot
fig.update_xaxes(visible=False, row=3, col=2)
fig.update_yaxes(visible=False, row=3, col=2)

fig.show()
# combined_fig.write_html("sales_report.html")  # Save as standalone HTML
