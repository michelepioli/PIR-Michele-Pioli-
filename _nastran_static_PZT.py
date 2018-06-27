# -*- coding: utf-8 -*-

from __future__ import print_function

from openmdao.api import ExternalCode

import numpy as np

import os.path

import sys

from aerostructures.number_formatting.field_writer_8 import print_float_8

from aerostructures.number_formatting.is_number import isfloat, isint

class NastranStatic(ExternalCode):
    template_file = 'nastran_static_template.inp'


    def __init__(self, node_id, node_id_all, n_stress, tn, tpn, mn, case_name):
        super(NastranStatic, self).__init__()

        #Identification number of the outer surface nodes
        self.node_id = node_id

        #Identification number of all the structural nodes
        self.node_id_all = node_id_all

        #Number of nodes on the outer surface
        self.ns = len(node_id)

        #Total number of structural nodes
        self.ns_all = len(node_id_all)

        #Number of stress outputs
        self.n_stress = n_stress

        #Number of regions where the thicknesses are defined
        self.tn = tn
	
	#Number of regions where the PZT thicknesses are defined
        self.tpn = tpn

        #Number of concentrated masses
        self.mn = mn

        #Case name (for file naming)
        self.case_name = case_name

        #Forces on the nodes of the outer surface
        self.add_param('f_node', val=np.zeros((self.ns, 3)))

        #Coordinates of all structural nodes
        self.add_param('node_coord_all', val=np.zeros((self.ns_all, 3)))

        #Vector containing the thickness of each region
        self.add_param('t', val=np.zeros(self.tn))

	#Vector containing the offset of the bottom surf. from the reference plane
        self.add_param('z0', val=np.zeros(self.tn))

	#Vector containing the thickness of each PZT region
        self.add_param('tp', val=np.zeros(self.tn))

	#Vector containing the voltage of each patch
        self.add_param('V', val=np.zeros(self.tn))

        #Vector containing the concentrated masses' values
        self.add_param('m', val=np.zeros(self.mn))

        #Young's modulus
        self.add_param('E', val=1.)

        #Poisson's ratio
        self.add_param('nu', val=0.3)

        #Material density
        self.add_param('rho_s', val=1.)

	#Piezoelectric constant
	self.add_param('d31', val=0)

	#PZT Young's modulus
	self.add_param('E_pzt', val=0)

	#PZT Poisson's ratio
	self.add_param('nu_pzt', val=0)

	#PZT density
	self.add_param('rho_pzt', val=0)

        #Displacements of the nodes on the outer surface
        self.add_output('u', val=np.zeros((self.ns, 3)))

        #Von Mises stress of all elements
        self.add_output('VMStress', val=np.zeros(self.n_stress))

        #Structural mass
        self.add_output('mass', val=1.)

        self.input_filepath = 'nastran_static_'+self.case_name+'.inp'
        self.output_filepath = 'nastran_static_'+self.case_name+'.pnh'
        self.output_file = 'nastran_static_'+self.case_name+'.out'

        #Check if the files exist (optional)
        self.options['external_input_files'] = [self.input_filepath,]
        #self.options['external_output_files'] = [self.output_filepath,]

        #Command according to OS
        if sys.platform == 'win32':
            self.options['command'] = ['cmd.exe', '/c', r'nastran.bat', self.input_filepath.rstrip('.inp')]
        else:
            self.options['command'] = ['nastran.cmd', self.input_filepath.rstrip('.inp')]


    def solve_nonlinear(self, params, unknowns, resids):

        # Generate the input file for Nastran from the input file template and pressure values at the nodes
        self.create_input_file(params)

        # Parent solve_nonlinear function actually runs the external code
        super(NastranStatic, self).solve_nonlinear(params, unknowns, resids)

        output_data = self.get_output_data()

        # Parse the output file from the external code and set the value of u
        unknowns['u'] = output_data['u']

        #Parse the output file from the external code and get the Von Mises Stresses
        unknowns['VMStress'] = output_data['VMStress']

        #Parse the output file from the external code and get the structural mass
        unknowns['mass'] = output_data['mass']

    def create_input_file(self, params):

        f_node = params['f_node']
        node_coord_all = params['node_coord_all']
        t = params['t']
	z0 = t/2.
        m = params['m']
        E = params['E']
        nu = params['nu']
        rho_s = params['rho_s']
	tp = params['tp']
	V = params['V']
	d31 = params['d31']
	E_pzt = params['E_pzt']
	nu_pzt = params['nu_pzt']
	rho_pzt = params['rho_pzt']



        input_data = {}

        #Assign each force value to its corresponding node ID in the input data dictionary
        for i in range(len(f_node)):
            input_data['Fx'+self.node_id[i]] = print_float_8(f_node[i, 0])
            input_data['Fy'+self.node_id[i]] = print_float_8(f_node[i, 1])
            input_data['Fz'+self.node_id[i]] = print_float_8(f_node[i, 2])

        #Assign each node coordiantes to its corresponding node ID in the input data dictionary
        for i in range(len(node_coord_all)):
            input_data['x'+self.node_id_all[i]] = print_float_8(node_coord_all[i,0])
            input_data['y'+self.node_id_all[i]] = print_float_8(node_coord_all[i,1])
            input_data['z'+self.node_id_all[i]] = print_float_8(node_coord_all[i,2])

        #Assign each thickness value to its corresponding ID in the input data dictionary
        for i in range(len(t)):
            input_data['t'+str(i+1)] = print_float_8(t[i])

	#Assign each offset to its corresponding ID in the input data dictionary
        for i in range(len(z0)):
            input_data['z0'+str(i+1)] = print_float_8(z0[i])

        #Assign each mass value to its corresponding ID in the input data dictionary
        for i in range(len(m)):
            input_data['m'+str(i+1)] = print_float_8(m[i])

        #Assign the Young's modulus to its input data dictionary key
        input_data['E'] = print_float_8(E)

        #Assign the Poisson's ratio to its input data dictionary key
        input_data['nu'] = print_float_8(nu)

        #Assign the material density to its input data dictionary key
        input_data['rho_s'] = print_float_8(rho_s)

	#Assign the PZT Young's modulus to its input data dictionary key
        input_data['E_pzt'] = print_float_8(E_pzt)

        #Assign the PZT Poisson's ratio to its input data dictionary key
        input_data['nu_pzt'] = print_float_8(nu_pzt)

        #Assign the PZT density to its input data dictionary key
        input_data['rho_pzt'] = print_float_8(rho_pzt)

	#Assign the PZT constant to its input data dictionary key
        input_data['d31'] = print_float_8(d31)

	#Assign each PZT thickness value to its corresponding ID in the input data dictionary
        for i in range(len(tp)):
            input_data['tp'+str(i+1)] = print_float_8(tp[i])

	#Assign each PZT voltage (temperature in nastran) to its corresponding ID in the input data dictionary
        for i in range(len(V)):
            input_data['V'+str(i+1)] = print_float_8(V[i])

        #Read the input file template
        f = open(self.template_file,'r')
        tmp = f.read()
        f.close()

        #Replace the input data contained in the dictionary onto the new input file
        new_file = tmp.format(**input_data)

        inp = open(self.input_filepath,'w')
        inp.write(new_file)
        inp.close()


    def get_output_data(self):

        #Read the punch and output files only if they exist and their last modified date is older than input file one

        while(not os.path.isfile(self.output_filepath)): pass

        while(os.path.getmtime(self.output_filepath) <= os.path.getmtime(self.input_filepath)): pass

        while(not os.path.isfile(self.output_file)): pass

        while(os.path.getmtime(self.output_file) <= os.path.getmtime(self.input_filepath)): pass

        u = np.zeros((self.ns,3))

        shell_stress = []

        mass = 0.

        #Read the Nastran punch file (.pnh) and extract displacement and stress data
        with open(self.output_filepath) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for i in range(len(lines)):
                if len(lines[i]) > 1:

                    #Write nodal displacements onto u if the node belongs to the outer surface
                    if lines[i][0] in self.node_id and lines[i][1] == 'G':
                        u[self.node_id.index(lines[i][0])][0] = lines[i][2]
                        u[self.node_id.index(lines[i][0])][1] = lines[i][3]
                        u[self.node_id.index(lines[i][0])][2] = lines[i][4]

                    if isint(lines[i][0]) and isfloat(lines[i][1]):
                        #Store stresses only if the element is of shell type:
                        if lines[i+1][0] == '-CONT-' and lines[i+2][0] == '-CONT-' and lines[i+3][0] == '-CONT-' and lines[i+4][0] == '-CONT-' and lines[i+5][0] == '-CONT-':
                            #Write shell principal stresses onto a list (upper and lower shell faces)
                            shell_stress.append(((float(lines[i+1][3]), float(lines[i+2][1])), (float(lines[i+4][2]), float(lines[i+4][3]))))

        #Compute the Von Mises Stress on the structure
        VM = []

        for s in shell_stress:
            VM.append(np.sqrt(s[0][0]**2 - s[0][0]*s[0][1] + s[0][1]**2))
            VM.append(np.sqrt(s[1][0]**2 - s[1][0]*s[1][1] + s[1][1]**2))

        VMStress = np.asarray(VM)

        #Read the Nastran output file (.out) and extract the total mass of the structure (M)
        with open(self.output_file) as f:
            lines = f.readlines()
            lines = [i.split() for i in lines]

            for i in range(len(lines)):
                if len(lines[i]) > 4:
                    if lines[i][4] == 'MASS' and lines[i][5] == 'X-C.G.':
                        mass = float(lines[i+1][1].replace('D', 'E'))

        output_data = {}

        output_data['u'] = u
        output_data['VMStress'] = VMStress
        output_data['mass'] = mass

        return output_data
