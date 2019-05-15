from models.Image import Image
from models.Flavor import Flavor
from models.Instance import Instance
from models.Rack import Rack
from models.Server import Server
from Validator import Validator as validator
import Exceptions as exp
import DAO as dao


class Controller:

    # Initializes the database
    @staticmethod
    def initialize_tables():
        dao.initialize()

    # Reads image configuration from file and creates images in database
    @staticmethod
    def create_images(file_name):
        with open(file_name, "r") as f:
            # The first line indicates how many images store
            images_cnt = f.readline().split()
            images_list = []
            for i in range(int(images_cnt[0])):
                line = f.readline().split()
                image = Image(line[0], validator.validate_int_value(line[1]), line[2])
                images_list.append(image)
            dao.create_images(images_list)

    # Reads flavors configuration from file and creates flavors in database
    @staticmethod
    def create_flavors(file_name):
        with open(file_name, "r") as f:
            # The first line indicates how many flavors store
            flavors_cnt = f.readline().split()
            flavors_list = []
            for i in range(int(flavors_cnt[0])):
                line = f.readline().split()
                flavor = Flavor(line[0], validator.validate_int_value(line[1]),
                                validator.validate_int_value(line[2]), validator.validate_int_value(line[3]))
                flavors_list.append(flavor)
            dao.create_flavors(flavors_list)

    # Reads rack and machine configuration from file and creates both racks and machines in database in that order
    @staticmethod
    def create_racks_servers(file_name):
        with open(file_name, "r") as f:
            racks_cnt = f.readline().split()
            rack_config = []
            for i in range(int(racks_cnt[0])):
                line = f.readline().split()
                rack = Rack(line[0], validator.validate_int_value(line[1]))
                rack_config.append(rack)
            dao.create_racks(rack_config)
            servers_cnt = f.readline().split()
            server_config = []
            for i in range(int(servers_cnt[0])):
                line = f.readline().split()
                server = Server(line[0], validator.validate_rack(line[1]), validator.validate_ip(line[2]),
                                validator.validate_int_value(line[3]),
                                validator.validate_int_value(line[4]),
                                validator.validate_int_value(line[5]))
                server_config.append(server)
            dao.create_servers(server_config)

    # Creates instance based on the image and flavor configuration given by user
    @staticmethod
    def create_instance_with_cache(name, flavor, image):
        rack_with_image_cached = dao.search_lookup(image)
        if rack_with_image_cached:
            server = Controller.best_fit(flavor, rack_with_image_cached)
            if server is not None:
                instance = Instance(name, flavor, image, server["Name"])
                dao.create_instance(instance)
            else:
                racks = dao.get_valid_racks()
                new_racks = [n for n in racks if n not in rack_with_image_cached]
                server = Controller.best_fit(flavor, new_racks)
                if server is not None:
                    instance = Instance(name, flavor, image, server["Name"])
                    dao.create_instance(instance)
                else:
                    raise Exception(exp.COMPATIBLE_MACHINE_UNAVAILABLE.format(name))
        else:
            server = Controller.best_fit(flavor)
            if server is not None:
                instance = Instance(name, flavor, image, server["Name"])
                dao.create_instance(instance)
            else:
                raise Exception(exp.COMPATIBLE_MACHINE_UNAVAILABLE.format(name))

    # Adds a new machine. Used after the sick machine is fixed
    @staticmethod
    def add_new_machine(name, rack, ip, memory, disk, vcpus):
        server = Server(name, rack, ip, memory, disk, vcpus)
        dao.create_server(server)

    # Checks if the machine can support flavor. Returns Yes if can otherwise No
    @staticmethod
    def can_host_flavor(f, s):
        flavor = dao.get_flavor(f)
        server = dao.get_server(s)
        print("yes" if Controller.can_host(flavor, server) else "No")

    # Runs best fit algorithm to check which machine can host instance
    @staticmethod
    def best_fit(f, racks=None):
        flavor = dao.get_flavor(f)
        servers = dao.get_all_servers(racks)
        server = None
        for s in servers:
            if Controller.can_host(flavor, s):
                server = s
                break
        return server

    @staticmethod
    def can_host(flavor, server):
        possible = False
        if server["Memory_free"] >= flavor["Memory"] and \
                server["disk_free"] >= flavor["Disk"] and \
                server["VCPU_free"] >= flavor["VCPU"]:
            possible = True
        return possible

    # Migrates all the instance running in the server. If migration is successful, remove the machine otherwise throws
    # an exception.
    @staticmethod
    def remove_server(server):
        instances = dao.get_all_instances([server])
        dao.deactivate_server(server)
        instances_migrated = []
        for instance in instances:
            flavor = instance["Flavor"]
            new_server = Controller.best_fit(flavor)
            if new_server is not None:
                instances_migrated.append(instance)
                dao.delete_instance(instance["Name"])
                new_instance = Instance(instance["Name"], instance["Flavor"], instance["Image"], new_server["Name"])
                dao.create_instance(new_instance)
            else:
                dao.reactivate_server(server)
                for ins in instances_migrated:
                    dao.delete_instance(ins["Name"])
                for ins in instances_migrated:
                    roll_back_instance = Instance(ins["Name"], ins["Flavor"], ins["Image"], ins["Server"])
                    dao.create_instance(roll_back_instance)
                raise Exception(exp.MIGRATION_NOT_POSSIBLE.format(instance["Name"]))
        dao.delete_server(server)

    # Migrates all the instances of the rack into another racks. Renders all the machine in the rack unusable after
    # evacuation is completed. If any of the instance cannot be migrated, the entire operation is aborted
    @staticmethod
    def migrate_rack(rack):
        servers = dao.get_all_servers([rack])
        racks = dao.get_valid_racks()
        racks.remove(rack)
        instances_migrated = []
        servers_to_deactivate = []
        for server in servers:
            servers_to_deactivate.append(server)
            instances = dao.get_all_instances([server["Name"]])
            for instance in instances:
                flavor = instance["Flavor"]
                new_server = Controller.best_fit(flavor, racks)
                if new_server is not None:
                    instances_migrated.append(instance)
                    dao.delete_instance(instance["Name"])
                    new_instance = Instance(instance["Name"], instance["Flavor"], instance["Image"], new_server["Name"])
                    dao.create_instance(new_instance)
                else:
                    for ins in instances_migrated:
                        dao.delete_instance(ins["Name"])
                    for ins in instances_migrated:
                        roll_back_instance = Instance(ins["Name"], ins["Flavor"], ins["Image"], ins["Server"])
                        dao.create_instance(roll_back_instance)
                    raise Exception(exp.MIGRATION_NOT_POSSIBLE.format(instance["Name"]))
        for server in servers_to_deactivate:
            dao.deactivate_server(server["Name"])

    # Removes instance from database
    @staticmethod
    def delete_instance(instance):
        dao.delete_instance(instance)

