import streamlit as st
import numpy as np
import pandas as pd
import math

# CONSTANTS

PAGE_SIZE = 100

def get_artists(df: pd.DataFrame):
    """
    Get individual artists for searching
    """

    return df.drop_duplicates('Artist')['Artist']

def preprocess_data(df: pd.DataFrame):
    """
    Preprocess the data.

    - Combines entries with the same artist
    """

    # Combine artists on the same track
    # Note that we can still get the original artist using
    # the Url_spotify column
    artists = df.groupby('Uri')['Artist'].transform(', '.join)

    df['Artist'] = artists

    df = df.drop_duplicates('Uri')

    return df

def get_num_of_pages(df: pd.DataFrame):
    """
    Utility function to get number of pages in the dataframe
    based on page size
    Allows for validation, so that number of pages is not
    exceeded
    """
    df_length = len(df)
    return math.ceil(df_length)

@st.cache_data
def load_data():
    """
    Load data.
    """
    DATA_LOCATION = 'data/data.csv'

    try:
        data = pd.read_csv(
            DATA_LOCATION,
            index_col=0,    # Remove the initial row column
        )
    except FileNotFoundError:
        return None

    return data

@st.cache_data
def filter_data(
        df: pd.DataFrame,
        artist_search: None | str = None,
    ):
        if artist_search:
            df = df[df['Artist'].str.contains(artist_search)]

        return df

    
def paginate_data(
        df: pd.DataFrame,
        page_number = 1,
    ):

        # Validate number of pages
        max_num_of_pages = get_num_of_pages(df)

        if not 1 <= page_number <= max_num_of_pages:
            return df

def handle_search_form(
        data: pd.DataFrame,
        artists,
    ):
    form = st.form('search_form')
    with form:
        st.markdown('''
            Search for an artist to see their top ten tracks.
        ''')
        artist_search = st.selectbox(
            'Artist:',
            options=artists,
            index=None,
            key='artist',
        )

        submitted = st.form_submit_button("Search")
        if artist_search:
            st.write(f'Searching for {artist_search}...')
    return form

def handle_dataframe(DATA):
    # container = st.cont
    DATA = filter_data(
        DATA,
        st.session_state.artist,
    )
    st.dataframe(
        DATA,
        # hide_index=True,
        column_config={
            'Danceability': st.column_config.ProgressColumn(),
            'Energy': st.column_config.ProgressColumn(),
        }
    )

def main_layout(DATA, artists):
    st.title(":musical_note: Spotify Artists' Top Tens :musical_note:")
    with st.expander('Search'):
        form = handle_search_form(DATA, artists)
    handle_dataframe(DATA)

if __name__ == '__main__':
    DATA = load_data()

    if DATA is None:
        exit(1)

    artists = get_artists(DATA)

    DATA = preprocess_data(DATA)

    main_layout(DATA, artists)


# dataframe = pd.DataFrame(
#     np.random.randn(10, 20),
#     columns=('col %d' % i for i in range(20)))
#
# st.dataframe(dataframe.style.highlight_max(axis=0))
