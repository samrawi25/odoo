import pandas as pd

# Leads as consumers of AMG Holdings and Adama Steel
data = {
    "Lead Number": ["LD0045", "LD0046", "LD0047", "LD0048", "LD0049", "LD0050", "LD0051", "LD0052", "LD0053", "LD0054"],
    "Lead": [
        "Coffee Packaging Expansion", "Construction Firm Steel Supply", "Nail Usage in Residential Projects",
        "Wire Rod Bulk Purchase", "RHS Structural Project", "CCL Sheet Procurement",
        "Organic Coffee Export", "Industrial Building Steel Usage", "Wire Rod Supply for Manufacturing", "High-Volume Nail Procurement"
    ],
    "Contact Name": [
        "Alemayehu Bekele", "Sara Desta", "Tigist Abate", "Yonas Fikadu", "Meron Tesfaye",
        "Daniel Kebede", "Hanna Tadesse", "Fitsum Alemayehu", "Bethelhem Gebremedhin", "Samuel Mekonnen"
    ],
    "Company Name": [
        "EthioCoffee Packers", "Addis Construction Co.", "Oromia Housing Projects", "WireBuild Ltd",
        "RHS Builders Co.", "CCL Fabricators", "BlueBean Exports", "MegaSteel Contractors", "WireTech Manufacturing", "Prime Nails Importers"
    ],
    "Email": [
        "alemayehu@ethiocoffee.com", "sara@addisconstruction.com", "tigist@oromiahousing.com", "yonas@wirebuild.com",
        "meron@rhsbuilders.com", "daniel@cclfabricators.com", "hanna@bluebeanexports.com", "fitsum@megasteel.com",
        "bethelhem@wiretech.com", "samuel@primenails.com"
    ],
    "Phone": [
        "0913344550", "0913344551", "0913344552", "0913344553", "0913344554",
        "0913344555", "0913344556", "0913344557", "0913344558", "0913344559"
    ],
    "Company": ["Consumer"] * 10,
    "City": [
        "Addis Ababa", "Bahir Dar", "Jimma", "Adama", "Hawassa",
        "Mekelle", "Dire Dawa", "Gondar", "Addis Ababa", "Adama"
    ],
    "Country": ["Ethiopia"] * 10,
    "Salesperson": [
        "Sarah Confirmer", "Administrator", "Sarah Confirmer", "Administrator",
        "Sarah Confirmer", "Administrator", "Sarah Confirmer", "Administrator",
        "Sarah Confirmer", "Administrator"
    ],
    "Sales Team": ["Sales"] * 10,
    "Source": [
        "Referral", "Direct Call", "Marketing Campaign", "Trade Fair", "Walk-in Client",
        "Conference", "Online Inquiry", "Telemarketing", "Bidding", "Online Campaign"
    ]
}

# Create DataFrame and save as Excel
df = pd.DataFrame(data)
file_path = "D:\crm_project\custom_addons\product_price_log/CRM_Leads_Consumer_Industrial.xlsx"
df.to_excel(file_path, index=False)

file_path
