#!/usr/bin/env python
# coding: utf-8

# In[53]:


#This performs a single peak MWHP conversion on an amino acid sequence
def PCDTWConvert(x,PCProp1='Mass',PCProp2='HydroPho',normalize=False):
    BaseArray=NoteValueConverter(PCProp1,PCProp2,Normalize=normalize)

    #Create an empty list to hold the vectors produced from each run of the loop (JD).
    tempnamesLST=[]
    temptpLST=[]
    tempspLST=[]
  
    currentseq = x
    
    lengther=len(currentseq)   
    
    #Convert all of the charaters to upper before converting it to a list (JD)
    currentseq=currentseq.upper()
    
    #Convert the current sequence to a list (JD)
    currentseq=list(currentseq)
    
    #Loop through all of the characters and if any are not allowed amino acids, replace them with a 'G'(AK)
    for j in range(lengther):
            strAllowedChars = ["A", "C", "D", "E", "F", "G", "H", "I", "K", "L","M", "N", "P", "Q", "R", "S", "T", "V", "W", "Y"]
    
            if currentseq[j] not in strAllowedChars: 
                currentseq[j] = currentseq[j].replace(currentseq[j],'G')
    
    #Convert the list back to a string (JD)
    currentseq=''.join(currentseq)
   
    ##This block of code creates a vector containing only the notevalues representing the amino acid sequence (JD).    
    NoteVec=[]
    ender=currentseq[-1]
    currentseq="G"+currentseq+ender
    lengther=len(currentseq)
    
    for k in range(lengther):
        if k==lengther:
            NoteVec.append(BaseArray[currentseq[k-1]].NoteValue)
        else:
            NoteVec.append(BaseArray[currentseq[k]].NoteValue)
  
    ##This block of code converts a vector of NoteValues to a single-peak vector (JD)   
    lengther2=(len(NoteVec))-1
    SinglePeakOutVector=[]
    
    for l in range(lengther2):
        if l==0:
            Outvalue=((NoteVec[l]*2)+((NoteVec[l]+NoteVec[l+1])/2))/2
            SinglePeakOutVector.append(round(Outvalue,4))
        else:
            Outvalue=((NoteVec[l])+((NoteVec[l]+NoteVec[l+1])/2)+((NoteVec[l]+NoteVec[l-1])/2))/2  
            SinglePeakOutVector.append(round(Outvalue,4))

    return SinglePeakOutVector[1:], NoteVec

#Conversion function that takes any two PC properties and converts them to a notevalue list
def NoteValueConverter(PropA,PropB,Normalize=True):
    
    import pandas as pd
    
    #The values in this dataframe were taken from DOI:10.1371/journal.pone.0147 and vary slightly from the values used in
    #The MWHP algorithm used in Dixson and Azad 2021.  Zero values were treated as 0.001 here except for hydrophobicity
    #where they were set to 1 as in the original algorithm.  The values for hydrophobicity are mostly from Monera 1995 except for 
    #proline that was not included in that publication.  The value for proline was set at -46 in accordance with the chart at
    #https://www.sigmaaldrich.com/US/en/technical-documents/technical-article/protein-biology/protein-structural-analysis/amino-acid-reference-chart?srsltid=AfmBOop298sG6HwDyQ7tvsDFLsBOA2B9f8MQMalLOrTFF3h3_fC7iqZC
    #which includes the values from Monera et al 1995.

    
    PCPropertiesRaw=pd.DataFrame.from_dict({'HydroPho':[1,41,97,74,100,97,-23,-10,-31,-5,-46,76,99,49,63,8,-14,-28,-55,13],
                                    'HydroPhIl':[0.001,-0.5,-1.8,-1.3,-2.5,-3.4,3,0.2,3,0.3,0.001,-1.5,-1.8,-1,-2.3,-0.5,3,2,3,-0.4],
                                    'Hbond':[2,2,2,2,2,3,2,4,4,4,2,2,2,2,3,4,4,4,4,4],
                                    'SideVol':[0.001,27.5,93.5,94.1,115.5,145.5,100,80.7,62,29.3,41.9,71.5,93.5,44.6,117.3,79,105,58.7,40,51.3],
                                    'Polarity':[9,8.1,4.9,5.7,5.2,5.4,11.3,10.5,12.3,9.2,8,5.9,5.2,5.5,6.2,10.4,10.5,11.6,13,8.6],
                                    'Polarizability':[0.001,0.046,0.186,0.221,0.29,0.409,0.219,0.18,0.151,0.062,0.131,0.14,0.186,0.128,0.298,0.23,0.18,0.134,0.105,0.108],
                                    'SASA':[0.881,1.181,1.931,2.034,2.228,2.663,2.258,1.932,1.862,1.298,1.468,1.645,1.81,1.461,2.368,2.025,1.932,1.655,1.587,1.525],
                                    'NCI':[0.179052,0.007187,0.051672,0.002683,0.037552,0.037977,0.017708,0.049211,0.006802,0.004627,0.239531,0.057004,0.021631,-0.03661,0.023599,-0.01069,0.049211,0.005392,-0.02382,0.003352],
                                    'Mass':[57.05,71.08,113.16,131.2,147.18,186.22,128.18,128.13,129.12,87.08,97.12,99.13,113.16,103.15,163.18,137.14,156.19,114.11,115.09,101.11]},
                                    orient='index', columns=['G','A','L','M','F','W','K','Q','E','S','P','V','I','C','Y','H','R','N','D','T'])
    
    PCPropertiesNorm=pd.DataFrame()
    PCProperties=pd.DataFrame()

    def absolute_maximum_scale(series):
        return series / series.abs().max()

    PCPropertiesNorm=PCPropertiesRaw.transpose()

    for col in PCPropertiesNorm.columns:
        PCPropertiesNorm[col] = absolute_maximum_scale(PCPropertiesNorm[col])
    PCPropertiesNorm=PCPropertiesNorm.transpose() 
    
    if Normalize is True:
        PCProperties=PCPropertiesNorm
    else:
        PCProperties=PCPropertiesRaw
     
    PreNotesA=PCProperties.loc[PropA].tolist()
    PreNotesB=PCProperties.loc[PropB].tolist()
    
    MaxNoteA=max(PreNotesA)
    
    outNoteslst=[]
    
    for i in range(20):
        R=PCProperties.loc[PropA].tolist()[i]
        G=max(PreNotesA)
        H=PCProperties.loc[PropB].tolist()[i]
        V=round(((R/G)*H),4)
        outNoteslst.append(V)
        
    BaseArray=pd.DataFrame.from_dict({
        'NoteValue': outNoteslst},
    orient='index', columns=['G','A','L','M','F','W','K','Q','E','S','P','V','I','C','Y','H','R','N','D','T'])
   
    return BaseArray



# In[2]:


#This performs a single peak MWHP alignment
def PCDTWAlign(inputseq1str,inputseq2str,PCProp1='Mass',PCProp2='HydroPho',Penalty=0,Window=3):
    from dtaidistance import dtw
    import numpy as np

    vector1=PCDTWConvert(inputseq1str,PCProp1,PCProp2)
    vector2=PCDTWConvert(inputseq2str,PCProp1,PCProp2)

    path=dtw.warping_path(vector1, vector2,penalty=Penalty,window=Window)
    
    #Split the path into two lists that represent index values of the original sequence.
    vector1indexlst, vector2indexlst = zip(*path)
    
    alignedseq1=""
    alignedseq2=""
    
    h=0
    while h <(len(vector1indexlst)):
        looker1=vector1indexlst[h]
        temp1counter=vector1indexlst.count(looker1)
        if temp1counter==1:
            alignedseq1=alignedseq1+(list(inputseq1str))[vector1indexlst[h]]
            h+=temp1counter
        elif temp1counter>1:
            alignedseq1=alignedseq1+(list(inputseq1str))[vector1indexlst[h]]
            for l in range(temp1counter-1):
                alignedseq1=alignedseq1+"-"
            h+=temp1counter
    
    
    j=0
    while j <(len(vector2indexlst)):
        looker2=vector2indexlst[j]
        temp2counter=vector2indexlst.count(looker2)
        if temp2counter==1:
            alignedseq2=alignedseq2+(list(inputseq2str))[vector2indexlst[j]]
            j+=temp2counter
        elif temp2counter>1:
            alignedseq2=alignedseq2+(list(inputseq2str))[vector2indexlst[j]]
            for l in range(temp2counter-1):
                alignedseq2=alignedseq2+"-"
            j+=temp2counter
            
            
###########################GET THE ALIGNED VECTORS########################################
    alignedvec1=[]
    alignedvec2=[]
    
    h=0
    while h <(len(vector1indexlst)):
        looker1=vector1indexlst[h]
        temp1counter=vector1indexlst.count(looker1)
        if temp1counter==1:
            alignedvec1.append(vector1[vector1indexlst[h]])
            h+=temp1counter
        elif temp1counter>1:
            alignedvec1.append(vector1[vector1indexlst[h]])
            for l in range(temp1counter-1):
                alignedvec1.append(vector1[vector1indexlst[h]])
            h+=temp1counter
    
    
    j=0
    while j <(len(vector2indexlst)):
        looker2=vector2indexlst[j]
        temp2counter=vector2indexlst.count(looker2)
        if temp2counter==1:
            alignedvec2.append(vector2[vector2indexlst[j]])
            j+=temp2counter
        elif temp2counter>1:
            alignedvec2.append(vector2[vector2indexlst[j]])
            for l in range(temp2counter-1):
                alignedvec2.append(vector2[vector2indexlst[j]])
            j+=temp2counter
    outp1arr=np.array(alignedvec1)
    outp2arr=np.array(alignedvec2)
    ConsensusVector=(outp1arr+outp2arr)/2
            
###########################GET THE ALIGNED VECTORS########################################
    
    
    GAPS=(alignedseq1+alignedseq2).count('-')
    Seq1Alignstr=alignedseq1
    Seq2Alignstr=alignedseq2
    
    counter=0
    for i in range(len(Seq1Alignstr)):
        if Seq1Alignstr[i]==Seq2Alignstr[i]:
            counter=counter+1
    identity=(int((counter/len(Seq1Alignstr))*100))
    
    midalignstr=''
    for i in range(len(Seq1Alignstr)):
        if Seq1Alignstr[i]==Seq2Alignstr[i]:
            midalignstr=midalignstr+'|'
        else:
            midalignstr=midalignstr+' '
    FullAlignment= Seq1Alignstr+'\n'+midalignstr+'\n'+Seq2Alignstr
    
    #Full list of variables that could be returned:Seq1Alignstr, Seq2Alignstr, GAPS, path, identity, alignedvec1, alignedvec2, ConsensusVector
    PCDTWAlnResult={
        'Seq1AlignedString':Seq1Alignstr,
        'Seq2AlignedString':Seq2Alignstr,
        'FullAlignment':FullAlignment,
        'Identity':identity,
        'ConsensusVector':ConsensusVector       
                   }

    return PCDTWAlnResult


# In[3]:


#This returns the dtw distance per residue.  Default is single peak vector (i.e. one peak per residue)
def PCDTWDist(Seq1,Seq2,PCProp1='Mass',PCProp2='HydroPho',PeaksPerRes=1,Penalty=0,Window=3):
    from dtaidistance import dtw
    Vec1=PCDTWConvert(Seq1,PCProp1,PCProp2)
    Vec2=PCDTWConvert(Seq2,PCProp1,PCProp2)
    
    DTWDistance = dtw.distance(Vec1, Vec2, penalty=Penalty, window=Window)
    DTWDistance=DTWDistance/(len(Vec1)*PeaksPerRes)
    DTWDistance=round(DTWDistance,3)

    return DTWDistance


# In[94]:


#Function to evolve a sequence with the objective of minimizing the physicochemical change (2 properties) while maximizing the sequence level change.
#The sequences output from this function will vary slightly from those Dixson et. al. 2025 because the hydrophobicity values have been updated
#This change is discussed further in the NoteValueConverter function comments above.

def PCEvolve(Seq='GALM', PCProp1='Mass', PCProp2='HydroPho', BaseName='ProtX'):
    import pandas as pd
    NoteVector = (PCDTWConvert(x=Seq, PCProp1=PCProp1, PCProp2=PCProp2, normalize=False))[1]
    NoteVector=NoteVector[:-1]
    NoteVector=NoteVector[1:]

    #Create an empty dataframe to hold the top three residues that match the input sequence
    MatchedRes=pd.DataFrame()      
    
    # #Creat lists to hold the residues and the notevalue for each residue
    NoteResLst=(NoteValueConverter(PropA=PCProp1,PropB=PCProp2,Normalize=False)).columns.tolist()  
    NoteValLst=(NoteValueConverter(PropA=PCProp1,PropB=PCProp2,Normalize=False)).iloc[0].tolist()

    #Put the Notevalues into a dict
    NoteDict = dict(zip(NoteResLst, NoteValLst))

    #Convert the input sequence to a vector of note values
    NoteValues = [NoteDict[char] for char in Seq if char in NoteDict]

    #Find the closest fully divergent sequence to the input NoteValues
    FullDivSeq = []
    for value in NoteValues:
        closest_key = None
        min_difference = float('inf')
        
        for key, dict_value in NoteDict.items():
            difference = abs(dict_value - value)
            
            if difference < min_difference and dict_value != value:
                min_difference = difference
                closest_key = key
        
        if closest_key is not None:
            FullDivSeq.append(closest_key)

    #Iterate through the NoteValues 20 times with a step of 0.05 difference so that a residue is only replaced if it is the step percentage value
    #or less different than the original sequence
    fasta_output = ""
    threshold = 0  # Starts at 0% for identical sequence
    previous_seq = Seq  # Initialize with original sequence to exclude it
    seq_number = 1  # Output sequence numbering
    
    for i in range(20):
        new_seq = ""
    
        for j, char in enumerate(Seq):
            if char in NoteDict:
                original_value = NoteDict[char]
                alternative_value = NoteDict.get(FullDivSeq[j], original_value)  # Alternative or original value
                percent_difference = abs(alternative_value - original_value) / original_value * 100
    
                # Final iteration: Apply 95% threshold and include all values exceeding it
                if i == 19 and percent_difference > 95:
                    new_seq += FullDivSeq[j]
                elif percent_difference <= threshold and alternative_value != original_value:
                    new_seq += FullDivSeq[j]
                else:
                    new_seq += char
            else:
                new_seq += char  # Preserve unchanged if not in dictionary
    
        # Append sequence only if it's different from the previous one AND not the original Seq
        if new_seq != previous_seq:
            fasta_output += f">{BaseName}_{'SimHomolog_'}{seq_number}\n{new_seq}\n"
            previous_seq = new_seq  # Update sequence tracker
            seq_number += 1  # Increment naming only for unique sequences
    
        # Increase threshold by 5% per iteration, stopping at 95% for the final loop
        threshold = min(threshold + 5, 95)
       
    return fasta_output

