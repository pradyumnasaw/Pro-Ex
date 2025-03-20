import os
import csv
import uuid 
from django.shortcuts import render
from django.http import JsonResponse
# from django.core.files.storage import default_storage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Define where uploaded files are stored
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists
LATEST_CSV_FILE = None

def index(request):
    """Render the main page with company list from the latest uploaded file."""
    global LATEST_CSV_FILE
    companies = []
    
    if LATEST_CSV_FILE:
        csv_file_path = os.path.join(UPLOAD_DIR, LATEST_CSV_FILE)
        print("Checking File Path:", csv_file_path)


        if os.path.exists(csv_file_path):
            companies, _ = load_companies(csv_file_path)

        print("Companies Found:", companies)

    return render(request, "company_app/index.html", {"companies": companies})

@csrf_exempt 
def upload_csv(request):
    """Handle CSV file upload and save it."""
    global LATEST_CSV_FILE

    if request.method == "POST" and request.FILES.get("csv_file"):
        uploaded_file = request.FILES["csv_file"]

        file_extension = uploaded_file.name.split(".")[-1]
        new_filename = f"upload_{uuid.uuid4().hex}.{file_extension}"

        file_path = os.path.join(UPLOAD_DIR, new_filename)

        # Save file
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        LATEST_CSV_FILE = new_filename 
        print("File Uploaded Successfully:", LATEST_CSV_FILE)
        return JsonResponse({"message": "File uploaded successfully"}, status=200)

    return JsonResponse({"error": "No file provided"}, status=400)


def load_companies(file_path):
    """Load company names from a CSV file."""
    companies = set()
    data = []

    if not os.path.exists(file_path):
        print("❌ CSV File Not Found:", file_path)  # Debugging
        return [], []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            headers = reader.fieldnames
            print("CSV Headers:", headers)  # Debug: Print headers

            possible_company_columns = ["Company", "index_name", "company_name"]
            company_column = next((col for col in possible_company_columns if col in headers), None)

            if not company_column:
                print("❌ No Company Name Column Found")
                return [], []
            
            print("Detected Company Column:", company_column)

            for row in reader:
                print("Row Data:", row)  # Debug: Print each row
                companies.add(row[company_column])
                data.append(row)

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return [], []

    return list(companies), data

def get_company_data(request, company_name):
    """Return data for the selected company."""
    global LATEST_CSV_FILE

    if not LATEST_CSV_FILE:
        return JsonResponse({"error": "No CSV file uploaded yet"}, status=400)
    
    csv_file_path = os.path.join(UPLOAD_DIR, LATEST_CSV_FILE)

    if not os.path.exists(csv_file_path):
        return JsonResponse({"error": "No CSV file uploaded yet"}, status=400)
    companies, data = load_companies(csv_file_path)

    print(f"Looking for company: {company_name}")  
    _, data = load_companies(csv_file_path)
    company_data = [row for row in data if row.get("Company") == company_name]

    

    print("Company Data for:", company_name, company_data)  # Debugging
    

    if not company_data:
        return JsonResponse({"error": f"No data found for {company_name}"}, status=404)


    return JsonResponse(company_data, safe=False)
