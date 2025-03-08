from dateutil.relativedelta import relativedelta
from datetime import datetime
from math import floor
import json
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import FileSystemStorage
from accounts.models import Freelancer
from accounts.mixins import CustomLoginRequiredMixin
from projects.models import Skill
from .models import Education, Certificate
from .utils import *

# Testing Complete
class UserBasicInfoView(CustomLoginRequiredMixin, View):
    profile_template = 'freelancerprofile/profile.html'
    home_url = 'homes:home'

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            educations = list(Education.objects.filter(freelancer_id=freelancer))
            certificates = list(Certificate.objects.filter(freelancer_id=freelancer)) 

            experience_years = freelancer.experience_years
            if experience_years is not None:
                if experience_years == 0:
                    experience_display = "Less than a year"
                elif experience_years == 1:
                    experience_display = "1+ year"
                else:
                    experience_display = f"{experience_years}+ years"
            else:
                experience_display = "Not Provided"

            current_date = datetime.now()

            educations_with_duration = []
            if educations:
                for edu in educations:
                    educations_with_duration.append({
                        'education': edu,
                        'is_current': edu.end_date is None,
                        'start_date': edu.start_date,
                        'end_date': edu.end_date or current_date,
                    })
                educations_with_duration.sort(key=lambda x: (
                    not x['is_current'],  
                    -datetime.combine(x['start_date'], datetime.min.time()).timestamp() if x['is_current'] else -datetime.combine(x['end_date'], datetime.min.time()).timestamp()
                ))

            certificates_sorted = []
            if certificates:
                certificates_sorted = sorted(certificates, key=lambda x: x.issued_date, reverse=True)

            return render(request, self.profile_template, {
                'freelancer': freelancer,
                'experience_display': experience_display,
                'educations_with_duration': educations_with_duration,
                'certificates': certificates_sorted,  
                'current_year': current_date.year
            })
    
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.home_url)

# Testing Complete
class EditProfileImageView(CustomLoginRequiredMixin, View):
    edit_profile_template = 'freelancerprofile/editprofileimage.html'
    edit_profile_url = 'freelancer:edit-profile-image'
    freelancer_profile_url = 'freelancer:profile'

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            return render(request, self.edit_profile_template, {'freelancer': freelancer})
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)

    def post(self, request):
        try:
            profile_image = request.FILES.get('profile_image')
            username = request.POST.get('username')

            if profile_image:
                valid, error_message = validate_profile_image(profile_image)
                if not valid:
                    messages.error(request, error_message)
                    return render(request, self.edit_profile_template, {'last_username': username})
            
            if not username:
                messages.error(request, 'Username cannot be empty.')
                return render(request, self.edit_profile_template, {'last_username': username})

            valid, error_message = validate_username(username, request)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.edit_profile_template, {'last_username': username})
            user = request.user
            user.username = username
            if profile_image:
                fs = FileSystemStorage(location='media/profile_images')
                filename = fs.save(profile_image.name, profile_image)
                user.profile_image = filename.split('/')[-1]
             
            user.save()
            messages.success(request, 'Your profile has been successfully updated.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_profile_url)
    
# Testing Complete
class EditPersonalInfoView(CustomLoginRequiredMixin, View):
    personal_details_template = 'freelancerprofile/editpersonalinfo.html'
    personal_details_url = 'freelancer:edit-personal-info'
    freelancer_profile_url = 'freelancer:profile'

    available_languages = [
        'English', 'Nepali', 'Hindi', 'Chinese', 'Urdu', 'Spanish', 'French', 
        'Arabic', 'German', 'Russian', 'Portuguese', 'Japanese', 'Korean', 
        'Italian', 'Dutch', 'Turkish', 'Persian', 'Bengali', 'Swahili', 'Polish',
        'Thai', 'Vietnamese', 'Tagalog', 'Greek', 'Swedish', 'Czech'
    ]

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            selected_languages = freelancer.languages.split(',') if freelancer.languages else []
            selected_languages = [lang.strip() for lang in selected_languages if lang.strip()]
            
            return render(request, self.personal_details_template, {
                'freelancer': freelancer,
                'available_languages': self.available_languages,
                'selected_languages': selected_languages
            })
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)

    def post(self, request):
        try:
            user = request.user
            freelancer = Freelancer.objects.get(user=user)
            
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            phone_number = request.POST.get('phone_number')
            languages_selected = request.POST.getlist('languages-select')
            bio = request.POST.get('bio')

            form_data = {
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone_number,
                'bio': bio,
                'languages_selected': languages_selected
            }

            valid, error_message = validate_personal_info(first_name, last_name, phone_number, bio, languages_selected, request)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.personal_details_template, {
                    'form_data': form_data,
                    'freelancer': freelancer,
                    'selected_languages': languages_selected,
                    'available_languages': self.available_languages
                })
                
            user.first_name = first_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.save()

            freelancer.bio = bio
            freelancer.languages = ','.join(languages_selected)
            freelancer.save()

            messages.success(request, 'Your profile has been successfully updated.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)
            
# Testing Complete
class EditUserAddressView(CustomLoginRequiredMixin, View):
    address_template = 'freelancerprofile/editaddress.html'
    address_url = 'freelancer:edit-address'
    freelancer_profile_url = 'freelancer:profile'
    
    countries_and_cities = {
        "Afghanistan": ["Kabul", "Kandahar", "Herat", "Mazar-i-Sharif", "Jalalabad", "Other"],
        "Albania": ["Tirana", "Durrës", "Vlorë", "Shkodër", "Fier", "Other"],
        "Algeria": ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Other"],
        "Andorra": ["Andorra la Vella", "Escaldes-Engordany", "Encamp", "Sant Julià de Lòria", "La Massana", "Other"],
        "Angola": ["Luanda", "N'dalatando", "Huambo", "Lobito", "Benguela", "Other"],
        "Antigua and Barbuda": ["St. John's", "All Saints", "Liberta", "Potters Village", "Bolans", "Other"],
        "Argentina": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "La Plata", "Other"],
        "Armenia": ["Yerevan", "Gyumri", "Vanadzor", "Vagharshapat", "Hrazdan", "Other"],
        "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Other"],
        "Austria": ["Vienna", "Graz", "Linz", "Salzburg", "Innsbruck", "Other"],
        "Azerbaijan": ["Baku", "Ganja", "Sumqayit", "Mingachevir", "Khirdalan", "Other"],
        "Bahamas": ["Nassau", "Freeport", "West End", "Coopers Town", "Marsh Harbour", "Other"],
        "Bahrain": ["Manama", "Riffa", "Muharraq", "Hamad Town", "A'ali", "Other"],
        "Bangladesh": ["Dhaka", "Chittagong", "Khulna", "Rajshahi", "Sylhet", "Other"],
        "Barbados": ["Bridgetown", "Speightstown", "Oistins", "Holetown", "Bathsheba", "Other"],
        "Belarus": ["Minsk", "Gomel", "Mogilev", "Vitebsk", "Grodno", "Other"],
        "Belgium": ["Brussels", "Antwerp", "Ghent", "Charleroi", "Liège", "Other"],
        "Belize": ["Belmopan", "Belize City", "San Ignacio", "Orange Walk", "Dangriga", "Other"],
        "Benin": ["Porto-Novo", "Cotonou", "Parakou", "Djougou", "Bohicon", "Other"],
        "Bhutan": ["Thimphu", "Phuntsholing", "Paro", "Gelephu", "Samdrup Jongkhar", "Other"],
        "Bolivia": ["La Paz", "Santa Cruz", "Cochabamba", "Sucre", "Oruro", "Other"],
        "Bosnia and Herzegovina": ["Sarajevo", "Banja Luka", "Tuzla", "Zenica", "Mostar", "Other"],
        "Botswana": ["Gaborone", "Francistown", "Molepolole", "Maun", "Serowe", "Other"],
        "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Other"],
        "Brunei": ["Bandar Seri Begawan", "Kuala Belait", "Tutong", "Bangar", "Seria", "Other"],
        "Bulgaria": ["Sofia", "Plovdiv", "Varna", "Burgas", "Ruse", "Other"],
        "Burkina Faso": ["Ouagadougou", "Bobo-Dioulasso", "Koudougou", "Banfora", "Ouahigouya", "Other"],
        "Burundi": ["Bujumbura", "Gitega", "Muyinga", "Ruyigi", "Ngozi", "Other"],
        "Cambodia": ["Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville", "Kampong Cham", "Other"],
        "Cameroon": ["Yaoundé", "Douala", "Bamenda", "Garoua", "Maroua", "Other"],
        "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Ottawa", "Other"],
        "Cape Verde": ["Praia", "Mindelo", "Santa Maria", "Assomada", "São Filipe", "Other"],
        "Central African Republic": ["Bangui", "Bimbo", "Berbérati", "Carnot", "Bambari", "Other"],
        "Chad": ["N'Djamena", "Moundou", "Sarh", "Abéché", "Am Timan", "Other"],
        "Chile": ["Santiago", "Valparaíso", "Concepción", "La Serena", "Antofagasta", "Other"],
        "China": ["Shanghai", "Beijing", "Guangzhou", "Shenzhen", "Chongqing", "Other"],
        "Colombia": ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Other"],
        "Comoros": ["Moroni", "Mutsamudu", "Fomboni", "Domoni", "Tsimbeo", "Other"],
        "Congo": ["Brazzaville", "Pointe-Noire", "Dolisie", "Nkayi", "Kindamba", "Other"],
        "Costa Rica": ["San José", "Alajuela", "Cartago", "Heredia", "Liberia", "Other"],
        "Croatia": ["Zagreb", "Split", "Rijeka", "Osijek", "Zadar", "Other"],
        "Cuba": ["Havana", "Santiago de Cuba", "Camagüey", "Holguín", "Guantánamo", "Other"],
        "Cyprus": ["Nicosia", "Limassol", "Larnaca", "Paphos", "Famagusta", "Other"],
        "Czech Republic": ["Prague", "Brno", "Ostrava", "Pilsen", "Liberec", "Other"],
        "Democratic Republic of the Congo": ["Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kananga", "Kisangani", "Other"],
        "Denmark": ["Copenhagen", "Aarhus", "Odense", "Aalborg", "Frederiksberg", "Other"],
        "Djibouti": ["Djibouti City", "Ali Sabieh", "Tadjoura", "Obock", "Dikhil", "Other"],
        "Dominica": ["Roseau", "Portsmouth", "Marigot", "Grand Bay", "Castle Bruce", "Other"],
        "Dominican Republic": ["Santo Domingo", "Santiago", "La Romana", "San Pedro", "Puerto Plata", "Other"],
        "East Timor": ["Dili", "Baucau", "Lospalos", "Same", "Aileu", "Other"],
        "Ecuador": ["Quito", "Guayaquil", "Cuenca", "Machala", "Manta", "Other"],
        "Egypt": ["Cairo", "Alexandria", "Giza", "Shubra El Kheima", "Port Said", "Other"],
        "El Salvador": ["San Salvador", "Santa Ana", "San Miguel", "Mejicanos", "Apopa", "Other"],
        "Equatorial Guinea": ["Malabo", "Bata", "Ebebiyin", "Aconibe", "Anisok", "Other"],
        "Eritrea": ["Asmara", "Keren", "Massawa", "Assab", "Mendefera", "Other"],
        "Estonia": ["Tallinn", "Tartu", "Narva", "Pärnu", "Kohtla-Järve", "Other"],
        "Eswatini": ["Mbabane", "Manzini", "Big Bend", "Siteki", "Piggs Peak", "Other"],
        "Ethiopia": ["Addis Ababa", "Dire Dawa", "Mek'ele", "Gondar", "Adama", "Other"],
        "Fiji": ["Suva", "Lautoka", "Nadi", "Labasa", "Ba", "Other"],
        "Finland": ["Helsinki", "Espoo", "Tampere", "Vantaa", "Oulu", "Other"],
        "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Other"],
        "Gabon": ["Libreville", "Port-Gentil", "Franceville", "Oyem", "Moanda", "Other"],
        "Gambia": ["Banjul", "Serekunda", "Brikama", "Bakau", "Farafenni", "Other"],
        "Georgia": ["Tbilisi", "Batumi", "Kutaisi", "Rustavi", "Gori", "Other"],
        "Germany": ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Other"],
        "Ghana": ["Accra", "Kumasi", "Tamale", "Sekondi-Takoradi", "Sunyani", "Other"],
        "Greece": ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Other"],
        "Grenada": ["St. George's", "Grenville", "Gouyave", "Victoria", "Sauteurs", "Other"],
        "Guatemala": ["Guatemala City", "Mixco", "Villa Nueva", "Petapa", "Quetzaltenango", "Other"],
        "Guinea": ["Conakry", "Nzérékoré", "Kankan", "Kindia", "Labé", "Other"],
        "Guinea-Bissau": ["Bissau", "Bafatá", "Gabú", "Bissorã", "Bolama", "Other"],
        "Guyana": ["Georgetown", "Linden", "New Amsterdam", "Anna Regina", "Bartica", "Other"],
        "Haiti": ["Port-au-Prince", "Cap-Haïtien", "Carrefour", "Delmas", "Pétionville", "Other"],
        "Honduras": ["Tegucigalpa", "San Pedro Sula", "Choloma", "La Ceiba", "El Progreso", "Other"],
        "Hungary": ["Budapest", "Debrecen", "Szeged", "Miskolc", "Pécs", "Other"],
        "Iceland": ["Reykjavík", "Kópavogur", "Hafnarfjörður", "Akureyri", "Reykjanesbær", "Other"],
        "India": ["Mumbai", "Delhi", "Bangalore", "Kolkata", "Chennai", "Other"],
        "Indonesia": ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Other"],
        "Iran": ["Tehran", "Mashhad", "Isfahan", "Karaj", "Shiraz", "Other"],
        "Iraq": ["Baghdad", "Basra", "Mosul", "Erbil", "Najaf", "Other"],
        "Ireland": ["Dublin", "Cork", "Limerick", "Galway", "Waterford", "Other"],
        "Israel": ["Jerusalem", "Tel Aviv", "Haifa", "Rishon LeZion", "Petah Tikva", "Other"],
        "Italy": ["Rome", "Milan", "Naples", "Turin", "Palermo", "Other"],
        "Jamaica": ["Kingston", "Montego Bay", "Spanish Town", "Portmore", "Mandeville", "Other"],
        "Japan": ["Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo", "Other"],
        "Jordan": ["Amman", "Zarqa", "Irbid", "Russeifa", "Aqaba", "Other"],
        "Kazakhstan": ["Almaty", "Nur-Sultan", "Shymkent", "Karaganda", "Aktobe", "Other"],
        "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Other"],
        "Kiribati": ["South Tarawa", "Betio", "Bikenibeu", "Teaoraereke", "Bairiki", "Other"],
        "Kosovo": ["Pristina", "Prizren", "Ferizaj", "Pejë", "Gjakova", "Other"],
        "Kuwait": ["Kuwait City", "Jahrah", "Salmiya", "Hawally", "Farwaniya", "Other"],
        "Kyrgyzstan": ["Bishkek", "Osh", "Jalal-Abad", "Karakol", "Tokmok", "Other"],
        "Laos": ["Vientiane", "Pakse", "Savannakhet", "Luang Prabang", "Thakhek", "Other"],
        "Latvia": ["Riga", "Daugavpils", "Liepāja", "Jelgava", "Jūrmala", "Other"],
        "Lebanon": ["Beirut", "Tripoli", "Sidon", "Tyre", "Jounieh", "Other"],
        "Lesotho": ["Maseru", "Teyateyaneng", "Mafeteng", "Hlotse", "Mohale's Hoek", "Other"],
        "Liberia": ["Monrovia", "Gbarnga", "Buchanan", "Kakata", "Voinjama", "Other"],
        "Libya": ["Tripoli", "Benghazi", "Misrata", "Tarhuna", "Al Khums", "Other"],
        "Liechtenstein": ["Vaduz", "Schaan", "Triesen", "Balzers", "Eschen", "Other"],
        "Lithuania": ["Vilnius", "Kaunas", "Klaipėda", "Šiauliai", "Panevėžys", "Other"],
        "Luxembourg": ["Luxembourg City", "Esch-sur-Alzette", "Dudelange", "Differdange", "Ettelbruck", "Other"],
        "Madagascar": ["Antananarivo", "Toamasina", "Antsirabe", "Fianarantsoa", "Mahajanga", "Other"],
        "Malawi": ["Lilongwe", "Blantyre", "Mzuzu", "Zomba", "Kasungu", "Other"],
        "Malaysia": ["Kuala Lumpur", "George Town", "Ipoh", "Shah Alam", "Petaling Jaya", "Other"],
        "Maldives": ["Malé", "Addu City", "Fuvahmulah", "Kulhudhuffushi", "Thinadhoo", "Other"],
        "Mali": ["Bamako", "Sikasso", "Ségou", "Mopti", "Koutiala", "Other"],
        "Malta": ["Valletta", "Birkirkara", "Qormi", "Mosta", "Zabbar", "Other"],
        "Marshall Islands": ["Majuro", "Ebeye", "Laura", "Arno", "Jabor", "Other"],
        "Mauritania": ["Nouakchott", "Nouadhibou", "Kiffa", "Kaédi", "Rosso", "Other"],
        "Mauritius": ["Port Louis", "Beau Bassin-Rose Hill", "Vacoas", "Curepipe", "Quatre Bornes", "Other"],
        "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "Other"],
        "Micronesia": ["Palikir", "Kolonia", "Weno", "Tofol", "Colonia", "Other"],
        "Moldova": ["Chișinău", "Bălți", "Comrat", "Hîncești", "Orhei", "Other"],
        "Monaco": ["Monte Carlo", "La Condamine", "Fontvieille", "Monaco-Ville", "Moneghetti", "Other"],
        "Mongolia": ["Ulaanbaatar", "Erdenet", "Darkhan", "Choibalsan", "Moron", "Other"],
        "Montenegro": ["Podgorica", "Nikšić", "Herceg Novi", "Pljevlja", "Bar", "Other"],
        "Morocco": ["Casablanca", "Rabat", "Fez", "Marrakesh", "Tangier", "Other"],
        "Mozambique": ["Maputo", "Matola", "Beira", "Nampula", "Chimoio", "Other"],
        "Myanmar": ["Yangon", "Mandalay", "Naypyidaw", "Mawlamyine", "Bago", "Other"],
        "Namibia": ["Windhoek", "Walvis Bay", "Swakopmund", "Oshakati", "Rundu", "Other"],
        "Nauru": ["Yaren", "Denigomodu", "Aiwo", "Boe", "Buada", "Other"],
        "Nepal": ["Kathmandu", "Pokhara", "Lalitpur", "Bharatpur", "Birgunj", "Other"],
        "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Other"],
        "New Zealand": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Tauranga", "Other"],
        "Nicaragua": ["Managua", "León", "Masaya", "Matagalpa", "Chinandega", "Other"],
        "Niger": ["Niamey", "Zinder", "Maradi", "Agadez", "Tahoua", "Other"],
        "Nigeria": ["Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt", "Other"],
        "North Korea": ["Pyongyang", "Hamhung", "Chongjin", "Nampo", "Wonsan", "Other"],
        "North Macedonia": ["Skopje", "Bitola", "Kumanovo", "Prilep", "Tetovo", "Other"],
        "Norway": ["Oslo", "Bergen", "Trondheim", "Stavanger", "Drammen", "Other"],
        "Oman": ["Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Other"],
        "Pakistan": ["Karachi", "Lahore", "Islamabad", "Faisalabad", "Rawalpindi", "Other"],
        "Palau": ["Ngerulmud", "Koror", "Melekeok", "Airai", "Kloulklubed", "Other"],
        "Palestine": ["East Jerusalem", "Gaza", "Hebron", "Nablus", "Ramallah", "Other"],
        "Panama": ["Panama City", "San Miguelito", "David", "Arraiján", "La Chorrera", "Other"],
        "Papua New Guinea": ["Port Moresby", "Lae", "Mount Hagen", "Madang", "Goroka", "Other"],
        "Paraguay": ["Asunción", "Ciudad del Este", "San Lorenzo", "Luque", "Capiatá", "Other"],
        "Peru": ["Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Other"],
        "Philippines": ["Manila", "Quezon City", "Davao", "Cebu", "Makati", "Other"],
        "Poland": ["Warsaw", "Kraków", "Łódź", "Wrocław", "Poznań", "Other"],
        "Portugal": ["Lisbon", "Porto", "Vila Nova de Gaia", "Amadora", "Braga", "Other"],
        "Qatar": ["Doha", "Al Wakrah", "Al Khor", "Al Rayyan", "Umm Salal", "Other"],
        "Romania": ["Bucharest", "Cluj-Napoca", "Timișoara", "Iași", "Constanța", "Other"],
        "Russia": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan", "Other"],
        "Rwanda": ["Kigali", "Butare", "Gitarama", "Ruhengeri", "Gisenyi", "Other"],
        "Saint Kitts and Nevis": ["Basseterre", "Charlestown", "Sandy Point", "Cayon", "Gingerland", "Other"],
        "Saint Lucia": ["Castries", "Vieux Fort", "Micoud", "Dennery", "Soufrière", "Other"],
        "Saint Vincent and the Grenadines": ["Kingstown", "Arnos Vale", "Layou", "Barrouallie", "Georgetown", "Other"],
        "Samoa": ["Apia", "Asau", "Mulifanua", "Afega", "Vaitele", "Other"],
        "San Marino": ["San Marino", "Dogana", "Borgo Maggiore", "Serravalle", "Domagnano", "Other"],
        "São Tomé and Príncipe": ["São Tomé", "Santo António", "Neves", "Santana", "Trinidad", "Other"],
        "Saudi Arabia": ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Other"],
        "Senegal": ["Dakar", "Touba", "Thiès", "Rufisque", "Kaolack", "Other"],
        "Serbia": ["Belgrade", "Novi Sad", "Niš", "Kragujevac", "Subotica", "Other"],
        "Seychelles": ["Victoria", "Anse Boileau", "Beau Vallon", "Cascade", "Takamaka", "Other"],
        "Sierra Leone": ["Freetown", "Bo", "Kenema", "Makeni", "Koidu", "Other"],
        "Singapore": ["Singapore", "Woodlands", "Tampines", "Jurong East", "Hougang", "Other"],
        "Slovakia": ["Bratislava", "Košice", "Prešov", "Žilina", "Banská Bystrica", "Other"],
        "Slovenia": ["Ljubljana", "Maribor", "Celje", "Kranj", "Velenje", "Other"],
        "Solomon Islands": ["Honiara", "Auki", "Gizo", "Kirakira", "Tulagi", "Other"],
        "Somalia": ["Mogadishu", "Hargeisa", "Bosaso", "Kismayo", "Merca", "Other"],
        "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Other"],
        "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Other"],
        "South Sudan": ["Juba", "Wau", "Malakal", "Yei", "Yambio", "Other"],
        "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Other"],
        "Sri Lanka": ["Colombo", "Kandy", "Galle", "Jaffna", "Negombo", "Other"],
        "Sudan": ["Khartoum", "Omdurman", "Nyala", "Port Sudan", "Kassala", "Other"],
        "Suriname": ["Paramaribo", "Lelydorp", "Nieuw Nickerie", "Moengo", "Brownsweg", "Other"],
        "Sweden": ["Stockholm", "Gothenburg", "Malmö", "Uppsala", "Västerås", "Other"],
        "Switzerland": ["Zürich", "Geneva", "Basel", "Lausanne", "Bern", "Other"],
        "Syria": ["Damascus", "Aleppo", "Homs", "Latakia", "Hama", "Other"],
        "Taiwan": ["Taipei", "Kaohsiung", "Taichung", "Tainan", "New Taipei", "Other"],
        "Tajikistan": ["Dushanbe", "Khujand", "Kulob", "Bokhtar", "Isfara", "Other"],
        "Tanzania": ["Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya", "Other"],
        "Thailand": ["Bangkok", "Nonthaburi", "Nakhon Ratchasima", "Chiang Mai", "Hat Yai", "Other"],
        "Togo": ["Lomé", "Sokodé", "Kara", "Kpalimé", "Atakpamé", "Other"],
        "Tonga": ["Nuku'alofa", "Neiafu", "Pangai", "Ohonua", "Vaini", "Other"],
        "Trinidad and Tobago": ["Port of Spain", "San Fernando", "Chaguanas", "Arima", "Point Fortin", "Other"],
        "Tunisia": ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte", "Other"],
        "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Other"],
        "Turkmenistan": ["Ashgabat", "Türkmenabat", "Daşoguz", "Mary", "Balkanabat", "Other"],
        "Tuvalu": ["Funafuti", "Alapi", "Senala", "Savave", "Tanrake", "Other"],
        "Uganda": ["Kampala", "Gulu", "Lira", "Mbarara", "Jinja", "Other"],
        "Ukraine": ["Kyiv", "Kharkiv", "Odesa", "Dnipro", "Donetsk", "Other"],
        "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman", "Other"],
        "United Kingdom": ["London", "Birmingham", "Manchester", "Glasgow", "Liverpool", "Other"],
        "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Other"],
        "Uruguay": ["Montevideo", "Salto", "Ciudad de la Costa", "Paysandú", "Las Piedras", "Other"],
        "Uzbekistan": ["Tashkent", "Namangan", "Samarkand", "Andijan", "Nukus", "Other"],
        "Vanuatu": ["Port Vila", "Luganville", "Norsup", "Isangel", "Sola", "Other"],
        "Vatican City": ["Vatican City", "Other"],
        "Venezuela": ["Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maracay", "Other"],
        "Vietnam": ["Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong", "Can Tho", "Other"],
        "Yemen": ["Sana'a", "Aden", "Taiz", "Al Hudaydah", "Ibb", "Other"],
        "Zambia": ["Lusaka", "Kitwe", "Ndola", "Kabwe", "Chingola", "Other"],
        "Zimbabwe": ["Harare", "Bulawayo", "Chitungwiza", "Mutare", "Gweru", "Other"]
    }

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            countries_and_cities_json = json.dumps(self.countries_and_cities)
            
            return render(request, self.address_template, {
                'freelancer': freelancer,
                'countries_and_cities': self.countries_and_cities,
                'countries_and_cities_json': countries_and_cities_json,
            })
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)

    def post(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            
            country = request.POST.get('country')
            city = request.POST.get('city')
            if not country or not city:
                messages.error(request, "Both country and city are required.")
                return render(request, self.address_template, {
                    'freelancer': freelancer,
                    'countries_and_cities': self.countries_and_cities,
                    'countries_and_cities_json': json.dumps(self.countries_and_cities)
                })
            
            freelancer.country = country
            freelancer.city = city
            freelancer.save()
            
            messages.success(request, 'Your profile has been successfully updated.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.address_url)
        
# Testing Complete
class EditUserSkillsView(CustomLoginRequiredMixin, View):
    skills_template = 'freelancerprofile/editskills.html'
    skills_url = 'freelancer:edit-skill'
    freelancer_profile_url = 'freelancer:profile'

    def get(self, request):
        try:
            freelancer = Freelancer.objects.get(user=request.user)
            skills = Skill.objects.all().order_by('name')
            selected_skills = freelancer.skills.values_list('id', flat=True)

            context = {
                'freelancer': freelancer,
                'skills': skills,
                'skills_select': selected_skills,  
            }

            return render(request, self.skills_template, context)
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    def post(self, request):
        try:
            skills = Skill.objects.all().order_by('name')
            freelancer = Freelancer.objects.get(user=request.user)
            
            experience = request.POST.get('experience')
            hourly_rate = request.POST.get('hourly-rate')
            selected_skills = request.POST.getlist('skills-select')
            selected_skills = [int(skill_id) for skill_id in selected_skills]
            
            context = {
                'freelancer': freelancer,
                'experience': experience,
                'hourly_rate': hourly_rate,
                'skills_select': selected_skills,
                'skills': skills,  
            }

            is_valid, error_message = validate_freelancer_skills_form(experience, hourly_rate, selected_skills)
            if not is_valid:
                messages.error(request, error_message)
                return render(request, self.skills_template, context)
            
            freelancer = Freelancer.objects.get(user=request.user)
            experience = int(experience)
            freelancer.experience_years = experience
            freelancer.hourly_rate = hourly_rate
            
            freelancer.skills.clear() 
            skills = Skill.objects.filter(id__in=selected_skills)
            freelancer.skills.add(*skills)  

            freelancer.save()

            messages.success(request, 'Your profile has been successfully updated.')
            return redirect(self.freelancer_profile_url)

        except Exception:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect(self.skills_url) 
        
# Testing Complete
class AddEducationView(CustomLoginRequiredMixin, View):
    education_form_template = 'freelancerprofile/addeducation.html'
    education_form_url = 'freelancer:add-new-education'
    freelancer_profile_url = 'freelancer:profile'

    months = {
        "jan": "January",
        "feb": "February",
        "mar": "March",
        "apr": "April",
        "may": "May",
        "jun": "June",
        "jul": "July",
        "aug": "August",
        "sep": "September",
        "oct": "October",
        "nov": "November",
        "dec": "December",
    }
    current_year = datetime.now().year
    years = {str(year): year for year in range(current_year, 1979, -1)}
    
    def get(self, request):
        context = {
            'months': self.months,
            'years': self.years,
        }
        return render(request, self.education_form_template, context)
    
    def post(self, request):            
        try:
            institution_logo = request.FILES.get('institution_logo')  
            institution_name = request.POST.get('institution_name')  
            level = request.POST.get('level')  
            start_month = request.POST.get('start_month')  
            start_year = request.POST.get('start_year')  
            end_month = request.POST.get('end_month')  
            end_year = request.POST.get('end_year')  
            location = request.POST.get('location')  
            currently_studying = request.POST.get('currently_studying')
        
            context = {
                'institution_name': institution_name,
                'level': level,
                'start_month': start_month,
                'start_year': start_year,
                'end_month': end_month,
                'end_year': end_year,
                'location': location,
                'currently_studying': currently_studying,
                'months': self.months,
                'years': self.years,
            }
        
            valid, error_message = validate_education(
                institution_logo, institution_name, level, start_month, start_year, 
                end_month, end_year, location, currently_studying, self.months
            )
        
            if not valid:
                messages.error(request, error_message)
                return render(request, self.education_form_template, context)
            
            if start_month and start_year:
                start_month_name = self.months.get(start_month)
                start_date_str = f"{start_month_name}-{start_year}"
                start_date = datetime.strptime(start_date_str, "%B-%Y").date()
            else:
                start_date = None
            
            if not currently_studying and end_month and end_year:
                end_month_name = self.months.get(end_month)
                end_date_str = f"{end_month_name}-{end_year}"
                end_date = datetime.strptime(end_date_str, "%B-%Y").date()
            else:
                end_date = None
                
            freelancer = Freelancer.objects.get(user=request.user)
            education = Education.objects.create(
                institution=institution_name,
                education_level=level,
                start_date=start_date,
                end_date=end_date,
                location=location,
                freelancer=freelancer 
            )
            
            if institution_logo:
                fs = FileSystemStorage(location='media/education_images')
                filename = fs.save(institution_logo.name, institution_logo)
                education.logo = filename.split('/')[-1]
            education.save()
                
            messages.success(request, 'Your education details have been successfully added.')
            return redirect(self.freelancer_profile_url)  
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.education_form_url) 
 
# Testing Complete
class EditEducationView(CustomLoginRequiredMixin, View):
    education_form_template = 'freelancerprofile/editeducation.html'
    education_form_url = 'freelancer:edit-education'
    freelancer_profile_url = 'freelancer:profile'
    
    months = {
        "jan": "January",
        "feb": "February",
        "mar": "March",
        "apr": "April",
        "may": "May",
        "jun": "June",
        "jul": "July",
        "aug": "August",
        "sep": "September",
        "oct": "October",
        "nov": "November",
        "dec": "December",
    }
    current_year = datetime.now().year
    years = {str(year): year for year in range(current_year, 1979, -1)}
    
    def get(self, request, education_id):
        try:
            education = Education.objects.get(education_id=education_id)
            start_month = education.start_date.strftime("%b").lower() if education.start_date else ""
            start_year = str(education.start_date.year) if education.start_date else ""

            end_month = education.end_date.strftime("%b").lower() if education.end_date else ""
            end_year = str(education.end_date.year) if education.end_date else ""

            currently_studying = education.end_date is None  
            
            context = {
                'education': education,
                'months': self.months,
                'years': self.years,
                'start_month': start_month,
                'start_year': start_year,
                'end_month': end_month,
                'end_year': end_year,
                'currently_studying': currently_studying
            }
            return render(request, self.education_form_template, context)
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)       
    
    def post(self, request, education_id):
        try:
            education = Education.objects.get(education_id=education_id)
            
            institution_logo = request.FILES.get('institution_logo')  
            institution_name = request.POST.get('institution_name')  
            level = request.POST.get('level')  
            start_month = request.POST.get('start_month') 
            start_year = request.POST.get('start_year')  
            end_month = request.POST.get('end_month')  
            end_year = request.POST.get('end_year')  
            location = request.POST.get('location')  
            currently_studying = request.POST.get('currently_studying')
            
            context = {
                'education': education,
                'institution_name': institution_name,
                'level': level,
                'start_month': start_month,
                'start_year': start_year,
                'end_month': end_month,
                'end_year': end_year,
                'location': location,
                'currently_studying': currently_studying,
                'months': self.months,
                'years': self.years,
            }
            
            valid, error_message = validate_education(
                institution_logo, institution_name, level, start_month, start_year, 
                end_month, end_year, location, currently_studying, self.months
            )
            
            if not valid:
                messages.error(request, error_message)
                return render(request, self.education_form_template, context)
            
            if start_month and start_year:
                start_month_name = self.months.get(start_month)
                start_date_str = f"{start_month_name}-{start_year}"
                start_date = datetime.strptime(start_date_str, "%B-%Y").date()
            else:
                start_date = None
        
            if not currently_studying and end_month and end_year:
                end_month_name = self.months.get(end_month)
                end_date_str = f"{end_month_name}-{end_year}"
                end_date = datetime.strptime(end_date_str, "%B-%Y").date()
            else:
                end_date = None
            
            education.institution=institution_name
            education.education_level=level
            education.start_date=start_date
            education.end_date=end_date if not currently_studying else None
            education.location=location
                
            if institution_logo:
                fs = FileSystemStorage(location='media/education_images')
                filename = fs.save(institution_logo.name, institution_logo)
                education.logo = filename.split('/')[-1]
            education.save()
            
            messages.success(request, 'Your education details have been successfully updated.')
            return redirect(self.freelancer_profile_url) 
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(reverse(self.education_form_url, args=[education_id])) 

# Testing Complete
class DeleteEducationView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request, education_id):
        try:
            education = Education.objects.get(education_id=education_id)
            education.delete()
            
            messages.success(request, 'Your education details have been successfully deleted.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
# Testing Complete
class AddCertificateView(CustomLoginRequiredMixin, View):
    certificate_template = 'freelancerprofile/addcertificate.html'
    certificate_url = 'freelancer:add-new-certificate'
    freelancer_profile_url = 'freelancer:profile'

    months = {
        "jan": "January",
        "feb": "February",
        "mar": "March",
        "apr": "April",
        "may": "May",
        "jun": "June",
        "jul": "July",
        "aug": "August",
        "sep": "September",
        "oct": "October",
        "nov": "November",
        "dec": "December",
    }
    current_year = datetime.now().year
    years = {str(year): year for year in range(current_year, 1979, -1)}
    
    def get(self, request):
        context = {
            'months': self.months,
            'years': self.years,
        }
        return render(request, self.certificate_template, context)       
    
    def post(self, request):
        try:
            certificate_logo = request.FILES.get('certificate_logo')
            certificate_name = request.POST.get('certificate_name', '').strip()
            certificate_provider = request.POST.get('certificate_provider', '').strip()
            issue_month = request.POST.get('issue_month')
            issue_year = request.POST.get('issue_year')
            certificate_url = request.POST.get('certificate_url', '').strip()
        
            context = {
                'certificate_name': certificate_name,
                'certificate_provider': certificate_provider,
                'issue_month': issue_month,
                'issue_year': issue_year,
                'certificate_url': certificate_url,
                'months': self.months,
                'years': self.years,
            }
        
            is_valid, error_msg = validate_certificate(
                certificate_logo, certificate_name, certificate_provider, 
                issue_month, issue_year, certificate_url, self.months
            )

            if not is_valid:
                messages.error(request, error_msg)
                return render(request, self.certificate_template, context)
            if issue_month and issue_year:
                start_month_name = self.months.get(issue_month)
                start_date_str = f"{start_month_name}-{issue_year}"
                issued_date = datetime.strptime(start_date_str, "%B-%Y").date()
            else:
                issued_date = None
                
            freelancer = Freelancer.objects.get(user=request.user)
            certificate = Certificate.objects.create(
                certificate_name=certificate_name,
                certificate_provider=certificate_provider,
                issued_date=issued_date,
                freelancer=freelancer 
            )
            
            if certificate_logo:
                fs = FileSystemStorage(location='media/certificate_images')
                filename = fs.save(certificate_logo.name, certificate_logo)
                certificate.certificate_logo = filename.split('/')[-1]
                
            if certificate_url:
                certificate.certificate_url = certificate_url
                
            certificate.save()
                
            messages.success(request, 'Your certificate details have been successfully added.')
            return redirect(self.freelancer_profile_url)  
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.certificate_url) 
        
# Testing Complete
class EditCertificateView(CustomLoginRequiredMixin, View):
    certificate_form_template = 'freelancerprofile/editcertificate.html'
    education_form_url = 'freelancer:edit-certificate'
    freelancer_profile_url = 'freelancer:profile'
    
    months = {
        "jan": "January",
        "feb": "February",
        "mar": "March",
        "apr": "April",
        "may": "May",
        "jun": "June",
        "jul": "July",
        "aug": "August",
        "sep": "September",
        "oct": "October",
        "nov": "November",
        "dec": "December",
    }
    current_year = datetime.now().year
    years = {str(year): year for year in range(current_year, 1979, -1)}
    
    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)
            issued_month = certificate.issued_date.strftime("%b").lower() if certificate.issued_date else ""
            issued_year = str(certificate.issued_date.year) if certificate.issued_date else ""
            
            context = {
                'certificate': certificate,
                'months': self.months,
                'years': self.years,
                'issued_month': issued_month,
                'issued_year': issued_year,
            }
            return render(request, self.certificate_form_template, context)
        except Exception:
            messages.error(request, 'Failed to load your profile. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
    def post(self, request, certificate_id):
        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)
            
            certificate_logo = request.FILES.get('certificate_logo')
            certificate_name = request.POST.get('certificate_name', '').strip()
            certificate_provider = request.POST.get('certificate_provider', '').strip()
            issue_month = request.POST.get('issue_month')
            issue_year = request.POST.get('issue_year')
            certificate_url = request.POST.get('certificate_url', '').strip()
            
            context = {
                'certificate': certificate,
                'certificate_name': certificate_name,
                'certificate_provider': certificate_provider,
                'issue_month': issue_month,
                'issue_year': issue_year,
                'certificate_url': certificate_url,
                'months': self.months,
                'years': self.years,
            }
            
            is_valid, error_msg = validate_certificate(
                certificate_logo, certificate_name, certificate_provider, 
                issue_month, issue_year, certificate_url, self.months
            )
        
            if not is_valid:
                messages.error(request, error_msg)
                return render(request, self.certificate_form_template, context)
            
            if issue_month and issue_year:
                start_month_name = self.months.get(issue_month)
                start_date_str = f"{start_month_name}-{issue_year}"
                issued_date = datetime.strptime(start_date_str, "%B-%Y").date()
            else:
                issued_date = None
                
            certificate.certificate_name=certificate_name
            certificate.certificate_provider=certificate_provider
            certificate.issued_date=issued_date
            
            if certificate_logo:
                fs = FileSystemStorage(location='media/certificate_images')
                filename = fs.save(certificate_logo.name, certificate_logo)
                certificate.certificate_logo = filename.split('/')[-1]
                
            if certificate_url:
                certificate.certificate_url = certificate_url
                
            certificate.save()
                
            messages.success(request, 'Your certificate details have been successfully updated.')
            return redirect(self.freelancer_profile_url)   
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(reverse(self.education_form_url, args=[certificate_id]))
                
# Testing Complete
class DeleteCertificateView(CustomLoginRequiredMixin, View):
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)
            certificate.delete()
            
            messages.success(request, 'Your certificate details have been successfully deleted.')
            return redirect(self.freelancer_profile_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.freelancer_profile_url)
        
# Testing Complete
class PasswordChangeView(CustomLoginRequiredMixin, View):
    password_change_template = 'freelancerprofile/passwordchange.html'
    password_change_url = 'freelancer:change-password'
    freelancer_profile_url = 'freelancer:profile'
    
    def get(self, request):
        return render(request, self.password_change_template)
    
    def post(self, request):
        try:
            old_password = request.POST.get('oldpassword')
            new_password = request.POST.get('newpassword')
            confirm_password = request.POST.get('confirmpassword')
        
            valid, error_message = validate_password(old_password, new_password, confirm_password, request.user)
            if not valid:
                messages.error(request, error_message)
                return render(request, self.password_change_template)
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Your password has been changed successfully.')
            return redirect(self.password_change_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.password_change_url)