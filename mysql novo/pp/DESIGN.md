Before the website could be implemented, I parsed a larged amount of data (json and HTML) with python from https://api.cs50.io/map/buildings, https://map.harvard.edu/, and ArcGIS data to set up the geojson file and sql database.

The SQL database has the same building ids as the geojson so the data could be cross referenced. Right now the geojson data is created and stored on GitHub and accessed via an URL.
This was the easiest and cleanest way to link it to Leaflet to create the shapes on the map.

Many things were done with javascript because I wanted to provide a smooth user experience using a dynamic interface.
For example, using the modal on the homepage prevented me from using Jinja because the HTML has to be changed dyanmically every time a new building is clicked on.
So I had to work around with Javascript/JQuery to search via Flask and to change the page.

For the edit feature, I embedded a rich text editor so that the users can edit the format of the description text.