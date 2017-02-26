# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 20:27:04 2017

@author: Afkar
"""

from bs4 import BeautifulSoup
import requests, csv

lat, lng = [], []
nama_unit, kode_unit = [], []
alamat = []
spesialis, umum, gigi = [], [], []
perawat, bidan, farmasi = [], [], []
lainnya, pendukung = [], []
provinsi = []

def assign_pegawai(marker, separator, char):
    """Check if value is missing"""
    total = '?'
    s = marker.split(separator)
    x = (s[1])[0]
    if (x != char):
        total = int((s[1].split(char))[0])
    return total

def assign_to_list(marker, prov):
    """Assign values (also missing values) to lists"""
    kode = marker.split("Kode Unit:")
    kode = (kode[1].split(','))[0]
    
    nama = marker.split("Nama Unit:")
    nama = (nama[1].split(','))[0]
    
    almt = marker.split("Alamat :")
    almt = (almt[1].split(',Data SDMK'))[0]
    if almt == '0':
            almt = '?'
    
    ltd = marker.split("lat: ")
    try:
        ltd = float((ltd[1].split(','))[0])
        if ltd == 0:
            ltd = '?'
    except Exception:
        ltd = (ltd[1].split(','))[0]
        x = ltd.split('.')
        dec = ''.join(x[1:len(x)])
        ltd = float('.'.join([x[0], dec]))
    
    long = marker.split("lng: ")
    try:
        long = float((long[1].split(','))[0])
        if long == 0:
            long = '?'
    except Exception:
        long = (long[1].split(','))[0]
        x = long.split('.')
        dec = ''.join(x[1:len(x)])
        long = float('.'.join([x[0], dec]))
        
    if (ltd == '?' and long != '?'):
        ltd = 0
        
    if (ltd != '?' and long == '?'):
        long = 0
    
    d1 = assign_pegawai(marker, "Dokter Spesialis : ", ',')
    d2 = assign_pegawai(marker, "Dokter Umum : ", ',')
    d3 = assign_pegawai(marker, "Dokter Gigi : ", ',')
    r = assign_pegawai(marker, "Perawat : ", ',')
    b = assign_pegawai(marker, "Bidan : ", ',')
    f = assign_pegawai(marker, "Farmasi : ", ',')
    l = assign_pegawai(marker, "Nakes Lainnya : ", ',')
    p = assign_pegawai(marker, "Tenaga Pendukung : ", '}')
    
    lat.append(ltd)
    lng.append(long)
    kode_unit.append(kode)
    nama_unit.append(nama)
    alamat.append(almt)
    spesialis.append(d1)
    umum.append(d2)
    gigi.append(d3)
    perawat.append(r)
    bidan.append(b)
    farmasi.append(f)
    lainnya.append(l)
    pendukung.append(p)
    provinsi.append(prov)
    

def pretty(old_string):
    """Get value after split the data"""
    result = []
    
    for item in old_string:
        s = item.replace("\t", '')
        s = s.replace("\r", '')
        s = s.replace("\n", '')
        s = s.replace("\"<div><table border=1>", '{')
        s = s.replace("<br/></td></tr></table></div>\"", '}')
        s = s.replace("<td>", '')
        s = s.replace("</td>", '')
        s = s.replace("</tr><tr>", ',')
        s = s.replace("<tr>", '')
        s = s.replace("</tr>", '')
        s = s.replace("<br/>", ', ')
        s = s.replace(");", '')
        s = s.replace("(", '')
        s = s.replace("=", ':')
        result.append(s)
        
    return result

#Region and its code for URL
prov_dict = {"ACEH" : 11,
"SUMATERA UTARA" : 12,
"SUMATERA BARAT" : 13,
"RIAU" : 14,
"JAMBI" : 15,
"SUMATERA SELATAN" : 16,
"BENGKULU" : 17,
"LAMPUNG" : 18,
"KEPULAUAN BANGKA BELITUNG" : 19,
"KEPULAUAN RIAU" : 21,
"DKI JAKARTA" : 31,
"JAWA BARAT" : 32,
"JAWA TENGAH" : 33,
"DI YOGYAKARTA" : 34,
"JAWA TIMUR" : 35,
"BANTEN" : 36,
"BALI" : 51,
"NUSA TENGGARA BARAT" : 52,
"NUSA TENGGARA TIMUR" : 53,
"KALIMANTAN BARAT" : 61,
"KALIMANTAN TENGAH" : 62,
"KALIMANTAN SELATAN" : 63,
"KALIMANTAN TIMUR" : 64,
"KALIMANTAN UTARA" : 65,
"SULAWESI UTARA" : 71,
"SULAWESI TENGAH" : 72,
"SULAWESI SELATAN" : 73,
"SULAWESI TENGGARA" : 74,
"GORONTALO" : 75,
"SULAWESI BARAT" : 76,
"MALUKU" : 81,
"MALUKU UTARA" : 82,
"PAPUA BARAT" : 91,
"PAPUA" : 94}

#Loop for each region / province
for key in prov_dict:
    print("processing " + key + "...")
    
    #Get HTML Data From URL
    r = requests.get("http://bppsdmk.kemkes.go.id/info_sdmk/peta?prov=" + str(prov_dict[key]))
    data = r.text
    soup = BeautifulSoup(data, "lxml")

    #Find script which contains target data
    list_script = soup.find_all("script")
    length = len(list_script)

    #Split to get smaller info
    jsons = (list_script[length-2].string).split("map.addMarker")
    new_jsons = pretty(jsons)

    #Assign to corresponding lists
    for marker in new_jsons[1:len(new_jsons)]:
        assign_to_list(marker, key)

#combine all data 
all_list = zip(lat, lng, nama_unit, kode_unit, alamat, spesialis, umum,\
               gigi, perawat, bidan, farmasi, lainnya, pendukung, provinsi)

print ("total data: ", len(kode_unit))

print("writing to csv...")

with open("output.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Latitude', 'Longitude', 'Nama_Unit', 'Kode_Unit', 'Alamat',\
                     'Dokter_Spesialis', 'Dokter_Umum', 'Dokter_Gigi', 'Perawat',\
                     'Bidan', 'Farmasi', 'Nakes_Lainnya', 'Tenaga_Pendukung', 'Provinsi'])
    for row in all_list:
        writer.writerow(row)
    
print("done writing!")
#print_result()

#with open('scrap_raw.txt', mode='wt', encoding='utf-8') as file:
#    file.write(str(new_jsons))
