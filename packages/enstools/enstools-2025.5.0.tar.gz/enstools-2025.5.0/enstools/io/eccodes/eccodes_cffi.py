"""
A minial Interface to ecCodes based on CFFI
"""
import cffi
import numpy as np
import xarray
import struct
import threading
import platform
import logging
import os

# initialize the interface to the C-Library
ffi = cffi.FFI()

# type definition. No need to specify internals of the structs. just name them
ffi.cdef("typedef struct codes_handle codes_handle;")
ffi.cdef("typedef struct codes_context codes_context;")
ffi.cdef("typedef struct codes_keys_iterator codes_keys_iterator;")

# definition of the used functions
ffi.cdef("long codes_get_api_version (void);")
ffi.cdef("codes_handle* codes_handle_new_from_message(codes_context* c, const void*	data, size_t data_len);")
ffi.cdef("int codes_handle_delete(codes_handle* h);")
ffi.cdef("int codes_get_long(codes_handle* h, const char* key, long* value);")
ffi.cdef("int codes_get_double(codes_handle* h, const char* key, double* value);")
ffi.cdef("int codes_get_string(codes_handle* h, const char* key, char* mesg, size_t* length);")
ffi.cdef("int codes_get_size(codes_handle* h, const char* key, size_t* size);")
ffi.cdef("int codes_get_long_array(codes_handle* h, const char* key, long* vals, size_t* length);")
ffi.cdef("int codes_get_double_array(codes_handle* h, const char* key, double* vals, size_t* length);")
ffi.cdef("int grib_get_native_type(codes_handle* h, const char* name, int* type);")

# functions for key-iterators
ffi.cdef("codes_keys_iterator* codes_keys_iterator_new(codes_handle *h, unsigned long filter_flags, const char* name_space);")
ffi.cdef("int codes_keys_iterator_next (codes_keys_iterator *kiter);")
ffi.cdef("const char* codes_keys_iterator_get_name(codes_keys_iterator *kiter);")
ffi.cdef("int codes_keys_iterator_delete(codes_keys_iterator *kiter);")


def __find_lib_ld_library_path(name):
    """
    find a library on a linux system with the LD_LIBRARY_PATH, is defined.

    Parameters
    ----------
    name: str
            name of the library, e.g. libeccodes

    Returns
    -------
    str:
            absolute path of the library if found. if not found, the name is returned
    """
    LD_LIBRARY_PATH = os.getenv("LD_LIBRARY_PATH")
    if LD_LIBRARY_PATH is not None:
        components = LD_LIBRARY_PATH.split(":")
        for one_component in components:
            lib_path = os.path.join(one_component, name)
            if os.path.exists(lib_path + ".so"):
                return lib_path
    return name


# load the actual c-library
if platform.system() == "Linux":
    __libext = "so"
    __libname = __find_lib_ld_library_path("libeccodes")
elif platform.system() == "Darwin":
    __libext = "dylib"
    __libname = "libeccodes"
elif platform.system() == "Windows":
    __libext = "dll"
    __libname = "eccodes"
else:
    raise OSError("Unknown platform: %s" % platform.system())
try:
    _eccodes = ffi.dlopen("{name}.{ext}".format(name=__libname, ext=__libext))
except OSError:
    logging.warning("eccodes c-library not found, grib file support not available!")


# Constants for 'missing'
CODES_MISSING_DOUBLE = -1e+100
CODES_MISSING_LONG = 2147483647

# list of staggered variables in U-direction
# FIXME: this is COSMO-specific and related to issue #39
staggered_u = ["u", "aumfl_s"]  #, "u_10m", "umfl_s"]
staggered_v = ["v", "avmfl_s"]  #, "v_10m", "vmfl_s"]

# standard keys required by read_grib_file
standard_keys = ['bitsPerValue',
                 'cfName',
                 'cfVarName',
                 'dataDate',
                 'dataTime',
                 'discipline',
                 'editionNumber',
                 'gridDefinitionDescription',
                 'gridType',
                 'iDirectionIncrementInDegrees',
                 'indicatorOfParameter',
                 'jDirectionIncrementInDegrees',
                 'latitudeOfFirstGridPointInDegrees',
                 'latitudeOfLastGridPointInDegrees',
                 'latitudeOfSouthernPoleInDegrees',
                 'level',
                 'localActualNumberOfEnsembleNumber',
                 'longitudeOfFirstGridPointInDegrees',
                 'longitudeOfLastGridPointInDegrees',
                 'longitudeOfSouthernPoleInDegrees',
                 'missingValue',
                 'Ni',
                 'Nj',
                 'numberOfDataPoints',
                 'parameterCategory',
                 'parameterName',
                 'parameterNumber',
                 'parameterUnits',
                 'perturbationNumber',
                 'scaledValueOfFirstFixedSurface',
                 'scaledValueOfSecondFixedSurface',
                 'shortName',
                 'table2Version',
                 'typeOfLevel',
                 'validityDate',
                 'validityTime']

# allow only one read per time
read_msg_lock = threading.Lock()


# A representation of one grib message
class GribMessage():

    def __init__(self, file, offset=0, read_data=False):
        """
        create a message from the data buffer object

        Parameters
        ----------
        file : file-object
                a file object which points already to the beginning of the message

        offset : int
                position of the file where the message starts

        read_data : bool
                False: read only the header of the message.
        """
        # cache for all read operations of keys
        self.cache = {}
        self.has_data = read_data

        # read the content of the message
        self.buffer = _read_message_raw_data(file, offset, read_data=read_data)
        # was there a message?
        if self.buffer is None:
            self.handle = ffi.NULL
            return

        # decode the message
        with read_msg_lock:
            # read the message itself
            self.handle = _eccodes.codes_handle_new_from_message(ffi.NULL, ffi.from_buffer(self.buffer), len(self.buffer))

            # pre-read common keys and don't care for errors
            for one_key in standard_keys:
                try:
                    self.__getitem__(one_key, use_lock=False)
                except:
                    pass

            # pre-read the values also if we read the data in memory
            if read_data:
                self.__getitem__("values", use_lock=False)

        # was the reading successful?
        if self.handle == ffi.NULL:
            raise ValueError("unable to read grib message from buffer!")

    def __getitem__(self, item, use_lock=True):
        if item in self.cache:
            result = self.cache[item]
            if result is None:
                raise KeyError("key '%s' not found in grib message!" % item)
            return result
        else:
            try:
                # lock if we do not yet have a lock from a calling function
                if use_lock:
                    read_msg_lock.acquire()

                # read the key
                ckey = _cstr(item)
                nelements = self.__codes_get_size(ckey)
                if nelements > 1:
                    value = self.__codes_get_array(ckey, nelements)
                else:
                    value = self.__codes_get(ckey)
                self.cache[item] = value
            except ValueError:
                # store the error
                self.cache[item] = None
                # nothing found? Any error is interpreted as Key not found.
                raise KeyError("key '%s' not found in grib message!" % item)
            finally:
                # unlock if locked
                if use_lock:
                    read_msg_lock.release()
            return value

    def __contains__(self, item):
        # is the value already in cache?
        if item in self.cache:
            if self.cache[item] is None:
                return False
            return True
        else:
            # The value is not cached, try to read it from the grib message
            try:
                self.__getitem__(item)
            except KeyError:
                return False
            return True

    def keys(self):
        """
        returns all GRIB keys of this GRIB message

        Returns
        -------
        list :
                list of strings with the names of the keys
        """
        result = []
        with read_msg_lock:
            # 128 is the value of the C-constant GRIB_KEYS_ITERATOR_DUMP_ONLY and reduces the set of keys to those
            # really available
            kiter = _eccodes.codes_keys_iterator_new(self.handle, 128, ffi.NULL)
            while _eccodes.codes_keys_iterator_next(kiter) == 1:
                result.append(ffi.string(_eccodes.codes_keys_iterator_get_name(kiter)).decode("utf-8"))
        return result

    def is_valid(self):
        """
        returns true if the content of a message was readable
        """
        return self.buffer is not None

    def get_name(self, prefer_cf=True):
        """
        find a name for this variable.

        Parameters
        ----------
        prefer_cf : bool
                if True, the search order for the name is "cfName", "cfVarName", "shortName", otherwise it is
                "shortName", "cfName", "cfVarName".

        Returns
        -------
        string
                name of the variable.
        """
        if prefer_cf:
            name_keys = ["cfName", "cfVarName", "shortName"]
        else:
            name_keys = ["shortName", "cfName", "cfVarName"]
        for key in name_keys:
            result = self.__getitem__(key)
            if result != "unknown":
                break
        return result

    def get_dimension(self, dimensions=None, dimension_names=None):
        """
        get the shape of one message depending on the grid type

        Returns
        -------
        tuple
                (shape, dim-names)
        """
        if self["gridType"] == "rotated_ll":
            shape = (self["Nj"], self["Ni"])
            # the dimension names differ for staggered variables like u and v
            var_name = self["shortName"].lower()
            if var_name in staggered_u and self["typeOfLevel"] not in ["heightAboveSea", "isobaricInhPa"]:
                #breakpoint()
                dim_names = ["rlat", "srlon"]
            elif var_name in staggered_v and self["typeOfLevel"] not in ["heightAboveSea", "isobaricInhPa"]:
                dim_names = ["srlat", "rlon"]
            else:
                dim_names = ["rlat", "rlon"]
        elif self["gridType"] == "regular_ll":
            shape = (self["Nj"], self["Ni"])
            dim_names = ["lat", "lon"]
        elif self["gridType"] in ["sh", "reduced_gg", "unstructured_grid"]:
            shape = (self["numberOfDataPoints"],)
            dim_names = ["cell"]
        else:
            raise ValueError("don't know how to calculate the shape for grid type %s" % self["gridType"])

        # loop over all already used dims for comparison
        if dimensions is not None and dimension_names is not None:
            for one_var in dimensions.keys():
                if dimension_names[one_var] == dim_names and dimensions[one_var] != shape:
                    for id, dn in enumerate(dim_names):
                        dim_names[id] = "%s%d" % (dn, 2)
        return shape, dim_names

    def get_coordinates(self, dimension_names):
        """
        get the longitude and latitude coordinates for one message

        Returns
        -------
        tuple:
            ((lon-dim-names, lon-coord), (lat-dim-names), lat-coord)
        """
        # are coordinates available?
        if "longitudes" not in self or "latitudes" not in self:
            return None, None

        if self["gridType"] == "rotated_ll":
            lon = (dimension_names, np.array(self["longitudes"].reshape(self["Nj"], self["Ni"]), dtype=np.float32))
            lat = (dimension_names, np.array(self["latitudes"].reshape(self["Nj"], self["Ni"]), dtype=np.float32))
        elif self["gridType"] in ["sh", "reduced_gg", "unstructured_grid"]:
            lon = (dimension_names[0], np.array(self["longitudes"], dtype=np.float32))
            lat = (dimension_names[0], np.array(self["latitudes"], dtype=np.float32))
        elif self["gridType"] == "regular_ll":
            lon = (dimension_names[1], np.array(self["longitudes"].reshape(self["Nj"], self["Ni"])[0, :], dtype=np.float32))
            lat = (dimension_names[0], np.array(self["latitudes"].reshape(self["Nj"], self["Ni"])[:, 0], dtype=np.float32))
        else:
            lon = (dimension_names[1], np.array(self["longitudes"], dtype=np.float32))
            lat = (dimension_names[0], np.array(self["latitudes"], dtype=np.float32))
        return lon, lat

    def get_rotated_ll_info(self, dim_names):
        """
        get the rotated pole and the rotated lon/lat coordinates

        Parameters
        ----------
        dim_names : list
                names of the rlat and rlon dimensions

        Returns
        -------

        """
        if self["gridType"] != "rotated_ll":
            raise ValueError("The gridType '%s' has not rotated pole!" % self["gridType"])
        rotated_pole_name = "rotated_pole"
        if not dim_names[0].endswith("t"):
            rotated_pole_name += dim_names[0][-1]
        # create rotated pole description
        rotated_pole = xarray.DataArray(np.zeros(1, dtype=np.int8), dims=(rotated_pole_name,))
        rotated_pole.attrs["grid_mapping_name"] = "rotated_latitude_longitude"
        rotated_pole.attrs["grid_north_pole_latitude"] = self["latitudeOfSouthernPoleInDegrees"] * -1
        rotated_pole.attrs["grid_north_pole_longitude"] = self["longitudeOfSouthernPoleInDegrees"] - 180
        # create rotated coordinate arrays
        # perform calculations on large integers to avoid rounding errors
        factor = 10 ** 10
        first_lon = int(self["longitudeOfFirstGridPointInDegrees"] * factor)
        last_lon = int(self["longitudeOfLastGridPointInDegrees"] * factor)
        first_lat = int(self["latitudeOfFirstGridPointInDegrees"] * factor)
        last_lat = int(self["latitudeOfLastGridPointInDegrees"] * factor)
        if last_lon < first_lon and first_lon > 180 * factor:
            first_lon -= 360 * factor
        # using linspace instead of array and the stored increment to ensure the correct number of values.
        rlon_int = np.linspace(first_lon, last_lon, self["Ni"], dtype=np.int64)
        rlon = xarray.DataArray(np.asarray(rlon_int / factor, dtype=np.float32), dims=(dim_names[-1],))
        rlon.attrs["long_name"] = "longitude in rotated pole grid"
        rlon.attrs["units"] = "degrees"
        rlon.attrs["standard_name"] = "grid_longitude"
        rlat_int = np.linspace(first_lat, last_lat, self["Nj"], dtype=np.int64)
        rlat = xarray.DataArray(np.asarray(rlat_int / factor, dtype=np.float32), dims=(dim_names[-2],))
        rlat.attrs["long_name"] = "latitude in rotated pole grid"
        rlat.attrs["units"] = "degrees"
        rlat.attrs["standard_name"] = "grid_latitude"
        return rotated_pole_name, rotated_pole, rlat, rlon

    def get_level(self):
        """
        gets the center value of the level coordinate, or if available first and second layer

        """
        if self["typeOfLevel"] in ["generalVerticalLayer", "isobaricInhPa"]:
            return self["level"]
        if not "scaledValueOfFirstFixedSurface" in self or not "scaledValueOfSecondFixedSurface" in self:
            return self["level"]
        first_surface = self["scaledValueOfFirstFixedSurface"]
        second_surface = self["scaledValueOfSecondFixedSurface"]
        first_missing = first_surface == CODES_MISSING_LONG or first_surface == CODES_MISSING_DOUBLE
        second_missing = second_surface == CODES_MISSING_LONG or second_surface == CODES_MISSING_DOUBLE

        if first_missing and not second_missing:
            return second_surface
        elif not first_missing and second_missing:
            return first_surface
        elif first_missing and second_missing:
            return self["level"]
        else:
            return first_surface, second_surface

    def get_values(self, shape=None, dtype=None, missing=None):
        """
        read the encoded values from the message

        Parameters
        ----------
        dtype : np.dtype
                values are returned in an array of the specified type

        missing : float
                value used within the grib message the mark missing values. The returned array will contain NaN at this
                locations.

        Returns
        -------
        np.ndarray
        """
        # do we have data in this message?
        if not self.has_data:
            raise ValueError("this message was created from the header only. No data is available!")
        values = self["values"]
        if shape is not None:
            values = values.reshape(shape)
        if dtype is not None and dtype != np.float64:
            values = np.array(values, dtype=dtype)
        # replace fill values with nan
        values = np.where(values == missing, np.nan, values)
        return values

    def __grib_get_native_type(self, key):
        """
        Get the native type of a specific grib key
        """
        itype = ffi.new("int[1]")
        err = _eccodes.grib_get_native_type(self.handle, key, itype)
        if err != 0:
            raise ValueError("unable to get type of key '%s'" % ffi.string(key))
        if itype[0] == 1:
            return int
        elif itype[0] == 2:
            return float
        else:
            return str

    def __codes_get_size(self, key):
        """
        get the number of elements for a given key

        Parameters
        ----------
        key : cstr
                name of the key

        Returns
        -------
        int :
                number of elements
        """
        size = ffi.new("size_t[1]")
        err = _eccodes.codes_get_size(self.handle, key, size)
        if err != 0:
            raise ValueError("unable to get number of elements for key '%s'" % ffi.string(key))
        return size[0]

    def __codes_get(self, key):
        """
        get the value of a non-array key

        Parameters
        ----------
        key : cstr
                name of the key

        Returns
        -------
        int or float or str
        """
        key_type = self.__grib_get_native_type(key)
        if key_type == int:
            value_ptr = ffi.new("long[1]")
            err = _eccodes.codes_get_long(self.handle, key, value_ptr)
            value = value_ptr[0]
        elif key_type == float:
            value_ptr = ffi.new("double[1]")
            err = _eccodes.codes_get_double(self.handle, key, value_ptr)
            value = value_ptr[0]
        else:
            value_buffer = np.zeros(1024, dtype=np.uint8)
            value_buffer_length = ffi.new("size_t[1]", init=[1024])
            err = _eccodes.codes_get_string(self.handle, key, ffi.from_buffer(value_buffer), value_buffer_length)
            if value_buffer_length[0] == 1024:
                value_buffer_length[0] = np.where(value_buffer == 0)[0][0]
            value = value_buffer[:value_buffer_length[0]-1].tobytes().decode("utf-8")
        if err != 0:
            raise ValueError("unable to get value for key '%s'" % ffi.string(key))
        return value

    def __codes_get_array(self, key, nelements):
        """
        Get a values for a key with multiple values

        Parameters
        ----------
        key : cstr
                name of the key

        nelements : int
                size the array to retrieve

        Returns
        -------
        np.ndarray
        """
        key_type = self.__grib_get_native_type(key)
        length = ffi.new("size_t[1]")
        length[0] = nelements
        if key_type == int:
            values = np.empty(nelements, dtype=np.int64)
            err = _eccodes.codes_get_long_array(self.handle, key, ffi.cast("long*", ffi.from_buffer(values)), length)
        elif key_type == float:
            values = np.empty(nelements, dtype=np.float64)
            err = _eccodes.codes_get_double_array(self.handle, key, ffi.cast("double*", ffi.from_buffer(values)), length)
        else:
            raise ValueError("string arrays are not yet supported!")
        if err != 0:
            raise ValueError("unable to get value for key '%s'" % ffi.string(key))
        return values

    def __del__(self):
        """
        free up the memory
        """
        with read_msg_lock:
            if self.handle != ffi.NULL:
                err = _eccodes.codes_handle_delete(self.handle)
                self.handle = ffi.NULL
                if err != 0:
                    raise ValueError("unable to free memory of grib message!")


def _cstr(pstr):
    """
    convert a python string object into a c string object (copy).

    Parameters
    ----------
    pstr : str
            python string

    Returns
    -------
    const char*
    """
    buffer = np.frombuffer(pstr.encode("utf8") + b"\x00", dtype=np.uint8)
    result = ffi.from_buffer(buffer)
    return result


def _read_message_raw_data(infile, offset, read_data=False):
    """
    Read the header of a grib message and return an byte array with the length of the full message, but without
    the actual data

    Parameters
    ----------
    infile

    Returns
    -------

    """
    # find the start word GRIB. Allow up to 1k junk in front of the actual message
    infile.seek(offset)
    start = infile.read(1024)
    istart = start.find(b"GRIB")
    if istart == -1:
        return None
    offset += istart

    # find at first the grib edition to account for different formats
    infile.seek(offset + 7)
    edition = struct.unpack(">B", infile.read(1))[0]

    # get the length of the total message
    if edition == 1:
        # read the first section
        infile.seek(offset)
        section0 = infile.read(8)
        length_total = struct.unpack(">I", b'\x00' + section0[4:7])[0]

        # check if the length is correct, the message is supposed to end with 7777
        # this is a workaround, apparently, the length of grib1 messages is sometimes wrong.
        infile.seek(offset + length_total - 4)
        section5 = infile.read(4)
        if section5 != b"7777":
            # the maximal length of a grib1 message is 16MB. Read this amount of data and search for the end
            infile.seek(offset)
            maxdata = infile.read(16777216)
            endpos = maxdata.find(b"7777")
            if endpos == -1:
                return None
            else:
                length_total = endpos + 4
                read_data = True
        infile.seek(offset + 8)

        # create an numpy array with the total size of the message
        bytes = np.zeros(length_total, dtype=np.uint8)
        bytes[0:8] = np.frombuffer(section0, dtype=np.uint8)
        pos = 8

        # read the complete message?
        if read_data:
            infile.readinto(memoryview(bytes[8:]))
            return bytes

        # read the first sections, but not the data
        for sec in range(1, 5):
            # read the length of the section
            infile.readinto(memoryview(bytes[pos:pos+3]))
            length_sec = struct.unpack(">I", b'\x00' + bytes[pos:pos+3].tobytes())[0]

            # do not read if this is the final data section
            if pos + length_sec + 4 >= length_total:
                # read the first bytes only
                infile.readinto(memoryview(bytes[pos+3:pos+11]))
                infile.seek(offset + length_total - 5)
                infile.readinto(memoryview(bytes[-5:]))
                break
            else:
                # read data of this section
                infile.readinto(memoryview(bytes[pos+3:pos+length_sec]))
                pos = pos + length_sec
    else:
        # read first section
        infile.seek(offset)
        section0 = infile.read(16)
        length_total = struct.unpack(">Q", section0[8:16])[0]

        # create an numpy array with the total size of the message
        bytes = np.zeros(length_total, dtype=np.uint8)
        bytes[0:16] = np.frombuffer(section0, dtype=np.uint8)
        pos = 16

        # read the complete message?
        if read_data:
            infile.readinto(memoryview(bytes[16:]))
            return bytes

        # read the first sections, but not the data.
        # For standard binary data, we don't read the data section. For other formats we do to avoid decoding errors.
        # TODO: replace any complex data representation with standard binary data to avoid reading!
        data_representation = 0
        while True:
            # read the length of the section and the section number
            infile.readinto(memoryview(bytes[pos:pos+5]))
            length_sec = struct.unpack(">I", bytes[pos:pos+4].tobytes())[0]
            section = bytes[pos+4]

            # do not read completely if this is the final data section
            if pos + length_sec + 4 >= length_total:
                # read the first bytes only (max 1k). For any complex packing, read the complete data section.
                if data_representation != 0:
                    infile.readinto(memoryview(bytes[pos+5:pos+length_sec]))
                # read the final 7777
                infile.seek(offset + length_total - 4)
                infile.readinto(memoryview(bytes[-4:]))
                break
            else:
                # read data of this section
                infile.readinto(memoryview(bytes[pos+5:pos+length_sec]))
                # if this is section 5, get the data representation type
                if section == 5:
                    data_representation = struct.unpack(">H", bytes[pos+9:pos+11].tobytes())[0]
                pos = pos + length_sec

    return bytes
