from pathlib import Path
import os
from django.utils.translation import gettext_lazy as _
import dj_database_url

# Define base directory path for the project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key for Django project; keep it confidential in production.
SECRET_KEY = "django-insecure-y9vjmoy_i9&x-5!dq7w-dq+fsts@dsmut9(yp)$)lyg%rd43_x"

# Debug mode setting; should be False in production.
DEBUG = False

# List of allowed hostnames for the application.
ALLOWED_HOSTS = ['*', 'hiremenepal.tech', 'www.hiremenepal.tech']

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
    "contract",
    "translation", 
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
"""
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
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hiremedb',  # RDS database name
        'USER': 'hireme_user',
        'PASSWORD': 'HireMeDatabase_2060',
        'HOST': 'hiremedb.c9qyc8uss9wk.ap-south-1.rds.amazonaws.com',  # RDS endpoint
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

# Contact details
COMPANY_NAME = 'HireMe Nepal Pvt. Ltd.'
LOCATION = 'Baneshwor, Kathmandu, Nepal'
CONTACT_EMAIL = 'bishalbhattarai472@gmail.com'
SUPPORT_EMAIL = 'support@hiremeapp.com'
CONTACT_PHONE = '+977 9860000000'
CONTACT_PHONE_2 = '+977 9860000001'
ADMIN_EMAIL = 'bishalbhattarai472@gmail.com'

# Form upload settings
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

# Reserved usernames that users can't register with
RESERVED_USERNAMES = {
    "admin", "administrator", "root", "superuser", "sysadmin", 
    "moderator", "support", "helpdesk", "service", "client",
    "freelancer", "user", "guest", "owner", "manager",
    "staff", "team", "developer", "dev", "test",
    "system", "operator", "security", "bot", "official"
}

category_skills_map = {
    "Web Development": [
        # Core Technologies
        "HTML", "HTML5", "CSS", "CSS3", "SASS", "SCSS", "Less", "JavaScript", "TypeScript", "ES6+", 
        "DOM Manipulation", "JSON", "AJAX", "XML", "HTTP/HTTPS", "WebSockets", "Web Workers", "IndexedDB",
        "LocalStorage", "SessionStorage", "Cookies", "JWT", "OAuth", "CORS", "REST", "SOAP",
        
        # Frontend Frameworks & Libraries
        "React.js", "Angular", "Vue.js", "Svelte", "Next.js", "Nuxt.js", "Gatsby", "Astro", "Solid.js", 
        "Alpine.js", "Ember.js", "Stimulus", "Redux", "MobX", "Zustand", "Context API", "React Router", 
        "Axios", "Fetch API", "jQuery", "D3.js", "Three.js", "Chart.js", "Highcharts", "WebGL", 
        "Canvas API", "SVG", "Storybook", "StyleX", "Chakra UI", "Material UI", "Tailwind CSS", 
        "Bootstrap", "Bulma", "Foundation", "Ant Design", "Semantic UI", "Styled Components", 
        "Emotion", "CSS Modules", "CSS-in-JS", "Framer Motion", "GSAP", "Motion One", "React Spring",
        
        # Backend Frameworks & Technologies
        "Node.js", "Express.js", "Koa.js", "Fastify", "NestJS", "Django", "Flask", "FastAPI", 
        "Ruby on Rails", "Laravel", "Symfony", "CodeIgniter", "CakePHP", "Spring Boot", "ASP.NET Core",
        "Phoenix (Elixir)", "Play Framework", "Gin (Go)", "Echo (Go)", "Fiber (Go)", "Actix (Rust)",
        "Rocket (Rust)", "Axum (Rust)", "Phalcon", "Slim", "Lumen", "AdonisJS", "Strapi", "Meteor",
        "LoopBack", "Hapi.js", "Sails.js", "Feathers.js", "Serverless Framework",
        
        # Databases & Data Storage
        "MySQL", "PostgreSQL", "MariaDB", "SQLite", "SQL Server", "Oracle Database", "MongoDB", 
        "Firebase", "Firestore", "Supabase", "DynamoDB", "Cassandra", "Redis", "Elasticsearch", 
        "Neo4j", "CouchDB", "RethinkDB", "InfluxDB", "TimescaleDB", "Prisma", "Sequelize", 
        "Mongoose", "TypeORM", "Knex.js", "SQLAlchemy", "Hibernate", "Entity Framework",
        
        # CMS & E-commerce
        "WordPress", "Shopify", "WooCommerce", "Magento", "Drupal", "Joomla", "Ghost", "Contentful", 
        "Sanity.io", "Webflow", "Wix", "Squarespace", "BigCommerce", "PrestaShop", "OpenCart", 
        "Salesforce Commerce Cloud", "Sitecore", "AEM", "Contentstack", "Strapi", "Payload CMS", 
        "Kentico", "Umbraco", "Craft CMS", "ExpressionEngine",
        
        # DevOps & Deployment
        "Git", "GitHub", "GitLab", "Bitbucket", "CI/CD", "Jenkins", "Travis CI", "CircleCI", 
        "GitHub Actions", "AWS", "Azure", "Google Cloud", "DigitalOcean", "Heroku", "Netlify", 
        "Vercel", "Docker", "Kubernetes", "Terraform", "CloudFormation", "Ansible", "Chef", 
        "Puppet", "Prometheus", "Grafana", "Nginx", "Apache", "IIS", "Cloudflare", "Cloudinary",
        
        # Testing & Quality Assurance
        "Jest", "Mocha", "Chai", "Jasmine", "Karma", "Cypress", "Selenium", "Puppeteer", "Playwright", 
        "TestCafe", "WebdriverIO", "Postman", "SoapUI", "JUnit", "PyTest", "PHPUnit", "RSpec", 
        "TestNG", "Cucumber", "BDD", "TDD", "E2E Testing", "Unit Testing", "Integration Testing", 
        "Regression Testing", "Load Testing", "Performance Testing", "A/B Testing",
        
        # Web Performance & Optimization
        "Webpack", "Vite", "Rollup", "Parcel", "Gulp", "Grunt", "Babel", "ESBuild", "SWC", "PostCSS", 
        "Critical CSS", "Lazy Loading", "Code Splitting", "Tree Shaking", "Minification", "Compression", 
        "Caching Strategies", "CDN Implementation", "Image Optimization", "Responsive Design", 
        "Mobile-First Design", "Progressive Enhancement", "Graceful Degradation", "Web Vitals Optimization",
        "Lighthouse Optimization", "Browser Compatibility", "Cross-Browser Testing",
        
        # Web 3.0 & Emerging Technologies
        "PWA Development", "Service Workers", "Web3.js", "Ethers.js", "IPFS", "Smart Contract Integration", 
        "dApp Development", "Web Assembly", "WebRTC", "Web Audio API", "Web Speech API", "WebVR", 
        "WebXR", "AMP", "Jamstack Architecture", "Headless Architecture", "Micro Frontends",
        "Server Components", "Edge Computing", "WebGPU", "Web NFC", "Web Bluetooth", "WebUSB",
        
        # Accessibility & Internationalization
        "Web Accessibility (WCAG)", "ARIA", "Screen Reader Optimization", "Keyboard Navigation", 
        "Color Contrast", "Focus Management", "Internationalization (i18n)", "Localization (l10n)", 
        "RTL Support", "Multi-language Support"
    ],
    
    "Mobile App Development": [
        # Cross-Platform Development
        "React Native", "Flutter", "Xamarin", "Ionic", "Capacitor", "NativeScript", "PhoneGap", 
        "Cordova", "Kotlin Multiplatform Mobile", "Unity for Mobile", "Expo", "PWA for Mobile",
        "Framework7", "Quasar", "Titanium", "React Native Paper", "React Native Elements",
        "React Native Navigation", "React Native Reanimated", "React Native Gesture Handler",
        "MobX with React Native", "Redux with React Native", "Context API with React Native",
        "Yoga Layout", "Native Modules", "CodePush", "Fastlane with React Native", "App Center",
        "Flutter Bloc", "Flutter Provider", "Flutter Riverpod", "GetX", "Flutter Hooks",
        "Flutter Animations", "Flutter Navigation", "Flutter Form Validation", "Flutter State Management",
        
        # iOS Development
        "Swift", "Objective-C", "SwiftUI", "UIKit", "Core Data", "Core Animation", "Core Graphics", 
        "Core ML", "ARKit", "SpriteKit", "SceneKit", "Metal", "HealthKit", "HomeKit", "MapKit", 
        "CloudKit", "WatchKit", "Push Notifications", "In-App Purchases", "TestFlight", "XCTest", 
        "Instruments", "Grand Central Dispatch", "Operation Queues", "Combine Framework", "Swift Package Manager",
        "Xcode", "Interface Builder", "Auto Layout", "Size Classes", "App Extensions", "Universal Links",
        "Keychain", "UserDefaults", "Storyboards", "XIBs", "Core Location", "Core Motion", "AVFoundation",
        "Core Bluetooth", "Core NFC", "Core Image", "Vision Framework", "Speech Recognition", "CallKit",
        "StoreKit", "Apple Pay", "WidgetKit", "App Clips",
        
        # Android Development
        "Kotlin", "Java for Android", "Jetpack Compose", "Android SDK", "Android NDK", "Android Studio", 
        "XML Layouts", "Material Design Components", "Constraint Layout", "Recycler View", "Android Jetpack", 
        "Room Database", "LiveData", "ViewModel", "Data Binding", "WorkManager", "Navigation Component", 
        "Paging Library", "Dagger/Hilt", "Koin", "RxJava", "RxKotlin", "Coroutines", "Flow", "Retrofit", 
        "OkHttp", "Glide", "Picasso", "Coil", "Firebase for Android", "Google Play Services", 
        "Google Maps SDK", "Location Services", "Notifications", "Broadcasts", "Services", "Content Providers",
        "Activity Lifecycle", "Fragment Lifecycle", "MVVM Architecture", "MVP Architecture", "Clean Architecture",
        "Espresso Testing", "JUnit for Android", "Mockito", "Android Debug Bridge (ADB)", "ProGuard",
        "R8 Optimizer", "APK Analysis", "Google Play Console", "In-App Reviews", "In-App Updates",
        
        # Mobile UI/UX Design
        "Mobile UI Patterns", "Gesture-Based Interfaces", "Mobile Navigation Patterns", "Bottom Sheets", 
        "Bottom Navigation", "Tab Bars", "Floating Action Buttons", "Pull to Refresh", "Infinite Scrolling", 
        "Skeleton Screens", "Microinteractions", "Action Sheets", "Form Design for Mobile", 
        "Onboarding Flows", "Permission Requests", "Mobile Typography", "Mobile Color Theory",
        "Mobile-First Design", "Responsive Design for Mobile", "Adaptive Design",
        
        # Mobile App Testing & Quality
        "Mobile App Testing", "Device Fragmentation Testing", "Cross-Device Testing", "Network Condition Testing", 
        "Battery Consumption Testing", "Memory Usage Optimization", "Mobile Performance Testing", 
        "Mobile Security Testing", "Biometric Authentication", "Offline Functionality", "Sync Mechanisms",
        "Crash Analytics", "BrowserStack", "Sauce Labs", "AWS Device Farm", "Firebase Test Lab", "Appium",
        "Calabash", "Detox", "UI Automator", "XCUITest",
        
        # Mobile App Backend & Services
        "Mobile Backend as a Service (MBaaS)", "Firebase", "AWS Amplify", "App Center", "Parse Server", 
        "Realm Database", "SQLite", "Push Notification Services", "Deep Linking", "App Indexing", 
        "Mobile Analytics", "Crash Reporting", "Mobile App Security", "Mobile Authentication", 
        "OAuth for Mobile", "JWT for Mobile", "Mobile API Integration", "GraphQL for Mobile", 
        
        # App Store & Distribution
        "App Store Optimization (ASO)", "Google Play Store Optimization", "App Store Screenshots", 
        "App Store Description", "App Ratings & Reviews", "App Store Guidelines", "Google Play Policies", 
        "App Release Management", "Beta Testing", "Alpha Testing", "Staged Rollouts", "Feature Flags",
        "App Versioning", "App Updates Strategy", "App Localization", "App Internationalization",
        
        # Advanced & Emerging Mobile Technologies
        "AR for Mobile", "VR for Mobile", "Mobile Machine Learning", "On-Device ML", "Mobile IoT Integration", 
        "Wearable App Development", "Apple Watch Apps", "Android Wear OS", "Mobile Blockchain Integration",
        "App Clips", "Instant Apps", "Mini Programs", "Super Apps", "Mobile Edge Computing",
        "Mobile Voice Interfaces", "Mobile Biometrics", "Foldable Device Support", 
        "Multi-Window Support", "Mobile Dark Mode", "Dynamic Theming"
    ],
    
    "UI/UX Design": [
        # Design Tools & Software
        "Figma", "Adobe XD", "Sketch", "InVision", "Framer", "Axure RP", "Balsamiq", "Marvel", 
        "Principle", "ProtoPie", "Adobe Illustrator", "Adobe Photoshop", "Adobe After Effects", 
        "Webflow", "Zeplin", "Abstract", "Avocode", "Vectornator", "Lunacy", "UXPin", "Penpot",
        "Mockplus", "Justinmind", "Origami Studio", "Maze", "Optimal Workshop", "Hotjar", "Lookback", 
        "Miro", "Figjam", "FlowMapp", "Whimsical", "Adobe Creative Cloud", "Affinity Designer",
        
        # UX Research & Strategy
        "User Research", "Competitive Analysis", "User Personas", "User Journeys", "User Scenarios", 
        "Experience Maps", "Empathy Maps", "Customer Journey Mapping", "Service Blueprints", 
        "Stakeholder Interviews", "User Interviews", "Contextual Inquiry", "Field Studies", 
        "Ethnographic Research", "Diary Studies", "Card Sorting", "Tree Testing", "First Click Testing", 
        "Preference Testing", "5-Second Tests", "A/B Testing", "Multivariate Testing", "User Surveys", 
        "Focus Groups", "Usability Benchmarking", "Heuristic Evaluation", "Cognitive Walkthroughs", 
        "Expert Reviews", "SWOT Analysis", "Jobs To Be Done (JTBD)", "Feature Prioritization", 
        "Design Sprints", "Design Thinking", "Lean UX", "Agile UX", "Google HEART Framework",
        "Kano Model", "MoSCoW Method", "Product Discovery", "UX Strategy", "North Star Metrics",
        
        # Information Architecture & Content Strategy
        "Information Architecture", "Site Mapping", "User Flows", "Task Flows", "Content Auditing", 
        "Content Strategy", "Content Modeling", "Taxonomy Development", "Navigation Design", 
        "Search Experience Design", "Microcopy", "UX Writing", "Content Hierarchy", "Mental Models", 
        "Cognitive Load Theory", "Content Governance", "Content Management Systems", "Content Templates", 
        "Labeling Systems", "Content Personalization", "Content Localization", "Content Accessibility",
        "Holistic Content Strategy", "Adaptive Content", "Progressive Disclosure", "Information Scent",
        "Content First Design", "Readability Analysis", "Voice & Tone Guidelines",
        
        # Wireframing & Prototyping
        "Wireframing", "Low-Fidelity Prototyping", "Medium-Fidelity Prototyping", "High-Fidelity Prototyping", 
        "Interactive Prototyping", "Paper Prototyping", "Digital Prototyping", "Rapid Prototyping", 
        "Clickable Prototypes", "Prototype Testing", "Animation Prototyping", "Flow Diagrams", 
        "Storyboarding", "Scenario Mapping", "Component Libraries", "Design Systems", "Responsive Prototyping",
        "Micro-interactions Prototyping", "Voice UI Prototyping", "Gesture Prototyping",
        
        # Visual Design & UI
        "Visual Design", "UI Design", "Graphic Design", "Typography", "Color Theory", "Layout Design", 
        "Grid Systems", "Composition", "Visual Hierarchy", "Icon Design", "Logo Design", "Brand Identity", 
        "Style Guides", "Design Tokens", "Design Systems", "Component Libraries", "Pattern Libraries", 
        "Atomic Design", "Responsive Design", "Mobile-First Design", "Adaptive Design", 
        "Fluid Design", "Material Design", "Apple Human Interface Guidelines", "Fluent Design", 
        "Illustration for UI", "Photography for UI", "Animation in UI", "Microinteractions", 
        "Motion Design", "Dark Mode Design", "Variable Fonts", "Data Visualization", "Dashboard Design",
        "Form Design", "Button Design", "Card Design", "Modal Design", "Loader Design", "Empty States Design",
        "Error States Design", "Success States Design", "Skeleton Screens", "Toast Notifications",
        
        # Interaction Design
        "Interaction Design", "Microinteractions", "Gesture Design", "Animation Design", "Motion Design", 
        "Transitions", "State Changes", "Affordances", "Feedback Design", "Error Prevention", 
        "Forgiving Formats", "Progressive Enhancement", "Meaningful Animation", "Interface Timing", 
        "Loading States", "Input Methods", "Voice Interfaces", "Touch Interfaces", "Pointer Interfaces", 
        "Multi-modal Interfaces", "Haptic Feedback Design", "Sound Design for UI", "Dialogue Design",
        "Drag and Drop Interactions", "Scrolling Behaviors", "Pagination Design", "Infinite Scroll Design",
        "Pull to Refresh", "Swipe Actions", "Pinch to Zoom", "Double Tap", "Long Press",
        
        # Design Systems & Documentation
        "Design Systems", "Design Tokens", "Component Libraries", "Style Guides", "Pattern Libraries", 
        "Atomic Design", "Design Documentation", "Design Versioning", "Design Collaboration", 
        "Design Handoff", "Developer Handoff", "Code and Design Sync", "Component Specifications", 
        "Accessibility Documentation", "Design QA", "Design Review", "Design Critiques",
        "DesignOps", "Design Governance", "Design at Scale", "Design System Analytics",
        
        # Accessibility & Inclusive Design
        "Accessibility Design", "WCAG Guidelines", "Inclusive Design", "Universal Design", 
        "Screen Reader Compatibility", "Keyboard Navigation", "Color Contrast", "Font Accessibility", 
        "Alternative Text", "ARIA Labels", "Focus States", "Cognitive Accessibility", "Readability", 
        "Color Blindness Considerations", "Neurodiversity Considerations", "Global Accessibility Awareness", 
        "Mobile Accessibility", "Voice UI Accessibility", "Accessible Animation", "Accessibility Testing",
        "Assistive Technology Compatibility", "Motor Impairment Considerations", "Hearing Impairment Considerations",
        "Visual Impairment Considerations", "Situational Disabilities", "Accessibility Audits",
        
        # Specialized UI/UX Areas
        "Mobile UI/UX", "Web UI/UX", "Tablet UI/UX", "Desktop UI/UX", "Responsive UI/UX", 
        "E-commerce UX", "SaaS UI/UX", "Enterprise UX", "Dashboard UX", "Data Visualization UX", 
        "Healthcare UX", "Fintech UX", "Educational UX", "Game UX", "AR/VR UX", "Voice UI/UX", 
        "Chat UI/UX", "AI Interface Design", "IoT Interface Design", "Wearable UI/UX", 
        "Automotive UI/UX", "Kiosk UI/UX", "Command Line UX", "Form UX", "Conversion-Centered Design",
        "Cross-Cultural Design", "Cross-Platform Design", "Design for Children", "Design for Elderly",
        "Design for Low-Literacy Users"
    ],

    "Graphic Design": [
        # Design Software & Tools
        "Adobe Photoshop", "Adobe Illustrator", "Adobe InDesign", "Adobe XD", "Adobe Lightroom", 
        "Adobe Dimension", "Adobe Fresco", "Affinity Designer", "Affinity Photo", "Affinity Publisher", 
        "Sketch", "Figma", "CorelDRAW", "GIMP", "Inkscape", "Lunacy", "Gravit Designer", "Procreate", 
        "Clip Studio Paint", "Canva", "Pixlr", "Krita", "Adobe Creative Cloud", "Blender for Graphics", 
        "Paint Tool SAI", "Aseprite", "Adobe Animate", "Adobe After Effects", "Cinema 4D", "Vectornator",
        "Pixelmator", "Penpot", "Adobe Express", "Photoscape X", "Design Space", "Crello", "PicMonkey",
        
        # Visual Design Fundamentals
        "Color Theory", "Typography", "Composition", "Layout Design", "Visual Hierarchy", "Grid Systems", 
        "Gestalt Principles", "Balance", "Contrast", "Alignment", "Repetition", "Proximity", "White Space", 
        "Golden Ratio", "Rule of Thirds", "Symmetry", "Asymmetry", "Form", "Shape", "Line", "Texture", 
        "Pattern Design", "Visual Weight", "Scale", "Proportion", "Rhythm", "Unity", "Color Psychology", 
        "Color Schemes", "Color Harmonies", "RGB Color Mode", "CMYK Color Mode", "Pantone Matching System",
        "HSL Color Mode", "Color Calibration", "Color Management", "Type Anatomy", "Type Classification",
        "Kerning", "Tracking", "Leading", "Widows and Orphans", "Ligatures",
        
        # Branding & Identity Design
        "Logo Design", "Brand Identity Design", "Corporate Identity", "Visual Identity Systems", 
        "Brand Guidelines", "Style Guides", "Brand Positioning", "Brand Strategy", "Brand Voice", 
        "Brand Storytelling", "Rebranding", "Brand Architecture", "Brand Audits", "Logo Animation", 
        "Brand Asset Management", "Brand Extensions", "Logo Variations", "Responsive Logos", 
        "Brandmarks", "Wordmarks", "Lettermarks", "Emblems", "Mascot Design", "Brand Color Palettes", 
        "Brand Typography", "Brand Imagery", "Brand Applications", "Brand Collateral", "Stationery Design",
        "Business Card Design", "Letterhead Design", "Envelope Design", "Merchandise Design",
        "Brand Book Creation", "Co-branding", "Sub-branding", "Brand Equity Analysis",
        
        # Print Design
        "Editorial Design", "Publication Design", "Magazine Layout", "Newspaper Layout", "Book Design", 
        "Book Cover Design", "Print Production", "Print Specifications", "Print Finishes", "Binding Types", 
        "Paper Selection", "Paper Weight", "Paper Finish", "Prepress", "Pagination", "Imposition", 
        "Bleed Setup", "Crop Marks", "Registration Marks", "CMYK Color Separation", "Spot Colors", 
        "Overprinting", "Trapping", "Die Cutting", "Embossing", "Foil Stamping", "Varnishes", 
        "Specialty Printing", "Large Format Printing", "Digital Printing", "Offset Printing", 
        "Screen Printing", "Letterpress", "Risograph", "Flexography", "Gravure Printing",
        "Print-Ready Files", "Print Proofing", "Color Matching", "Print Quality Control",
        
        # Packaging Design
        "Package Design", "Product Packaging", "Structural Packaging", "Sustainable Packaging", 
        "Retail Packaging", "Food Packaging", "Beverage Packaging", "Cosmetic Packaging", 
        "Pharmaceutical Packaging", "Luxury Packaging", "Eco-Friendly Packaging", "Packaging Prototypes", 
        "Dieline Creation", "Packaging Materials", "Unboxing Experience", "Shelf Impact", 
        "Packaging Labels", "Packaging Inserts", "Carton Design", "Bottle Design", "Can Design", 
        "Tube Design", "Pouch Design", "Box Design", "Bag Design", "Sleeve Design", "Hang Tag Design",
        "Point of Purchase Design", "Child-Resistant Packaging", "Tamper-Evident Packaging",
        "Limited Edition Packaging", "Seasonal Packaging", "Gift Packaging",
        
        # Marketing & Advertising Design
        "Advertising Design", "Campaign Design", "Billboard Design", "Poster Design", "Flyer Design", 
        "Brochure Design", "Catalog Design", "Direct Mail Design", "Point of Sale Design", 
        "Trade Show Graphics", "Exhibition Design", "Retail Graphics", "Signage Design", 
        "Banner Design", "Print Ads", "Digital Ads", "Social Media Graphics", "Email Graphics", 
        "Infographic Design", "Presentation Design", "PowerPoint Design", "Keynote Design", 
        "Google Slides Design", "Media Kit Design", "Sales Deck Design", "Pitch Deck Design",
        "Event Graphics", "Promotional Materials", "Gift Card Design", "Loyalty Card Design",
        "Menu Design", "Promotional Merchandise Design", "Vehicle Wraps", "Environmental Graphics",
        
        # Digital & Web Design
        "Web Graphics", "UI Design", "App Design", "Icon Design", "Web Banner Design", 
        "Social Media Post Design", "Social Media Profile Design", "Digital Ad Design", 
        "Email Newsletter Design", "Digital Publication Design", "E-book Design", "Blog Graphics", 
        "Thumbnail Design", "Favicon Design", "Avatar Design", "GIF Creation", "Web Animation", 
        "Responsive Design Graphics", "Landing Page Design", "Digital Product Design", 
        "App Store Graphics", "Website Header Design", "Digital Banners", "Facebook Cover Design", 
        "Twitter Header Design", "LinkedIn Background Design", "YouTube Thumbnail Design", 
        "YouTube Channel Art", "Instagram Story Design", "Instagram Post Design", "Instagram Grid Design",
        "Instagram Highlight Cover Design", "TikTok Cover Design", "Twitch Overlay Design",
        "Discord Server Graphics", "Podcast Cover Art",
        
        # Illustration & Drawing
        "Digital Illustration", "Vector Illustration", "Raster Illustration", "Character Design", 
        "Environment Design", "Concept Art", "Storyboarding", "Comic Art", "Children's Book Illustration", 
        "Editorial Illustration", "Fashion Illustration", "Technical Illustration", "Medical Illustration", 
        "Scientific Illustration", "Architectural Illustration", "Product Illustration", "Food Illustration", 
        "Botanical Illustration", "Wildlife Illustration", "Portrait Illustration", "Caricature", 
        "Cartoon Style", "Isometric Illustration", "Flat Illustration", "Line Art", "Pixel Art", 
        "Watercolor Illustration", "Gouache Illustration", "Pen and Ink Illustration", "Pencil Illustration",
        "Digital Painting", "Background Illustration", "Spot Illustration", "Decorative Illustration",
        "Fantasy Illustration", "Sci-Fi Illustration", "Instructional Illustration",
        
        # Photo Editing & Manipulation
        "Photo Retouching", "Photo Manipulation", "Photo Compositing", "Image Restoration", 
        "Color Correction", "Color Grading", "Beauty Retouching", "Product Retouching", 
        "Background Removal", "Image Masking", "Photo Collage", "HDR Processing", "Frequency Separation", 
        "Dodge and Burn", "Liquify", "Clone Stamping", "Healing", "Content-Aware Fill", 
        "Image Resizing", "Image Optimization", "Batch Processing", "Raw Processing", "Digital Makeup", 
        "Body Reshaping", "Skin Smoothing", "Eye Enhancement", "Teeth Whitening", "Hair Retouching",
        "Shadow Creation", "Reflection Creation", "Lighting Adjustment", "Image Sharpening",
        "Noise Reduction", "Grain Addition", "Vintage Photo Effects", "Black and White Conversion",
        
        # Motion Graphics & Animation
        "2D Animation", "Motion Graphics", "Kinetic Typography", "Logo Animation", "Icon Animation", 
        "Character Animation", "Explainer Video Animation", "UI Animation", "Social Media Animation", 
        "GIF Creation", "Animated Banners", "Animated Infographics", "Title Sequences", 
        "Lower Thirds", "Animated Transitions", "Video Editing", "Animated Illustrations", 
        "Storyboarding for Animation", "After Effects Animation", "Premiere Pro Editing", 
        "Frame-by-Frame Animation", "Rigging", "Tweening", "Easing", "Keyframing", "Timeline Animation",
        "Path Animation", "Shape Animation", "Mask Animation", "Text Animation", "Particle Effects",
        "Liquid Animation", "Stop Motion Animation", "Animated Explainers", "Loop Animation",
        "Animated Stickers", "Animated Emojis", "Animated Avatars"
    ],

    "Content Writing": [        
        # Industry-Specific Writing
        "Medical Writing", "Legal Writing", "Financial Writing", "Technical Writing", "Scientific Writing", 
        "Healthcare Content", "B2B Writing", "B2C Writing", "SaaS Content", "Fintech Content", 
        "Blockchain Content", "Cryptocurrency Content", "Real Estate Content", "Travel Writing", 
        "Food Writing", "Fashion Writing", "Beauty Writing", "Technology Writing", "Gaming Content", 
        "Sports Writing", "Entertainment Writing", "Education Content", "E-learning Content", 
        "Environmental Writing", "Sustainability Content", "Nonprofit Content", "Lifestyle Content", 
        "Wellness Content", "Fitness Content", "Parenting Content", "Pet Content", "Automotive Content",
        "Manufacturing Content", "Industrial Content", "Construction Content", "Agriculture Content",
        "Energy Sector Content", "Insurance Content", "Banking Content", "Investment Content",
        "Human Resources Content", "Recruiting Content", "Marketing Content", "Sales Content",
        "Public Relations Content", "Crisis Communication Content", "Internal Communications",
        "Executive Communications", "Political Writing", "Regulatory Content", "Compliance Content",
        
        # Content Formats & Specializations
        "Listicle Creation", "How-to Guide Writing", "Tutorial Writing", "FAQ Writing", "Q&A Content", 
        "Roundup Post Creation", "Ultimate Guide Creation", "Comparison Content", "Interview Content", 
        "Expert Roundup Content", "Thought Leadership Content", "Opinion Piece Writing", "Editorial Writing", 
        "News Article Writing", "Feature Article Writing", "Review Writing", "Product Review Writing", 
        "Service Review Writing", "Book Review Writing", "Movie Review Writing", "Testimonial Writing", 
        "Quote Collection", "Statistic Roundup", "Data Visualization Content", "Infographic Content", 
        "Chart Explanation", "Graph Interpretation", "Timeline Content", "History Content", "Biography Writing",
        "Microcopy", "Push Notification Copy", "Chatbot Script Writing", "Podcast Show Notes",
        "Video Script Writing", "Webinar Content", "Course Content", "Interactive Content",
        "Quiz Content", "Poll Content", "Survey Content", "Contest Content", "Resource List Creation",
        "Checklist Creation", "Template Creation", "Worksheet Creation", "Workbook Creation",
        
        # Writing Tools & Technologies
        "Microsoft Word", "Google Docs", "Grammarly", "Hemingway Editor", "ProWritingAid", 
        "WordPress", "Content Management Systems", "Markdown", "HTML Basics", "SEO Tools", 
        "Keyword Research Tools", "Google Analytics", "Google Search Console", "Ahrefs", 
        "SEMrush", "Moz", "Clearscope", "MarketMuse", "Surfer SEO", "Frase", "Content Scheduling Tools", 
        "Editorial Calendar Software", "Project Management Tools", "Trello for Content", "Asana for Content", 
        "ClickUp for Content", "Monday.com", "Content Brief Creation", "AI Writing Tools", "GPT Knowledge",
        "Jasper", "Copy.ai", "Notion", "Evernote", "Scrivener", "Final Draft", "Screenwriting Software",
        "Citation Software", "Plagiarism Checkers", "Readability Analysis Tools", "Tone Analysis Tools",
        "Content Performance Tools", "A/B Testing Tools", "Heat Map Tools", "Content Collaboration Tools",
        
        # Content Strategy & Management
        "Content Strategy Development", "Content Planning", "Editorial Calendar Management", 
        "Content Workflow Management", "Content Team Management", "Freelance Writer Management", 
        "Content Quality Control", "Content Style Guide Creation", "Brand Voice Development", 
        "Tone of Voice Guidelines", "Content Brief Creation", "Content Template Creation", 
        "Content Production Process", "Content Review Process", "Content Approval Workflow", 
        "Content Performance Tracking", "Content Analytics Reporting", "Content ROI Measurement", 
        "Content Effectiveness Analysis", "Content Engagement Analysis", "Content Update Strategy",
        "Content Retirement Planning", "Content Governance", "Content Taxonomy", "Content Categorization",
        "Content Tagging", "Content Management System (CMS) Administration", "Digital Asset Management",
        "Content Localization Management", "Global Content Strategy", "Regional Content Adaptation",
        "Multi-channel Content Strategy", "Content Repurposing Strategy", "Content Migration Planning"
    ],
    
    "Digital Marketing": [
        # Search Engine Marketing & Optimization
        "SEO Strategy", "On-Page SEO", "Off-Page SEO", "Technical SEO", "Local SEO", "Mobile SEO", 
        "International SEO", "E-commerce SEO", "Voice Search SEO", "Video SEO", "Image SEO", 
        "Keyword Research", "Competitive Analysis", "Link Building", "Content Optimization", 
        "Semantic SEO", "Featured Snippet Optimization", "SEO Audit", "SEO Reporting", "Website Structure Optimization", 
        "URL Structure Optimization", "Site Migration SEO", "Penalty Recovery", "Rank Tracking", 
        "Google Algorithm Updates Knowledge", "Search Console Management", "Bing Webmaster Tools", 
        "SEM Strategy", "Google Ads", "Bing Ads", "Yahoo Gemini", "Display Advertising", 
        "Remarketing/Retargeting", "Shopping Ads", "PPC Management", "Ad Copywriting", "Ad Testing", 
        "Bid Management", "Quality Score Optimization", "Landing Page Optimization", "Conversion Rate Optimization",
        "A/B Testing", "Google Tag Manager", "Structured Data/Schema Markup", "SERP Analysis",
        "Core Web Vitals Optimization", "Crawlability Optimization", "Indexability Assessment",
        "HTTP Status Codes", "Robots.txt Configuration", "XML Sitemap Creation", "Hreflang Implementation",
        "Canonical Tag Implementation", "Mobile-First Indexing", "Page Speed Optimization",
        
        # Social Media Marketing
        "Social Media Strategy", "Content Calendar Creation", "Facebook Marketing", "Instagram Marketing", 
        "Twitter Marketing", "LinkedIn Marketing", "Pinterest Marketing", "TikTok Marketing", 
        "YouTube Marketing", "Snapchat Marketing", "Reddit Marketing", "Discord Community Management", 
        "WhatsApp Marketing", "Telegram Marketing", "Social Media Content Creation", "Social Media Copywriting", 
        "Social Media Visual Design", "Social Media Video Creation", "Social Media Analytics", 
        "Social Media Reporting", "Community Management", "Social Media Engagement", "Social Listening", 
        "Influencer Marketing", "Influencer Outreach", "Influencer Management", "Influencer Analytics", 
        "Social Media Advertising", "Facebook Ads", "Instagram Ads", "Twitter Ads", "LinkedIn Ads", 
        "Pinterest Ads", "TikTok Ads", "YouTube Ads", "Snapchat Ads", "Social Media Contest Management",
        "UGC (User-Generated Content) Strategy", "Social Media Takeovers", "Live Streaming Management",
        "Hashtag Strategy", "Social Media Trend Analysis", "Meme Marketing", "Social Commerce",
        "Community Building", "Social Media Crisis Management", "Platform-Specific Best Practices",
        
        # Email Marketing
        "Email Strategy", "Email Campaign Planning", "Email Copywriting", "Email Template Design", 
        "Email HTML Coding", "Email Deliverability", "Email Automation", "Email Segmentation", 
        "Email Personalization", "A/B Testing", "Email Analytics", "Email List Management", 
        "Lead Nurturing", "Drip Campaigns", "Broadcast Emails", "Newsletter Creation", 
        "Transactional Emails", "Re-engagement Campaigns", "Welcome Series", "Abandoned Cart Emails", 
        "Post-Purchase Series", "Email Subject Line Optimization", "Preview Text Optimization", 
        "Email Call-to-Action Optimization", "Email Template Responsive Design", "Email Client Testing", 
        "GDPR Compliance", "CAN-SPAM Compliance", "CASL Compliance", "Email Service Providers (ESPs)",
        "Mailchimp", "Campaign Monitor", "ActiveCampaign", "Klaviyo", "Constant Contact",
        "ConvertKit", "HubSpot Email Tools", "Sendinblue", "AWeber", "GetResponse",
        "Email List Building", "Opt-in Strategy", "Double Opt-in Implementation",
        "Email Authentication (SPF, DKIM, DMARC)", "Email Marketing Metrics Analysis",
        
        # Content Marketing
        "Content Marketing Strategy", "Content Calendar Management", "Blog Management", "Content Creation", 
        "Content Distribution", "Content Promotion", "Content Performance Analysis", "Content ROI Tracking", 
        "Guest Posting", "Influencer Content Collaboration", "Content Partnerships", "Content Repurposing", 
        "Cornerstone Content Creation", "Pillar Content Strategy", "Content Cluster Strategy", 
        "Thought Leadership Development", "Industry Research Reports", "White Paper Creation", 
        "Ebook Production", "Case Study Development", "Infographic Creation", "Video Content Strategy", 
        "Podcast Production", "Webinar Management", "Live Event Content", "User-Generated Content Strategy",
        "Interactive Content Creation", "Quizzes & Assessments", "Calculators & Tools", "Content Auditing",
        "Competitive Content Analysis", "Content Gap Analysis", "Topic Research", "Evergreen Content Strategy",
        "Seasonal Content Planning", "Trending Content Creation", "Viral Content Strategy",
        "Customer Journey Content Mapping", "Sales Funnel Content", "Multi-language Content Strategy",
        "Content Localization", "Regional Content Adaptation", "Industry-Specific Content Expertise",
        
        # Analytics & Data
        "Google Analytics", "Google Analytics 4 Migration", "Google Tag Manager", "Data Studio", 
        "Adobe Analytics", "Mixpanel", "Amplitude", "Heap", "Hotjar", "Crazy Egg", "Lucky Orange", 
        "Mouseflow", "FullStory", "Optimizely", "VWO", "Google Optimize", "A/B Testing", "Multivariate Testing", 
        "Conversion Tracking", "Event Tracking", "Attribution Modeling", "UTM Parameter Management", 
        "Custom Dimension Configuration", "Enhanced E-commerce Tracking", "Goal Setup & Tracking", 
        "Funnel Analysis", "User Flow Analysis", "Bounce Rate Analysis", "Exit Rate Analysis", 
        "Heat Map Analysis", "Session Recording Analysis", "Form Analytics", "Page Speed Analysis",
        "Cross-device Tracking", "Cross-domain Tracking", "Server-side Tracking", "Cookie Compliance Tracking",
        "Data Visualization", "Custom Dashboard Creation", "Report Automation", "Marketing ROI Analysis",
        "Customer Lifetime Value Analysis", "Cohort Analysis", "Segmentation Analysis", "Predictive Analytics",
        "Machine Learning for Marketing", "Statistical Analysis", "Big Data Analysis", "Excel for Data Analysis",
        
        # E-commerce Marketing
        "E-commerce Strategy", "Product Page Optimization", "Category Page Optimization", 
        "Shopping Cart Optimization", "Checkout Optimization", "Product Description Writing", 
        "E-commerce SEO", "E-commerce PPC", "Amazon Marketplace Optimization", "Amazon PPC", 
        "eBay Marketing", "Etsy Marketing", "Shopify Marketing", "WooCommerce Marketing", 
        "Magento Marketing", "BigCommerce Marketing", "Abandoned Cart Recovery", "Cross-selling Strategies", 
        "Upselling Strategies", "Product Bundling", "Dynamic Pricing Strategies", "Discount Strategy", 
        "Coupon Strategy", "Flash Sale Management", "Holiday Marketing", "Seasonal Campaigns", 
        "E-commerce Email Marketing", "SMS Marketing for E-commerce", "Customer Loyalty Programs",
        "E-commerce Analytics", "Conversion Rate Optimization", "Customer Review Management",
        "Social Proof Implementation", "Product Photography Direction", "E-commerce Content Marketing",
        "Marketplace Strategy", "Multi-channel Selling Strategy", "Inventory Management", "Supply Chain Optimization",
        "Fulfillment Strategy", "Returns Policy Optimization", "Customer Service Strategy",
        
        # Marketing Automation & CRM
        "Marketing Automation Strategy", "HubSpot", "Marketo", "Pardot", "ActiveCampaign", 
        "Mailchimp Automation", "Customer Journey Mapping", "Lead Scoring", "Lead Nurturing", 
        "Workflow Creation", "Trigger Setup", "Conditional Logic", "Personalization Rules", 
        "Dynamic Content", "Behavioral Targeting", "CRM Integration", "Salesforce", "Zoho CRM", 
        "HubSpot CRM", "Pipedrive", "Sales and Marketing Alignment", "Lead Lifecycle Management", 
        "Customer Lifecycle Management", "Customer Segmentation", "Account-Based Marketing Automation",
        "Marketing-Sales Handoff", "SLA Development", "Revenue Attribution", "Multi-touch Attribution",
        "Custom Integration Development", "API Implementation", "Webhook Configuration",
        "Progressive Profiling", "Form Strategy", "Landing Page Strategy", "Marketing Database Management",
        "Data Cleansing", "Contact Management", "Customer Data Platform (CDP) Management",
        
        # Advertising & Paid Media
        "Paid Media Strategy", "Media Planning", "Media Buying", "Google Ads", "Facebook Ads", 
        "Instagram Ads", "Twitter Ads", "LinkedIn Ads", "Pinterest Ads", "TikTok Ads", "Snapchat Ads", 
        "YouTube Ads", "Display Advertising", "Programmatic Advertising", "Native Advertising", 
        "In-app Advertising", "Mobile Advertising", "Video Advertising", "Connected TV Advertising", 
        "Podcast Advertising", "Audio Advertising", "Out-of-Home Advertising", "Print Advertising", 
        "Direct Mail", "Retargeting/Remarketing", "Geotargeting", "Demographic Targeting", 
        "Interest Targeting", "Behavioral Targeting", "Contextual Targeting", "Ad Copywriting",
        "Ad Creative Direction", "Ad Landing Page Design", "Ad Performance Tracking", "Ad Testing",
        "Ad Optimization", "Bid Management", "Budget Allocation", "ROAS Optimization", "CPM Optimization",
        "CPC Optimization", "CPA Optimization", "Ad Fraud Detection", "Brand Safety Measures",
        
        # Brand & PR
        "Brand Strategy", "Brand Positioning", "Brand Messaging", "Brand Voice", "Brand Identity", 
        "Brand Guidelines", "Brand Monitoring", "Reputation Management", "Online Reputation Management", 
        "Crisis Communication", "PR Strategy", "Media Relations", "Media Outreach", "Press Release Writing", 
        "Press Kit Development", "Media Pitch Creation", "Journalist Relationship Building", 
        "Thought Leadership Placement", "Speaking Opportunity Sourcing", "Award Submission Management", 
        "Event PR", "Product Launch PR", "Investor Relations", "Internal Communications", 
        "Employer Branding", "Corporate Social Responsibility", "Cause Marketing", "Sponsorship Strategy",
        "Sponsorship Activation", "Influencer Relations", "Celebrity Endorsements", "Brand Partnerships",
        "Co-branding Initiatives", "Brand Affiliate Programs", "Brand Ambassador Programs",
        "Community Relations", "Local Marketing", "Brand Consistency Management", "Brand Health Metrics",
        
        # Specialized Marketing Areas
        "Growth Hacking", "Viral Marketing", "Guerrilla Marketing", "Experiential Marketing", 
        "Event Marketing", "Trade Show Marketing", "Webinar Marketing", "Video Marketing", 
        "Podcast Marketing", "App Store Optimization", "Mobile Marketing", "SMS Marketing", 
        "QR Code Marketing", "Proximity Marketing", "Location-based Marketing", "Geofencing", 
        "AR Marketing", "VR Marketing", "Voice Search Marketing", "Conversational Marketing", 
        "Chatbot Marketing", "AI Marketing", "Neuromarketing", "Behavioral Marketing", 
        "Psychological Marketing", "Emotional Marketing", "Sensory Marketing", "Scarcity Marketing", 
        "FOMO Marketing", "Referral Marketing", "Affiliate Marketing", "Partner Marketing",
        "B2B Marketing", "Account-Based Marketing", "Lead Generation", "Demand Generation",
        "Field Marketing", "Inside Sales Support", "Sales Enablement", "Product Marketing",
        "Launch Marketing", "Adoption Marketing", "Retention Marketing", "Reactivation Marketing",
        "Win-back Campaigns", "Customer Marketing"
    ],
    
    "Video & Animation": [
        # Video Production & Editing
        "Video Shooting", "Camera Operation", "Cinematography", "Lighting Setup", "Audio Recording", 
        "Directing", "Video Production Planning", "Storyboarding", "Script Writing", "Shot List Creation", 
        "Production Management", "Video Editing", "Adobe Premiere Pro", "Final Cut Pro", "DaVinci Resolve", 
        "Vegas Pro", "iMovie", "Adobe Rush", "Avid Media Composer", "Filmora", "Color Grading", 
        "Color Correction", "Audio Editing", "Sound Design", "Sound Mixing", "Foley Recording", 
        "Voice-over Direction", "Voice-over Recording", "Music Selection", "Stock Music Integration", 
        "Green Screen/Chroma Key", "Rotoscoping", "Keying", "Tracking", "Stabilization", "LUTs",
        "Multi-camera Editing", "Video Compression", "Video Encoding", "Video Format Conversion",
        "Frame Rate Conversion", "Video Aspect Ratio Adjustment", "Video Resolution Scaling",
        "Video Noise Reduction", "Video Interview Setup", "Remote Video Production", "Live Switching",
        "Live Streaming Production", "YouTube Video Optimization", "Video SEO", "Video Thumbnail Creation",
        
        # 2D Animation
        "2D Animation", "Traditional Animation", "Digital 2D Animation", "Frame-by-Frame Animation", 
        "Cel Animation", "Vector Animation", "Character Animation", "Lip Sync Animation", 
        "Walk Cycle Animation", "Character Rigging (2D)", "Puppet Animation", "Cut-out Animation", 
        "Motion Graphics", "Kinetic Typography", "Text Animation", "Logo Animation", "Explainer Video Animation", 
        "Whiteboard Animation", "Doodle Animation", "Infographic Animation", "Cartoon Animation", 
        "Comic Style Animation", "Anime Style Animation", "2D Game Animation", "UI Animation", 
        "GIF Creation", "Social Media Animation", "After Effects Animation", "Adobe Animate", 
        "Toon Boom Harmony", "TV Paint", "Moho (Anime Studio)", "Synfig", "Krita Animation",
        "Rough Animation", "Clean-up Animation", "In-betweening", "Onion Skinning", "Tweening",
        "Easing", "Squash and Stretch", "Anticipation", "Follow Through", "Overlapping Action",
        "Arcs", "Timing and Spacing", "Character Design for Animation", "Background Design for Animation",
        
        # 3D Animation
        "3D Animation", "3D Character Animation", "3D Character Rigging", "Weight and Balance", 
        "3D Walk Cycle", "3D Lip Sync", "Facial Animation", "Body Mechanics", "Creature Animation", 
        "Crowd Simulation", "Procedural Animation", "Physics-based Animation", "Cloth Simulation", 
        "Hair and Fur Simulation", "Fluid Simulation", "Particle Effects", "Soft Body Dynamics", 
        "Rigid Body Dynamics", "Motion Capture", "Facial Motion Capture", "3D Camera Animation", 
        "Lighting Animation", "3D Modeling for Animation", "3D Texturing", "3D Rendering", 
        "Blender Animation", "Maya Animation", "Cinema 4D Animation", "3ds Max Animation", 
        "Houdini Animation", "ZBrush for Animation", "Substance Painter for Animation",
        "Unreal Engine Animation", "Unity Animation", "Marvelous Designer", "Character Creator",
        "iClone", "Daz3D", "MotionBuilder", "Rokoko", "Mixamo", "Cascadeur", "Procedural Animation",
        "Dynamic Animation", "Keyframe Animation", "Non-linear Animation", "Animation Layers",
        "Animation Blending", "Inverse Kinematics", "Forward Kinematics",
        
        # Motion Graphics & VFX
        "Motion Graphics Design", "After Effects", "Cinema 4D", "Blender for Motion Graphics", 
        "Element 3D", "Particular", "Trapcode Suite", "Saber", "Animation Composer", "Motion Factory", 
        "Motion Array", "Video Copilot", "Red Giant Tools", "FxFactory", "Sapphire Plugins", 
        "Mocha AE", "Track Mattes", "Shape Layers", "Expressions", "Null Objects", "Parenting", 
        "Text Animation", "Shape Animation", "Liquid Animation", "Particle Animation", "Logo Animation", 
        "Broadcast Package Design", "Lower Thirds Design", "Transition Design", "Title Sequence Design", 
        "HUD/UI Animation", "Data Visualization Animation", "Infographic Animation", "Visual Effects (VFX)",
        "Compositing", "Keying", "Rotoscoping", "Tracking", "Match Moving", "Camera Tracking",
        "Object Removal", "Sky Replacement", "Screen Replacement", "Set Extension", "Light Effects",
        "Fire Effects", "Water Effects", "Smoke Effects", "Explosion Effects", "Blood Effects",
        "Weather Effects", "Sci-fi Effects", "Magic Effects", "Energy Effects", "Destruction Effects",
        
        # Video Marketing & Strategy
        "Video Marketing Strategy", "Video Content Planning", "YouTube Channel Management", 
        "YouTube Growth Strategy", "YouTube SEO", "YouTube Analytics", "Video Script Writing", 
        "Video Storyboarding", "Brand Video Production", "Product Video Production", "Explainer Video Production", 
        "Testimonial Video Production", "Corporate Video Production", "Social Media Video Strategy", 
        "Instagram Video Strategy", "TikTok Video Strategy", "Facebook Video Strategy", "LinkedIn Video Strategy", 
        "Short-form Video Creation", "Vertical Video Production", "Square Video Production", 
        "Live Video Production", "Live Streaming Management", "Webinar Production", "Video Monetization Strategy",
        "Video Advertising Strategy", "Video Thumbnail Design", "Video Call-to-Action Strategy",
        "Closed Caption Creation", "Subtitle Creation", "Video Localization", "Multi-language Video Strategy",
        "Video Analytics & Performance Tracking", "Video A/B Testing", "Video Conversion Optimization",
        "Video Distribution Strategy", "Video Syndication", "Video Remarketing Strategy",
        
        # Specialized Animation Styles
        "Stop Motion Animation", "Claymation", "Paper Cut-out Animation", "Sand Animation", 
        "Pixilation", "Puppet Animation", "LEGO Animation", "Action Figure Animation", "Flipbook Animation", 
        "Rotoscoping Animation", "Light Painting Animation", "Time-Lapse Animation", "Tilt-Shift Animation", 
        "Silhouette Animation", "Shadow Puppetry", "Pinscreen Animation", "Paint-on-Glass Animation", 
        "Drawn-on-film Animation", "Charcoal Animation", "Watercolor Animation", "Isometric Animation", 
        "Low Poly Animation", "Flat Design Animation", "Minimalist Animation", "Glitch Animation", 
        "Retro Animation", "Pixel Art Animation", "Anime Animation", "Cartoon Network Style", 
        "Disney Style Animation", "Anime Style Animation", "Manga Style Animation", "Chibi Style Animation",
        "Comic Book Style Animation", "South Park Style Animation", "The Simpsons Style Animation",
        "Looney Tunes Style Animation", "CalArts Style Animation", "UPA Style Animation",
        
        # Specialized Video Content
        "YouTube Video Production", "YouTube Shorts Creation", "TikTok Video Creation", 
        "Instagram Reels Production", "Instagram Stories Production", "Facebook Watch Videos", 
        "LinkedIn Video Content", "Twitter Video Content", "Vlog Production", "Travel Video Production", 
        "Food Video Production", "Recipe Video Production", "ASMR Video Production", "Gaming Video Production", 
        "Let's Play Videos", "Unboxing Videos", "Product Review Videos", "Tutorial Videos", 
        "How-to Videos", "Educational Videos", "Explainer Videos", "Whiteboard Videos", 
        "Talking Head Videos", "Interview Videos", "Documentary Production", "Short Film Production", 
        "Music Video Production", "Wedding Videography", "Event Videography", "Real Estate Videos",
        "Virtual Tour Videos", "Drone Videography", "Underwater Videography", "Sports Videography",
        "Fitness Videos", "Fashion Videos", "Beauty Tutorial Videos", "Medical Videos",
        "Legal Videos", "Training Videos", "Corporate Videos", "Testimonial Videos",
        "Case Study Videos", "Crowdfunding Videos", "Nonprofit Videos", "Political Campaign Videos",
        
        # Video Hardware & Equipment Knowledge
        "Camera Equipment", "DSLR Video", "Mirrorless Camera Video", "Cinema Camera Operation", 
        "Action Camera Usage", "Smartphone Videography", "Camera Settings", "Lens Selection", 
        "Focal Length Understanding", "Aperture Settings", "Shutter Speed Settings", "ISO Settings", 
        "White Balance", "Composition Rules", "Camera Movement", "Gimbal Operation", "Steadicam Operation", 
        "Dolly Operation", "Slider Operation", "Jib/Crane Operation", "Drone Operation", "Lighting Equipment", 
        "Three-point Lighting", "Natural Lighting", "Lighting Temperature", "Light Modifiers", 
        "Audio Equipment", "Microphone Types", "Lavalier Mic Setup", "Shotgun Mic Usage", 
        "Boom Mic Operation", "Audio Recorder Operation", "Green Screen Setup", "Studio Setup",
        "Field Recording", "Location Scouting", "Set Design", "Prop Management",
        "Wardrobe Selection", "Makeup for Video", "Special Effects Makeup"
    ],
    
    "Data Science & Analytics": [
        # Programming Languages
        "Python", "R", "SQL", "Julia", "Scala", "Java", "C++", "MATLAB", "Bash", "SAS",
        
        # Data Manipulation & Analysis
        "Pandas", "NumPy", "Dask", "Data.table (R)", "Tidyverse", "Data Wrangling", "Data Cleaning",
        "Data Transformation", "Exploratory Data Analysis (EDA)", "Data Imputation",
        "Descriptive Statistics", "Inferential Statistics", "Statistical Testing", "Hypothesis Testing",
        "Statistical Modeling", "Time Series Analysis", "Multivariate Analysis", "ANOVA", "Regression Analysis",
        
        # Data Visualization
        "Matplotlib", "Seaborn", "Plotly", "Bokeh", "Altair", "ggplot2", "Tableau", "Power BI",
        "Looker", "D3.js", "Dash", "Shiny (R)", "Google Data Studio", "Excel Data Visualization",
        "Interactive Dashboards", "Infographics", "Data Storytelling", "Geospatial Visualization",
        
        # Machine Learning
        "Scikit-learn", "XGBoost", "LightGBM", "CatBoost", "Keras", "TensorFlow", "PyTorch", "FastAI",
        "MLlib (Spark)", "Weka", "H2O.ai", "Supervised Learning", "Unsupervised Learning",
        "Reinforcement Learning", "Semi-supervised Learning", "Clustering", "Classification", 
        "Regression Models", "Dimensionality Reduction", "Ensemble Methods", "Model Evaluation",
        "Model Selection", "Cross-validation", "Hyperparameter Tuning", "Grid Search", "Random Search",
        "Automated Machine Learning (AutoML)", "ML Pipelines", "Model Deployment", "ML Model Explainability",
        "Bias and Fairness in ML", "Model Monitoring", "Retraining Strategies",
        
        # Deep Learning
        "Neural Networks", "CNNs", "RNNs", "LSTM", "GRU", "GANs", "Autoencoders", 
        "Transfer Learning", "Pre-trained Models", "Object Detection", "Image Classification", 
        "Image Segmentation", "Speech Recognition", "Text-to-Speech", "Computer Vision",
        "Natural Language Processing (NLP)", "BERT", "GPT Models", "Hugging Face Transformers",
        
        # Big Data & Distributed Computing
        "Apache Spark", "PySpark", "Hadoop", "MapReduce", "Hive", "Pig", "Kafka", "Flink", 
        "Dask", "Ray", "Presto", "HBase", "BigQuery", "Athena", "AWS EMR", "Azure Data Lake",
        "Google Cloud Dataflow", "Databricks", "Snowflake", "Delta Lake", "Apache Airflow",
        
        # Databases & Querying
        "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Elasticsearch", "Neo4j", 
        "NoSQL Databases", "GraphQL", "Oracle DB", "SQL Server", "ClickHouse",
        
        # Data Engineering & ETL
        "ETL Pipelines", "Apache NiFi", "Luigi", "Kettle", "SSIS", "Talend", "DBT", "Airbyte", 
        "Fivetran", "Informatica", "Kafka Streams", "Data Ingestion", "Data Warehousing", 
        "Data Lakes", "Data Marts", "Data Modeling", "Star Schema", "Snowflake Schema",
        "Schema Design", "Data Pipeline Monitoring", "Streaming Data Processing",
        
        # Cloud & DevOps for Data Science
        "AWS (S3, Lambda, SageMaker)", "Azure ML", "Google Cloud AI Platform", "Docker", 
        "Kubernetes", "Terraform", "MLflow", "DVC", "Kubeflow", "Model Registry",
        "CI/CD for ML", "Data Versioning", "Experiment Tracking",
        
        # BI & Reporting Tools
        "Tableau", "Power BI", "Looker", "QlikView", "Qlik Sense", "Superset", "Metabase",
        "Google Sheets", "Excel (Advanced)", "Zoho Analytics", "Crystal Reports",
        
        # Data Governance & Ethics
        "Data Privacy", "GDPR Compliance", "CCPA Compliance", "PII Handling", 
        "Data Security", "Ethical AI", "Bias Mitigation", "Fairness in AI", 
        "Model Interpretability", "Explainable AI (XAI)", "Auditability", "Data Provenance",
        
        # Soft Skills & Methodologies
        "Business Acumen", "Communication", "Data Storytelling", "Stakeholder Management",
        "Agile for Data Teams", "CRISP-DM", "KDD Process", "Design Thinking", 
        "Requirement Gathering", "Collaboration with Domain Experts"
    ],
    
    "Virtual Assistance": [
        # Administrative Tasks
        "Calendar Management", "Email Management", "Appointment Scheduling", "Meeting Coordination",
        "Travel Planning", "Expense Reporting", "Task Management", "Event Planning", "Online Research",
        "Data Entry", "File Organization", "Document Management", "Spreadsheets", "Transcription",
        "Taking Meeting Minutes", "Presentation Preparation", "Proofreading", "Template Creation",
        "Note-taking", "Document Formatting",

        # Communication & Customer Support
        "Live Chat Support", "Email Support", "Phone Support", "CRM Software", "Customer Relationship Management",
        "Zendesk", "Freshdesk", "HubSpot CRM", "Zoho CRM", "Intercom", "Tawk.to", "Gorgias", "Help Scout",
        "Social Media Inbox Management", "Customer Feedback Collection", "Issue Escalation",
        "Lead Nurturing", "Ticketing System Management",

        # Project & Task Management Tools
        "Trello", "Asana", "ClickUp", "Monday.com", "Notion", "Wrike", "Airtable", "Smartsheet", "Basecamp",
        "Google Workspace", "Microsoft 365", "Slack", "Microsoft Teams", "Zoom", "Skype", "Google Meet",

        # eCommerce & Order Support
        "Shopify Order Fulfillment", "Amazon Seller Support", "Etsy Shop Management", "eBay Store Management",
        "WooCommerce Support", "Inventory Updates", "Order Tracking", "Return Management",
        "Customer Inquiry Handling", "Product Listings Management", "Cart Abandonment Follow-ups",

        # Social Media Management
        "Instagram Scheduling", "Facebook Page Updates", "LinkedIn Profile Management",
        "Pinterest Pin Scheduling", "Buffer", "Hootsuite", "Later", "Content Scheduling",
        "Engagement Tracking", "Hashtag Research", "Social Media Comments Management",

        # Bookkeeping & Finance Support
        "Invoicing", "Bill Payments", "Receipts Tracking", "Basic Bookkeeping", "QuickBooks", "Xero",
        "Wave Accounting", "FreshBooks", "Bank Reconciliation", "Budget Monitoring", "Spreadsheet Finance Tracking",

        # Content Support
        "Blog Post Formatting", "Newsletter Setup", "Proofreading", "Basic SEO Formatting",
        "WordPress Management", "Content Editing", "Headline Testing", "Formatting for Readability",
        "Link Checking", "Uploading Media", "Image Optimization",

        # Marketing Support
        "Email Campaign Scheduling", "Mailchimp", "ConvertKit", "Klaviyo", "Landing Page Setup",
        "Google Forms Creation", "Survey Distribution", "Lead Magnet Delivery", "Opt-in Form Setup",
        "Basic Analytics Reporting", "UTM Link Creation",

        # Tech-Savviness
        "Google Sheets", "Excel (Formulas & Shortcuts)", "PowerPoint", "Google Slides",
        "Canva", "Loom", "Screencast Tools", "Password Managers (LastPass, 1Password)",
        "Zapier", "IFTTT", "Browser Automation Tools", "PDF Management", "Basic HTML Edits",

        # Soft Skills & Traits
        "Time Management", "Attention to Detail", "Multitasking", "Confidentiality Handling",
        "Self-Motivation", "Problem Solving", "Reliability", "Clear Communication", "Adaptability",
        "Proactive Attitude", "Empathy", "Task Prioritization", "Follow-through"
    ],
    
    "Business & Finance": [
        # Accounting & Bookkeeping
        "Financial Accounting", "Managerial Accounting", "Bookkeeping", "Accounts Payable", 
        "Accounts Receivable", "General Ledger", "Bank Reconciliation", "Expense Tracking", 
        "Chart of Accounts", "Payroll Processing", "Month-End Closing", "Year-End Closing",
        "Cash Flow Tracking", "Journal Entries", "Account Reconciliation", "Petty Cash Management",
        
        # Finance Tools & Software
        "QuickBooks", "Xero", "Wave Accounting", "FreshBooks", "Sage", "Tally ERP", 
        "Zoho Books", "Kashoo", "NetSuite", "SAP FICO", "Oracle Financials", 
        "Microsoft Excel (Advanced)", "Google Sheets for Finance", "Pivot Tables", "VLOOKUP", "Power Query",
        
        # Financial Analysis & Forecasting
        "Financial Statements Analysis", "Balance Sheet", "Income Statement", "Cash Flow Statement",
        "Ratio Analysis", "Profitability Analysis", "Cost Analysis", "Break-even Analysis",
        "Variance Analysis", "Budgeting", "Forecasting", "Revenue Modeling", "Scenario Planning",
        "Financial Modeling", "DCF Valuation", "NPV and IRR", "Capital Budgeting", "Financial KPIs",
        
        # Investment & Corporate Finance
        "Investment Analysis", "Portfolio Management", "Asset Allocation", "Risk Management",
        "Capital Structure Analysis", "Cost of Capital", "Equity Valuation", "Bond Valuation",
        "Stock Market Analysis", "IPO Preparation", "Mergers and Acquisitions", "Private Equity",
        "Venture Capital", "Startup Financial Planning", "Investor Reporting",
        
        # Business Planning & Strategy
        "Business Plan Writing", "Market Research", "Competitive Analysis", "SWOT Analysis",
        "Business Model Canvas", "Lean Canvas", "Financial Projections", "Go-to-Market Strategy",
        "Pricing Strategy", "Revenue Streams Design", "Operations Planning", "Business Consulting",
        
        # Taxation & Compliance
        "Tax Filing (Personal & Business)", "GST/VAT Compliance", "Sales Tax Reporting", 
        "Income Tax Preparation", "Quarterly Tax Estimates", "IRS Forms", "Tax Deductions",
        "1099 Preparation", "W-2 Preparation", "Business Registration", "Compliance Audits",
        "Payroll Tax Filing", "Filing Annual Returns", "Local Business License Applications",
        
        # Auditing & Controls
        "Internal Auditing", "External Audit Preparation", "Internal Controls", 
        "Audit Trail Documentation", "SOX Compliance", "Risk Assessment", "Fraud Detection",
        "Operational Auditing", "Compliance Checklists", "Audit Reports",
        
        # Procurement & Inventory
        "Purchase Order Management", "Vendor Payments", "Inventory Tracking", 
        "Supply Chain Cost Analysis", "Cost of Goods Sold (COGS)", "Reorder Levels",
        "Inventory Valuation", "Budgeted Procurement", "Vendor Negotiation",
        
        # Business Operations Support
        "KPI Reporting", "Dashboards", "Business Intelligence", "Process Automation",
        "Standard Operating Procedures (SOPs)", "Project Costing", "Time Tracking Analysis",
        "Workforce Budgeting", "Financial Risk Assessment", "Credit Control",
        
        # Soft Skills & Reporting
        "Attention to Detail", "Analytical Thinking", "Problem Solving", "Communication of Financial Data",
        "Report Writing", "Presenting to Stakeholders", "Data Interpretation", "Confidentiality Handling",
        "Cross-Functional Collaboration", "Business English", "Decision Making",
        "Ethics in Finance", "Professional Judgment"
    ],
    
    "Cybersecurity": [
        # Core Concepts & Principles
        "Information Security", "CIA Triad (Confidentiality, Integrity, Availability)",
        "Risk Management", "Threat Modeling", "Attack Vectors", "Vulnerability Assessment",
        "Security Controls", "Defense in Depth", "Security Policies", "Security Awareness Training",
        "Incident Response", "Security Audit", "Security Standards (ISO 27001, NIST)",

        # Networking & Network Security
        "TCP/IP Protocols", "OSI Model", "Packet Analysis", "Firewalls", "VPNs", 
        "Intrusion Detection Systems (IDS)", "Intrusion Prevention Systems (IPS)",
        "Network Access Control (NAC)", "Proxy Servers", "DDoS Mitigation", "Wi-Fi Security",
        "Secure Network Design", "Network Segmentation", "NAT", "IPSec", "MAC Filtering",
        "Port Security", "802.1X Authentication", "Network Monitoring",

        # System & Endpoint Security
        "Operating System Security", "Patch Management", "Antivirus & Anti-malware",
        "Application Whitelisting", "Host-based Firewalls", "Endpoint Detection & Response (EDR)",
        "Mobile Device Management (MDM)", "Secure Configuration", "Least Privilege",
        "Remote Desktop Security", "USB Device Security",

        # Web & Application Security
        "OWASP Top 10", "Cross-Site Scripting (XSS)", "SQL Injection", "CSRF", "Broken Access Control",
        "Security Misconfiguration", "Sensitive Data Exposure", "Authentication Vulnerabilities",
        "Secure Coding Practices", "Static Code Analysis", "Dynamic Application Testing (DAST)",
        "Web Application Firewalls (WAF)", "Code Review for Security",

        # Identity & Access Management (IAM)
        "Authentication", "Authorization", "Multi-Factor Authentication (MFA)",
        "Role-Based Access Control (RBAC)", "Identity Federation", "SSO (Single Sign-On)",
        "LDAP", "Kerberos", "OAuth2", "OpenID Connect", "SAML", "Privileged Access Management (PAM)",

        # Encryption & Cryptography
        "Symmetric Encryption", "Asymmetric Encryption", "Public Key Infrastructure (PKI)",
        "TLS/SSL", "Hashing (SHA, MD5, bcrypt)", "Digital Signatures", "Key Management",
        "Certificate Authorities (CAs)", "Disk Encryption", "End-to-End Encryption",
        "PGP", "Zero-Knowledge Proofs",

        # Penetration Testing & Ethical Hacking
        "Penetration Testing", "Vulnerability Scanning", "Metasploit", "Burp Suite", "Nmap",
        "Wireshark", "Kali Linux", "Aircrack-ng", "Hydra", "John the Ripper",
        "Social Engineering", "Physical Security Testing", "Red Teaming", "Blue Teaming",
        "Capture the Flag (CTF)", "Reconnaissance", "Exploit Development", "Post-Exploitation",

        # Governance, Risk & Compliance (GRC)
        "Compliance Frameworks (HIPAA, GDPR, SOX, PCI-DSS)", "Policy Development", "Risk Assessment",
        "Security Gap Analysis", "Business Continuity Planning", "Disaster Recovery Planning",
        "Data Classification", "Regulatory Requirements", "Security Metrics & Reporting",

        # Cloud Security
        "Cloud Security Best Practices", "AWS Security", "Azure Security", "Google Cloud Security",
        "Shared Responsibility Model", "IAM for Cloud", "Cloud Access Security Brokers (CASB)",
        "Cloud Security Posture Management (CSPM)", "Container Security", "Serverless Security",
        "Data Loss Prevention (DLP) in Cloud", "S3 Bucket Security", "Cloud Encryption", 
        "Secrets Management (Vault, AWS Secrets Manager)",

        # Security Tools & Platforms
        "SIEM (Splunk, LogRhythm, IBM QRadar)", "EDR Solutions (CrowdStrike, SentinelOne)",
        "Threat Intelligence Platforms", "Security Orchestration Automation & Response (SOAR)",
        "Vulnerability Scanners (Nessus, Qualys)", "Log Analysis", "Sysmon", "Security Bash Scripting",

        # Cybersecurity Certifications
        "CompTIA Security+", "CEH (Certified Ethical Hacker)", "CISSP", "CISM", "OSCP",
        "GIAC Certifications", "CCSP", "ISO 27001 Lead Implementer", "Certified SOC Analyst (CSA)",
        "PenTest+", "Cloud Security Certifications (AWS, Azure, GCP)",

        # Soft Skills & Professional Ethics
        "Problem Solving", "Analytical Thinking", "Attention to Detail", "Critical Thinking",
        "Communication Skills", "Security Documentation", "Security Training Delivery",
        "Collaboration with DevOps & IT", "Security Advocacy", "Ethical Responsibility"
    ],
    
    "Game Development": [
        # Game Engines & Frameworks
        "Unity", "Unreal Engine", "Godot", "CryEngine", "GameMaker Studio", "Cocos2d-x",
        "Phaser", "PICO-8", "Construct 3", "GDevelop", "Defold", "LibGDX", "MonoGame",
        "RPG Maker", "Ren'Py", "Panda3D", "OpenGL", "DirectX", "Vulkan", "WebGL", "Three.js",

        # Programming Languages
        "C#", "C++", "Java", "JavaScript", "Python", "Lua", "GDScript", "Haxe", "Rust",
        "Kotlin", "Swift", "TypeScript", "Visual Scripting (Blueprints, Bolt)",

        # Game Design Principles
        "Game Mechanics Design", "Level Design", "Game Balance", "Player Psychology",
        "Game Loop Development", "Progression Systems", "Economy Systems", "Replayability",
        "Storytelling in Games", "Dialogue Design", "Quest Design", "Puzzle Design",
        "Narrative Design", "Character Design", "Game Monetization Models", "Freemium Design",

        # 2D & 3D Art Integration
        "2D Sprite Animation", "Tilemap Design", "3D Model Importing", "Rigging & Skinning",
        "Texture Mapping", "UV Unwrapping", "Shaders & Materials", "Lighting Design",
        "Camera Systems", "Post-processing Effects", "Particle Systems", "Parallax Scrolling",

        # Animation & Rigging
        "2D Animation", "Bone-based Animation", "Sprite Sheet Animation", "3D Rigging",
        "Inverse Kinematics", "Facial Animation", "Blend Shapes", "Animation Trees",
        "Cutscene Animation", "Motion Capture Integration", "Timeline Animations",
        "Animation Controllers", "Procedural Animation",

        # Audio & Music Integration
        "Sound FX Design", "Voice Acting Integration", "Dynamic Music", "Audio Mixing",
        "Spatial Audio", "FMOD", "Wwise", "Audio Triggers", "Audio Scripting",
        "Looping Sounds", "Music Transitions", "Dialogue Tree Audio",

        # Physics & Interactions
        "Physics Engines (Box2D, PhysX, Bullet)", "Ragdoll Physics", "Collision Detection",
        "Hitboxes and Hurtboxes", "Raycasting", "Triggers and Events", "Character Controllers",
        "Vehicle Physics", "Object Destruction", "Environmental Interaction",

        # Multiplayer & Networking
        "Multiplayer Setup", "Client-Server Architecture", "Peer-to-Peer Networking",
        "Photon Engine", "Mirror (Unity)", "UNet", "Steam Multiplayer", "Matchmaking Systems",
        "Lag Compensation", "State Syncing", "Voice Chat Integration", "Backend Servers (PlayFab, Nakama)",
        "Network Latency Handling", "Dedicated Servers", "Multiplayer Lobby Design",

        # Game UI/UX
        "HUD Design", "Menu Design", "Inventory Systems", "Dialog Boxes", "In-game Notifications",
        "UI Animation", "Cross-Platform Input Mapping", "Accessibility in Games",
        "Touch Controls", "Gamepad Support", "Key Remapping", "Responsive UI Scaling",

        # Monetization & Publishing
        "In-App Purchases", "Ads Integration (AdMob, Unity Ads)", "Rewarded Ads",
        "App Store Optimization (ASO)", "Steam Publishing", "Google Play Submission",
        "Apple App Store Submission", "Itch.io Deployment", "Epic Games Store Publishing",
        "Game Porting", "Version Control for Games", "Patch Management", "Game Localization",

        # Game Testing & QA
        "Bug Tracking", "Playtesting", "Performance Optimization", "FPS Monitoring",
        "Memory Leak Detection", "Unit Testing in Games", "Stress Testing", "Beta Testing",
        "UX Testing for Games", "Analytics Integration", "Telemetry Tracking",

        # VR, AR, and XR Development
        "VR Development (Oculus, SteamVR)", "AR Development (ARKit, ARCore)", "Mixed Reality",
        "Haptic Feedback", "360° Video Integration", "Motion Tracking", "Hand Tracking",
        "XR Input Systems", "Gaze Interaction", "Teleportation Navigation",

        # Soft Skills & Game Production
        "Agile Game Development", "Game Documentation (GDD)", "Trello for Game Dev",
        "JIRA for Games", "Scrum/Standups", "Cross-functional Collaboration",
        "Version Control (Git, GitHub, GitLab)", "CI/CD for Games", "Asset Management",
        "Modding Support", "Open Source Game Dev", "Community Building", "Game Marketing"
    ],
    
    "E-commerce Development": [
        # E-commerce Platforms
        "Shopify", "WooCommerce", "Magento", "BigCommerce", "PrestaShop", "OpenCart",
        "Squarespace Commerce", "Wix eCommerce", "Salesforce Commerce Cloud", "SAP Commerce Cloud",
        "VTEX", "Ecwid", "Shift4Shop", "Weebly eCommerce", "nopCommerce", "CS-Cart", "Zen Cart",
        "Shopware", "Commerce.js", "Snipcart",

        # Custom E-commerce Development
        "Headless Commerce", "Custom Cart Development", "Checkout Flow Customization",
        "Product Variations Handling", "Wishlist & Favorites", "Custom Payment Gateways",
        "Multi-vendor Marketplace Setup", "Dynamic Pricing Systems", "Abandoned Cart Recovery",
        "Order Tracking Systems", "Custom Loyalty Programs", "Subscription Models",
        "Customer Group Pricing", "Wholesale vs Retail Pricing Logic",

        # Frontend Development for E-commerce
        "HTML/CSS", "JavaScript", "React", "Vue", "Next.js", "Nuxt.js", "Tailwind CSS",
        "Bootstrap", "Liquid (Shopify)", "Handlebars", "Blade (Laravel)", "Alpine.js",
        "Responsive Design", "UI/UX for Shopping", "Mobile-First Checkout", "Accessibility (WCAG)",

        # Backend Technologies
        "Node.js", "Express", "Django", "Flask", "Laravel", "Symfony", "Ruby on Rails",
        "Spring Boot", "PHP", "GraphQL", "REST APIs", "JWT", "OAuth2", "Role-Based Access Control (RBAC)",
        "Product CRUD Systems", "Inventory Sync", "Order Management", "Customer Profile Systems",

        # Payment Integration
        "Stripe", "PayPal", "Square", "Razorpay", "Authorize.net", "2Checkout", "Payoneer", "Google Pay",
        "Apple Pay", "Cashfree", "Flutterwave", "Klarna", "Afterpay", "Cryptocurrency Integration (Coinbase, BitPay)",
        "Payment Flow Optimization", "Secure Checkout Implementation", "PCI DSS Compliance",

        # Shipping & Fulfillment
        "Shipping Rate APIs", "ShipStation", "EasyPost", "FedEx/UPS/DHL Integrations",
        "Real-Time Shipment Tracking", "Shipping Label Generation", "Order Fulfillment Systems",
        "Multi-warehouse Support", "Shipping Zones & Taxes", "Drop Shipping Integrations",

        # Product Management
        "SKU Management", "Bulk Product Uploads", "CSV/Excel Import/Export", "Image Galleries",
        "Product Filtering & Sorting", "Product Search with Autocomplete", "ElasticSearch",
        "Advanced Attribute Handling", "Product Badges", "Flash Sale Timers", "Product Comparison Features",

        # SEO & Marketing Tools
        "E-commerce SEO", "Rich Snippets", "Product Schema Markup", "Canonical URLs", "Sitemap.xml",
        "Meta Tags Automation", "Google Merchant Center", "Facebook Shop", "Pinterest Product Feed",
        "Email Marketing Integration", "Newsletter Popups", "Referral Marketing Tools",
        "SMS Marketing", "Affiliate Marketing Systems", "Google Analytics Integration",
        "Hotjar", "Session Replay Tools", "Retargeting Pixels (FB/Google)", "Dynamic Ads Feeds",

        # User Accounts & Security
        "Secure User Authentication", "Social Login Integration", "Account Dashboard",
        "Password Recovery Flows", "Two-Factor Authentication (2FA)", "Email Verification",
        "Customer Segmentation", "User Preferences", "Order History", "Secure Storage of Sensitive Data",

        # Analytics & Reporting
        "Sales Dashboards", "Customer Reports", "Product Performance Analytics",
        "Conversion Funnel Analysis", "Cart Abandonment Tracking", "UTM Tracking",
        "Multi-Channel Attribution", "Lifetime Value Calculation", "Google Tag Manager",
        "Custom Event Tracking", "Real-time Reporting Dashboards",

        # Performance & Optimization
        "Lazy Loading", "Code Splitting", "Page Speed Optimization", "CDN Integration",
        "Image Compression", "AMP for Product Pages", "Mobile Optimization", "SSR (Server-side Rendering)",
        "Caching Strategies", "Gzip/Brotli Compression", "Minification", "Web Vitals Tuning",

        # Compliance & Legal
        "GDPR Compliance", "Cookie Consent Management", "Terms & Conditions Pages",
        "Privacy Policy Pages", "Return & Refund Policy Setup", "Invoice Generation",
        "Tax Rules (VAT/GST)", "SSL Certificates", "CAPTCHA Protection", "Bot Mitigation"
    ],
    
    "Translation & Languages": [
        # Language Pairs (Common)
        "English to Spanish", "Spanish to English", "English to French", "French to English",
        "English to German", "German to English", "English to Nepali", "Nepali to English",
        "English to Hindi", "Hindi to English", "English to Chinese", "English to Arabic",
        "English to Japanese", "Japanese to English", "Korean to English", "Russian to English",

        # Specialized Translation Fields
        "Medical Translation", "Legal Translation", "Technical Translation", "Financial Translation",
        "Literary Translation", "Academic Translation", "Marketing Translation", "Website Translation",
        "Software/App Localization", "E-commerce Translation", "Tourism & Travel Translation",
        "Patent Translation", "Scientific Research Translation", "Government Document Translation",

        # Interpretation Services
        "Simultaneous Interpretation", "Consecutive Interpretation", "Whispered Interpretation",
        "Sign Language Interpretation", "Conference Interpretation", "Business Meeting Interpretation",
        "Telephone Interpretation", "Video Remote Interpretation (VRI)", "On-site Interpretation",

        # Subtitling & Captioning
        "Subtitling", "Closed Captioning", "Open Captioning", "Timecoding", "Line Break Optimization",
        "SRT/ASS/VTT File Creation", "Subtitle Translation", "Audio-visual Sync", "Subtitle QC",
        "Burned-in Subtitles", "Hardcoded Subtitles", "Transcreation for Subtitles",

        # Transcription Services
        "General Transcription", "Verbatim Transcription", "Clean Read Transcription",
        "Medical Transcription", "Legal Transcription", "Interview Transcription",
        "Podcast Transcription", "Lecture Transcription", "Zoom Call Transcription",
        "Audio to Text", "Video to Text", "Timestamping", "Speaker Labeling",

        # Localization Services
        "Website Localization", "Mobile App Localization", "Game Localization",
        "Marketing Material Localization", "Social Media Localization",
        "Software String Translation", "Cultural Adaptation", "Right-to-Left Language Support (RTL)",
        "Unicode Handling", "Pseudo-localization Testing", "Internationalization Testing (i18n)",

        # Tools & Platforms
        "SDL Trados", "MemoQ", "Wordfast", "Smartling", "Lokalise", "Crowdin", "POEditor",
        "Memsource", "Transifex", "OmegaT", "CAT Tools (Computer-Assisted Translation)",
        "Xbench", "QA Distiller", "Subtitle Edit", "Aegisub", "Amara", "Veed.io", "Descript",

        # Linguistic Quality Assurance
        "Terminology Consistency", "Grammar & Syntax Review", "Cultural Sensitivity",
        "Spelling & Punctuation Checks", "Translation Memory (TM) Usage", "Glossary Management",
        "Quality Assurance Reports", "Language Sign-off (LSO)", "Back Translation",

        # Voiceover & Dubbing
        "Voiceover Translation", "Multilingual Dubbing", "Lip Sync Matching",
        "Script Adaptation", "Narration", "IVR Recording Translation", "E-learning Narration Translation",

        # Writing & Editing in Multilingual Contexts
        "Multilingual Content Writing", "Multilingual SEO Writing", "Language-specific Blog Writing",
        "Grammar Correction", "Editing & Proofreading", "Copy Editing", "Post-editing Machine Translation (PEMT)",
        "Bilingual Content Creation", "Multilingual Marketing Writing",

        # Soft Skills & Professional Traits
        "Attention to Cultural Nuances", "Linguistic Sensitivity", "Confidentiality",
        "Attention to Detail", "Deadline Adherence", "Cross-cultural Communication",
        "Project Collaboration", "Client Communication", "Remote Work Ethics"
    ],
    
    "Blockchain & Web3": [
        # Core Concepts
        "Blockchain Fundamentals", "Consensus Algorithms", "Proof of Work", "Proof of Stake",
        "Smart Contracts", "Decentralized Applications (dApps)", "Tokenomics", "Gas Fees",
        "Public vs Private Blockchains", "On-chain vs Off-chain", "Layer 1 vs Layer 2",
        "Distributed Ledger Technology (DLT)", "Hashing", "Immutability", "Forks", "Block Explorers",

        # Blockchain Platforms
        "Ethereum", "Polygon", "Binance Smart Chain", "Solana", "Avalanche", "Fantom", "Near Protocol",
        "Algorand", "Polkadot", "Cosmos", "Cardano", "Tezos", "Tron", "Hedera Hashgraph", "Bitcoin",
        "Stacks (Bitcoin Layer 2)", "Arbitrum", "Optimism", "zkSync", "Base",

        # Smart Contract Development
        "Solidity", "Vyper", "Rust (for Solana)", "Move (for Aptos)", "Cadence (for Flow)",
        "Smart Contract Design Patterns", "Smart Contract Security", "Reentrancy Prevention",
        "Gas Optimization", "Upgradable Contracts", "Smart Contract Testing", "Hardhat", "Truffle",
        "Brownie", "Foundry", "OpenZeppelin", "Ethers.js", "Web3.js", "Alchemy", "Infura",

        # Wallet & Identity
        "MetaMask", "WalletConnect", "Ledger", "Trezor", "Phantom Wallet", "Trust Wallet",
        "Private/Public Key Handling", "ENS Domains", "Wallet Authentication (Sign-In with Wallet)",
        "Seed Phrases", "Mnemonic Storage", "Self-Custody Wallet Setup",

        # Web3 Frontend Integration
        "Web3.js", "Ethers.js", "React with Web3", "Next.js with Blockchain", "Web3Modal",
        "RainbowKit", "Wagmi", "Thirdweb", "Moralis", "Alchemy SDK", "IPFS Integration",
        "Connecting Wallets", "Reading from Smart Contracts", "Writing to Smart Contracts",
        "Real-time Blockchain Updates (using WebSocket or Events)",

        # DeFi (Decentralized Finance)
        "DEX (Decentralized Exchanges)", "Liquidity Pools", "Staking", "Yield Farming", "Lending & Borrowing",
        "AMMs (Automated Market Makers)", "Slippage", "Impermanent Loss", "Stablecoins", "Flash Loans",
        "DeFi Protocols (Aave, Compound, Uniswap, Sushiswap)", "TVL (Total Value Locked)", "Governance Tokens",

        # NFTs & Metaverse
        "ERC-721", "ERC-1155", "NFT Minting", "NFT Metadata", "IPFS for NFTs", "Lazy Minting",
        "NFT Marketplaces (OpenSea, Rarible)", "Royalties", "NFT Collection Deployment",
        "NFT Smart Contract Security", "NFT Whitelisting", "NFT Auctions", "Metaverse SDKs",
        "Spatial Web", "VR in Web3", "Wearable NFTs", "Land Ownership in Metaverse",

        # DAOs & Governance
        "DAO Setup", "Snapshot Voting", "On-chain Voting", "Multi-signature Wallets (Gnosis Safe)",
        "Token-based Governance", "DAO Frameworks (Aragon, DAOstack, Moloch)", "Quadratic Voting",
        "Treasury Management", "Governance Proposals", "DAO Automation",

        # Oracles & Cross-chain
        "Chainlink", "Band Protocol", "API3", "Decentralized Oracles", "Price Feeds",
        "Random Number Generation", "Cross-chain Bridges", "Interoperability", "Wormhole",
        "LayerZero", "Axelar", "Synapse Protocol", "Token Wrapping",

        # Blockchain Testing & Security
        "Unit Testing Smart Contracts", "Chai/Mocha Testing for Web3", "Ganache", "Anvil",
        "Testnet Deployment (Goerli, Sepolia, Mumbai)", "Security Audits", "Formal Verification",
        "MythX", "Slither", "Remix IDE", "Bug Bounty Platforms (Immunefi)", "Phishing Prevention",
        "Rug Pull Detection", "MEV (Miner Extractable Value)", "Reorg Attacks", "Flash Loan Attacks",

        # Storage & Infrastructure
        "IPFS", "Arweave", "Filecoin", "Pinata", "NFT.Storage", "The Graph", "Moralis",
        "Decentralized Indexing", "Smart Contract Events", "Subgraph Development",

        # Web3 DevOps & CI/CD
        "Contract Deployment Automation", "Hardhat Deploy", "Etherscan Verification",
        "Continuous Testing of dApps", "Version Control for Smart Contracts", "Rollbacks",
        "On-chain Logging", "Monitoring Transaction Status", "Gas Usage Alerts",

        # Blockchain Certifications & Ecosystem Skills
        "Certified Blockchain Developer", "Ethereum Developer Certification", "Consensys Academy",
        "Alchemy University", "Solidity Bootcamps", "Web3 Foundation Learning",
        "Community Contribution", "Hackathons", "GitHub PRs for Open Source Protocols"
    ],
    
    "Cloud Computing": [
        # Core Cloud Concepts
        "Cloud Architecture", "Public vs Private vs Hybrid Cloud", "Multi-Cloud Strategy",
        "Virtualization", "Scalability & Elasticity", "High Availability", "Fault Tolerance",
        "Load Balancing", "Cloud Storage Types (Object, Block, File)", "Shared Responsibility Model",
        "Cloud Security Best Practices", "Disaster Recovery Planning", "Cloud Cost Optimization",

        # Major Cloud Providers
        "Amazon Web Services (AWS)", "Microsoft Azure", "Google Cloud Platform (GCP)",
        "IBM Cloud", "Oracle Cloud", "DigitalOcean", "Linode", "Heroku", "Vultr", "Alibaba Cloud",

        # AWS Services
        "EC2", "S3", "Lambda", "RDS", "DynamoDB", "ECS", "EKS", "CloudFront", "SQS", "SNS", "CloudWatch",
        "IAM", "CloudTrail", "Route 53", "API Gateway", "CloudFormation", "Elastic Beanstalk",

        # Azure Services
        "Azure Virtual Machines", "Azure Blob Storage", "Azure Functions", "Azure SQL Database",
        "App Services", "Azure Kubernetes Service (AKS)", "Azure DevOps", "Azure Monitor",
        "Azure Active Directory", "Azure Logic Apps", "Azure API Management", "ARM Templates",

        # GCP Services
        "Compute Engine", "Cloud Storage", "Cloud Functions", "App Engine", "Cloud Run", "Firestore",
        "BigQuery", "Cloud Pub/Sub", "GKE (Google Kubernetes Engine)", "Stackdriver", "IAM & Admin",
        "Cloud Load Balancing", "Cloud DNS", "VPC Networks",

        # Serverless & Function-as-a-Service (FaaS)
        "AWS Lambda", "Azure Functions", "Google Cloud Functions", "Netlify Functions",
        "Serverless Framework", "Event-Driven Architectures", "Cold Start Optimization",
        "Asynchronous Processing", "Webhooks and Triggers",

        # Infrastructure as Code (IaC)
        "Terraform", "AWS CloudFormation", "Pulumi", "Azure Resource Manager (ARM)",
        "Google Deployment Manager", "Crossplane", "Chef", "Ansible", "SaltStack",

        # Containerization & Orchestration
        "Docker", "Docker Compose", "Kubernetes", "Helm", "Kustomize", "Minikube", "EKS", "AKS", "GKE",
        "Pod Management", "ReplicaSets", "StatefulSets", "Volumes", "Namespaces", "ConfigMaps",
        "Secrets", "RBAC for Kubernetes", "Service Mesh (Istio, Linkerd)",

        # DevOps & CI/CD in Cloud
        "CI/CD Pipelines", "GitHub Actions", "GitLab CI", "CircleCI", "Jenkins", "Bitbucket Pipelines",
        "Azure DevOps Pipelines", "CodePipeline (AWS)", "Artifact Repositories (JFrog, Nexus)",
        "Automated Testing", "Blue/Green Deployment", "Canary Deployment", "Rolling Updates",

        # Cloud Security & Compliance
        "IAM & Role Management", "Encryption at Rest & In Transit", "KMS (Key Management Service)",
        "Secrets Managers", "Cloud Firewall Configurations", "Security Groups & NACLs",
        "Cloud Compliance (SOC 2, ISO 27001, HIPAA, GDPR)", "WAF", "Cloud Audit Logs",
        "Vulnerability Scanning", "Penetration Testing Policies",

        # Networking in Cloud
        "VPC Setup", "Subnets", "Internet Gateway", "NAT Gateway", "Load Balancers",
        "Route Tables", "DNS Configuration", "VPN Setup", "Direct Connect", "Cloud CDN",
        "Multi-Region Deployment", "Availability Zones",

        # Monitoring, Logging & Observability
        "CloudWatch", "Azure Monitor", "GCP Stackdriver", "Prometheus", "Grafana", "New Relic",
        "Datadog", "ELK Stack", "Fluentd", "Logstash", "Application Insights", "Tracing with Jaeger",
        "Sentry", "Honeycomb", "OpenTelemetry",

        # Cloud Databases & Storage
        "S3", "Azure Blob Storage", "GCP Cloud Storage", "Amazon RDS", "Cloud SQL",
        "Cosmos DB", "Firestore", "Bigtable", "Amazon Aurora", "Elasticache", "Cloud Memorystore",
        "NoSQL & SQL in Cloud", "Multi-region Replication", "Read Replicas", "Backups & Snapshots",

        # Cloud Certifications
        "AWS Certified Solutions Architect", "AWS Certified Developer", "AWS Certified SysOps Admin",
        "Azure Fundamentals", "Azure Administrator", "Azure Developer", "GCP Associate Cloud Engineer",
        "GCP Professional Cloud Architect", "HashiCorp Certified Terraform Associate",

        # Soft Skills & Cloud Strategy
        "Cost Management", "Cloud Migration Strategy", "Cloud Native Architecture",
        "Lift & Shift vs Refactoring", "Vendor Lock-in Considerations", "Documentation & Runbooks",
        "Cross-team Collaboration", "Incident Management", "Change Management in Cloud Environments"
    ],
    
    "Photography & Editing": [
        # Photography Types & Specialties
        "Portrait Photography", "Product Photography", "Event Photography", "Wedding Photography",
        "Fashion Photography", "Food Photography", "Real Estate Photography", "Travel Photography",
        "Documentary Photography", "Street Photography", "Landscape Photography", "Wildlife Photography",
        "Sports Photography", "Pet Photography", "Commercial Photography", "Corporate Headshots",
        "Drone Photography", "Aerial Photography", "Architectural Photography", "Automotive Photography",

        # Camera & Equipment Handling
        "DSLR Photography", "Mirrorless Camera Operation", "Medium Format Cameras", "Point-and-Shoot Cameras",
        "Camera Settings (ISO, Aperture, Shutter Speed)", "Manual Mode Photography", "White Balance Adjustment",
        "Focal Length Understanding", "Lens Selection", "Tripod Usage", "Lighting Equipment", "Flash Photography",
        "Light Modifiers (Softboxes, Reflectors)", "Gimbal Operation", "Camera Stabilization", "Remote Triggering",

        # Composition & Shooting Techniques
        "Rule of Thirds", "Leading Lines", "Symmetry & Patterns", "Depth of Field", "Framing & Cropping",
        "Perspective Control", "Golden Hour Shooting", "Night Photography", "Long Exposure Techniques",
        "Bokeh Effects", "Macro Photography", "Panoramic Shots", "HDR Photography", "Burst Mode Shooting",
        "Bracketing", "Focus Stacking", "Self-Portrait Techniques",

        # Image Editing Software
        "Adobe Photoshop", "Adobe Lightroom", "Capture One", "Affinity Photo", "Luminar", "ON1 Photo RAW",
        "GIMP", "Darktable", "DxO PhotoLab", "Corel PaintShop Pro", "Pixlr", "Fotor", "Canva for Photo Editing",

        # Editing Techniques
        "RAW File Processing", "Exposure Correction", "Color Correction", "Color Grading", "Tone Curve Adjustments",
        "White Balance Adjustments", "Shadow & Highlight Recovery", "Sharpening & Noise Reduction",
        "Skin Retouching", "Eye Enhancement", "Teeth Whitening", "Object Removal", "Background Replacement",
        "Vignette Effects", "Dodging & Burning", "Split Toning", "Presets & LUTs", "Batch Editing",
        "Non-destructive Editing", "Layer Masking", "Cloning & Healing Tools", "High-Pass Sharpening",

        # Retouching & Special Effects
        "Beauty Retouching", "Frequency Separation", "Digital Makeup", "Body Contouring", "Liquify Tool Usage",
        "Composite Image Creation", "Double Exposure Effects", "Color Splash Effects", "Photo Manipulation",
        "Poster Design with Photos", "Cinematic Look Application", "Lens Flare Effects", "Light Leak Overlays",

        # Image Organization & Delivery
        "Photo Culling", "Metadata Management", "Keyword Tagging", "Collections & Albums",
        "Watermarking", "Photo Export Settings", "Web Optimization", "Print Optimization",
        "Client Galleries", "Online Portfolio Curation", "Cloud Backup", "Image Licensing Knowledge",

        # Printing & Formats
        "Print Resolution Setup", "Color Profile Management (sRGB, AdobeRGB, CMYK)", "Canvas Printing",
        "Metal Print Preparation", "Framing & Mounting Advice", "Photo Book Creation", "Album Design",
        "Photo Enlargement", "Photo Cropping for Print", "Aspect Ratio Conversion",

        # Photography Business Skills
        "Client Communication", "Booking & Scheduling", "Pricing Strategy", "Model Release Forms",
        "Contract & Licensing Agreements", "Photo Delivery Timelines", "Social Media Promotion",
        "Online Portfolio Setup", "Instagram for Photographers", "Client Feedback & Revisions",
        "Collaboration with Stylists & Models", "Event Coordination", "Branding for Photographers",

        # Drone & Aerial Skills
        "Drone Operation", "Drone Photography Techniques", "ND Filters for Drones",
        "Aerial Composition", "Flight Planning", "Drone Safety Guidelines", "Drone Licensing Regulations",
        "Panoramic Drone Shots", "Real Estate Drone Photography", "Drone Video Editing",

        # Mobile Photography & Editing
        "iPhone Photography", "Android Photography", "Mobile Camera Apps (Halide, ProCamera)",
        "VSCO Editing", "Snapseed", "Lightroom Mobile", "TouchRetouch", "Facetune", "Instagram Editing Tools",
        "Mobile Workflow Optimization", "Cloud Syncing from Mobile Devices"
    ],
    
    "Legal Consulting": [
        # Core Legal Services
        "Legal Research", "Contract Drafting", "Contract Review", "Legal Opinion Writing",
        "Legal Document Review", "Terms & Conditions Drafting", "Privacy Policy Drafting",
        "Service Agreement Drafting", "Non-Disclosure Agreements (NDAs)", "Partnership Agreements",
        "Employment Contracts", "Lease Agreements", "Purchase Agreements", "Franchise Agreements",
        "Shareholder Agreements", "Licensing Agreements", "Settlement Agreements",

        # Corporate & Business Law
        "Business Formation", "LLC/Corporation Setup", "Operating Agreements", "Corporate Governance",
        "Mergers & Acquisitions", "Due Diligence", "Compliance Checks", "Company Bylaws Drafting",
        "Startup Legal Consulting", "Fundraising Legal Support", "SAFE Agreements", "Convertible Notes",

        # Intellectual Property (IP) Law
        "Trademark Search", "Trademark Registration", "Copyright Registration", 
        "Patent Filing Assistance", "IP Licensing", "IP Transfer Agreements", 
        "Cease and Desist Letters", "IP Infringement Counseling", "DMCA Takedown Requests",
        "Trade Secret Protection", "Domain Name Disputes",

        # Employment & Labor Law
        "Employment Agreements", "Independent Contractor Agreements", "Employee Handbooks",
        "Disciplinary Action Documentation", "Termination Notices", "Non-compete Clauses",
        "Workplace Policies", "Wage and Hour Law", "Workplace Harassment Law", "Remote Work Agreements",
        "HR Policy Compliance", "Labor Union Negotiations Support",

        # International Law & Cross-border Consulting
        "Cross-border Transactions", "International Business Contracts", "FCPA Compliance",
        "GDPR Compliance", "Data Protection Regulations", "Immigration Documentation",
        "International Trade Law", "Export/Import Agreements", "Conflict of Laws Analysis",
        "UN, WTO, and ICC Law Support",

        # Litigation & Dispute Resolution
        "Demand Letters", "Litigation Strategy Consulting", "Pleadings Drafting", 
        "Discovery Process Support", "Legal Argument Development", "Arbitration Consulting",
        "Mediation Agreement Drafting", "Settlement Negotiation Assistance", 
        "Pre-trial Motions", "Evidence Analysis", "Expert Witness Preparation",

        # Regulatory & Compliance
        "Regulatory Research", "Industry-Specific Compliance (Healthcare, FinTech, Real Estate)",
        "Anti-Money Laundering (AML)", "Know Your Customer (KYC)", "HIPAA Compliance",
        "FTC Guidelines", "SEC Filings & Disclosures", "Corporate Compliance Audits",
        "Legal Risk Assessments", "Internal Investigations Support",

        # Real Estate & Property Law
        "Deed Preparation", "Title Review", "Purchase/Sale Agreements", 
        "Landlord-Tenant Agreements", "Eviction Notices", "HOA Guidelines",
        "Zoning & Land Use Consultations", "Real Estate Closing Documents", 
        "Lease Negotiation", "Rent Control Advice",

        # Legal Tech & Tools
        "Clio", "MyCase", "PracticePanther", "DocuSign", "Contractbook", "HelloSign",
        "Smokeball", "LegalZoom", "Rocket Lawyer", "Westlaw", "LexisNexis", "Casetext",
        "PACER", "Lawyaw", "Lawmatics", "Document Automation Tools", "eDiscovery Platforms",

        # Legal Writing & Communication
        "Legal Memos", "Case Briefs", "Court Submissions", "Client Letters", 
        "Negotiation Drafts", "Legal Blog Writing", "White Papers on Law Topics",
        "Professional Communication with Clients", "Clarity in Legal Language",

        # Soft Skills & Ethics
        "Confidentiality", "Legal Ethics", "Client Advocacy", "Attention to Detail",
        "Negotiation Skills", "Analytical Thinking", "Time Management for Legal Cases",
        "Billing & Time Tracking", "Multi-jurisdictional Awareness", "Cultural Sensitivity in International Law"
    ],
    
    "Music & Audio": [
        # Music Production
        "Music Composition", "Songwriting", "Audio Recording", "Arrangement", "Melody Creation",
        "Chord Progressions", "Instrumental Production", "Loop-Based Production", "Remixing",
        "Sample Pack Creation", "Beat Making", "Soundtrack Composition", "Royalty-Free Music Creation",

        # Digital Audio Workstations (DAWs)
        "FL Studio", "Ableton Live", "Logic Pro X", "Pro Tools", "Cubase", "Studio One",
        "GarageBand", "Reaper", "Reason", "Bitwig Studio", "BandLab", "Mixcraft", "Audacity",

        # Audio Editing
        "Audio Clipping Removal", "Noise Reduction", "EQ & Filtering", "Compressor & Limiter Usage",
        "Pitch Correction", "Time Stretching", "Fade In/Out", "Automation", "Stereo Imaging",
        "Audio Restoration", "Volume Balancing", "Reverb & Delay Effects", "Vocal Editing",
        "Spectral Editing", "Multitrack Editing",

        # Mixing & Mastering
        "Mixing Vocals", "Mixing Instruments", "Master Bus Processing", "Dynamic Range Control",
        "Multiband Compression", "Sidechain Compression", "De-essing", "Limiter Settings",
        "Reference Track Matching", "Loudness Normalization", "Mastering for Streaming Platforms",
        "Stem Mastering", "Stereo Widening", "Finalizing Audio Tracks",

        # Voiceover & Narration
        "Voice Acting", "Voiceover Recording", "IVR Recordings", "Explainer Video Voiceover",
        "Audiobook Narration", "Character Voice Creation", "Podcast Intros/Outros", 
        "E-learning Voiceover", "YouTube Voiceover", "Real Estate Tour Narration",

        # Podcast Production
        "Podcast Editing", "Intro/Outro Creation", "Noise Gate Setup", "Audio Equalization for Podcasts",
        "Remote Podcast Recording", "Multi-guest Audio Mixing", "Level Matching",
        "Podcast Hosting Setup", "RSS Feed Management", "Publishing to Apple/Spotify",
        "Podcast Jingles", "Podcast Sound Branding",

        # Sound Design
        "Synth Sound Design", "SFX Creation", "Foley Recording", "Ambient Soundscapes",
        "UI/UX Sounds", "Sound Libraries", "Field Recording", "Sound Layering",
        "Sci-Fi Sound Effects", "Fantasy Sounds", "Nature Sounds", "Urban Sounds",
        "Game Sound Design", "Film Sound Design", "Surround Sound Design",

        # Music for Media
        "Scoring for Film", "TV Commercial Music", "Jingle Production", "Documentary Soundtracks",
        "Theatre & Stage Sound", "Animation Scoring", "Mobile Game Soundtracks", 
        "Advertising Audio", "YouTube Background Music", "Twitch Sound Alerts",
        "Instagram Reel Music", "TikTok Sound Bites",

        # Musical Instruments (Recording & Editing)
        "Guitar Recording", "Piano Recording", "Drum Programming", "Bassline Editing",
        "Virtual Instruments (VSTs)", "MIDI Editing", "Acoustic Instrument Miking",
        "Synth Layering", "Live Instrument Integration", "Session Instrument Arrangement",

        # Music Distribution & Metadata
        "Uploading to Spotify", "DistroKid", "TuneCore", "CD Baby", "Music Metadata Tagging",
        "ISRC/UPC Code Assignment", "Royalty Collection", "Split Sheet Management",
        "Music Licensing", "Sync Licensing", "Music Copyrighting",

        # Tools & Plugins
        "Waves Plugins", "FabFilter", "Native Instruments Komplete", "iZotope Suite",
        "Kontakt Libraries", "Serum", "Omnisphere", "Ozone Mastering Suite",
        "Melodyne", "Auto-Tune", "Valhalla Reverb", "Slate Digital Plugins", "Splice Sounds",

        # Soft Skills & Workflow
        "Creative Direction", "Client Collaboration", "Project Organization",
        "Revision Handling", "Deadlines in Audio Work", "Mood Boards for Music",
        "Remote Production Workflow", "Audio File Delivery Standards", "Bit Depth & Sample Rate Knowledge"
    ],
    
    "HR & Recruiting": [
        # Talent Acquisition
        "Job Description Writing", "Job Posting Optimization", "Sourcing Candidates",
        "Boolean Search", "LinkedIn Recruiting", "Indeed / Glassdoor / Naukri Usage",
        "Candidate Screening", "Interview Scheduling", "Applicant Tracking Systems (ATS)",
        "Headhunting", "Campus Recruitment", "Executive Search", "Diversity Hiring",
        "Freelancer Sourcing", "Referral Program Management", "Pipeline Management",

        # Interviewing & Evaluation
        "Resume Screening", "Behavioral Interviewing", "Technical Interviewing",
        "Situational Interviewing", "Competency-Based Interviews", "Panel Interviews",
        "Pre-screen Calls", "Video Interview Tools (Zoom, HireVue)", "Assessment Coordination",
        "Scoring Rubrics", "Candidate Evaluation Forms", "Post-Interview Feedback Collection",

        # Onboarding & Orientation
        "New Hire Onboarding", "Preboarding Setup", "Orientation Design", "Policy Acknowledgments",
        "Document Collection", "Welcome Kit Management", "Mentorship Matching",
        "30/60/90 Day Planning", "Onboarding Checklists", "Probation Period Setup",
        "Exit Interview Planning (For Reverse Mentoring)",

        # HR Operations
        "Employee Records Management", "HRIS Tools (BambooHR, Zoho People, Gusto)",
        "Attendance & Leave Tracking", "Timesheet Management", "Payroll Coordination",
        "HR Compliance Documentation", "Employee Handbook Creation", "Organization Chart Management",
        "Offer Letter Creation", "Promotion Letters", "Experience Certificates",
        "Compliance with Labor Laws", "EPF/ESIC/Gratuity Handling (India)", "401k and Benefits Setup",

        # Performance & Training
        "Performance Review Scheduling", "KPI Tracking", "360-Degree Feedback Collection",
        "LMS Management (Learning Management Systems)", "Training Calendar Coordination",
        "Workshop Setup", "E-learning Tools (Udemy, Coursera for Business)", "Soft Skills Development",
        "Technical Skills Gap Analysis", "Career Path Planning", "Certification Management",
        "Succession Planning", "Leadership Training Programs",

        # Employee Engagement & Retention
        "Employee Surveys", "Engagement Programs", "Pulse Check Tools", "Virtual Team Building",
        "Recognition & Rewards Program", "Employee Wellness Programs", "Remote Culture Development",
        "Anniversary & Birthday Programs", "Offsite Planning", "Feedback Loops", "Townhall Setup",

        # Compensation & Benefits
        "Salary Benchmarking", "Compensation Planning", "Bonus Structure Drafting",
        "Equity/ESOP Handling", "Salary Breakup Structuring", "Tax Compliance on Payroll",
        "Benefits Administration", "Insurance Policy Coordination", "Flexible Work Arrangement Policies",

        # Exit & Offboarding
        "Resignation Handling", "Exit Interviews", "Final Settlement Processing",
        "Knowledge Transfer Coordination", "Clearance Checklist Management",
        "Exit Survey Design", "Voluntary vs Involuntary Exit Differentiation",

        # Recruitment Tools & Platforms
        "Greenhouse", "Lever", "Workable", "Breezy HR", "SmartRecruiters", "Zoho Recruit",
        "Freshteam", "JazzHR", "Jobvite", "Recruitee", "Hireology", "Manatal", "Recruit CRM",
        "Calendly for Interviews", "Google Calendar Sync", "Slack for HR Coordination",

        # Soft Skills & Legal
        "Confidentiality Handling", "Conflict Resolution", "Employee Advocacy", "Negotiation",
        "HR Ethics", "Communication Skills", "Multitasking", "Empathy in HR",
        "Labor Law Awareness", "HR Documentation Standards", "GDPR for Recruiters",
        "Hiring Compliance", "Diversity & Inclusion Policy Awareness", "Bias-Free Hiring",
        "HR Reporting & Analytics", "Attrition Analysis", "Hiring Funnel Optimization"
    ]
}

    
    
