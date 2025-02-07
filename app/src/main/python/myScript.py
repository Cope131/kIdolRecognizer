# Files imported into python directory
# - labels.pickle 120421
# - encodings.pickle 120421
# - Kpop_Idols_090421_CSV.csv

import os
import numpy as np
import pickle
import cv2
import base64
import face_recognition
import pandas as pd

kpop_idols_csv_filename = "Kpop_Idols_090421_CSV.csv"

def detect_face_fr(image_data):
    # Decode Image Data and Convert To Numpy
    decode_data = base64.b64decode(image_data)
    np_data = np.fromstring(decode_data, np.uint8)
    image_4_channels = cv2.imdecode(np_data, cv2.IMREAD_UNCHANGED)
    img = image_4_channels[...,:3]

    labels, encodings = retrieve_encodings_labels()

    # Using Face Recognition
    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgSmall)
    encodesCurFrame = face_recognition.face_encodings(imgSmall, facesCurFrame)

    # Loop Faces for Current Frame
    idsBbox = []
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodings, encodeFace)
        faceDis = face_recognition.face_distance(encodings, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            # (1) label
            temp = []
            label = labels[matchIndex]
            temp.append(extractId(label))
            # (2) bounding box axis
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            temp.extend([x1, x2, y1, y2])
            # add to nested list
            idsBbox.append(temp)

    print(idsBbox)

    return idsBbox

def extractId(label):
    id = label.split('_')[0]
    return id

def retrieve_encodings_labels():

    lblFileName = os.path.join(os.path.dirname(__file__), "labels.pickle")
    lblFile = open(lblFileName, "rb")
    labels = pickle.load(lblFile)
    lblFile.close()

    encFileName = os.path.join(os.path.dirname(__file__), "encodings.pickle")
    encFile = open(encFileName, "rb")
    encodings = pickle.load(encFile)
    encFile.close()

    return labels, encodings

def get_idol_profile(id):

    dataFileName = os.path.join(os.path.dirname(__file__), kpop_idols_csv_filename)
    dataFileNameUser = os.path.join(os.environ["HOME"], kpop_idols_csv_filename)

    # read from? home user directory OR python directory
    if os.path.exists(dataFileNameUser):
        data = pd.read_csv(dataFileNameUser)
    else:
        data = pd.read_csv(dataFileName)

    fltr = data['Id'] == int(id)
    idol = data.loc[fltr]

    headerVal = data.columns.values.tolist()
    try:
        idolVal = idol.values[0].tolist()
    except:
        idolVal = []

    idolProfile = {}

    if len(headerVal) > 0 and len(idolVal) > 0:
        for i in range(len(headerVal)):
            idolProfile[headerVal[i]] = idolVal[i]

    return idolProfile


def getType(value):
    return type(value)


def update_favorite(id, isFave):

    # proper bool string
    properValue = isFave.title()

    # valid bool string > update data frame and overwrite csv
    if properValue == 'True' or properValue == 'False':
        # convert to bool
        boolValue = eval(properValue)

        dataFileName = os.path.join(os.path.dirname(__file__), kpop_idols_csv_filename)
        dataFileNameUser = os.path.join(os.environ["HOME"], kpop_idols_csv_filename)
        # read from? home user directory OR python directory
        if os.path.exists(dataFileNameUser):
            data = pd.read_csv(dataFileNameUser)
        else:
            data = pd.read_csv(dataFileName)

        # update fave value of idol
        fltr = data['Id'] == int(id)
        data.loc[fltr, 'Favorite'] = boolValue

        # save
        if os.path.exists(dataFileNameUser):
            data.to_csv(dataFileNameUser, index=False)
        else:
            data.to_csv(dataFileName, index=False)

        return True

    return False


def save_idols_data_to_home():

    dataFileName = os.path.join(os.path.dirname(__file__), kpop_idols_csv_filename)
    data = pd.read_csv(dataFileName)

    # save data to home: /data/user/0/com.daryl.kidolrecognizer/files
    homePath = os.environ["HOME"]
    newFilePath = os.path.join(homePath, kpop_idols_csv_filename)
    data.to_csv(newFilePath, index=False)

    exist = os.path.exists(newFilePath)

    return exist


def check_idols_data_from_home():
    homePath = os.environ["HOME"]
    newFilePath = os.path.join(homePath, kpop_idols_csv_filename)
    exist = os.path.exists(newFilePath)
    return exist

def get_favorite_idols():

    faveIdols = []

    dataFileNameUser = os.path.join(os.environ["HOME"], kpop_idols_csv_filename)
    exist = os.path.exists(dataFileNameUser)
    print('Home CSV Exist? ', exist)

    if exist:
        # read csv
        data = pd.read_csv(dataFileNameUser)
        # get favorite idol rows
        faveFltr = data['Favorite'] == True
        idols = data.loc[faveFltr]
        # get only stage name & group name
        idols2Cols = idols[['Id', 'Stage Name', 'Group Name']]
        # to list
        idols2ColsVal = idols2Cols.values.tolist()

        faveIdols = idols2ColsVal

    print(faveIdols)

    return faveIdols


def get_all_idols():

    idolsList = []

    dataFileNameUser = os.path.join(os.environ["HOME"], kpop_idols_csv_filename)
    exist = os.path.exists(dataFileNameUser)
    print('Home CSV Exist? ', exist)

    if exist:
        # read csv
        data = pd.read_csv(dataFileNameUser)
        # get only stage name & group name
        allIdols = data[['Id', 'Stage Name', 'Group Name', 'Favorite']]
        # to list
        allIdolsVal = allIdols.values.tolist()

        idolsList = allIdolsVal

    return idolsList


def unique_values_from_col(columnName):

    values = []

    dataFileNameUser = os.path.join(os.environ["HOME"], kpop_idols_csv_filename)

    exist = os.path.exists(dataFileNameUser)
    print('Home CSV Exist? ', exist)

    if exist:
        # read csv
        data = pd.read_csv(dataFileNameUser)
        values = data[columnName].unique().tolist()

    return values


def filter_idols(data, query):
    idolsDataFrame = data.query(query)
    return idolsDataFrame


def sort_idols(data, columnNames, columnNamesOrder):
    colNames = []
    colNamesOrder = []

    for columnName in columnNames:
        colNames.append(columnName)

    for columnNameOrder in columnNamesOrder:
        colNamesOrder.append(columnNameOrder)

    # ascending order? -> 1 - true, 0 - false
    return data.sort_values(by=colNames, ascending=colNamesOrder)


def sort_and_filter(query, columnNames, columnNamesOrder):

    idolsList = []

    dataFileNameUser = os.path.join(os.environ["HOME"], kpop_idols_csv_filename)

    exist = os.path.exists(dataFileNameUser)
    print('Home CSV Exist? ', exist)

    if exist:
        # read csv
        data = pd.read_csv(dataFileNameUser)

        # sort & filter idols
        data.columns = [column.replace(" ", "_") for column in data.columns]

        if len(columnNames) > 0:
            sortedIdols = sort_idols(data, columnNames, columnNamesOrder)
        else:
            sortedIdols = data

        if len(query) > 0:
            filteredAndSortedIdols = filter_idols(sortedIdols, query)
        else:
            filteredAndSortedIdols = sortedIdols

        # columns needed
        filteredAndSortedIdols = filteredAndSortedIdols[['Id', 'Stage_Name', 'Group_Name', 'Favorite']]

        # to list
        filteredAndSortedIdolsList = filteredAndSortedIdols.values.tolist()

        idolsList = filteredAndSortedIdolsList

    return idolsList



