from flask import Blueprint, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import folium
from folium import IFrame
import base64
import tempfile
import os
from sqlalchemy.orm import Session
from config import SessionLocal
from services.models import Landmark 
from services.models import FileStorage
from sqlalchemy.orm import Session
from sqlalchemy import update
from datetime import datetime
from config import engine
from folium import Tooltip

ox.config(use_cache=True, log_console=True)

outer_map_bp = Blueprint("outer_map_bp", __name__)

# Function to fetch landmarks from the database
def get_landmarks():
    db: Session = SessionLocal()
    landmarks = db.query(Landmark).all()
    db.close()
    return landmarks

landmark = get_landmarks()

def get_coordinates(landmark_name):
    db: Session = SessionLocal()
    landmark = db.query(Landmark).filter(Landmark.landmark_name == landmark_name).first()
    db.close()
    if landmark:
        return (landmark.latitude, landmark.longitude)
    return None

@outer_map_bp.route('/distance', methods=['POST', 'GET'])
def distance():
    if request.method == 'POST':
        data = request.json
        source = data['source']
        target = data['target']
        optim = data['optimizer']
        mode = data['mode']

        source_coordinates = get_coordinates(source)
        target_coordinates = get_coordinates(target)
        # with SessionLocal() as session:
        #     stmt = (
        #         update(FileStorage)
        #         .where(FileStorage.timestamp.is_(None))
        #         .values(timestamp=datetime.utcnow())
        #     )
        #     result = session.execute(stmt)
        #     print(f"Rows affected: {result.rowcount}")
        #     session.flush() 
        #     session.commit()
        
        start_latlng = (source_coordinates[0],source_coordinates[1])
        end_latlng = (target_coordinates[0],target_coordinates[1])
        optimizer = optim
        graph = ox.graph.graph_from_bbox(12.8303, 12.8169, 80.0563, 80.0363, network_type=mode)
        # find the nearest node to the start location
        orig_node = ox.distance.nearest_nodes(graph, start_latlng[1], start_latlng[0])
        # find the nearest node to the end location
        dest_node = ox.distance.nearest_nodes(graph, end_latlng[1], end_latlng[0])
        
        # Get updated lat/lon for matched nodes
        orig_x, orig_y = graph.nodes[orig_node]['x'], graph.nodes[orig_node]['y']
        dest_x, dest_y = graph.nodes[dest_node]['x'], graph.nodes[dest_node]['y']
        
        start_latlng = (orig_y, orig_x)
        end_latlng = (dest_y, dest_x)

        #  find the shortest path
        shortest_route = nx.shortest_path(graph,
                                          orig_node,
                                          dest_node,
                                          weight=optimizer)
        le=nx.shortest_path_length(graph,orig_node,dest_node, method='dijkstra',weight=optimizer)
        edges = list(zip(shortest_route[:-1], shortest_route[1:]))
        m = folium.Map(location=[start_latlng[0], start_latlng[1]], zoom_start=8)
        
        
        polyLinePopupContent = ''
        
        if optimizer=='time':
            Info='It will take you '+str(le)+' minutes'
            polyLinePopupContent = str(le) + ' minutes'
        elif optimizer=='length':
            Info='The distance between your source and target is '+str(le)+' meters'
            polyLinePopupContent = str(le) + ' meters'
        else:
            Info='Please select your source and target'
            
        if mode == 'walk':
            polyLinePopupContent = '&#x1F6B6; ' + polyLinePopupContent  # 🚶 Walking
        elif mode == 'bike':
            polyLinePopupContent = '&#x1F6B4; ' + polyLinePopupContent  # 🚴 Biking
        elif mode == 'drive':
            polyLinePopupContent = '&#x1F697; ' + polyLinePopupContent  # 🚗 Car


        
        # Plot the route with hover popups
        for u, v in edges:
    
            # Get coordinates of edge
            u_lat, u_lon = graph.nodes[u]['y'], graph.nodes[u]['x']
            v_lat, v_lon = graph.nodes[v]['y'], graph.nodes[v]['x']
            
            # Get weight (distance/time)
            edge_data = graph.get_edge_data(u, v)[0]  # First edge data (multi-edge case)
            weight = edge_data.get(optimizer, "Unknown")  # Get distance/time
            
            # Create polyline with tooltip (hover effect)
            folium.PolyLine(
                [[u_lat, u_lon], [v_lat, v_lon]],
                color="blue",
                weight=5
            ).add_to(m).add_child(folium.Tooltip(f'{polyLinePopupContent}'))

            
        shortest_route_map = m
        # Add Marker
        if source == 'Tech Park':
            encoded = base64.b64encode(open('static/img/techpark.jpg', 'rb').read())
            html = '''
            <div class="row">
            <div class="columntpr"><img src="data:image/png;base64,{}" width="250" height="200"></div>
            </div>'''.format
            iframe = IFrame(html(encoded.decode('UTF-8')), width=250, height=200)
            popup = folium.Popup(iframe, max_width=400)
            start_marker = folium.Marker(location=start_latlng, icon=folium.Icon(color='green'), popup=popup,
                                         tooltip=source)
            print(start_marker)
        elif source == 'BIO-Tech Block':
            encoded = base64.b64encode(open('static/img/BioTech.jpg', 'rb').read())
            html = '''
            <div class="row">
            <div class="columntpr"><img src="data:image/png;base64,{}" width="250" height="200"></div>
            </div>'''.format
            iframe = IFrame(html(encoded.decode('UTF-8')), width=250, height=200)
            popup = folium.Popup(iframe, max_width=400)
            # start_latlng = (start_latlng[0], start_latlng[1])
            start_marker = folium.Marker(location=start_latlng, icon=folium.Icon(color='green'), popup=popup,
                                         tooltip=source)
        elif source == 'SRM University Building':
            encoded = base64.b64encode(open('static/img/ub.jpg', 'rb').read())
            html = '''
            <div class="row">
            <div class="columntpr"><img src="data:image/png;base64,{}" width="250" height="200"></div>
            </div>'''.format
            iframe = IFrame(html(encoded.decode('UTF-8')), width=250, height=200)
            popup = folium.Popup(iframe, max_width=400)
            # start_latlng = (start_latlng[0], start_latlng[1])
            start_marker = folium.Marker(location=start_latlng, icon=folium.Icon(color='green'), popup=popup,
                                         tooltip=source)
        else:
            print(source)
            # start_latlng = (start_latlng[0], start_latlng[1])
            start_marker = folium.Marker(location=start_latlng, icon=folium.Icon(color='green'), popup=source,
                                         tooltip=source)
        if target == 'Tech Park':
            # Encode the image in Base64
            with open('static/img/techpark.jpg', 'rb') as image_file:
                encoded_t = base64.b64encode(image_file.read()).decode('UTF-8')
            
            # Create the HTML to embed the image
            html_t = f'<img src="data:image/jpeg;base64,{encoded_t}" width="250" height="200">'
            
            # Embed the HTML in an IFrame
            iframe_t = IFrame(html_t, width=320, height=240)  # Add some padding for better appearance
            
            # Create a Popup using the IFrame
            popup_t = folium.Popup(iframe_t, max_width=320)
            
            # Define the marker location and popup
            end_marker = folium.Marker(
                location=end_latlng,
                icon=folium.Icon(color='red'),
                popup=popup_t,
                tooltip=target
            )
            
        elif target == 'BIO-Tech Block':
            encoded_t = base64.b64encode(open('static/img/BioTech.jpg', 'rb').read())
            html_t = '<img src="data:image/png;base64,{}">'.format
            iframe_t = IFrame(html_t(encoded_t.decode('UTF-8')), width=250, height=200)
            popup_t = folium.Popup(iframe_t, max_width=400)
            # end_latlng = (end_latlng[0], end_latlng[1])
            end_marker = folium.Marker(location=end_latlng, icon=folium.Icon(color='red'), popup=popup_t,
                                       tooltip=target)
        elif target == 'SRM University Building':
            encoded_t = base64.b64encode(open('static/img/ub.jpg', 'rb').read())
            html_t = '<img src="data:image/png;base64,{}" width="250" height="200" >'.format
            iframe_t = IFrame(html_t(encoded_t.decode('UTF-8')), width=250, height=200)
            popup_t = folium.Popup(iframe_t, max_width=400)
            # end_latlng = (end_latlng[0], end_latlng[1])
            end_marker = folium.Marker(location=end_latlng, icon=folium.Icon(color='red'), popup=popup_t,
                                       tooltip=target)
        else:
            # end_latlng = (end_latlng[0], end_latlng[1])
            end_marker = folium.Marker(location=end_latlng, icon=folium.Icon(color='red'), popup=target,
                                       tooltip=target)
        # add the circle marker to the map
        start_marker.add_to(shortest_route_map)
        end_marker.add_to(shortest_route_map)
        print(shortest_route_map)
        shortest_route_map.save('static/DestinationMap.html')
          # Save the map to a temporary HTML file
        tmp_html = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        shortest_route_map.save(tmp_html.name)
        tmp_html.close()

        # Read the content of the HTML file
        with open(tmp_html.name, 'r') as file:
            html_content = file.read()

        # Remove the temporary HTML file after reading its content
        os.unlink(tmp_html.name)
         # Return the HTML content as JSON response
        return jsonify({'html_content': html_content, 'info': Info})
        # return render_template('distance.html', landmarks=landmark,final_map='static/Destination_map.html',modes=['walk','bike','drive'],optims=['length','time'],Info=Info)
    return render_template('distance.html',landmarks=landmark,final_map='static/DestinationMap.html',modes=['walk','bike','drive'],optims=['length','time'],Info='Please select your source and target')