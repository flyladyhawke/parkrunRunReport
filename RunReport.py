from bs4 import BeautifulSoup
import math
import requests
import re

class RunReportTemplates:
    VOLUNTEER_START_TEXT = 'We are very grateful to the volunteers who made this event happen:'
    PB_TEXT = 'New PB!'
    
    sectionHeadingTemplate = '''<div style="border: 1px solid #ccc; padding: 5px; text-align: center;">
<h3 style="padding: 0; margin: 0;"><a name="{}"></a>{}</h3>
</div>
'''
    sectionContentTemplate = '''<div style="border: 1px solid #ccc; padding: 5px;">
<p style="padding: 0; margin: 0;">{}</p>
</div>
'''
    separator = '<div style="height: 10px;"></div>'
    
    tableStart = '<table style="width: 100%; padding: 0; border-collapse: collapse;" cellspacing="0" cellpadding="0"><tbody>'
    
    tableHeader =  '''<tr>
<th style="width: 50%; text-align: center; border: 1px solid #ccc !important;">Runners ({} or more from last {} events)</th>
<th style="width: 50%; text-align: center; border: 1px solid #ccc !important;">Volunteers ({} or more from last {} events)</th>
</tr>
'''

    tableHeaderTemplate =  '<tr><th style="width: {}%; text-align: center; border: 1px solid #ccc !important;">{}</th></tr>'

    tableHeaderCellSummaryTemplate = '{} ({} or more from last {} events)'

    tableCell = '''<td style="padding-left: 10px; border-width: 0 0 1px 0 !important; border-style: solid  !important; border-color: #ccc !important;">
{}</td>
'''
    
    photoTemplate = '<img src="{}" alt="{}" width="{}" height="{}" />'
    
    tableEnd = '</tbody></table>' 

	
class RunReport(object):   
    resultsSystemText = ''
    templates = False
    currentEventVolunteers = []
    currentEventRunners = {}
    photos = []
    
    toc = []
    runCount = []
    
    runners = {}
    volunteers = {}
    
    VOLUNTEER_START_TEXT = 'We are very grateful to the volunteers who made this event happen:'
    PB_TEXT = 'New PB!'  

	
    def __init__(self):
        self.templates = RunReportTemplates()
    
	
    def setResultsSystem(self, text):
        text = text.strip()
        if text == '':
            return	
        self.resultsSystemText = text
        
        
    def setCurrentEventAll(self, text):
        text = text.strip()
        if text == '':
            return	
        # set currentEventRunners and currentEventVolunteers 
        self.setCurrentEventRunners(text)
        self.setCurrentEventVolunteers(text)
            
            
    def parseCurrentEvent(self, text, parseType):
        soup = BeautifulSoup(text,'html.parser')
        if parseType == 'runners':
            rows = soup.find(id="results").find("tbody").find_all("tr")
        elif parseType == 'volunteers':
            # <p class="paddedb">
            # We are very grateful to the volunteers who made this event happen:
            # Aaryan BHATIA, Naomi (Tullae) CROTTY, Darren JEFFREYS, Gregory MOORE, Sadia NAZIER, Jenny PATERSON, Elijah SUMMERS, Kaila SWYER, Rosemary WAGHORN, Ashley WILLIS, Nathan WRIGHT
            # </p>  
            start = soup.p.find(text=re.compile(self.VOLUNTEER_START_TEXT))
            pos = start.find(':')
            sub = start[pos+1:]
            rows = sub.split(', ')          
        return rows
    
            
    def setCurrentEventRunners(self, text):
        rows = self.parseCurrentEvent(text, 'runners')      
        for row in rows:
            details = self.getRunnerDetails(row.find_all("td"))
            if details:
                self.currentEventRunners[details['id']] = {"name":details['name'],"time":details['time']}
                
                
    def setCurrentEventVolunteers(self, text):              
        names = self.parseCurrentEvent(text, 'volunteers')          
        for n in names:
            self.currentEventVolunteers.append(n)
            
        
    def addTOC(self, anchor, heading):
        # Add to toc
        self.toc.append('<li><a href="#'+anchor+'">'+heading+'</a></li>')
        
        
    def getSectionHeading(self, anchor, heading):
        self.addTOC(anchor, heading)
        return self.templates.sectionHeadingTemplate.format(anchor, heading)
    
    
    def getSectionContent(self, content):
        return self.templates.sectionContentTemplate.format(content)
    
    def getSectionSeparator(self):
        return self.templates.separator
    
    
    def getCurrentEventVolunteerHTML(self):
        html = '<ul style="padding-bottom: 0;padding-top: 0;padding-left: 10px;margin-bottom: 0;margin-top: 0;margin-left: 10px">'
        for vol in self.currentEventVolunteers:
            html += '<li>'+vol+'</li>'
        html += '</ul>'
        return html
    
           
    def getRunnerDetails(self, cells):
        # <tr>
        # <td class="pos">2</td>
        # <td><a href="athletehistory?athleteNumber=111111" target="_top">Firstname LASTNAME</a></td>
        # <td>18:14</td>
        # <td><a href="../agecategorytable/?ageCat=SM30-34">SM30-34</a></td>
        # <td>71.12 %</td>
        # <td>M</td>
        # <td>2</td>
        # <td><a href="../clubhistory?clubNum=1187"/></td>
        # <td>New PB!</td>
        # <td>2</td>
        # <td style="min-width:72px"/>
        # </tr>
        cell = cells[1]
        pb = 0
        if cells[8] == self.PB_TEXT:
            pb = 1
        name = cell.get_text()
        time = cells[2].get_text()
        if name != 'Unknown':
            href = cell.a["href"]
            # format of href="athletehistory?athleteNumber=208507"
            pos = href.find('=')
            id = href[pos+1:]
            return {"id":id,"name":name,"time":time,"pb":pb}
        else:
            return False
        
        
    def addRunners(self, text):
        text = text.strip()
        if text == '':
            return	
        rows = self.parseCurrentEvent(text, 'runners') 
        eventCount = 0
        for row in rows:
            cells = row.find_all("td")
            details = self.getRunnerDetails(cells)
            if details:
                eventCount = eventCount + 1
                pbCount = 0
                if details['id'] in self.runners:
                    count = self.runners[details['id']]['count'] + 1
                    if details['pb'] == 1:
                        pbCount = self.runners[details['id']]['pbCount'] + 1
                else:
                    count = 1
                    if details['pb'] == 1:
                         pbCount = 1   
                
                self.runners[details['id']] = {"name":details['name'],"pbCount":pbCount,"count":count}
        self.runCount.append(eventCount);
        
        
    def addVolunteers(self, text):  
        text = text.strip()
        if text == '':
            return	
        names = self.parseCurrentEvent(text, 'volunteers') 
        
        for n in names:
            if n in self.volunteers:
                count = self.volunteers[n] + 1
            else:
                 count = 1
            self.volunteers[n] = count
            
    def addPhoto(self, text, size, photoType):
        text = text.strip()
        if text == '':
            return	
        startPos = text.find('[img]') + len('[img]')
        endPos = text.find('.jpg') + len('.jpg')
        flickrLink = text[startPos:endPos]
        
        self.photos.append({'link':flickrLink,'size':size,'type':photoType})
     
    def getPhotoLinks(self, photoType):
        html = ''
        for p in self.photos:
            if p['type'] == photoType:
                dims = p['size']
                if int(dims[0]) == 640:
                    dims[0] = 620
                    dims[1] = math.floor(620 * int(dims[1]) / 640)
                elif int(dims[1]) == 640:
                    dims[1] = 620
                    dims[0] = math.floor(620 * int(dims[0]) / 640)
                html += self.templates.photoTemplate.format(p['link'],p['type'],dims[0],dims[1])
        
        return html
        
    def getAestheticTimes(self):
        html = ''
        #print(self.currentEventRunners)
        for key, data in self.currentEventRunners.items():
            time = data['time']
            if time[-2:] == '00' or time[-2:] == time[0:2]:
                html += time + ' - ' + data['name'] + '<br/>'
            elif time[0] == time[1] and time[3] == time[4]:
                html += time + ' - ' + data['name'] + '<br/>'    
            elif time[0] == time[4] and time[1] == time[2]:
                html += time + ' - ' + data['name'] + '<br/>' 
        
        html = self.getSectionContent(html)
        return html
		
    def getPBSummary(self, pbLimit=2):
        events = len(self.runCount)
        regularPbs = {k:v for k,v in self.runners.items() if v['pbCount'] >= pbLimit}	
      
        header = []
        header.append(self.templates.tableHeaderCellSummaryTemplate.format('PBs', pbLimit, events))
		
        html = self.templates.tableStart 
        html += self.templates.tableHeaderTemplate.format(100, header)
        for l,v in regularPbs: 
            html += '<tr>'+self.templates.tableCell.format(v['name'])+'</tr>'

        html += self.templates.tableEnd
		
        return html
	
	
    def getAgeGroupFinisher(self):
        html = ''
		
        return html	
        
    def getRegularSummary(self, runnerLimit, volunteerLimit):
        events = len(self.runCount)
        regularRunners = {k:v for k,v in self.runners.items() if v['count'] >= runnerLimit}
        runnersList = sorted(regularRunners.items(), key=lambda x: x[1]['name'])  
        
        regularVolunteer = {k:v for k,v in self.volunteers.items() if v >= volunteerLimit}
        volunteerList = sorted(regularVolunteer.items(), key=lambda x: x[0])
                 
        header = []
        header.append(self.templates.tableHeaderCellSummaryTemplate.format('Runners', runnerLimit, events))
        header.append(self.templates.tableHeaderCellSummaryTemplate.format('Volunteers', volunteerLimit, events))
		
        html = self.templates.tableStart
        html += self.templates.tableHeader.format(runnerLimit, events, volunteerLimit, events)
        
        # work out a better way of transposing two arrays of diff lengths
        rows = {} 
        
        count = 1
        for l,v in runnersList: 
            rows[count] = []
            rows[count].append(self.templates.tableCell.format(v['name']))
            count = count + 1
          
        count = 1
        for key,value in volunteerList: 
            rows[count].append(self.templates.tableCell.format(key))
            count = count + 1 
            
        for key,value in rows.items():
            html += '<tr>'
            for r in value:
                html += r
                if len(value) == 1:
                    html += self.templates.tableCell.format('')
            html += "</tr>\n"
            
        html += self.templates.tableEnd
        
        return html;

class RunReportWeek(RunReport):
    
    runReportHTML = ''
	
	
    def createWeek(self, week, options):
        self.addSummarySection()
        self.addUpcomingSection()
        self.addVolunteerSection()
        
        if week == 1:
            self.addAgeGroupSection()
        elif week == 2:   
            self.addRegularSection(options['runnerLimit'],options['volunteerLimit'])
        elif week == 3:  
            self.addWeekPBSection(options['pbLimit'])
        elif week == 4:  
            self.addCommunitySection()
            
        self.addTimesSection()
        self.addPhotoSection()
    
        return self.getFullRunReportHTML()

    def addSummarySection(self):
        text = self.resultsSystemText
        html = self.getSectionHeading('summary','Summary')
        content = '<ul>';
        
        # get text until first .
        content += '<li>'+text[:text.find('.')+1]+'</li>'
        
        # get text from second last . (with white space at start trimmed) 
        pos = text.rfind('.', 0, text.rfind('.'))
        content += '<li>'+text[pos+1:].strip()+'</li>'
        
        content += '</ul>'
        content += 'Thanks to everyone for their participation and we hope to see everyone again next week. Remember to tell your friends parkrun is fun for everyone, it’s the taking part that counts.'
        
        html += self.getSectionContent(content) 
        html += self.getSectionSeparator()
        self.runReportHTML += html
    
    def addUpcomingSection(self):
        html = self.getSectionHeading('upcoming','Upcoming')
        content = '''
<div style="padding: 0px;width: 50%;margin-left: auto;margin-right: auto">
<img src="https://farm1.staticflickr.com/1741/41551984125_2039b19528_z.jpg" alt="runners" width="310" height="148" /></div>
<div>Please Note: Our anniversary is coming up on 23 June and Jells parkrun is turning <b>3</b>. We'll be having a pyjama run. Run in your pjs, dressing gown, bring your teddy bear along. And there will be cake!
<a href="https://www.facebook.com/events/1962473370464471/">Link to Facebook event</a></div>
'''
        html += self.getSectionContent(content)
        html += self.getSectionSeparator()
        self.runReportHTML += html
        
    def addVolunteerSection(self):  
        html = self.getSectionHeading('volunteers','Volunteers')
        content = '''
Jells parkrun relies on volunteers to bring you a free, timed event each week. We encourage everyone to volunteer because it's fun, rewarding, and giving to your community. 
Please review the <a href="https://www.parkrun.com.au/jells/volunteer/futureroster/">Future Roster</a> to see where volunteers are needed and email <a href="mailto:jellshelpers@parkrun.com">jellshelpers@parkrun.com</a> 
if you can help. The wonderful volunteers who made this event possible are:
'''
        content += self.getCurrentEventVolunteerHTML()
        html += self.getSectionContent(content)      
        html += self.getPhotoLinks('volunteer')
        html += self.getSectionSeparator()
        self.runReportHTML += html
    
    def addAgeGroupSection(self):
        html = self.getSectionHeading('agegroup','Age Group First Finishers')
        html += self.getAgeGroupFinisher()
        self.runReportHTML += html  
        
    def addRegularSection(self, runnerLimit=7, volunteerLimit=2):
        html = self.getSectionHeading('regular','Regular Runners / Volunteers')
        html += self.getRegularSummary(runnerLimit,volunteerLimit)
        self.runReportHTML += html  
        
    def addWeekPBSection(self, pbLimit=2):
        html = self.getSectionHeading('pbs','Regular PBs')
        html += self.getPBSummary(pbLimit)
        self.runReportHTML += html
            
    def addCommunitySection(self):
        html = self.getSectionHeading('fun','Having Fun')
        self.runReportHTML += html
        
    def addTimesSection(self):
        html = self.getSectionHeading('times','Aesthetically pleasing times')
        html += self.getAestheticTimes()
        html += self.getSectionSeparator()
        self.runReportHTML += html
            
    def addPhotoSection(self):
        html = self.getSectionHeading('photos','Photos')
        html += self.getPhotoLinks('photo')
        self.runReportHTML += html
        
    def getRunReportHeader(self):
        return '<h1 style="padding: 0;margin: 0">Run Report</h1>'
        
    def getRunReportTOC(self):
        html = '<ul>'
        for toc in self.toc:
           html += toc
        html += '</ul>'
        
        return html    
        
    def getFullRunReportHTML(self):
        html = self.getRunReportHeader()
        html += self.getRunReportTOC()
        html += self.runReportHTML
        
        return html
                
 