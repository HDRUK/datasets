#### START DEFINE MAPPING v1 --> v2 ####
def map_identifier(dm_v1, dm_v2):
    dm_id = dm_v1.get('id', None)
    if dm_id:
        dm_v2['identifier'] = f"https://web.www.healthdatagateway.org/dataset/{dm_id}"

def map_schema(dm_v1, dm_v2):
    dm_v2['@schema'] = {
        'type': "Dataset",
        'version': '2.0.0',
        'url': "https://raw.githubusercontent.com/HDRUK/schemata/develop/schema/dataset/latest/dataset.schema.json"
    }

def map_version(dm_v1, dm_v2):
    dm_version = dm_v1.get('documentationVersion', None)
    dm_v2['version'] = dm_version


def mapl_revisions(dm_v1, dm_v2):
    dm_revisions = dm_v1.get('revisions', [])
    if dm_revisions:
        dm_v2['revisions'] = []
        for k,v in dm_revisions.items():
            if 'latest'==k:
                continue
            dm_v2['revisions'].append({'version': k,
                                       'url': f"https://web.www.healthdatagateway.org/dataset/{v}"})
    #[{'revisions_version':'revisions_version', 'revisions_url':'revisions_url'}]


def map_issued(dm_v1, dm_v2):
    dm_issued = dm_v1.get('issued', None)
    dm_v2['issued'] = dm_issued


def map_modified(dm_v1, dm_v2):
    dm_modified = dm_v1.get('modified', None)
    if dm_modified:
        dm_v2['modified'] = dm_modified


def map_summary_title(dm_v1, dm_v2):
    dm_title = dm_v1.get('title', None)
    if not dm_title:
        dm_title = dm_v1.get('label', 'title')
    dm_v2.setdefault("summary", {})['title'] = dm_title


def map_summary_abstract(dm_v1, dm_v2):
    dm_abstract = dm_v1.get('abstract', None)
    dm_v2.setdefault("summary", {})['abstract'] = dm_abstract


def map_summary_publisher_memberOf(dm_v1, dm_v2):
    pub_dict = {'Barts Health NHS Trust': 'ALLIANCE > BARTS',
                'NHS Digital': 'ALLIANCE > NHS Digital',
                'NIHR Health Informatics Collaborative Cardiovascular Theme': 'OTHER > NIHR HIC',
                'NIHR Health Informatics Collaborative Critical Care Theme': 'OTHER > NIHR HIC',
                'NIHR Health Informatics Collaborative Renal Transplantation Theme': 'OTHER > NIHR HIC',
                'NIHR Health Informatics Collaborative Viral Hepatitis Theme': 'OTHER > NIHR HIC',
                'Oxford University Hospitals NHS Foundation Trust': 'ALLIANCE > Oxford',
                'SLaM': 'ALLIANCE > South London and Maudsley',
                'SAIL Databank': 'OTHER > SAIL Databank',
                'HDR UK': 'OTHER > HDR UK'}

    dm_membership = dm_v1.get('publisher', None)
    if dm_membership:
        dm_membership = pub_dict.get(dm_membership, dm_membership)
        publisher = dm_membership.split('>')
        membership = publisher[0].strip()
        if 'HUBS' == membership:
            membership = 'HUB'
        if membership not in ['HUB', 'ALLIANCE', 'OTHER']:
            print(f"ERROR: Member Of: '{dm_membership}'")
        dm_v2.setdefault("summary", {}).setdefault("publisher", {})['memberOf'] = membership  #'summary_publisher_memberOf'


def map_summary_publisher_accessRights(dm_v1, dm_v2):
    dm_accessRights = dm_v1.get('accessRights', 'In Progress')
    dm_v2.setdefault("summary", {}).setdefault("publisher", {})['accessRights'] = dm_accessRights


def map_summary_publisher_deliveryLeadTime(dm_v1, dm_v2):
    dm_deliveryLeadTime = dm_v1.get('accessRequestDuration', 'OTHER')
    dm_deliveryLeadTime = dm_deliveryLeadTime.upper()
    if ('LESS 1 WEEK'==dm_deliveryLeadTime
       or 'INSTANT ACCESS'==dm_deliveryLeadTime[:14]):
        dm_deliveryLeadTime='LESS 1 WEEK'
    elif '1-2 WEEKS'==dm_deliveryLeadTime:
        dm_deliveryLeadTime='1-2 WEEKS'
    elif ('2-4 WEEKS'==dm_deliveryLeadTime
         or '>1 WEEK'==dm_deliveryLeadTime
         or '2 WEEKS'==dm_deliveryLeadTime[:7]):
        dm_deliveryLeadTime='2-4 WEEKS'
    elif ('1-2 MONTHS'==dm_deliveryLeadTime
         or '4 - 6 WEEKS'==dm_deliveryLeadTime
         or '4-6 WEEKS'==dm_deliveryLeadTime
         or '48 DAYS'==dm_deliveryLeadTime[:8]):
        dm_deliveryLeadTime='1-2 MONTHS'
    elif (  '2-6 MONTHS'==dm_deliveryLeadTime
         or '2-3 MONTHS'==dm_deliveryLeadTime
         or '~ 3 MONTHS.'==dm_deliveryLeadTime[-11:]
         or '16 WEEKS'==dm_deliveryLeadTime[:9]
         or '3-6 MONTHS'==dm_deliveryLeadTime):
        dm_deliveryLeadTime='2-6 MONTHS'
    elif ('MORE 6 MONTHS'==dm_deliveryLeadTime
         or '~6-12 MONTHS'==dm_deliveryLeadTime):
        dm_deliveryLeadTime='MORE 6 MONTHS'
    elif ('VARIABLE'==dm_deliveryLeadTime
         or 'SUBJECT TO NEGOTIATION'==dm_deliveryLeadTime):
        dm_deliveryLeadTime='VARIABLE'
    elif 'NOT APPLICABLE'==dm_deliveryLeadTime:
        dm_deliveryLeadTime='NOT APPLICABLE'
    elif 'OTHER'==dm_deliveryLeadTime:
        dm_deliveryLeadTime='OTHER'
    dm_v2.setdefault("summary", {}).setdefault("publisher", {})['deliveryLeadTime'] = dm_deliveryLeadTime


def map_summary_publisher_dataUseLimitation(dm_v1, dm_v2):
    #dm_v2["summary"]["publisher"]['dataUseLimitation'] = ['summary_publisher_dataUseLimitation']
    pass


def map_summary_publisher_dataUseRequirements(dm_v1, dm_v2):
    #dm_v2["summary"]["publisher"]['dataUseRequirements'] = ['summary_publisher_dataUseRequirements']
    pass


def map_summary_publisher_accessService(dm_v1, dm_v2):
    #dm_v2["summary"]["publisher"]['accessService'] = ['summary_publisher_accessService']
    pass


def map_summary_publisher_name(dm_v1, dm_v2):
    pub_dict = {'Barts Health NHS Trust': 'ALLIANCE > BARTS',
                'NHS Digital': 'ALLIANCE > NHS Digital',
                'NIHR Health Informatics Collaborative Cardiovascular Theme': 'OTHER > NIHR HIC',
                'NIHR Health Informatics Collaborative Critical Care Theme': 'OTHER > NIHR HIC',
                'NIHR Health Informatics Collaborative Renal Transplantation Theme': 'OTHER > NIHR HIC',
                'NIHR Health Informatics Collaborative Viral Hepatitis Theme': 'OTHER > NIHR HIC',
                'Oxford University Hospitals NHS Foundation Trust': 'ALLIANCE > Oxford',
                'SLaM': 'ALLIANCE > South London and Maudsley',
                'SAIL Databank': 'OTHER > SAIL Databank',
                'HDR UK': 'OTHER > HDR UK'}
    
    dm_publisher = dm_v1.get('publisher', None)
    dm_publisher = pub_dict.get(dm_publisher, dm_publisher)
    publisher = dm_publisher.split('>')
    publisher = publisher[1].strip()
    dm_v2.setdefault("summary", {}).setdefault("publisher", {})['name'] = publisher


def map_summary_publisher_logo(dm_v1, dm_v2):
    #dm_v2["summary"]["publisher"]['logo'] = 'https://images.app.goo.gl/MXpLA4Dku7dZe8PL6'
    pass


def map_summary_publisher_description(dm_v1, dm_v2):
    if False:
        dm_publisher = dm_v1.get('creator', None)
        dm_v2.setdefault("summary", {}).setdefault("publisher", {})['description'] = dm_publisher


def map_summary_publisher_contactPoint(dm_v1, dm_v2):
    dm_contactPoint = dm_v1.get('contactPoint', None)
    dm_v2.setdefault("summary", {}).setdefault("publisher", {})['contactPoint'] = dm_contactPoint


def map_summary_contactPoint(dm_v1, dm_v2):
    dm_contactPoint = dm_v1.get('contactPoint', None)
    dm_v2.setdefault("summary", {})['contactPoint'] = dm_contactPoint


def mapl_summary_keywords(dm_v1, dm_v2):
    dm_keywords = dm_v1.get('keywords', '')
    dm_v2["summary"]["keywords"] = []
    if dm_keywords:
        keywords = dm_keywords.split(',')
        unique_keywords = set()
        for kw in keywords:
            kw = kw.lstrip()
            unique_keywords.add(kw)

        dm_v2.setdefault("summary", {})["keywords"] = list(unique_keywords)


def map_summary_alternateIdentifiers(dm_v1, dm_v2):
    #dm_v2["summary"]['alternateIdentifiers'] = ['summary_alternateIdentifiers']
    pass


def map_summary_doiName(dm_v1, dm_v2):
    dm_doi = dm_v1.get('doi', None)
    if dm_doi:
        dm_doi = dm_doi.lower()
        if 'https://doi.org/'==dm_doi[:16]:
            dm_doi = dm_doi[16:]
        elif 'doi:'==dm_doi[:4]:
            dm_doi = dm_doi[4:]
        dm_doi = dm_doi.lstrip()
    dm_v2.setdefault("summary", {})['doiName'] = dm_doi


def map_documentation_description(dm_v1, dm_v2):
    dm_description = dm_v1.get('description', None)
    dm_v2.setdefault("documentation", {})['description'] = dm_description


def mapl_documentation_associatedMedia(dm_v1, dm_v2):
    # dm_v2["documentation"]["associatedMedia"] = ['documentation_associatedMedia']
    pass


def mapl_documentation_isPartOf(dm_v1, dm_v2):
    dm_isPartOf = dm_v1.get('group', 'NOT APPLICABLE')
    dm_v2.setdefault("documentation", {})["isPartOf"] = [dm_isPartOf]


def map_coverage_spatial(dm_v1, dm_v2):
    dm_spatial = dm_v1.get('geographicCoverage', None)
    dm_v2.setdefault("coverage", {})['spatial'] = dm_spatial


def map_coverage_typicalAgeRange(dm_v1, dm_v2):
    dm_ageRange = dm_v1.get('ageBand', None)
    dm_v2.setdefault("coverage", {})['typicalAgeRange'] = dm_ageRange


def mapl_coverage_physicalSampleAvailability(dm_v1, dm_v2):
    dm_physicalSamples = dm_v1.get('physicalSampleAvailability', None)
    dm_v2.setdefault("coverage", {})["physicalSampleAvailability"] = []
    if dm_physicalSamples:
        dm_physicalSamples = dm_physicalSamples.replace(';', ',')
        dm_physicalSamples = dm_physicalSamples.upper()
        physicalSamples = dm_physicalSamples.split(',')
        for p in physicalSamples:
            dm_v2.setdefault("coverage", {})["physicalSampleAvailability"].append(p.lstrip())


def map_coverage_followup(dm_v1, dm_v2):
    dm_v2.setdefault("coverage", {})['followup'] = 'UNKNOWN'


def mapl_coverage_pathway(dm_v1, dm_v2):
    #dm_v2["coverage"]["pathway"] = 'Please indicate if the dataset is representative of the patient pathway and any limitations the dataset may have with respect to pathway coverage.'
    dm_v2.setdefault("coverage", {})["pathway"] = None


def mapl_provenance_origin_purpose(dm_v1, dm_v2):
    dm_v2.setdefault("provenance", {}).setdefault("origin", {})["purpose"] = [] #['Please indicate the purpose(s) that the dataset was collected']


def mapl_provenance_origin_source(dm_v1, dm_v2):
    dm_v2.setdefault("provenance", {}).setdefault("origin", {})["source"] = [] #['Please indicate the source of the data extraction.']


def mapl_provenance_origin_collectionSituation(dm_v1, dm_v2):
    dm_v2.setdefault("provenance", {}).setdefault("origin", {})["collectionSituation"] = [] #['Please indicate the setting(s) where data was collected. Multiple settings may be provided.']


def map_provenance_temporal_accrualPeriodicity(dm_v1, dm_v2):
    dm_periodicity = dm_v1.get('periodicity', 'OTHER')
    dm_periodicity = dm_periodicity.upper()

    if ('ANNUAL' == dm_periodicity[:6]
        or 'UPDATED ANNUALLY' == dm_periodicity
        or 'A NEW DATASET IS ADDED APPROXIMATELY ANNUALLY' == dm_periodicity):
        dm_periodicity = 'ANNUAL'
    elif 'BIANNUAL' == dm_periodicity[:8]:
        dm_periodicity = 'BIANNUAL'
    elif 'BIENNIAL' == dm_periodicity:
        dm_periodicity = 'BIENNIAL'
    elif 'BIMONTHLY' == dm_periodicity:
        dm_periodicity = 'BIMONTHLY'
    elif 'BIWEEKLY' == dm_periodicity:
        dm_periodicity = 'BIWEEKLY'
    elif ('CONTINUOUS' == dm_periodicity
         or 'DATA IS UPDATED HOURLY' == dm_periodicity):
        dm_periodicity = 'CONTINUOUS'
    elif 'DAILY' == dm_periodicity:
        dm_periodicity = 'DAILY'
    elif 'IRREGULAR' == dm_periodicity:
        dm_periodicity = 'IRREGULAR'
    elif ('MONTHLY' == dm_periodicity
         or '1 MONTH CYCLE' == dm_periodicity
         or 'PROVISIONAL DATA: MONTHLY' == dm_periodicity):
        dm_periodicity = 'MONTHLY'
    elif 'OTHER' == dm_periodicity:
        dm_periodicity = 'OTHER'
    elif ('QUARTERLY' == dm_periodicity[:9]
         or 'PROVISIONAL DATA: QUARTERLY' == dm_periodicity
         or 'GENOMICS ENGLAND DATASET ARE UPDATED ON A QUARTERLY BASIS.' == dm_periodicity
         or 'GENOMICS ENGLAND DATASET ARE UPDATED ON A QUARTERLY BASIS' == dm_periodicity):
        dm_periodicity = 'QUARTERLY'
    elif ('SEMIWEEKLY' == dm_periodicity
         or 'TWICE WEEKLY' == dm_periodicity
         or 'TWICE A WEEK (APPROXIMATELY)' == dm_periodicity):
        dm_periodicity = 'SEMIWEEKLY'
    elif ('STATIC' == dm_periodicity
         or 'NA (SINGLE RELEASE)' == dm_periodicity
         or 'SINGLE EXTRACT' == dm_periodicity
         or 'NOT APPLICABLE (SINGLE RELEASE)' == dm_periodicity):
        dm_periodicity = 'STATIC'
    elif ('WEEKLY' == dm_periodicity
         or 'UPDATED AT LEAST WEEKLY' == dm_periodicity):
        dm_periodicity = 'WEEKLY'

    dm_v2.setdefault("provenance", {}).setdefault("temporal", {})['accrualPeriodicity'] = dm_periodicity


def map_provenance_temporal_distributionReleaseDate(dm_v1, dm_v2):
    dm_releaseDate = dm_v1.get('releaseDate', None)
    dm_v2.setdefault("provenance", {}).setdefault("temporal", {})['distributionReleaseDate'] = dm_releaseDate


def map_provenance_temporal_endDate(dm_v1, dm_v2):
    dm_endDate = dm_v1.get('datasetEndDate', None)
    dm_v2.setdefault("provenance", {}).setdefault("temporal", {})['endDate'] = dm_endDate


def map_provenance_temporal_timeLag(dm_v1, dm_v2):
    #dm_v2.setdefault("provenance", {}).setdefault("temporal", {})['timeLag'] = ['Please indicate the typical time-lag between an event and the data for that event appearing in the dataset"']
    pass


def map_provenance_temporal_startDate(dm_v1, dm_v2):
    dm_startDate = dm_v1.get('datasetStartDate', None)
    dm_v2.setdefault("provenance", {}).setdefault("temporal", {})['startDate'] = dm_startDate


def map_accessibility_access_accessRights(dm_v1, dm_v2):
    dm_accessRights = dm_v1.get('accessRights', None)
    dm_v2.setdefault("accessibility", {}).setdefault("access", {})['accessRights'] = dm_accessRights


def map_accessibility_access_accessService(dm_v1, dm_v2):
    dm_v2.setdefault("accessibility", {}).setdefault("access", {})['accessService'] = None #'Please provide a brief description of the data access environment that is currently available to researchers.'


def map_accessibility_access_deliveryLeadTime(dm_v1, dm_v2):
    dm_accessRequestDuration = dm_v1.get('accessRequestDuration', None)
    if not dm_accessRequestDuration:
        return

    dm_accessRequestDuration = dm_accessRequestDuration.upper()
    if ('1-2 MONTHS' == dm_accessRequestDuration
       or '4-6 WEEKS' == dm_accessRequestDuration
       or '4 - 6 WEEKS' == dm_accessRequestDuration
       or '48 DAYS' == dm_accessRequestDuration[:7]):
        dm_accessRequestDuration = '1-2 MONTHS'
    elif '1-2 WEEKS' == dm_accessRequestDuration:
        dm_accessRequestDuration = '1-2 WEEKS'
    elif ('2-4 WEEKS' == dm_accessRequestDuration
          or '2 WEEKS' == dm_accessRequestDuration[:7]):
        dm_accessRequestDuration = '2-4 WEEKS'
    elif ('2-6 MONTHS' == dm_accessRequestDuration
          or '3-6 MONTHS' == dm_accessRequestDuration
          or '2-3 MONTHS' == dm_accessRequestDuration
          or '16 WEEKS' == dm_accessRequestDuration[:8]):
        dm_accessRequestDuration = '2-6 MONTHS'
    elif ('LESS 1 WEEK' == dm_accessRequestDuration
         or 'INSTANT ACCESS' == dm_accessRequestDuration[:14]
         or 'ACCESS TO FULL GWAS' == dm_accessRequestDuration[:19]):
        dm_accessRequestDuration = 'LESS 1 WEEK'
    elif ('MORE 6 MONTHS' == dm_accessRequestDuration
         or '~6-12 MONTHS' == dm_accessRequestDuration):
        dm_accessRequestDuration = 'MORE 6 MONTHS'
    elif 'NOT APPLICABLE' == dm_accessRequestDuration:
        dm_accessRequestDuration = 'NOT APPLICABLE'
    elif 'OTHER' == dm_accessRequestDuration:
        dm_accessRequestDuration = 'OTHER'
    elif 'VARIABLE' == dm_accessRequestDuration:
        dm_accessRequestDuration = 'VARIABLE'
    dm_v2.setdefault("accessibility", {}).setdefault("access", {})['deliveryLeadTime'] = dm_accessRequestDuration


def mapl_accessibility_access_jurisdiction(dm_v1, dm_v2):
    dm_jurisdiction = dm_v1.get('jurisdiction', None)
    dm_v2.setdefault("accessibility", {}).setdefault("access", {})["jurisdiction"] = [dm_jurisdiction]


def map_accessibility_access_dataController(dm_v1, dm_v2):
    dm_dataController = dm_v1.get('dataController', None)
    dm_v2.setdefault("accessibility", {}).setdefault("access", {})['dataController'] = dm_dataController


def map_accessibility_access_dataProcessor(dm_v1, dm_v2):
    dm_dataProcessor = dm_v1.get('dataProcessor', None)
    dm_v2.setdefault("accessibility", {}).setdefault("access", {})['dataProcessor'] = dm_dataProcessor


def mapl_accessibility_usage_dataUseLimitation(dm_v1, dm_v2):
    dm_v2.setdefault("accessibility", {}).setdefault("usage", {})["dataUseLimitation"] = [] #['Please provide an indication of consent permissions for datasets and/or materials.']


def mapl_accessibility_usage_dataUseRequirements(dm_v1, dm_v2):
    dm_v2.setdefault("accessibility", {}).setdefault("usage", {})["dataUseRequirements"] = [] #['Please indicate if there are any additional conditions set for use of the data.']


def map_accessibility_usage_resourceCreator(dm_v1, dm_v2):
    dm_creator = dm_v1.get('creator', None)
    dm_v2.setdefault("accessibility", {}).setdefault("usage", {})['resourceCreator'] = dm_creator


def mapl_accessibility_usage_investigations(dm_v1, dm_v2):
    dm_v2.setdefault("accessibility", {}).setdefault("usage", {})["investigations"] = ['accessibility_usage_investigations']


def mapl_accessibility_usage_isReferencedBy(dm_v1, dm_v2):
    dm_citations = dm_v1.get('citations', None)
    dm_v2.setdefault("accessibility", {}).setdefault("usage", {})["isReferencedBy"] = []
    if dm_citations:
        dm_citations = dm_citations.replace(';', ',')
        citations = dm_citations.split(',')
        for c in citations:
            citation = c.lstrip()
            if 'https://doi.org/' == citation[:16]:
                citation = citation[16:]
            elif 'doi:' == citation[:4]:
                citation = citation[4:]
            dm_v2.setdefault("accessibility", {}).setdefault("usage", {})["isReferencedBy"].append(citation)


def mapl_accessibility_formatAndStandards_vocabularyEncodingScheme(dm_v1, dm_v2):
    dm_controlledVocabulary = dm_v1.get('controlledVocabulary', None)
    dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["vocabularyEncodingScheme"] = []
    if dm_controlledVocabulary:
        dm_controlledVocabulary = dm_controlledVocabulary.replace(';', ',')
        dm_controlledVocabulary = dm_controlledVocabulary.upper()
        encodingSchemes = dm_controlledVocabulary.split(',')
        for e in encodingSchemes:
            e = e.lstrip()
            if 'AMT' == e:
                e = 'AMT'
            elif 'APC' == e:
                e = 'APC'
            elif 'ATC' == e:
                e = 'ATC'
            elif 'CIEL' == e:
                e = 'CIEL'
            elif 'CPT4' == e:
                e = 'CPT4'
            elif ('DM PLUS D' == e
                  or 'DM+D' == e):
                e = 'DM PLUS D'
            elif 'DPD' == e:
                e = 'DPD'
            elif 'DRG' == e:
                e = 'DRG'
            elif 'HEMONC' == e:
                e = 'HEMONC'
            elif 'HPO' == e:
                e = 'HPO'
            elif ('ICD10' in e
                 or 'ICD-10' in e
                 or 'ICD 10' in e
                 or 'INTERNATIONAL CLASSIFICATION OF DISEASES VERSION 10' in e):
                e = 'ICD10'
            elif 'ICD10CM' == e:
                e = 'ICD10CM'
            elif 'ICD10PCS' == e:
                e = 'ICD10PCS'
            elif ('ICD9' == e
                 or 'ICD-9'==e):
                e = 'ICD9'
            elif 'ICD9CM' == e:
                e = 'ICD9CM'
            elif 'ICDO3' == e:
                e = 'ICDO3'
            elif 'JMDC' == e:
                e = 'JMDC'
            elif 'KCD7' == e:
                e = 'KCD7'
            elif 'LOCAL' == e[:5]:
                e = 'LOCAL'
            elif 'LOINC' == e:
                e = 'LOINC'
            elif 'MULTUM' == e:
                e = 'MULTUM'
            elif 'NAACCR' == e:
                e = 'NAACCR'
            elif 'NDC' == e:
                e = 'NDC'
            elif 'NDFRT' == e:
                e = 'NDFRT'
            elif ('NHS NATIONAL CODES' == e
                  or 'WWW.DATADICTIONARY.NHS.UK/DATA_DICTIONARY' in e
                  or 'WWW.GOV.UK/GOVERNMENT/STATISTICS' in e
                  or 'HS DATA DICTIONARY' in e):
                e = 'NHS NATIONAL CODES'
            elif 'WWW.NDC.SCOT.NHS.UK/DICTIONARY-A-Z' in e:
                e = 'NHS SCOTLAND NATIONAL CODES'
            elif ('GOV.WALES/NATIONAL-SURVEY-WALES' in e
                  or 'WWW.DATADICTIONARY.WALES.NHS.UK' in e):
                e = 'NHS WALES NATIONAL CODES'
            elif 'ODS' == e:
                e = 'ODS'
            elif ('OPCS4' == e[:5]
                  or 'OPSC 4.8' == e
                  or 'OPSC' in e
                  or 'OPCS' in e):
                e = 'OPCS4'
            elif 'OTHER' == e:
                e = 'OTHER'
            elif 'OXMIS' == e:
                e = 'OXMIS'
            elif ('READ' in e or 'READ V2'==e):
                e = 'READ'
            elif 'RXNORM' == e:
                e = 'RXNORM'
            elif 'RXNORM EXTENSION' == e:
                e = 'RXNORM EXTENSION'
            elif ('SNOMED RT' in e
                  or 'SNOMED-RT' in e
                  or 'SNOMEDRT' in e
                  or 'SNOMED_RT' in e):
                e = 'SNOMED RT'
            elif ('SNOMED' in e):
                e = 'SNOMED CT'
            elif 'SPL' == e:
                e = 'SPL'

            dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["vocabularyEncodingScheme"].append(e)


def mapl_accessibility_formatAndStandards_conformsTo(dm_v1, dm_v2):
    dm_conformsTo = dm_v1.get('conformsTo', None)
    dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["conformsTo"] = []
    if dm_conformsTo:
        dm_conformsTo = dm_conformsTo.replace(';', ',')
        dm_conformsTo = dm_conformsTo.upper()
        conformsTo = dm_conformsTo.split(',')
        for c in conformsTo:
            c = c.lstrip()
            if 'AMT' == c:
                c = 'AMT'
            elif 'APC' == c:
                c = 'APC'
            elif 'ATC' == c:
                c = 'ATC'
            elif 'CIEL' == c:
                c = 'CIEL'
            elif 'CPT4' == c:
                c = 'CPT4'
            elif 'DM PLUS D' == c:
                c = 'DM PLUS D'
            elif 'DPD' == c:
                c = 'DPD'
            elif 'DRG' == c:
                c = 'DRG'
            elif 'HEMONC' == c:
                c = 'HEMONC'
            elif 'HPO' == c:
                c = 'HPO'
            elif 'ICD10' == c:
                c = 'ICD10'
            elif 'ICD10CM' == c:
                c = 'ICD10CM'
            elif 'ICD10PCS' == c:
                c = 'ICD10PCS'
            elif 'ICD9' == c:
                c = 'ICD9'
            elif 'ICD9CM' == c:
                c = 'ICD9CM'
            elif 'ICDO3' == c:
                c = 'ICDO3'
            elif 'JMDC' == c:
                c = 'JMDC'
            elif 'KCD7' == c:
                c = 'KCD7'
            elif 'LOCAL' == c[:5]:
                c = 'LOCAL'
            elif 'LOINC' == c:
                c = 'LOINC'
            elif 'MULTUM' == c:
                c = 'MULTUM'
            elif 'NAACCR' == c:
                c = 'NAACCR'
            elif 'NDC' == c:
                c = 'NDC'
            elif 'NDFRT' == c:
                c = 'NDFRT'
            elif 'NHS NATIONAL CODES' == c:
                c = 'NHS NATIONAL CODES'
            elif ('NHS DATA DICTIONARY' == c
                  or 'WWW.DATADICTIONARY.NHS.UK' in c):
                c = 'NHS DATA DICTIONARY'
            elif 'NHS SCOTLAND NATIONAL CODES' == c:
                c = 'NHS SCOTLAND NATIONAL CODES'
            elif ('WWW.NDC.SCOT.NHS.UK/DICTIONARY-A-Z' in c
                  or 'WWW.NDC.SCOT.NHS.UK/DICTIONARY-A-Z' in c):
                c = 'NHS SCOTLAND DATA DICTIONARY'
            elif 'NHS WALES NATIONAL CODES' == c:
                c = 'NHS WALES NATIONAL CODES'
            elif 'WWW.DATADICTIONARY.WALES.NHS.UK' in c:
                c = 'NHS WALES DATA DICTIONARY'
            elif 'ODS' == c:
                c = 'ODS'
            elif 'OPCS4' == c:
                c = 'OPCS4'
            elif ('OTHER' == c
                  or 'GOV.WALES' in c
                  or 'WWW.GOV.UK/GOVERNMENT/STATISTICS' in c):
                c = 'OTHER'
            elif 'OXMIS' == c:
                c = 'OXMIS'
            elif 'READ' == c:
                c = 'READ'
            elif 'RXNORM EXTENSION' == c:
                c = 'RXNORM EXTENSION'
            elif 'RXNORM' == c:
                c = 'RXNORM'
            elif 'SNOMED CT' == c:
                c = 'SNOMED CT'
            elif 'SNOMED RT' == c:
                c = 'SNOMED RT'
            elif 'SPL' == c:
                c = 'SPL'
            dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["conformsTo"].append(c)


def mapl_accessibility_formatAndStandards_language(dm_v1, dm_v2):
    dm_language = dm_v1.get('language', None)
    if 'English (UK)'==dm_language:
        dm_language='en'
    dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["language"] = []
    if dm_language:
        dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["language"] = [dm_language]


def mapl_accessibility_formatAndStandards_format(dm_v1, dm_v2):
    dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["format"] = []
    dm_format = dm_v1.get('format', None)
    if dm_format:
        dm_format = dm_format.replace(';', ',')
        formats = dm_format.split(',')
        for f in formats:
            dm_v2.setdefault("accessibility", {}).setdefault("formatAndStandards", {})["format"].append(f.lstrip())


def mapl_enrichmentAndLinkage_qualifiedRelation(dm_v1, dm_v2):
    dm_v2.setdefault("enrichmentAndLinkage", {})["qualifiedRelation"] = []
    dm_linkedDataset = dm_v1.get('linkedDataset', None)
    if dm_linkedDataset:
        dm_linkedDataset = dm_linkedDataset.replace(';', ',')
        linkedDatasets = dm_linkedDataset.split(',')
        for l in linkedDatasets:
            dm_v2.setdefault("enrichmentAndLinkage", {})["qualifiedRelation"].append(l.lstrip())


def mapl_enrichmentAndLinkage_derivation(dm_v1, dm_v2):
    dm_v2.setdefault("enrichmentAndLinkage", {})["derivation"] = []
    dm_derivedDatasets = dm_v1.get('derivedDatasets', None)
    if dm_derivedDatasets:
        dm_derivedDatasets = dm_derivedDatasets.replace(';', ',')
        derivedDatasets = dm_derivedDatasets.split(',')
        for d in derivedDatasets:
            dm_v2.setdefault("enrichmentAndLinkage", {})["derivation"].append(d.lstrip())


def mapl_enrichmentAndLinkage_tools(dm_v1, dm_v2):
    dm_v2.setdefault("enrichmentAndLinkage", {})["tools"] = [] #['enrichmentAndLinkage_tools']


def mapl_observations(dm_v1, dm_v2):
    dm_v2["observations"] = [] #[{'observations_observedNode':'observations_observedNode', 'observations_measuredValue':'observations_measuredValue', 'observations_observationDate':'observations_observationDate', 'observations_disambiguatingDescription':'observations_disambiguatingDescription', 'observations_measuredProperty':'observations_measuredProperty'}]


#### END DEFINE MAPPING v1 --> v2 ####


#### MAPPING ####
def map_data(dm_v1, dm_v2):
#### START MAPPING v1 --> v2 ####
    map_identifier(dm_v1, dm_v2)
    map_schema(dm_v1, dm_v2)
    map_version(dm_v1, dm_v2)
    mapl_revisions(dm_v1, dm_v2)
    map_issued(dm_v1, dm_v2)
    map_modified(dm_v1, dm_v2)
    map_summary_title(dm_v1, dm_v2)
    map_summary_abstract(dm_v1, dm_v2)
    map_summary_publisher_memberOf(dm_v1, dm_v2)
    map_summary_publisher_accessRights(dm_v1, dm_v2)
    map_summary_publisher_deliveryLeadTime(dm_v1, dm_v2)
    map_summary_publisher_dataUseLimitation(dm_v1, dm_v2)
    map_summary_publisher_dataUseRequirements(dm_v1, dm_v2)
    map_summary_publisher_accessService(dm_v1, dm_v2)
    map_summary_publisher_name(dm_v1, dm_v2)
    map_summary_publisher_logo(dm_v1, dm_v2)
    map_summary_publisher_description(dm_v1, dm_v2)
    map_summary_publisher_contactPoint(dm_v1, dm_v2)
    map_summary_contactPoint(dm_v1, dm_v2)
    mapl_summary_keywords(dm_v1, dm_v2)
    map_summary_alternateIdentifiers(dm_v1, dm_v2)
    map_summary_doiName(dm_v1, dm_v2)
    map_documentation_description(dm_v1, dm_v2)
    mapl_documentation_associatedMedia(dm_v1, dm_v2)
    mapl_documentation_isPartOf(dm_v1, dm_v2)
    map_coverage_spatial(dm_v1, dm_v2)
    map_coverage_typicalAgeRange(dm_v1, dm_v2)
    mapl_coverage_physicalSampleAvailability(dm_v1, dm_v2)
    map_coverage_followup(dm_v1, dm_v2)
    mapl_coverage_pathway(dm_v1, dm_v2)
    mapl_provenance_origin_purpose(dm_v1, dm_v2)
    mapl_provenance_origin_source(dm_v1, dm_v2)
    mapl_provenance_origin_collectionSituation(dm_v1, dm_v2)
    map_provenance_temporal_accrualPeriodicity(dm_v1, dm_v2)
    map_provenance_temporal_distributionReleaseDate(dm_v1, dm_v2)
    map_provenance_temporal_endDate(dm_v1, dm_v2)
    map_provenance_temporal_timeLag(dm_v1, dm_v2)
    map_provenance_temporal_startDate(dm_v1, dm_v2)
    map_accessibility_access_accessRights(dm_v1, dm_v2)
    map_accessibility_access_accessService(dm_v1, dm_v2)
    map_accessibility_access_deliveryLeadTime(dm_v1, dm_v2)
    mapl_accessibility_access_jurisdiction(dm_v1, dm_v2)
    map_accessibility_access_dataController(dm_v1, dm_v2)
    map_accessibility_access_dataProcessor(dm_v1, dm_v2)
    mapl_accessibility_usage_dataUseLimitation(dm_v1, dm_v2)
    mapl_accessibility_usage_dataUseRequirements(dm_v1, dm_v2)
    map_accessibility_usage_resourceCreator(dm_v1, dm_v2)
    mapl_accessibility_usage_investigations(dm_v1, dm_v2)
    mapl_accessibility_usage_isReferencedBy(dm_v1, dm_v2)
    mapl_accessibility_formatAndStandards_vocabularyEncodingScheme(dm_v1, dm_v2)
    mapl_accessibility_formatAndStandards_conformsTo(dm_v1, dm_v2)
    mapl_accessibility_formatAndStandards_language(dm_v1, dm_v2)
    mapl_accessibility_formatAndStandards_format(dm_v1, dm_v2)
    mapl_enrichmentAndLinkage_qualifiedRelation(dm_v1, dm_v2)
    mapl_enrichmentAndLinkage_derivation(dm_v1, dm_v2)
    mapl_enrichmentAndLinkage_tools(dm_v1, dm_v2)
    mapl_observations(dm_v1, dm_v2)
#### END MAPPING v1 --> v2 ####