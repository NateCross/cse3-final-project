import streamlit as st
import pandas as pd
import math
import streamlit_extras.row
from streamlit_extras.metric_cards import style_metric_cards

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

def handle_search_form(
        artists,
    ):
    form = st.form('search_form')
    with form:
        st.markdown('''
            Search for an artist to see their top ten tracks.
            Clear the selection and click "search" to show all tracks.
        ''')
        artist_search = st.selectbox(
            'Artist:',
            options=artists,
            index=None,
            key='artist',
        )

        st.form_submit_button("Search")
        if artist_search:
            st.write(f'Searching for {artist_search}...')
    return form

def handle_dataframe(DATA):
    # Create dataframe showing all the data
    st.dataframe(
        DATA,
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
                help="Detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.",
            ),
            'Acousticness': st.column_config.ProgressColumn(
                help="A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.",
            ),
            'Instrumentalness': st.column_config.ProgressColumn(
                help="Predicts whether a track contains no vocals. 'Ooh' and 'aah' sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly 'vocal'. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0."
            ),
            'Liveness': st.column_config.ProgressColumn(
                help="detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live."
            ),
            'Valence': st.column_config.ProgressColumn(
                help="A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry)."
            ),
            'Danceability': st.column_config.ProgressColumn(
                help="Describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.",
            ),
            'Energy': st.column_config.ProgressColumn(
                help="Is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy."
            ),
        }
    )

def handle_characteristic_vs_metric_plot(DATA):
    """
    Scatter plot that lets user select an engagement metric
    and see its correlation with a track characteristic
    """
    with st.container(border=True):
        selection_row = streamlit_extras.row.row(5)

        # Define the selection of metric and characteristic
        # The empty methods are used to add padding
        selection_row.empty()

        characteristic = selection_row.radio(
            "**Track Characteristic**",
            [
                "Danceability", 
                "Energy", 
                "Speechiness",
                "Acousticness",
                "Instrumentalness",
                "Liveness",
                "Valence",
            ],
            captions=[
                "How suitable a track is for dancing",
                "How intense and active a song is",
                "How present spoken words are in the song",
                "How likely the song is acoustic",
                "How likely a song contains no vocals",
                "How present an audience is in the song",
                "How musically positive a song is",
            ],
        )

        selection_row.empty()

        metric = selection_row.radio(
            "**Engagement Metric**",
            ["Stream", "Views", "Likes"],
            captions=[
                "Number of streams on Spotify",
                "Number of views on its Youtube video",
                "Number of likes on its Youtube video",
            ],
        )

        selection_row.empty()

        st.divider()

        st.scatter_chart(
            DATA,
            x=characteristic,
            y=metric,
        )
        

def handle_filtered_data_metrics(DATA):
    """
    Use this function after filtering data to get metrics
    """
    if not st.session_state.artist:
        st.info("Select an artist to see their engagement metrics.")
        return

    artist_metrics_row = streamlit_extras.row.row(4)

    artist_metrics_row.metric(
        'Artist',
        value=st.session_state.artist,
    )
    artist_metrics_row.metric(
        'Average Streams',
        value=f"{DATA['Stream'].mean():,.2f}",
        help="The average number of streams the artists' top ten songs have on Spotify",
    )
    artist_metrics_row.metric(
        'Average Views',
        value=f"{DATA['Views'].mean():,.2f}",
        help="The average number of views the artists' top ten songs have on their Youtube videos",
    )
    artist_metrics_row.metric(
        'Average Likes',
        value=f"{DATA['Likes'].mean():,.2f}",
        help="The average number of likes the artists' top ten songs have on Youtube videos",
    )

    style_metric_cards(
        background_color='#0E1117',
        border_color='#3D4044',
        border_left_color=None,
    )

def main_layout(DATA, artists):
    # Title text
    st.title(
        ":musical_note: Spotify Artists' Top Tens :musical_note:"
    )

    st.write("""
        Welcome to the Spotify Artists' Top Tens data visualization app.

        Here you can see the top ten songs by Spotify streams of various artists. Each song also has several characteristics; you can hover over the column name to find out more about it.
    """)

    # Filter data after getting the search
    DATA = filter_data(
        DATA,
        st.session_state.artist,
    )

    handle_dataframe(DATA)

    st.divider()

    # Search form
    st.header("Select an artist")

    st.write("""
        Here you can search for a specific artist to find their top ten songs in the table above. You can also find out about the average of the engagement metrics of their top ten songs.
    """)

    with st.expander('**Selection**'):
        handle_search_form(artists)
        handle_filtered_data_metrics(DATA)

    st.divider()

    # Characteristic vs metric plot
    
    st.header("Characteristic vs Metric Plot")

    st.write("""
        Here you can see a plot asking the question, 'what is the correlation between a song characteristic and their engagement?'

        You can choose which characteristic and metric to correlate in the selection below. If you selected an artist, you will be able to see the points for that artist's songs.
    """)

    handle_characteristic_vs_metric_plot(DATA)

if __name__ == '__main__':
    st.set_page_config(layout="wide")

    if 'artist' not in st.session_state:
        st.session_state.artist = None

    DATA = load_data()

    if DATA is None:
        print("ERROR: Data not found")
        exit(1)

    artists = get_artists(DATA)

    DATA = preprocess_data(DATA)

    main_layout(DATA, artists)

