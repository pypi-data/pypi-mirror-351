from __future__ import absolute_import

import datetime
import json
import os
import re
import tempfile

import cohesivenet.util
from cohesivenet import rest


class Serializer(object):
    def __init__(self, configuration=None):
        self.configuration = None

    PRIMITIVE_TYPES = (float, bool, bytes, int, str)
    NATIVE_TYPES_MAPPING = {
        "int": int,
        "long": int,  # noqa: F821
        "float": float,
        "str": str,
        "bool": bool,
        "date": datetime.date,
        "datetime": datetime.datetime,
        "object": object,
    }

    def sanitize_for_serialization(self, obj):
        """Builds a JSON POST object.

        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is OpenAPI model, return the properties dict.

        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj) for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj) for sub_obj in obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            raise RuntimeError("Unkown object type %s" % str(type(obj)))

        return {
            key: self.sanitize_for_serialization(val) for key, val in obj_dict.items()
        }

    def deserialize(self, response, response_type="object"):
        """Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: class literal for
            deserialized object, or string of class name.

        :return: deserialized object.
        """
        if response.data is None:
            return None

        if type(response.data) is str:
            error_response_str = re.findall(r"{\"error\".*}", response.data)
            if error_response_str:
                raise rest.ApiException(
                    status=response.status, reason=error_response_str[0]
                )

        # handle file downloading
        # save response body into a tmp file and return the instance
        if "file" in response_type:
            return self.__deserialize_file(response, response_type)

        # fetch data from response object
        try:
            data = json.loads(response.data)
        except ValueError:
            data = response.data

        return self.__deserialize(data, response_type)

    def __deserialize(self, data, klass):
        """Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if type(klass) == str:
            if klass.startswith("list["):
                sub_kls = re.match(r"list\[(.*)\]", klass).group(1)
                return [self.__deserialize(sub_data, sub_kls) for sub_data in data]

            if klass.startswith("dict("):
                sub_kls = re.match(r"dict\(([^,]*), (.*)\)", klass).group(2)
                return {k: self.__deserialize(v, sub_kls) for k, v in data.items()}

            # convert str to class
            if klass in self.NATIVE_TYPES_MAPPING:
                klass = self.NATIVE_TYPES_MAPPING[klass]
            else:
                raise RuntimeError("Unknown native type: %s" % klass)

        if klass in self.PRIMITIVE_TYPES:
            return self.__deserialize_primitive(data, klass)
        elif klass == object:
            return self.__deserialize_object(data)
        elif klass == datetime.date:
            return self.__deserialize_date(data)
        elif klass == datetime.datetime:
            return self.__deserialize_datatime(data)
        else:
            raise RuntimeError("Unknown type %s. Classes not supported." % klass)

    def __deserialize_file(self, response, response_type=None):
        """Deserializes body to file

        Saves response body into a file in a temporary folder,
        using the filename from the `Content-Disposition` header if provided.

        :param response:  RESTResponse.
        :return: file path.
        """
        file_type = ""
        if response_type:
            file_parts = response_type.split(":")
            if len(file_parts) >= 2:
                file_type = file_parts[1]

        fd, path = tempfile.mkstemp(
            dir=(self.configuration.temp_folder_path if self.configuration else None)
        )
        os.close(fd)
        os.remove(path)

        # default to timestamped filename
        filename = cohesivenet.util.random_timestamp_filename(file_type=file_type)
        content_disposition = response.getheader("Content-Disposition")
        if content_disposition:
            content_filename = re.search(
                r'filename=[\'"]?([^\'"\s]+)[\'"]?', content_disposition
            ).group(1)

            if (
                content_filename != "yourfilename"
            ):  # API returns this by default, which is annoying.
                filename = content_filename

        path = os.path.join(os.path.dirname(path), filename)
        response_binary = (
            str.encode(response.data) if type(response.data) is str else response.data
        )
        with open(path, "wb") as f:
            f.write(response_binary)

        return path

    def __deserialize_primitive(self, data, klass):
        """Deserializes string to primitive type.

        :param data: str.
        :param klass: class literal.

        :return: int, long, float, str, bool.
        """
        try:
            return klass(data)
        except UnicodeEncodeError:
            return str(data)
        except TypeError:
            return data

    def __deserialize_object(self, value):
        """Return an original value.

        :return: object.
        """
        return value

    def __deserialize_date(self, string):
        """Deserializes string to date.

        :param string: str.
        :return: date.
        """
        try:
            from dateutil.parser import parse

            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise rest.ApiException(
                status=0, reason="Failed to parse `{0}` as date object".format(string)
            )

    def __deserialize_datatime(self, string):
        """Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.
        :return: datetime.
        """
        try:
            from dateutil.parser import parse

            return parse(string)
        except ImportError:
            return string
        except ValueError:
            raise rest.ApiException(
                status=0,
                reason=("Failed to parse `{0}` as datetime object".format(string)),
            )
