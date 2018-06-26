from bs4 import BeautifulSoup
import re
import src.RunReportTemplates as reportTemplates

class RunReport(object):  
    templates = False
    parkrun_name = ''
    parkrun_event_number = ''
    options = {'runner_limit':7, 'volunteer_limit':2, 'pb_limit':2, 'event_limit':8}
    
    results_system_text = ''
    templates = False
    current_event_volunteers = []
    current_event_runners = {}
    photos = []
    
    toc = []
    runCount = []
    
    runners = {}
    volunteers = {}
    
    VOLUNTEER_START_TEXT = 'We are very grateful to the volunteers who made this event happen:'
    PB_TEXT = 'New PB!'  

    def __init__(self, name, event_number):
        self.templates = reportTemplates.StandardTemplate()   
        self.parkrun_name = name
        self.parkrun_event_number = event_number
  
        # make sure these are reset each time you call the init
        self.runners = {}
        self.volunteers = {}

    def set_results_system(self, text):
        text = text.strip()
        if text == '':
            return	
        self.results_system_text = text

    def parse_event_result(self, text, is_current=False):
        text = text.strip()
        if text == '':
            return	
        if is_current:
            self.set_current_event(text)
        self.parse_runners(text)
        self.parse_volunteers(text)
        
    def set_current_event(self, text):
        text = text.strip()
        if text == '':
            return	
        # set currentEventRunners and currentEventVolunteers 
        self.set_current_event_runners(text)
        self.set_current_event_volunteers(text)
            
    def parse_current_event(self, text, parseType):
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
            
    def set_current_event_runners(self, text):
        self.current_event_runners = {}
        rows = self.parse_current_event(text, 'runners')
        for row in rows:
            details = self.get_runner_details(row.find_all("td"))
            if details:
                self.current_event_runners[details['id']] = {"name":details['name'], "time":details['time'], "age_group":details['age_group']}
                
    def set_current_event_volunteers(self, text):
        self.current_event_volunteers = []
        names = self.parse_current_event(text, 'volunteers')
        for n in names:
            self.current_event_volunteers.append(n)
        
    def add_toc(self, anchor, heading):
        # Add to toc
        self.toc.append('<li><a href="#'+anchor+'">'+heading+'</a></li>')      
        
    def get_section_heading(self, anchor, heading):
        self.add_toc(anchor, heading)
        return self.templates.sectionHeadingTemplate.format(anchor, heading)    
    
    def get_section_content(self, content):
        return self.templates.sectionContentTemplate.format(content)    
    
    def get_section_separator(self):
        return self.templates.separator    
    
    def get_current_event_volunteer_html(self):
        html = '<ul style="padding-bottom: 0;padding-top: 0;padding-left: 10px;margin-bottom: 0;margin-top: 0;margin-left: 10px">'
        for vol in self.current_event_volunteers:
            html += '<li>'+vol+'</li>'
        html += '</ul>'
        return html    
           
    def get_runner_details(self, cells):
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
            age_group = cells[3].get_text()
            position = cells[0].get_text()
            pb = 0
            if cells[8].get_text() == self.PB_TEXT:
                pb = 1

            return {"id":id,"name":name,"time":time,"pb":pb,"age_group":age_group,"position":position}
        else:
            return False  
        
    def parse_runners(self, text):
        text = text.strip()
        if text == '':
            return	
        rows = self.parse_current_event(text, 'runners')
        event_count = 0
        for row in rows:
            cells = row.find_all("td")
            details = self.get_runner_details(cells)
            if details:
                event_count = event_count + 1
                pb_count = 0
                if details['id'] in self.runners:
                    count = self.runners[details['id']]['count'] + 1
                    if details['pb'] == 1:
                        pb_count = self.runners[details['id']]['pb_count'] + 1
                    else:
                        pb_count = self.runners[details['id']]['pb_count']
                else:
                    count = 1
                    if details['pb'] == 1:
                         pb_count = 1
                
                self.runners[details['id']] = {"name":details['name'],"pb_count":pb_count,"count":count}
        self.runCount.append(event_count);
        
    def parse_volunteers(self, text):
        text = text.strip()
        if text == '':
            return	
        names = self.parse_current_event(text, 'volunteers')
        
        for n in names:
            if n in self.volunteers:
                count = self.volunteers[n] + 1
            else:
                count = 1
            self.volunteers[n] = count            
            
    def add_photo(self, text, size, photo_type, title=''):
        text = text.strip()
        if text == '':
            return	
        start_pos = text.find('[img]') + len('[img]')
        end_pos = text.find('.jpg') + len('.jpg')
        flickr_link = text[start_pos:end_pos]
        
        self.photos.append({'link':flickr_link,'size':size,'type':photo_type, 'title':title})
     
    def get_photo_links(self, photo_type):
        html = ''
        picture_width = 620
        for p in self.photos:
            if p['type'] == photo_type:
                dims = p['size']
                title = p['title']
                curr_width = int(dims[0])
                curr_height = int(dims[1])
                if curr_width >= curr_height:
                    dims[0] = picture_width
                    dims[1] = (picture_width * curr_height) // curr_width
                elif curr_height > curr_width:
                    # get two pictures on one row
                    dims[0] = picture_width // 2 - 5
                    dims[1] = ((picture_width / 2 - 5) * curr_height) // curr_width
                html += self.templates.photoTemplate.format(p['link'],p['type'],dims[0],dims[1],title)
                # TODO add &nbsp; if odd count
        
        return html       
        
    def get_aesthetic_times(self):
        html = ''
        for key, data in self.current_event_runners.items():
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
        
        html = self.get_section_content(html)
        return html 

    def get_table_header_cell_template(self, width, header, colspan=1):
        return self.templates.tableHeaderCellTemplate.format(width, colspan, header)
        
    def get_summary_table_html(self, headers, selected_list):
        width = 100 // len(headers)
     
        html = self.templates.tableStart 
        html += '<tr>'      
        for header in headers:
            html += self.get_table_header_cell_template(width, header, 2)
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
        
    def get_pb_summary(self, pbLimit=2):
        events = len(self.runCount)

        selected = {k:v for k,v in self.runners.items() if v['pb_count'] >= pbLimit}
        selected_list = sorted(selected.items(), key=lambda x: x[1]['name'])

        headers = []
        headers.append(self.templates.tableHeaderCellSummaryTemplate.format('PBs', pbLimit, events))

        html = self.get_summary_table_html(headers, selected_list)       

        return html	
        
    def calc_age_groups(self):
        runners = self.current_event_runners
        age_group = {}
        for l, v in runners.items():
            age = v['age_group']
            age_number = age[2:]
            if age[0:2] == 'SM' or age[0:2] == 'VM':
                if age_number not in age_group:
                    age_group[age_number] = {'menName':'','menTime':'','womenName':'','womenTime':''}
                if age_group[age_number]['menName'] == '':
                    age_group[age_number]['menName'] = v['name']
                    age_group[age_number]['menTime'] = v['time']
            elif age[0:2] == 'SW' or age[0:2] == 'VW':
                if age_number not in age_group:
                    age_group[age_number] = {'menName':'','menTime':'','womenName':'','womenTime':''}
                if age_group[age_number]['womenName'] == '':
                    age_group[age_number]['womenName'] = v['name']
                    age_group[age_number]['womenTime'] = v['time']
        sorted_age = sorted(age_group.items(), key=lambda x: x[0])
        return sorted_age
        
    def get_age_group_finisher(self):
        list = self.calc_age_groups()
        html = self.templates.tableStart
        html += '<tr>'
        html += self.get_table_header_cell_template(20, 'Age Group')
        html += self.get_table_header_cell_template(40, 'Men', 2)
        html += self.get_table_header_cell_template(40, 'Women', 2)
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
        
    def get_regular_summary(self, runner_limit, volunteer_limit):
        events = len(self.runCount)
        regular_runners = {k:v for k,v in self.runners.items() if v['count'] >= runner_limit}
        runners_list = sorted(regular_runners.items(), key=lambda x: x[1]['name'])
        
        regular_volunteer = {k:v for k,v in self.volunteers.items() if v >= volunteer_limit}
        volunteer_list = sorted(regular_volunteer.items(), key=lambda x: x[0])
                 
        headers = [
        self.templates.tableHeaderCellSummaryTemplate.format('Runners', runner_limit, events),
        self.templates.tableHeaderCellSummaryTemplate.format('Volunteers', volunteer_limit, events)
        ]
        width = 100 / len(headers)
         
        html = self.templates.tableStart
        html += self.templates.tableHeader.format(runner_limit, events, volunteer_limit, events)
        html += '<tr>'      
        for header in headers:
            html += self.get_table_header_cell_template(width, header)
        html += '</tr>'
        
        # work out a better way of transposing two arrays of diff lengths
        rows = {} 
        
        count = 1
        for l,v in runners_list:
            rows[count] = []
            rows[count].append(self.templates.tableCell.format(v['name']))
            count = count + 1
          
        count = 1
        for key,value in volunteer_list:
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
        
        return html


class RunReportWeek(RunReport):
    
    parkrun_week = 1
    run_report_html = ''
    
    def __init__(self, name, event_number, week, options):
        RunReport.__init__(self, name, event_number)
        self.parkrun_week = week
        # merge options
        self.options = {**self.options, **options}
        
        self.print_urls()
        
    def print_urls(self):
        links = []
        event_number = str(self.parkrun_event_number);
        links.append('tag: ' + self.parkrun_name + '_parkrun_' + event_number)
        links.append('tag: ' + self.parkrun_name)
        links.append('tag: parkrun')
        links.append('https://www.flickr.com/groups_pool_add.gne?path=' + self.parkrun_name + '-parkrun')
        links.append('https://www.flickr.com/groups/' + self.parkrun_name + '-parkrun/')
        links.append('http://www.parkrun.com.au/' + self.parkrun_name + '/results/weeklyresults/?runSeqNumber=' + event_number)
        
        if self.parkrun_week == 2 or self.parkrun_week == 3:
             for i in range(1, self.options['event_number']):
                event_number = str(self.parkrun_event_number - i)
                links.append('http://www.parkrun.com.au/' + self.parkrun_name + '/results/weeklyresults/?runSeqNumber=' + event_number)
          
        # TODO display as html  
        print('Links to use in the below sections')
        print("\n".join(links))

    def create_week(self, week=False, options=False):
        self.add_summary_section()
        self.add_upcoming_section()
        self.add_volunteer_section()
        self.add_milestone_section()
        
        # allow override of week and options since week and options in class init are only used for link creation.
        if week is not False:
            self.parkrun_week = week
            
        # merge options
        if options is not False:
            self.options = {**self.options, **options}
        
        if self.parkrun_week == 1:
            self.add_age_group_section()
        elif self.parkrun_week == 2:
            self.add_regular_section(self.options['runner_limit'], self.options['volunteer_limit'])
        elif self.parkrun_week == 3:
            self.add_week_pb_section(self.options['pb_limit'])
        elif self.parkrun_week == 4:
            self.add_community_section()
            
        self.add_times_section()
        self.add_photo_section()
    
        return self.get_full_run_report_html()

    def add_summary_section(self):
        text = self.results_system_text
        html = self.get_section_heading('summary', 'Summary')
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
        html += self.get_section_content(content)
        html += self.get_section_separator()
        self.run_report_html += html
    
    def add_upcoming_section(self):
        html = self.get_section_heading('upcoming', 'Upcoming')
        content = self.templates.upcomingText;
        html += self.get_section_content(self.templates.upcomingText)
        html += self.get_section_separator()
        self.run_report_html += html

    def add_milestone_section(self):
        # TODO only Add if there are any milestones
        html = self.get_section_heading('milestone', 'Milestones')
        html += self.get_photo_links('milestone')
        html += self.get_section_separator()
        self.run_report_html += html
        
    def add_volunteer_section(self):
        html = self.get_section_heading('volunteers', 'Volunteers')
        content = self.templates.volunteerText
        content += self.get_current_event_volunteer_html()
        html += self.get_section_content(content)
        html += self.get_photo_links('volunteer')
        html += self.get_section_separator()
        self.run_report_html += html
    
    def add_age_group_section(self):
        html = self.get_section_heading('age_group', 'Age Group First Finishers')
        html += self.get_age_group_finisher()
        self.run_report_html += html
        
    def add_regular_section(self, runner_limit=7, volunteer_limit=2):
        html = self.get_section_heading('regular', 'Regular Runners / Volunteers')
        html += self.get_regular_summary(runner_limit, volunteer_limit)
        self.run_report_html += html
        
    def add_week_pb_section(self, pbLimit=2):
        html = self.get_section_heading('pbs', 'Regular PBs')
        html += self.get_pb_summary(pbLimit)
        self.run_report_html += html
            
    def add_community_section(self):
        html = self.get_section_heading('fun', 'Having Fun')
        self.run_report_html += html
        
    def add_times_section(self):
        html = self.get_section_heading('times', 'Aesthetically pleasing times')
        html += self.get_aesthetic_times()
        html += self.get_section_separator()
        self.run_report_html += html
            
    def add_photo_section(self):
        html = self.get_section_heading('photos', 'Photos')
        html += self.get_photo_links('photo')
        self.run_report_html += html
        
    def get_run_report_header(self):
        return '<h1 style="padding: 0;margin: 0">Run Report</h1>'
        
    def get_run_report_toc(self):
        html = '<ul>'
        for toc in self.toc:
           html += toc
        html += '</ul>'
        
        return html    
        
    def get_full_run_report_html(self):
        html = self.get_run_report_header()
        html += self.get_run_report_toc()
        html += self.run_report_html
        
        return html
                
 