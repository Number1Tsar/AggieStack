from pymongo import MongoClient
import datetime
MongoDB_Server_IP = 'localhost'
MongoDB_Server_Port = 27017
MongoDB_Server_Database = 'Aggiestack_2_0_128002165'


# Creates a connection object to Connect to Mongo DB
def connection():
    conn = MongoClient(MongoDB_Server_IP, MongoDB_Server_Port)
    db = conn[MongoDB_Server_Database]
    return db


# Initializes the database and creates necessary collection each with 'Name' as primary key
def initialize():
    db = connection()
    db["Racks"].create_index("Name", unique=True)
    db["Servers"].create_index("Name", unique=True)
    db["Flavors"].create_index("Name", unique=True)
    db["Images"].create_index("Name", unique=True)
    db["Instances"].create_index("Name", unique=True)
    db["ImageLookup"].create_index("Image", unique=True)


# This is a used for Part-C. Searches the Racks for cached copy of the request image. Returns None if cannot
# find any
def search_lookup(image):
    db = connection()
    lookup = db["ImageLookup"]
    result = lookup.find_one({'Image': image})
    if result is not None:
        return result["Racks"]
    else:
        return result


# Updates the Rack-Image-Cache table every time new image is added or old image is removed from the Racks
def update_lookup(image, rack, flag=False):
    db = connection()
    lookup = db["ImageLookup"]
    if lookup.find({'Image': image}).count() > 0:
        if flag:
            lookup.update({"Image": image}, {"$pull": {"Racks": rack}})
        else:
            lookup.update({"Image": image}, {"$addToSet": {"Racks": rack}})
    else:
        if not flag:
            cache = dict()
            cache["Image"] = image
            cache["Racks"] = [rack]
            lookup.insert_one(cache)


# Creates Flavors from flavor configuration file. Using bulk execute operation to improve efficiency of write operation
def create_flavors(list_flavors):
    db = connection()
    flavors = db["Flavors"]
    bulk = flavors.initialize_ordered_bulk_op()
    for flavor in list_flavors:
        bulk.find({'Name': flavor.Name}).upsert().update({"$set": flavor.__dict__})
    bulk.execute()


# Returns the flavor present in database else returns None
def get_flavor(name):
    db = connection()
    flavors = db["Flavors"]
    result = flavors.find_one({'Name': name})
    return result


# Returns all the flavors in the database
def get_all_flavors():
    db = connection()
    flavors = db["Flavors"]
    result = flavors.find()
    return result


# Return valid flavors
def get_valid_flavors():
    result = []
    flavors = get_all_flavors()
    if flavors is not None:
        for flavor in flavors:
            result.append(flavor["Name"])
    return result


# Creates images that are read from image configuration file. Uses bulk operation for efficient database write
def create_images(list_images):
    db = connection()
    flavors = db["Images"]
    bulk = flavors.initialize_ordered_bulk_op()
    for image in list_images:
        bulk.find({'Name': image.Name}).upsert().update({"$set": image.__dict__})
    bulk.execute()


# Returns the images present in database else returns None
def get_image(name):
    db = connection()
    images = db["Images"]
    result = images.find_one({'Name': name})
    return result


# Returns all the images in database
def get_all_images():
    db = connection()
    images = db["Images"]
    result = images.find()
    return result


# Returns valid images
def get_valid_images():
    result = []
    images = get_all_images()
    if images is not None:
        for image in images:
            result.append(image["Name"])
    return result


# Creates Racks from configuration file.
def create_racks(list_racks):
    db = connection()
    racks = db["Racks"]
    bulk = racks.initialize_ordered_bulk_op()
    for rack in list_racks:
        bulk.find({'Name': rack.Name}).upsert().update({"$set": rack.__dict__})
    bulk.execute()


# Returns the rack requested
def get_rack(r):
    db = connection()
    racks = db["Racks"]
    rack = racks.find_one({"Name": r})
    return rack


# Returns the list of rack currently present in the database
def get_valid_racks():
    db = connection()
    racks = db["Racks"]
    result = racks.find()
    valid_racks = []
    for rack in result:
        valid_racks.append(rack["Name"])
    return valid_racks


# Removes the cached image from the rack
def remove_image_from_rack_cache(r):
    db = connection()
    racks = db["Racks"]
    rack = racks.find_one({"Name": r})
    if rack is not None:
        lru = racks.aggregate([{"$match": {"Name": r}},
                               {"$unwind": "$ImageCache"},
                               {"$sort": {"ImageCache.Timestamp": 1}},
                               {"$limit": 1}])
        list_lru = list(lru)
        if list_lru:
            lru_image = list_lru[0]["ImageCache"]
            racks.update({"Name": r}, {"$pull": {"ImageCache": {"Name": lru_image["Name"]}},
                                       "$inc": {"AvailableCapacity": lru_image["Size"]}})
            update_lookup(lru_image["Name"], r, True)


# Creates or updates the image cache. Updates the timestamp of the image to most recently time.
def update_or_create_image_in_rack_cache(r, img):
    db = connection()
    racks = db["Racks"]
    image = get_image(img)
    if racks.find({"Name": r, "ImageCache.Name": img}).count() > 0:
        racks.update({"Name": r}, {"$pull": {"ImageCache": {"Name": img}}})
        image["Timestamp"] = datetime.datetime.utcnow()
        racks.update({"Name": r}, {"$addToSet": {"ImageCache": image}})
    else:
        image["Timestamp"] = datetime.datetime.utcnow()
        racks.update({"Name": r}, {"$addToSet": {"ImageCache": image}, "$inc": {"AvailableCapacity": -image["Size"]}})
        update_lookup(img, r)


# Creates individual Machine if non existing, Updates if deactivated. Used during add machine operation.
def create_server(server):
    db = connection()
    servers = db["Servers"]
    if servers.find({"Name": server.Name, "isActive": True}).count() > 0:
        print("Machine \"{}\" already exists".format(server.Name))
        return
    servers.update_one({'Name': server.Name}, {"$set": server.__dict__}, upsert=True)


# Creates multiple machine at once. Used during config hardware operation
def create_servers(list_servers):
    db = connection()
    servers = db["Servers"]
    list_of_servers = []
    for server in list_servers:
        list_of_servers.append(server.__dict__)
    servers.insert_many(list_of_servers)


# Deletes the machine from database
def delete_server(server_name):
    db = connection()
    servers = db["Servers"]
    server = servers.find_one({"Name": server_name})
    if server is not None:
        servers.remove(server)


# Deactivates the active state of machine
def deactivate_server(server_name):
    db = connection()
    servers = db["Servers"]
    servers.update({"Name": server_name}, {"$set": {"isActive": False}})


# Reactivates the server state of machine
def reactivate_server(server_name):
    db = connection()
    servers = db["Servers"]
    servers.update({"Name": server_name}, {"$set": {"isActive": True}})


# Returns all the servers created in increasing order of available memory, disk and vcpu
def get_all_servers(racks=None):
    db = connection()
    servers = db["Servers"]
    if racks is not None:
        result = servers.find({"Rack": {"$in": racks}, "isActive": True})\
            .sort([("Memory_free", 1), ("disk_free", 1), ("VCPU_free", 1)])
    else:
        result = servers.find({"isActive": True}).sort([("Memory_free", 1), ("disk_free", 1), ("VCPU_free", 1)])

    return result


# Returns all the servers present in database irrespective of their active status
def get_all_valid_server():
    db = connection()
    servers = db["Servers"]
    result = servers.find().sort([("Memory_free", 1), ("disk_free", 1), ("VCPU_free", 1)])
    return result


# Returns all servers not present in racks
def get_all_servers_except(racks):
    db = connection()
    servers = db["Servers"]
    all_servers = servers.find({"Rack": {"$nin": racks}, "isActive": True})
    return all_servers


# Return the server by name
def get_server(name):
    db = connection()
    servers = db["Servers"]
    result = servers.find_one({"Name": name})
    return result


# Return the servers currently present in the database
def get_valid_server():
    result = get_all_valid_server()
    servers = []
    if result is not None:
        for server in result:
            servers.append(server["Name"])
    return servers


# Updates the server when new instance is created or deleted
def update_server(server_name, flavor, flag):
    db = connection()
    servers = db["Servers"]
    flavor_details = get_flavor(flavor)
    if flag:
        servers.update({"Name": server_name}, {
                                           "$inc": {"Memory_free": -flavor_details["Memory"],
                                                    "VCPU_free": -flavor_details["VCPU"],
                                                    "disk_free": -flavor_details["Disk"]}})
    else:
        servers.update({"Name": server_name}, {
                                           "$inc": {"Memory_free": flavor_details["Memory"],
                                                    "VCPU_free": flavor_details["VCPU"],
                                                    "disk_free": flavor_details["Disk"]}})


# Creates instance if instance with same name doesnot exists
def create_instance(new_instance):
    db = connection()
    instances = db["Instances"]
    if instances.find({'Name': new_instance.Name}).count() > 0:
        print("Instance \"{}\" already exists".format(new_instance.Name))
        return
    server = get_server(new_instance.Server)
    check_lru(server["Rack"], new_instance.Image)
    instances.insert_one(new_instance.__dict__)
    update_server(new_instance.Server, new_instance.Flavor, True)


# Performs Least Recently used algorithm in the image cache
def check_lru(r, img):
    rack = get_rack(r)
    image = get_image(img)
    if rack["Capacity"] >= image["Size"]:
        cached_images = []
        for images in rack["ImageCache"]:
            cached_images.append(images["Name"])
        if img not in cached_images:
            while rack["AvailableCapacity"] < image["Size"]:
                remove_image_from_rack_cache(r)
                rack = get_rack(r)
        update_or_create_image_in_rack_cache(r, img)


# Delete instance from database
def delete_instance(name):
    db = connection()
    instances = db["Instances"]
    instance = instances.find_one({"Name": name})
    if instance is not None:
        instances.remove(instance)
        update_server(instance["Server"], instance["Flavor"], False)


# Returns the list of all instance present in server. By default returns all instances in datacenter
def get_all_instances(server=None):
    db = connection()
    instances = db["Instances"]
    if server is not None:
        result = instances.find({"Server": {"$in": server}})
    else:
        result = instances.find()
    return result


# Returns list of instance present in database. Used for validation
def get_all_instances_name():
    instances = get_all_instances()
    instance_name = []
    for instance in instances:
        instance_name.append(instance["Name"])
    return instance_name
