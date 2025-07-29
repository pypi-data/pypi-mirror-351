#!/usr/bin/env python3

"""Run Cycles simulations for different crops under different nuclear war scenarios

Run Cycles simulations
"""
import os
import pandas as pd
import subprocess
from string import Template
from setting import RM_CYCLES_IO
from .cycles_input import generate_control_file

def _generate_operation_file(template_fn, operation_fn, operation_dict):
    with open(template_fn) as f:
        operation_file_template = Template(f.read())

    with open(operatin_fn, 'w') as f:
        f.write(operation_file_template.substitute(operation_dict))


def _generate_control_file(control_fn, control_dict):
    with open(control_fn) as f:
        control_file_template = Template(f.read())

    with open(f'./input/{gid}.ctrl', 'w') as f:
        f.write(control_file_template.substitute(control_dict))


def _run_cycles(simulation, spin_up=False):
    if spin_up == False and uv == False:
        cmd = [CYCLES, simulation]
    else:
        options = '-'
        if spin_up: options += 's'
        if uv: options += 'u'
        cmd = [CYCLES, options, simulation]

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode


def write_summary(gid, row, header, summary_fp):
    df = pd.read_csv(
        f'output/{gid}/season.txt',
        sep='\t',
        header=0,
        skiprows=[1],
        skipinitialspace=True,
    )
    df = df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'))
    df['crop'] = df['crop'].str.strip()
    df.insert(0, 'gid', gid)
    df.insert(1, 'area_km2', row['AreaKm2'])
    df.insert(2, 'area_fraction', row['AreaFraction'])

    strs = df.to_csv(header=header, index=False)

    summary_fp.write(''.join(strs))


def write_water_summary(gid, header, water_summary_fp):
    df1 = pd.read_csv(
        f'output/{gid}/environ.txt',
        sep='\t',
        header=0,
        skiprows=[1, 2],
        skipinitialspace=True,
        index_col=0,
    )

    df2 = pd.read_csv(
        f'output/{gid}/water.txt',
        sep='\t',
        header=0,
        skiprows=[1, 2],
        skipinitialspace=True,
        index_col=0,
    )

    df = df2.join(df1, how='inner')
    df = df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'))
    df['year'] = df.index.str[:4]
    df = df[['soil_evap', 'res_evap', 'snow_sub', 'transpiration', 'precipitation']].groupby(df['year']).sum()
    df.insert(0, 'gid', gid)
    df.insert(1, 'year', df.index)

    strs = df.to_csv(header=header, index=False)

    water_summary_fp.write(''.join(strs))


def main(params):
    os.makedirs('summary', exist_ok=True)

    max_temperature = CROPS[crop]['maximum_temperature']
    min_temperature = CROPS[crop]['minimum_temperature']

    # Read in look-up table or run table
    with open(RUN_FILE(lookup_table, crop)) as f:
        reader = csv.reader(f, delimiter=',')

        headers = next(reader)
        data = [{h:x for (h,x) in zip(headers,row)} for row in reader]

    first = True

    counter = 0
    with open(SUMMARY_FILE(lookup_table, scenario, crop, adaptation, uv), 'w') as summary_fp, open(WATER_SUMMARY_FILE(lookup_table, scenario, crop, adaptation, uv), 'w') as water_summary_fp:
        # Run each region
        for row in data:
            if not row: continue    # Skip empty lines

            gid = row['GID']
            weather = f'{scenario}/{scenario}_{row["Weather"]}.weather' if lookup_table == 'EOW' else row['Weather']
            soil = row['Soil']

            print(
                f'{gid} - [{weather}, {soil}] - ',
                end=''
            )

            planting_date = row['pd']
            if lookup_table == 'EOW':
                if adaptation == 2:     # Full adaptation
                    hybrids = [row[CONTROL_SCENARIO] if y <= INJECTION_YEAR else row[f'{scenario}_{y:04}'] for y in range(start_year, end_year + 1)]
                elif adaptation == 1:   # Partial adaptation, choose hybrid based on last year's weather
                    hybrids = [row[CONTROL_SCENARIO] if y <= INJECTION_YEAR else row[f'{scenario}_{(y - 1):04}'] for y in range(start_year, end_year + 1)]
                else:
                    hybrids = [row[CONTROL_SCENARIO]]
                rotation_size = end_year - start_year + 1 if adaptation > 0 else 1
            else:
                hybrids = [row['crop']]
                rotation_size = 1

            # Run Cycles spin-up
            generate_operation_file(gid, hybrids, rotation_size, max_temperature, min_temperature, planting_date)
            generate_control_file(gid, f'soil/{soil}', weather, start_year, INJECTION_YEAR - 1 if lookup_table == 'EOW' else end_year, rotation_size)
            _run_cycles(gid, spin_up=True, uv=uv)

            # If running EOW, run Cycles again using steady state soil
            if lookup_table == 'EOW':
                generate_control_file(gid, f'{gid}_ss.soil', weather, start_year, end_year, rotation_size)
                _run_cycles(gid, spin_up=False, uv=uv)

            try:
                write_water_summary(gid, first, water_summary_fp)
                write_summary(gid, row, first, summary_fp)
                if first: first = False
                print('Success')
            except:
                print('Cycles errors')

            # Remove generated input/output files
            subprocess.run(
                RM_CYCLES_IO,
                shell='True',
            )

            counter += 1
            #if counter == 250: break


def _main():
    parser = argparse.ArgumentParser(description='Cycles execution for a crop')
    parser.add_argument(
        '--crop',
        default='maize',
        choices=CROPS,
        help='Crop to be simulated',
    )
    parser.add_argument(
        '--lut',
        default='global',
        choices=['global', 'CONUS', 'EOW', 'test'],
        help='Look-up table to be used',
    )
    parser.add_argument(
        '--scenario',
        default='nw_cntrl_03',
        choices=SCENARIOS,
        help='EOW NW scenario',
    )
    parser.add_argument(
        '--start',
        required=True,
        type=int,
        help='Start year of simulation (use 0001 for EOW simulations)',
    )
    parser.add_argument(
        '--end',
        required=True,
        type=int,
        help='End year of simulation (use 0019 for EOW simulations)',
    )
    parser.add_argument("-v", "--verbosity", action="count", default=0,
                    help="increase output verbosity")

    parser.add_argument(
        '--adaptation',
        type=int,
        default=0,
        choices=[0, 1, 2],
        help='Flag for adaptation strategy',
    )
    parser.add_argument(
        '--uv',
        action='store_true',
        help='Flag for UV effect',
    )
    parser.set_defaults(uv=False)
    args = parser.parse_args()

    main(vars(args))
