from apogee.bluetooth.Calculators import *

#region BLE SENSOR CLASSES
class ApogeeSensor:
    sensorID = 0
    model = ""
    type = ""
    data_labels = []

    @classmethod
    def calculate_data(cls, data):
        return data

class SP_110:
    sensorID = 1
    model = "SP-110"
    type = "Pyranometer"
    data_labels = ["Shortwave"]

    @classmethod
    def calculate_data(cls, data):
        return data

class SP_510:
    sensorID = 2
    model = "SP-510"
    type = "Thermopile Pyranometer"
    data_labels = ["Shortwave"]
        
    @classmethod
    def calculate_data(cls, data):
        return data

class SP_610:
    sensorID = 3
    model = "SP-610"
    type = "Thermopile Pyranometer (Downward)"
    data_labels = ["Shortwave"]
        
    @classmethod
    def calculate_data(cls, data):
        return data

class SQ_110:
    sensorID = 4
    model = "SQ-110"
    type = "Quantum (Solar)"
    data_labels = ["PPFD"]
        
    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        return calculated_data
    
class SQ_120:
    sensorID = 5
    model = "SQ-120"
    type = "Quantum (Electric)"
    data_labels = ["PPFD"]
        
    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        return calculated_data
    
class SQ_500:
    sensorID = 6
    model = "SQ-500"
    type = "Quantum (Full Spectrum)"
    data_labels = ["PPFD"]
        
    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        return calculated_data

class SL_510:
    sensorID = 7
    model = "SL-510"
    type = "Pyrgeometer"
    data_labels = ["Longwave", "Temperature"]
        
    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        temp = temp_calculator(calculated_data[1])
        calculated_data[1] = temp
        return calculated_data
    
class SL_610:
    sensorID = 8
    model = "SL-610"
    type = "Pyrgeometer (Downward)"
    data_labels = ["Longwave", "Temperature"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        temp = temp_calculator(calculated_data[1])
        calculated_data[1] = temp

        return calculated_data


class SI_1XX:
    sensorID = 9
    model = "SI-1XX"
    type = "IR Sensor"
    data_labels = ["Target Temp", "Sensor Temp"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        target_temp = temp_calculator(calculated_data[0])
        sensor_temp = temp_calculator(calculated_data[1])

        calculated_data = [target_temp, sensor_temp]
        return calculated_data

class SU_200:
    sensorID = 10
    model = "SU-200"
    type = "UV Sensor"
    data_labels = ["UV_EFD", "UV_PFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        uv_pfd = uv_pfd_calculator(calculated_data[0])
        calculated_data.append(uv_pfd)

        return calculated_data

class SE_100:
    sensorID = 11
    model = "SE-100"
    type = "Photometric"
    data_labels = ["Illuminance"]

    @classmethod
    def calculate_data(cls, data):
        return data

class S2_111:
    sensorID = 12
    model = "S2-111"
    type = "NDVI"
    data_labels = ["red", "NIR"]

    @classmethod
    def calculate_data(cls, data):
        return data

class S2_112:
    sensorID = 13
    model = "S2-112"
    type = "NDVI (Downward)"
    data_labels = ["red", "NIR", "NDVI"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        ndvi = approx_ndvi_calculator(calculated_data[0], calculated_data[1])
        calculated_data.append(ndvi)

        return calculated_data

class S2_121:
    sensorID = 14
    model = "S2-121"
    type = "PRI"
    data_labels = ["green", "yellow"]

    @classmethod
    def calculate_data(cls, data):
        return data

class S2_122:
    sensorID = 15
    model = "S2-122"
    type = "PRI (Downward)"
    data_labels = ["green", "yellow"]

    @classmethod
    def calculate_data(cls, data):
        return data

class S2_131:
    sensorID = 16
    model = "S2-131"
    type = "Red/FarRed"
    data_labels = ["red", "far_red", "red_farRed_ratio", "percent_red_farRed"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        red_farRed_ratio = red_farRed_ratio_calculator(calculated_data[0], calculated_data[1])
        percent_red_farRed = percent_red_farRed_calculator(calculated_data[0], calculated_data[1])

        calculated_data.append(red_farRed_ratio)
        calculated_data.append(percent_red_farRed)

        return calculated_data

class S2_141:
    sensorID = 17
    model = "S2-141"
    type = "PAR/FAR"
    data_labels = ["PAR", "far_red", "percent_par_farRed", "Total PFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        percent_par_farRed = percent_par_farRed_calculator(calculated_data[0], calculated_data[1])
        total_pfd = total_pfd_calculator(calculated_data[0], calculated_data[1])
        
        calculated_data[0] = par
        calculated_data.append(percent_par_farRed)
        calculated_data.append(total_pfd)
        
        return calculated_data

class SQ_610:
    sensorID = 18
    model = "SQ-610"
    type = "ePAR"
    data_labels = ["ePPFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        
        return calculated_data

class ST_XX0:
    sensorID = 19
    model = "ST-XX0"
    type = "Thermistor"
    data_labels = ["Temperature"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        temp = temp_calculator(calculated_data[0])
        calculated_data = [temp]

        return calculated_data

class SP_700:
    sensorID = 20
    model = "SP-700"
    type = "Albedometer"
    data_labels = ["Upward", "Downward", "Albedo"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 2):
            return calculated_data
        
        albedo = albedo_calculator(calculated_data[0], calculated_data[1])
        calculated_data.append(albedo)

        return calculated_data

class SQ_620:
    sensorID = 21
    model = "SQ-620"
    type = "Quantum (Extended Range)"
    data_labels = ["PFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par

        return calculated_data

class SQ_640:
    sensorID = 22
    model = "SQ-640"
    type = "Quantum (Low-Light)"
    data_labels = ["PFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        
        return calculated_data

class NDVI_Pair:
    sensorID = 23
    model = "NDVI Pair"
    type = "Pair NDVI"
    data_labels = ["red", "NIR"]

    @classmethod
    def calculate_data(cls, data):
        if (len(data) != 4):
            return data
        
        red_reflectance = reflectance_calculator(data[2], data[0])
        nir_reflectance = reflectance_calculator(data[3], data[1])
        ndvi = pair_ndvi_calculator(red_reflectance, nir_reflectance)

        calculated_data = [ndvi, red_reflectance, nir_reflectance]
        return calculated_data

class PRI_Pair:
    sensorID = 24
    model = "PRI Pair"
    type = "Pair PRI"
    data_labels = ["green", "yellow"]

    @classmethod
    def calculate_data(cls, data):
        return [data[0], data[1]]

class AY_002:
    sensorID = 25
    model = "Four Channel"
    type = "Four Channel"
    data_labels = ["ch1", "ch2", "ch3", "ch4"]

    @classmethod
    def calculate_data(cls, data):
        return data

class AY_001:
    sensorID = 26
    model = "Dual Channel"
    type = "Dual Channel"
    data_labels = ["ch1", "ch2"]

    @classmethod
    def calculate_data(cls, data):
        return data

class SQ_100X:
    sensorID = 27
    model = "SQ-100X"
    type = "Quantum"
    data_labels = ["PPFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        return calculated_data

class SQ_313:
    sensorID = 28
    model = "SQ-313"
    type = "Line Quantum"
    data_labels = ["PPFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        calculated_data[0] = par
        return calculated_data

class SM_500:
    sensorID = 29
    model = "SM-500"
    type = "Guardian"
    data_labels = ["PPFD", "Temperature", "Humidity", "CO2", "Pressure", "Dew Point", "VPD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 5):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        temp = temp_calculator(calculated_data[1])
        dew_point = dew_point_calculator(calculated_data[2], calculated_data[1])
        vpd = vpd_calculator(calculated_data[2], calculated_data[1])

        calculated_data[0] = par
        calculated_data[1] = temp
        calculated_data.append(dew_point)
        calculated_data.append(vpd)
        
        return calculated_data

class SM_600:
    sensorID = 30
    model = "SM-600"
    type = "Guardian"
    data_labels = ["ePPFD", "Temperature", "Humidity", "CO2", "Pressure", "Dew Point", "VPD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 5):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        temp = temp_calculator(calculated_data[1])
        dew_point = dew_point_calculator(calculated_data[2], calculated_data[1])
        vpd = vpd_calculator(calculated_data[2], calculated_data[1])

        calculated_data[0] = par
        calculated_data[1] = temp
        calculated_data.append(dew_point)
        calculated_data.append(vpd)
        
        return calculated_data

class SM1HUH:
    sensorID = 31
    model = "SM1HUH"
    type = "Guardian"
    data_labels = ["PPFD", "Temperature", "Humidity", "CO2", "Pressure", "Dew Point", "VPD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 5):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        temp = temp_calculator(calculated_data[1])
        dew_point = dew_point_calculator(calculated_data[2], calculated_data[1])
        vpd = vpd_calculator(calculated_data[2], calculated_data[1])

        calculated_data[0] = par
        calculated_data[1] = temp
        calculated_data.append(dew_point)
        calculated_data.append(vpd)
        
        return calculated_data
    
class SM2HUH:
    sensorID = 32
    model = "SM2HUH"
    type = "Guardian"
    data_labels = ["PPFD", "Temperature", "Humidity", "CO2", "Pressure", "Dew Point", "VPD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 5):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        temp = temp_calculator(calculated_data[1])
        dew_point = dew_point_calculator(calculated_data[2], calculated_data[1])
        vpd = vpd_calculator(calculated_data[2], calculated_data[1])

        calculated_data[0] = par
        calculated_data[1] = temp
        calculated_data.append(dew_point)
        calculated_data.append(vpd)
        
        return calculated_data

class SM3HUH:
    sensorID = 33
    model = "SM3HUH"
    type = "Guardian"
    data_labels = ["PPFD", "Temperature", "Humidity", "CO2", "Pressure", "Dew Point", "VPD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 5):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        temp = temp_calculator(calculated_data[1])
        dew_point = dew_point_calculator(calculated_data[2], calculated_data[1])
        vpd = vpd_calculator(calculated_data[2], calculated_data[1])

        calculated_data[0] = par
        calculated_data[1] = temp
        calculated_data.append(dew_point)
        calculated_data.append(vpd)
        
        return calculated_data
    
class SM4HUH:
    sensorID = 34
    model = "SM4HUH"
    type = "Guardian"
    data_labels = ["PPFD", "Temperature", "Humidity", "CO2", "Pressure", "Dew Point", "VPD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 5):
            return calculated_data
        
        par = par_calculator(calculated_data[0])
        temp = temp_calculator(calculated_data[1])
        dew_point = dew_point_calculator(calculated_data[2], calculated_data[1])
        vpd = vpd_calculator(calculated_data[2], calculated_data[1])

        calculated_data[0] = par
        calculated_data[1] = temp
        calculated_data.append(dew_point)
        calculated_data.append(vpd)
        
        return calculated_data

class SO_100:
    sensorID = 35
    model = "SO-100"
    type = "Oxygen Sensor"
    data_labels = ["Oxygen"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = [data[0]]
        return calculated_data

class SO_200:
    sensorID = 36
    model = "SO-200"
    type = "Oxygen Sensor"
    data_labels = ["Oxygen"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = [data[0]]
        return calculated_data

class SU_300:
    sensorID = 37
    model = "SU-300"
    type = "UV Index"
    data_labels = ["UV_Index", "UBV_EFD", "UVB_PFD"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        uvb_efd = uvb_efd_calculator(calculated_data[0])
        uvb_pfd = uvb_pfd_calculator(calculated_data[0])

        calculated_data.append(uvb_efd)
        calculated_data.append(uvb_pfd)

        return calculated_data

class SF_110:
    sensorID = 38
    model = "SF-110"
    type = "Radiation Frost"
    data_labels = ["Temperature"]

    @classmethod
    def calculate_data(cls, data):
        calculated_data = data
        if (len(calculated_data) != 1):
            return calculated_data
        
        temp = temp_calculator(calculated_data[0])
        
        calculated_data = [temp]
        
        return calculated_data
#endregion

SENSOR_REGISTRY = {
    0: ApogeeSensor,
    1: SP_110,
    2: SP_510,
    3: SP_610,
    4: SQ_110,
    5: SQ_120,
    6: SQ_500,
    7: SL_510,
    8: SL_610,
    9: SI_1XX,
    10: SU_200,
    11: SE_100,
    12: S2_111,
    13: S2_112,
    14: S2_121,
    15: S2_122,
    16: S2_131,
    17: S2_141,
    18: SQ_610,
    19: ST_XX0,
    20: SP_700,
    21: SQ_620,
    22: SQ_640,
    23: NDVI_Pair,
    24: PRI_Pair,
    25: AY_002,
    26: AY_001,
    27: SQ_100X,
    28: SQ_313,
    29: SM_500,
    30: SM_600,
    31: SM1HUH,
    32: SM2HUH,
    33: SM3HUH,
    34: SM4HUH,
    35: SO_100,
    36: SO_200,
    37: SU_300,
    38: SF_110
}
