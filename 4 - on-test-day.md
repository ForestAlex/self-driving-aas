# 4 - On test day

### 1) A master mix of the _in-vitro_ translation kit

Prepare a 40x MM (= master mix) of the _in-vitro_ translation components **on ice**. This is then supplied to the robot (as the last thing, keep it cold as long as possible):

**40x MM**
- [ ] 120 µl Sol. B
- [ ] 80 µl Sol. A
- [ ] 40 µl tRNAs
- [ ] NO AMINO ACID MIX
- [ ] 40 µl plasmid
- [ ] 5 µl RNAse inhibitor
---------------------------
total: 285 µl 

Per reaction this will be **7.125 µl** to pipet (we will tell the robot to pipet 7 µl to have buffer).

### 2) "Knockout" amino acid solutions

From the 100 mM solutions of canonical amino acids prepare in 15 ml falcons (this should give always 10 ml total). These are then supplied to the robot:

Note: The water please has to be MilliQ water or sterile.

- [ ] **+ control:** 0.5 ml of A, C, D, E, F, G, **H**, **I**, K, L, M, N, P, Q, R, S, T, V, **W**, **Y**
- [ ] **-His (H solution):** 0.5 ml of A, C, D, E, F, G, **water**, **I**, K, L, M, N, P, Q, R, S, T, V, **W**, **Y**
- [ ] **-Ile (I solution):** 0.5 ml of A, C, D, E, F, G, **H**, **water**, K, L, M, N, P, Q, R, S, T, V, **W**, **Y**
- [ ] **-Trp (W solution):** 0.5 ml of A, C, D, E, F, G, **H**, **I**, K, L, M, N, P, Q, R, S, T, V, **water**, **Y**
- [ ] **-Tyr (Y solution):** 0.5 ml of A, C, D, E, F, G, **H**, **I**, K, L, M, N, P, Q, R, S, T, V, **W**, **water**

Note: We add 1 µl of 100 mM amino acid mix to each reaction typically (= per amino acid 5 mM). For the experiments we add the non-standard amino acid in 5x excess due to typically lower incorporation rates. A 25 mM solution is often well soluble with slight acidic conditions and ultrasound.

### 3) Amino acids

The amino acid solutions are dissolved at 25 mM solutions (see Excel). A set of 40 is supplied to the robot in the 96-well plate which was prepared on the day before during the dissolution.

### 4) Robot pipetting: Round 1

The robot pipets the following:

Into a black 384-well plate:

- [X] 1 positive control: **1 µl +aa control** + **2 µl MilliQ water** + *7 µl MM*
- [X] 5 negative controls: **1 µl -aa (only 19 aa solution)** + **2 µl MilliQ water** + *7 µl MM*
- [X] 34 amino acid reactions:
  - [X] 4x histidine derivatives (A11, C8, E6, G6)
  - [X] 4x tyrosine derivatives (A2, B5, D6, _F10_) 
  - [X] 6x tryptophan derivatives (C6, C9, E4, F4, H10)
  - [X] 7x phenylalanine derivatives (**1xF:** A10/D2 **2xF**: A3/H8)
    - [X] of which are similar to tyrosine: A9, H3
    - [X] of which are hydrophobic: G2 
  - [X] 7x isoleucine derivatives (phenylglycine form: **F8**, A5, B4, C2, G3, **G9**)  
  - [X] 2x harder tryptophan derivatives (B6, D9)
  - [X] 2x harder tyrosine derivates (C10, H2)
  - [X] 2x harder isoleucine derivates (A2.2, A6) _Note: A2.2 means that it came from the second plate._
     
It should pipet for each:  **1 µl RESPECTIVE -aa (only 19 aa solution)** + **2 µl MilliQ water** + *7 µl MM*

Then the experiment begins with platereader observations: 
- [X] The robot puts onto heater-shaker and 37°C.
- [ ] 0 h PAUSE: Add lid. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 1 h PAUSE: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 2 h PAUSE: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 3 h PAUSE: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 4 h FINAL: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. **Put plate to 4°C or -20°C for post-analysis of wavelength scans and SDS PAGE gels.**

### 5) Robot pipetting: Round 2

Depending on the final fluorescence readout, perhaps the phenylalanine synthetase was not the best. We read in the .csv from the **4 h** final readout and repeat for the **4 phenylalanine derivates** a test with the **-Tyr** solution. We also motivate the robot to gamble :) For the **6** remaining spots, it is allowed to choose whatever amino acid it likes from the list of phenylalanine derivates not yet tried.

- [ ] Load in the .csv file.
- [ ] Add a second 384-well black plate (to store the other at 4°C or -20°C).
- [ ] Prepare a **10x MM** solution and give it to the robot.
- [X] The robot adds **7 µ MM** to 10 wells.
- [X] The robot adds **1 µ -Tyr solution** to the 10 wells. 
- [X] Let the robot choose **6** from the following list `np.random`: A9, B3, B9, B10, C3, C11, H5, H7, H9, E7, F7, **E9, G7, F7**, G4, D3, E11
  - [X] The robot pipets **1 µl** of this to the solution.
- [X] Let the robot choose the **3** from the .csv file which are phenylalanine but lowest light.
  - [X] The robot pipets **2 µl** of this to the solution.

Then the experiment begins with platereader observations (exactly as above): 
- [X] The robot puts onto heater-shaker and 37°C.
- [ ] 0 h PAUSE: Add lid. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 1 h PAUSE: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 2 h PAUSE: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 3 h PAUSE: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. Add plate back to heater-shaker.
- [ ] 4 h FINAL: Remove from heater-shaker. Remove lid. Measure fluorescence with plate reader (440 nm EXC, 500 nm EM, gain 100). Add lid. **Put plate to 4°C or -20°C for post-analysis of wavelength scans and SDS PAGE gels.**
- [ ]   

**10x MM**
- [ ] 30 µl Sol. B (should be the complete remaining, pipet directly into this tube).
- [ ] 20 µl Sol. A
- [ ] 10 µl tRNAs
- [ ] NO AMINO ACID MIX
- [ ] 10 µl plasmid
- [ ] 1 µl RNAse inhibitor
--------------------------
total: 71 µl 

Per reaction this will be **7.1 µl** to pipet. We tell the robot to pipet **7 µl** to have buffer.
  **2xCl**: C3/H5/H7


