import json
from opentrons import protocol_api, types
import numpy as np
from opentrons.protocol_api import RuntimeParameterRequiredError

metadata = {
    "protocolName": "self-driving-aas PROTOCOL 2",
    "author": "Waldherr A., Max Planck Institute for Biology",
    "description": "This protocol 2 and was created during the UZH + EPFL self-driving lab hackathon 2026 and investigates how well non-standard amino acids can be incorporated into proteins using an in-vitro translation system and an IF1-mNeonGreen fluorescent readout (EXC: 440 nm, EM: 500 nm).\n",
    "created": "2026-10-22T06:41:44.599Z",
    "internalAppBuildDate": "Thu, 13 Aug 2026 17:57:06 GMT",
    "lastModified": "2026-10-22T11:30:57.242Z",
    "protocolDesigner": "26.6.0",
    "source": "Protocol Designer",
}

requirements = {"robotType": "OT-2", "apiLevel": "2.28"}


# Loading the fluorescence csv while disregarding OVER
# TODO: Get count of well A2
# TODO: Get count of wells A3, A9, A10, D2, G2, H3, H8 and find the 4 minimal ones 
# DONE: Choose random from B3, B9, B10, C3, C11, D3, E7, E9, E11, F7, G4, G7, H5, H7, H9 -> add these as variables below


EXPECTED_HEADER = ["<>","1","2","3","4","5","6","7","8","9","10","11","12"]     # this is how it is normally seen
EXPECTED_HEADER = ["ï»¿<>","1","2","3","4","5","6","7","8","9","10","11","12"]  # this is how it is if I use the csv python module'ï»¿<>'

TEST_CSV = [
        EXPECTED_HEADER,
        ["A", "4800", "5000", "2500", "0", "1200", "1200", "0", "0", "35", "OVER", "1200", "0"],
        ["B", "50", "0", "0", "1200", "5000", "5000", "0", "0", "0", "0", "0", "0"],
        ["C", "50", "1200", "0", "0", "0", "5000", "0", "1200", "5000", "5000", "0", "0"],
        ["D", "50", "2500", "0", "0", "0", "0", "0", "0", "5000", "0", "5000", "0"],
        ["E", "50", "0", "0", "5000", "0", "1200", "0", "0", "0", "0", "0", "0"],
        ["F", "50", "0", "0", "5000", "0", "0", "0", "1200", "0", "5000", "0", "0"],
        ["G", "0", "5000", "1200", "0", "0", "1200", "0", "1200", "1200", "0", "0"],
        ["H", "0", "1200", "4900", "0", "0", "0", "0", "40", "0", "5000", "0", "0"],
        ["I", "1200", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
    ]

# !!! our CSV is ; delimited from the plate reader and we have to account for this

def add_parameters(parameters: protocol_api.ParameterContext):
    parameters.add_csv_file(
        variable_name="input_csv",
        display_name="Input parameters (CSV)",
        description="; separated fluorescence CSV results. Layout like in the plate: Columns: . 1 2 3 4 5 6 7 8 9 10 11 12, Rows: . A B C D E F G H I ",
    )

def load_rows(protocol):
    try:
        rows = protocol.params.input_csv.parse_as_csv(delimiter=";")      # https://docs.python.org/3/library/csv.html#csv-fmt-params
    except RuntimeParameterRequiredError:
        protocol.comment("No CSV selected - using built-in test data")
        rows = TEST_CSV
    return rows


def validate(rows, lowest=4):

    # first try except to see what the header reading works like
    try:
        columns = [c.strip() for c in rows[0]]   
        if columns != EXPECTED_HEADER:
            raise ValueError(f"Unexpected header {columns}, expected {EXPECTED_HEADER}")
        errors, parsed = [], []
    except:
        errors, parsed = "Cannot read csv header (perhaps encoding problem).", []

    # second try except to see if my logical code works well (e.g. if the plate reader gives out something like "UNDER" we would fail)
    try:

        phenyl_groundtruth = {"B1": rows[2][1]}

        phenyl_candidates = {"A3": rows[1][3], "A9": rows[1][9], "A10": rows[1][10],
                             "D2": rows[4][2],
                             "G2": rows[7][2],
                             "H3": rows[8][3], "H8": rows[8][8]}

        # e.g. makes from the test the: phenyl_candidates = {'A3': 2500, 'A9': 35, 'A10': 100000, 'D2': 2500, 'G2': 5000, 'H3': 4900, 'H8': 40}
        # then creates from OVER: phenyl_candidates = phenyl_candidates
        # and chooses: ['A9', 'H8', 'A3', 'D2']
    
        
        # choose the wells to pick with lowest fluorescence, to try and optimize/crosstest for tyrosine
        for well, value in phenyl_candidates.items():
            
            if value == "OVER":
                phenyl_candidates[well] = 100000      # add a large number to not use these wells
            else:
                phenyl_candidates[well] = int(value)  # convert the strings to an integer so that sorting works numerically not alphabetically
        
        print(phenyl_candidates)
        
        optimization_picks = sorted(phenyl_candidates, key=phenyl_candidates.get)[:lowest]    # get 4 smallest

    # in case there is any error, we still want to collect some insights
    except:
        optimization_picks = ["A9", "H3", "G2", "G8"]

    return optimization_picks




def run(protocol: protocol_api.ProtocolContext) -> None:

    ######################################
    # random selection: a gambling robot #
    ######################################
    selection = ["B3", "B9", "B10", "C3", "C11", "D3", "E7", "E9", "E11", "F7", "G4", "G7", "H5", "H7", "H9"]
    np.random.seed(2001)
    random_picks = np.random.choice(selection, 6, replace=False)   # pick 6  
    random_picks = [str(well) for well in random_picks]            # Opentron likes strings it seems :)   

    # third try to test if logging works
    try:
        protocol.comment(f"random_picks: {random_picks}")
    except:
        None
    
    ######################################
    # optimization picks                 #
    ######################################
    optimization_picks = validate(load_rows(protocol), lowest=4)    # source = well_plate_1, not here defined yet, picks 4 with lowest phenylalanine fluorescence readout

    # fourth try to test if logging works for optimization picks
    try:
        protocol.comment(f"optimization_picks: {optimization_picks}")
    except:
        None

    # Load Modules:
    heater_shaker_module_1 = protocol.load_module("heaterShakerModuleV1", "10")

    # Load Adapters:
    adapter_1 = heater_shaker_module_1.load_adapter(
        "opentrons_universal_flat_adapter",
        namespace="opentrons",
        version=1,
    )

    # Load Labware:
    reservoir_1 = protocol.load_labware_from_definition(
        CUSTOM_LABWARE["custom_beta/axygen_12_reservoir_12000ul/1"],
        location="1",
    )
    well_plate_1 = protocol.load_labware(
        "corning_falcon_384_wellplate_130ul_flat",
        location="3",
        namespace="opentrons",
        version=1,
    )
    tip_rack_1 = protocol.load_labware(
        "opentrons_96_filtertiprack_20ul",
        location="5",
        namespace="opentrons",
        version=1,
    )
    well_plate_2 = protocol.load_labware(
        "corning_falcon_384_wellplate_130ul_flat",
        location="4",
        namespace="opentrons",
        version=1,
    )

    # Load Pipettes:
    pipette_left = protocol.load_instrument("p20_single_gen2", "left")

    # Define Liquids:
    liquid_1 = protocol.define_liquid(
        "+control",
        description="all 20 amino acids in 10 ml (100 µM)",
        display_color="#ffa7a7ff",
    )
    liquid_2 = protocol.define_liquid(
        "-F",
        description="only 19 amino acids in 10 ml without phenylalanine (95 µM)",
        display_color="#6bd8efff",
    )
    liquid_3 = protocol.define_liquid(
        "-H",
        description="only 19 amino acids in 10 ml without histidine (95 µM)",
        display_color="#d29dffff",
    )
    liquid_4 = protocol.define_liquid(
        "-I",
        description="only 19 amino acids in 10 ml without isoleucine (95 µM)",
        display_color="#ffd600ff",
    )
    liquid_5 = protocol.define_liquid(
        "-W",
        description="only 19 amino acids in 10 ml without tryptophan (95 µM)",
        display_color="#276c30ff",
    )
    liquid_6 = protocol.define_liquid(
        "-Y",
        description="only 19 amino acids in 10 ml without tyrosine (95 µM)",
        display_color="#ffb380ff",
    )
    liquid_7 = protocol.define_liquid(
        "in-vitro MM",
        description="In-vitro translation master mix (40x MM: 275 µl, 10x MM: 71 µl)",
        display_color="#ff4f4fff",
    )
    liquid_8 = protocol.define_liquid(
        "aa-A11",
        display_color="#eedaf8ff",
    )
    liquid_9 = protocol.define_liquid(
        "aa-C8",
        display_color="#eedaf8ff",
    )
    liquid_10 = protocol.define_liquid(
        "aa-E6",
        display_color="#eedaf8ff",
    )
    liquid_11 = protocol.define_liquid(
        "aa-G6",
        display_color="#eedaf8ff",
    )
    liquid_12 = protocol.define_liquid(
        "aa-A2",
        display_color="#f9d5b4ff",
    )
    liquid_13 = protocol.define_liquid(
        "aa-B5",
        display_color="#f9d5b4ff",
    )
    liquid_14 = protocol.define_liquid(
        "aa-D6",
        display_color="#f9d5b4ff",
    )
    liquid_15 = protocol.define_liquid(
        "aa-F10",
        display_color="#f9d5b4ff",
    )
    liquid_16 = protocol.define_liquid(
        "aa-C6",
        display_color="#99b59cff",
    )
    liquid_17 = protocol.define_liquid(
        "aa-C9",
        display_color="#99b59cff",
    )
    liquid_18 = protocol.define_liquid(
        "aa-D11",
        display_color="#99b59cff",
    )
    liquid_19 = protocol.define_liquid(
        "aa-E4",
        display_color="#99b59cff",
    )
    liquid_20 = protocol.define_liquid(
        "aa-F4",
        display_color="#99b59cff",
    )
    liquid_21 = protocol.define_liquid(
        "aa-H10",
        display_color="#99b59cff",
    )
    liquid_22 = protocol.define_liquid(
        "aa-A3",
        display_color="#b2f4f2ff",
    )
    liquid_23 = protocol.define_liquid(
        "aa-A9",
        display_color="#b2f4f2ff",
    )
    liquid_24 = protocol.define_liquid(
        "aa-A10",
        display_color="#b2f4f2ff",
    )
    liquid_25 = protocol.define_liquid(
        "aa-D2",
        display_color="#b2f4f2ff",
    )
    liquid_26 = protocol.define_liquid(
        "aa-G2",
        display_color="#b2f4f2ff",
    )
    liquid_27 = protocol.define_liquid(
        "aa-H3",
        display_color="#b2f4f2ff",
    )
    liquid_28 = protocol.define_liquid(
        "aa-H8",
        display_color="#b2f4f2ff",
    )
    liquid_29 = protocol.define_liquid(
        "aa-A5",
        display_color="#e0d7a7ff",
    )
    liquid_30 = protocol.define_liquid(
        "aa-B4",
        display_color="#e0d7a7ff",
    )
    liquid_31 = protocol.define_liquid(
        "aa-C2",
        display_color="#e0d7a7ff",
    )
    liquid_32 = protocol.define_liquid(
        "aa-F8",
        display_color="#e0d7a7ff",
    )
    liquid_33 = protocol.define_liquid(
        "aa-G3",
        display_color="#e0d7a7ff",
    )
    liquid_34 = protocol.define_liquid(
        "aa-G9",
        display_color="#e0d7a7ff",
    )
    liquid_35 = protocol.define_liquid(
        "aa-G10",
        display_color="#e0d7a7ff",
    )
    liquid_36 = protocol.define_liquid(
        "aa-B6",
        display_color="#5d8261ff",
    )
    liquid_37 = protocol.define_liquid(
        "aa-D9",
        display_color="#5d8261ff",
    )
    liquid_38 = protocol.define_liquid(
        "aa-C10",
        display_color="#de9555ff",
    )
    liquid_39 = protocol.define_liquid(
        "aa-H2",
        display_color="#de9555ff",
    )
    liquid_40 = protocol.define_liquid(
        "aa-I1",
        display_color="#aea15dff",
    )
    liquid_41 = protocol.define_liquid(
        "aa-A6",
        display_color="#aea15dff",
    )
    liquid_42 = protocol.define_liquid(
        "MilliQ water",
        display_color="#0019ffff",
    )
    liquid_43 = protocol.define_liquid(
        "aa-B3",
        display_color="#4c8482ff",
    )
    liquid_44 = protocol.define_liquid(
        "aa-B9",
        display_color="#4c8482ff",
    )
    liquid_45 = protocol.define_liquid(
        "aa-B10",
        display_color="#4c8482ff",
    )
    liquid_46 = protocol.define_liquid(
        "aa-C3",
        display_color="#4c8482ff",
    )
    liquid_47 = protocol.define_liquid(
        "aa-C11",
        display_color="#4c8482ff",
    )
    liquid_48 = protocol.define_liquid(
        "aa-D3",
        display_color="#4c8482ff",
    )
    liquid_49 = protocol.define_liquid(
        "aa-E7",
        display_color="#4c8482ff",
    )
    liquid_50 = protocol.define_liquid(
        "aa-E9",
        display_color="#4c8482ff",
    )
    liquid_51 = protocol.define_liquid(
        "aa-E11",
        display_color="#4c8482ff",
    )
    liquid_52 = protocol.define_liquid(
        "aa-H5",
        display_color="#4c8482ff",
    )
    liquid_53 = protocol.define_liquid(
        "aa-H7",
        display_color="#4c8482ff",
    )
    liquid_54 = protocol.define_liquid(
        "aa-H9",
        display_color="#4c8482ff",
    )
    liquid_55 = protocol.define_liquid(
        "aa-F7",
        display_color="#4c8482ff",
    )
    liquid_56 = protocol.define_liquid(
        "aa-G4",
        display_color="#4c8482ff",
    )
    liquid_57 = protocol.define_liquid(
        "aa-G7",
        display_color="#4c8482ff",
    )

    # Load Liquids:
    reservoir_1.load_liquid(
        wells=["A1"],
        liquid=liquid_1,
        volume=10000,
    )
    reservoir_1.load_liquid(
        wells=["A2"],
        liquid=liquid_2,
        volume=10000,
    )
    reservoir_1.load_liquid(
        wells=["A3"],
        liquid=liquid_3,
        volume=10000,
    )
    reservoir_1.load_liquid(
        wells=["A4"],
        liquid=liquid_4,
        volume=10000,
    )
    reservoir_1.load_liquid(
        wells=["A5"],
        liquid=liquid_5,
        volume=10000,
    )
    reservoir_1.load_liquid(
        wells=["A6"],
        liquid=liquid_6,
        volume=10000,
    )
    reservoir_1.load_liquid(
        wells=["A7"],
        liquid=liquid_42,
        volume=10000,
    )
    well_plate_1.load_liquid(
        wells=["A3"],
        liquid=liquid_22,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["A9"],
        liquid=liquid_23,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["A10"],
        liquid=liquid_24,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["D2"],
        liquid=liquid_25,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["H3"],
        liquid=liquid_27,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["H8"],
        liquid=liquid_28,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["G2"],
        liquid=liquid_26,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["C3"],
        liquid=liquid_46,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["B3"],
        liquid=liquid_43,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["B9"],
        liquid=liquid_44,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["B10"],
        liquid=liquid_45,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["C11"],
        liquid=liquid_47,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["D3"],
        liquid=liquid_48,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["E7"],
        liquid=liquid_49,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["E9"],
        liquid=liquid_50,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["E11"],
        liquid=liquid_51,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["H5"],
        liquid=liquid_52,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["H7"],
        liquid=liquid_53,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["H9"],
        liquid=liquid_54,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["F7"],
        liquid=liquid_55,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["G4"],
        liquid=liquid_56,
        volume=30,
    )
    well_plate_1.load_liquid(
        wells=["G7"],
        liquid=liquid_57,
        volume=30,
    )
    well_plate_2.load_liquid(
        wells=[
            "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8",
            "A9", "A10"
        ],
        liquid=liquid_7,
        volume=7,
    )

    # PROTOCOL STEPS

    # Step 1: transfer
    pipette_left.transfer_with_liquid_class(
        volume=7,
        source=[reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"], reservoir_1["A6"]],
        dest=[well_plate_2["A1"], well_plate_2["A2"], well_plate_2["A3"], well_plate_2["A4"], well_plate_2["A5"], well_plate_2["A6"], well_plate_2["A7"], well_plate_2["A8"], well_plate_2["A9"], well_plate_2["A10"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_1",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 0)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 2: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[random_picks[0]]],  # add first random choice
        dest=[well_plate_2["A1"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_2",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 3: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[random_picks[1]]],  # second choice
        dest=[well_plate_2["A2"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_3",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 4: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[random_picks[2]]],  # third choice
        dest=[well_plate_2["A3"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_4",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 5: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[random_picks[3]]],     # fourth choice 
        dest=[well_plate_2["A4"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_5",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 6: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[random_picks[4]]],    # fifth choice
        dest=[well_plate_2["A5"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_6",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 7: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[random_picks[5]]],     # sixth choice
        dest=[well_plate_2["A6"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_7",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 8: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[optimization_picks[0]]],
        dest=[well_plate_2["A7"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_8",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 9: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[optimization_picks[1]]],
        dest=[well_plate_2["A8"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_9",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 10: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[optimization_picks[2]]],
        dest=[well_plate_2["A9"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_10",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 11: transfer
    pipette_left.transfer_with_liquid_class(
        volume=2,
        source=[well_plate_1[optimization_picks[3]]],
        dest=[well_plate_2["A10"]],
        new_tip="always",
        trash_location=protocol.fixed_trash,
        keep_last_tip=True,
        tip_racks=[tip_rack_1],
        liquid_class=protocol.define_liquid_class(
            name="transfer_step_11",
            properties={"p20_single_gen2": {"opentrons/opentrons_96_filtertiprack_20ul/1": {
                "aspirate": {
                    "aspirate_position": {
                        "offset": {"x": 0, "y": 0, "z": 2},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "pre_wet": False,
                    "correction_by_volume": [(0, 0)],
                    "delay": {"enabled": False},
                    "mix": {"enabled": True, "repetitions": 2, "volume": 5},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                    },
                },
                "dispense": {
                    "dispense_position": {
                        "offset": {"x": 0, "y": 0, "z": 1.5},
                        "position_reference": "well-bottom",
                    },
                    "flow_rate_by_volume": [(0, 3.7)],
                    "delay": {"enabled": False},
                    "submerge": {
                        "delay": {"enabled": False},
                        "speed": 125,
                        "start_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                    },
                    "retract": {
                        "air_gap_by_volume": [(0, 0)],
                        "delay": {"enabled": False},
                        "end_position": {
                            "offset": {"x": 0, "y": 0, "z": 2},
                            "position_reference": "well-top",
                        },
                        "speed": 125,
                        "touch_tip": {"enabled": False},
                        "blowout": {"enabled": False},
                    },
                    "correction_by_volume": [(0, 0)],
                    "push_out_by_volume": [(0, 1)],
                    "mix": {"enabled": False},
                },
            }}},
        ),
    )
    pipette_left.drop_tip()

    # Step 12: Heater-Shaker
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.open_labware_latch()

    # Step 13: move
    protocol.move_labware(well_plate_2, adapter_1)

    # Step 14: Heater-Shaker
    heater_shaker_module_1.close_labware_latch()
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.set_and_wait_for_shake_speed(250)
    protocol.delay(seconds=60)
    heater_shaker_module_1.deactivate_shaker()
    heater_shaker_module_1.deactivate_heater()

    # Step 15: Open Heater-Shaker
    heater_shaker_module_1.set_target_temperature(37)
    heater_shaker_module_1.wait_for_temperature()
    protocol.delay(seconds=120)
    heater_shaker_module_1.deactivate_shaker()
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.open_labware_latch()

    # Step 16: pause
    protocol.pause("PAUSE 0 h: Measure the 0 h fluorescence on the 384 black well plate.\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.")

    # Step 17: Heater-Shaker
    heater_shaker_module_1.close_labware_latch()
    heater_shaker_module_1.set_target_temperature(37)
    heater_shaker_module_1.wait_for_temperature()
    protocol.delay(seconds=3600)
    heater_shaker_module_1.deactivate_shaker()
    heater_shaker_module_1.deactivate_heater()

    # Step 18: Open Heater-Shaker
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.open_labware_latch()

    # Step 19: pause
    protocol.pause("1 h PAUSE: Measure the 1 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.")

    # Step 20: Heater-Shaker
    heater_shaker_module_1.close_labware_latch()
    heater_shaker_module_1.set_target_temperature(37)
    heater_shaker_module_1.set_and_wait_for_shake_speed(200)
    heater_shaker_module_1.wait_for_temperature()
    protocol.delay(seconds=3600)
    heater_shaker_module_1.deactivate_shaker()
    heater_shaker_module_1.deactivate_heater()

    # Step 21: Open Heater-Shaker
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.open_labware_latch()

    # Step 22: pause
    protocol.pause("PAUSE 2 h: Measure the 2 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.")

    # Step 23: Heater-Shaker
    heater_shaker_module_1.close_labware_latch()
    heater_shaker_module_1.set_target_temperature(37)
    heater_shaker_module_1.wait_for_temperature()
    protocol.delay(seconds=3600)
    heater_shaker_module_1.deactivate_shaker()
    heater_shaker_module_1.deactivate_heater()

    # Step 24: Open Heater-Shaker
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.open_labware_latch()

    # Step 25: pause
    protocol.pause("3 h PAUSE: Measure the 3 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.")

    # Step 26: Heater-Shaker
    heater_shaker_module_1.close_labware_latch()
    heater_shaker_module_1.set_target_temperature(37)
    heater_shaker_module_1.set_and_wait_for_shake_speed(200)
    heater_shaker_module_1.wait_for_temperature()
    protocol.delay(seconds=3600)
    heater_shaker_module_1.deactivate_shaker()
    heater_shaker_module_1.deactivate_heater()

    # Step 27: Open Heater-Shaker
    heater_shaker_module_1.deactivate_heater()
    heater_shaker_module_1.open_labware_latch()

    # Step 28: pause
    protocol.pause("END :) Now at 4 h: Measure the 4 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and please STORE IT at -20°C.\n\nPlease place the amino acid solutions in a 4°C fridge.\n\nThis is it :)")

CUSTOM_LABWARE = json.loads("""{"custom_beta/axygen_12_reservoir_12000ul/1":{"ordering":[["A1"],["A2"],["A3"],["A4"],["A5"],["A6"],["A7"],["A8"],["A9"],["A10"],["A11"],["A12"]],"brand":{"brand":"Axygen","brandId":["12 Res 12mL V-shape HighProfile"]},"metadata":{"displayName":"Axygen 12 Reservoir 12000 µL","displayCategory":"reservoir","displayVolumeUnits":"µL","tags":[]},"dimensions":{"xDimension":127.7,"yDimension":85.4,"zDimension":44},"wells":{"A1":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":14.5,"y":42.7,"z":5.1},"A2":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":23.5,"y":42.7,"z":5.1},"A3":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":32.5,"y":42.7,"z":5.1},"A4":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":41.5,"y":42.7,"z":5.1},"A5":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":50.5,"y":42.7,"z":5.1},"A6":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":59.5,"y":42.7,"z":5.1},"A7":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":68.5,"y":42.7,"z":5.1},"A8":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":77.5,"y":42.7,"z":5.1},"A9":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":86.5,"y":42.7,"z":5.1},"A10":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":95.5,"y":42.7,"z":5.1},"A11":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":104.5,"y":42.7,"z":5.1},"A12":{"depth":38.9,"totalLiquidVolume":12000,"shape":"rectangular","xDimension":8,"yDimension":71,"x":113.5,"y":42.7,"z":5.1}},"groups":[{"metadata":{"wellBottomShape":"v"},"wells":["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12"]}],"parameters":{"format":"irregular","quirks":["centerMultichannelOnWells","touchTipDisabled"],"isTiprack":false,"isMagneticModuleCompatible":false,"loadName":"axygen_12_reservoir_12000ul"},"namespace":"custom_beta","version":1,"schemaVersion":2,"cornerOffsetFromSlot":{"x":0,"y":0,"z":0},"stackingOffsetWithLabware":{"opentrons_universal_flat_adapter":{"x":0,"y":0,"z":9.1}}}}""")

DESIGNER_APPLICATION = """{"robot":{"model":"OT-2 Standard"},"designerApplication":{"name":"opentrons/protocol-designer","version":"2606.0.0","data":{"pipetteTiprackAssignments":{"db47980c-6f43-4f51-a8de-7d26dae59bce":["opentrons/opentrons_96_filtertiprack_10ul/1","opentrons/opentrons_96_filtertiprack_20ul/1"]},"dismissedWarnings":{"form":[],"timeline":[]},"ingredients":{"0":{"displayName":"+control","displayColor":"#ffa7a7ff","description":"all 20 amino acids in 10 ml (100 µM)","liquidGroupId":"0"},"1":{"displayName":"-F","displayColor":"#6bd8efff","description":"only 19 amino acids in 10 ml without phenylalanine (95 µM)","liquidGroupId":"1"},"2":{"displayName":"-H","displayColor":"#d29dffff","description":"only 19 amino acids in 10 ml without histidine (95 µM)","liquidGroupId":"2"},"3":{"displayName":"-I","displayColor":"#ffd600ff","description":"only 19 amino acids in 10 ml without isoleucine (95 µM)","liquidGroupId":"3"},"4":{"displayName":"-W","displayColor":"#276c30ff","description":"only 19 amino acids in 10 ml without tryptophan (95 µM)","liquidGroupId":"4"},"5":{"displayName":"-Y","displayColor":"#ffb380ff","description":"only 19 amino acids in 10 ml without tyrosine (95 µM)","liquidGroupId":"5"},"6":{"displayName":"in-vitro MM","displayColor":"#ff4f4fff","description":"In-vitro translation master mix (40x MM: 275 µl, 10x MM: 71 µl)","liquidGroupId":"6"},"7":{"displayName":"aa-A11","displayColor":"#eedaf8ff","description":null,"liquidGroupId":"7"},"8":{"displayName":"aa-C8","displayColor":"#eedaf8ff","description":null,"liquidGroupId":"8"},"9":{"displayName":"aa-E6","displayColor":"#eedaf8ff","description":null,"liquidGroupId":"9"},"10":{"displayName":"aa-G6","displayColor":"#eedaf8ff","description":null,"liquidGroupId":"10"},"11":{"displayName":"aa-A2","displayColor":"#f9d5b4ff","description":null,"liquidGroupId":"11"},"12":{"displayName":"aa-B5","displayColor":"#f9d5b4ff","description":null,"liquidGroupId":"12"},"13":{"displayName":"aa-D6","displayColor":"#f9d5b4ff","description":null,"liquidGroupId":"13"},"14":{"displayName":"aa-F10","displayColor":"#f9d5b4ff","description":null,"liquidGroupId":"14"},"15":{"displayName":"aa-C6","displayColor":"#99b59cff","description":null,"liquidGroupId":"15"},"16":{"displayName":"aa-C9","displayColor":"#99b59cff","description":null,"liquidGroupId":"16"},"17":{"displayName":"aa-D11","displayColor":"#99b59cff","description":null,"liquidGroupId":"17"},"18":{"displayName":"aa-E4","displayColor":"#99b59cff","description":null,"liquidGroupId":"18"},"19":{"displayName":"aa-F4","displayColor":"#99b59cff","description":null,"liquidGroupId":"19"},"20":{"displayName":"aa-H10","displayColor":"#99b59cff","description":null,"liquidGroupId":"20"},"21":{"displayName":"aa-A3","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"21"},"22":{"displayName":"aa-A9","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"22"},"23":{"displayName":"aa-A10","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"23"},"24":{"displayName":"aa-D2","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"24"},"25":{"displayName":"aa-G2","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"25"},"26":{"displayName":"aa-H3","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"26"},"27":{"displayName":"aa-H8","displayColor":"#b2f4f2ff","description":null,"liquidGroupId":"27"},"28":{"displayName":"aa-A5","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"28"},"29":{"displayName":"aa-B4","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"29"},"30":{"displayName":"aa-C2","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"30"},"31":{"displayName":"aa-F8","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"31"},"32":{"displayName":"aa-G3","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"32"},"33":{"displayName":"aa-G9","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"33"},"34":{"displayName":"aa-G10","displayColor":"#e0d7a7ff","description":null,"liquidGroupId":"34"},"35":{"displayName":"aa-B6","displayColor":"#5d8261ff","description":null,"liquidGroupId":"35"},"36":{"displayName":"aa-D9","displayColor":"#5d8261ff","description":null,"liquidGroupId":"36"},"37":{"displayName":"aa-C10","displayColor":"#de9555ff","description":null,"liquidGroupId":"37"},"38":{"displayName":"aa-H2","displayColor":"#de9555ff","description":null,"liquidGroupId":"38"},"39":{"displayName":"aa-I1","displayColor":"#aea15dff","description":null,"liquidGroupId":"39"},"40":{"displayName":"aa-A6","displayColor":"#aea15dff","description":null,"liquidGroupId":"40"},"41":{"displayName":"MilliQ water","displayColor":"#0019ffff","description":null,"liquidGroupId":"41"},"42":{"displayName":"aa-B3","displayColor":"#4c8482ff","description":null,"liquidGroupId":"42"},"43":{"displayName":"aa-B9","displayColor":"#4c8482ff","description":null,"liquidGroupId":"43"},"44":{"displayName":"aa-B10","displayColor":"#4c8482ff","description":null,"liquidGroupId":"44"},"45":{"displayName":"aa-C3","displayColor":"#4c8482ff","description":null,"liquidGroupId":"45"},"46":{"displayName":"aa-C11","displayColor":"#4c8482ff","description":null,"liquidGroupId":"46"},"47":{"displayName":"aa-D3","displayColor":"#4c8482ff","description":null,"liquidGroupId":"47"},"48":{"displayName":"aa-E7","displayColor":"#4c8482ff","description":null,"liquidGroupId":"48"},"49":{"displayName":"aa-E9","displayColor":"#4c8482ff","description":null,"liquidGroupId":"49"},"50":{"displayName":"aa-E11","displayColor":"#4c8482ff","description":null,"liquidGroupId":"50"},"51":{"displayName":"aa-H5","displayColor":"#4c8482ff","description":null,"liquidGroupId":"51"},"52":{"displayName":"aa-H7","displayColor":"#4c8482ff","description":null,"liquidGroupId":"52"},"53":{"displayName":"aa-H9","displayColor":"#4c8482ff","description":null,"liquidGroupId":"53"},"54":{"displayName":"aa-F7","displayColor":"#4c8482ff","description":null,"liquidGroupId":"54"},"55":{"displayName":"aa-G4","displayColor":"#4c8482ff","description":null,"liquidGroupId":"55"},"56":{"displayName":"aa-G7","displayColor":"#4c8482ff","description":null,"liquidGroupId":"56"}},"ingredLocations":{"d6a2d095-ce8b-4925-b5d0-65ce508c989b:custom_beta/axygen_12_reservoir_12000ul/1":{"A1":{"0":{"volume":10000}},"A2":{"1":{"volume":10000}},"A3":{"2":{"volume":10000}},"A4":{"3":{"volume":10000}},"A5":{"4":{"volume":10000}},"A6":{"5":{"volume":10000}},"A7":{"41":{"volume":10000}}},"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1":{"A3":{"21":{"volume":30}},"A9":{"22":{"volume":30}},"A10":{"23":{"volume":30}},"D2":{"24":{"volume":30}},"H3":{"26":{"volume":30}},"H8":{"27":{"volume":30}},"G2":{"25":{"volume":30}},"C3":{"45":{"volume":30}},"B3":{"42":{"volume":30}},"B9":{"43":{"volume":30}},"B10":{"44":{"volume":30}},"C11":{"46":{"volume":30}},"D3":{"47":{"volume":30}},"E7":{"48":{"volume":30}},"E9":{"49":{"volume":30}},"E11":{"50":{"volume":30}},"H5":{"51":{"volume":30}},"H7":{"52":{"volume":30}},"H9":{"53":{"volume":30}},"F7":{"54":{"volume":30}},"G4":{"55":{"volume":30}},"G7":{"56":{"volume":30}}},"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1":{"A1":{"6":{"volume":7}},"A2":{"6":{"volume":7}},"A3":{"6":{"volume":7}},"A4":{"6":{"volume":7}},"A5":{"6":{"volume":7}},"A6":{"6":{"volume":7}},"A7":{"6":{"volume":7}},"A8":{"6":{"volume":7}},"A9":{"6":{"volume":7}},"A10":{"6":{"volume":7}}}},"savedStepForms":{"__INITIAL_DECK_SETUP_STEP__":{"stepType":"manualIntervention","id":"__INITIAL_DECK_SETUP_STEP__","labwareLocationUpdate":{"d6a2d095-ce8b-4925-b5d0-65ce508c989b:custom_beta/axygen_12_reservoir_12000ul/1":"1","f103c2e1-d9e7-4388-8ce7-7c57bc926f63:opentrons/opentrons_universal_flat_adapter/1":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1":"3","7e8a5013-7124-42ae-9222-e909662e4c2b:opentrons/opentrons_96_filtertiprack_20ul/1":"5","f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1":"4"},"pipetteLocationUpdate":{"db47980c-6f43-4f51-a8de-7d26dae59bce":"left"},"moduleLocationUpdate":{"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType":"10"},"moduleStateUpdate":{},"trashBinLocationUpdate":{"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin":"cutout12"},"wasteChuteLocationUpdate":{},"stagingAreaLocationUpdate":{},"gripperLocationUpdate":{}},"b064106d-1d4b-4124-8008-8c370527ce96":{"moduleId":null,"pauseAction":"untilResume","pauseMessage":"PAUSE 0 h: Measure the 0 h fluorescence on the 384 black well plate.\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.","pauseTemperature":null,"pauseTime":null,"id":"b064106d-1d4b-4124-8008-8c370527ce96","stepType":"pause","stepName":"pause","stepDetails":"","stepNumber":0},"90679852-6db3-449a-b906-e8ee762e89f8":{"labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","newLocation":"f103c2e1-d9e7-4388-8ce7-7c57bc926f63:opentrons/opentrons_universal_flat_adapter/1","useGripper":false,"id":"90679852-6db3-449a-b906-e8ee762e89f8","stepType":"moveLabware","stepName":"move","stepDetails":"","stepNumber":0},"008a7c81-c55d-47f9-aad3-07ec0a73366d":{"heaterShakerSetTimer":null,"heaterShakerTimer":null,"latchOpen":true,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":false,"setShake":null,"targetHeaterShakerTemperature":"","targetSpeed":null,"id":"008a7c81-c55d-47f9-aad3-07ec0a73366d","stepType":"heaterShaker","stepName":"Heater-Shaker","stepDetails":"","stepNumber":0},"96ab75ec-1d64-4b1c-904c-1383ad487770":{"heaterShakerSetTimer":true,"heaterShakerTimer":"00:01:00","latchOpen":false,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":false,"setShake":true,"targetHeaterShakerTemperature":"","targetSpeed":"250","id":"96ab75ec-1d64-4b1c-904c-1383ad487770","stepType":"heaterShaker","stepName":"Heater-Shaker","stepDetails":"","stepNumber":0},"f98bc165-f122-4b58-b722-61df4b8e24cd":{"heaterShakerSetTimer":true,"heaterShakerTimer":"00:02:00","latchOpen":true,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":true,"setShake":null,"targetHeaterShakerTemperature":"37","targetSpeed":null,"id":"f98bc165-f122-4b58-b722-61df4b8e24cd","stepType":"heaterShaker","stepName":"Open Heater-Shaker","stepDetails":"","stepNumber":0},"d0aac356-31b0-4bdc-801a-53da5d1675a7":{"heaterShakerSetTimer":true,"heaterShakerTimer":"01:00:00","latchOpen":false,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":true,"setShake":false,"targetHeaterShakerTemperature":"37","targetSpeed":"","id":"d0aac356-31b0-4bdc-801a-53da5d1675a7","stepType":"heaterShaker","stepName":"Heater-Shaker","stepDetails":"","stepNumber":0},"a83be31b-0eec-47d4-bffc-da05f03ce115":{"moduleId":null,"pauseAction":"untilResume","pauseMessage":"1 h PAUSE: Measure the 1 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.","pauseTemperature":null,"pauseTime":null,"id":"a83be31b-0eec-47d4-bffc-da05f03ce115","stepType":"pause","stepName":"pause","stepDetails":"","stepNumber":0},"1880f9c8-fa3d-42be-a4c5-5d78141f4156":{"heaterShakerSetTimer":true,"heaterShakerTimer":"01:00:00","latchOpen":false,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":true,"setShake":true,"targetHeaterShakerTemperature":"37","targetSpeed":"200","id":"1880f9c8-fa3d-42be-a4c5-5d78141f4156","stepType":"heaterShaker","stepName":"Heater-Shaker","stepDetails":"","stepNumber":0},"3afe3739-225d-41b2-b0bf-55dc4b9e7c2c":{"moduleId":null,"pauseAction":"untilResume","pauseMessage":"PAUSE 2 h: Measure the 2 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.","pauseTemperature":null,"pauseTime":null,"id":"3afe3739-225d-41b2-b0bf-55dc4b9e7c2c","stepType":"pause","stepName":"pause","stepDetails":"","stepNumber":0},"43e2cb7d-1977-4a5f-8505-d63db423b5e1":{"heaterShakerSetTimer":true,"heaterShakerTimer":"01:00:00","latchOpen":false,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":true,"setShake":false,"targetHeaterShakerTemperature":"37","targetSpeed":"","id":"43e2cb7d-1977-4a5f-8505-d63db423b5e1","stepType":"heaterShaker","stepName":"Heater-Shaker","stepDetails":"","stepNumber":0},"1f4c8f48-30a9-4872-a023-d1494ba06946":{"moduleId":null,"pauseAction":"untilResume","pauseMessage":"3 h PAUSE: Measure the 3 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and place it on the heater-shaker.","pauseTemperature":null,"pauseTime":null,"id":"1f4c8f48-30a9-4872-a023-d1494ba06946","stepType":"pause","stepName":"pause","stepDetails":"","stepNumber":0},"44a0d9a4-8723-4b9a-a364-a38fa082de46":{"heaterShakerSetTimer":true,"heaterShakerTimer":"01:00:00","latchOpen":false,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":true,"setShake":true,"targetHeaterShakerTemperature":"37","targetSpeed":"200","id":"44a0d9a4-8723-4b9a-a364-a38fa082de46","stepType":"heaterShaker","stepName":"Heater-Shaker","stepDetails":"","stepNumber":0},"87d433bb-b4ad-4550-97b7-b86ae004201d":{"moduleId":null,"pauseAction":"untilResume","pauseMessage":"END :) Now at 4 h: Measure the 4 h fluorescence on the 384 black well plate (without lid).\n\nPlate a lid on the 384 black well plate and please STORE IT at -20°C.\n\nPlease place the amino acid solutions in a 4°C fridge.\n\nThis is it :)","pauseTemperature":null,"pauseTime":null,"id":"87d433bb-b4ad-4550-97b7-b86ae004201d","stepType":"pause","stepName":"pause","stepDetails":"","stepNumber":0},"e7fb8a97-3f71-440f-87eb-e9469c9fd71d":{"id":"e7fb8a97-3f71-440f-87eb-e9469c9fd71d","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"d6a2d095-ce8b-4925-b5d0-65ce508c989b:custom_beta/axygen_12_reservoir_12000ul/1","aspirate_mix_checkbox":false,"aspirate_mix_times":"","aspirate_mix_volume":null,"aspirate_mmFromBottom":null,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["A6"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":null,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A1","A2","A4","A3","A6","A5","A7","A8","A10","A9"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":false,"pushOut_volume":"0","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"7"},"a0f263d9-15c5-4249-af3c-8c85f7395024":{"id":"a0f263d9-15c5-4249-af3c-8c85f7395024","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["B3","E9"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A1"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"7f0b86a9-2dd3-4a09-9238-d579317b78a1":{"id":"7f0b86a9-2dd3-4a09-9238-d579317b78a1","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["B3"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A3"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"cf2e4755-1f60-4268-b99b-8a51e1c862e7":{"id":"cf2e4755-1f60-4268-b99b-8a51e1c862e7","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["A9"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A4"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"b437c218-f0b9-4199-a53b-845a8d2ce30e":{"id":"b437c218-f0b9-4199-a53b-845a8d2ce30e","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["B9"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A5"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"f7f210d3-82bf-4425-b87d-cec3dd45e14a":{"id":"f7f210d3-82bf-4425-b87d-cec3dd45e14a","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["F7"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A6"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"411dc772-9397-4ccb-9c0a-c3b743b2ba4f":{"id":"411dc772-9397-4ccb-9c0a-c3b743b2ba4f","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["H7"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A7"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"007971f0-ae95-4972-847f-2af3b9a0b990":{"id":"007971f0-ae95-4972-847f-2af3b9a0b990","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["E9"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A8"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"132fc612-ea0d-4f19-a7fb-53ed248802f6":{"id":"132fc612-ea0d-4f19-a7fb-53ed248802f6","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["H9"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A9"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"21cbb838-b409-4fe8-88dd-758c79f5a9c3":{"id":"21cbb838-b409-4fe8-88dd-758c79f5a9c3","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["H3"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A10"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"},"0131b043-30eb-4d3b-920f-04c8dd98b11f":{"id":"0131b043-30eb-4d3b-920f-04c8dd98b11f","stepType":"heaterShaker","stepName":"Open Heater-Shaker","stepDetails":"","stepNumber":0,"heaterShakerSetTimer":null,"heaterShakerTimer":null,"latchOpen":true,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":null,"setShake":null,"targetHeaterShakerTemperature":null,"targetSpeed":null},"6a87fb4f-d926-419e-bda5-3d37c829eab3":{"id":"6a87fb4f-d926-419e-bda5-3d37c829eab3","stepType":"heaterShaker","stepName":"Open Heater-Shaker","stepDetails":"","stepNumber":0,"heaterShakerSetTimer":null,"heaterShakerTimer":null,"latchOpen":true,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":null,"setShake":null,"targetHeaterShakerTemperature":null,"targetSpeed":null},"a9180f8e-85c3-4293-8e49-6b56b17f5bd1":{"id":"a9180f8e-85c3-4293-8e49-6b56b17f5bd1","stepType":"heaterShaker","stepName":"Open Heater-Shaker","stepDetails":"","stepNumber":0,"heaterShakerSetTimer":null,"heaterShakerTimer":null,"latchOpen":true,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":null,"setShake":null,"targetHeaterShakerTemperature":null,"targetSpeed":null},"5103c8aa-49d7-4953-9843-f89134e1bda8":{"id":"5103c8aa-49d7-4953-9843-f89134e1bda8","stepType":"heaterShaker","stepName":"Open Heater-Shaker","stepDetails":"","stepNumber":0,"heaterShakerSetTimer":null,"heaterShakerTimer":null,"latchOpen":true,"moduleId":"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType","setHeaterShakerTemperature":null,"setShake":null,"targetHeaterShakerTemperature":null,"targetSpeed":null},"12d1b381-3ea1-4086-aac3-dfd04d1352f2":{"id":"12d1b381-3ea1-4086-aac3-dfd04d1352f2","stepType":"moveLiquid","stepName":"transfer","stepDetails":"","stepNumber":0,"aspirate_airGap_checkbox":false,"aspirate_airGap_volume":"","aspirate_delay_checkbox":false,"aspirate_delay_seconds":"1","aspirate_flowRate":"3.7","aspirate_labware":"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1","aspirate_mix_checkbox":true,"aspirate_mix_times":"2","aspirate_mix_volume":"5","aspirate_mmFromBottom":2,"aspirate_position_reference":"well-bottom","aspirate_retract_delay_seconds":"0","aspirate_retract_mmFromBottom":2,"aspirate_retract_speed":"125","aspirate_retract_x_position":0,"aspirate_retract_y_position":0,"aspirate_retract_position_reference":"well-top","aspirate_submerge_delay_seconds":"0","aspirate_submerge_speed":"125","aspirate_submerge_mmFromBottom":2,"aspirate_submerge_x_position":0,"aspirate_submerge_y_position":0,"aspirate_submerge_position_reference":"well-top","aspirate_touchTip_checkbox":false,"aspirate_touchTip_mmFromTop":null,"aspirate_touchTip_speed":60,"aspirate_touchTip_mmFromEdge":0,"aspirate_wellOrder_first":"t2b","aspirate_wellOrder_second":"l2r","aspirate_wells_grouped":false,"aspirate_wells":["B3"],"aspirate_x_position":0,"aspirate_y_position":0,"blowout_checkbox":false,"blowout_flowRate":"3.7","blowout_location":null,"blowout_mmFromBottom":null,"blowout_x_position":null,"blowout_y_position":null,"blowout_position_reference":"well-top","changeTip":"always","conditioning_checkbox":false,"conditioning_volume":null,"dispense_airGap_checkbox":false,"dispense_airGap_volume":"","dispense_delay_checkbox":false,"dispense_delay_seconds":"1","dispense_flowRate":"3.7","dispense_labware":"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1","dispense_mix_checkbox":false,"dispense_mix_times":"","dispense_mix_volume":null,"dispense_mmFromBottom":1.5,"dispense_position_reference":"well-bottom","dispense_retract_delay_seconds":"0","dispense_retract_mmFromBottom":2,"dispense_retract_speed":"125","dispense_retract_x_position":0,"dispense_retract_y_position":0,"dispense_retract_position_reference":"well-top","dispense_submerge_delay_seconds":"0","dispense_submerge_speed":"125","dispense_submerge_mmFromBottom":2,"dispense_submerge_x_position":0,"dispense_submerge_y_position":0,"dispense_submerge_position_reference":"well-top","dispense_touchTip_checkbox":false,"dispense_touchTip_mmFromTop":null,"dispense_touchTip_speed":60,"dispense_touchTip_mmFromEdge":0,"dispense_wellOrder_first":"t2b","dispense_wellOrder_second":"l2r","dispense_wells":["A2"],"dispense_x_position":0,"dispense_y_position":0,"disposalVolume_checkbox":true,"disposalVolume_volume":null,"dropTip_location":"19bdf8df-b25f-4f11-976c-d3a252f3e3f5:trashBin","liquidClassesSupported":true,"liquidClass":"none","nozzles":"ALL","path":"single","pipette":"db47980c-6f43-4f51-a8de-7d26dae59bce","preWetTip":false,"primaryNozzle":"A1","pushOut_checkbox":true,"pushOut_volume":"1","tipRack":"opentrons/opentrons_96_filtertiprack_20ul/1","tip_tracking":"automatic","tiprack_selected":null,"tips_selected":[],"volume":"2"}},"orderedStepIds":["e7fb8a97-3f71-440f-87eb-e9469c9fd71d","a0f263d9-15c5-4249-af3c-8c85f7395024","12d1b381-3ea1-4086-aac3-dfd04d1352f2","7f0b86a9-2dd3-4a09-9238-d579317b78a1","cf2e4755-1f60-4268-b99b-8a51e1c862e7","b437c218-f0b9-4199-a53b-845a8d2ce30e","f7f210d3-82bf-4425-b87d-cec3dd45e14a","411dc772-9397-4ccb-9c0a-c3b743b2ba4f","007971f0-ae95-4972-847f-2af3b9a0b990","132fc612-ea0d-4f19-a7fb-53ed248802f6","21cbb838-b409-4fe8-88dd-758c79f5a9c3","008a7c81-c55d-47f9-aad3-07ec0a73366d","90679852-6db3-449a-b906-e8ee762e89f8","96ab75ec-1d64-4b1c-904c-1383ad487770","f98bc165-f122-4b58-b722-61df4b8e24cd","b064106d-1d4b-4124-8008-8c370527ce96","d0aac356-31b0-4bdc-801a-53da5d1675a7","0131b043-30eb-4d3b-920f-04c8dd98b11f","a83be31b-0eec-47d4-bffc-da05f03ce115","1880f9c8-fa3d-42be-a4c5-5d78141f4156","6a87fb4f-d926-419e-bda5-3d37c829eab3","3afe3739-225d-41b2-b0bf-55dc4b9e7c2c","43e2cb7d-1977-4a5f-8505-d63db423b5e1","a9180f8e-85c3-4293-8e49-6b56b17f5bd1","1f4c8f48-30a9-4872-a023-d1494ba06946","44a0d9a4-8723-4b9a-a364-a38fa082de46","5103c8aa-49d7-4953-9843-f89134e1bda8","87d433bb-b4ad-4550-97b7-b86ae004201d"],"pipettes":{"db47980c-6f43-4f51-a8de-7d26dae59bce":{"pipetteName":"p20_single_gen2"}},"modules":{"53f93402-0a64-42fa-b99f-5654eafe4ef5:heaterShakerModuleType":{"model":"heaterShakerModuleV1"}},"labware":{"d6a2d095-ce8b-4925-b5d0-65ce508c989b:custom_beta/axygen_12_reservoir_12000ul/1":{"displayName":"Axygen 12 Reservoir 12000 µL","labwareDefURI":"custom_beta/axygen_12_reservoir_12000ul/1"},"f103c2e1-d9e7-4388-8ce7-7c57bc926f63:opentrons/opentrons_universal_flat_adapter/1":{"displayName":"Opentrons Universal Flat Heater-Shaker Adapter","labwareDefURI":"opentrons/opentrons_universal_flat_adapter/1"},"f2d0477a-dc4d-4325-a1b6-ef438f66f723:opentrons/corning_falcon_384_wellplate_130ul_flat/1":{"displayName":"Corning Falcon 384 Well Microtest Plate 130 µL","labwareDefURI":"opentrons/corning_falcon_384_wellplate_130ul_flat/1"},"7e8a5013-7124-42ae-9222-e909662e4c2b:opentrons/opentrons_96_filtertiprack_20ul/1":{"displayName":"Opentrons OT-2 96 Filter Tip Rack 20 µL","labwareDefURI":"opentrons/opentrons_96_filtertiprack_20ul/1"},"f2b446ea-e226-40db-bfdb-69032baecf94:opentrons/corning_falcon_384_wellplate_130ul_flat/1":{"displayName":"Corning Falcon 384 Well Microtest Plate 130 µL","labwareDefURI":"opentrons/corning_falcon_384_wellplate_130ul_flat/1"}}}},"metadata":{"protocolName":"self-driving-aas PROTOCOL 2","author":"Waldherr A., Max Planck Institute for Biology","description":"This protocol 2 and was created during the UZH + EPFL self-driving lab hackathon 2026 and investigates how well non-standard amino acids can be incorporated into proteins using an in-vitro translation system and an IF1-mNeonGreen fluorescent readout (EXC: 440 nm, EM: 500 nm).\n","source":"Protocol Designer","created":1792651304599,"lastModified":1792668657242}}"""
