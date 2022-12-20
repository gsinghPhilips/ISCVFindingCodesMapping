from wsgiref import headers
from quickumls import QuickUMLS

import pandas as pd
import requests

df = pd.read_csv('inputdata/FullList_FC.csv')

accepted_sem= {'T020', 'T190', 'T038','T120','T185','T201','T019','T060','T047','T033','T059','T044','T046','T121'}

matcher1 = QuickUMLS(quickumls_fp = 'umls_data', overlapping_criteria = 'length', threshold = 0.98,similarity_name = 'cosine', window = 10, accepted_semtypes=accepted_sem)
matcher2 = QuickUMLS(quickumls_fp = 'umls_data', overlapping_criteria = 'length', threshold = 0.95,similarity_name = 'cosine', window = 5)

headers={
'Content-Type':'application/json',
'Accept':'application/json',
'X-API-KEY':'1A67C7B0-EE63-4DAB-9B15-B77C56BBB016'
}

umlsWebServiceUrl='http://unifiedcoding.htce.nl.philips.com:8101'

searchAtomsBySearchContextUrl = umlsWebServiceUrl + '/api/Umls/SearchAtomsBySearchContext'
searchConceptsBySearchContextUrl = umlsWebServiceUrl + '/api/Umls/SearchConceptsBySearchContext'

AnnotatedCUI_code=[]
AnnotatedTerm_code=[]
AnnotatedCUI_group=[]
AnnotatedTerm_group=[]


for index,row in df.iterrows():
    try:
        result1 = matcher1.match(row[3], best_match=True, ignore_syntax=False) #text = input free text/string 
        cui = result1[0][0]["cui"]
        term = result1[0][0]["term"]
        AnnotatedTerm_code.append(term)
        AnnotatedCUI_code.append(cui)
                    
    except:
        AnnotatedTerm_code.append("No match")
        AnnotatedCUI_code.append("No match")
        #print("No match")

    try: 
        result = matcher2.match(row[5], best_match=True, ignore_syntax=False) #text = input free text/string 
        cui2 = result[0][0]["cui"]
        term2 = result[0][0]["term"]
        AnnotatedTerm_group.append(term2)
        AnnotatedCUI_group.append(cui2)
    except:
        AnnotatedTerm_group.append("No match")
        AnnotatedCUI_group.append("No match")
        #print("No match")

AnotatatedSnomedCTID_code=[]
AnotatatedSnomedCTID_group=[]

print(AnnotatedCUI_code)

print(AnnotatedTerm_code)


for c in AnnotatedCUI_code:
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
            AnotatatedSnomedCTID_code.append(searchSnomedResponse[0]["code"])
        except:
            AnotatatedSnomedCTID_code.append("No match")   
    else:
        AnotatatedSnomedCTID_code.append("No match")

print(AnotatatedSnomedCTID_code)


for c in AnnotatedCUI_group:
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
            AnotatatedSnomedCTID_group.append(searchSnomedResponse[0]["code"])
        except:
            AnotatatedSnomedCTID_group.append("No match")   
    else:
        AnotatatedSnomedCTID_group.append("No match")

print(AnotatatedSnomedCTID_group)



df['mappedCUI_code']=AnnotatedCUI_code
df['mappedTerm_label_code']=AnnotatedTerm_code
df['mappedsnomedID_code']=AnotatatedSnomedCTID_code
df['mappedCUI_group']=AnnotatedCUI_code
df['mappedTerm_label_group']=AnnotatedTerm_code
df['mappedsnomedID_group']=AnotatatedSnomedCTID_code



df.to_csv('outputdata/output_FullList_FCwithFG.csv', index=False)

