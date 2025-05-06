import pandas as pd
import ujson as json
import plotly.express as px

with open("../data/app_data.json") as fp:
    data = json.load(fp)

sample_data = []

for obj in data:
    lines_per_page = obj["lines_per_page"][0] if obj["lines_per_page"] else None
    
    script = obj["script"]
    if script == "Asiatique très soignée":
        script = "Asiatique"
    if script == "Asiatique très serrée":
        script = "Asiatique"
    
    sample_data.append({
        "script": script,
        "number_of_folios": obj["number_of_folios"],
        "lines_per_page": lines_per_page,
        "material": obj["material"],
        "place_of_publication": obj["publication"][0]["place"] if obj["publication"] else None,
    })

df = pd.DataFrame(sample_data)

fig = px.scatter(
    df,
    x='number_of_folios',
    y='lines_per_page',
    color='script',
    title='Lines per Page vs. Number of Folios (Colored by Script)',
    labels={
        'number_of_folios': 'Number of Folios',
        'lines_per_page': 'Lines per Page',
        'script': 'Script Type'
    },
    hover_data=['material', 'place_of_publication'],
    # trendline="lowess",
)

fig.update_layout(
    xaxis_title='Number of Folios',
    yaxis_title='Lines per Page',
    hovermode='closest',
    showlegend=True,
)

fig.show()