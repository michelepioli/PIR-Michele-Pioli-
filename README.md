# PIR-Michele-Pioli-

The repository contains some file related to my PIR project:
PZT MODELING IN OPENNASTRAN95 FOR SCALED AIRCRAFT IN AEROELASTIC SIMILARITY

Inside the folder Open: 4 OpenNastran95 input files simulating the static deflection of a cantilever beam due to a piezo-actuator. 5A/5H refer to the piezoelectric material modeled. Moment/temp indicate the way of modeling them (through applied bending moments or temperature cards)

Inside the folder MSC: the same files of Open translated in MSC/Nastran language

5H_abaqus.inp: input file for Abaqus. The same problem mentioned above

nastran_static_PZT_template.inp: OpenNastran95 template file to be filled with numerical values (material properties, thicknesses, voltages...).
Nastran_static.py is an example of python code to generate the input file by filling the template.
