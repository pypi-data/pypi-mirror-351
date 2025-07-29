#!/usr/bin/env python3
import toml
import glob
import os
import sys
import copy
import shutil
import argparse

elems_valences = {
    "H":  "+1; 0/-1",
    "He": "0",
    "Li": "+1; 0",
    "Be": "0",
    "B":  "+3; +2/+1/0",
    "C":  "+4/+2/-4; +3/+1/0/-1/-2/-3",
    "N":  "-3; 0/-1/-2/-3",
    "O":  "-2; -1/0",
    "F":  "-1",
    "Ne": "0",
    "Na": "+1; 0",
    "Mg": "+2; +1/0",
    "Al": "+3; +2/+1/0",
    "Si": "+4; +3//0",
    "P":  "+5; +4//0",
    "S":  "+6; +4//0",
    "Cl": "-1; 0",
    "Ar": "0",
    "K":  "+1; 0",
    "Ca": "+2; +1/0",
    "Sc": "+3; +2/+1/0",
    "Ti": "+4/+3; +2/+1/0",
    "V":  "+5; +4/+3/+2/+1/0",
    "Cr": "+3; +2/+1/0",
    "Mn": "+4/+2; +1/0",
    "Fe": "+3/+2; +1/0",
    "Co": "+3/+2; +4/+1/0",
    "Ni": "+2/+3; +1/0",
    "Cu": "+2/+1; 0",
    "Zn": "+2; +1/0",
    "Ga": "+3; +2//0",
    "Ge": "+4; +3/+2/+1/0",
    "As": "+3/+5; +4/+2/+1/0",
    "Se": "-2; -1/0",
    "Br": "-1; 0",
    "Kr": "0",
    "Rb": "+1; 0",
    "Sr": "+2; +1/0",
    "Y":  "+3; +2//0",
    "Zr": "+4; +3//0",
    "Nb": "+5; +4//0",
    "Mo": "+6; +5//0",
    "Tc": "+7; +6//0",
    "Ru": "+4/+3; +2/+1/0",
    "Rh": "+3; +2/+1/0",
    "Pd": "+4; +3/+2/+1/0",
    "Ag": "+1; +2/0",
    "Cd": "+2; +1/0",
    "In": "+3; +2/+1/0",
    "Sn": "+4; +3//0",
    "Sb": "+5; +4//0",
    "Te": "+6; +5//0",
    "I":  "-1; 0",
    "Xe": "0",
    "Cs": "+1; 0",
    "Ba": "+2; +1/0",
    "La": "+3; +2//0",
    "Ce": "+3/+4; +4//0",
    "Pr": "+3/+4; +4//0",
    "Nd": "+3; +2//0",
    "Pm": "+3; +2//0",
    "Sm": "+3/+2; +1/0",
    "Eu": "+3/+2; +1/0",
    "Gd": "+3; +2/+1/0",
    "Tb": "+3/+4; +2/+1/0",
    "Dy": "+3; +2/+1/0",
    "Ho": "+3; +2/+1/0",
    "Er": "+3; +2/+1/0",
    "Tm": "+3; +2/+1/0",
    "Yb": "+3/+2; +1/0",
    "Lu": "+3; +2/+1/0",
    "Hf": "+4; +3/+2/+1/0",
    "Ta": "+5; +4/+3/+2/+1/0",
    "W":  "+6; +5/+4/+3/+2/+1/0",
    "Re": "+7/+6; +5/+4/+3/+2/+1/0",
    "Os": "+4; +3/+2/+1/0",
    "Ir": "+3; +2/+1/0",
    "Pt": "+2/+4; +3/+1/0",
    "Au": "+1; 0",
    "Hg": "+1; 0",
    "Tl": "+1; 0",
    "Pb": "+2/+4; +3/+1/0",
    "Bi": "+3; +2/+1/0",
    "Po": "+4; +3/+2/+1/0",
    "At": "-1; 0",
    "Rn": "0",
}

def parse_valence(val_in: str):
    v1 = val_in.split(";")
    v1main = []
    v2 = v1[0]
    if "//" in v2:
        v3 = [ int(t1.strip()) for t1 in v2.split("//")]
        if v3[0]>v3[1]:
            step3 = -1
        else:
            step3 = +1
        v4 = list(range(v3[0],v3[1]+step3,step3))
    else:
        v4 = [ int(t1.strip()) for t1 in v2.split("/")]
    for v5 in v4:
        if v5 not in v1main:
            v1main.append(v5)
    v1sub = []
    if len(v1)==2:
        v2 = v1[1]
        if "//" in v2:
            v3 = [ int(t1.strip()) for t1 in v2.split("//")]
            if v3[0]>v3[1]:
                step3 = -1
            else:
                step3 = +1
            v4 = list(range(v3[0],v3[1]+step3,step3))
        else:
            v4 = [ int(t1.strip()) for t1 in v2.split("/")]
        for v5 in v4:
            if v5 not in v1sub and v5 not in v1main:
                v1sub.append(v5)
    return {"main":v1main, "sub":v1sub}

def setup_folders_vasp():
    parser = argparse.ArgumentParser(
        prog='pydecs-run-setupFolders',
        description='Generating folders for VASP run'
    )
    parser.add_argument(
        'input_toml', 
        nargs="?",
        type=str, 
        default="inpydecs_setup.toml",
        help='Path to input toml file')
    parser.add_argument(
        "-p", "--print_template",
        action="store_true",
        help='Printout template input file (inpydecs_genDefs.toml)')
    args = parser.parse_args()
    toml_path = args.input_toml
    if args.print_template:
        str_input_template = """
input_paths_strs = ["",""]

valence.Ga = "+3; +2//0"
valence.O = "-2; -1//0"

# set_nupdown = true

"""
        if not os.path.exists(toml_path):
            fout1 = open("inpydecs_setup.toml","w")
            fout1.write(str_input_template)
        else:
            print(str_input_template)
            print("### Input-file name is \"inpydecs_setup.toml\", wihch already exists in this folder.")
        sys.exit()

    print(f"  Starting setup_folders_vasp")
    run_list = open("run_list.txt", "w")
    if not os.path.exists(toml_path):
        print(f"  Error: '{toml_path}' not found.")
        print(f"    Template file is output by option \"-p\" ")
        sys.exit()
    params_in = toml.load(toml_path)

    input_paths = params_in.get("input_paths_strs")
    if input_paths is None:
        sys.exit("  Error: Key 'input_paths_strs' not found in the input file.")

    set_nupdown = False
    input_nupdown = params_in.get("set_nupdown")
    if input_paths != None:
        set_nupdown = input_nupdown
    print(f"  set_nupdown = {set_nupdown}")

    valences_dict1 = copy.deepcopy(elems_valences)
    input_vals = params_in.get("valence")
    if input_paths != None:
        for k1,v1 in input_vals.items():
            if k1 not in valences_dict1:
                print(f"  {k1} for the valence setting from the input file, not exist in the default element list, but continued.")
            valences_dict1[k1] = v1

    vasp_files = []
    print(f"  Searching vasp files:")
    for p in input_paths:
        pattern = os.path.join(p, "defModel_*.vasp")
        matched = glob.glob(pattern)
        print(f"    Folder-name: '{p}'")
        print(f"      Found {len(matched)} files.")
        vasp_files.extend(matched)
    vasp_files.sort()

    if not vasp_files:
        print("Warning: No files matching 'defModel_*.vasp' were found in the specified directories.")
    elems_set = set()
    for f1 in vasp_files:
        f2 = os.path.basename(f1)
        if "supercell" in f2:
            continue
        f3 = f2.split("_")
        e1 = f3[2].strip()
        e2 = f3[3].strip()
        e3 = e2.split("[")[0]
        if "vac" != e1.lower():
            elems_set.add(e1)
        if "int" != e3.lower():
            elems_set.add(e3)
    str1 = "  Elements:"
    for e1 in elems_set:
        str1 += f" {e1},"
    print(f"{str1[:-1]}")
    
    valences_dict2 = {}
    for e1 in elems_set:
        v1 = valences_dict1[e1]
        valences_dict2[e1] = parse_valence(v1)
    print(f"  Valence list:")
    for k2,v2 in valences_dict2.items():
        str1 = f"    {k2}-main:"
        for v3 in v2["main"]:
            str1 += f" {v3},"
        print(f"{str1[:-1]}")
        str1 = f"    {k2}-sub:"
        for v3 in v2["sub"]:
            str1 += f" {v3},"
        print(f"{str1[:-1]}")
    
    cwd = os.getcwd()
    path_INCAR_temp = os.path.join(cwd, "INCAR_temp")
    path_kpoints = os.path.join(cwd, "KPOINTS")
    if not os.path.exists(path_INCAR_temp):
        sys.exit(f"  Error: INCAR_temp not found: '{path_INCAR_temp}'")
    if not os.path.exists(path_kpoints):
        path_kpoints = None
    for f1 in vasp_files:
        f2 = os.path.basename(f1)
        fol3 = f2[f2.find("_")+1:f2.find(".vasp")]
        os.makedirs(fol3, exist_ok=True)
        print(f"  Making der: {fol3} ")
        shutil.copy(f1, fol3)
        with open(f1) as fin1:
            fin2 = fin1.readlines()
            elems = [ t1.strip() for t1 in fin2[5].split()]
            natoms =  [ int(t1) for t1 in fin2[6].split()]
        path_POTCAR = os.path.join(fol3, "POTCAR")
        NELECT = 0
        with open(path_POTCAR, "w") as f_pot:
            for e1,n1 in zip(elems,natoms):
                pot_src = os.path.join(cwd, f"POTCAR_{e1}")
                if not os.path.exists(pot_src):
                    sys.exit(f"  Error: POTCAR_<elem> not found: '{pot_src}'")
                zval1 = None
                with open(pot_src) as f_in:
                    l1 = f_in.readline()
                    while l1:
                        f_pot.write(l1)
                        if "ZVAL" in l1:
                            zval1 = int(float(l1.split()[5]))
                        l1 = f_in.readline()
                NELECT += zval1*n1
        print(f"    {NELECT = }")
        qmain_list =[]
        qsub_list =[]
        def3 = fol3[fol3.find("_")+1:]
        if "supercell" in def3:
            qmain_list.append(0)
        else:
            def4 = def3.split("_")
            e4 = def4[0]
            s4 = def4[1]
            es4 = s4.split("[")[0]
            qe4_main = [0]
            qe4_sub = [0]
            if e4 in valences_dict2:
                qe4_main = valences_dict2[e4]["main"]
                qe4_sub = valences_dict2[e4]["sub"]
            qes4_main = [0]
            qes4_sub = [0]
            if es4 in valences_dict2:
                qes4_main = valences_dict2[es4]["main"]
                qes4_sub = valences_dict2[es4]["sub"]
            for q4 in qe4_main:
                for qs4 in qes4_main:
                    dq4 = q4-qs4
                    if dq4 not in qmain_list:
                        qmain_list.append(dq4)
            qsub_list =[]
            for q4 in qe4_main+qe4_sub:
                for qs4 in qes4_main+qes4_sub:
                    dq4 = q4-qs4
                    if dq4 not in qmain_list and dq4 not in qsub_list:
                        qsub_list.append(dq4)
            qmain_list.sort(reverse=True)
            qsub_list.sort(reverse=True)
        for iq1,q1 in enumerate(qmain_list+qsub_list):
            folder2 = os.path.join(fol3,f"{iq1+1:03}_q{q1}")
            os.makedirs(folder2, exist_ok=True)
            print(f"    Making der: {folder2} ")
            NUDlist = ["None"]
            if set_nupdown:
                for q2 in qmain_list:
                    dq12 = abs(q2-q1)
                    NUDlist_tmp = list(range(dq12,-1,-2))
                    for nud1 in NUDlist_tmp:
                        if nud1 not in NUDlist:
                            NUDlist.append(nud1)
            print(f"      {NUDlist = }")
            for inud1,nud1 in enumerate(NUDlist):
                # folder3 = f"{folder2}/{inud1+1:03}_nud{nud1}"
                folder3 = os.path.join(folder2,f"{inud1+1:03}_nud{nud1}")
                os.makedirs(folder3, exist_ok=True)
                print(f"      Making der: {folder3} ")
                shutil.copy(f1, os.path.join(folder3, "POSCAR"))
                if path_kpoints != None:
                    shutil.copy(path_kpoints, os.path.join(folder3, "KPOINTS"))
                shutil.copy(path_POTCAR, os.path.join(folder3, "POTCAR"))

                nelect3 = NELECT - q1
                out_path = os.path.join(folder3, "INCAR_temp2")
                with open(out_path, "w") as fout:
                    fout.write(f"\nNELECT = {nelect3}\n")
                    if nud1 != "None":
                        fout.write(f"NUPDOWN = {nud1}\n")
                    with open(path_INCAR_temp) as fin:
                        fout.write(fin.read())
                run_list.write(os.path.abspath(folder3) + "\n")
    return 

def apply_extFNV_to_all():
    from pydecs.aux_EdefCorrection_VASP import calcEdefCorrectionVASP
    print(f"  Starting automatic FNV correction")
    parser = argparse.ArgumentParser(
        prog='pydecs-run-autoFNV',
        description='Applying FNV corrections using run_list.txt and inpydecs_Edef.toml.'
    )
    if not os.path.exists("run_list.txt"):
        sys.exit(f"  Error: run_list.txt not found in the current forlder")
    run_list = [ t1.strip() for t1 in open("run_list.txt").readlines()]
    cwd = os.getcwd()
    path_inEdef = os.path.join(cwd, "inpydecs_Edef.toml")
    if not os.path.exists(path_inEdef):
        sys.exit(f"  Error: inpydecs_Edef.toml not found in the current forlder")
    for fol1 in run_list:
        print(fol1)
        fol2 = os.path.join(fol1,"post_FNV")
        print(f"  Creating: {fol2}")
        os.makedirs(fol2, exist_ok=True)
        os.chdir(fol2)
        shutil.copy(path_inEdef,"./")
        if os.path.exists("../OUTCAR"):
            print(f"  Adopting FNV correction")
            try:
                calcEdefCorrectionVASP()
            except SystemExit as e:
                e
        else:
            print(f"  Skipping FNV correction due to the absence of ../OUTCAR")
    return

def collect_energies_vasp():
    from pathlib import Path
    print(f"  Starting to collect the relaxed energies")
    if not os.path.exists("run_list.txt"):
        sys.exit(f"  Error: run_list.txt not found in the current forlder")
    cwd = os.getcwd()
    run_list = [ t1.strip() for t1 in open("run_list.txt").readlines()]
    paths_defects = []
    paths_Q = {}
    for fol1 in run_list:
        fol2 = fol1[:fol1.rfind("/")]
        fol2Q = fol2[fol2.rfind("/")+1:]
        fol3 = fol2[:fol2.rfind("/")]
        fol3def = fol3[fol3.rfind("/")+1:]
        
        if fol3def not in paths_defects:
            paths_defects.append(fol3def)
        if fol3def not in paths_Q:
            paths_Q[fol3def] = [fol2Q]
        else:
            if fol2Q not in paths_Q[fol3def]:
                paths_Q[fol3def].append(fol2Q)
    enelist = []
    path_FNV="post_FNV/out_pydecs_Edef.txt" 
    for fol1 in run_list:
        print(f"  chdir: {fol1}")
        os.chdir(fol1)
        files = list(Path('.').rglob('OUTCAR*'))
        files_sorted = sorted(files, key=lambda p: p.stat().st_mtime)
        print(files_sorted)
        istep2 = 0 
        nstep = 0
        bool_conv = False
        fout2 = open("res_energies_during_relax.csv","w")
        for f2 in files_sorted:
            fin2 = open(f2)
            nstep = 0
            bool_conv = False
            for i2, l2 in enumerate(fin2, start=1):
                if "entropy= " in l2:
                    e2 = float(l2.split()[-1])
                    enelist.append(e2)
                    nstep += 1
                    istep2 += 1
                    fout2.write(f"{istep2}, {e2}\n")
                if "stopping structural energy minimisation" in l2:
                    bool_conv = True
        ene_fnv = "0.0"
        if os.path.exists(path_FNV):
            with open(path_FNV) as fin_fnv:
                l1=fin_fnv.readline()
                while l1:
                    if "Ecorr =" in l1:
                        l1=fin_fnv.readline()
                        ene_fnv = l1.split()[-1].strip()
                    l1=fin_fnv.readline()
        fout3 = open("res_energy_fin.csv","w")
        fout2.write(f"# ene_fnv = {ene_fnv} \n")
        if bool_conv==True and nstep==1:
            fout2.write(f"# Converged \n")
            fout3.write(f"{e2}, {ene_fnv}, Converged \n")
        else:
            fout2.write(f"# Not-Converged \n")
            fout3.write(f"{e2}, {ene_fnv}, Not-Converged \n")
        fout2.close()
        fout3.close()
    
    fnin_multi = cwd+"/def_list.csv"
    muliplicity_dict0 = {}
    if os.path.exists(fnin_multi):
        fin_multi = open(fnin_multi).readlines()
        for l1 in fin_multi[1:]:
            l2 = l1.split(",")
            d2 = l2[2].strip()
            m2 = l2[3].strip()
            muliplicity_dict0[d2] = m2

    def_list = []
    Q_list = []
    ene_list = []
    efnv_list = []
    strconv_list = []
    multiplicity_list = []
    ene_perf = None
    for p1_def in paths_defects:
        for p2_Q in paths_Q[p1_def]:
            fol1 = cwd+"/"+p1_def+"/"+p2_Q
            os.chdir(fol1)
            files = list(Path('.').rglob("res_energy_fin.csv"))
            fout1 = open("res_energies_nud.csv","w")
            ene2=1e10
            efnv2=1e10
            strconv2=None
            for f1 in files:
                l1 = open(f1).readline()
                l2 = l1.split(",")
                if len(l2)==0:
                    continue
                ene1 = float(l2[0].strip())
                if ene1 < ene2:
                    ene2 = ene1
                    efnv2 = float(l2[1].strip())
                    strconv2 = l2[2].strip()
                fout1.write(l1)
            fout1.close()
            if "supercell" in p1_def:
                if "q0" in p2_Q:
                    ene_perf = ene2
            else:
                def2 = p1_def[p1_def.find("_")+1:]
                def_list.append(def2)
                q2 = p2_Q[p2_Q.find("q")+1:]
                Q_list.append(q2)
                ene_list.append(ene2)
                efnv_list.append(efnv2)
                strconv_list.append(strconv2)
                for d1,m1 in muliplicity_dict0.items():
                    if d1 in p1_def:
                        multiplicity_list.append(m1)
    if ene_perf == None:
        print("Warning: Energy for perfect cell is not set")

    
    fnin_def1 = cwd+"/inpydecs_defects.csv"
    if os.path.exists(fnin_def1):
        print("  Warning: inpydecs_defects.csv is overlapped....")
        fnin_def2 = fnin_def1+"_old"
        shutil.copy(fnin_def1,fnin_def2)
    fout5 = open(fnin_def1,"w")
    fout5.write("commentout,memo,label,defect_type,charge,energy_defect,energy_perfect,energy_correction,multiplicity,,line_color,line_style,line_width\n")
    for i1,d1 in enumerate(def_list):
        str1 = f",,{d1},{d1},"
        str1 += f"{Q_list[i1]},"
        str1 += f"{ene_list[i1]},"
        str1 += f"{ene_perf},"
        str1 += f"{efnv_list[i1]},"
        if len(multiplicity_list)>0:
            str1 += f"{multiplicity_list[i1]},"
        else:
            str1 += f"1,"
        str1 += f",,,"
        fout5.write(str1+"\n")
    return


if __name__ == "__main__":
    setup_folders_vasp()


