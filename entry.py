import datetime
import logging
import json

from google.appengine.ext import ndb
import webapp2

def parse_timestamp(raw):
    return datetime.datetime.fromtimestamp(int(raw))

def format_timestamp(dtime):
    return dtime.strftime('%s')
    
class LogEntry(ndb.Model):
    log_id = ndb.StringProperty()
    entry_timestamp = ndb.DateTimeProperty(auto_now_add=True)
    client_name = ndb.StringProperty()
    client_timestamp = ndb.DateTimeProperty()  # stored to monitor synchronization times
    message = ndb.TextProperty()

class Appender(webapp2.RequestHandler):
    def post(self):
        # TODO validate write permissions
        try:
            entry = LogEntry(
                log_id=self.request.get('log_id'),
                client_name=self.request.get('client_name', 'default'),
                client_timestamp=parse_timestamp(self.request.get('client_timestamp')),
                message=self.request.get('message'))
            entry.put()
        except Exception as e:
            logging.error(e)
            self.response.write(json.dumps({'status': 'error'}))
            return
            
        self.response.write(json.dumps({'status': 'OK'}))

class Tailer(webapp2.RequestHandler):
    def get(self):
        entries_query = LogEntry.query(
            LogEntry.log_id == self.request.get('log_id'),
            LogEntry.entry_timestamp >= parse_timestamp(self.request.get('since')))

        max_results = int(self.request.get('max_results', '64'))
        entries = entries_query.fetch(max_results)

        def write(l, m):
            self.response.write(l + ":" + unicode(m) + "\n")

        results = []        
        for entry in entries:
            results.append({
                "id": entry.key.id(),
                "tstamp": format_timestamp(entry.entry_timestamp),
                "message": entry.message,
            })
            
            
        self.response.write(json.dumps({
            'status': 'OK',
            'entries': results
        }))

app = webapp2.WSGIApplication([
    ('/append', Appender),
    ('/tail', Tailer)
    ], debug=True)
