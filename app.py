
import googlemaps
import pandas as pd
import streamlit as st
st.set_page_config('Available Properties @ Basico', layout='wide')
from streamlit.components.v1 import html   # use this to add js

""" Module documentation
"""


@st.cache_data
def load_data():
    """ Loads all the data needed
    """
    gmaps = googlemaps.Client(key='{put key here}')
    df = pd.read_csv("activos_prx_lat.csv", encoding='utf-8', sep=";")
    new_df = pd.DataFrame(columns=['latlon', 'city', 'province'])
    for index, lat_long in enumerate(df["uwgoogle"].dropna().unique()):
        # new_df.loc[index+1] = [float(i.strip()) for i in lat_long.split(',')]
        reverse_geocode_result = gmaps.reverse_geocode((lat_long))[0]['address_components']
        new_df.loc[index+1] = [
                                lat_long, 
                                reverse_geocode_result[2]['long_name'].lower(), 
                                reverse_geocode_result[3]['long_name'].lower()
                            ]
    return new_df


def generate_map(city, province, st_column):
    """ A callback function for the view map button in the app
    """
    # filter the data df by city and province
    markers = ""
    df = load_data()
    if province != '':
        df = df[df['province']==province.lower()]
    if city != '':
        df = df[df['city']==city.lower()]
    for position in df['latlon']:
        marker_template = f'<gmp-advanced-marker position="{position}"></gmp-advanced-marker> '
        markers += marker_template
    
    html_string = """ <!DOCTYPE html>
                <html>
                <head>
                    <title>Basico Properties</title>
                    <!-- The callback parameter is required, so we use console.debug as a noop -->
                    <script async src="https://maps.googleapis.com/maps/api/js?key={put key here}&callback=console.debug&libraries=maps,marker&v=beta">
                    </script>
                    <style>
                    /* Always set the map height explicitly to define the size of the div
                    * element that contains the map. */
                    gmp-map {
                        height: 100%;
                    }

                    /* Optional: Makes the sample page fill the window. */
                    html,
                    body {
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }
                    </style>
                </head>
                <body>
                    <gmp-map center="39.862832,-4.027323" zoom="6" map-id="DEMO_MAP_ID">
            """ + markers + """
                    </gmp-map>
                </body>
                </html>
            """
    with st_column:
        html(html_string, height=550, scrolling=True)
        # st_column.map(data, color="#0000FF")        # use streamlit mapbox


def main():
    """ The main method
    """

    st.markdown("""
            <style>
                   .block-container {
                        padding-top: 1%;
                        padding-bottom: 10%;
                        padding-left: 10%;
                        padding-right: 10%;
                    }
            </style>
            """, unsafe_allow_html=True)
    header, main, map = st.container(), st.container(), st.container()

    data = load_data()
    # cities_, provinces_, data_= [''], [''], {}
    # for row in data.iterrows():
    #     city, province = row[1]['city'], row[1]['province']
    #     if province not in data_:
    #         data_[province] = [city]
    #     if city not in data_[province]:
    #         data_[province] += [city]
    # provinces_ += data_.keys()

    cities_ = [''] + [i[0].upper() + i[1:] for i in data['city'].unique()]
    provinces_ = [''] + [i[0].upper() + i[1:] for i in data['province'].unique()]

    with header:
        # you only use the title once
        st.markdown("<h1 style='text-align: center;'>Available Properties @ Basico</h1>", unsafe_allow_html=True)
        
        # add some space
        for i in range(3):
            st.text('')
    
    with main:
        submain, _,  map = main.columns([1, 0.5, 4.5]) # the list specifies the ratio of size of the containers
        submain.markdown("<h4>Filter By:</h4>", unsafe_allow_html=True)
        city, province = '', ''
        cities = submain.columns(1)[0]
        city = cities.selectbox(label="City", options=cities_)

        provinces = submain.columns(1)[0]
        province = provinces.selectbox(label="Province", options=provinces_)

        # Add some space
        with submain.columns(1)[0]:
            st.write('')
            st.write('')
        submain.button('Reset Map', on_click=generate_map(city, province, map))
        

if __name__=="__main__":
    main()
