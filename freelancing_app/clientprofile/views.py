from django.shortcuts import render, redirect
from django.views import View
from accounts.models import User, Client
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .utils import *
import json
from datetime import datetime
from .models import Company
from accounts.mixins import CustomLoginRequiredMixin

# Testing Complete
class UserBasicInfoView(CustomLoginRequiredMixin, View):
    profile_template = 'clientprofile/profile.html'
    home_url = 'homes:home' 
    
    def get(self, request):
        try: 
            client = Client.objects.get(user=request.user)
            company = Company.objects.filter(client_id=client)
        except Exception:
            messages.error(request, 'Unable to fetch your profile details.')
            return redirect(self.home_url)
        
        current_year = datetime.now().year
        companies_with_duration = []

        for comp in company:
            if comp.end_date:
                duration = comp.end_date.year - comp.start_date.year
            else:
                duration = current_year - comp.start_date.year
            
            companies_with_duration.append({
                'company': comp,
                'duration': duration
            })
        
        return render(request, self.profile_template, {
            'client': client,
            'companies_with_duration': companies_with_duration,
            'current_year': current_year
        })

# Testing Complete
class EditProfileImageView(CustomLoginRequiredMixin, View):
    edit_profile_template = 'clientprofile/editprofileimage.html'
    edit_profile_url = 'client:edit-profile-image'
    home_url = 'homes:home'

    def get(self, request):
        try:
            client = Client.objects.get(user=request.user)
            return render(request, self.edit_profile_template, {'client': client})
        except Exception:
            messages.error(request, 'Unable to fetch your profile details.')
            return redirect(self.home_url)

    def post(self, request):
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

        try:
            user = request.user
            user.username = username
            if profile_image:
                fs = FileSystemStorage(location='media/profile_images')
                filename = fs.save(profile_image.name, profile_image)
                user.profile_image = filename.split('/')[-1]
             
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect(self.edit_profile_url)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.edit_profile_url)
        
# Testing Complete
class EditPersonalInfoView(CustomLoginRequiredMixin, View):
    personal_details_template = 'clientprofile/editpersonalinfo.html'
    personal_details_url = 'client:edit-personal-info'
    home_url = 'homes:home'
    
    available_languages = [
        'English', 'Nepali', 'Hindi', 'Chinese', 'Urdu', 'Spanish', 'French', 
        'Arabic', 'German', 'Russian', 'Portuguese', 'Japanese', 'Korean', 
        'Italian', 'Dutch', 'Turkish', 'Persian', 'Bengali', 'Swahili', 'Polish',
        'Thai', 'Vietnamese', 'Tagalog', 'Greek', 'Swedish', 'Czech'
    ]

    def get(self, request):
        try:
            client = Client.objects.get(user=request.user)
            selected_languages = client.languages.split(',') if client.languages else []
            selected_languages = [lang.strip() for lang in selected_languages if lang.strip()]
            
            return render(request, self.personal_details_template, {
                'client': client,
                'available_languages': self.available_languages,
                'selected_languages': selected_languages
            })
        except Exception:
            messages.error(request, 'Unable to fetch your profile details.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            user = request.user
            client = Client.objects.get(user=user)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)

        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        bio = request.POST.get('bio')
        languages_selected = request.POST.getlist('languages-select')

        form_data = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'bio': bio,
            'languages_selected': languages_selected
        }

        valid, error_message = validate_personal_info(first_name, middle_name, last_name, phone_number, bio, languages_selected, request)
        if not valid:
            messages.error(request, error_message)
            return render(request, self.personal_details_template, {
                'form_data': form_data,
                'client': client,
                'selected_languages': languages_selected,
                'available_languages': self.available_languages
            })

        try:
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.phone_number = phone_number
            user.save()

            client.bio = bio
            client.languages = ','.join(languages_selected)
            client.save()

            messages.success(request, 'Profile Updated Successfully.')
            return redirect(self.personal_details_url)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.personal_details_url)
            
#Testing Complete
class EditUserAddressView(CustomLoginRequiredMixin, View):
    address_template = 'clientprofile/editaddress.html'
    address_url = 'client:edit-address'
    home_url = 'homes:home'
    
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
            client = Client.objects.get(user=request.user)
            countries_and_cities_json = json.dumps(self.countries_and_cities)
            
            return render(request, self.address_template, {
                'client': client,
                'countries_and_cities': self.countries_and_cities,
                'countries_and_cities_json': countries_and_cities_json,
            })
        except Exception:
            messages.error(request, 'Unable to fetch your profile details.')
            return redirect(self.home_url)

    def post(self, request):
        try:
            client = Client.objects.get(user=request.user)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.address_url)

        country = request.POST.get('country')
        city = request.POST.get('city')
        
        if not country or not city:
            messages.error(request, "Both country and city are required.")
            return render(request, self.address_template, {
                'client': client,
                'countries_and_cities': self.countries_and_cities,
                'countries_and_cities_json': json.dumps(self.countries_and_cities)
            })
 
        try:
            client.country = country
            client.city = city
            client.save()
            
            messages.success(request, 'Profile Updated Successfully.')
            return redirect(self.address_url)
        except Exception:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.address_url)
        
#Testing Complete
class AddCompanyView(CustomLoginRequiredMixin, View):
    company_template = 'clientprofile/addcompany.html'
    company_url = 'client:addcompany'
    
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
        return render(request, self.company_template, context)
    
    def post(self, request):
        company_logo = request.FILES.get('company_logo')  
        company_name = request.POST.get('company_name')  
        position = request.POST.get('position')  
        start_month = request.POST.get('start_month')  
        start_year = request.POST.get('start_year')  
        end_month = request.POST.get('end_month')  
        end_year = request.POST.get('end_year')  
        location = request.POST.get('location')  
        url = request.POST.get('url')  
        currently_working = request.POST.get('currently_working')
        
        context = {
            'company_logo': company_logo,
            'company_name': company_name,
            'position': position,
            'start_month': start_month,
            'start_year': start_year,
            'end_month': end_month,
            'end_year': end_year,
            'location': location,
            'url': url,
            'currently_working': currently_working,
            'months': self.months,
            'years': self.years,
        }
        
        valid, error_message = create_company(
            company_logo, company_name, position, start_month, start_year, 
            end_month, end_year, location, url, currently_working, self.months
        )
        
        if not valid:
            messages.error(request, error_message)
            return render(request, self.company_template, context)
        
        if start_month and start_year:
            start_month_name = self.months.get(start_month)
            start_date_str = f"{start_month_name}-{start_year}"
            start_date = datetime.strptime(start_date_str, "%B-%Y").date()
        else:
            start_date = None
        
        if not currently_working and end_month and end_year:
            end_month_name = self.months.get(end_month)
            end_date_str = f"{end_month_name}-{end_year}"
            end_date = datetime.strptime(end_date_str, "%B-%Y").date()
        else:
            end_date = None
            
        try:
            client = Client.objects.get(user=request.user)
            company = Company.objects.create(
                logo=company_logo,
                name=company_name,
                position=position,
                start_date=start_date,
                end_date=end_date,
                location=location,
                url=url,
                client=client 
            )
            
            if company_logo:
                fs = FileSystemStorage(location='media/company_images')
                filename = fs.save(company_logo.name, company_logo)
                company.logo = filename.split('/')[-1]
            company.save()
                
            messages.success(request, "Company added successfully.")
            return redirect(self.company_url)  
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.company_url) 
        
# Testing In Progress
class EditCompanyView(CustomLoginRequiredMixin, View):
    edit_company_template = 'clientprofile/editcompany.html'
    def get(self, request, company_id):
        company = Company.objects.get(id=company_id)
        return render(request, self.edit_company_template, {'company': company})
    
#Testing Complete
class PasswordChangeView(CustomLoginRequiredMixin, View):
    password_change_template = 'clientprofile/passwordchange.html'
    password_change_url = 'client:change-password'
    home_url = 'homes:home'

    def get(self, request):
        return render(request, self.password_change_template)
    
    def post(self, request):
        old_password = request.POST.get('oldpassword')
        new_password = request.POST.get('newpassword')
        confirm_password = request.POST.get('confirmpassword')
    
        valid, error_message = validate_password(old_password, new_password, confirm_password, request.user)
        if not valid:
            messages.error(request, error_message)
            return render(request, self.password_change_template)

        try:
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, 'Your password has been changed successfully.')
            return redirect(self.password_change_url)
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again later.')
            return redirect(self.password_change_url)
