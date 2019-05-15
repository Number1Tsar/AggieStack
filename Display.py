import DAO as dao


class Display:
    # Display the flavor created in tabular format
    @staticmethod
    def display_flavors():
        flavors = []
        for flavor in dao.get_all_flavors():
            flavors.append(flavor)
        if flavors:
            headers = list(flavors[0].keys())
            headers.remove('_id')
            Display.print_table(flavors, headers)
        else:
            print("No Flavors available")

    # Display the images created in tabular format
    @staticmethod
    def display_images():
        images = []
        for image in dao.get_all_images():
            images.append(image)
        if images:
            headers = list(images[0].keys())
            headers.remove('_id')
            Display.print_table(images, headers)
        else:
            print("No Images available")

    # Display the Servers created in tabular format. Flag = true displays verbose information.
    @staticmethod
    def display_servers(flag=False):
        servers = []
        for server in dao.get_all_valid_server():
            servers.append(server)
        if servers:
            headers = list(servers[0].keys())
            headers.remove('_id')

            if not flag:
                headers.remove('isActive')
                headers.remove('Memory_free')
                headers.remove('VCPU_free')
                headers.remove('disk_free')
            Display.print_table(servers, headers)
        else:
            print("No Machines available")

    # Display the Instances created in tabular format. Flag = true displays verbose information.
    @staticmethod
    def display_instances(flag=False):
        instances = []
        for instance in dao.get_all_instances():
            instances.append(instance)
        if instances:
            headers = list(instances[0].keys())
            headers.remove('_id')
            if not flag:
                headers.remove("Server")
            Display.print_table(instances, headers)
        else:
            print("No Instances available")

    # Display the Images cached in the racks.
    @staticmethod
    def display_image_cache(r):
        rack = dao.get_rack(r)
        if rack is not None:
            headers = list(rack.keys())
            images = []
            for image in rack["ImageCache"]:
                images.append(image["Name"])
            rack["ImageCache"] = images
            headers.remove('_id')
            headers.remove('Capacity')
            racks = [rack]
            Display.print_table(racks, headers)
        else:
            print("No Racks available")

    @staticmethod
    def print_table(dictionary, headers=None):

        """Author: Thierry Husson. Taken from stackoverflow
        https://stackoverflow.com/questions/17330139/python-printing-a-dictionary-as-a-horizontal-table-with-headers"""

        if not headers:
            headers = list(dictionary[0].keys() if dictionary else [])
        my_list = [headers]
        for item in dictionary:
            my_list.append([str(item[col]) for col in headers])
        col_size = [max(map(len, col)) for col in zip(*my_list)]
        format_str = ' | '.join(["{{:<{}}}".format(i) for i in col_size])
        my_list.insert(1, ['-' * i for i in col_size])
        for item in my_list:
            print(format_str.format(*item))
        print()
