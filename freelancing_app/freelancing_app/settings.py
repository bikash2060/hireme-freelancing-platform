from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _

# Define base directory path for the project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key for Django project; keep it confidential in production.
SECRET_KEY = "django-insecure-y9vjmoy_i9&x-5!dq7w-dq+fsts@dsmut9(yp)$)lyg%rd43_x"

# Debug mode setting; should be False in production.
DEBUG = True

# List of allowed hostnames for the application.
ALLOWED_HOSTS = ['*']

SITE_ID = 1

# Installed apps for the project, including Django and custom apps
INSTALLED_APPS = [
    # Django built-in apps
    "django.contrib.admin",
    'django.contrib.sites',
    'django.contrib.auth',
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.humanize',
    "channels",

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    
    # Custom apps
    "accounts",
    "chat",
    "clientprofile",
    "dashboard",
    "freelancerprofile",
    "home",
    "notification",
    "projects",
    "proposals",
]

# Middleware stack for request/response processing
MIDDLEWARE = [
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "accounts.middleware.UserActivityMiddleware",
]

# Message storage backend for the project
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Root URL configuration for the project
ROOT_URLCONF = "freelancing_app.urls"

# Templates configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / 'templates',
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "notification.context_processors.notifications",
            ],
        },
    },
]

# WSGI application entry point for the project
WSGI_APPLICATION = "freelancing_app.wsgi.application"

ASGI_APPLICATION = "freelancing_app.asgi.application"

# Channel layers configuration for WebSocket support
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# Database configuration for MySQL backend
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hireme_db',
        'USER': 'root',
        'PASSWORD': 'Bishal@123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'accounts.utils.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Login and redirect URLs
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
SOCIALACCOUNT_LOGIN_ON_GET = True

# Use our custom social account adapter
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = False

# Basic allauth settings
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"

# Google OAuth provider settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['email', 'profile'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
        'VERIFIED_EMAIL': True,
    }
}

# Language and timezone settings
LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('en', _('English')),
    ('ne', _('Nepali')),
]

TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_L10N = True
USE_TZ = False

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files settings
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'bishalbhattarai472@gmail.com'
EMAIL_HOST_PASSWORD = 'auqv lisg jxjh sjis'

# Reserved usernames that users can't register with
RESERVED_USERNAMES = {
    "admin", "administrator", "root", "superuser", "sysadmin", 
    "moderator", "support", "helpdesk", "service", "client",
    "freelancer", "user", "guest", "owner", "manager",
    "staff", "team", "developer", "dev", "test",
    "system", "operator", "security", "bot", "official"
}

PROJECT_CATEGORIES = [
    "Web Development",
    "Mobile App Development",
    "Software Development",
    "Data Science & AI",
    "Game Development",
    "Blockchain & Cryptocurrency",
    "E-Commerce Development",
    "Chatbot Development",
    "Desktop Applications",
    "Product Management",
    "UX/UI Design",
    "Graphic Design",
    "Logo & Brand Identity",
    "Illustration",
    "3D Modeling & CAD",
    "Video Editing",
    "Animation",
    "Photography",
    "Virtual Reality",
    "Augmented Reality",
    "Digital Marketing",
    "SEO",
    "Social Media Marketing",
    "Content Marketing",
    "Email Marketing",
    "Copywriting",
    "Technical Writing",
    "Content Writing",
    "Blog & Article Writing",
    "Proofreading & Editing",
    "Translation",
    "Voice Over",
    "Business Consulting",
    "Financial Consulting",
    "Legal Consulting",
    "Career Counseling",
    "Life Coaching",
    "Data Entry",
    "Excel & Google Sheets",
    "PowerPoint Presentations",
    "Virtual Assistant",
    "Customer Service",
    "Market Research",
    "Architecture & Interior Design",
    "Engineering & CAD",
    "Electrical Engineering",
    "Mechanical Engineering",
    "Civil Engineering",
    "Accounting & Bookkeeping",
    "Tax Preparation",
    "ERP Consulting",
    "HR Consulting",
    "Recruiting",
    "Education & Tutoring",
    "Music & Audio Production",
    "Fitness & Nutrition",
    "Event Planning",
    "Fashion & Jewelry Design",
    "Other"
]

skills_list = [
    # Programming Languages
    "Python", "JavaScript", "Java", "C#", "C++", "PHP", "Ruby", "Swift", "Kotlin", "TypeScript",
    "Go", "Rust", "Scala", "Perl", "Objective-C", "R", "MATLAB", "Dart", "Lua", "Groovy",
    "Haskell", "Clojure", "Erlang", "F#", "VBA", "Shell Script", "PowerShell", "Bash", "COBOL", "Fortran",
    "Assembly", "Visual Basic", "Delphi", "Ada", "ABAP", "Apex", "Crystal", "Elixir", "Elm", "Julia",
    "Lisp", "Prolog", "Scheme", "Smalltalk", "Solidity", "SQL", "PL/SQL", "T-SQL", "HiveQL", "SQRL",
    
    # Web Development - Frontend
    "HTML", "CSS", "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "Svelte", "jQuery", "Bootstrap",
    "Material UI", "Tailwind CSS", "SASS", "LESS", "Emotion", "Styled Components", "Redux", "MobX", "RxJS", "Next.js",
    "Gatsby", "Nuxt.js", "Ember.js", "Backbone.js", "Polymer", "Lit", "Alpine.js", "Stimulus", "Solid.js", "Preact",
    "Web Components", "PWA", "AMP", "Webpack", "Rollup", "Parcel", "Vite", "Snowpack", "Babel", "ESLint",
    "Prettier", "Jest", "Cypress", "Playwright", "Puppeteer", "Storybook", "Vitest", "Testing Library", "Mocha", "Chai",
    
    # Web Development - Backend
    "Node.js", "Express.js", "Django", "Flask", "Ruby on Rails", "Laravel", "Spring Boot", "ASP.NET Core", "FastAPI", "Symfony",
    "CodeIgniter", "CakePHP", "Zend Framework", "Yii", "Sinatra", "Tornado", "NestJS", "Strapi", "Adonis.js", "Koa.js",
    "Feathers.js", "Hapi.js", "LoopBack", "Meteor", "Sails.js", "GraphQL", "REST API", "SOAP", "JSON-RPC", "gRPC",
    "WebSockets", "Socket.IO", "JWT", "OAuth", "OpenID Connect", "Passport.js", "Spring Security", "Auth0", "Keycloak", "Okta",
    
    # Mobile Development
    "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic", "PhoneGap", "Cordova", "Swift UI", "Jetpack Compose",
    "Objective-C", "Kotlin", "Java for Android", "SwiftUI", "UIKit", "ARKit", "Core ML", "Android Jetpack", "Kotlin Multiplatform Mobile", "NativeScript",
    "Mobile App Design", "Progressive Web Apps", "Responsive Web Design", "Mobile App Testing", "App Store Optimization", "In-App Purchases", "Push Notifications", 
    "Mobile Analytics", "Mobile Security", "Mobile Performance Optimization",
    
    # Database Technologies
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Microsoft SQL Server", "MariaDB", "Redis", "Cassandra", "DynamoDB",
    "Firebase", "Elasticsearch", "Firestore", "Neo4j", "CouchDB", "Realm", "Couchbase", "InfluxDB", "TimescaleDB", "Amazon RDS",
    "Azure SQL", "Google Cloud SQL", "IBM Db2", "Supabase", "PlanetScale", "Cockroach DB", "Database Design", "Data Modeling", "Database Optimization", "Database Migration",
    "SQL Queries", "Normalization", "Denormalization", "Indexing", "Stored Procedures", "Triggers", "Views", "Constraints", "Transactions", "ACID Compliance",
    
    # DevOps & Cloud
    "AWS", "Azure", "Google Cloud", "Heroku", "DigitalOcean", "Linode", "OVH", "Vultr", "Alibaba Cloud", "Oracle Cloud",
    "Docker", "Kubernetes", "Jenkins", "GitLab CI/CD", "GitHub Actions", "CircleCI", "Travis CI", "Ansible", "Terraform", "Puppet",
    "Chef", "SaltStack", "Vagrant", "Packer", "Docker Compose", "Docker Swarm", "Kubernetes Operators", "Helm", "Prometheus", "Grafana",
    "ELK Stack", "Logstash", "Kibana", "Splunk", "Datadog", "New Relic", "Dynatrace", "AppDynamics", "Sentry", "PagerDuty",
    "CloudWatch", "CloudTrail", "Azure Monitor", "Stackdriver", "Linux Administration", "Windows Server Administration", "Network Administration", "Load Balancing", "Proxies", "VPN",
    
    # Data Science & Analytics
    "Data Analysis", "Data Science", "Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision", "Statistical Analysis", 
    "Predictive Modeling", "Data Mining", "Big Data", "Data Visualization", "Tableau", "Power BI", "Looker", "QlikView", "Qlik Sense", "D3.js", "Matplotlib", "Seaborn", "Plotly",
    "Pandas", "NumPy", "SciPy", "scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM", "CatBoost",
    "NLTK", "SpaCy", "OpenCV", "Dask", "PySpark", "Hadoop", "Apache Spark", "Apache Flink", "Apache Kafka", "Apache Airflow",
    "ETL", "Data Warehousing", "Data Pipeline", "Data Lake", "Data Governance", "Feature Engineering", "Dimensionality Reduction", "Clustering", "Classification", "Regression",
    
    # AI & Machine Learning
    "Artificial Intelligence", "Machine Learning", "Deep Learning", "Neural Networks", "Reinforcement Learning", "Supervised Learning", "Unsupervised Learning", 
    "Transfer Learning", "GANs", "Transformers", "BERT", "GPT", "LLM", "DALL-E", "Stable Diffusion", "Midjourney", "Computer Vision", "Natural Language Processing", 
    "Speech Recognition", "Text-to-Speech", "Image Recognition", "Object Detection", "Facial Recognition", "Semantic Segmentation", "Time Series Analysis", 
    "Anomaly Detection", "Recommendation Systems", "Chatbots", "Voice Assistants", "Sentiment Analysis", "A/B Testing", "Hyperparameter Tuning", "Feature Selection",
    "Model Deployment", "MLOps", "AI Ethics", "Explainable AI", "Model Interpretability", "Quantization", "Model Compression",
    
    # UI/UX Design
    "UI Design", "UX Design", "User Interface", "User Experience", "Wireframing", "Prototyping", "Mockups", "User Research", "Usability Testing", "Information Architecture",
    "Interaction Design", "Visual Design", "Responsive Design", "Mobile Design", "Web Design", "App Design", "Design Systems", "Atomic Design", "Material Design", 
    "Human Interface Guidelines", "Accessibility", "Color Theory", "Typography", "User Flows", "Journey Mapping", "Persona Development", "A/B Testing", "User-Centered Design", 
    "Design Thinking", "Heuristic Evaluation", "Figma", "Adobe XD", "Sketch", "InVision", "Axure", "Balsamiq", "Marvel", "Framer", "Zeplin", "Abstract",
    
    # Graphic Design
    "Graphic Design", "Illustration", "Logo Design", "Brand Identity", "Typography", "Print Design", "Layout Design", "Package Design", "Editorial Design", "Book Cover Design",
    "Poster Design", "Brochure Design", "Advertising Design", "Album Cover Design", "T-shirt Design", "Merchandise Design", "Icon Design", "Infographic Design", "Data Visualization", 
    "Vector Graphics", "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Affinity Designer", "Affinity Photo", "Affinity Publisher", "CorelDRAW", "GIMP", "Inkscape", "Procreate",
    "Digital Painting", "Photo Editing", "Photo Retouching", "Photo Manipulation", "Color Correction", "Vector Illustration", "Raster Graphics", "Pattern Design", "Texture Creation", 
    "Digital Art",
    
    # Motion Graphics & Animation
    "Motion Graphics", "Animation", "2D Animation", "3D Animation", "Character Animation", "Motion Design", "After Effects", "Cinema 4D", "Blender", "Maya",
    "3ds Max", "Houdini", "Nuke", "Fusion", "Toon Boom", "Animate CC", "Harmony", "Stop Motion", "Frame-by-Frame Animation", "Rigging",
    "Compositing", "Visual Effects", "VFX", "Special Effects", "Particle Systems", "Dynamics", "Fluid Simulation", "Character Rigging", "Character Modeling", "Texture Mapping",
    "UV Mapping", "Shader Development", "Lighting", "Rendering", "Post-Production", "Color Grading", "Rotoscoping", "Match Moving", "Motion Tracking", "Chroma Keying",
    
    # 3D Modeling & Rendering
    "3D Modeling", "3D Design", "3D Printing", "CAD", "Parametric Modeling", "Sculpting", "Hard Surface Modeling", "Organic Modeling", "Architectural Visualization", "Product Visualization",
    "Interior Design", "Exterior Design", "Landscape Design", "Character Modeling", "Environment Modeling", "Prop Modeling", "Asset Creation", "Texture Creation", "Material Creation", "Rendering",
    "Maya", "Blender", "Cinema 4D", "3ds Max", "ZBrush", "Substance Painter", "Substance Designer", "Marvelous Designer", "SketchUp", "Rhino",
    "AutoCAD", "Revit", "SolidWorks", "Fusion 360", "Inventor", "CATIA", "Modo", "Houdini", "Unreal Engine", "Unity",
    
    # Video Production
    "Video Production", "Video Editing", "Filmmaking", "Cinematography", "Videography", "Video Directing", "Camera Operation", "Lighting", "Sound Recording", "Sound Design",
    "Premiere Pro", "Final Cut Pro", "DaVinci Resolve", "Avid Media Composer", "Adobe Audition", "Logic Pro", "Pro Tools", "GarageBand", "Ableton Live", "FL Studio",
    "Screenwriting", "Storyboarding", "Shot Composition", "Color Grading", "Color Correction", "Post-Production", "Video Compression", "Video Encoding", "Live Streaming", 
    "Broadcast Production", "Corporate Video", "Documentary", "Short Film", "Music Video", "Commercial", "Promotional Video", "Explainer Video", "Interview Production", "Event Videography", "Drone Videography",
    
    # Audio Production
    "Audio Production", "Sound Design", "Music Production", "Voice-Over", "Audio Editing", "Audio Mixing", "Audio Mastering", "Sound Engineering", "Music Composition",
    "Podcast Production", "Foley", "ADR", "Sound Effects", "Audio Restoration", "Audio Cleanup", "Pro Tools", "Logic Pro", "Ableton Live", "FL Studio", "Cubase",
    "Studio One", "Reaper", "Reason", "Audacity", "GarageBand", "Nuendo", "Wavelab", "Audition", "Audio Hardware", "Microphone Technique",
    "Recording", "Mixing Console", "Audio Interface", "MIDI", "Virtual Instruments", "Music Theory", "Songwriting", "Music Arrangement", "Audio Programming", "Synthesis",
    
    # Marketing
    "Digital Marketing", "Content Marketing", "Social Media Marketing", "Email Marketing", "SEO", "SEM", "PPC", "Google Ads", "Facebook Ads", "Instagram Ads",
    "TikTok Ads", "LinkedIn Ads", "Twitter Ads", "Pinterest Ads", "Snapchat Ads", "YouTube Ads", "Display Advertising", "Native Advertising", "Video Marketing", "Influencer Marketing",
    "Affiliate Marketing", "Growth Hacking", "Conversion Rate Optimization", "A/B Testing", "Marketing Analytics", "Brand Strategy", "Brand Management", "Public Relations", "Media Relations", "Press Release Writing",
    "Marketing Strategy", "Marketing Plan", "Campaign Management", "Marketing Automation", "Customer Acquisition", "Customer Retention", "Lead Generation", "Lead Nurturing", "Funnel Optimization", "Market Research",
    
    # SEO & Content
    "Search Engine Optimization", "Keyword Research", "On-Page SEO", "Off-Page SEO", "Technical SEO", "Local SEO", "E-commerce SEO", "Mobile SEO", "International SEO", 
    "Voice Search Optimization", "SEO Audit", "Link Building", "Backlink Analysis", "Content Strategy", "Content Creation", "Blog Writing", "Article Writing", "Copywriting", 
    "Technical Writing", "Creative Writing", "Editing", "Proofreading", "Content Editing", "Content Optimization", "Content Promotion", "Keyword Optimization", "Meta Description Writing", 
    "Title Tag Optimization", "Image SEO", "Schema Markup", "Google Analytics", "Google Search Console", "Ahrefs", "SEMrush", "Moz", "Screaming Frog", "Ubersuggest", 
    "Rank Tracker", "SEO Competitor Analysis", "SEO Reporting",
    
    # Social Media
    "Social Media Management", "Social Media Strategy", "Facebook Management", "Instagram Management", "Twitter Management", "LinkedIn Management", "Pinterest Management", 
    "TikTok Management", "YouTube Management", "Reddit Management", "Social Media Content Creation", "Social Media Scheduling", "Social Media Analytics", "Community Management", 
    "Social Listening", "Social Media Engagement", "Social Media Advertising", "Influencer Outreach", "Hashtag Strategy", "Social Media Audit", "Facebook Ads Manager", "Instagram Ads", 
    "Twitter Ads", "LinkedIn Ads", "TikTok Ads", "Pinterest Ads", "Snapchat Ads", "Social Media Copywriting", "Social Media Video", "Social Media Graphics",
    "Hootsuite", "Buffer", "Sprout Social", "Later", "SocialBee", "Agorapulse", "Iconosquare", "Planoly", "Tailwind", "Canva",
    
    # Writing & Editing
    "Content Writing", "Copywriting", "Technical Writing", "Creative Writing", "Academic Writing", "Business Writing", "Grant Writing", "Resume Writing", "Cover Letter Writing", 
    "Ghostwriting", "Editing", "Proofreading", "Copy Editing", "Line Editing", "Developmental Editing", "Substantive Editing", "Content Editing", "Book Editing", "Manuscript Evaluation", 
    "Beta Reading", "Blog Writing", "Article Writing", "Website Content", "Product Description", "Case Study", "White Paper", "Ebook", "Newsletter", "Email Copy", "Sales Copy",
    "Landing Page Copy", "Ad Copy", "Social Media Copy", "Press Release", "Speech Writing", "Scriptwriting", "Screenplay Writing", "Dialogue Writing", "Fiction Writing", 
    "Non-Fiction Writing",
    
    # Translation & Localization
    "Translation", "Localization", "Transcreation", "Interpretation", "Subtitling", "Dubbing", "Voice-Over", "MTPE", "Transcription", "Closed Captioning",
    "English to Spanish", "English to French", "English to German", "English to Italian", "English to Portuguese", "English to Russian", "English to Chinese", 
    "English to Japanese", "English to Korean", "English to Arabic", "Spanish to English", "French to English", "German to English", "Italian to English", "Portuguese to English", 
    "Russian to English", "Chinese to English", "Japanese to English", "Korean to English", "Arabic to English", "Localization Testing", "Linguistic Quality Assurance", 
    "Cultural Adaptation", "Language Consulting", "Terminology Management", "Translation Memory", "Glossary Creation", "Style Guide Creation", "CAT Tools", "SDL Trados",
    
    # E-commerce
    "E-commerce Development", "Shopify Development", "WooCommerce Development", "Magento Development", "BigCommerce Development", "PrestaShop Development", "OpenCart Development", 
    "Ecwid Development", "Squarespace Development", "Wix Development", "E-commerce Design", "Product Page Design", "Checkout Optimization", "Shopping Cart Design", "Product Photography", 
    "Product Listing Optimization", "E-commerce SEO", "E-commerce Copywriting", "E-commerce Marketing", "Marketplace Management", "Amazon Seller Central", "eBay Store Management", 
    "Etsy Shop Management", "Walmart Marketplace", "Wish Store Management", "Mercado Libre", "Rakuten", "Taobao", "JD.com", "Flipkart", "E-commerce Strategy", "Pricing Strategy", 
    "Inventory Management", "Order Fulfillment", "Dropshipping", "Print on Demand", "Payment Gateway Integration", "Shipping Integration", "Tax Compliance", "E-commerce Analytics",
    
    # Business & Finance
    "Business Strategy", "Business Planning", "Business Analysis", "Market Research", "Competitive Analysis", "SWOT Analysis", "Business Development", "Strategic Planning", "Operations Management", "Process Optimization",
    "Financial Analysis", "Financial Modeling", "Financial Forecasting", "Budgeting", "Cost Analysis", "Profit Analysis", "Revenue Projection", "Cash Flow Management", "Investment Analysis", "Valuation",
    "Accounting", "Bookkeeping", "Tax Preparation", "Financial Reporting", "Balance Sheet", "Income Statement", "Cash Flow Statement", "Profit & Loss", "Accounts Receivable", "Accounts Payable",
    "QuickBooks", "Xero", "FreshBooks", "Wave", "MYOB", "Sage", "NetSuite", "SAP", "Microsoft Dynamics", "Zoho Books",
    
    # Project Management
    "Project Management", "Program Management", "Product Management", "Agile Project Management", "Scrum", "Kanban", "Lean", "Waterfall", "Hybrid Methodology", "Prince2",
    "Project Planning", "Project Scheduling", "Project Budgeting", "Resource Allocation", "Risk Management", "Issue Management", "Change Management", "Stakeholder Management", "Scope Management", "Quality Management",
    "JIRA", "Asana", "Trello", "Monday.com", "ClickUp", "Notion", "Basecamp", "Microsoft Project", "Smartsheet", "Wrike",
    "Project Documentation", "Requirements Gathering", "User Stories", "Acceptance Criteria", "Project Reporting", "Sprint Planning", "Daily Standup", "Sprint Review", "Sprint Retrospective", "Backlog Refinement",
    
    # Legal Services
    "Legal Writing", "Contract Drafting", "Contract Review", "Legal Research", "Legal Analysis", "Compliance", "Regulatory Compliance", "Privacy Policy", "Terms of Service", "GDPR Compliance",
    "Intellectual Property", "Trademark", "Copyright", "Patent", "Trade Secret", "Licensing Agreement", "NDA", "Non-Compete Agreement", "Employment Contract", "Service Agreement",
    "Corporate Law", "Business Formation", "LLC Formation", "Corporation Formation", "Partnership Formation", "Corporate Governance", "Bylaws", "Operating Agreement", "Business Licensing", "Business Permits",
    "Legal Consulting", "Legal Transcription", "Legal Translation", "Legal Document Preparation", "Legal Document Review", "Legal Document Management", "Legal Project Management", "Legal Case Management", "Legal Operations", "Legal Tech",
    
    # Virtual Assistance
    "Virtual Assistance", "Administrative Support", "Email Management", "Calendar Management", "Appointment Setting", "Customer Support", "Data Entry", "Transcription", "Research", "Personal Assistance",
    "Executive Assistance", "Travel Arrangement", "Event Planning", "Meeting Coordination", "Presentation Preparation", "Document Preparation", "Expense Reporting", "Invoice Processing", "CRM Management", "Contact Management",
    "Email Marketing Support", "Social Media Support", "Content Management", "Blog Management", "WordPress Management", "Shopify Store Management", "Bookkeeping Support", "Customer Service", "Order Processing", "Live Chat Support",
    "Microsoft Office", "Google Workspace", "Slack", "Zoom", "Microsoft Teams", "Salesforce", "HubSpot", "Zendesk", "Freshdesk", "Intercom",
    
    # Education & E-learning
    "Instructional Design", "Course Development", "Curriculum Development", "E-learning Development", "Learning Management System", "Educational Content Creation", "Training Material Development", "Assessment Development", "Educational Video Production", "Educational Animation",
    "Online Teaching", "Virtual Tutoring", "Language Teaching", "Math Tutoring", "Science Tutoring", "Test Preparation", "Academic Writing", "Research Assistance", "Dissertation Support", "Thesis Support",
    "Moodle", "Canvas", "Blackboard", "Articulate Storyline", "Adobe Captivate", "Lectora", "iSpring", "H5P", "Camtasia", "Screencast-O-Matic",
    "Educational Consulting", "Educational Technology", "Gamification", "Microlearning", "Mobile Learning", "Blended Learning", "Synchronous Learning", "Asynchronous Learning", "Social Learning", "Adaptive Learning",
    
    # Engineering & Architecture
    "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Chemical Engineering", "Aerospace Engineering", "Biomedical Engineering", "Environmental Engineering", "Structural Engineering", "Industrial Engineering", "Petroleum Engineering",
    "AutoCAD", "SolidWorks", "CATIA", "Revit", "ArchiCAD", "Rhino", "SketchUp", "Fusion 360", "Inventor", "Altium Designer",
    "PCB Design", "Circuit Design", "FPGA", "Microcontroller Programming", "Control Systems", "PLC Programming", "SCADA", "Embedded Systems", "IoT Development", "Robotics",
    "Architectural Design", "Interior Design", "Landscape Design", "Urban Planning", "Construction Documentation", "Building Information Modeling", "Sustainable Design", "3D Rendering", "Visualization", "Drafting",
    
    # Blockchain & Cryptocurrency
    "Blockchain Development", "Smart Contract Development", "Ethereum Development", "Solidity", "Rust for Blockchain", "Hyperledger", "Corda", "Bitcoin Development", "Cryptocurrency Trading", "Crypto Research",
    "DeFi", "NFT", "Tokenomics", "ICO", "STO", "IEO", "Cryptocurrency Exchange", "Cryptocurrency Wallet", "Web3", "dApp Development",
    "Solidity Audit", "Blockchain Security", "Consensus Mechanisms", "Mining", "Staking", "Yield Farming", "Liquidity Pools", "DAOs", "Blockchain Analytics", "Cryptocurrency Regulation",
    "Token Engineering", "Crypto Marketing", "Blockchain Consulting", "Whitepaper Writing", "Technical Paper Writing", "Blockchain Architecture", "Decentralized Storage", "Decentralized Identity", "Zero-Knowledge Proofs", "Layer 2 Solutions",
    
    # Gaming
    "Game Development", "Game Design", "Level Design", "Game Programming", "Game Art", "3D Game Art", "2D Game Art", "Game Animation", "Game Character Design", "Game Environment Design",
    "Unity", "Unreal Engine", "Godot", "GameMaker Studio", "CryEngine", "Construct", "Phaser", "PlayCanvas", "Three.js", "Babylon.js",
    "C# for Unity", "C++ for Unreal", "Blueprint Visual Scripting", "Shader Programming", "Game AI", "Game Physics", "Game Networking", "Game Sound Design", "Game Music Composition", "Game Voice Acting",
    "Mobile Game Development", "Console Game Development", "PC Game Development", "VR Game Development", "AR Game Development", "Hyper-casual Games", "Game Monetization", "Game Analytics", "Game Localization", "Game Testing",
    
    # Cybersecurity
    "Cybersecurity", "Network Security", "Information Security", "Application Security", "Cloud Security", "Web Security", "Mobile Security", "IoT Security", "Penetration Testing", "Vulnerability Assessment",
    "Security Audit", "Security Compliance", "Risk Assessment", "Threat Modeling", "Security Architecture", "Security Engineering", "Security Operations", "Security Monitoring", "Incident Response", "Digital Forensics",
    "Ethical Hacking", "Red Team", "Blue Team", "Purple Team", "Security Awareness Training", "Social Engineering", "Phishing Simulation", "Security Policy Development", "Security Documentation", "Security Training",
    "CISSP", "CEH", "CISM", "CISA", "Security+", "OSCP", "GIAC", "CCSP", "CySA+", "CASP+",
    
    # Data Entry & Admin
    "Data Entry", "Data Processing", "Data Cleansing", "Data Enrichment", "Data Mining", "Data Collection", "Web Research", "Internet Research", "Virtual Administration", "Administrative Support",
    "Microsoft Excel", "Google Sheets", "Data Formatting", "PDF Conversion", "Document Conversion", "Transcription", "Audio Transcription", "Video Transcription", "Medical Transcription", "Legal Transcription",
    "Word Processing", "Microsoft Word", "Google Docs", "PDF Editing", "Proofreading", "Copy Typing", "Form Filling", "Data Categorization", "Data Tagging", "Data Validation",
    "Spreadsheet Management", "Presentation Creation", "PowerPoint", "Google Slides", "Email Management", "Calendar Management", "Contact Management", "Database Management", "File Organization", "Document Management",
    
    # Specialized Skills
    "Quantum Computing", "Bioinformatics", "Computational Biology", "Genomics", "Proteomics", "Molecular Modeling", "Computational Chemistry", "Computational Physics", "Computational Neuroscience", "Computational Linguistics",
    "Geographic Information Systems", "Remote Sensing", "Spatial Analysis", "Cartography", "Photogrammetry", "LiDAR Processing", "GPS", "Digital Mapping", "Environmental Modeling", "Geospatial Analytics",
    "Renewable Energy", "Solar Energy", "Wind Energy", "Hydroelectric Energy", "Geothermal Energy", "Biomass Energy", "Energy Efficiency", "Energy Conservation", "Energy Management", "Energy Analysis",
    "Aerospace Design", "Aircraft Design", "Spacecraft Design", "Rocket Design", "Drone Design", "UAV Design", "Flight Simulation", "Aerodynamics", "Propulsion Systems", "Avionics",
    
    # Academic & Research
    "Academic Writing", "Research Writing", "Literature Review", "Systematic Review", "Meta-Analysis", "Academic Editing", "Scientific Editing", "Academic Translation", "Statistical Analysis", "Qualitative Analysis",
    "Quantitative Analysis", "Mixed Methods Research", "Survey Design", "Experimental Design", "Research Methodology", "Data Collection", "Data Analysis", "Research Proposal", "Grant Writing", "Funding Proposal",
    "Dissertation Writing", "Thesis Writing", "Academic Proofreading", "Bibliography Creation", "Citation Management", "EndNote", "Zotero", "Mendeley", "Reference Management", "Academic Formatting",
    "APA Style", "MLA Style", "Chicago Style", "Harvard Style", "Vancouver Style", "IEEE Style", "OSCOLA", "Bluebook", "Research Presentation", "Scientific Poster",
    
    # Soft Skills
    "Communication", "Leadership", "Teamwork", "Problem-Solving", "Critical Thinking", "Creativity", "Time Management", "Organization", "Project Management", "Conflict Resolution",
    "Negotiation", "Interpersonal Skills", "Presentation Skills", "Public Speaking", "Customer Service", "Client Management", "Relationship Building", "Networking", "Emotional Intelligence", "Cultural Awareness",
    "Adaptability", "Flexibility", "Resilience", "Attention to Detail", "Analytical Thinking", "Strategic Thinking", "Innovation", "Initiative", "Self-Motivation", "Responsibility",
    "Decision Making", "Work Ethic", "Stress Management", "Multitasking", "Prioritization", "Active Listening", "Feedback Provision", "Coaching", "Mentoring", "Training",
    
    # Languages
    "English", "Spanish", "Mandarin Chinese", "Hindi", "Arabic", "Portuguese", "Bengali", "Russian", "Japanese", "Punjabi",
    "German", "French", "Italian", "Korean", "Turkish", "Vietnamese", "Tamil", "Urdu", "Polish", "Ukrainian",
    "Dutch", "Romanian", "Greek", "Czech", "Swedish", "Hungarian", "Finnish", "Norwegian", "Danish", "Slovak",
    "Thai", "Indonesian", "Malay", "Tagalog", "Swahili", "Hebrew", "Persian", "Hausa", "Yoruba", "Igbo",
    
    # Industry Knowledge
    "Finance", "Banking", "Insurance", "Real Estate", "Retail", "E-commerce", "Manufacturing", "Healthcare", "Pharmaceuticals", "Biotechnology",
    "Telecommunications", "Media", "Entertainment", "Advertising", "Marketing", "Public Relations", "Education", "Government", "Non-profit", "Legal",
    "Hospitality", "Tourism", "Food & Beverage", "Transportation", "Logistics", "Supply Chain", "Energy", "Oil & Gas", "Mining", "Construction",
    "Agriculture", "Forestry", "Fisheries", "Environmental", "Renewable Energy", "Automotive", "Aviation", "Aerospace", "Defense", "Space",
    
    # Additional Framework and Technology Skills
    "Spring Framework", "Hibernate", "JPA", "Jakarta EE", "Micronaut", "Quarkus", "Vert.x", "Play Framework", "Akka", "gRPC",
    "Apache Kafka", "RabbitMQ", "ActiveMQ", "ZeroMQ", "NATS", "Apache Pulsar", "Apache Camel", "Apache ServiceMix", "Apache Flink", "Apache Beam",
    ".NET Framework", ".NET Core", "ASP.NET MVC", "ASP.NET Web API", "Entity Framework", "Blazor", "SignalR", "WCF", "Windows Forms", "WPF",
    "Xamarin.Forms", "MAUI", "Mono", "Avalonia", "Uno Platform", "DotVVM", "NancyFX", "ServiceStack", "NServiceBus", "Hangfire", "Quartz.NET",
    "Dapper", "AutoMapper", "FluentValidation", "MediatR", "Serilog", "NLog", "Log4Net", "Polly", "Moq",
    "xUnit", "NUnit", "MSTest", "SpecFlow", "FluentAssertions", "RestSharp", "HttpClientFactory", "IdentityServer4", "OpenIddict", "Duende IdentityServer", "ASP.NET Identity",
    "OAuth2", "OpenID Connect", "SAML", "JWT", "Claims-based Authentication", "ASP.NET Core Identity", "ASP.NET Core Security", "OWIN", "Katana",
    "ASP.NET Core Middleware", "ASP.NET Core MVC", "ASP.NET Core Razor Pages", "ASP.NET Core Blazor", "ASP.NET Core Web API", "ASP.NET Core SignalR",
]