import streamlit as st
import numpy as np
import pandas as pd

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

    return df
    

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

def handle_search_form(
        data: pd.DataFrame,
    ):
    form = st.form('search_form')
    with form:
        artist_search = st.selectbox(
            'Artist:',
            options=data['Artist'].drop_duplicates(),
            index=None,
            key='artist',
        )
        track_search = st.selectbox(
            'Song:',
            options=data['Track'],
            index=None,
            key='track',
        )
        album_search = st.selectbox(
            'Album:',
            options=data['Album'],
            index=None,
            key='album',
        )

        submitted = st.form_submit_button("Search")
        print(track_search)
        if artist_search or track_search or album_search:
            st.write('Searching...')
    return form

if __name__ == '__main__':
    DATA = load_data()

    if DATA is None:
        exit(1)

    DATA = preprocess_data(DATA)

    form = handle_search_form(DATA)

    search_form_data = st.session_state.artist

    print(search_form_data)

    st.dataframe(
        DATA,
        column_config={
            'Danceability': st.column_config.ProgressColumn(),
            'Energy': st.column_config.ProgressColumn(),
        }
    )

# dataframe = pd.DataFrame(
#     np.random.randn(10, 20),
#     columns=('col %d' % i for i in range(20)))
#
# st.dataframe(dataframe.style.highlight_max(axis=0))
