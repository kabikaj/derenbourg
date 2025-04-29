
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

fig = px.scatter(
    df,
    x='script',
    y='lines_per_page',
    title='Comparison of Lines per Page by Script',
    labels={'script': 'Script', 'lines_per_page': 'Lines per Page'},
    hover_data=['date_of_book_author', 'date_of_manuscript']  # Optional: add more hover info
)

fig.update_layout(
    xaxis_title='Script',
    yaxis_title='Lines per Page',
    hovermode='closest'
)


fig.show()

