from bs4 import BeautifulSoup
import re
import src.RunReportTemplates as reportTemplates
	
class RunReport(object):  
    templates = False
    parkrunName = ''  
    parkrunEventNumber = ''
    options = {'runnerLimit':7, 'volunteerLimit':2, 'pbLimit':2, 'eventNumber':8}
    
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
	
    def __init__(self, name, eventNumber):
        self.templates = reportTemplates.StandardTemplate()   
        self.parkrunName = name
        self.parkrunEventNumber = eventNumber   
  
        # make sure these are reset each time you call the init
        self.runners = {}
        self.volunteers = {}
	
    def setResultsSystem(self, text):
        text = text.strip()
        if text == '':
            return	
        self.resultsSystemText = text  

    def parseEvent(self, text, is_current=False):
        text = text.strip()
        if text == '':
            return	
        if is_current:
            self.setCurrentEvent(text)
        self.parseRunners(text)	
        self.parseVolunteers(text)		
        
    def setCurrentEvent(self, text):
        text = text.strip()
        if text == '':
            return	
        # set currentEventRunners and currentEventVolunteers 
        self.setCurrentEventRunners(text)
        self.setCurrentEventVolunteers(text)            
            
    def parseCurrentEvent(self, text, parseType):
        soup = BeautifulSoup(text,'html.parser')		
        if parseType == 'runners':
			# get every row from the result table
            rows = soup.find(id="results").find("tbody").find_all("tr")
        elif parseType == 'volunteers':
            # <p class="paddedb">
            # We are very grateful to the volunteers who made this event happen:
            # Aaryan BHATIA, Naomi (Tullae) CROTTY, Darren JEFFREYS, Gregory MOORE, Sadia NAZIER, Jenny PATERSON, Elijah SUMMERS, Kaila SWYER, Ashley WILLIS, Nathan WRIGHT
            # </p>  
            start = soup.p.find(text=re.compile(self.VOLUNTEER_START_TEXT))
            pos = start.find(':')
            sub = start[pos+1:]
            rows = sub.split(', ')          
        return rows    
            
    def setCurrentEventRunners(self, text):        
        self.currentEventRunners = {}
        rows = self.parseCurrentEvent(text, 'runners')      
        for row in rows:
            details = self.getRunnerDetails(row.find_all("td"))
            if details:
                self.currentEventRunners[details['id']] = {"name":details['name'],"time":details['time'],"ageGroup":details['ageGroup']}                
                
    def setCurrentEventVolunteers(self, text):    
        self.currentEventVolunteers = []    
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
        name = cell.get_text()        
        if name != 'Unknown':
            href = cell.a["href"]
            # format of href="athletehistory?athleteNumber=208507"
            pos = href.find('=')
            id = href[pos+1:]
            
            time = cells[2].get_text()
            ageGroup = cells[3].get_text()
            position = cells[0].get_text()
            pb = 0
            if cells[8].get_text() == self.PB_TEXT:
                pb = 1

            return {"id":id,"name":name,"time":time,"pb":pb,"ageGroup":ageGroup,"position":position}
        else:
            return False  
        
    def parseRunners(self, text):
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
                        pbCount = self.runners[details['id']]['pbCount']
                else:
                    count = 1
                    if details['pb'] == 1:
                         pbCount = 1   
                
                self.runners[details['id']] = {"name":details['name'],"pbCount":pbCount,"count":count}
        self.runCount.append(eventCount); 
        
    def parseVolunteers(self, text):  
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
            
    def addPhoto(self, text, size, photoType, title=''):
        text = text.strip()
        if text == '':
            return	
        startPos = text.find('[img]') + len('[img]')
        endPos = text.find('.jpg') + len('.jpg')
        flickrLink = text[startPos:endPos]
        
        self.photos.append({'link':flickrLink,'size':size,'type':photoType,'title':title})   
     
    def getPhotoLinks(self, photoType):
        html = ''
        pictureWidth = 620
        for p in self.photos:
            if p['type'] == photoType:
                dims = p['size']
                title = p['title']
                currWidth = int(dims[0])
                currHeight = int(dims[1])
                if currWidth >= currHeight:
                    dims[0] = pictureWidth
                    dims[1] = (pictureWidth * currHeight) // currWidth
                elif currHeight > currWidth:
                    # get two pictures on one row
                    dims[0] = pictureWidth // 2 - 5
                    dims[1] = ((pictureWidth / 2 - 5) * currHeight) // currWidth                   
                html += self.templates.photoTemplate.format(p['link'],p['type'],dims[0],dims[1],title)
                # TODO add &nbsp; if odd count
        
        return html       
        
    def getAestheticTimes(self):
        html = ''
        for key, data in self.currentEventRunners.items():
            time = data['time']
            # end in :00 or start = end like 21:21
            if time[-2:] == '00' or time[-2:] == time[0:2]:
                html += time + ' - ' + data['name'] + '<br/>'
            # e.g. 22:33    
            elif time[0] == time[1] and time[3] == time[4]:
                html += time + ' - ' + data['name'] + '<br/>'  
            # e.g. 21:12               
            elif time[0] == time[4] and time[1] == time[2]:
                html += time + ' - ' + data['name'] + '<br/>' 
        
        html = self.getSectionContent(html)
        return html 

    def getTableHeaderCellTemplate(self, width, header, colspan=1):
        return self.templates.tableHeaderCellTemplate.format(width, colspan, header)
        
    def getSummaryTableHTML(self, headers, selected_list):
        width = 100 // len(headers)
     
        html = self.templates.tableStart 
        html += '<tr>'      
        for header in headers:
            html += self.getTableHeaderCellTemplate(width, header, 2)
        html += '</tr>'
        
        count = 0;       
        for l,v in selected_list: 
            if count % 2 == 0:
                html += '<tr>'
            html += self.templates.tableCell.format(v['name'])
            if count % 2 == 1:
                html += '</tr>'
            count += 1

        html += self.templates.tableEnd
        return html
        
    def getPBSummary(self, pbLimit=2):
        events = len(self.runCount)

        selected = {k:v for k,v in self.runners.items() if v['pbCount'] >= pbLimit}
        selectedList = sorted(selected.items(), key=lambda x: x[1]['name'])
		 
        headers = []
        headers.append(self.templates.tableHeaderCellSummaryTemplate.format('PBs', pbLimit, events))
		
        html = self.getSummaryTableHTML(headers, selectedList)
		
        return html	
        
    def calcAgeGroups(self):
        list = self.currentEventRunners
        ageGroup = {}
        for l, v in list.items():
            age = v['ageGroup']
            ageNumber = age[2:]
            if age[0:2] == 'SM' or age[0:2] == 'VM':
                if ageNumber not in ageGroup:
                    ageGroup[ageNumber] = {'menName':'','menTime':'','womenName':'','womenTime':''}
                if ageGroup[ageNumber]['menName'] == '':
                    ageGroup[ageNumber]['menName'] = v['name']
                    ageGroup[ageNumber]['menTime'] = v['time']
            elif age[0:2] == 'SW' or age[0:2] == 'VW':
                if ageNumber not in ageGroup:
                    ageGroup[ageNumber] = {'menName':'','menTime':'','womenName':'','womenTime':''} 
                if ageGroup[ageNumber]['womenName'] == '':
                    ageGroup[ageNumber]['womenName'] = v['name']
                    ageGroup[ageNumber]['womenTime'] = v['time']
        sortedAge = sorted(ageGroup.items(), key=lambda x: x[0])   
        return sortedAge 
        
    def getAgeGroupFinisher(self):        
        list = self.calcAgeGroups()
        html = self.templates.tableStart
        html += '<tr>'
        html += self.getTableHeaderCellTemplate(20, 'Age Group')
        html += self.getTableHeaderCellTemplate(40, 'Men', 2)
        html += self.getTableHeaderCellTemplate(40, 'Women', 2)
        html += '</tr>'
        for l, v in list:
            html += '<tr>'  
            html += self.templates.tableCell.format(l)
            html += self.templates.tableCell.format(v['menName'])
            html += self.templates.tableCell.format(v['menTime'])
            html += self.templates.tableCell.format(v['womenName'])
            html += self.templates.tableCell.format(v['womenTime'])
            html += '</tr>'         
        html += self.templates.tableEnd
        return html	
        
    def getRegularSummary(self, runnerLimit, volunteerLimit):
        events = len(self.runCount)
        regularRunners = {k:v for k,v in self.runners.items() if v['count'] >= runnerLimit}
        runnersList = sorted(regularRunners.items(), key=lambda x: x[1]['name'])  
        
        regularVolunteer = {k:v for k,v in self.volunteers.items() if v >= volunteerLimit}
        volunteerList = sorted(regularVolunteer.items(), key=lambda x: x[0])
                 
        headers = []
        headers.append(self.templates.tableHeaderCellSummaryTemplate.format('Runners', runnerLimit, events))
        headers.append(self.templates.tableHeaderCellSummaryTemplate.format('Volunteers', volunteerLimit, events))
        width = 100 / len(headers)
         
        html = self.templates.tableStart
        html += self.templates.tableHeader.format(runnerLimit, events, volunteerLimit, events)
        html += '<tr>'      
        for header in headers:
            html += self.getTableHeaderCellTemplate(width, header)
        html += '</tr>'
        
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
    
    parkrunWeek = 1
    runReportHTML = ''	
    
    def __init__(self, name, eventNumber, week, options):
        RunReport.__init__(self, name, eventNumber)
        self.parkrunWeek = week
        # merge options
        self.options = {**self.options, **options} 
        
        self.printUrls()
        
    def printUrls(self):
        links = []
        eventNumber = str(self.parkrunEventNumber);
        links.append('tag: '+self.parkrunName+'_parkrun_'+eventNumber)
        links.append('tag: '+self.parkrunName)
        links.append('tag: parkrun')
        links.append('https://www.flickr.com/groups_pool_add.gne?path='+self.parkrunName+'-parkrun')
        links.append('https://www.flickr.com/groups/'+self.parkrunName+'-parkrun/')               
        links.append('http://www.parkrun.com.au/'+self.parkrunName+'/results/weeklyresults/?runSeqNumber='+eventNumber)
        
        if self.parkrunWeek == 2 or self.parkrunWeek == 3:
             for i in range(1, self.options['eventNumber']):
                eventNumber = str(self.parkrunEventNumber - i)
                links.append('http://www.parkrun.com.au/'+self.parkrunName+'/results/weeklyresults/?runSeqNumber='+eventNumber)
          
        # TODO display as html  
        print('Links to use in the below sections')
        print("\n".join(links))
	
    def createWeek(self, week=False, options=False):
        self.addSummarySection()
        self.addUpcomingSection()
        self.addVolunteerSection()
        self.addMilestoneSection()
        
        # allow override of week and options since week and options in class init are only used for link creation.
        if week != False:
            self.parkrunWeek = week
            
        # merge options
        if options != False:
            self.options = {**self.options, **options}     
        
        if self.parkrunWeek == 1:
            self.addAgeGroupSection()
        elif self.parkrunWeek == 2:   
            self.addRegularSection(self.options['runnerLimit'],self.options['volunteerLimit'])
        elif self.parkrunWeek == 3:  
            self.addWeekPBSection(self.options['pbLimit'])
        elif self.parkrunWeek == 4:  
            self.addCommunitySection()
            
        self.addTimesSection()
        self.addPhotoSection()
    
        return self.getFullRunReportHTML()

    def addSummarySection(self):
        text = self.resultsSystemText
        html = self.getSectionHeading('summary','Summary')
        content = '<ul style="padding-bottom: 0;padding-top: 0;padding-left: 10px;margin-bottom: 0;margin-top: 0;margin-left: 10px">'
        
        # get text until first .
        content += '<li>'+text[:text.find('.')+1]+'</li>'
        
        # get text from third last . (with white space at start trimmed) 
        pos = text.rfind('.')
        pos = text.rfind('.', 0, pos)
        pos = text.rfind('.', 0, pos)
        content += '<li>'+text[pos+1:].strip()+'</li>'
        
        content += '</ul>'
        content += self.templates.summaryThanks       
        html += self.getSectionContent(content) 
        html += self.getSectionSeparator()
        self.runReportHTML += html
    
    def addUpcomingSection(self):
        html = self.getSectionHeading('upcoming','Upcoming')
        content = self.templates.upcomingText;
        html += self.getSectionContent(self.templates.upcomingText)
        html += self.getSectionSeparator()
        self.runReportHTML += html
		
    def addMilestoneSection(self):
        # TODO only Add if there are any milestones
        html = self.getSectionHeading('milestone','Milestones')
        html += self.getPhotoLinks('milestone')
        html += self.getSectionSeparator()
        self.runReportHTML += html
        
    def addVolunteerSection(self):  
        html = self.getSectionHeading('volunteers','Volunteers')
        content = self.templates.volunteerText
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
                
 