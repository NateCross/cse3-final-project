import streamlit as st
import numpy as np
import pandas as pd
import math
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

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

def get_grid_options(df: pd.DataFrame):
    """
    Build grid options for dataframe display
    """
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(
        resizable=True,
        filterable=True,
        sortable=True,
        editable=False,
    )

    gb.configure_selection(
        selection_mode="single",
    )

    # gb.configure_side_bar()

    grid_options = gb.build()

    return grid_options

def handle_dataframe(DATA):
    # container = st.cont
    DATA = filter_data(
        DATA,
        st.session_state.artist,
    )

    st.dataframe(
        DATA,
        # hide_index=True,
        column_order=(
            "Artist",
            "Track",
            "Album",
            "Stream",
            "Views",
            "Likes",
            "Danceability",
            "Energy",
            "Speechiness",
            "Acousticness",
            "Instrumentalness",
            "Liveness",
            "Valence",
            "Url_youtube",
        ),
        column_config={
            'Stream': st.column_config.Column(
                "Streams",
                help="Number of streams of the song on Spotify",
            ),
            'Views': st.column_config.Column(
                help="Number of views of the song on Youtube",
            ),
            'Likes': st.column_config.Column(
                help="Number of likes of the song on Youtube",
            ),
            'Url_youtube': st.column_config.LinkColumn(
        'Youtube Link',
    ),
            'Speechiness': st.column_config.ProgressColumn(
                help="detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.",
            ),
            'Acousticness': st.column_config.ProgressColumn(
                help="a confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.",
            ),
            'Instrumentalness': st.column_config.ProgressColumn(
                help="predicts whether a track contains no vocals. 'Ooh' and 'aah' sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly 'vocal'. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0."
            ),
            'Liveness': st.column_config.ProgressColumn(),
            'Valence': st.column_config.ProgressColumn(),
            'Danceability': st.column_config.ProgressColumn(
                help="describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.",
            ),
            'Energy': st.column_config.ProgressColumn(
                help=" is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy."
            ),
        }
    )

def main_layout(DATA, artists):
    st.title(":musical_note: Spotify Artists' Top Tens :musical_note:")
    with st.expander('Select an artist'):
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
