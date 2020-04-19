import urllib.request
from urllib.parse import unquote
import re
from html.parser import HTMLParser


def html2text(strText):
    str1 = strText
    int2 = str1.lower().find("<body")
    if int2>0:
       str1 = str1[int2:]
    int2 = str1.lower().find("</body>")
    if int2>0:
       str1 = str1[:int2]
    list1 = ['<br>',  '<tr',  '<td', '</p>', 'span>', 'li>', '</h', 'div>' ]
    list2 = [chr(13), chr(13), chr(9), chr(13), chr(13),  chr(13), chr(13), chr(13)]
    bolFlag1 = True
    bolFlag2 = True
    strReturn = ""
    for int1 in range(len(str1)):
      str2 = str1[int1]
      for int2 in range(len(list1)):
        if str1[int1:int1+len(list1[int2])].lower() == list1[int2]:
           strReturn = strReturn + list2[int2]
      if str1[int1:int1+7].lower() == '<script' or str1[int1:int1+9].lower() == '<noscript':
         bolFlag1 = False
      if str1[int1:int1+6].lower() == '<style':
         bolFlag1 = False
      if str1[int1:int1+7].lower() == '</style':
         bolFlag1 = True
      if str1[int1:int1+9].lower() == '</script>' or str1[int1:int1+11].lower() == '</noscript>':
         bolFlag1 = True
      if str2 == '<':
         bolFlag2 = False
      if bolFlag1 and bolFlag2 and (ord(str2) != 10) :
        strReturn = strReturn + str2
      if str2 == '>':
         bolFlag2 = True
      if bolFlag1 and bolFlag2:
        strReturn = strReturn.replace(chr(32)+chr(13), chr(13))
        strReturn = strReturn.replace(chr(9)+chr(13), chr(13))
        strReturn = strReturn.replace(chr(13)+chr(32), chr(13))
        strReturn = strReturn.replace(chr(13)+chr(9), chr(13))
        strReturn = strReturn.replace(chr(13)+chr(13), chr(13))
    strReturn = strReturn.replace(chr(13), '\n')
    return strReturn

def fetch_article(strURL):
#    with urllib.request.urlopen('http://www.ceskenoviny.cz') as response:
    with urllib.request.urlopen(strURL) as response:
        output=response.read()
        try:
            html = unquote(output.decode('utf8'))
        except:
            html = unquote(output.decode('ISO-8859-2'))
            #html = html.encode('utf-8')
        #html = response.read()

    html=(html2text(str(html)))


    regexp = "&.+?;"
    list_of_html = re.findall(regexp, html) #finds all html entites in page
    for e in list_of_html:
        h = HTMLParser()
        unescaped = h.unescape(e) #finds the unescaped value of the html entity
        html = html.replace(e, unescaped) #replaces html entity with unescaped value

    return(html)


# = "http://www.theguardian.com/world/2014/sep/25/us-air-strikes-islamic-state-oil-isis"
#html = urllib.request.urlopen(url).read()
#print(html2text(html))

