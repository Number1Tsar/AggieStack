Aggiestack 0.2
===============

Supported Commands

`python aggiestack.py config --hardware hdwr-config.txt`

`python aggiestack.py config --images image-config.txt `

`python aggiestack.py config --flavors flavor-config.txt`

`python aggiestack.py show hardware`

`python aggiestack.py show images `

`python aggiestack.py server create --image IMAGE -- flavor FLAVOR_NAME INSTANCE_NAME `

`python aggiestack.py server delete INSTANCE_NAME`

`python aggiestack.py server list`

`python aggiestack.py admin show imagecaches RACK_NAME`

`python aggiestack.py admin show hardware `

`python aggiestack.py admin show instances`

`python aggiestack.py admin evacuate RACK_NAME `

`python aggiestack.py admin remove MACHINE`

`python aggiestack.py admin add –-mem MEM – disk NUM_DISKS –vcpus VCPUs –ip IP –rack RACK_NAME MACHINE`

`python aggiestack.py admin show Imagecache RACK_NAME`

How to run the program
======================

Our program makes use of database service at its back end, in particular MongoDB. Before running the program, please ensure MongoDB server is locally running in the system. The server should be running at host =”localhost” and port=27017. If you need to change this configuration, the values can be changed in DAO.py file. The host and port are defined by the constants MongoDB_Server_IP and MongoDB_Server_Port respectively. The program creates database called ‘Aggiestack_2_0_128002165’. Refer to this database for any debugging and test. Also, the program was developed using python3.6. For best replication use python 3.5 and beyond.

To run the program, download the zip file and extract it. The entry point of our program is aggiestack.py. Once the database server is up and running, the program can simply be run from any terminal like this:

`Python aggiestack.py config --hardware <hardware-config.txt>`

Please note that every command terminates after its completion. To issue another command you have to run it again like above. For example after you ran the hardware configuration, to view the machines created you run following command

`Python aggiestack.py show hardware`

Since the program uses database, the necessary states of the program are stored in the database. The program will write to console output for all show commands and in case of exception in the program.
`
