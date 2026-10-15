# Setup of the protocols submitted prior to the hackathon

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

**Run the protocol on the simulation apps**
- [ ] Download the protocol.

## TODO
- [ ] get the 20 standard amino acids as solutions from Tübingen
- [ ] get the sfGFP plasmid from Tübingen with RNAse Inhibitor (NEB Murine) inside
- [ ] get the amino acid layout of the library
- [ ] ? prepare ivtRNAs and lyophilized them in Tübingen
