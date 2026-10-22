# Setup of the protocols submitted prior to the hackathon

## Tests in the meeting
- [ ] Go to [ot2.designer.opentrons.com]
- [ ] Start a new **OT2** protocol.
  - [ ] Select 0.5-10 µl pipet (= small volumes). Note: This is _GEN2_.
  - [ ] Select 20 µl pipet (= complete reaction). Note: This is _GEN2_.
  - [ ] Add a heater-shaker module. Note: This is _GEN1_.
- [ ] Save the new protocol as _in-vitro-nc-amino-acids_.

**Refine the protocol**
- [ ] Deck hardware: Click on the _heater shaker_ and set to **10**.
  - [ ] Add a _Opentrons Universal Flat Heater-Shaker Adapter_. Note: Click on pos. **10** to get it.
  - [ ] Add a _Opentrons 10 Tube Rack with Falcon 4x50 mL, 6x15 mL Conical_.
  - [ ] **Option A (tRNA + ncAAs):** Add 2x 96-well 200 µl plates (for 2x duplicates on reactions).
  - [ ] **Option B (tRNA or ncAAs 3x):** Add 3x 96-well 200 µl plates (for 3x triplicates on reactions).
  - [ ] **Option C (1x tRNA, 3x repeat):** Add 1-2x 96-well 200 µl plates, **readout**, optimize replicas depending on readout.
  - Optional: Add custom labware (not needed as Axygen, Sarstedt, VWR all >200 µl).
  - **NOTE: ADD LIDS FOR 37° INCUBATION BUT MAKE SURE TO REMOVE THOSE LATER.**
- [ ] Liquids: Add liquids.
  - [ ] L.A) reservoir for Sol. A
  - [ ] L.B) reservoir for 3.75 µl Sol. B
  - [ ] L.C) reservoir for water
  - [ ] L.D) reservoir for 100 ng/µl plasmid
  - [ ] (reservoir for 1.25 µl tRNA) => all 21x tRNAs
  - [ ] (reservoir for 1.25 µl +aa) => all 20x amino acids
  - [ ] (reservoir for ncAAs) => one spot for the ncAA / one plate for the ncAAs
- [ ] Add the liquids: Click on the _Tube Rack_ $\rightarrow$ add liquid $\rightarrow$ define volumes.

**Add the steps**
- [ ] Click on _Starting Deck_ (left bottom) and _+ Add Step_. **PAUSE** Remove all lids.
  - [ ] Add pipetting steps for all of the IVT-components.
  - [ ] Add pipetting steps for the unique amino acid / tRNA mixtures (pre-mixtures).
  - [ ] Add pipetting steps for the single component of interest.
  - [ ] Add transfer to heater-shaker. **PAUSE** Add lid.
  - [ ] Add heater-shaker @37°C for 4 h. **PAUSE** Remove lid.
  - [ ] Fluorescence readout.
- [ ] Click on _End Deck_ (left bottom).
- [ ] Look at all the final mixtures.

**Manual protocol**
- [ ] **Export protocol = Python code.**
- [ ] Optional: Optimize the run of the code.
  - [ ] `add_parameters` $\rightarrow$ `load_rows` $\rightarrow$ `validate` $\rightarrow$ `run`
  - [ ] `run` modify by destination and source and save in list and iterate over list
  - [ ] `source, destination` could be iterative variables as well
  - [ ] old legacy: instead of _liquid_ class there is an _aspiration_ class
- [ ] Note: Use `RuntimeParameter`.
- [ ] Note: The _.csv_ will be supplied by the plate reader.

## Real protocol-1 constructed
- [X] Add the custom reservoirs.
- [X] Add the heater-shaker adapters.
- [?] Add the custom 384-well plate (_Note:_ This was not possible due to the heater-shaker adapter so I am using the 384-well Corning Falcon 384 Well Microtest Plate 130 µL as alternative.) This includes the amino acid mixtures and water for the controls. 


## Real protocol-2 constructed
- [X] Add the custom reservoirs and the pre-pipetted 384-well plate with A1-A10.
- [X] Delete the other plates.
- [X] Add -Tyr amino acid (19 aa) to each well.

#### Part of protocol-2: Gambling robot
- [X] Add the **random choices** of amino acids in the **A1-A6**. This I did with `numpy` to make a **gambling robot** that not only pipets for me, but also chooses for me. :)
  - [X] `selection = ["B3", "B9", "B10", "C3", "C11", "D3", "E7", "E9", "E11", "F7", "G4", "G7", "H5", "H7", "H9"]`
  - [X] `random_picks = np.random.choice(selection, 6, replace=False)   # pick 6`
  - [X] `random_picks = [str(well) for well in random_picks]            # Opentron likes strings it seems :)`
  - [X] And then in the different transfers: `source=[well_plate_1[random_picks[i]]],`

#### Part of protocol-2: Automatic iteration / optimization with a ";" .csv file
- [X] Add the **optimization choices** with the help/trouble of the custom plate reader _.csv_ file.
  - [X] NOTE! This is ";" delimited, so I adapted to `rows = protocol.params.input_csv.parse_as_csv(delimiter=";")`.
  - [X] NOTE! When I read in the _.csv_ file from the plate reader with Python, the first cell is not "<>" but "'ï»¿<>'". So we adjust the _EXPECTED_HEADER_ for that. 
  - [X] NOTE! We have to remove "OVER" if plate reader logs errors and convert them into large numbers.

These are the functions as unit tests:

`with open("3 - fluorescenceReadout modified.csv", newline="\n") as file:
    fluorescence_reader = csv.reader(file, delimiter=";")
    rows = [row for row in fluorescence_reader]`

`validate(rows)`

with the function:

`def validate(rows, num=4):

    # e.g. makes from the test the: phenyl_candidates = {'A3': '2500', 'A9': '35', 'A10': 'OVER', 'D2': '0', 'G2': '1200', 'G8': '40'}
    # then creates from OVER: phenyl_candidates = phenyl_candidates
    # and chooses: ['D2', 'A9', 'G8', 'G2']
    
    try:
        # get the values of the phenylalanine only 19 aa control in the csv
        phenyl_groundtruth = {"B1": rows[2][1]}
    
        # get the values of the phenylalanine candidates in the csv
        phenyl_candidates = {"A3": rows[1][3], "A9": rows[1][9], "A10": rows[1][10],
                             "D2": rows[5][2],
                             "G2": rows[8][2], "G8": rows[8][8]}
    
        
        # choose the wells to pick with lowest fluorescence, to try and optimize/crosstest for tyrosine
        for well, value in phenyl_candidates.items():
            
            if value == "OVER":
                phenyl_candidates[well] = 100000      # add a large number to not use these wells
            else:
                phenyl_candidates[well] = int(value)  # convert the strings to an integer so that sorting works numerically not alphabetically
        
        print(phenyl_candidates)
        
        optimization_picks = sorted(phenyl_candidates, key=phenyl_candidates.get)[:num]    # get 4 smallest

    # in case there is any error, we still want to collect some insights
    except:
        optimization_picks = ["A9", "H3", "G2", "G8"]

    return optimization_picks`

**Run the protocol on the simulation apps**
- [ ] Download the protocol.
- [ ] Create a `conda` environment: `conda create --name self-driving-aas_env --clone base`
- [ ] `conda activate self-driving-aas_env`

## Done/To bring
- [ ] get the 20 standard amino acids as solutions from Tübingen
- [ ] get the sfGFP plasmid from Tübingen with RNAse Inhibitor (NEB Murine) inside
- [X] get the amino acid layout of the library and prepare everything accordingly, figures
- [X] prepare ivtRNAs and lyophilized them in Tübingen
