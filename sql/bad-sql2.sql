select
    party.Sales_Location_Id AS Sales_Location_Id, SFDC_ACCOUNT.SFDC_Account_Id AS SFDCAccountId,
    MAX(party.Org_Name_1) AS 1_Org_Name_, MAX(party.Org_Name_2) AS 2_Org_Name_,
    MAX(BEDIRECT_BRANCHENTEXT_REF.Be_Branche) AS IndustrySectorId,
    MAX(BEDIRECT_BRANCHENTEXT_REF.Be_Branchentext) AS IndustrySectorDescription,
    CAST(MAX(BEDIRECT_UNTERNEHMEN.BE_MITARBEITERZAHL) AS VARCHAR(50)) AS SalesLocation_Employee_Count
from MCDM_TPRD.CMR_CUSTOMER_BASE AS c1
join CIM_ENTERPRISE_PRD.CUSTOMER_ACCOUNT AS CUSTOMER_ACCOUNT
    on c1.Cust_Ident_1_Num
        = COALESCE(
            CAST(CUSTOMER_ACCOUNT.Ban AS VARCHAR(50)),
            CUSTOMER_ACCOUNT.Customer_Number
        )
        and COALESCE(c1.Cust_Ident_2_Num, '')
        = COALESCE(CUSTOMER_ACCOUNT.Market_Code, '')
join MCDM_TPRD.CMR_CUSTOMER_SAT_CAMP_CLUSTER AS CMR_CUSTOMER_SAT_CAMP_CLUSTER
    on c1.Pega_Cust_Id = CMR_CUSTOMER_SAT_CAMP_CLUSTER.Pega_Cust_Id
join CIM_ENTERPRISE_PRD.PARTY AS party
    on CUSTOMER_ACCOUNT.Party_Id = party.Party_Id
join DWH_CRM_PRD.SFDC_ACCOUNT AS SFDC_ACCOUNT
    on party.Sales_Location_Id = SFDC_ACCOUNT.Party_Id
left outer join CIM_ENTERPRISE_PRD.BEDIRECT_UNTERNEHMEN AS BEDIRECT_UNTERNEHMEN
    on party.Bedirect_Id = BEDIRECT_UNTERNEHMEN.BE_ID
        and party.Data_Source = BEDIRECT_UNTERNEHMEN.Be_KundenDatenLieferant_Name
        and party.Bedirect_Id IS NOT NULL
        and upper(party.Data_Source) IN ('BEDIRECT', 'INFAS-BED')
left outer join
    ODS_UDB_TPRD.BEDIRECT_BRANCHENTEXT_REF AS BEDIRECT_BRANCHENTEXT_REF
    ON BEDIRECT_UNTERNEHMEN.Be_Primaerbranche = BEDIRECT_BRANCHENTEXT_REF.Be_Branche
where
    CMR_CUSTOMER_SAT_CAMP_CLUSTER.Campaign_Cluster_Cd = 'CS' -- CS = Cluster SoHo
    and CUSTOMER_ACCOUNT.ROLE_FLAG = 'CH'
group by party.Sales_Location_Id, SFDC_ACCOUNT.SFDC_Account_Id