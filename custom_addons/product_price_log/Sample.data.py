import pandas as pd

# Create new data with similar structure but unique company/contact names
data = {
    "Lead Number": ["LD0015", "LD0016", "LD0017", "LD0018", "LD0019", "LD0020", "LD0021", "LD0022", "LD0023", "LD0024"],
    "Lead": [
        "Oil Distribution Partnership", "Industrial Fuel Supply", "Diesel Depot Setup",
        "Lubricant Distribution Deal", "Fuel Transport Service", "Bitumen Export Contract",
        "LPG Distribution Expansion", "Ethio Fuel Transport", "Petroleum Testing Project",
        "Oil Recycling Program"
    ],
    "Contact Name": [
        "Michael Getachew", "Abel Mulugeta", "Lidya Girma", "Kebede Alemu", "Hana Gebru",
        "Biniam Eshete", "Meron Kebede", "Samuel Worku", "Bethelhem Desta", "Dawit Alemayehu"
    ],
    "Company Name": [
        "BlueLine Oil Trading", "EthioFuel Logistics", "Oromia Infrastructure Supply",
        "Sheger Gas Distribution", "TransAfrica Energy", "Adama Heavy Industries",
        "EthioGas Systems", "TechLab Oil Services", "NextGen Fuel Systems", "EcoOil Recovery PLC"
    ],
    "Email": [
        "michael@bluelineoil.com", "abel@ethiofuel.com", "lidya@oromiainfra.com",
        "kebede@shegergas.com", "hana@transafrica.com", "biniam@adamaindustries.com",
        "meron@ethiogas.com", "samuel@techlab.com", "bethelhem@nextgenfuel.com",
        "dawit@ecooil.com"
    ],
    "Phone": [
        "0912345678", "0912456789", "0912567890", "0912678901", "0912789012",
        "0912890123", "0912901234", "0913012345", "0913123456", "0913234567"
    ],
    "Company": ["AMG Holdings"] * 10,
    "City": [
        "Addis Ababa", "Adama", "Jimma", "Sheger", "Hawassa", "Adama",
        "Mekelle", "Bahir Dar", "Addis Ababa", "Dire Dawa"
    ],
    "Country": ["Ethiopia"] * 10,
    "Salesperson": [
        "Sarah Confirmer", "Administrator", "Sarah Confirmer", "Administrator",
        "Sarah Confirmer", "Administrator", "Sarah Confirmer", "Administrator",
        "Sarah Confirmer", "Administrator"
    ],
    "Sales Team": ["Sales"] * 10,
    "Source": [
        "Online Inquiry", "Direct Call", "Marketing Campaign", "Telemarketing", "Trade Fair",
        "Walk-in Client", "Referral", "Conference", "Online Campaign", "Bidding"
    ]
}

# Create DataFrame and save as Excel
df = pd.DataFrame(data)
file_path = "D:\crm_project\custom_addons\product_price_log/CRM_Leads_Sample_New.xlsx"
df.to_excel(file_path, index=False)

file_path
