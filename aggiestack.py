import sys
import argparse
from Validator import Validator as validator
from Display import Display
import Logger as log
import Exceptions as exp
from Controller import Controller


# Global variable used to initialize admin privilege
privilege = dict()
privilege["admin_privilege"] = False


# checks if the command issued has admin privilege
def is_admin():
    return privilege["admin_privilege"]


# Runs configuration command based on user's input
@log.logger
def config(args):
    if args.images:
        Controller.create_images(args.images)
    elif args.flavors:
        Controller.create_flavors(args.flavors)
    elif args.hardware:
        Controller.create_racks_servers(args.hardware)


# Displays list of hardware.
@log.logger
def show_hardware(args):
    if is_admin():
        Display.display_servers(True)
    else:
        Display.display_servers()


# Displays list of Images.
@log.logger
def show_images(args):
    Display.display_images()


# Displays list of flavors.
@log.logger
def show_flavors(args):
    Display.display_flavors()


# Displays everything
@log.logger
def show_all(args):
    Display.display_flavors()
    Display.display_images()
    Display.display_servers()


# Displays list of instances.
@log.logger
def show_instances(args):
    if is_admin():
        Display.display_instances(True)
    else:
        raise Exception(exp.ADMIN_PRIVILEGE_REQUIRED)


# Displays which rack has which images cached and also the present capacity
@log.logger
def show_image_cache(args):
    if is_admin():
        rack = validator.validate_rack(args.rack_name)
        Display.display_image_cache(rack)
    else:
        raise Exception(exp.ADMIN_PRIVILEGE_REQUIRED)


# Displays all the instances running
@log.logger
def display_server(args):
    Display.display_instances()


# Creates new instance. Validates the inputs before proceeding
@log.logger
def create_server(args):
    Controller.create_instance_with_cache(args.instance_name, validator.validate_flavor(args.flavor),
                                          validator.validate_image(args.image))


# Deletes the instance
@log.logger
def delete_server(args):
    Controller.delete_instance(validator.validate_instance(args.instance_name))


# Checks if the machine can host the given flavor
@log.logger
def can_host_flavor(args):
    if is_admin():
        f = validator.validate_flavor(args.flavor)
        s = validator.validate_server(args.machine_name)
        Controller.can_host_flavor(f, s)
    else:
        raise Exception(exp.ADMIN_PRIVILEGE_REQUIRED)


# Add the new machine after fixing it
@log.logger
def add_machine(args):

    if is_admin():
        Controller.add_new_machine(args.server_name, validator.validate_rack(args.rack), validator.validate_ip(args.ip),
                                   validator.validate_int_value(args.mem), validator.validate_int_value(args.disk),
                                   validator.validate_int_value(args.vcpus))
    else:
        raise Exception(exp.ADMIN_PRIVILEGE_REQUIRED)


# Removes the machine from data center view. Migrates all the running instance before migrating
@log.logger
def remove_machine(args):
    if is_admin():
        Controller.remove_server(validator.validate_server(args.server_name))
    else:
        raise Exception(exp.ADMIN_PRIVILEGE_REQUIRED)


# Evacuates all the instances in the rack to another rack.
@log.logger
def evacuate_rack(args):
    if is_admin():
        rack_name = validator.validate_rack(args.rack_name)
        Controller.migrate_rack(validator.validate_rack(rack_name))
    else:
        raise Exception(exp.ADMIN_PRIVILEGE_REQUIRED)


def main(argv):
    Controller.initialize_tables()

    parser = argparse.ArgumentParser(prog='aggiestack')
    sub_parser = parser.add_subparsers(help='commands can be config, show')

    config_command = sub_parser.add_parser('config', help='configure')
    config_group = config_command.add_mutually_exclusive_group()
    config_group.add_argument("--hardware", help="list available hardware configurations")
    config_group.add_argument("--images", help="list available images")
    config_group.add_argument("--flavors", help="list available flavors")
    config_command.set_defaults(func=config)

    show_command = sub_parser.add_parser('show', help='display')
    show_sub_parser = show_command.add_subparsers(help='display image cache')

    show_hardware_command = show_sub_parser.add_parser('hardware', help='display hardware')
    show_hardware_command.set_defaults(func=show_hardware)

    show_images_command = show_sub_parser.add_parser('images', help='display images')
    show_images_command.set_defaults(func=show_images)

    show_flavors_command_ = show_sub_parser.add_parser('flavors', help='display flavors')
    show_flavors_command_.set_defaults(func=show_flavors)

    show_hardware_command = show_sub_parser.add_parser('all', help='display all hardware, images and flavors')
    show_hardware_command.set_defaults(func=show_all)

    show_hardware_command = show_sub_parser.add_parser('instances', help='display instances')
    show_hardware_command.set_defaults(func=show_instances)

    image_cache_command = show_sub_parser.add_parser('imagecaches', help='create cached images')
    image_cache_command.add_argument('rack_name', help="Rack Name")
    image_cache_command.set_defaults(func=show_image_cache)

    can_host_command = sub_parser.add_parser('can_host', help='can_host flavor on machine')
    can_host_command.add_argument("machine_name", help="machine name")
    can_host_command.add_argument("flavor", help="flavor name")
    can_host_command.set_defaults(func=can_host_flavor)

    evacuate_command = sub_parser.add_parser('evacuate', help='Evacuate rack')
    evacuate_command.add_argument("rack_name", help="Rack name")
    evacuate_command.set_defaults(func=evacuate_rack)

    remove_server_command = sub_parser.add_parser('remove', help="Remove machine")
    remove_server_command.add_argument("server_name", help="Machine name")
    remove_server_command.set_defaults(func=remove_machine)

    add_server_command = sub_parser.add_parser('add', help="Add a new machine")
    add_server_command.add_argument("--mem", help="Memory of machine")
    add_server_command.add_argument("--disk", help="disk size of machine")
    add_server_command.add_argument("--vcpus", help="VCPUs of machine")
    add_server_command.add_argument("--ip", help="IP address of machine")
    add_server_command.add_argument("--rack", help="rack on which machine is created")
    add_server_command.add_argument("server_name", help=" Machine name")
    add_server_command.set_defaults(func=add_machine)

    server_command = sub_parser.add_parser('server', help='server command')
    sub_sub_parser = server_command.add_subparsers(help='create, list or delete')
    server_create_command = sub_sub_parser.add_parser('create', help='create server')
    server_create_command.add_argument("--image", help="image")
    server_create_command.add_argument("--flavor", help="flavor")
    server_create_command.add_argument("instance_name", help="instance_name")
    server_create_command.set_defaults(func=create_server)

    server_list_command = sub_sub_parser.add_parser('list', help='list server')
    server_list_command.set_defaults(func=display_server)

    server_delete_command = sub_sub_parser.add_parser('delete', help='delete server')
    server_delete_command.add_argument('instance_name', help="instance_name")
    server_delete_command.set_defaults(func=delete_server)

    try:
        if sys.argv[1] == 'admin':
            privilege["admin_privilege"] = True
            args = parser.parse_args(sys.argv[2:])
        else:
            privilege["admin_privilege"] = False
            args = parser.parse_args(sys.argv[1:])
        args.func(args)

    except Exception as e:

        message = "Command cannot be executed "
        print(message)
        parser.print_usage()


if __name__ == "__main__":
    main(sys.argv)
