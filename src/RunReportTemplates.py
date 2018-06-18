class StandardTemplate:

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

    tableHeaderCellTemplate =  '<th style="width: {}%; text-align: center; border: 1px solid #ccc !important;" colspan="{}">{}</th>'

    tableHeaderCellSummaryTemplate = '{} ({} or more from last {} events)'

    tableCell = '''<td style="padding-left: 10px; border-width: 0 0 1px 0 !important; border-style: solid  !important; border-color: #ccc !important;">
{}</td>
'''
    
    photoTemplate = '<img src="{}" alt="{}" width="{}" height="{}" />{}'
    
    tableEnd = '</tbody></table>' 
    
    summaryThanks = 'Thanks to everyone for their participation and we hope to see everyone again next week. Remember to tell your friends parkrun is fun for everyone, it’s the taking part that counts.'
	
    volunteerText = '''
Jells parkrun relies on volunteers to bring you a free, timed event each week. We encourage everyone to volunteer because it's fun, rewarding, and giving to your community. 
Please review the <a href="https://www.parkrun.com.au/jells/volunteer/futureroster/">Future Roster</a> to see where volunteers are needed and email <a href="mailto:jellshelpers@parkrun.com">jellshelpers@parkrun.com</a> 
if you can help. The wonderful volunteers who made this event possible are:
'''

    # TODO move to text input in notebook ?
    upcomingText = '''
<div style="padding: 0px;width: 50%;margin-left: auto;margin-right: auto">
<img src="https://farm1.staticflickr.com/1741/41551984125_2039b19528_z.jpg" alt="runners" width="310" height="148" /></div>
<div>Please Note: Our anniversary is coming up on 23 June and Jells parkrun is turning <b>3</b>. We'll be having a pyjama run. Run in your pjs, dressing gown, bring your teddy bear along. And there will be cake!
<a href="https://www.facebook.com/events/1962473370464471/">Link to Facebook event</a></div>
'''   