from wsgiref import headers
from quickumls import QuickUMLS

import pandas as pd
import requests

df = pd.read_csv('inputdata/FullList_FC.csv')

qualifier_sem= {'T185','T080'}

matcher1 = QuickUMLS(quickumls_fp = 'umls_data', overlapping_criteria = 'length', threshold = 0.98,similarity_name = 'cosine', window = 10, accepted_semtypes=qualifier_sem)

headers={
'Content-Type':'application/json',
'Accept':'application/json',
'X-API-KEY':'1A67C7B0-EE63-4DAB-9B15-B77C56BBB016'
}

umlsWebServiceUrl='http://unifiedcoding.htce.nl.philips.com:8101'

searchAtomsBySearchContextUrl = umlsWebServiceUrl + '/api/Umls/SearchAtomsBySearchContext'
searchConceptsBySearchContextUrl = umlsWebServiceUrl + '/api/Umls/SearchConceptsBySearchContext'

AnnotatedCUI=[]
AnnotatedTerm=[]


for index,row in df.iterrows():
    try:
        result = matcher1.match(row[3], best_match=True, ignore_syntax=False) #text = input free text/string 
        cui = result[0][0]["cui"]
        term = result[0][0]["term"]
        AnnotatedTerm.append(term)
        AnnotatedCUI.append(cui)
                    
    except:
        AnnotatedTerm.append("No match")
        AnnotatedCUI.append("No match")
        #print("No match")

AnotatatedSnomedCTID=[]

print(AnnotatedCUI)

print(AnnotatedTerm)


for c in AnnotatedCUI:
    if c != "No match":
        searchContext = {
            'Cui':c,
            'Vocabularies':['SNOMEDCT_US'],
            'MaxResults':1,
            'ispref':'Y'
             }
        try:
            response=requests.get(url=searchAtomsBySearchContextUrl, headers=headers, json=searchContext)
            searchSnomedResponse=response.json()
            AnotatatedSnomedCTID.append(searchSnomedResponse[0]["code"])
        except:
            AnotatatedSnomedCTID.append("No match")   
    else:
        AnotatatedSnomedCTID.append("No match")

print(AnotatatedSnomedCTID)

df['mappedCUI']=AnnotatedCUI
df['mappedTerm_label']=AnnotatedTerm
df['mappedsnomedID']=AnotatatedSnomedCTID

df.to_csv('outputdata/output_FullList_Qualifier.csv', index=False)

