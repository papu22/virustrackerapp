






def map_data():

    # data = pandas.read_csv("Volcanoes_USA.txt")
    # lat = list(data["LAT"])
    # lon = list(data["LON"])
    # elev = list(data["ELEV"])
    #
    # def color_producer(elevation):
    #     if elevation < 1000:
    #         return 'green'
    #     elif 1000 <= elevation < 3000:
    #         return 'orange'
    #     else:
    #         return 'red'
    #
    # map = folium.Map(location=[38.58, -99.09], zoom_start=1, tiles="Stamen Terrain")
    #
    # fgv = folium.FeatureGroup(name="Volcanoes")
    #
    # for lt, ln, el in zip(lat, lon, elev):
    #     fgv.add_child(folium.CircleMarker(location=[lt, ln], radius=6, popup=str(el) + " m",
    #                                       fill_color=color_producer(el), fill=True, color='grey', fill_opacity=0.7))
    #
    # fgp = folium.FeatureGroup(name="Population")
    #
    # fgp.add_child(folium.GeoJson(data=open('world.json', 'r', encoding='utf-8-sig').read(),
    #                              style_function=lambda x: {'fillColor': 'green' if x['properties']['POP2005'] < 10000000
    #                              else 'orange' if 10000000 <= x['properties']['POP2005'] < 20000000 else 'red'}))
    #
    # map.add_child(fgv)
    # map.add_child(fgp)
    # map.add_child(folium.LayerControl())
    #
    # example = map.get_root().render()
    #
    #
    # return example
    # chart_studio.tools.set_credentials_file(username='papu22', api_key='9CCx7Vg3NDWMtxHwx5Ie')
    #
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(y=[2, 1, 4, 3]))
    # fig.add_trace(go.Bar(y=[1, 4, 3, 2]))
    # fig.update_layout(title='Hello Figure')
    # url = py.plot(fig,config=dict(
    #                 displayModeBar=True
    #             ), filename = 'basic-line', auto_open=False)
    # print(url)
    pass







# with open('do_re_mi.txt', 'w') as f:
#     f.write(example)
#
#
# map.save("Map1.html")
map_data()