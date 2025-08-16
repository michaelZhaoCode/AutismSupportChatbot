"""Contains the constant values used by various parts of the code"""

MAIN_MODEL_USE = "gpt-4o"
SERVICE_MODEL_USE = "gpt-4o-mini"
BLURB_MODEL_USE = "gpt-4o-mini"

MAJORITY_VOTING_N = 5
BLURB_HISTORY_CONTEXT = 6

MAX_SERVICES_RECOMMENDED = 5

REGION_TYPE_PRIORITY = {
    "Country": 1,
    "Province": 2,
    "State": 2,
    "City": 3,
}

# Web Search Configuration
ENABLE_DOMAIN_FILTERING = True  # Set to False to disable domain filtering

# List of allowed domains for web search
# Only URLs from these domains will be searched and extracted
ALLOWED_DOMAINS = [
    # Government and official sources
    "gov",  # All .gov domains
    "gc.ca",  # Canadian government
    "nhs.uk",  # UK National Health Service
    
    # Medical and research institutions
    "nih.gov",
    "cdc.gov",
    "who.int",
    "pubmed.ncbi.nlm.nih.gov",
    "mayoclinic.org",
    "webmd.com",
    "healthline.com",
    
    # Autism-specific organizations
    "autismspeaks.org",
    "autism.org.uk",
    "autismcanada.org",
    "autismontario.com",
    "asatonline.org",
    "researchautism.org",
    "autismresearchcentre.org",
    
    # Educational institutions
    "edu",  # All .edu domains
    
    # Mental health organizations
    "psychiatry.org",
    "psychology.org",
    "apa.org",
    "nimh.nih.gov",
    
    # Disability and support organizations
    "disabilityrightsca.org",
    "thearc.org",
    "ndss.org",
    
    # Healthcare providers
    "childrenshospital.org",
    "chop.edu",
    "sickkids.ca",
    
    # Trusted medical journals
    "nejm.org",
    "thelancet.com",
    "nature.com",
    "sciencedirect.com",
    "springer.com",
    "wiley.com",
    
]