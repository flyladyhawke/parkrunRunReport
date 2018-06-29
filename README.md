parkrun Run Report
=======
Jupiter Notebook to create html code for wordpress parkrun run reports

### Result System
* [List of all evNum](https://results-service.parkrun.com/resultsSystem/App/eventJournoReportHTML.php)
* Search for the parkrun name to get the evNum:
* Jells: 
  * [https://results-service.parkrun.com/resultsSystem/App/eventJournoReportHTML.php?evNum=1153](https://results-service.parkrun.com/resultsSystem/App/eventJournoReportHTML.php?evNum=1153) 
* Karkarook:
  * [https://results-service.parkrun.com/resultsSystem/App/eventJournoReportHTML.php?evNum=1541](https://results-service.parkrun.com/resultsSystem/App/eventJournoReportHTML.php?evNum=1541)  
* Copy text from results service into result service cell between the two ''' and '''

### Photos 
**facebook**
* Go through this week’s photos on the facebook page for the parkrun and select 9 or 10 to use in the report. 
* Try to represent the diversity of our run’s community. 
* Include one of the volunteers, and one of each milestone runner if possible
* You’ll probably have to rename them as the file names assigned by facebook are woeful.
* Follow the social media guidelines from the [https://wiki.parkrun.com/index.php/Index](https://wiki.parkrun.com/index.php/Index)

**flickr upload**  
* If you don't have a flickr account, create one
* Go to upload page when logged in
* [https://www.flickr.com/photos/upload/](https://www.flickr.com/photos/upload/)
* drag and drop photos onto page
* Make sure they are able to be viewed by anyone - set viewing privacy to public.
* Add the following tags to all at once 
* &lt;parkrunname&gt;\_parkrun\_&lt;eventnumber&gt; e.g. jells\_parkrun\_160
* &lt;parkrunname&gt;
* parkrun
* after tagging, finalise the upload by clicking on the 'Upload x photos' button

**flickr add to group**   
* Join the &lt;parkrunname&gt;-parkrun flickr group if you haven't already
* Add your photos to the photo pool for the parkrun 
* https://www.flickr.com/groups_pool_add.gne?path=<parkrunname>-parkrun
* search the &lt;parkrunname&gt;\_parkrun\_&lt;eventnumber&gt; tag and bring up just the ones from this week.
* add the photos to the photo pool for the parkrun 6 at a time

**flickr get urls for photo links**   
* go to the main flickr group page
* https://www.flickr.com/groups/<parkrunname>-parkrun/
* search for the &lt;parkrunname&gt;\_parkrun\_&lt;eventnumber&gt; tag
* Click on each photo. 
* Click on the 'Share Photo' icon
* Click on BBCode
* Note the width and height on that page as well.
* Copy the code into the photos cell between the ''' and '''
* Enter the width and height of the photo as well
* Enter the section for the photo to appear - options: summary, volunteer, photo
* run.addPhoto(text, ['&lt;width&gt;','&lt;height&gt;'], '&lt;section&gt;')
* e.g. 
  * run.addPhoto(text, ['640','427'], 'photo')
* to add more photos, copy and paste as many as necessary

### Event Results
* Since parkrun does not allow webscraping, html code from view source of event result pages need to be copied into the notebook.
* http://www.parkrun.com.au/&lt;parkrunname&gt;/results/weeklyresults/?runSeqNumber=&lt;eventnumber&gt;
* e.g.
* http://www.parkrun.com.au/jells/results/weeklyresults/?runSeqNumber=154
* Open url in new browser window, right click and select 'View page source'
* use control-f to search for  id="results"
* copy from the 
  * &lt;table class="sortable" id="results" 
* to the following text on the next line
  * What is this table? &lt;/h3&gt; 
* paste in the events cell on the blank line between the ''' and '''


