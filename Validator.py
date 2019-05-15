import DAO as dao
import Exceptions as exp
import re


class Validator:

    @staticmethod
    # This method validates and converts the value in string to an integer.
    def validate_int_value(value):
        try:
            int_value = int(value)
            return int_value
        except ValueError:
            raise ValueError(exp.INTEGER_VALUE_INVALID.format(value))
        except TypeError:
            raise TypeError(exp.INTEGER_VALUE_INVALID.format(value))

    @staticmethod
    def validate_ip(ip):
        regex = "^\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}$"
        try:
            if not re.match(regex, ip):
                raise Exception(exp.IP_ADDRESS__FORMAT_INVALID.format(ip))
        except TypeError:
            raise TypeError(exp.IP_ADDRESS_INVALID)
        return ip

    @staticmethod
    # This method validates if the image is a valid image present int the database
    def validate_image(image):
        images = dao.get_valid_images()
        if image not in images:
            raise Exception(exp.IMAGE_NOT_FOUND.format(image))
        return image

    @staticmethod
    # This method validates if the flavor is a valid flavor present in the database
    def validate_flavor(flavor):
        flavors = dao.get_valid_flavors()
        if flavor not in flavors:
            raise Exception(exp.FLAVOR_NOT_FOUND.format(flavor))
        return flavor

    @staticmethod
    def validate_server(server):
        servers = dao.get_valid_server()
        if server not in servers:
            raise Exception(exp.MACHINE_NOT_FOUND.format(server))
        return server

    @staticmethod
    # This method validates if the instance is currently present
    def validate_instance(instance):
        instances = dao.get_all_instances_name()
        if instance not in instances:
            raise Exception(exp.INSTANCE_NOT_FOUND.format(instance))
        return instance

    @staticmethod
    def validate_rack(rack):
        racks = dao.get_valid_racks()
        if rack not in racks:
            raise Exception(exp.RACK_NOT_FOUND.format(rack))
        return rack
