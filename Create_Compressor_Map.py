#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:36:18 2019
@author: sauer, elshof, stoewer
"""

import os
import time
import sys
import numpy as np

def run_map(stepList, timesteps, trace_control_cmd, nodes, cpus, mem, gmcPlay_exe, POST_EXE, start_point):
    simulation_dir = []
    for sim_number, pressure in enumerate(stepList):
        print('Starte')
        i = sim_number + start_point

        print('sim_number + starter_point = {}'.format(i))

        os.system('mkdir %02i_4AV_n17100_p60kPa_p%ikPa_Tt288'%(i, folderName[i]))
        os.chdir('./%02i_4AV_n17100_p60kPa_p%ikPa_Tt288'%(i, folderName[i]))
        cur_wd = os.getcwd()
        os.system('mkdir input run')
        os.system('cp  %s/TRACE_control.input %s/input'%(trace_tools_dir, cur_wd))
        os.system('cp  %s/job_TRACE.sh %s/run'%(trace_tools_dir, cur_wd))
        os.system('cp  %s/set_back_pressure.jou %s/input'%(trace_tools_dir, cur_wd))
        os.system('cp  %s/set_timesteps.jou %s/input'%(trace_tools_dir, cur_wd))
        os.system('cp  %s/pyTRACE_uni.py %s/run'%(trace_tools_dir, cur_wd))
        os.system('cp  %s/pyTRACE_Input.dat %s/run'%(trace_tools_dir, cur_wd))
        os.chdir('./run')
        os.system("sed -i s/REPLACE_JOB/%02i_4AV_n17100_p60kPa_p%ikPa_SST_Off_Bardina/g job_TRACE.sh"%(i, folderName[i]))
        os.system("sed -i s/REPLACE_NODES/%s/g job_TRACE.sh"%(nodes))
        os.system("sed -i s/REPLACE_CPUS/%s/g job_TRACE.sh"%(cpus))
        os.system("sed -i s/REPLACE_MEM/%s/g job_TRACE.sh"%(mem))
        os.chdir('../input')

        print('Ausführen der Befehle')

        if i != 0:
            print('Copy last simulation as initialization')	
            os.system('cp ../../%02i_4AV_n17100_p60kPa_p%ikPa_Tt288/output/cgns/TRACE.cgns ./'%(i-1, folderName[i-1]))
            os.system('cp ../../%02i_4AV_n17100_p60kPa_p%ikPa_Tt288/input/TRACE_entry.input ./'%(i-1, folderName[i-1]))
            f= open("set_back_pressure.jou","a+")
            f.write("gmc -> set_solver_properties for 'machine' : Restart to On\n")
            f.write("gmc -> set_solver_properties for 'IGV' : Restart to  On \n")
            f.write("gmc -> set_solver_properties for 'R1' : Restart to On \n")
            f.write("gmc -> set_solver_properties for 'R3' : Restart to On\n")
            f.write("gmc -> set_solver_properties for 'R4' : Restart to On \n")
            f.write("gmc -> set_solver_properties for 'S4' : Restart to On\n")
            f.write("gmc -> set_solver_properties for 'R2' : Restart to On \n")
            f.write("gmc -> set_solver_properties for 'S2' : Restart to On \n")
            f.write("gmc -> set_solver_properties for 'S3' : Restart to On \n")
            f.write("gmc -> set_solver_properties for 'S1' : Restart to On \n")
            f.write("gmc -> save 'TRACE.cgns'\n")
            f = open('%s/output/residual/residual.dat'%(script_path ), 'r')
            lines = f.read().splitlines()
            lastline =  lines[-1]
            old_timestep = lastline.split()
            old_timestep = int(float(old_timestep[0]))
            new_timestep = old_timestep + timesteps
            os.system("sed -i s/REPLACE_TIMESTEP/%s/g set_timesteps.jou"%(new_timestep))
        else:
            new_timestep = 10000
            os.system('cp  %s/TRACE.cgns %s/input/.'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/S2M_average_mass.dat %s/input/.'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/TRACE_entry.input %s/input/.'%(trace_tools_dir, cur_wd))
            os.system("sed -i s/REPLACE_TIMESTEP/%s/g set_timesteps.jou"%(new_timestep))
        os.system("sed -i s/REPLACE_PRESSURE/%s/g set_back_pressure.jou"%(stepList[i]))
        os.system(str(gmcPlay_exe) + " set_back_pressure.jou > gmc.log")
        print('Set back pressure to %d Pa'%(folderName[i]))
        os.system(str(gmcPlay_exe) + " set_timesteps.jou > gmc.log")
        print('Set new max timestep to %i'%(new_timestep))
        os.system('cd ../run/ && yes | sbatch job_TRACE.sh && sleep 3')
        os.chdir(script_path + '/%02i_4AV_n17100_p60kPa_p%ikPa_Tt288'%(i, folderName[i]))
        print(os.getcwd())
        print('Simulation has been started')
        time.sleep(5400)
        print('Warte bis sich datein füllen')

        while os.path.isfile('./run/TRACE_job.dat') is False:
            time.sleep(600)
            print('Warte weiter')
            continue
        test = open('./run/TRACE_job.dat','r').read()
        if 'errorcode 1' in test:
            print('Simulation not converged - Switching to mass flow BC')
            return [1, i]
        else:
            print('Simulation converged, starting next simulation')
            os.system('rm ./run/TRACE.lst.*')
            os.system('rm ./output/cgns/TRACE.cgns.backup')
        os.chdir('./output/cgns/')
        os.system('cp  %s/merge.jou %s'%(trace_tools_dir, os.getcwd()))
        os.system(str(gmcPlay_exe) + " merge_heiss.jou > gmc.log")
        time.sleep(60)

        simulation_dir.append(cur_wd)
        os.chdir(script_path)

        print('Fertig')

    return 0


def continue_map(sim_number, timesteps, trace_control_cmd, nodes, cpus, mem, gmcPlay_exe, folderName):
        i = sim_number
        f = open('%s/%02i_4AV_n17100_p60kPa_p%ikPa/output/residual/d0_mass_IGV_INFLOW.dat'%(script_path, i-1, folderName[i-1]), 'r')
        lines = f.read().splitlines()
        lastline =  lines[-1]
        old_massflow = lastline.split()
        old_massflow = float(float(old_massflow[1]))
        new_massflow = old_massflow - 0.10
        for n in range(i, i+5):
            os.system('mkdir %02i_4AV_n17100_p60kPa_m%10.2fkgs'%(n, new_massflow))
            os.chdir('./%02i_4AV_n17100_p60kPa_m%10.2fkgs'%(n, new_massflow))
            cur_wd = os.getcwd()
            os.system('mkdir input run')
            os.system('cp  %s/TRACE_control.input %s/input'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/job_TRACE.sh %s/run'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/set_outlet_massflow.jou %s/input'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/set_timesteps.jou %s/input'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/pyTRACE_uni.py %s/run'%(trace_tools_dir, cur_wd))
            os.system('cp  %s/pyTRACE_Input.dat %s/run'%(trace_tools_dir, cur_wd))
            os.chdir('./run')
            os.system("sed -i s/REPLACE_JOB/%02i_4AV_n17100_p60kPa_m%10.2fkgs/g job_TRACE.sh"%(n, new_massflow))
            os.system("sed -i s/REPLACE_NODES/%s/g job_TRACE.sh"%(nodes))
            os.system("sed -i s/REPLACE_CPUS/%s/g job_TRACE.sh"%(cpus))
            os.system("sed -i s/REPLACE_MEM/%s/g job_TRACE.sh"%(mem))
            os.chdir('../input')
            # f = open("TRACE_control.input","w+")
            # for cmd in range(len(trace_control_cmd)):
            #  f.write("%s\n" % (trace_control_cmd[cmd]))
            #  f.close
            if n == i:

                print('Copy last simulation as initialization')	
                os.system('cp ../../%02i_4AV_n17100_p60kPa_p%ikPa/output/cgns/TRACE.cgns ./'%(n-1, folderName[i-1]))
                os.system('cp ../../%02i_4AV_n17100_p60kPa_p%ikPafkgs/input/TRACE_entry.input ./'%(n-1, folderName[i-1]))
                f = open('%s/%02i_4AV_n17100_p60kPa_p%ikPa/output/residual/residual.dat'%(script_path, i-1, folderName[i-1]), 'r')
                lines = f.read().splitlines()
                lastline =  lines[-1]
                old_timestep = lastline.split()
                old_timestep = int(float(old_timestep[0]))
                new_timestep = old_timestep + timesteps
            else:
                print('Copy last simulation as initialization')	
                os.system('cp ../../%02i_4AV_n17100_p60kPa_p%ikPa/output/cgns/TRACE.cgns ./'%(n-1, folderName[i-1]))
                os.system('cp ../../%02i_4AV_n17100_p60kPa_p%ikPafkgs/input/TRACE_entry.input ./'%(n-1, folderName[i-1]))
                f = open('%s/%02i_4AV_n17100_p60kPa_m%10.2fkgs/output/residual/residual.dat'%(script_path, i-1, folderName[i-1]), 'r')
                lines = f.read().splitlines()
                lastline =  lines[-1]
                old_timestep = lastline.split()
                old_timestep = int(float(old_timestep[0]))
                new_timestep = old_timestep + timesteps
            os.system("sed -i s/REPLACE_TIMESTEP/%s/g set_timesteps.jou"%(new_timestep))

            os.system("sed -i s/REPLACE_MASSFLOW/%s/g set_outlet_massflow.jou"%(stepList[i]))

            os.system(str(gmcPlay_exe) + " set_outlet_massflow.jou > gmc.log")
            print('Set back outlet mass flow to %d kgs'%(new_massflow))

            os.system(str(gmcPlay_exe) + " set_timesteps.jou > gmc.log")
            print('Set new max timestep to %i'%(new_timestep))

            os.system('cd ../run/ && yes | sbatch job_TRACE.sh && sleep 3')
            os.chdir(script_path + '/%02i_4AV_n17100_p60kPa_m%10.2fkgs'%(n, new_massflow))
            print(os.getcwd())
            print('Simulation has been started')

            time.sleep(10800)

            while os.path.isfile('./run/TRACE_job.dat') is False:
                time.sleep(600)
                continue

            if open('./run/TRACE_job.dat','r').read().find('with errorcode 1') is True:
                print('Simulation not converged - Switching to mass flow BC')
                return [1, i]

            elif open('./run/TRACE.lst.001','r').read().find('TRACE  terminated normally') is True:
                print('Simulation converged, starting next simulation')

            os.chdir('./output/cgns/')
            #os.system('cp  %s/merge.jou %s'%(trace_tools_dir, os.getcwd()))
            #os.system(str(gmcPlay_exe) + " merge_heiss.jou > gmc.log")
            time.sleep(60)
            #os.system(POST_EXE+' --input TRACE.cgns -rbc --createBandedInterfaces --averaging --TurbomachineryAnalysis_0D1D -cda -ulist ../../post/gta.ulst -tecplotASCII ../../post >>' + cur_wd + '/post.log')

            simulation_dir.append(cur_wd)
            os.chdir(script_path)
            new_massflow = old_massflow - 0.10


def read_d0_variable(postdir,var,zones=['4AV'],d0type='primitives',ave='mass'):
    '''
    Get value of specified variable "var" from TRACE post processing d0-file 
    "postfile" at one or several "zones"
    '''
    postfile = os.path.join(postdir,'d0_'+d0type+'_'+ave+'.dat')

    n_zones = len(zones)    

    flag_var = False
    flag_zone = False

    infile = open(postfile)

    values = np.zeros((n_zones,1))
    i = 0

    for line in infile:
        zone = zones[i]
        if zone in line:
            flag_zone = True
            continue

        if flag_zone and var in line:
            flag_var = True
            continue

        if flag_var:
            values[i,0] = np.float(line)
            flag_var = False
            flag_zone = False
            if i<n_zones-1:
                i += 1
            else:
                break

    infile.close()

    if n_zones==1:
        return values[0,0]
    else:    
        return values


def create_map_file(script_path,POST_EXE):

    os.chdir(script_path)

    with open('map_data.dat','w+') as f:
        f.write('Back Pressure[Pa] MassFlow[kg/s] MassFlow_corr[kg/s] PI_t EffPoly[%] EffIsen[%] Ma_in T_in[K]\n')
    ls
    subfolders = [f.path for f in os.scandir(os.getcwd()) if f.is_dir() ]
    print(subfolders)

    for sim_dir in subfolders:
        os.system(POST_EXE+' --input ' + sim_dir + '/output/cgns/TRACE.cgns -rbc --createBandedInterfaces --averaging --TurbomachineryAnalysis_0D1D -cda -ulist ' + sim_dir + '/post/gta.ulst -tecplotASCII ' + sim_dir + '/post/ >> ' + sim_dir + '/post.log')
        print('TRACE Post finished')
	#time.sleep(90)
    for sim_dir in subfolders:
        if os.path.exists(sim_dir + '/post'): 

            postdir = os.path.join(sim_dir,'post')

            MassFlow = read_d0_variable(postdir,'MassFlowUnsigned',zones=['IGV_INFLOW'])
            MassFlow_corr = read_d0_variable(postdir,'MassFlowCorrected',zones=['IGV_INFLOW'])

            EffPoly = read_d0_variable(postdir,'EfficiencyPolytropic',d0type='relations')
            PI_t = re48gbad_d0_variable(postdir,'PressureStagnationAbsRatio',d0type='relations')
            PressureIn = read_d0_variable(postdir,'Pressure',zones=['IGV_INFLOW'],ave='area')
            PressureOut = read_d0_variable(postdir,'Pressure',zones=['S4_OUTFLOW'],ave='area')
            Ma_in = read_d0_variable(postdir,'Mach',zones=['IGV_INFLOW'])

            PressureStatAbs=PressureOut/PressureIn
            EffIsen = read_d0_variable(postdir,'EfficiencyIsentropicHWoLeak',d0type='relations')
            T_in = read_d0_variable(postdir,'Temperature',zones=['IGV_INFLOW'],ave='area')
            TemperatureOut = read_d0_variable(postdir,'Temperature',zones=['S4_OUTFLOW'],ave='area')
            Back_pressure = read_d0_variable(postdir,'Pressure',zones=['S4_OUTFLOW'],ave='area')
            os.chdir(script_path)
            with open('map_data.dat','a+') as f:
                f.write(str(Back_pressure) + ' ' + str(MassFlow) + ' ' + str(MassFlow_corr) + ' ' + str(PI_t) + ' '  + str(EffPoly) + ' ' + str(EffIsen) + ' ' +  str(Ma_in) + ' ' + str(T_in) + '\n')


# Im Ordner sollen sich der Ordner TRACE_tools und Create_Compressor_Map.py befinden
script_path = os.path.dirname(os.path.realpath(__file__))

# Benennung der Pfade
bigwork = ('/bigwork/nhkcdael/00_4AV_pt60kPa_Tt288_p100kPa/')

# Deklaration hier nicht ändern
trace_tools_dir = ('%sTRACE_tools'%(bigwork))
gmcPlay_exe = "/home/nhkcssch/sw/sandy_bridge/gmc/9.0.26/gmcPlay_v9_0_26"
POST_EXE = "/home/nhkcssch/sw/sandy_bridge/post/9.1.538.TFD.0/POST"


# Define steplist for back pressure
stepList =  np.concatenate([np.arange(1.0, 1.3, 0.05)*10**5,  np.arange(1.3, 1.46, 0.02)*10**5, np.arange(1.46, 1.55, 0.01)*10**5])
folderName = stepList / 1000

# start_point = 0 ist default
start_point = 0

timesteps = 10000

trace_control_cmd = ['all immediate ChangeTurbulenceSettings --model MenterSST2003 --stagnationPointAnomalyFix KatoLaunder --solutionMethod ILU --rotationalEffects Bardina --transitionModel OFF\nall immediate ChangeScalarTransportAttr --model TURBULENCE --spaceAccuracy 2ndOrder']

# Cluster properties
nodes = 20
cpus = 4
mem = "20gb"

[status, sim_number] = run_map(stepList, timesteps, trace_control_cmd, nodes, cpus, mem, gmcPlay_exe, POST_EXE, start_point)
print([status, sim_number])

if status == 1:
    trace_control_cmd = ['all immediate ChangeTurbulenceSettings --model MenterSST2003 --stagnationPointAnomalyFix KatoLaunder --solutionMethod ILU --rotationalEffects Bardina --transitionModel OFF\nall immediate ChangeScalarTransportAttr --model TURBULENCE --spaceAccuracy 2ndOrder\nall immediate SetCflNum 20']
    continue_map(sim_number, timesteps, trace_control_cmd, nodes, cpus, mem, gmcPlay_exe, folderName)
