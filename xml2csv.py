from xml.sax import handler, make_parser
from ordereddict import OrderedDict
import itertools

and_reduce = lambda vec: reduce(lambda x,y: x and y,vec,True)

class CsvHandler(handler.ContentHandler):
  def __init__(self,main_tag,tags,out_fid,header=True,deps={}):
    self.main_tag = main_tag
    self.store = tags
    self.tags = list(set(tags+list(itertools.chain(*deps.values()))))
    self.deps = deps
    self.out_fid = out_fid
    self.header = header

    self.in_flags_0 = OrderedDict(zip(self.tags,len(self.tags)*[False]))
    self.content_0 = OrderedDict(zip(self.store,len(self.store)*['']))

  def startDocument(self):
    self.num_recs = 0
    self.last_tag = None

    if self.header:
      self.out_fid.write(','.join(self.content_0)+'\n')

  def endDocument(self):
    pass

  def startElement(self, name, attrs):
    if name == self.main_tag:
      self.in_flags = self.in_flags_0.copy()
      self.content = self.content_0.copy()

    if name in self.tags:
      if and_reduce([self.in_flags[nm] for nm in self.deps.get(name,[])]):
        self.in_flags[name] = True
        if name in self.store:
	   self.last_tag = name
	   self.content[name] = ''
    else:
      self.last_tag = None

  def endElement(self, name):
    self.last_tag = None
    if name == self.main_tag:
      self.num_recs += 1
      self.writeRecord()
    elif name in self.tags:
      self.in_flags[name] = False

  def characters(self, content):
    if self.last_tag:
      self.content[self.last_tag] += content

  def writeRecord(self):
    self.out_fid.write('\"'+'\",\"'.join(self.content.values())+'\"\n')

def xml_to_csv(main_tag,tags,in_fname,out_fname,header=True,deps={}):
  out_fid = open(out_fname,'w+')

  parser = make_parser()
  csv_handler = CsvHandler(main_tag,tags,out_fid,header=header,deps=deps)
  parser.setContentHandler(csv_handler)
  parser.parse(in_fname)

  return csv_handler.num_recs

