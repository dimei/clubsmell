import pandas as pd
import plotly.express as px
import numpy as np
import os
import datetime

def read_wears():
    """
    Read fragrance wear data from Excel sheets.

    Reads all sheets from the Excel file 'Copy of Silly_Fragrance_excel.xlsx' and concatenates them
    into a single DataFrame. Filters out rows where 'Wears' is equal to 0 and removes any unnamed columns.

    Returns:
        pd.DataFrame: A DataFrame containing fragrance wear data with a new column 'sheet_name'.
    """
    #excel_file='Copy of Silly_Fragrance_excel.xlsx'
    excel_file = os.path.join(os.path.dirname(__file__), 'Copy of Silly_Fragrance_excel.xlsx')


    # Read all sheets into a dictionary
    all_sheets = pd.read_excel(excel_file, sheet_name=None)

    # Filter sheets containing 'Wears for'
    wears_sheets = {sheet_name: sheet_df for sheet_name, sheet_df in all_sheets.items() if 'Wears for' in sheet_name}
    
    #sort ascending, so that is in order by each year 2021-2022, 2023, 2024
    wears_sheets_ordered = dict(sorted(wears_sheets.items()))
    
    # Concatenate all DataFrames into one DataFrame with a new column 'sheet_name'
    wears_df = pd.concat([df.assign(sheet_name=sheet_name) for sheet_name, df in wears_sheets_ordered.items()], ignore_index=True)
    wears_df=wears_df.dropna(how='all')
    wears_df = wears_df.loc[:, ~wears_df.columns.str.contains('^Unnamed')]
    wears_df = wears_df[wears_df['Wears'] != 0]
    return wears_df



def sum_wears(wears_df,frag):
    """
    Summarize fragrance wear data for a specific fragrance.

    Groups the DataFrame by fragrance and calculates the sum of 'Wears' for each fragrance.
    Returns the total wears, rank based on total wears, and estimates the leftover milliliters
    of fragrance based on assumptions of sprays per milliliter and sprays per wear.

    Args:
        wears_df (pd.DataFrame): DataFrame containing fragrance wear data.
        frag (str): The fragrance for which to summarize wear data.

    Returns:
        tuple: A tuple containing the following elements:
            - int: Total wears for the given fragrance across all sheets.
            - int: Rank of the fragrance based on total wears.
            - float: Estimated leftover milliliters of fragrance.
            - pd.DataFrame: Subset of the original DataFrame for the specified fragrance.
    """
    
    
    wears_allsum=wears_df.groupby(['Fragrance'])['Wears'].sum()
    if frag not in wears_allsum.index:
        print(f"Wears not tracked for fragrance: {frag}")
        return None  # or any other value indicating not tracked
    
    frag_wears_alltime=wears_allsum[frag]
    rank= int(wears_allsum.rank(ascending=False)[frag])
    
    total_ml_df=wears_df[wears_df["Fragrance"]==frag]["mL"] +(wears_df[wears_df["Fragrance"]==frag]["mL"] * wears_df[wears_df["Fragrance"]==frag]["Backups"])
    total_ml=total_ml_df.unique()

    # if total_ml no consensus amongst Wears tabs, take the last one -1 (most recent). 
    # if consensus, 0 to grab the only value
    # assume 12 sprays per mL. 4 sprays per wear. So 1 wear is 4/12 of a mL
    if len(total_ml) >1:
        starting_ml=total_ml[-1]

    else:
        starting_ml=total_ml[0]
    leftover_ml=starting_ml-(frag_wears_alltime*4/12)
    return frag_wears_alltime,rank, leftover_ml,wears_df[wears_df["Fragrance"]==frag], starting_ml


def plot_wears (plot_df,starting_ml):
    plot_df["Year"]=plot_df["sheet_name"].str.extract('(\d{4})')
    plot_df.loc[plot_df['Year'] == '2021', 'Wears'] /= 2
    # Filter rows where Year is 2021
    rows_2021 = plot_df[plot_df['Year'] == '2021']

    # Duplicate the rows
    rows_2022 = rows_2021.copy()
    rows_2020=rows_2021.copy()

    # Set the "Year" column to 2022 for the new rows
    rows_2022['Year'] = '2022'
    rows_2020['Year'] = '2020'
    rows_2020["Wears"]=0
    #Round Wears for 2021 down, for 2022 up
    # Concatenate the original and new rows
    plot_df = pd.concat([plot_df, rows_2022,rows_2020], ignore_index=True)

    plot_df['Wears'] = np.where(plot_df['Year'] == '2021', np.floor(plot_df['Wears']), np.ceil(plot_df['Wears']))
    plot_df["Year"]=plot_df["Year"].astype(int)
    plot_df=plot_df.sort_values(by="Year",ascending=True)

    # Assuming plot_df is your DataFrame
    plot_df['Cumulative Wears'] = plot_df['Wears'].cumsum()

    plot_df["Years"]=plot_df['Year']
    # Set today's date
    today = datetime.date.today()
    fraction_of_year_passed = today.timetuple().tm_yday / 365

    # for this year, set plot year (Years) to last year + fraction of this year passed
    # this sets the width of this year's x axis proportional to fraction of this year passed
    plot_df.loc[plot_df['Year'] == datetime.datetime.now().year, 'Years'] = datetime.datetime.now().year-1+fraction_of_year_passed


    # Plotting cumulative wears as a line chart
    fig_cumulative_wears = px.line(
        plot_df,
        x="Years",  # Use the DataFrame index as x-axis
        y="Cumulative Wears",
        title="Cumulative Wears per Year",
        color_discrete_sequence=["#4111a4"],
        template="plotly_white",
    )

    fig_cumulative_wears.update_layout(xaxis=dict(tickmode="linear", tickvals=plot_df['Year'].unique(), ticktext=plot_df['Year'].unique().astype(int)))
    
    slope=plot_df["Cumulative Wears"].max()/(datetime.datetime.now().year+fraction_of_year_passed-2021)

    # Display the plot
    
    return fig_cumulative_wears, slope


def all_wears_plot (selected_fragrance,wears_df):

    sorted_df = wears_df.groupby(["Fragrance"])["Wears"].sum().reset_index().sort_values(by='Wears', ascending=False).reset_index()

    # Create a bar plot
    fig = px.bar(sorted_df, x='Fragrance', y='Wears', title='Wears by Fragrance (Descending Order)')



    # Highlight the bar for the selected fragrance
    highlighted_bar_index = sorted_df[sorted_df['Fragrance'] == selected_fragrance].index[0]
    #display(sorted_df[sorted_df['Fragrance'] == selected_fragrance].index)
    colors = ['gold' if i == highlighted_bar_index else 'black' for i in range(len(sorted_df))]
    fig.data[0].marker.color = colors


    variable2=sorted_df.index.max()
    fig.update_layout(
        title=f'All Time Wears Per Fragrance, Rank: {highlighted_bar_index+1} out of {variable2+1}',
    xaxis_title=None)
    
    return fig

def plot_bottles(mL_left, mL_start):
    # Percentage (replace this with your actual percentage value)
    percentage_filled = mL_left / mL_start
    
    # size factor: if it's a 10 mL bottle, normal size. goes up from there
    # change this later to break out per bottle or backup. lol
    size_fac = 1
    size_facy = 1


    # Create a bar plot
    fig = px.bar(
        x=[0],
        y=[0])

      # Add bottom rectangle (upright) filled gold
    fig.add_shape(
        type="rect",
        x0=-0.2*size_fac,
        y0=0,
        x1=0.2*size_fac,
        y1=0.8*percentage_filled*size_facy,
        fillcolor="gold",
        line=dict(color="black")
    )

    # Add bottom rectangle (upright) empty white
    fig.add_shape(
        type="rect",
        x0=-0.2*size_fac,
        y0=0.8*percentage_filled*size_facy,
        x1=0.2*size_fac,
        y1=0.8*size_facy,
        fillcolor="white",
        line=dict(color="black"),
    )
    # Add top rectangle (lying flat), black cap
    fig.add_shape(
        type="rect",
        x0=-0.14 * size_fac,
        y0=0.8 * size_facy,
        x1=0.14 * size_fac,
        y1=1.2 * size_facy,
        fillcolor="black",
        line=dict(color="black"),
    )
    # max is 1300 mL, min is 30 mL roughly. update later.
    norm_mL_start = (mL_start - 30) / (600 - 30)
    # Set layout properties
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=1000*float(norm_mL_start),
        width=1000*float(norm_mL_start)
    )

    return fig

# Example usage
#fig = plot_bottles(30, 50)
#fig.show()
