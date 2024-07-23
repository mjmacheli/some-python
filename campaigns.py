import string
import datetime

import requests

lemlist_pw = ''
nordbak_company_guid = ''
nordbak_sales_stuff_guid = ''
success_msg = 'Lead Created Successfully'
bluwavecrm_url = "https://www.bluwavecrm.co.za/WebService/Service1.asmx"
bluwavecrm_headers = {
    'Content-Type': 'application/soap+xml; charset=utf-8'
}

campaigns = [
    'cam_QR4Q3GJuDT7rWq5Nq']


class Lead:
    companyGuid = nordbak_company_guid  # not required
    salesStaffGuid = nordbak_sales_stuff_guid  # not required
    companyName = ''  # required
    title = ''  # not required
    initial = ''  # not required
    firstName = ''  # not required
    surname = ''  # not required
    designation = ''  # not required
    cellNo = ''  # not required
    telNo = ''  # not required
    faxNo = ''  # not required
    email = ''  # not required
    postalAddress1 = ''  # not required
    postalAddress2 = ''  # not required
    postalAddress3 = ''  # not required
    postCode = ''  # not required
    postalCountry = ''  # not required
    physicalAddress1 = ''  # not required
    physicalAddress2 = ''  # not required
    physicalAddress3 = ''  # not required
    physicalPostCode = ''  # not required
    physicalCountry = ''  # not required
    status = ''  # not required
    source = ''  # not required
    noOfEmployees = 0  # required
    industry = ''  # not required
    notes = ''  # not required
    rating = ''  # not required
    UDF1 = 0  # required
    UDF2 = 0  # required
    UDF3 = 0  # required
    UDF4 = ''  # not required
    UDF5 = ''  # not required
    UDF6 = ''  # not required


class PhysicalAddress:
    physicalAddress1 = ''
    physicalAddress2 = ''
    physicalAddress3 = ''
    physicalPostCode = ''
    physicalCountry = ''


def send_to_log(message):
    with open(f'{datetime.date.today()}.log', 'a+') as f:
        print(f"Timestamp: {datetime.datetime.now()}", file=f)
        print(message, file=f)


def fetch_leads(campaign_id):
    rest_url = f'https://api.lemlist.com/api/campaigns/{campaign_id}/export/leads?state=all'
    username = ""
    password = lemlist_pw
    session = requests.Session()
    session.auth = (username, password)

    response = session.get(rest_url)
    if response.status_code == 200:
        return response.text.split('\n')
    else:
        send_to_log(response.text)


def transform_lead_to_xml(lead: Lead):
    return f'''<?xml version="1.0" encoding="utf-8"?>
        <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                <soap12:Body>
                    <InsertLead xmlns="https://www.bluwavecrm.co.za/WebService">
                    <CompanyGuid>{lead.companyGuid}</CompanyGuid>
                    <SalesStaffGuid>{lead.salesStaffGuid}</SalesStaffGuid>
                    <CompanyName>{lead.companyName}</CompanyName>
                    <Title>Testing {lead.title}</Title>
                    <Initial>{lead.initial}</Initial>
                    <FirstName>test mj {lead.firstName}</FirstName>
                    <Surname>test mj {lead.surname}</Surname>
                    <Designation>{lead.designation}</Designation>
                    <CellNo>{lead.cellNo}</CellNo>
                    <TelNo>{lead.telNo}</TelNo>
                    <FaxNo>{lead.faxNo}</FaxNo>sdf
                    <Email>{lead.email}</Email>
                    <PostalAddress1>{lead.postalAddress1}</PostalAddress1>
                    <PostalAddress2>{lead.postalAddress2}</PostalAddress2>
                    <PostalAddress3>{lead.postalAddress3}</PostalAddress3>
                    <PostCode>{lead.postCode}</PostCode>
                    <PostalCountry>{lead.postalCountry}</PostalCountry>
                    <PhysicalAddress1>{lead.physicalAddress1}</PhysicalAddress1>
                    <PhysicalAddress2>{lead.physicalAddress2}</PhysicalAddress2>
                    <PhysicalAddress3>{lead.physicalAddress3}</PhysicalAddress3>
                    <PhysicalPostCode>{lead.physicalPostCode}</PhysicalPostCode>
                    <PhysicalCountry>{lead.physicalCountry}</PhysicalCountry>
                    <Status>{lead.status}</Status>
                    <Source>{lead.source}</Source>
                    <NoOfEmployees>{lead.noOfEmployees}</NoOfEmployees>
                    <Industry>{lead.industry}</Industry>
                    <Notes>{lead.notes}</Notes>
                    <Rating>{lead.rating}</Rating>
                    <UDF1>{lead.UDF1}</UDF1>
                    <UDF2>{lead.UDF2}</UDF2>
                    <UDF4>{lead.UDF4}</UDF4>
                    <UDF5>{lead.UDF5}</UDF5>
                    <UDF6>{lead.UDF6}</UDF6>
                    </InsertLead>
                </soap12:Body>
            </soap12:Envelope>'''


def transform_leads(payload: list[string]):
    # payload is an array of leads in the below format
    # emailStatus,email,firstName,lastName,picture,phone,linkedinUrl,companyName,companyDomain,icebreaker,Title,
    # Industry,Website,Company Address,Company City,Company State,Company Country,_ Employees,Job Title,Job title,
    # lastState,status
    results = list[Lead]()
    del payload[0]
    if len(payload) == 0:
        return []
    for elem in payload:
        lead = Lead()
        data = elem.split(',')
        physical_addr = data[14].split(',')
        if len(physical_addr) > 1:
            # physical address element
            lead.physicalAddress1 = physical_addr[0]
            lead.physicalAddress2 = physical_addr[1]
            lead.physicalAddress3 = physical_addr[2]
            lead.physicalCountry = physical_addr[3]
            lead.physicalPostCode = physical_addr[4]
        lead.email = data[1]
        lead.firstName = data[2]
        lead.surname = data[3]
        lead.cellNo = data[5]
        lead.companyName = data[7] if data[7] else 'No Company'
        lead.title = data[10]
        lead.industry = data[11]

        lead.noOfEmployees = data[17] if data[17] else 0
        lead.UDF1 = 0
        lead.UDF2 = 0
        lead.notes = f'''company domain: {data[8]}\nice breaker: {data[9]}\n''' if data[8] and data[9] else ''
        lead.status = 'AL'
        lead.source = 'WEB'
        results.append(lead)
    return results


def post_leads_to_bluwave(leads: list[Lead]):
    for lead in leads:
        response = requests.request("POST", bluwavecrm_url,
                                    headers=bluwavecrm_headers, data=transform_lead_to_xml(lead))
        if success_msg not in response.text:
            send_to_log(response.text)


def upload_leads():
    for campaign in campaigns:
        lemlist_leads = fetch_leads(campaign)
        if lemlist_leads:
            transformed_leads = transform_leads(lemlist_leads)
            post_leads_to_bluwave(transformed_leads)


upload_leads()