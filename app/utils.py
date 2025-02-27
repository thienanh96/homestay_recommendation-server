from scipy.spatial import distance
import scipy
print('scipy.__version__',scipy.__version__)
import numpy as np
from unidecode import unidecode
import textdistance
import cloudinary
from rest_framework.views import status
from rest_framework.response import Response
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from rest_framework_jwt.settings import api_settings
import math
cloudinary.config( 
  cloud_name = "homestayhub", 
  api_key = "324217692173642", 
  api_secret = "fYCSwPmuwwhAMZDcE0ZYZREomKM" 
)
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
# dict cho gia dinh
dict_chogiadinh = [('phuhopvoitrenho', 0),
                   ('dembosung', 1), ('khonghutthuoc', 2)]


# dict tien ich bep
dict_tienichbep = [('bepdien', 0), ('lovisong', 1),
                   ('tulanh', 2), ('bepga', 3)]

# dict hoat dong giai tri
dict_hoatdonggiaitri = [('bbq', 0), ('canhquandep', 1), ('gansangolf', 2),
                        ('beboi', 3), ('huongbien', 5), ('chothucung', 19), ('cauca', 97)]

# dict tien ich phong
dict_tienichphong = [('bancong', 0)]

# dict tien tich chung
dict_tienich = [('wifi', 0), ('tv', 1), ('dieuhoa', 2), ('maygiat', 3), ('daugoi,dauxa', 4), ('giayvesinh', 5), ('giayan', 6), ('nuockhoang', 7),
                ('khantam', 8), ('kemdanhrang', 9), ('xaphongtam', 10), ('thangmay', 72), ('staircase', 218), ('thangbo', 219), ('maysay', 922)]

cities = ['hagiang','laocai','huubang','sonla','hoabinh','thainguyen','haiphong','quangninh','bacninh','hungyen','hanoi','vinhphuc','ninhbinh','thanhhoa','nghean','quangbinh','danang','thuathienhue','quangnam','quangngai','binhdinh','gialai','phuyen','daklak','daknong','lamdong','ninhthuan','binhthuan','khanhhoa','vungtau','bariavungtau','tiengiang','vinhlong','hochiminh','tayninh','longan','kiengiang','cantho','bangkok','chuacapnhat','thailand','maidich']

# def similarity_by_fields(first_homestay, second_homestay):
#     index = 0
#     similarity = []
#     try:
#         for key, value in first_homestay.items():
#             if index == 0:
#                 score = get_price_similarity(value, second_homestay[key])
#                 similarity.append(score)
#             elif index == 1:
#                 score = get_cities_similarity(value, second_homestay[key])
#                 similarity.append(score)
#             elif index == 2:
#                 city_sim = get_cities_similarity(value, second_homestay['city'])
#                 score = 1 if value.strip() == second_homestay[key].strip() and city_sim == 1 else 0
#                 similarity.append(score)
#             else:
#                 score = 0
#                 if all(i == 0 for i in value) or all(i == 0 for i in second_homestay[key]): 
#                     score = 0
#                 else:
#                     score = 1- distance.cosine(value, second_homestay[key])
#                 similarity.append(score)
#             index = index + 1
#     except RuntimeWarning as e:
#         print('loii: ',e)
#     # dist_cos = distance.cosine(similarity, [1,1,1,1,1,1,1,1,1,1],[2,4,5,2,2,2,2,2,2,2])
#     return 1 - distance.cosine(similarity, [1,1,1,1,1,1,1,1,1,1],[3,8,2,1,1,1,1,1,1,1])

def similarity_by_fields(first_homestay, second_homestay):
    index = 0
    first_vector = []
    second_vector = []
    try:
        for key, value in first_homestay.items():
            if index == 0:
                price1,price2 = get_price_similarity(value, second_homestay[key])
                first_vector.append(price1)
                second_vector.append(price2)
            elif index == 1:
                city1,city2 = get_cities_similarity(value, second_homestay[key])
                first_vector.append(city1)
                second_vector.append(city2)
            elif index == 2:
                _city1,_city2 = get_cities_similarity(value, second_homestay['city'])
                score = 1 if value.strip() == second_homestay[key].strip() and _city1 == _city2 else 0
                if score == 1:
                    first_vector.append(1)
                    second_vector.append(1)
                else:
                    first_vector.append(1)
                    second_vector.append(0)
            else:
                if value is None:
                    value = [1]
                if second_homestay[key] is None:
                    second_homestay[key] = [1]
                max_vector1 = max(value) if max(value) != 0 else 1
                max_vector2 = max(second_homestay[key]) if max(second_homestay[key]) != 0 else 1
                first_homestay_vector = [x / max_vector1 for x in value]
                second_homestay_vector = [x / max_vector2 for x in second_homestay[key]]
                assert len(first_homestay_vector) == len(second_homestay_vector)
                count_el = 0
                for vec in first_homestay_vector:
                    first_vector.append(vec)
                    second_vector.append(second_homestay_vector[count_el])
                    count_el += 1
            index = index + 1
    except RuntimeWarning as e:
        print('loii: ',e)
    # dist_cos = distance.cosine(similarity, [1,1,1,1,1,1,1,1,1,1],[2,4,5,2,2,2,2,2,2,2])
    assert len(first_vector) == len(second_vector)
    weights = np.concatenate(([3,10,2],np.ones(len(first_vector) - 3)))
    dist = distance.euclidean(first_vector, second_vector,weights)
    sim = 1/(1 + dist)
    if math.isnan(sim):
        sim = 0
    return sim

def get_cities_similarity(city_1,city_2):
    index=0
    index1 = 0
    index2 = 0
    for city in cities:
        if(city.strip() == city_1.strip()):
            index1 = index
        if city.strip() == city_2.strip():
            index2 = index
        index = index + 1
    return index1/len(cities), index2/len(cities)
    # return  1 - (abs(index1 - index2)/len(cities))

def get_price_similarity(price_1,price_2):
    return price_1/max(price_1,price_2),price_2/max(price_1,price_2)
    # return  1 - (abs(price_1 - price_2)/max(price_1,price_2))

def convert_to_text(arr):
    text = ''
    for el in arr:
        text = text + ',' + el
    return text[1:]

def check_includes(arr, el):
    index = 0
    for ell in arr:
        if ell[0] == el:
            return (True, index)
        index = index + 1
    return (False,)


def create_array(length):
    final = []
    for i in range(length):
        final.append(0)
    return final


def adjust_arr(arr):
    final = []
    for el in arr:
        if el is None:
            el = ''
        final.append(unidecode(el).replace(' ', '').lower())
    return final

def embed_to_vector(homestay):
    field_names = homestay['amenities']['data']
    main_price = 0
    try:
        main_price = int(homestay['main_price'])
    except ValueError as e:
        main_price = 0
    vector = {
        'gia': main_price,  # 2
        'city': unidecode(homestay['city'] if homestay['city'] is not None else '').replace(' ', '').lower(),  # 3
        # 2
        'district': unidecode(homestay['district'] if homestay['district'] is not None else '').replace(' ', '').lower(),
        'phongngu': None,
        'phongtam': None,
        'chogiadinh': create_array(len(dict_chogiadinh)),
        'tienichbep': create_array(len(dict_tienichbep)),
        'hoatdonggiaitri': create_array(len(dict_hoatdonggiaitri)),
        'tienichphong': create_array(len(dict_tienichphong)),
        'tienich': create_array(len(dict_tienich))
    }
    for field_name in field_names:
        for key, value in field_name.items():
            if key is None:
                key = ''
            key = unidecode(key).replace(' ', '').lower()
            value = adjust_arr(value)
            if((key == 'phongngu')):
                intData = []
                try:
                    max_tourist = int(value[0].replace(
                        'toida', '').replace('khach', ''))
                except ValueError as e:
                    max_tourist = 0
                intData.append(max_tourist)
                try:
                    bedrooms = int(value[1].replace('phongngu', ''))
                except ValueError as e:
                    bedrooms = 0
                intData.append(bedrooms)
                try:
                    bed = int(value[2].replace('giuong', ''))
                except ValueError as e:
                    bed = 0
                intData.append(bed)
                vector['phongngu'] = intData
                continue
            if(key == 'phongtam'):
                phongtam = 0
                try:
                    phongtam = int(value[0].replace('phongtam', ''))
                except ValueError as e:
                    phongtam = 0
                vector['phongtam'] = [phongtam]
                continue
            picked_dict = []
            if key == 'chogiadinh':
                picked_dict = dict_chogiadinh
            if key == 'tienichbep':
                picked_dict = dict_tienichbep
            if key == 'hoatdonggiaitri':
                picked_dict = dict_hoatdonggiaitri
            if key == 'tienichphong':
                picked_dict = dict_tienichphong
            if key == 'tienich':
                picked_dict = dict_tienich
            for val in value:
                check_dt = check_includes(picked_dict, val)
            if(check_dt[0] == True):
                vector[key][check_dt[1]] = 1
    return (vector,homestay['homestay_id'])

def get_score(vector_1,vector_2):
    si_vector = similarity_by_fields(vector_1[0], vector_2[0]) 
    return "("+str(vector_1[1])+","+str(vector_2[1])+","+str(si_vector)+")"

def get_cropped_size_image(_file):
    response = upload(_file)
    cropped_width = 0
    cropped_height = 0
    url = None
    width_image = int(response['width'])
    height_image = int(response['height'])
    if width_image/height_image >= 1.5:
        cropped_height = height_image
        cropped_width = cropped_height * 1.5
    else:
        cropped_width = width_image
        cropped_height = cropped_width / 1.5
    url, options = cloudinary_url(
        response['public_id'],
        format=response['format'],
        width=int(cropped_width),
        height=int(cropped_height),
        crop="crop"
    )
    return url

def get_response(_status,data_for_ok={}):
    return {
        '200': Response(data=data_for_ok,status=status.HTTP_200_OK),
        '401': Response(data={},status=status.HTTP_401_UNAUTHORIZED),
        '500': Response(data={}, status=status.HTTP_500_INTERNAL_SERVER_ERROR),
        '204': Response(data={},status=status.HTTP_204_NO_CONTENT),
        '404': Response(data={},status=status.HTTP_404_NOT_FOUND)
    }.get(_status, Response(data=data_for_ok,status=status.HTTP_200_OK)) 

def get_new_token(profile):
    return jwt_encode_handler(jwt_payload_handler(profile))
