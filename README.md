# UOCIS322 - Project 6 #
Online brevet time calculator webapp, database, api, and api interface with login and (not very fancy but usable) UX.
Author: Jeremy Lavagnino, jlavagni@uoregon.edu
## Overview

Reimplementation of the RUSA ACP controle time calculator with Flask and AJAX.

## About ACP controle times

That's *"controle"* with an *e*, because it's French, although "control" is also accepted. Controls are points where a rider must obtain proof of passage, and control[e] times are the minimum and maximum times by which the rider must arrive at the location.

The algorithm for calculating controle times is described here [https://rusa.org/pages/acp-brevet-control-times-calculator](https://rusa.org/pages/acp-brevet-control-times-calculator). Additional background information is given here [https://rusa.org/pages/rulesForRiders](https://rusa.org/pages/rulesForRiders). Some of the specifications are somewhat ambiguous, so the current RUSA ACP control time calculator ([https://rusa.org/octime_acp.html](https://rusa.org/octime_acp.html)) has been used to clarify them. Specifically, the table with minimum/maximum speeds has the boundary distances (such as 200 km) in multiple rows, making unclear which one to use. I determined that the first row the value appears in is always used (so for 200 km, that would mean a max speed of 34 km/h instead of 32), which is what my program uses. Additionally, I determined through experimentation with the online calculator that it rounds up to the nearest minute from 30+ seconds and down from 29 seconds and below, which is how I implemented the rounding behaviour in this program. Also, the algorithm now takes into account the set close times for brevets available at https://en.m.wikipedia.org/wiki/Randonneuring.

## Usage
Use docker-compose in the brevets directory to run and build the images for the sites, api, and database. To use the main website, simply input the distances from the start of the controle locations in either of the first two columns depending on whether you prefer to use miles or kilometers, and the start/close time columns will be calcualted and automatically filled in. Note that all distances are converted to km for backend calculations.

## Saving times to the database

You can save one set of time calculations at a time to the database for seperate viewing by pressing the "Submit" button. Pressing "Submit" will save the distance in kilometers, open time, and close time of all the controles currently in the form, and will overwrite any previously-saved values. If there are multiple controls at the same distance in the form, only one of them will be saved in the database. Pressing "Display" will open a seperate page displaying all of the most-recently submitted control information. If no times have been submitted, "Display" will only display an error message on the main page.

## Database API

A RESTful service to expose the times stored in the database is also included at port 5495. There are three basic services: listAll to list both open and close times, listOpenOnly for just open times, and listCloseOnly for only close times. After those, you can also specify the format by adding csv or json, though the default is json if format is not specify. The query parameter top can be used to get just the top k times in ascending order. Note that a k value of zero is the default and will list all times. So, an example api call to get the top 5 open times in CSV format would be: 
"http://<host>:5495/listOpenOnly/csv?top=5". Also note that though the controle distances are also stored in the database, there is no way to retrieve them using the API.
**The API now requires a valid token to access. Register using the API Interface Website and login, then use the data retrieval tool which will automatically fill in a valid token in order to use the API**
   
## API Interface Website

A website is also provided in order to make retrieving data using the API a little more user-friendly. A valid login is required to access the data retrieval page, otherwise a page with "Login" and "Register" buttons will be displayed. First, click "Register" and fill in a username that has not been used yet and a password of your choice. If succesful, you will be directed back to the page with "Login" and "Register" buttons. Now you can press "Login", and if you login using the correct credentials, you will be redirected to the data retrieval page. The various options can be selected or entered on a webpage (format, number to display, whether to display only open, only close, or both) and then pressing submit will automatically form the API request and return the appropriate data in the appropriate format, although not very fancy-looking because I got lazy. Once you are done, use the Logout button at the bottom of the page to logout. Otherwise, the tokens will timeout automatically after 10 minutes.


## Credits

Michal Young, Ram Durairajan, Steven Walton, Joe Istas.
