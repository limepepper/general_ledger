"""
this data was extracted from the wikipedia page on sort codes
https://en.wikipedia.org/wiki/Sort_code#England_and_Wales
if you need more information, you can visit the page
this is not being kept up to date
"""

sort_codes = {
    "00": "For IBAN use only",
    "01-": "NatWest Bank",
    "04-": "Utility bank",
    "04-00": "BFC Bank",
    "04-00-03..08": "Monzo",
    "04-00-11": "Satabank",
    "04-00-40": "Starling Bank",
    "04-00-53": "Payrnet/Railsbank",
    "04-00-72..74": "Modulr",
    "04-00-75": "Revolut",
    "04-00-76": "LCH Limited",
    "04-00-78": "Elavon Financial Services",
    "04-00-79..80": "Virgin Money Head Office",
    "04-03-00..29": "LHV Pank",
    "04-03-33": "Mettle by NatWest",
    "04-04-05": "ClearBank",
    "04-04-76..77": "Enumis",
    "04-05-40..41": "BCB Group",
    "04-06-05": "Tide by ClearBank",
    "04-13-01": "Midpoint & Transfer",
    "04-13-02..03": "Bilderlings Pay",
    "04-13-04..05": "Ecology Building Society",
    "04-13-06": "Allpay Limited",
    "04-13-07..08": "Clear Junction",
    "04-13-12": "Modulr",
    "04-13-13..14": "Project Imagine",
    "04-13-15..16": "Universal Securities & Investment",
    "04-13-17..19": "Contis Financial Services",
    "04-13-42": "Duesday",
    "04-29-09": "Revolut",
    "04-36-14..23": "Griffin Bank",
    "05-": "Clydesdale Bank (as Yorkshire Bank)",
    "07-00..49": "Nationwide Building Society",
    "08-": "The Co-operative Bank",
    "08-30-": "Citibank",
    "08-31..32": "UK Government banking",
    "08-33..39-": "Citibank",
    "08-60-64": "Virgin Money (ex Northern Rock account)",
    "09-": "Santander UK",
    "10-00..79-": "Bank of England",
    "11-": "Bank of Scotland",
    "12-": "Bank of Scotland",
    "12-00..69": "Sainsbury's Bank",
    "13..14-": "Barclays Bank",
    "15..19-": "Royal Bank of Scotland",
    "16-00-38": "Drummonds Bank",
    "16-52-21": "Cumberland Building Society",
    "16-57-10": "Cater Allen Private Bank",
    "18-00-00..14": "Coutts & Co",
    "18-00-36": "Coutts & Co",
    "18-00-38": "Coutts & Co",
    "18-00-91..98": "Coutts & Co",
    "18-01-01": "Coutts & Co",
    "18-01-04": "Coutts & Co",
    "18-01-09..10": "Coutts & Co",
    "18-01-55..56": "Coutts & Co",
    "18-40-40": "Coutts & Co",
    "18-50-01": "Coutts & Co",
    "20..29-": "Barclays Bank",
    "20-11-47": "HMRC",
    "23-00-88": "VFX Financial",
    "23-05-80": "Metro Bank",
    "23-05-05": "Stripe",
    "23-14-70": "Wise",
    "23-22-21": "Fire Financial Services",
    "23-32-72": "Pockit",
    "23-59-54": "Newcastle Building Society",
    "23-69-72": "Prepay Technologies",
    "23-73-24": "Loot Financial Services",
    "30-": "Lloyds or TSB Bank",
    "30-00-66": "Arbuthnot Latham Private Bank",
    "30-00-83": "Al Rayan Bank",
    "30-02-48": "FinecoBank UK",
    "40..49-": "HSBC Bank",
    "40-12-50..55": "M&S Bank",
    "40-51-78": "Jyske Bank Gibraltar",
    "40-51-98": "Turkish Bank UK",
    "40-60-80": "CashFlows",
    "40-63-01": "Coventry Building Society",
    "40-63-77": "Cynergy Bank Limited",
    "40-64-05..16": "Tesco Bank",
    "40-64-25": "Virgin Money",
    "40-64-37": "Marcus by Goldman Sachs",
    "50..59-": "NatWest Bank",
    "60-01-73": "Reliance Bank",
    "60-83-12": "Atom Bank",
    "60-83-14": "Gibraltar International Bank",
    "60-83-66": "Fidor Bank UK",
    "60-83-71": "Starling Bank",
    "60-84-00": "Zopa Bank Limited",
    "60-84-07": "Chase UK",
    "60..66-": "NatWest Bank",
    "60-93-03": "Weatherbys Bank Ltd",
    "60-93-71..76": "Bank of Baroda",
    "60-93-84": "Bank of Baroda",
    "70-": "International Bank (no longer issued?)",
    "71-": "National Savings Bank (bank of england)",
    "72-": "Santander UK",
    "77-00..44-": "Formerly Lloyds TSB",
    "77-46..99-": "Formerly Lloyds TSB",
    "80..81-": "Bank of Scotland",
    "82-": "Clydesdale Bank",
    "83..84-": "Royal Bank of Scotland",
    "86-": "Royal Bank of Scotland",
    "87-": "TSB Bank Plc",
    "89-00..29-": "Santander UK",
    "90-": "Bank of Ireland",
    "91-": "Northern Bank",
    "92-": "Central Bank of Ireland",
    "93-": "Allied Irish Banks (UK)",
    "93-09-03": "JP Morgan Bank Ireland plc",
    "93-90-21": "EBS d.a.c.",
    "94-": "Bank of Ireland",
    "95-": "Northern Bank",
    "98-": "Ulster Bank",
    "99-00-51..52": "Citibank Europe plc",
    "99-00-61..62": "Bank of America Realex Financial Services",
    "99-02-04": "Royal Bank of Scotland",
    "99-02-06": "BNP Paribas Ireland",
    "99-02-12": "Barclays Bank Ireland",
    "99-02-31": "HSBC Bank",
    "99-02-40": "ING Bank",
    "99-02-60": "Rabobank International",
    "99-02-70": "KBC Bank Ireland",
    "99-03-01": "An Post",
    "99-03-20": "Aareal Bank",
    "99-03-25": "CACEIS Bank",
    "99-03-60": "Revolut Bank UAB",
    "99-04-": "Bank of Scotland",
    "99-10-": "BNP Paribas Ireland for Irish Credit Unions",
    "99-11-99": "Fire Financial Services",
    "99-21..22-": "Irish Credit Unions",
    "99-99-01": "Central Bank of Ireland",
}
